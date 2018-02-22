import os
import sys
import traceback
try:
    from pysphere import VIServer
except:
    print 'pysphere not installed'

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
import commands

def get_obj(content, vimtype, name=None):
    obj = None
    container = content.viewManager.CreateContainerView(
        content.rootFolder, vimtype, True)
    if name:
        for c in container.view:
            if c.name == name:
                obj = c
                return obj
    return container.view

def get_vcenter_vm_status_by_vm_name(vm_name):
    """
    This function is used for return vm status by vmware sdk
    """
    import ssl
    from pyVmomi import vim
    import atexit
    from pyVim import connect

    vcenter_password = os.environ['vcenterpwd']
    vcenter_server = os.environ['vcenter']
    vcenter_username = os.environ['vcenteruser']

    sslContext = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    sslContext.verify_mode = ssl.CERT_NONE
    SI = connect.SmartConnect(host=vcenter_server, user=vcenter_username, pwd=vcenter_password, port=443, sslContext=sslContext)
    if not SI:
        test_util.test_fail("Unable to connect to the vCenter")
    content = SI.RetrieveContent()

    vm = get_obj(content, [vim.VirtualMachine], name=vm_name)
    if not isinstance(vm, vim.VirtualMachine):
        test_util.test_fail("%s is not found in vcenter %s" %(vm_name, vcenter_server))

    pysf_vm_real_status = vm.summary.runtime.powerState

    atexit.register(connect.Disconnect, SI)
    return pysf_vm_real_status


class zstack_vcenter_vm_running_checker(checker_header.TestChecker):
    '''check vcenter vm running status. If it is running, return self.judge(True).
        If it is stopped, return self.judge(False)'''
    def check(self):
        super(zstack_vcenter_vm_running_checker, self).check()
        vm = self.test_obj.vm
        #host_cond = res_ops.gen_query_conditions("hypervisorType", '=', "ESX")
        #hosts = res_ops.query_resource_fields(res_ops.HOST, host_cond, None)
        #host_ip = hosts[0].managementIp
        #test_util.test_logger('Check [vm:] %s running status on host [name:] %s [uuid:] %s.' % (vm.uuid, hosts[0].name, hosts[0].uuid))

        #server = VIServer()
        #server.connect(host_ip, "root", "password")
        #if os.environ['DATASTORE_HEAD_FOR_CHECKER']:
        #    vm_path  = os.environ['DATASTORE_HEAD_FOR_CHECKER'] + " " + vm.name + "/" + vm.name + ".vmx"
        #else:
        #    vm_path  = "[datastore1] " + vm.name + "/" + vm.name + ".vmx"
        #pysf_vm = server.get_vm_by_path(vm_path)
        #pysf_vm = server.get_vm_by_name(vm.name)
        #pysf_vm_real_status = pysf_vm.get_status()

        pysf_vm_real_status = get_vcenter_vm_status_by_vm_name(vm.name)

        if pysf_vm_real_status == "poweredOn" :
            test_util.test_logger('Check result: [vm:] %s is RUNNING.' % (vm.uuid))
            return self.judge(True)
        else:
            test_util.test_logger('Check result: [vm:] %s is NOT RUNNING. ; Expected status: %s ; Actual status: %s' % (vm.uuid, "POWERED ON", pysf_vm_real_status))
            return self.judge(False)


class zstack_vcenter_vm_destroyed_checker(checker_header.TestChecker):
    '''check vcenter vm destroyed status. If it is not running and not stopped,
        return self.judge(True). If either is true, return self.judge(False)'''
    def check(self):
        super(zstack_vcenter_vm_destroyed_checker, self).check()
        vm = self.test_obj.vm

        pysf_vm_real_status = get_vcenter_vm_status_by_vm_name(vm.name)

        if pysf_vm_real_status == "poweredOff" :
            test_util.test_logger('Check result: [vm:] %s is DESTROYED.' % (vm.uuid))
            return self.judge(True)
        else:
            test_util.test_logger('Check result: [vm:] %s is NOT DESTROYED. ; Expected status: %s ; Actual status: %s' % (vm.uuid, "POWERED OFF", pysf_vm_real_status))
            return self.judge(False)


class zstack_vcenter_vm_stopped_checker(checker_header.TestChecker):
    '''check vcenter vm stopped status. If it is stopped, return self.judge(True).
        If it is stopped, return self.judge(False)

        This checker is deprecated, since the stopped VM will also removed from
        host libvirt.
        '''
    def check(self):
        super(zstack_vcenter_vm_stopped_checker, self).check()
        vm = self.test_obj.vm

        pysf_vm_real_status = get_vcenter_vm_status_by_vm_name(vm.name)

        #if check_result == vm_plugin.VmAgent.VM_STATUS_STOPPED:
        if pysf_vm_real_status == "poweredOff" :
            test_util.test_logger('Check result: [vm:] %s is STOPPED.' % (vm.uuid))
            return self.judge(True)
        else:
            test_util.test_logger('Check result: [vm:] %s is NOT STOPPED. ; Expected status: %s ; Actual status: %s' % (vm.uuid, "POWERED OFF", pysf_vm_real_status))
            return self.judge(False)


class zstack_vcenter_vm_suspended_checker(checker_header.TestChecker):
    '''check vcenter vm suspended status. If it is suspended, return self.judge(True).
        If it is not suspended, return self.judge(False)'''
    def check(self):
        super(zstack_vcenter_vm_suspended_checker, self).check()
        vm = self.test_obj.vm

        pysf_vm_real_status = get_vcenter_vm_status_by_vm_name(vm.name)

        #if check_result == vm_plugin.VmAgent.VM_STATUS_STOPPED:
        if pysf_vm_real_status == "suspended" :
            test_util.test_logger('Check result: [vm:] %s is SUSPENDED.' % (vm.uuid))
            return self.judge(True)
        else:
            test_util.test_logger('Check result: [vm:] %s is NOT SUSPENDED. ; Expected status: %s ; Actual status: %s' % (vm.uuid, "SUSPENDED", pysf_vm_real_status))
            return self.judge(False)



class zstack_vcenter_vm_set_host_vlan_ip(checker_header.TestChecker):
    '''
        This is not a real checker. Its function is to assign an IP address for host vlan device.
    '''
    def check(self):
        vm = self.test_obj.vm
        test_lib.lib_set_vm_host_l2_ip(vm)
        return self.judge(self.exp_result)


class zstack_vcenter_vm_network_checker(checker_header.TestChecker):
    '''check vcenter vm network connection status. If VM's network is reachable,
        return self.judge(True). If not, return self.judge(False)

        Only check the IP address behind of Virtual Router with DHCP service,
        as the other NIC's IP address might be not correctly set.
    '''
    def check(self):
        super(zstack_vcenter_vm_network_checker, self).check()
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

class zstack_vcenter_vm_default_l3_checker(checker_header.TestChecker):
    '''check vcenter vm default l3 setting, when vm has multi l3.
        if vm router is set correct default l3,
        return self.judge(True). If not, return self.judge(False)'''
    def check(self):
        super(zstack_vcenter_vm_default_l3_checker, self).check()
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

        command = 'route|grep default'
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

class zstack_vcenter_vm_dns_checker(checker_header.TestChecker):
    '''check vcenter vm dns status. If VM's dns is set correctly,
        return self.judge(True). If not, return self.judge(False)'''
    def check(self):
        super(zstack_vcenter_vm_dns_checker, self).check()
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

class zstack_vcenter_vm_ssh_no_vr_checker(checker_header.TestChecker):
    '''
    Check special flat network service provider, which doesn't use VR VM.
    '''
    def check(self):
        super(zstack_vcenter_vm_ssh_no_vr_checker, self).check()
        vm = self.test_obj.vm
        host = test_lib.lib_get_vm_host(vm)
        test_lib.lib_install_testagent_to_host(host)
        test_lib.lib_set_vm_host_l2_ip(vm)
        nic = vm.vmNics[0]
        ip = nic.ip

        shell_command = 'exit 0'
        vm_cmd_result = test_lib.lib_ssh_vm_cmd_by_agent_with_retry(host.managementIp, ip, test_lib.lib_get_vm_username(vm), test_lib.lib_get_vm_password(vm), shell_command, self.exp_result)
        if not vm_cmd_result:
            test_util.test_logger('Checker result: FAIL to execute test ssh command in test [vm:] %s throught [host:] %s.' % (vm.uuid, host.name))
            return self.judge(False)
        test_util.test_logger('Checker result: Success to execute test ssh command in test [vm:] %s throught [host:] %s.' % (vm.uuid, host.name))
        return self.judge(True)

class zstack_vcenter_vm_dhcp_checker(checker_header.TestChecker):
    '''check vcenter vm dhcp status. If VM's dhcp is set correctly,
        return self.judge(True). If not, return self.judge(False)'''
    def check(self):
        super(zstack_vcenter_vm_dhcp_checker, self).check()
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

class zstack_vcenter_vm_snat_checker(checker_header.TestChecker):
    '''check vcenter vm snat status. If VM could ping external target,
        return self.judge(True). If not, return self.judge(False)'''
    def check(self):
        super(zstack_vcenter_vm_snat_checker, self).check()
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


class zstack_vcenter_vm_offering_checker(checker_header.TestChecker):
    '''check vcenter vm instance offering config'''
    def check(self):
        def _do_check(value1, value2, key):
            if value1 != value2:
                test_util.test_logger(\
                    '%s comparison failed, vm value: %s; offering value: %s' \
                    % (key, value1, value2))
                return False
            test_util.test_logger('%s comparison pass' % key)
            return True

        super(zstack_vcenter_vm_running_checker, self).check()
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
