import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.header.checker as checker_header
import zstackwoodpecker.header.vm as vm_header
import zstackwoodpecker.header.port_forwarding as pf_header
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state

import zstacklib.utils.http as http
import zstacklib.utils.jsonobject as jsonobject
import zstacklib.utils.linux as linux
import zstacklib.utils.list_ops as list_ops

import apibinding.inventory as inventory
import zstacktestagent.plugins.vm as vm_plugin
import zstacktestagent.plugins.host as host_plugin
import zstacktestagent.testagent as testagent

import os
import sys
import traceback

port_header = test_state.Port

class zstack_kvm_pf_rule_exist_checker(checker_header.TestChecker):
    '''
    Check if pf rules are setting in vr
    '''
    def check(self):
        super(zstack_kvm_pf_rule_exist_checker, self).check()
        test_result = test_lib.lib_check_vm_pf_rule_exist_in_iptables(self.test_obj.get_port_forwarding())
        test_util.test_logger('Check result: [Port Forwarding] %s finishes rule existance testing' % self.test_obj.get_port_forwarding().uuid)
        return self.judge(test_result)

class zstack_kvm_pf_tcp_checker(checker_header.TestChecker):
    '''check kvm vm dnat status. If VM is reachable from external target, 
        return self.judge(True). If not, return self.judge(False)'''

    def check(self):
        '''
            check will assume target vm only have 1 port forwarding VR. 
            So all vms PF rules are assigned to 1 VM nic.
        '''
        super(zstack_kvm_pf_tcp_checker, self).check()
        test_result = True
        target_vm = self.test_obj.get_target_vm().vm
        pf_rule = self.test_obj.get_port_forwarding()
        vm_nic = test_lib.lib_get_nic_by_uuid(pf_rule.vmNicUuid)
        all_ports = port_header.all_ports
        #only open ports when VM is running.
        if self.test_obj.get_target_vm().state == vm_header.RUNNING:
            test_lib.lib_open_vm_listen_ports(target_vm, all_ports, vm_nic.l3NetworkUuid)
        #consolidate rules for TCP/UDP/ICMP with different AllowedCidr
        rule_port = port_header.get_port_rule(pf_rule.vipPortStart, pf_rule.vipPortEnd)

        #check SG ingress limitation. Since SG rule will not consider vip as 
        #allowedCidr, if there is ingress limitation, the ingress PF connection
        #will be blocked.
        sg_tcp_ingress_flag = _sg_rule_exist(vm_nic, inventory.TCP, pf_rule)

        allowedCidr = pf_rule.allowedCidr
        allowed_vr_ip = allowedCidr.split('/')[0]
        allowed_vr_vm = test_lib.lib_get_vm_by_ip(allowed_vr_ip)
        vr_nic = test_lib.lib_get_nic_by_ip(allowed_vr_ip)
        l3_uuid = vr_nic.l3NetworkUuid

        allowed_vr_uuid_list = [allowed_vr_vm.uuid]
        #target_vm's VRs should be excluded, otherwise the ip package will be routed to this VR directly.
        pf_vm_vrs = test_lib.lib_find_vr_by_vm(target_vm)
        for pf_vr in pf_vm_vrs:
            allowed_vr_uuid_list.append(pf_vr.uuid)

        denied_vr_vm = _find_denied_vr(target_vm.clusterUuid, l3_uuid, allowed_vr_uuid_list)
        denied_vr_ip = test_lib.lib_find_vr_pub_ip(denied_vr_vm)

        vip_uuid = pf_rule.vipUuid
        cond = res_ops.gen_query_conditions('uuid', '=', vip_uuid)
        vipIp = res_ops.query_resource(res_ops.VIP, cond)[0].ip
        if sg_tcp_ingress_flag:
            test_util.test_logger('SG TCP Ingress rule existence. PF TCP ingress rule will be blocked for [vm:] %s' % target_vm.uuid)
            try:
                test_lib.lib_check_ports_in_a_command(allowed_vr_vm, allowed_vr_ip, vipIp, [], all_ports, target_vm)
            except:
                test_util.test_logger("Catch failure when checking Port Forwarding TCP [rule:] %s for allowed Cidr from [vm:] %s, when SG rule exists. " % (pf_rule.uuid, target_vm.uuid))
                test_result = False
                if test_result != self.exp_result:
                    return self.judge(test_result)
        else:
            allowed_ports = port_header.get_ports(rule_port)
            denied_ports = list_ops.list_minus(all_ports, allowed_ports)
            try:
                test_lib.lib_check_ports_in_a_command(allowed_vr_vm, allowed_vr_ip, vipIp, allowed_ports, denied_ports, target_vm)
            except:
                traceback.print_exc(file=sys.stdout)
                test_util.test_logger("Catch failure when checking Port Forwarding TCP [rule:] %s for allowed Cidr from [vm:] %s " % (pf_rule.uuid, target_vm.uuid))
                test_result = False
                if test_result != self.exp_result:
                    return self.judge(test_result)
            else:
                test_util.test_logger("Checking pass for Port Forwarding TCP [rule:] %s for allowed Cidr from [vm:] %s " % (pf_rule.uuid, target_vm.uuid))

            try:
                test_lib.lib_check_ports_in_a_command(denied_vr_vm, denied_vr_ip, vipIp, [], all_ports, target_vm)
            except:
                traceback.print_exc(file=sys.stdout)
                test_util.test_logger("Catch failure when checking Port Forwarding TCP [rule:] %s for not allowed Cidr from [vm:] %s" % (pf_rule.uuid, target_vm.uuid))
                test_result = False
                if test_result != self.exp_result:
                    return self.judge(test_result)
            else:
                test_util.test_logger("Checking pass for Port Forwarding TCP [rule:] %s for not allowed Cidr from [vm:] %s . All ports should be blocked. " % (pf_rule.uuid, target_vm.uuid))

        test_util.test_logger('Check result: [Port Forwarding] finishes TCP testing for [vm:] %s [nic:] %s' % (target_vm.uuid, vm_nic.uuid))
        return self.judge(test_result)

class zstack_kvm_pf_udp_checker(checker_header.TestChecker):
    '''check kvm vm dnat status. If VM is reachable from external target, 
        return self.judge(True). If not, return self.judge(False)'''

    def check(self):
        '''
            check will assume target vm only have 1 port forwarding VR. 
            So all vms PF rules are assigned to 1 VM nic.
        '''
        #TODO: add check for udp.
        super(zstack_kvm_pf_udp_checker, self).check()
        return self.judge(self.exp_result)

class zstack_kvm_pf_vip_icmp_checker(checker_header.TestChecker):
    '''check PF's VIP IP icmp status. If VIP is not pingable, return 
    self.judge(False). If yes, return self.judge(True)'''
    def check(self):
        super(zstack_kvm_pf_vip_icmp_checker, self).check()
        test_result = True
        pf_rule = self.test_obj.get_port_forwarding()
        vip_uuid = pf_rule.vipUuid
        cond = res_ops.gen_query_conditions('uuid', '=', vip_uuid)
        vipIp = res_ops.query_resource(res_ops.VIP, cond)[0].ip
        vip_l3_uuid = test_lib.lib_get_vip_by_uuid(pf_rule.vipUuid).l3NetworkUuid
        any_vr = test_lib.lib_find_vr_by_l3_uuid(vip_l3_uuid)[0]
        try:
            test_lib.lib_check_ping(any_vr, vipIp)
        except:
            test_util.test_logger("Catch exception: Port Forwarding [rule:] %s is not pingable from [vm:] %s " % (pf_rule.uuid, any_vr.uuid))
            test_result = False
            if test_result != self.exp_result:
                return self.judge(test_result)
        else:
            test_util.test_logger("Port Forwarding [rule:] %s is pingable from [vm:] %s" % (pf_rule.uuid, any_vr.uuid))
        return self.judge(test_result)

def _sg_rule_exist(nic, protocol, pf_rule):
    conditions = res_ops.gen_query_conditions('vmNicUuid', '=', nic.uuid)
    sg_nic = res_ops.query_resource(res_ops.VM_SECURITY_GROUP, conditions)
    if not sg_nic:
        return
    conditions = res_ops.gen_query_conditions('uuid', '=', sg_nic[0].securityGroupUuid)
    sg = res_ops.query_resource(res_ops.SECURITY_GROUP, conditions)[0]
    if not sg.rules:
        #ingress is defaultly blocked.
        return True

    for rule in sg.rules:
        if rule.protocol == protocol and rule.type == inventory.INGRESS:
            if rule.allowedCidr == pf_rule.allowedCidr and rule.startPort == pf_rule.privatePortStart and rule.endPort == pf_rule.privatePortEnd:
                return False

    return True

def _find_denied_vr(cluster_uuid, l3_uuid, allowed_vr_uuid_list):
    conditions = res_ops.gen_query_conditions('clusterUuid', '=', cluster_uuid)
    conditions = res_ops.gen_query_conditions('applianceVmType', '=', 'VirtualRouter', conditions)
    all_virtualrouter_vrs = res_ops.query_resource(res_ops.APPLIANCE_VM, conditions)
    conditions = res_ops.gen_query_conditions('clusterUuid', '=', cluster_uuid)
    conditions = res_ops.gen_query_conditions('applianceVmType', '=', 'vrouter', conditions)
    all_vyos_vrs = res_ops.query_resource(res_ops.APPLIANCE_VM, conditions)
    conditions = res_ops.gen_query_conditions('clusterUuid', '=', cluster_uuid)
    conditions = res_ops.gen_query_conditions('applianceVmType', '=', 'vpcvrouter', conditions)
    all_vpc_vrs = res_ops.query_resource(res_ops.APPLIANCE_VM, conditions)

    for vr in all_virtualrouter_vrs+all_vyos_vrs+all_vpc_vrs:
        if not vr.uuid in allowed_vr_uuid_list:
            for vm_nic in vr.vmNics:
                if vm_nic.l3NetworkUuid == l3_uuid:
                    return vr

