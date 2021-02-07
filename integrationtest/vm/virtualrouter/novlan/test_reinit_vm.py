'''

New Integration Test for reinit VM.

@author: quarkonics
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    ps = res_ops.query_resource(res_ops.PRIMARY_STORAGE)
    for i in ps:
        if i.type == 'AliyunEBS':
            test_util.test_skip('Skip vm reinit test on AliyunEBS')

    vm = test_stub.create_user_vlan_vm()
    test_obj_dict.add_vm(vm)
    vm.check()
    vm_inv = vm.get_vm()
    vm_ip = vm_inv.vmNics[0].ip 

    host_ip = test_lib.lib_find_host_by_vm(vm_inv).managementIp
    cmd = 'touch /root/test-file-for-reinit'
    rsp = test_lib.lib_ssh_vm_cmd_by_agent_with_retry(host_ip, vm_ip, 'root', 'password', cmd)
    if rsp == False:
	test_util.test_fail('Fail to create file in VM')

    vm.stop()
    vm.reinit()
    vm.update()
    vm.check()
    vm.start()

    cmd = '[ -e /root/test-file-for-reinit ] && echo yes || echo no'
    rsp = test_lib.lib_ssh_vm_cmd_by_agent_with_retry(host_ip, vm_ip, 'root', 'password', cmd)
    if rsp == 'yes':
	test_util.test_fail('VM does not be reverted to image used for creating the VM, the later file still exists')

    vm.destroy()
    test_util.test_pass('Re-init VM Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
