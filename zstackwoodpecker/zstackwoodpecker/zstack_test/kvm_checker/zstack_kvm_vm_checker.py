import os
import sys
import traceback

import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.header.checker as checker_header
import zstackwoodpecker.header.vm as vm_header
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstacklib.utils.http as http
import zstacklib.utils.jsonobject as jsonobject
import zstacklib.utils.linux as linux
import apibinding.inventory as inventory
import zstacktestagent.plugins.vm as vm_plugin
import zstacktestagent.plugins.host as host_plugin
import zstacktestagent.testagent as testagent

class zstack_kvm_vm_running_checker(checker_header.TestChecker):
    '''check kvm vm running status. If it is running, return self.judge(True). 
        If it is stopped, return self.judge(False)'''
    def check(self):
        super(zstack_kvm_vm_running_checker, self).check()

        vm = self.test_obj.vm
        host = test_lib.lib_get_vm_host(vm)
        if test_lib.lib_gen_serial_script_for_vm(vm):
            test_util.test_logger('Check [vm:] /tmp/serial_log_gen.sh is ready on [host:] %s [uuid:] %s.' % (host.name, host.uuid))

        test_lib.lib_install_testagent_to_host(host)
        test_lib.lib_set_vm_host_l2_ip(vm)
        cmd = vm_plugin.VmStatusCmd()
        cmd.vm_uuids = [vm.uuid]
        test_util.test_logger('Check [vm:] %s running status on host [name:] %s [uuid:] %s.' % (vm.uuid, host.name, host.uuid))
        rspstr = http.json_dump_post(testagent.build_http_path(host.managementIp, vm_plugin.VM_STATUS), cmd)
        rsp = jsonobject.loads(rspstr)
        check_result = rsp.vm_status[vm.uuid].strip()
        serial_log = rsp.vm_status[vm.uuid+"_log"].strip()
        if check_result  == vm_plugin.VmAgent.VM_STATUS_RUNNING :
            test_util.test_logger('Check result: [vm:] %s is RUNNING on [host:] %s .' % (vm.uuid, host.name))
            test_util.test_logger('Check [vm:] Start to check serial log for error for [vm:] %s on [host:] %s .' % (vm.uuid, host.name))
            _cmd = "grep -Ei 'kernel panic|call trace|BUG.*NULL|general protection fault|watchdog detected|BUG.*soft lockup|watchdog timeout|fatal exception' /tmp/%s" % (serial_log)
            _rsp = test_lib.lib_execute_ssh_cmd(host.managementIp, host.username, os.environ.get('hostPassword'), _cmd)

            if _rsp:
                test_util.test_logger('Check result: [vm:] %s is somehow panic on [host:] %s .' % (vm.uuid, host.name))
                _cmd = "cat /tmp/%s" % (serial_log)
                _rsp = test_lib.lib_execute_ssh_cmd(host.managementIp, host.username, os.environ.get('hostPassword'), _cmd)
                test_util.test_logger('Check result: [vm:] %s serial output: %s .' % (vm.uuid, _rsp))
                return self.judge(False)
            else:
                _cmd = "if [ ! -s /tmp/%s ]; then echo 'empty'; fi" % (serial_log)
                _rsp = test_lib.lib_execute_ssh_cmd(host.managementIp, host.username, os.environ.get('hostPassword'), _cmd)
                if _rsp and "empty" in _rsp:
                    test_util.test_logger('Check [vm:] %s is windows or serial console is not enabled, skip the serial log check' % (vm.uuid))

                test_util.test_logger('Check result: [vm:] %s serial log check is passed on [host:] %s .' % (vm.uuid, host.name))
                return self.judge(True)
        else:
            test_util.test_logger('Check result: [vm:] %s is NOT RUNNING on [host:] %s . ; Expected status: %s ; Actual status: %s' % (vm.uuid, host.name, vm_plugin.VmAgent.VM_STATUS_RUNNING, check_result))
            return self.judge(False)

class zstack_kvm_vm_destroyed_checker(checker_header.TestChecker):
    '''check kvm vm destroyed status. If it is not running and not stopped,
        return self.judge(True). If either is true, return self.judge(False)'''
    def check(self):
        super(zstack_kvm_vm_destroyed_checker, self).check()
        vm = self.test_obj.vm
        host = test_lib.lib_get_vm_host(vm)
        test_lib.lib_install_testagent_to_host(host)
        test_lib.lib_set_vm_host_l2_ip(vm)
        cmd = vm_plugin.VmStatusCmd()
        cmd.vm_uuids = [vm.uuid]
        test_util.test_logger('Check [vm:] %s status on host [name:] %s [uuid:] %s.' % (vm.uuid, host.name, host.uuid))
        rspstr = http.json_dump_post(testagent.build_http_path(host.managementIp, vm_plugin.VM_STATUS), cmd)
        rsp = jsonobject.loads(rspstr)
        check_result = rsp.vm_status[vm.uuid].strip()
        if check_result != vm_plugin.VmAgent.VM_STATUS_RUNNING and check_result != vm_plugin.VmAgent.VM_STATUS_STOPPED:
            test_util.test_logger('Check result: [vm:] %s is DESTROYED on [host:] %s .' % (vm.uuid, host.name))
            return self.judge(True)
        else:
            test_util.test_logger('Check result: [vm:] %s is NOT DESTROYED on [host:] %s . vm status is: %s' % (vm.uuid, host.name, check_result))
            return self.judge(False)

class zstack_kvm_vm_stopped_checker(checker_header.TestChecker):
    '''check kvm vm stopped status. If it is stopped, return self.judge(True). 
        If it is stopped, return self.judge(False)

        This checker is deprecated, since the stopped VM will also removed from
        host libvirt.         
        '''
    def check(self):
        super(zstack_kvm_vm_stopped_checker, self).check()

        return self.judge(self.exp_result)

        vm = self.test_obj.vm
        host = test_lib.lib_get_vm_host(vm)
        test_lib.lib_install_testagent_to_host(host)
        test_lib.lib_set_vm_host_l2_ip(vm)
        cmd = vm_plugin.VmStatusCmd()
        cmd.vm_uuids = [vm.uuid]
        test_util.test_logger('Check [vm:] %s stopped status on host [name:] %s [uuid:] %s.' % (vm.uuid, host.name, host.uuid))
        rspstr = http.json_dump_post(testagent.build_http_path(host.managementIp, vm_plugin.VM_STATUS), cmd)
        rsp = jsonobject.loads(rspstr)
        check_result = rsp.vm_status[vm.uuid].strip()
        if check_result == vm_plugin.VmAgent.VM_STATUS_STOPPED:
            test_util.test_logger('Check result: [vm:] %s is STOPPED on [host:] %s .' % (vm.uuid, host.name))
            return self.judge(True)
        else:
            test_util.test_logger('Check result: [vm:] %s is NOT STOPPED on [host:] %s . ; Expected status: %s ; Actual status: %s' % (vm.uuid, host.name, vm_plugin.VmAgent.VM_STATUS_STOPPED, check_result))
            return self.judge(False)

class zstack_kvm_vm_suspended_checker(checker_header.TestChecker):
    '''check kvm vm suspended status. If it is suspended, return self.judge(True). 
        If it is not suspended, return self.judge(False)'''
    def check(self):
        super(zstack_kvm_vm_suspended_checker, self).check()

        vm = self.test_obj.vm
        host = test_lib.lib_get_vm_host(vm)
        test_lib.lib_install_testagent_to_host(host)
        test_lib.lib_set_vm_host_l2_ip(vm)
        cmd = vm_plugin.VmStatusCmd()
        cmd.vm_uuids = [vm.uuid]
        test_util.test_logger('Check [vm:] %s suspended status on host [name:] %s [uuid:] %s.' % (vm.uuid, host.name, host.uuid))
        rspstr = http.json_dump_post(testagent.build_http_path(host.managementIp, vm_plugin.VM_STATUS), cmd)
        rsp = jsonobject.loads(rspstr)
        check_result = rsp.vm_status[vm.uuid].strip()
        if check_result == vm_plugin.VmAgent.VM_STATUS_PAUSED:
            test_util.test_logger('Check result: [vm:] %s is PAUSED on [host:] %s .' % (vm.uuid, host.name))
            return self.judge(True)
        else:
            test_util.test_logger('Check result: [vm:] %s is NOT PAUSED on [host:] %s . ; Expected status: %s ; Actual status: %s' % (vm.uuid, host.name, vm_plugin.VmAgent.VM_STATUS_PAUSED, check_result))
            return self.judge(False)


class zstack_kvm_vm_set_host_vlan_ip(checker_header.TestChecker):
    '''
        This is not a real checker. Its function is to assign an IP address for host vlan device.
    '''
    def check(self):
        super(zstack_kvm_vm_set_host_vlan_ip, self).check()
        vm = self.test_obj.vm
        test_lib.lib_set_vm_host_l2_ip(vm)
        return self.judge(self.exp_result)


class zstack_kvm_vm_network_checker(checker_header.TestChecker):
    '''check kvm vm network connection status. If VM's network is reachable, 
        return self.judge(True). If not, return self.judge(False)
    
        Only check the IP address behind of Virtual Router with DHCP service, 
        as the other NIC's IP address might be not correctly set.  
    '''
    def check(self):
        super(zstack_kvm_vm_network_checker, self).check()
        vm = self.test_obj.vm
        host = test_lib.lib_get_vm_host(vm)
        test_lib.lib_install_testagent_to_host(host)
        test_lib.lib_set_vm_host_l2_ip(vm)
        vr_vms = test_lib.lib_find_vr_by_vm(vm)
        if not vr_vms:
            test_util.test_warn('No Virtual Router was found for VM: %s. Skip testing.' % vm.uuid)
            return self.judge(self.exp_result)

        for vr_vm in vr_vms:
            nic = test_lib.lib_get_vm_nic_by_vr(vm, vr_vm)
            if not 'DHCP' in test_lib.lib_get_l3_service_type(nic.l3NetworkUuid):
                test_util.test_logger("Skip [VR:] %s, since it doesn't provide DHCP service" % vr_vm.uuid)
                continue
            else:
                break
        else:
            test_util.test_logger("Checker result FAILED: no DHCP in l3s")
            return self.judge(False)

        for vr_vm in vr_vms:
            nic = test_lib.lib_get_vm_nic_by_vr(vm, vr_vm)

            guest_ip = nic.ip
            command = 'ping -c 5 -W 5 %s >/tmp/ping_result 2>&1; ret=$?; cat /tmp/ping_result; exit $ret' % guest_ip
            if not test_lib.lib_execute_sh_cmd_by_agent_with_retry(host.managementIp, command, self.exp_result):
                test_util.test_logger('Checker result: FAIL to ping [target:] %s [ip:] %s from [host:] %s' % (vm.uuid, guest_ip, host.uuid))

                if self.exp_result == True:
                    test_util.test_logger("network connection result is not expected pass, will print VR's network configuration:")
                    test_lib.lib_print_vr_network_conf(vr_vm)
                return self.judge(False)
            else:
                test_util.test_logger('Checker result: SUCCESSFULLY ping [target:] %s [ip:] %s from [host:] %s' % (vm.uuid, guest_ip, host.uuid))

        test_util.test_logger("Checker result: ping target [vm:] %s from [host:] %s SUCCESS" % (vm.uuid, host.uuid))

        return self.judge(True)

class zstack_kvm_vm_default_l3_checker(checker_header.TestChecker):
    '''check kvm vm default l3 setting, when vm has multi l3. 
        if vm router is set correct default l3, 
        return self.judge(True). If not, return self.judge(False)'''
    def check(self):
        super(zstack_kvm_vm_default_l3_checker, self).check()
        vm = self.test_obj.vm
        default_l3_uuid \
                = self.test_obj.get_creation_option().get_default_l3_uuid()

        if vm.defaultL3NetworkUuid != default_l3_uuid:
            test_util.test_logger('Checker Fail: VM: %s setting default l3 uuid: %s is different with the one in database: %s' % (vm.uuid, default_l3_uuid, vm.defaultL3NetworkUuid))
            return self.judge(False)

        for vm_nic in vm.vmNics:
            if vm_nic.l3NetworkUuid == default_l3_uuid:
                gateway = vm_nic.gateway
                break
        else:
            test_util.test_logger('Checker Fail: Did not find default l3: %s is belonged to any VM: %s vmNics: %s' % (default_l3_uuid, vm.uuid, vm.vmNics))
            return self.judge(False)

        test_lib.lib_install_testagent_to_vr(vm)
        host = test_lib.lib_get_vm_host(vm)
        test_lib.lib_install_testagent_to_host(host)
        test_lib.lib_set_vm_host_l2_ip(vm)
        nic = test_lib.lib_get_vm_nic_by_l3(vm, default_l3_uuid)

        command = 'route -n |grep ^0.0.0.0'
        cmd_result = test_lib.lib_ssh_vm_cmd_by_agent_with_retry(host.managementIp, nic.ip, test_lib.lib_get_vm_username(vm), test_lib.lib_get_vm_password(vm), command, self.exp_result)
        if not cmd_result:
            test_util.test_logger('Checker result: FAIL to execute test ssh command in test [vm:] %s throught [host:] %s.' % (vm.uuid, host.name))
            return self.judge(False)

        if isinstance(cmd_result, str) and gateway in cmd_result:
            test_util.test_logger('Checker result: gateway %s is SUCCESSFULLY set in guest [vm:] %s default router. ' % (gateway, vm.uuid))
            return self.judge(True)
        else:
            test_util.test_logger('Checker result: gateway: %s is NOT set in guest [vm:] %s default router. The default route is : %s' % (gateway, vm.uuid, cmd_result))
            return self.judge(False)

class zstack_kvm_vm_dns_checker(checker_header.TestChecker):
    '''check kvm vm dns status. If VM's dns is set correctly, 
        return self.judge(True). If not, return self.judge(False)'''
    def check(self):
        super(zstack_kvm_vm_dns_checker, self).check()
        vm = self.test_obj.vm
        test_lib.lib_install_testagent_to_vr(vm)
        host = test_lib.lib_get_vm_host(vm)
        test_lib.lib_install_testagent_to_host(host)
        test_lib.lib_set_vm_host_l2_ip(vm)
        default_l3_uuid = vm.defaultL3NetworkUuid
        vr = test_lib.lib_find_vr_by_pri_l3(default_l3_uuid)
        nic = test_lib.lib_get_vm_nic_by_vr(vm, vr)

        test_util.test_logger("Begin to check [vm:] %s DNS setting" % vm.uuid)
        if not 'DNS' in test_lib.lib_get_l3_service_type(nic.l3NetworkUuid):
            test_util.test_logger('Checker result: SKIP DNS checker, since VM [VR:] %s does not provide DNS service. ' % vr.uuid)
            return self.judge(self.exp_result)

        command = 'cat /etc/resolv.conf'
        cmd_result = test_lib.lib_ssh_vm_cmd_by_agent_with_retry(host.managementIp, nic.ip, test_lib.lib_get_vm_username(vm), test_lib.lib_get_vm_password(vm), command, self.exp_result)
        if not cmd_result:
            test_util.test_logger('Checker result: FAIL to execute test ssh command in test [vm:] %s throught [host:] %s.' % (vm.uuid, host.name))
            return self.judge(False)

        vr_guest_ip = test_lib.lib_find_vr_private_ip(vr)
        if isinstance(cmd_result, str) and vr_guest_ip in cmd_result:
            test_util.test_logger('Checker result: VR [IP:] %s is SUCCESSFULLY set in guest [vm:] %s /etc/resolv.conf. ' % (vr_guest_ip, vm.uuid))
        else:
            test_util.test_logger('Checker result: VR [IP:] %s is NOT set in guest [vm:] %s /etc/resolv.conf' % (vr_guest_ip, vm.uuid))
            return self.judge(False)

        l3_inv = test_lib.lib_get_l3_by_uuid(default_l3_uuid)
        if l3_inv.domainName:
            if not l3_inv.domainName in cmd_result:
                test_util.test_logger('Checker result: L3: %s, Domain Name: %s is NOT set in guest [vm:] %s /etc/resolv.conf' % (l3_inv.uuid, l3_inv.domainName, vm.uuid))
                return self.judge(False)
            else:
                test_util.test_logger('Checker result: L3: %s, Domain Name: %s is set in guest [vm:] %s /etc/resolv.conf' % (l3_inv.uuid, l3_inv.domainName, vm.uuid))

        return self.judge(True)

class zstack_kvm_vm_ssh_no_vr_checker(checker_header.TestChecker):
    '''
    Check special flat network service provider, which doesn't use VR VM.
    '''
    def check(self):
        super(zstack_kvm_vm_ssh_no_vr_checker, self).check()
        vm = self.test_obj.vm
        host = test_lib.lib_get_vm_host(vm)
        test_lib.lib_install_testagent_to_host(host)
        test_lib.lib_set_vm_host_l2_ip(vm)
#        nic = vm.vmNics[0]
        l3_uuid = vm.defaultL3NetworkUuid
        nic = test_lib.lib_get_vm_nic_by_l3(vm, l3_uuid)
        ip = nic.ip
        

        shell_command = 'exit 0'
        vm_cmd_result = test_lib.lib_ssh_vm_cmd_by_agent_with_retry(host.managementIp, ip, test_lib.lib_get_vm_username(vm), test_lib.lib_get_vm_password(vm), shell_command, self.exp_result)
        if not vm_cmd_result:
            test_util.test_logger('Checker result: FAIL to execute test ssh command in test [vm:] %s throught [host:] %s.' % (vm.uuid, host.name))
            return self.judge(False)
        test_util.test_logger('Checker result: Success to execute test ssh command in test [vm:] %s throught [host:] %s.' % (vm.uuid, host.name))
        return self.judge(True)

class zstack_kvm_vm_dhcp_checker(checker_header.TestChecker):
    '''check kvm vm dhcp status. If VM's dhcp is set correctly, 
        return self.judge(True). If not, return self.judge(False)'''
    def check(self):
        super(zstack_kvm_vm_dhcp_checker, self).check()
        vm = self.test_obj.vm
        test_lib.lib_install_testagent_to_vr(vm)
        host = test_lib.lib_get_vm_host(vm)
        test_lib.lib_install_testagent_to_host(host)
        test_lib.lib_set_vm_host_l2_ip(vm)

        vm_cmd_result = None
        vr_vms = test_lib.lib_find_vr_by_vm(vm)
        print('find %d vr vms.' % len(vr_vms))
        for vr_vm in vr_vms:
            test_util.test_logger("Begin to check [vm:] %s DHCP binding setting in [VR:] %s" % (vm.uuid, vr_vm.uuid))
            nic = test_lib.lib_get_vm_nic_by_vr(vm, vr_vm)
            if not 'DHCP' in \
                    test_lib.lib_get_l3_service_type(nic.l3NetworkUuid):
                test_util.test_logger("Skip [VR:] %s, since it doesn't provide DHCP service" % vr_vm.uuid)
                continue

            for i in range(300):
                cond = res_ops.gen_query_conditions('uuid', '=', vr_vm.uuid)
                vr = res_ops.query_resource_fields(res_ops.VM_INSTANCE, cond, None)[0]
                if "connected" in vr.status.lower():
                    test_util.test_logger("vr.uuid=%s vr.status=%s" %(vr_vm.uuid, vr.status.lower()))
                    break
                time.sleep(1)
            else:
                test_util.test_fail("vr.uuid=%s is not changed to changed within max waiting time." %(vr_vm.uuid))
          
            guest_ip = nic.ip
            guest_mac = nic.mac
            vr_ip = test_lib.lib_find_vr_mgmt_ip(vr_vm)
            if vr_vm.hasattr('applianceVmType') and vr_vm.applianceVmType == 'vrouter':
                command = '/bin/cli-shell-api showCfg'
            else:
                command = 'cat /etc/hosts.dhcp'
            vr_cmd_result = test_lib.lib_execute_sh_cmd_by_agent_with_retry(vr_ip, command, self.exp_result)
            if not vr_cmd_result:
                test_util.test_logger('Checker result: FAIL to execute shell commaond in [vm:] %s' % vr_vm.uuid)
                return self.judge(False)
            
            if vr_cmd_result == True:
                test_util.test_logger('Checker result: FAIL to get ssh result in [vm:] %s' % vr_vm.uuid)
                return self.judge(False)

            if not guest_mac in vr_cmd_result or not guest_ip in vr_cmd_result:
                test_util.test_logger('Checker result: [vm:] %s [mac:] %s is not found in [vr:] %s. VR ip/mac result is %s.' % (vm.uuid, guest_mac, vr_vm.uuid, vr_cmd_result))
                return self.judge(False)
            else:
                test_util.test_logger('Checker result: [vm:] %s [mac:] %s is found in VR %s .' % (vm.uuid, guest_mac, vr_vm.uuid))

            test_util.test_logger("Begin to check VM DHCP in VM: %s" % vm.uuid)
            if not vm_cmd_result:
                vm_command = '/sbin/ip a'
                vm_cmd_result = test_lib.lib_ssh_vm_cmd_by_agent_with_retry(host.managementIp, nic.ip, test_lib.lib_get_vm_username(vm), test_lib.lib_get_vm_password(vm), vm_command, self.exp_result)
                if not vm_cmd_result:
                    test_util.test_logger('Checker result: FAIL to execute test ssh command in test [vm:] %s throught [host:] %s.' % (vm.uuid, host.name))
                    return self.judge(False)

            if isinstance(vm_cmd_result, str) and guest_ip in vm_cmd_result:
                test_util.test_logger('Checker result: guest [ip:] %s is SET in guest [vm:] %s.' % (guest_ip, vm.uuid))
            else:
                test_util.test_logger('Checker result: guest [ip:] %s is NOT found in guest [vm:] %s. \n Will Try again. It might be because the ifconfig is not reflect the ip address yet. \n The current ifconfig result is: %s' % (guest_ip, vm.uuid, vm_cmd_result))
                vm_cmd_result = test_lib.lib_ssh_vm_cmd_by_agent_with_retry(host.managementIp, nic.ip, test_lib.lib_get_vm_username(vm), test_lib.lib_get_vm_password(vm), vm_command, self.exp_result)
                if not vm_cmd_result:
                    test_util.test_logger('Checker result: FAIL to execute test ssh command in test [vm:] %s throught [host:] %s.' % (vm.uuid, host.name))
                    return self.judge(False)
                if isinstance(vm_cmd_result, str) and guest_ip in vm_cmd_result:
                    test_util.test_logger('Checker result: guest [ip:] %s is SET in guest [vm:] %s.' % (guest_ip, vm.uuid))
                else:
                    if not guest_ip in vm_cmd_result:
                        test_util.test_logger('Checker result: guest [ip:] %s is NOT found in guest [vm:] %s. The current ifconfig result is: %s' % (guest_ip, vm.uuid, vm_cmd_result))
                    else:
                        test_util.test_logger('vm_cmd_result: %s is not string type. It is: %s .' % (vm_cmd_result, type(vm_cmd_result)))
                    return self.judge(False)

        return self.judge(True)

class zstack_kvm_vm_snat_checker(checker_header.TestChecker):
    '''check kvm vm snat status. If VM could ping external target,
        return self.judge(True). If not, return self.judge(False)'''
    def check(self):
        super(zstack_kvm_vm_snat_checker, self).check()
        vm = self.test_obj.vm
        test_lib.lib_install_testagent_to_vr(vm)
        host = test_lib.lib_get_vm_host(vm)

        vm_cmd_result = None
        vr_vms = test_lib.lib_find_vr_by_vm(vm)
        test_lib.lib_set_vm_host_l2_ip(vm)
        for vr_vm in vr_vms:
            test_util.test_logger("Begin to check [vm:] %s SNAT" % vm.uuid)
            nic = test_lib.lib_get_vm_nic_by_vr(vm, vr_vm)
            if not 'SNAT' in test_lib.lib_get_l3_service_type(nic.l3NetworkUuid):
                test_util.test_logger("Skip [VR:] %s, since it doesn't provide SNAT service" % vr_vm.uuid)
                continue

            ping_target = test_lib.test_config.pingTestTarget.text_
            #Check if there is a SG rule to block ICMP checking
            if test_lib.lib_is_sg_rule_exist(nic.uuid, None, None, inventory.EGRESS):
                if not test_lib.lib_is_sg_rule_exist(nic.uuid, inventory.ICMP, ping_target, inventory.EGRESS):
                    test_util.test_warn('Skip SNAT checker: because there is ICMP Egress Rule was assigned to [nic:] %s and the allowed target ip is not %s' % (nic.uuid, ping_target))
                    return self.judge(self.exp_result)

            guest_ip = nic.ip
            vm_command = 'ping -c 5 -W 5 %s >/tmp/ping_result 2>&1; ret=$?; cat /tmp/ping_result; exit $ret' % ping_target
            vm_cmd_result = test_lib.lib_ssh_vm_cmd_by_agent_with_retry(host.managementIp, nic.ip, test_lib.lib_get_vm_username(vm), test_lib.lib_get_vm_password(vm), vm_command, self.exp_result)
            if not vm_cmd_result:
                test_util.test_logger('Checker result: FAIL to ping [target:] %s from [vm:] %s .' % (ping_target, vm.uuid))
                if self.exp_result == True:
                    test_util.test_logger("network connection result is not expected pass, will print VR's network configuration:")
                    test_lib.lib_print_vr_network_conf(vr_vm)
                return self.judge(False)
            else:
                test_util.test_logger('Checker result: SUCCEED to ping [target:] %s from [vm:] %s .' % (ping_target, vm.uuid))
                return self.judge(True)


class zstack_kvm_vm_offering_checker(checker_header.TestChecker):
    '''check kvm vm instance offering config''' 
    def check(self):
        def _do_check(value1, value2, key):
            if value1 != value2:
                test_util.test_logger(\
                    '%s comparison failed, vm value: %s; offering value: %s' \
                    % (key, value1, value2))
                return False
            test_util.test_logger('%s comparison pass' % key)
            return True

        super(zstack_kvm_vm_running_checker, self).check()
        vm = self.test_obj.vm
        instance_offering_uuid = self.test_obj.get_instance_offering_uuid() 
        instance_offering = test_lib.lib_get_instance_offering_by_uuid(instance_offering_uuid)
        if not instance_offering:
            test_util.test_logger('Skip Test: not find vm instance offering by uuid: %s. It might because the instance offering is deleted. Skip test.' % vm.uuid)
            return self.judge(self.exp_result)

        if not _do_check(vm.cpuNum, instance_offering.cpuNum, 'CPU number'):
            test_util.test_logger('Check result: vm resource is not synced with instance offering .' % vm.uuid)
            return self.judge(False)

        #if not _do_check(vm.cpuSpeed, instance_offering.cpuSpeed, 'CPU speed'):
        #    test_util.test_logger('Check result: vm resource is not synced with instance offering .' % vm.uuid)
        #    return self.judge(False)

        if not _do_check(vm.memorySize, instance_offering.memorySize, 'memory'):
            test_util.test_logger('Check result: vm resource is not synced with instance offering .' % vm.uuid)
            return self.judge(False)

        test_util.test_logger('Check result: Pass. vm resource is synced with instance offering .' % vm.uuid)
        return self.judge(True)
