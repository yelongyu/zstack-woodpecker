import zstackwoodpecker.header.checker as checker_header
import zstackwoodpecker.header.vm as vm_header
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state

import zstacklib.utils.http as http
import zstacklib.utils.linux as linux
import zstacklib.utils.list_ops as list_ops
import zstacklib.utils.jsonobject as jsonobject

import zstacktestagent.plugins.vm as vm_plugin
import zstacktestagent.plugins.host as host_plugin
import zstacktestagent.testagent as testagent
import apibinding.inventory as inventory
import os

import sys
import traceback

port_header = test_state.Port

class sg_common_checker(checker_header.TestChecker):
    '''define the sg common checker with same exeception handler'''
    def __init__(self):
        #Target nic_uuid for test. 
        self.nic_uuid = None
        self.test_vm = None
        super(sg_common_checker, self).__init__()

    def check(self):
        super(sg_common_checker, self).check()

    def judge(self, test_result):
        super(sg_common_checker, self).judge(test_result)

    def set_nic_uuid(self, nic_uuid):
        self.nic_uuid = nic_uuid

    def set_vm(self, vm):
        self.test_vm = vm

class zstack_vcenter_sg_db_exist_checker(sg_common_checker):
    '''check vcenter sg existence in database. If it is in db, 
        return self.judge(True). If not, return self.judge(False)'''
    def __init__(self):
        super(zstack_vcenter_sg_db_exist_checker, self).__init__()

    def check(self):
        super(zstack_vcenter_sg_db_exist_checker, self).check()
        sg_list = self.test_obj.get_sg_list_by_nic(self.nic_uuid)

        if not sg_list:
            conditions = res_ops.gen_query_conditions('vmNicUuid', '=', self.nic_uuid)
            nic_sg = res_ops.query_resource(res_ops.VM_SECURITY_GROUP, conditions)
            if not nic_sg:
                test_util.test_logger('Check result: No [Security Group] is found in database for [nic:] %s.' % self.nic_uuid)
                return self.judge(False)
            else:
                test_util.test_warn('Check result: [Security Group] is found in database for [nic:] %s. It is not consistent with test_sg record.' % self.nic_uuid)
                return self.judge(True)

        for test_sg in sg_list:
            try:
                conditions = res_ops.gen_query_conditions('uuid', '=', test_sg.security_group.uuid)
                sg = res_ops.query_resource(res_ops.SECURITY_GROUP, conditions)[0]
            except Exception as e:
                traceback.print_exc(file=sys.stdout)
                test_util.test_logger('Check result: [Security Group Inventory uuid:] %s does not exist in database.' % test_sg.security_group.uuid)
                return self.judge(False)

        test_util.test_logger('Check result: [SecurityGroup Inventory uuid:] %s exist in database.' % sg.uuid)
        return self.judge(True)

#class zstack_vcenter_sg_rule_db_exist_checker(sg_common_checker):
#    '''check vcenter sg rule existence in database. If it is in db, 
#        return self.judge(True). If not, return self.judge(False)'''
#    def __init__(self):
#        #Target nic_uuid for test. 
#        super(zstack_vcenter_sg_db_exist_checker, self).__init__()
#
#    def check(self):
#        try:
#            conditions = res_ops.gen_query_conditions('uuid', '=', self.test_obj.security_group.uuid)
#            sg = res_ops.query_resource(res_ops.SECURITY_GROUP, conditions)[0]
#        except Exception as e:
#            traceback.print_exc(file=sys.stdout)
#            test_util.test_logger('Check result: [Security Group Inventory uuid:] %s does not exist in database.' % self.test_obj.security_group.uuid)
#            return self.judge(False)
#
#        sg_db_rules = sg.rules
#        sg_test_rules = self.test_obj.get_tcp_egress_all_rule() + self.test_obj.get_tcp_ingress_all_rule() + self.test_obj.get_udp_egress_all_rule() + self.test_obj.get_udp_ingress_all_rule() + self.test_obj.get_icmp_egress_all_rule() + self.test_obj.get_icmp_ingress_all_rule()
#        try:
#            rules_diff = rule_list_minus(sg_test_rules, sg_db_rules)
#            if not rules_diff:
#                test_util.test_logger('Check result: [SG:] %s rules checking pass.' % sg.uuid)
#                return self.judge(True)
#            else:
#                rules_diff_uuid = ''
#                for rule in rules_diff:
#                    rules_diff_uuid = rules_diff_uuid + rule.uuid + ' '
#                test_util.test_logger('Check result: [SG:] %s rules checking fail. Test rules have more rules than database: %s' % (sg.uuid, rules_diff_uuid))
#                return self.judge(False)
#        except:
#            rules_diff = rule_list_minus(sg_db_rules, sg_test_rules)
#            rules_diff_uuid = ''
#            for rule in rules_diff:
#                rules_diff_uuid = rules_diff_uuid + rule.uuid + ' '
#            test_util.test_logger('Check result: [SG:] %s rules checking fail. Test rules have less rules than database: %s' % (sg.uuid, rules_diff_uuid))
#            return self.judge(False)

def do_check_sg_rule_exist(params_pkg):
    test_vm = params_pkg[0]
    direction = params_pkg[1]
    additional_str = params_pkg[2]
    expected_result = params_pkg[3]

    if test_lib.lib_check_vm_sg_rule_exist_in_iptables(test_vm, direction, additional_string=additional_str):
        test_util.test_logger('[Security Group] find TCP ingress rule for [vm:] %s. ' % test_vm.uuid)
        test_result = True
    else:
        test_util.test_logger('[Security Group] does NOT find TCP ingress rule for [vm:] %s. ' % test_vm.uuid)
        test_result = False

    return expected_result == test_result

def check_sg_rule_exist(test_vm, protocol, direction, extra_str, exp_result):
    if linux.wait_callback_success(do_check_sg_rule_exist, (test_vm, direction, extra_str, exp_result), 5, 0.2):
        test_result = exp_result
        if exp_result:
            test_util.test_logger('Expected result: [Security Group] find %s %s rule for [vm:] %s. ' % (protocol, direction, test_vm.uuid))
        else:
            test_util.test_logger('Expected result: [Security Group] FAIL to find %s %s rule for [vm:] %s in 5 seconds. ' % (protocol, direction, test_vm.uuid))
    else:
        test_result = not exp_result
        if exp_result:
            test_util.test_logger('Unexpected result: [Security Group] Not find %s %s rule for [vm:] %s. ' % (protocol, direction, test_vm.uuid))
        else:
            test_util.test_logger('Unexpected result: [Security Group]  find %s %s rule for [vm:] %s in 5 seconds. ' % (protocol, direction, test_vm.uuid))

    return test_result

def print_iptables(vm):
    host = test_lib.lib_find_host_by_vm(vm)
    try:
        if not host.managementIp:
            test_util.test_logger('did not find host for vm: %s ' % vm.uuid)
            return 
    except:
        test_util.test_logger('did not find host for vm: %s ' % vm.uuid)
        return 

    host_cmd = host_plugin.HostShellCmd()
    host_cmd.command = 'iptables-save'
    rspstr = http.json_dump_post(testagent.build_http_path(host.managementIp, host_plugin.HOST_SHELL_CMD_PATH), host_cmd)
    rsp = jsonobject.loads(rspstr)
    if rsp.return_code != 0:
        test_util.test_logger('can not dump iptables on host: %s; reason: %s' % (host.managementIp, rsp.stderr))
    else:
        test_util.test_logger('iptables-save result on %s: %s' % (host.managementIp, rsp.stdout))

class zstack_vcenter_sg_tcp_ingress_exist_checker(sg_common_checker):
    def __init__(self):
        super(zstack_vcenter_sg_tcp_ingress_exist_checker, self).__init__()

    def check(self):
        test_util.test_dsc('Check TCP ingress rules iptable state')
        super(zstack_vcenter_sg_tcp_ingress_exist_checker, self).check()
        test_result = True
        if self.nic_uuid:
            test_vm = test_lib.lib_get_vm_by_nic(self.nic_uuid)
        else:
            test_vm = self.test_vm

        test_result = check_sg_rule_exist(test_vm, inventory.TCP, inventory.INGRESS, "-p tcp", self.exp_result)

        test_util.test_logger('Check result: [Security Group] finishes TCP ingress iptables rule exsitence testing for [vm:] %s [nic:] %s' % (test_vm.uuid, self.nic_uuid))
        print_iptables(test_vm)
        return self.judge(test_result)

class zstack_vcenter_sg_tcp_egress_exist_checker(sg_common_checker):
    def __init__(self):
        super(zstack_vcenter_sg_tcp_egress_exist_checker, self).__init__()

    def check(self):
        test_util.test_dsc('Check TCP egress rules iptable state')
        super(zstack_vcenter_sg_tcp_egress_exist_checker, self).check()
        test_result = True
        if self.nic_uuid:
            test_vm = test_lib.lib_get_vm_by_nic(self.nic_uuid)
        else:
            test_vm = self.test_vm

        test_result = check_sg_rule_exist(test_vm, inventory.TCP, inventory.EGRESS, "-p tcp", self.exp_result)

        test_util.test_logger('Check result: [Security Group] pass TCP egress iptables rule exsitence testing for [vm:] %s [nic:] %s' % (test_vm.uuid, self.nic_uuid))
        print_iptables(test_vm)
        return self.judge(test_result)

class zstack_vcenter_sg_icmp_ingress_exist_checker(sg_common_checker):
    def __init__(self):
        super(zstack_vcenter_sg_icmp_ingress_exist_checker, self).__init__()

    def check(self):
        test_util.test_dsc('Check ICMP ingress rules iptable state')
        super(zstack_vcenter_sg_icmp_ingress_exist_checker, self).check()
        test_result = True
        if self.nic_uuid:
            test_vm = test_lib.lib_get_vm_by_nic(self.nic_uuid)
        else:
            test_vm = self.test_vm

        test_result = check_sg_rule_exist(test_vm, inventory.ICMP, inventory.INGRESS, "-p icmp", self.exp_result)

        test_util.test_logger('Check result: [Security Group] finishes ICMP ingress iptables rule exsitence testing for [vm:] %s [nic:] %s' % (test_vm.uuid, self.nic_uuid))
        if not test_result == self.exp_result:
            print_iptables(test_vm)
        return self.judge(test_result)

class zstack_vcenter_sg_icmp_egress_exist_checker(sg_common_checker):
    def __init__(self):
        super(zstack_vcenter_sg_icmp_egress_exist_checker, self).__init__()

    def check(self):
        test_util.test_dsc('Check ICMP egress rules iptable state')
        super(zstack_vcenter_sg_icmp_egress_exist_checker, self).check()
        test_result = True
        if self.nic_uuid:
            test_vm = test_lib.lib_get_vm_by_nic(self.nic_uuid)
        else:
            test_vm = self.test_vm

        test_result = check_sg_rule_exist(test_vm, inventory.ICMP, inventory.EGRESS, "-p icmp", self.exp_result)

        test_util.test_logger('Check result: [Security Group] pass ICMP egress iptables rule exsitence testing for [vm:] %s [nic:] %s' % (test_vm.uuid, self.nic_uuid))
        print_iptables(test_vm)
        return self.judge(test_result)

class zstack_vcenter_sg_tcp_egress_checker(sg_common_checker):
    '''check vcenter security group tcp egress connection.  
    Egress has high priority than ingress rule, because it needs firstly egress
    , then ingress. 
    Egress are defautly open to all, if there isn't egress rule. 
    '''
    def __init__(self):
        super(zstack_vcenter_sg_tcp_egress_checker, self).__init__()

    def check(self):
        super(zstack_vcenter_sg_tcp_egress_checker, self).check()
        all_ports = port_header.all_ports
        test_result = True
        nic = test_lib.lib_get_nic_by_uuid(self.nic_uuid)
        l3_uuid = nic.l3NetworkUuid
        test_util.test_dsc('Check TCP egress rules')
        if not 'DHCP' in test_lib.lib_get_l3_service_type(l3_uuid):
            test_util.test_logger("Skip SG test for [l3:] %s. Since it doesn't provide DHCP service, there isn't stable IP address for [nic:] %s." % (l3_uuid, self.nic_uuid))
            return self.judge(self.exp_result)

        stub_vm = self.test_obj.get_stub_vm(l3_uuid)
        if not stub_vm:
            test_util.test_warn('Did not find test stub vm for [target address:] %s. Skip test TCP egress rules network connection for this nic.' % target_addr)
            return self.judge(self.exp_result)
        stub_vm = stub_vm.vm

        stub_vm_ip = test_lib.lib_get_vm_nic_by_l3(stub_vm, l3_uuid).ip
        target_addr = '%s/32' % stub_vm_ip

        rules = self.test_obj.get_nic_tcp_egress_rule_by_addr(self.nic_uuid, target_addr)
        allowed_ports = []
        for rule in rules:
            rule_allowed_ports = port_header.get_ports(port_header.get_port_rule(rule.startPort))
            test_util.test_logger('[SG:] %s [egress rule]: %s allow to access [vm:] %s [ports]: %s ' % (rule.securityGroupUuid, rule.uuid, stub_vm.uuid, rule_allowed_ports))
            for port in rule_allowed_ports:
                if not port in allowed_ports:
                    allowed_ports.append(port)

        if not allowed_ports:
            #if no allowed port is added, it means no egress rule, so all ports
            # are allowed. 
            denied_ports = []
            allowed_ports = all_ports
        else:
            denied_ports = list_ops.list_minus(all_ports, allowed_ports)

        test_vm = test_lib.lib_get_vm_by_nic(nic.uuid)
        if test_vm.state == inventory.RUNNING:
            try:
                test_lib.lib_open_vm_listen_ports(stub_vm, all_ports, l3_uuid)
                test_lib.lib_check_vm_ports_in_a_command(test_vm, stub_vm, allowed_ports, denied_ports)
            except:
                traceback.print_exc(file=sys.stdout)
                test_util.test_logger('Check result: [Security Group] meets failure when checking TCP Egress rule for [vm:] %s [nic:] %s. ' % (test_vm.uuid, self.nic_uuid))
                test_result = False
        else:
            test_util.test_warn('Test [vm:] %s is not running. Skip SG TCP connection checker for this vm.' % test_vm.uuid)

        test_util.test_logger('Check result: [Security Group] finishes TCP egress testing for [vm nic:] %s' % self.nic_uuid)
        print_iptables(test_vm)
        return self.judge(test_result)

class zstack_vcenter_sg_tcp_ingress_checker(sg_common_checker):
    '''check vcenter security group tcp ingress connection. ''' 
    def __init__(self):
        super(zstack_vcenter_sg_tcp_ingress_checker, self).__init__()

    def check(self):
        super(zstack_vcenter_sg_tcp_ingress_checker, self).check()
        all_ports = port_header.all_ports
        test_result = True

        test_util.test_dsc('Check TCP ingress rules')
        nic = test_lib.lib_get_nic_by_uuid(self.nic_uuid)
        l3_uuid = nic.l3NetworkUuid
        if not 'DHCP' in test_lib.lib_get_l3_service_type(l3_uuid):
            test_util.test_logger("Skip SG test for [l3:] %s. Since it doesn't provide DHCP service, there isn't stable IP address for testint." % l3_uuid)
            return self.judge(self.exp_result)

        stub_vm = self.test_obj.get_stub_vm(l3_uuid)
        if not stub_vm:
            test_util.test_warn('Did not find test stub vm for [nic:] %s. Skip TCP ingress port checking for this nic.' % self.nic_uuid)
            return self.judge(self.exp_result)
        stub_vm = stub_vm.vm

        stub_vm_ip = test_lib.lib_get_vm_nic_by_l3(stub_vm, l3_uuid).ip
        target_addr = '%s/32' % stub_vm_ip

        rules = self.test_obj.get_nic_tcp_ingress_rule_by_addr(self.nic_uuid, target_addr)
        allowed_ports = []

        for rule in rules:
            rule_allowed_ports = port_header.get_ports(port_header.get_port_rule(rule.startPort))
            test_util.test_logger('[SG:] %s [ingress rule]: %s allow to access [nic:] %s [ports]: %s from [vm:] %s' % (rule.securityGroupUuid, rule.uuid, self.nic_uuid, rule_allowed_ports, stub_vm.uuid))
            for port in rule_allowed_ports:
                if not port in allowed_ports:
                    allowed_ports.append(port)

        if not allowed_ports:
            #If no allowed port, it means all denied. 
            denied_ports = list(all_ports)
        else:
            denied_ports = list_ops.list_minus(all_ports, allowed_ports)

        test_vm = test_lib.lib_get_vm_by_nic(nic.uuid)
        if test_vm.state == inventory.RUNNING:
            try:
                test_lib.lib_open_vm_listen_ports(test_vm, all_ports, l3_uuid)
                test_lib.lib_check_vm_ports_in_a_command(stub_vm, test_vm, allowed_ports, denied_ports)
            except:
                traceback.print_exc(file=sys.stdout)
                test_util.test_logger('Check result: [Security Group] meets failure when checking TCP ingress rule for [vm:] %s [nic:] %s. ' % (test_vm.uuid, self.nic_uuid))
                test_result = False
        else:
            test_util.test_warn('Test [vm:] %s is not running. Skip SG TCP ingress connection checker for this vm.' % test_vm.uuid)

        test_util.test_logger('Check result: [Security Group] finishes TCP ingress testing for [nic:] %s' % self.nic_uuid)
        print_iptables(test_vm)
        return self.judge(test_result)

class zstack_vcenter_sg_tcp_internal_vms_checker(sg_common_checker):
    '''check vcenter security group tcp connections between attached vms.
        based on security group defination. VMs with same SG group will 
        shared ingress ports and egress ports connection between each other.
    '''
    def __init__(self):
        super(zstack_vcenter_sg_tcp_internal_vms_checker, self).__init__()

    def check(self):
        test_util.test_dsc('Check TCP access between SG VMs.')
        super(zstack_vcenter_sg_tcp_internal_vms_checker, self).check()
        nic = test_lib.lib_get_nic_by_uuid(self.nic_uuid)
        l3_uuid = nic.l3NetworkUuid
        if not 'DHCP' in test_lib.lib_get_l3_service_type(l3_uuid):
            test_util.test_logger("Skip SG test for [l3:] %s, since it doesn't provide DHCP service" % l3_uuid)
            return self.judge(self.exp_result)

        test_result = True
        all_ports = port_header.all_ports

        tcp_egress_rules = self.test_obj.get_nic_tcp_egress_rules(self.nic_uuid)
        src_all_allowed_egress_ports = get_all_ports(tcp_egress_rules)
        if not src_all_allowed_egress_ports:
            src_all_allowed_egress_ports = list(all_ports)
        #src_all_allowed_ingress_ports = get_all_ports(self.test_obj.get_nic_tcp_ingress_rules(self.nic_uuid))
        #if not src_all_allowed_ingress_ports:
        #    src_all_allowed_ingress_ports = list(all_ports)

        nic_sg_list = self.test_obj.get_sg_list_by_nic(self.nic_uuid)
        src_vm = test_lib.lib_get_vm_by_nic(self.nic_uuid)

        #save all shared sg for self.nic_uuid, the key was the other nic_uuid, who shared sg with self.nic_uuid
        nic_shared_sg_dict = {}

        #find all other nic shared with same sg.
        for sg in nic_sg_list:
            same_l3_nic_list = list(sg.get_attached_nics_by_l3(l3_uuid))
            if len(same_l3_nic_list) == 1:
                test_util.test_logger("Skip [SG:] %s, since there is not 2nd VM is attached in this SG." % sg.security_group.uuid)
                continue

            if self.nic_uuid in same_l3_nic_list:
                same_l3_nic_list.remove(self.nic_uuid)

            for nic_uuid in same_l3_nic_list:
                if not nic_shared_sg_dict.has_key(nic_uuid):
                    nic_shared_sg_dict[nic_uuid] = [sg]
                elif not sg in nic_shared_sg_dict[nic_uuid]:
                    nic_shared_sg_dict[nic_uuid].append(sg)

        #for each shared sg nic to test.
        for nic_uuid in nic_shared_sg_dict.keys():
            dst_vm = test_lib.lib_get_vm_by_nic(nic_uuid)

            if dst_vm.state != inventory.RUNNING:
                test_util.test_logger("Skip [vm:] %s, since it is not running." % dst_vm.uuid)
                continue

            allowed_ingress_ports = []
            allowed_egress_ports = []

            #find out all shared SG ingress ports and egress ports
            for sg in nic_shared_sg_dict[nic_uuid]:
                sg_allowed_ingress_ports = \
                        get_all_ports(sg.get_tcp_ingress_all_rule())

                for port in sg_allowed_ingress_ports:
                    if not port in allowed_ingress_ports:
                        allowed_ingress_ports.append(port)

                sg_allowed_egress_ports = \
                        get_all_ports(sg.get_tcp_egress_all_rule())

                if not sg_allowed_egress_ports:
                    sg_allowed_egress_ports = list(all_ports)

                for port in sg_allowed_egress_ports:
                    if not port in allowed_egress_ports:
                        allowed_egress_ports.append(port)

            #find out all not shared SG ingress and egress ports for target 
            src_vm_allowedCidr = '%s/32' % test_lib.lib_get_nic_by_uuid(self.nic_uuid).ip
            dst_vm_allowedCidr = '%s/32' % test_lib.lib_get_nic_by_uuid(nic_uuid).ip

            #query all other left SG rules, which might not shard between src_vm
            #and dst_vm, but setting specifically for these two vms. 
            for in_port in get_all_ports(self.test_obj.get_nic_tcp_ingress_rule_by_addr(nic_uuid, src_vm_allowedCidr)):
                if not in_port in allowed_ingress_ports:
                    allowed_ingress_ports.append(in_port)

            for out_port in get_all_ports(self.test_obj.get_nic_tcp_egress_rule_by_addr(self.nic_uuid, dst_vm_allowedCidr)):
                if not out_port in allowed_egress_ports:
                    allowed_egress_ports.append(out_port)

            dst_all_allowed_ingress_ports = get_all_ports(self.test_obj.get_nic_tcp_ingress_rules(nic_uuid))

            if not dst_all_allowed_ingress_ports:
                test_util.test_logger('Destinated VM nic: %s does not allow any ingress rule, since it does not set any ingress rule' % nic_uuid)
                continue
            #if (not allowed_ingress_ports) \
            #    and (not dst_all_allowed_ingress_ports) \
            #    and (not self.test_obj.get_nic_udp_ingress_rules(nic_uuid)) \
            #    and (not self.test_obj.get_nic_icmp_ingress_rules(nic_uuid)):
            #        
            #    allowed_ingress_ports = list(all_ports)

            #if not find suitable port, means all egress opened. 
            if (not src_all_allowed_egress_ports) \
                and (not self.test_obj.get_nic_udp_egress_rules(nic_uuid)) \
                and (not self.test_obj.get_nic_icmp_egress_rules(nic_uuid)):

                allowed_egress_ports = list(all_ports)

            shared_ports = get_shared_ports(allowed_egress_ports, \
                    allowed_ingress_ports)

            not_shared_ports = list_ops.list_minus(all_ports, shared_ports)

            test_lib.lib_open_vm_listen_ports(dst_vm, all_ports, l3_uuid)
            try:
                test_lib.lib_check_vm_ports(src_vm, dst_vm, shared_ports, \
                        not_shared_ports)
            except:
                traceback.print_exc(file=sys.stdout)
                test_util.test_logger('Check result: [Security Group] meets failure when checking TCP Egress rule between [src_vm:] %s and [dst_vm:] %s. ' % (src_vm.uuid, dst_vm.uuid))
                test_result = False
                break

        test_util.test_logger('Check result: [Security Group] finishes TCP connection testing from [vm:] %s to other VMs in same SG.' % src_vm.uuid)
        print_iptables(src_vm)
        return self.judge(test_result)

class zstack_vcenter_sg_udp_ingress_checker(sg_common_checker):
    '''check vcenter security group udp ingress rule. 
    The main checking will be check if rule is there.
    ''' 
    def __init__(self):
        super(zstack_vcenter_sg_udp_ingress_checker, self).__init__()

    def check(self):
        super(zstack_vcenter_sg_udp_ingress_checker, self).check()
        test_util.test_dsc('Check UDP ingress rules')
        test_result = True
        if self.nic_uuid:
            test_vm = test_lib.lib_get_vm_by_nic(self.nic_uuid)
        else:
            test_vm = self.test_vm

        test_result = check_sg_rule_exist(test_vm, inventory.UDP, inventory.INGRESS, "-p udp", self.exp_result)

        test_util.test_logger('Check result: [Security Group] finishes UDP ingress testing for [vm:] %s [nic:] %s' % (test_vm.uuid, self.nic_uuid))
        print_iptables(test_vm)
        return self.judge(test_result)

class zstack_vcenter_sg_udp_egress_checker(sg_common_checker):
    '''check vcenter security group udp egress rule. 
    The main checking will be check if rule is there.
    ''' 
    def __init__(self):
        super(zstack_vcenter_sg_udp_egress_checker, self).__init__()

    def check(self):
        test_util.test_dsc('Check UDP egress rules')
        super(zstack_vcenter_sg_udp_egress_checker, self).check()
        test_result = True
        if self.nic_uuid:
            test_vm = test_lib.lib_get_vm_by_nic(self.nic_uuid)
        else:
            test_vm = self.test_vm

        test_result = check_sg_rule_exist(test_vm, inventory.UDP, inventory.EGRESS, "-p udp", self.exp_result)

        test_util.test_logger('Check result: [Security Group] finishes UDP egress testing for [vm:] %s [nic:] %s' % (test_vm.uuid, self.nic_uuid))
        return self.judge(test_result)

class zstack_vcenter_sg_icmp_ingress_checker(sg_common_checker):
    '''check vcenter security group icmp ingress rule. 
    ''' 
    def __init__(self):
        super(zstack_vcenter_sg_icmp_ingress_checker, self).__init__()

    def check(self):
        super(zstack_vcenter_sg_icmp_ingress_checker, self).check()
        test_result = True

        nic = test_lib.lib_get_nic_by_uuid(self.nic_uuid)
        l3_uuid = nic.l3NetworkUuid
        test_util.test_dsc('Check ICMP ingress rules')
        if not 'DHCP' in test_lib.lib_get_l3_service_type(l3_uuid):
            test_util.test_logger("Skip SG test for [l3:] %s. Since it doesn't provide DHCP service, there isn't stable IP address for testint." % l3_uuid)
            return self.judge(self.exp_result)

        stub_vm = self.test_obj.get_stub_vm(l3_uuid)
        if not stub_vm:
            test_util.test_warn('Did not find test stub vm for [target address:] %s. Skip testing some TCP rules' % target_addr)
            return self.judge(self.exp_result)
        stub_vm = stub_vm.vm

        stub_vm_ip = test_lib.lib_get_vm_nic_by_l3(stub_vm, l3_uuid).ip
        target_addr = '%s/32' % stub_vm_ip


        test_vm = test_lib.lib_get_vm_by_nic(nic.uuid)
        if test_vm.state == inventory.RUNNING:
            rules = self.test_obj.get_nic_icmp_ingress_rule_by_addr(self.nic_uuid, target_addr)
            target_ip = test_lib.lib_get_vm_ip_by_l3(test_vm, l3_uuid)
            if rules:
                if test_lib.lib_check_ping(stub_vm, target_ip, no_exception=True):
                    test_util.test_logger('Check result: [Security Group] pass ICMP ingress rule checking to ping [vm:] %s from [vm:] %s' % (test_vm.uuid, stub_vm.uuid))
                else:
                    test_util.test_logger('Check result: [Security Group] meets failure to ping [vm:] %s from [vm:] %s when checking ICMP ingress rule. ' % (test_vm.uuid, stub_vm.uuid))
                    test_result = False
            else:
                if not test_lib.lib_check_ping(stub_vm, target_ip, no_exception=True):
                    test_util.test_logger('Check result: [Security Group] pass ICMP ingress rule checking to ping [vm:] %s from [vm:] %s. Expected failure.' % (test_vm.uuid, stub_vm.uuid))
                else:
                    test_util.test_logger('Check result: [Security Group] meet failure when checking ICMP ingress rule to ping [vm:] %s from [vm:] %s. Unexpected ping successfully.' % (test_vm.uuid, stub_vm.uuid))
        else:
            test_util.test_warn('Test [vm:] %s is not running. Skip SG ICMP ingress checker for this vm.' % test_vm.uuid)
            
        test_util.test_logger('Check result: [Security Group] pass ICMP ingress testing for [vm:] %s [nic:] %s' % (test_vm.uuid, self.nic_uuid))
        print_iptables(test_vm)
        return self.judge(test_result)

class zstack_vcenter_sg_icmp_egress_checker(sg_common_checker):
    '''check vcenter security group icmp egress rule. 
    ''' 
    def __init__(self):
        super(zstack_vcenter_sg_icmp_egress_checker, self).__init__()

    def check(self):
        super(zstack_vcenter_sg_icmp_egress_checker, self).check()
        test_result = True

        nic = test_lib.lib_get_nic_by_uuid(self.nic_uuid)
        l3_uuid = nic.l3NetworkUuid
        test_util.test_dsc('Check ICMP egress rules')
        if not 'DHCP' in test_lib.lib_get_l3_service_type(l3_uuid):
            test_util.test_logger("Skip SG test for [l3:] %s. Since it doesn't provide DHCP service, there isn't stable IP address for testint." % l3_uuid)
            return self.judge(self.exp_result)

        stub_vm = self.test_obj.get_stub_vm(l3_uuid)
        if not stub_vm:
            test_util.test_warn('Did not find test stub vm for [target address:] %s. Skip testing some TCP rules' % target_addr)
            return self.judge(self.exp_result)
        stub_vm = stub_vm.vm

        stub_vm_ip = test_lib.lib_get_vm_nic_by_l3(stub_vm, l3_uuid).ip
        target_addr = '%s/32' % stub_vm_ip

        test_vm = test_lib.lib_get_vm_by_nic(nic.uuid)
        if test_vm.state == inventory.RUNNING:
            rules = self.test_obj.get_nic_icmp_egress_rule_by_addr(self.nic_uuid, target_addr)
            target_ip = test_lib.lib_get_vm_ip_by_l3(stub_vm, l3_uuid)
            if rules:
                if test_lib.lib_check_ping(test_vm, target_ip, no_exception=True):
                    test_util.test_logger('Check result: [Security Group] pass ICMP egress rule checking to ping [vm:] %s from [vm:] %s' % (stub_vm.uuid, test_vm.uuid))
                else:
                    test_util.test_logger('Check result: [Security Group] meet failure to ping [vm:] %s from [vm:] %s when checking ICMP egress rule. ' % (stub_vm.uuid, test_vm.uuid))
                    test_result = False
            else:
                if test_lib.lib_check_ping(test_vm, target_ip, no_exception=True):
                    test_util.test_logger('Check result: [Security Group] pass ICMP egress rule checking to ping [vm:] %s from [vm:] %s.' % (stub_vm.uuid, test_vm.uuid))
                else:
                    test_util.test_logger('Check result: [Security Group] meet failure when checking ICMP egress rule to ping [vm:] %s from [vm:] %s when checking ICMP egress rule. Unexpected ping failure, since there is not icmp egress rule was found.' % (stub_vm.uuid, test_vm.uuid))
        else:
            test_util.test_warn('Test [vm:] %s is not running. Skip SG ICMP egress checker for this vm.' % test_vm.uuid)
            
        test_util.test_logger('Check result: [Security Group] pass ICMP egress testing for [vm:] %s [nic:] %s' % (test_vm.uuid, self.nic_uuid))
        print_iptables(test_vm)
        return self.judge(test_result)

class zstack_vcenter_sg_icmp_internal_vms_checker(sg_common_checker):
    '''
    check vcenter security group icmp rule between attached VMs. 
    Only check the icmp ingress rules. If ingress rule is not set, there isn't
    any icmp can reach vm.
    ''' 
    def __init__(self):
        super(zstack_vcenter_sg_icmp_internal_vms_checker, self).__init__()

    def check(self):
        super(zstack_vcenter_sg_icmp_internal_vms_checker, self).check()
        #only check ingress icmp.
        if not self.test_obj.get_nic_icmp_ingress_rules(self.nic_uuid):
            test_util.test_logger("Skip SG internal ICMP test, since there isn't icmp ingress rules for nic: %s" % self.nic_uuid)
            return self.judge(self.exp_result)

        test_result = True

        test_util.test_dsc('Check ICMP rules between attached VMs')
        nic_sg_list = self.test_obj.get_sg_list_by_nic(self.nic_uuid)
        nic = test_lib.lib_get_nic_by_uuid(self.nic_uuid)
        dst_vm = test_lib.lib_get_vm_by_nic(self.nic_uuid)
        l3_uuid = nic.l3NetworkUuid
        if not 'DHCP' in test_lib.lib_get_l3_service_type(l3_uuid):
            test_util.test_logger("Skip SG test for [l3:] %s. Since it doesn't provide DHCP service, test vm's IP address is not stable." % l3_uuid)
            return self.judge(self.exp_result)

        target_ip = nic.ip
        allowed_src_nic_list = []
        temp_allowed_src_nic_list = []
        denied_nic_list = []
        for sg in nic_sg_list:
            same_l3_nic_list = list(sg.get_attached_nics_by_l3(l3_uuid))
            if len(same_l3_nic_list) < 2 :
                test_util.test_logger("Skip [l3:] %s ICMP internal VMs checking, since there is less 2 SG VMs in this l3." % l3_uuid)
                continue

            #if source vm's udp and tcp engress rules exist, while icmp ingress
            # rule does not exist, the src vm egress icmp should be denied.
            #minus current nic.
            nic_list_temp = list_ops.list_minus(list(same_l3_nic_list), [nic.uuid])
            for nic_uuid in nic_list_temp:
                source_nic_egress_icmp_rules = \
                        self.test_obj.get_nic_icmp_egress_rules(nic_uuid)
                if not source_nic_egress_icmp_rules:
                    if self.test_obj.get_nic_tcp_egress_rules(nic_uuid) or \
                            self.test_obj.get_nic_udp_egress_rules(nic_uuid):
                        if not nic_uuid in denied_nic_list:
                            denied_nic_list.append(nic_uuid)
                    else:
                        if not nic_uuid in temp_allowed_src_nic_list:
                            temp_allowed_src_nic_list.append(nic_uuid)
                else:
                    for rule in source_nic_egress_icmp_rules:
                        if target_ip in rule.allowedCidr:
                            if not nic_uuid in allowed_src_nic_list:
                                allowed_src_nic_list.append(nic_uuid)
                            break
                    else:
                        if not nic_uuid in denied_nic_list:
                            denied_nic_list.append(nic_uuid)

        for nic_uuid in list(denied_nic_list):
            if nic_uuid in allowed_src_nic_list:
                denied_nic_list.remove(nic_uuid)

        for nic_uuid in temp_allowed_src_nic_list:
            if not nic_uuid in denied_nic_list and \
                    not nic_uuid in allowed_src_nic_list:
                allowed_src_nic_list.append(nic_uuid)


        allowed_vm_list = get_all_running_vms_by_nics(allowed_src_nic_list)
        denied_vm_list = get_all_running_vms_by_nics(denied_nic_list)

        for src_vm in allowed_vm_list:
            if test_lib.lib_check_ping(src_vm, target_ip, no_exception=True):
                test_util.test_logger('Check result: [Security Group] pass ICMP rule checking to ping [vm:] %s from [vm:] %s' % (src_vm.uuid, dst_vm.uuid))
            else:
                test_util.test_logger('Check result: [Security Group] is FAIL to ping [vm:] %s from [vm:] %s when checking ICMP rule. ' % (src_vm.uuid, dst_vm.uuid))
                test_result = False

        for src_vm in denied_vm_list:
            if test_lib.lib_check_ping(src_vm, target_ip, no_exception=True):
                test_util.test_logger('Unexpected Result: [Security Group] ICMP ping [vm:] %s from [vm:] %s successfully' % (src_vm.uuid, dst_vm.uuid))
                test_result = False
            else:
                test_util.test_logger('Expected Result: [Security Group] FAIL to ping [vm:] %s from [vm:] %s when checking ICMP rule. ' % (src_vm.uuid, dst_vm.uuid))

        test_util.test_logger('Check result: [Security Group] finishes ICMP connection testing from other attached VMs to target [vm:] %s in same SG.' % dst_vm.uuid)
        print_iptables(dst_vm)
        return self.judge(test_result)

def get_all_running_vms_by_nics(nic_list):
    vm_list = []
    for nic_uuid in nic_list:
        test_vm = test_lib.lib_get_vm_by_nic(nic_uuid)
        if test_vm.state == inventory.RUNNING:
            vm_list.append(test_vm)
    return vm_list

#new list = list1 && list2
def get_shared_ports(list1, list2):
    shared_ports = list(list1)
    for item in list1:
        if not item in list2:
            shared_ports.remove(item)

    return shared_ports

#new list = list1 - list2
def rule_list_minus(list1, list2):
    new_list = list(list1)
    for item2 in list2:
        for item1 in list1:
            if item1.uuid == item2.uuid:
                new_list.remove(item1)
    return new_list

#same l3 will have same utility VM, so we will assume AllowedCidr is same.
#Then we can only care about the ports
def get_all_ports(rule_list):
    rule_ports = []
    for rule in rule_list:
        ports = port_header.get_ports(port_header.get_port_rule(rule.startPort))
        if not ports[0] in rule_ports:
            rule_ports.extend(ports)
    return rule_ports

def get_test_stub_vm_by_ip(test_obj, target_ip):
    for l3_uuid in test_obj.get_all_l3():
        stub_vm = test_obj.get_stub_vm(l3_uuid)
        if stub_vm:
            if test_lib.lib_get_vm_ip_by_l3(stub_vm.vm, l3_uuid) == target_ip:
                return l3_uuid, stub_vm.vm

    return None, None
