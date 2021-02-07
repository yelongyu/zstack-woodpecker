import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.header.checker as checker_header
import zstackwoodpecker.header.vm as vm_header
import zstackwoodpecker.header.vip as vip_header
import zstackwoodpecker.header.eip as eip_header
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
import random
import sys
import traceback

port_header = test_state.Port

class vip_used_for_checker(checker_header.TestChecker):
    '''
    Check if vip is set as used for target_use_for.

    The Checker need to be set target used for, after initialized.
    '''
    def __init__(self):
        self.use_for = None
        super(vip_used_for_checker, self).__init__()

    def set_target_use_for(self, useFor):
        self.use_for = useFor

    def check(self):
        super(vip_used_for_checker, self).check()
        test_result = True
        vip_uuid = self.test_obj.get_vip().uuid
        try:
            vip_db = test_lib.lib_get_vip_by_uuid(vip_uuid)
        except:
            test_util.test_logger('Check Result: not find vip by [uuid:] %s '\
                    % vip_uuid)
            return self.judge(False)

        if vip_db and self.use_for in vip_db.useFor:
            test_util.test_logger('Check Result: [vip:] %s is used for %s' \
                    % (vip_uuid, self.use_for))

            return self.judge(True)

        test_util.test_logger('Check Result: [vip:] %s is NOT used for %s' \
                % (vip_uuid, self.use_for))

        return self.judge(False)

class eip_checker(checker_header.TestChecker):
    '''
    Check eip 
    '''
    def __init__(self):
        super(eip_checker, self).__init__()
        self.allowed_ports = []
        self.denied_ports = []
        self.vm_nic_uuid = None
        self.allowed_vr = None  #only allowed_ports are allowed by allowed_vr
        self.allowed_vr_ip = None
        self.denied_vr = None   #denied means denying all ports.
        self.denied_vr_ip = None
        self.available_vr_dict = {} #{ip1:vr_vm_inv1, ip2:vr_vm_inv2}

    def get_all_available_vr_ip(self):
        vip = self.test_obj.get_vip()
        l3_uuid = vip.l3NetworkUuid
        vrs = test_lib.lib_find_vr_by_l3_uuid(l3_uuid)
        eip_vm_vr_uuids = []
        if self.vm_nic_uuid:
            #target_vm's VRs should be excluded, otherwise the ip package will be routed to this VR directly.
            vm_nic = test_lib.lib_get_nic_by_uuid(self.vm_nic_uuid)
            vr_l3_uuid = vm_nic.l3NetworkUuid
            vr = test_lib.lib_find_vr_by_l3_uuid(vr_l3_uuid)[0]
            eip_vm_vr_uuids.append(vr.uuid)

        for vr in vrs:
            vnic = test_lib.lib_get_vm_nic_by_l3(vr, l3_uuid)
            if vr.uuid in eip_vm_vr_uuids:
                continue
            ip = vnic.ip
            self.available_vr_dict[ip] = vr

    def set_random_allowed_vr(self):
        if self.available_vr_dict:
            self.allowed_vr_ip = random.choice(self.available_vr_dict.keys())
            self.allowed_vr = self.available_vr_dict[self.allowed_vr_ip]

    def set_random_denied_vr(self):
        if self.available_vr_dict:
            self.denied_vr_ip = random.choice(self.available_vr_dict.keys())
            self.denied_vr = self.available_vr_dict[self.denied_vr_ip]

    def check(self):
        super(eip_checker, self).check()
        try:
            test_vip = test_lib.lib_get_vip_by_uuid(self.test_obj.get_vip().uuid)
        except:
            test_util.test_logger('Check Result: [vip:] %s does not exist' % self.test_obj.get_vip().uuid)
            return self.judge(False)
        vip = self.test_obj.get_vip()
        vipIp = vip.ip

        eip_obj = self.test_obj.get_eip()
        eip = eip_obj.get_eip()
        try:
            test_eip = test_lib.lib_get_eip_by_uuid(eip.uuid)
        except:
            test_util.test_logger('Check Result: [eip:] %s does not exist' % eip.uuid)
            return self.judge(False)

        if eip_obj.state == eip_header.ATTACHED:
            self.vm_nic_uuid = eip.vmNicUuid

        self.get_all_available_vr_ip()

        all_ports = port_header.all_ports

        if not self.vm_nic_uuid:
            #eip is not attached
            self.set_random_denied_vr()
            return self.judge(self.check_eip_denied_tcp())
        else:
            vm_nic = test_lib.lib_get_nic_by_uuid(self.vm_nic_uuid)
            #only open ports when VM is running.
            if eip_obj.get_target_vm().state == vm_header.RUNNING:
                target_vm = eip_obj.get_target_vm().vm
                test_lib.lib_open_vm_listen_ports(target_vm, all_ports, vm_nic.l3NetworkUuid)
            else:
                self.set_random_denied_vr()
                return self.judge(self.check_eip_denied_tcp())

        #make sure no any SG rule can impact eip testing.
        sg_invs = test_lib.lib_get_sg_invs_by_nic_uuid(self.vm_nic_uuid)
        test_result = self.exp_result
        if not sg_invs:
            #If no SG TCP rules for vm_nic, means all ports are connectable
            self.set_random_allowed_vr()
            self.denied_vr = None
            self.denied_vr_ip = None
            self.allowed_ports = all_ports
            self.denied_ports = []
            test_result = self.check_eip_allowed_tcp()
            if test_result != self.exp_result:
                return self.judge(test_result)

            #if no icmp rule, means ping should be successful
            test_result = self.check_eip_icmp(True)
            if test_result != self.exp_result:
                return self.judge(test_result)
        else:
            self.calc_sg_tcp_ports(sg_invs)
            test_result = self.check_eip_allowed_tcp()
            if test_result != self.exp_result:
                return self.judge(test_result)
            test_result = self.check_eip_denied_tcp()
            if test_result != self.exp_result:
                return self.judge(test_result)

        test_util.test_logger('Checker Result for EIP checker: %s' % test_result)
        return self.judge(test_result)

    def check_eip_allowed_tcp(self):
        if not self.allowed_vr_ip:
            test_util.test_logger('No allowed vm for eip testing. Skip EIP allowed TCP checking')
            return True

        vip = self.test_obj.get_vip()
        vip_ip = vip.ip
        eip = self.test_obj.get_eip().get_eip()
        target_vm = self.test_obj.get_eip().get_target_vm().vm
        try:
            test_lib.lib_check_ports_in_a_command(self.allowed_vr, self.allowed_vr_ip, vip_ip, self.allowed_ports, self.denied_ports, target_vm)
        except:
            traceback.print_exc(file=sys.stdout)
            test_util.test_logger("Unexpected Result: Catch failure when checking [vip:] %s EIP: %s for allowed ip: %s from [vm:] %s . " % \
                (vip.uuid, eip.uuid, self.allowed_vr_ip, self.allowed_vr.uuid))
            return False

        test_util.test_logger("Expected Result: Network checking pass for [vip:] %s EIP: %s by allowed ip: %s from [vm:] %s . " % \
                (vip.uuid, eip.uuid, self.allowed_vr_ip, self.allowed_vr.uuid))
        return True

    def check_eip_denied_tcp(self):
        if not self.denied_vr_ip:
            test_util.test_logger('No denied vm for eip testing. Skip EIP deined TCP checking')
            return True

        vip = self.test_obj.get_vip()
        vip_ip = vip.ip
        eip_obj = self.test_obj.get_eip()
        eip = eip_obj.get_eip()
        if not eip_obj.get_target_vm():
            #eip is not attached yet. use vip's VR vm
            l3_uuid = self.test_obj.get_vip().l3NetworkUuid
            target_vm = test_lib.lib_find_vr_by_l3_uuid(l3_uuid)[0]
        else:
            target_vm = eip_obj.get_target_vm().vm

        all_ports = port_header.all_ports

        try:
            test_lib.lib_check_ports_in_a_command(self.denied_vr, self.denied_vr_ip, vip_ip, [], all_ports, target_vm)
        except:
            traceback.print_exc(file=sys.stdout)
            test_util.test_logger("Unexpected Result: Catch failure when checking [vip:] %s EIP: %s for denied ip: %s from [vm:] %s. All ports should be denied." % \
                (vip.uuid, eip.uuid, self.denied_vr_ip, self.denied_vr.uuid))
            return False

        test_util.test_logger("Expected Result: Network checking pass for [vip:] %s EIP: %s by denied ip: %s from [vm:] %s . " % \
                (vip.uuid, eip.uuid, self.denied_vr_ip, self.denied_vr.uuid))
        return True

    def check_eip_icmp(self, expected_result):
        vip_ip = self.test_obj.get_vip().ip
        eip = self.test_obj.get_eip().get_eip()
        try:
            if not self.allowed_vr:
                test_util.test_warn("Not find suitable VR vm to do test testing. Please make sure there are at least 3 VR VMs are exist for EIP testing.")
            test_lib.lib_check_ping(self.allowed_vr, vip_ip)
        except:
            if expected_result:
                test_util.test_logger("Unexpected Result: catch failure when checking EIP: %s ICMP for target ip: %s from [vm:] %s. " % (eip.uuid, vip_ip, self.allowed_vr.uuid))
                return False
            else:
                if self.allowed_vr:
                    test_util.test_logger("Expected Result: catch failure when checking EIP: %s ICMP for target ip: %s from [vm:] %s. " % (eip.uuid, vip_ip, self.allowed_vr.uuid))
                else:
                    test_util.test_logger("can not do test, due to missing allowed vr.  " % (eip.uuid, vip_ip, self.allowed_vr.uuid))

        if expected_result:
            test_util.test_logger("Expected Result: Ping successfully checking EIP: %s ICMP for target ip: %s from [vm:] %s" % (eip.uuid, vip_ip, self.allowed_vr.uuid))
        else:
            test_util.test_logger("Unexpected Result: Ping successfully checking EIP: %s ICMP for target ip: %s from [vm:] %s" % (eip.uuid, vip_ip, self.allowed_vr.uuid))
        return True

    def calc_sg_tcp_ports(self, sg_invs):
        '''
        calculate and setup allowed/denied vr and ip address for later testing.
        '''
        all_ports = port_header.all_ports
        allowed_ports = []
        denied_ports = all_ports

        #default all ingress ports are denied, unless we found vr ip is in 
        #allowed SG ingress rule. 
        self.allowed_vr = None
        self.allowed_vr_ip = None
        self.set_random_denied_vr()
        self.allowed_ports = []
        self.denied_ports = list(all_ports)

        #{vr_ip:{'allowed_ports': [], 'denied_ports': []}, }
        vr_port_map = {}

        for sg in sg_invs:
            if not sg.rules:
                continue 

            for rule in sg.rules:
                if rule.protocol == inventory.TCP \
                        and rule.type == inventory.INGRESS:

                    allowed_cidr = rule.allowedCidr
                    allowed_vr_ip = allowed_cidr.split('/')[0]
                    start_port = rule.startPort
                    end_port = rule.endPort
                    if allowed_vr_ip in self.available_vr_dict.keys():
                        rule_port_key = \
                                port_header.get_port_rule(start_port, end_port)
                        allowed_ports = port_header.get_ports(rule_port_key)
                        if not vr_port_map.has_key(allowed_vr_ip):
                            vr_port_map[allowed_vr_ip] = \
                                    {'allowed_ports': allowed_ports, \
                                    'denied_ports': []}
                        else:
                            for port in allowed_ports:
                                if not port in vr_port_map[allowed_vr_ip]['allowed_ports']:
                                    vr_port_map[allowed_vr_ip]['allowed_ports'].append(port)

        if not vr_port_map:
            #not find available vr ip is in allowed ingress rule. So all denied.
            return

        #pick one vr_ip as test target
        allowed_vr_ips = vr_port_map.keys()
        self.allowed_vr_ip = random.choice(allowed_vr_ips)
        self.allowed_vr = self.available_vr_dict[self.allowed_vr_ip]
        self.allowed_ports = vr_port_map[self.allowed_vr_ip]['allowed_ports']
        self.denied_ports = list_ops.list_minus(all_ports, self.allowed_ports)

        for vr_ip in self.available_vr_dict.keys():
            if not vr_ip in allowed_vr_ips:
                self.denied_vr_ip = vr_ip
                self.denied_vr = self.available_vr_dict[vr_ip]

class pf_checker(checker_header.TestChecker):
    '''
    Check port forwarding rules
    pf doesn't support ICMP
    '''
    def separate_tcp_udp_list(self, pf_list):
        pf_tcp_list = []
        pf_udp_list = []

        for pf in pf_list:
            pf_rule = pf.get_port_forwarding()
            if pf_rule.protocolType == inventory.TCP:
                pf_tcp_list.append(pf)
            else:
                pf_udp_list.append(pf)

        return pf_tcp_list, pf_udp_list

    def get_allowed_denied_vr_vm(self, allowed_vr_ip, vm_nic_uuid):
        '''
        Get source VR vm for PF port testing. 
        @return: allowed_vr, denied_vr
        '''
        #get allowed vr vm
        allowed_vr_vm = test_lib.lib_get_vm_by_ip(allowed_vr_ip)
        vr_nic = test_lib.lib_get_nic_by_ip(allowed_vr_ip)
        l3_uuid = vr_nic.l3NetworkUuid

        allowed_vr_uuid_list = [allowed_vr_vm.uuid]
        #target_vm's VRs should be excluded, otherwise the ip package will be routed to this VR directly.
        if vm_nic_uuid:
            vm_nic = test_lib.lib_get_nic_by_uuid(vm_nic_uuid)
            vr_l3_uuid = vm_nic.l3NetworkUuid
            pf_vr = test_lib.lib_find_vr_by_l3_uuid(vr_l3_uuid)[0]
            allowed_vr_uuid_list.append(pf_vr.uuid)

        denied_vr_vm = _find_denied_vr(allowed_vr_vm.clusterUuid, l3_uuid, allowed_vr_uuid_list)
        return allowed_vr_vm, denied_vr_vm

    def gen_tcp_dict_by_allowed_cidr(self, pf_tcp_list):
        '''
        Put all pf with same allowed_cidr in same list.
        '''
        pf_tcp_dict = {}
        for pf in pf_tcp_list:
            pf_rule = pf.get_port_forwarding()
            allowedCidr = pf_rule.allowedCidr
            allowed_vr_ip = allowedCidr.split('/')[0]
            if allowed_vr_ip in pf_tcp_dict.keys():
                pf_tcp_dict[allowed_vr_ip].append(pf)
            else:
                pf_tcp_dict[allowed_vr_ip] = [pf]

        return pf_tcp_dict

    def recalc_allowed_denied_ports(self, allowed_ports, denied_ports, \
            pf_allowed_ports, pf_denied_ports):
        new_allowed_ports = list(allowed_ports)
        new_denied_ports = list(denied_ports)
        for allowed_port in pf_allowed_ports:
            if allowed_port in allowed_ports:
                #this should not happen
                test_util.test_warn('Same VIP ports are assigned more than once. ')
            else:
                new_allowed_ports.append(allowed_port)
                new_denied_ports.remove(allowed_port)

        return new_allowed_ports, new_denied_ports

    def count_pf_allowed_denied_ports(self, pf_dict_list, allowed_ports, denied_ports):
        for pf in pf_dict_list:
            pf_rule = pf.get_port_forwarding()
            pf_allowed_ports, pf_denied_ports = \
                    self.calc_pf_sg_allowed_denied_ports(pf_rule)

            allowed_ports, denied_ports = \
                    self.recalc_allowed_denied_ports(allowed_ports, \
                    denied_ports, pf_allowed_ports, pf_denied_ports)

        return allowed_ports, denied_ports 

    def calc_pf_sg_allowed_denied_ports(self, pf_rule):
        vm_nic = test_lib.lib_get_nic_by_uuid(pf_rule.vmNicUuid)
        target_vm = test_lib.lib_get_vm_by_nic(vm_nic.uuid)
        all_ports = port_header.all_ports
        #consolidate rules for TCP/UDP/ICMP with different AllowedCidr
        rule_port = port_header.get_port_rule(pf_rule.vipPortStart, pf_rule.vipPortEnd)

        #If there is ingress controlled by SG rule and the PF rule is not in the
        # allowed SG rule's range, the ingress PF connection will be blocked.
        sg_tcp_ingress_flag = _sg_rule_exist_for_pf(vm_nic, pf_rule)

        if sg_tcp_ingress_flag:
            test_util.test_logger('SG TCP Ingress rule existence. PF TCP ingress rule will be blocked for [vm:] %s' % target_vm.uuid)
            return [], all_ports
        else:
            allowed_ports = port_header.get_ports(rule_port)
            denied_ports = list_ops.list_minus(all_ports, allowed_ports)
            return allowed_ports, denied_ports

    def check_denied_pf(self, pf):
        pf_rule = pf.get_port_forwarding()
        test_result = True
        all_ports = port_header.all_ports
        #all pf with same vip should have same l3.
        allowed_ports = []
        denied_ports = all_ports
        if not pf.get_target_vm():
            #Pf is not attached, use vip's VR VM. This wont' impact testing result.
            l3_uuid = self.test_obj.get_vip().l3NetworkUuid
            target_vm = test_lib.lib_find_vr_by_l3_uuid(l3_uuid)[0]
            vm_nic_uuid = None
        else:
            target_vm = pf.get_target_vm().vm
            vm_nic_uuid = pf_rule.vmNicUuid

        allowedCidr = pf_rule.allowedCidr
        allowed_vr_ip = allowedCidr.split('/')[0]
        allowed_vr_vm, denied_vr_vm = \
                self.get_allowed_denied_vr_vm(allowed_vr_ip, vm_nic_uuid)

        vipIp = self.test_obj.get_vip().ip
        try:
            test_lib.lib_check_ports_in_a_command(allowed_vr_vm, \
                    allowed_vr_ip, vipIp, allowed_ports, \
                    denied_ports, target_vm)
        except:
            traceback.print_exc(file=sys.stdout)
            test_util.test_logger("Catch failure when checking [vip:] %s Port Forwarding TCP [rules] for allowed Cidr: %s from [vm:] %s . " % \
                    (self.test_obj.get_vip().uuid, allowed_vr_ip, \
                    allowed_vr_vm.uuid))
            test_result = False

        return test_result

    def check(self):
        super(pf_checker, self).check()
        test_result = True

        try:
            test_vip = test_lib.lib_get_vip_by_uuid(self.test_obj.get_vip().uuid)
        except:
            test_util.test_logger('Check Result: [vip:] %s is not exist' % self.test_obj.get_vip().uuid)
            self.test_obj.update()
            return self.judge(False)

        if not self.test_obj.get_pf_list():
            test_util.test_logger('Check Result: [vip:] %s is not attached to any pf.' % self.test_obj.get_vip().uuid)
            self.test_obj.update()
            return self.judge(False)

        vip = self.test_obj.get_vip()
        vipIp = vip.ip
        all_ports = port_header.all_ports
        pf_running_list = self.test_obj.get_pf_list_for_running_vm()
        pf_tcp_list, pf_udp_list = self.separate_tcp_udp_list(pf_running_list)
        pf_tcp_dict = self.gen_tcp_dict_by_allowed_cidr(pf_tcp_list)

        pf_stopped_list = self.test_obj.get_pf_list_for_stopped_vm()
        pf_detached_list = self.test_obj.get_detached_pf_list()
        vip_l3 = self.test_obj.get_vip().l3NetworkUuid
        if not pf_running_list:
            # all ports should be denied, since no living vm. 
            for pf in pf_stopped_list:
                test_result = self.check_denied_pf(pf)
                if test_result != self.exp_result:
                    return self.judge(test_result)

            for pf in pf_detached_list:
                test_result = self.check_denied_pf(pf)
                if test_result != self.exp_result:
                    return self.judge(test_result)
        else:
            #open TCP ports for living vms
            for pf in pf_tcp_list:
                target_vm = pf.get_target_vm().vm
                vm_l3 = test_lib.lib_get_nic_by_uuid(pf.get_port_forwarding().vmNicUuid).l3NetworkUuid
                test_lib.lib_open_vm_listen_ports(target_vm, all_ports, vm_l3)

            #calc allowed ports, per allowed_cidr
            for allowed_vr_ip, pf_dict_list in pf_tcp_dict.iteritems():
                allowed_ports = []
                denied_ports = all_ports
                
                #find all pf rules on running vm. These rules are supposed to be connectable, unless they are blocked by target vm's sg.
                allowed_ports, denied_ports = \
                        self.count_pf_allowed_denied_ports(
                                pf_dict_list, 
                                allowed_ports,
                                denied_ports)

                #although the target_vm might be different, but the denied_vr_vm should be same. 
                target_vm_nic_uuid = pf_dict_list[0].get_port_forwarding().vmNicUuid
                allowed_vr_vm, denied_vr_vm = \
                        self.get_allowed_denied_vr_vm(allowed_vr_ip, target_vm_nic_uuid)
                denied_vr_ip = test_lib.lib_find_vr_pub_ip(denied_vr_vm)

                try:
                    test_lib.lib_check_ports_in_a_command(allowed_vr_vm, allowed_vr_ip, vipIp, allowed_ports, denied_ports, target_vm)
                except:
                    traceback.print_exc(file=sys.stdout)
                    test_util.test_logger("Catch failure when checking [vip:] %s Port Forwarding TCP [rules] for allowed Cidr: %s from [vm:] %s . " % \
                            (vip.uuid, allowed_vr_ip, allowed_vr_vm.uuid))

                    test_result = False
                    if test_result != self.exp_result:
                        return self.judge(test_result)

                if test_result != self.exp_result:
                    return self.judge(test_result)

                test_util.test_logger("Checking pass for [vip:] %s Port Forwardings TCP rules for allowed Cidr: %s from [vm:] %s " % \
                        (vip.uuid, allowed_vr_ip, allowed_vr_vm.uuid))

                #check denied vr access.
                allowed_ports = []
                denied_ports = all_ports

                #the denied vr might be in other pf rule.
                if denied_vr_ip in pf_tcp_dict.keys():
                    allowed_ports, denied_ports = \
                            self.count_pf_allowed_denied_ports(
                            pf_tcp_dict[denied_vr_ip], 
                            allowed_ports, 
                            denied_ports)

                try:
                    test_lib.lib_check_ports_in_a_command(denied_vr_vm, denied_vr_ip, vipIp, allowed_ports, denied_ports, target_vm)
                except:
                    traceback.print_exc(file=sys.stdout)
                    test_util.test_logger("Catch failure when checking [vip:] %s Port Forwarding TCPs for not allowed Cidr from [vm:] %s" % (vip.uuid, allowed_vr_vm.uuid))
                    test_result = False
                    if test_result != self.exp_result:
                        return self.judge(test_result)

                test_util.test_logger("Checking pass for Port Forwarding TCP [rule:] %s for not allowed Cidr from [vm:] %s . All ports should be blocked. " % (vip.uuid, allowed_vr_vm.uuid))
                if test_result != self.exp_result:
                    return self.judge(test_result)

        #check pf_udp rule existance.
        for pf in pf_udp_list:
            test_result = test_lib.lib_check_vm_pf_rule_exist_in_iptables(pf.get_port_forwarding())
            test_util.test_logger('Check result: [Port Forwarding] %s finishes UDP rule existance testing' % pf.get_port_forwarding().uuid)
            return self.judge(test_result)
                
        test_util.test_logger('Check result: [Port Forwarding] finishes [vip:] %s TCP testing.' % vip.uuid)
        return self.judge(test_result)

class vip_icmp_checker(checker_header.TestChecker):
    '''check VIP IP icmp status. If VIP is not pingable, return 
    self.judge(False). If yes, return self.judge(True)'''
    def check(self):
        super(vip_icmp_checker, self).check()
        test_result = True
        vip = self.test_obj.get_vip()
        vipIp = vip.ip
        vip_l3_uuid = vip.l3NetworkUuid
        any_vr = test_lib.lib_find_vr_by_l3_uuid(vip_l3_uuid)[0]
        try:
            test_lib.lib_check_ping(any_vr, vipIp)
        except:
            test_util.test_logger("Catch exception: [vip:] %s [IP:] %s is not pingable from [vm:] %s " % (vip.uuid, vipIp, any_vr.uuid))
            test_result = False
        else:
            test_util.test_logger("Successful ping [vip:] %s [IP:] %s from [vm:] %s " % (vip.uuid, vipIp, any_vr.uuid))
        return self.judge(test_result)

def _sg_rule_exist_for_pf(nic, pf_rule):
    '''
    When nic is in any SG, if its port forwarding protocol and port are not 
    listed in that SG rules, it returns True, otherwise returns False.
    '''
    conditions = res_ops.gen_query_conditions('vmNicUuid', '=', nic.uuid)
    sg_nics = res_ops.query_resource(res_ops.VM_SECURITY_GROUP, conditions)
    #No SG
    if not sg_nics:
        return False

    return _sg_rule_exist(sg_nics, 
            pf_rule.protocolType,
            pf_rule.privatePortStart, 
            pf_rule.privatePortEnd, 
            pf_rule.allowedCidr)

def _sg_rule_exist(sg_nics, protocol, start_port, end_port, allowed_cidr):
    for sg_nic in sg_nics:
        conditions = res_ops.gen_query_conditions('uuid', '=', sg_nic.securityGroupUuid)
        sg = res_ops.query_resource(res_ops.SECURITY_GROUP, conditions)[0]
        if not sg.rules:
            continue

        for rule in sg.rules:
            if rule.type == inventory.INGRESS:
                #PF testing only checking Ingress Rule
                if rule.protocol == protocol \
                        and rule.allowedCidr == allowed_cidr \
                        and rule.startPort == start_port \
                        and rule.endPort == end_port:
                    #SG rule is exist, but it is aligned with PF's rule. 
                    return False
    #No SG ingress rules, ingress default will be blocked.
    return True

def _find_denied_vr(cluster_uuid, l3_uuid, allowed_vr_uuid_list):
    conditions = res_ops.gen_query_conditions('clusterUuid', '=', cluster_uuid)
    conditions = res_ops.gen_query_conditions('applianceVmType', '=', 'VirtualRouter', conditions)
    all_virtualrouter_vrs = res_ops.query_resource(res_ops.APPLIANCE_VM, conditions)
    conditions = res_ops.gen_query_conditions('clusterUuid', '=', cluster_uuid)
    conditions = res_ops.gen_query_conditions('applianceVmType', '=', 'vrouter', conditions)
    all_vyos_vrs = res_ops.query_resource(res_ops.APPLIANCE_VM, conditions)

    for vr in all_virtualrouter_vrs+all_vyos_vrs:
        if not vr.uuid in allowed_vr_uuid_list:
            for vm_nic in vr.vmNics:
                if vm_nic.l3NetworkUuid == l3_uuid:
                    return vr

