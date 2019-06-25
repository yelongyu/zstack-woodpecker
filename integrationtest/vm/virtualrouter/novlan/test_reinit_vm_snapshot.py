'''

New Integration Test for reinit VM with snapshot.

@author: MengLai
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

    test_util.test_dsc('create test-file-1, test-file-2, test-file-3 and create snapshot1')
    num = 1
    while num <= 3:
        cmd = 'touch /root/test-file-%s' % num
        rsp = test_lib.lib_ssh_vm_cmd_by_agent_with_retry(host_ip, vm_ip, 'root', 'password', cmd)
        if rsp == False:
            test_util.test_fail('Fail to create test-file-%s in VM' % num)
        num = num + 1

    root_volume_uuid = test_lib.lib_get_root_volume_uuid(vm.get_vm())
    snapshots = test_obj_dict.get_volume_snapshot(root_volume_uuid)    
    snapshots.set_utility_vm(vm)
    vm.check() 
    snapshots.create_snapshot('create_root_snapshot1')

    test_util.test_dsc('delete test-file-1, create test-file-4, test-file-5 and create snapshot2')
    cmd = 'rm /root/test-file-1 || echo y'
    rsp = test_lib.lib_ssh_vm_cmd_by_agent_with_retry(host_ip, vm_ip, 'root', 'password', cmd)
    if rsp == False:
        test_util.test_fail('Fail to delete test-file-1 in VM')

    num = 4
    while num <= 5:
        cmd = 'touch /root/test-file-%s' % num
        rsp = test_lib.lib_ssh_vm_cmd_by_agent_with_retry(host_ip, vm_ip, 'root', 'password', cmd)
        if rsp == False:
            test_util.test_fail('Fail to create test-file-%s in VM' % num)
        num = num + 1

    root_volume_uuid = test_lib.lib_get_root_volume_uuid(vm.get_vm())
    snapshots2 = test_obj_dict.get_volume_snapshot(root_volume_uuid)    
    snapshots2.set_utility_vm(vm)
    vm.check() 
    snapshots2.create_snapshot('create_root_snapshot2')

    test_util.test_dsc('delete test-file-2, test-file-4,  create test-file-6 and create snapshot3')
    num_arr = [2, 4]
    for i in num_arr:
        cmd = 'rm /root/test-file-%s || echo y' % i
        rsp = test_lib.lib_ssh_vm_cmd_by_agent_with_retry(host_ip, vm_ip, 'root', 'password', cmd)
        if rsp == False:
            test_util.test_fail('Fail to delete test-file-%s in VM' % i)

    cmd = 'touch /root/test-file-6'
    rsp = test_lib.lib_ssh_vm_cmd_by_agent_with_retry(host_ip, vm_ip, 'root', 'password', cmd)
    if rsp == False:
        test_util.test_fail('Fail to create test-file-6 in VM')   

    root_volume_uuid = test_lib.lib_get_root_volume_uuid(vm.get_vm())
    snapshots3 = test_obj_dict.get_volume_snapshot(root_volume_uuid)    
    snapshots3.set_utility_vm(vm)
    vm.check() 
    snapshots3.create_snapshot('create_root_snapshot3')

    test_util.test_dsc('VM reinit')
    vm.stop()
    vm.reinit()
    vm.update()
    vm.check()
    vm.start()
    vm.check()

    num = 1
    while num <= 6:
        cmd = '[ -e /root/test-file-%s ] && echo yes || echo no' % num
        rsp = test_lib.lib_ssh_vm_cmd_by_agent_with_retry(host_ip, vm_ip, 'root', 'password', cmd)
        if rsp == False:
            test_util.test_fail('test-file-%s should not exist' % num)
        num = num + 1

    test_util.test_dsc('VM return to snapshot3')
    vm.stop()
    snapshots3.use_snapshot(snapshots.get_current_snapshot())
    vm.start()
    vm.check()

    num_arr = [1, 2, 4]
    for i in num_arr:
        cmd = '[ -e /root/test-file-%s ] && echo yes || echo no' % i
        rsp = test_lib.lib_ssh_vm_cmd_by_agent_with_retry(host_ip, vm_ip, 'root', 'password', cmd)
        if rsp == False:
            test_util.test_fail('test-file-%s should not exist' % i)

    num_arr = [3, 5, 6]
    for i in num_arr:
        cmd = '[ -e /root/test-file-%s ] && echo yes || echo no' % i
        rsp = test_lib.lib_ssh_vm_cmd_by_agent_with_retry(host_ip, vm_ip, 'root', 'password', cmd)
        if rsp == False:
            test_util.test_fail('test-file-%s should exist' % i)

    vm.destroy()
    test_util.test_pass('Re-init VM Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
