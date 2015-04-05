'''
EIP checker.

Author: YYK 
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.header.checker as checker_header

class eip_checker(checker_header.TestChecker):
    def __init__(self):
        super(eip_checker, self).__init__()

    def check(self):
        super(eip_checker, self).check()
        test_result = True
        if self.test_obj.vm:
            self.vm_check(test_result)
        test_util.test_logger('Check result:' )
        return self.judge(test_result)

    def vm_check(self, test_result):
        vm = self.test_obj.vm
        test_util.test_logger("Begin to check VM DHCP in VM: %s" % vm.uuid)
        nic = test_lib.lib_get_nic_by_uuid(self.test_obj.get_creation_option().get_vm_nic_uuid())
        test_lib.lib_find_vr_by_vm(vm)
        guest_ip = nic.ip
        host = test_lib.lib_get_vm_host(vm)
        vm_command = '/sbin/ifconfig'
        vm_cmd_result = test_lib.lib_ssh_vm_cmd_by_agent_with_retry(host.managementIp, self.test_obj.vip.ip, test_lib.lib_get_vm_username(vm), test_lib.lib_get_vm_password(vm), vm_command)
        if not vm_cmd_result:
            test_util.test_logger('Checker result: FAIL to execute test ssh command in test [vm:] %s throught [host:] %s.' % (vm.uuid, host.name))
            return self.judge(False)

        if guest_ip in vm_cmd_result:
            test_util.test_logger('Checker result: guest [ip:] %s is SET in guest [vm:] %s.' % (guest_ip, vm.uuid))
        else:
            test_util.test_logger('Checker result: guest [ip:] %s is NOT found in guest [vm:] %s. \n It might be because the ifconfig is not reflect the ip address yet. \n The current ifconfig result is: %s' % (guest_ip, vm.uuid, vm_cmd_result))
            return self.judge(False)
        return self.judge(True)

