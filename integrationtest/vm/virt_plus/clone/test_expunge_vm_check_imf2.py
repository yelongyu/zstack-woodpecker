'''
New Integration Test for cloning KVM VM.
Behavior check: cloned vm should not have data volume.

@author: SyZhao
'''

import apibinding.inventory as inventory
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import zstacklib.utils.ssh as ssh
import time
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
vn_prefix = 'vm-clone-%s' % time.time()
vm_names = ['%s-vm1' % vn_prefix]



def test():
    vm = test_stub.create_vlan_vm()
    #test_obj_dict.add_vm(vm)

    backup_storage_list = test_lib.lib_get_backup_storage_list_by_vm(vm.vm)
    for bs in backup_storage_list:
        if bs.type == inventory.IMAGE_STORE_BACKUP_STORAGE_TYPE:
            break
        #if bs.type == inventory.SFTP_BACKUP_STORAGE_TYPE:
        #    break
        #if bs.type == inventory.CEPH_BACKUP_STORAGE_TYPE:
        #    break
    else:
        vm.destroy()
        vm.expunge()
        test_util.test_skip('Not find image store type backup storage.')
    primary_storage_list = res_ops.query_resource(res_ops.PRIMARY_STORAGE)
    for ps in primary_storage_list:
        if ps.type == "SharedBlock":
            vm.destroy()
            vm.expunge()
            test_util.test_skip('The test is not support sharedblock storage.')

    new_vms = vm.clone(vm_names)
    for new_vm in new_vms:
        test_obj_dict.add_vm(new_vm)

    if len(new_vms) != len(vm_names):
        test_util.test_fail('only %s VMs have been cloned, which is less than required: %s' % (len(new_vms), vm_names))

    for new_vm in new_vms:
        new_vm = new_vm.get_vm()
        try:
            vm_names.remove(new_vm.name)
            test_util.test_logger('VM:%s name: %s is found' % (new_vm.uuid, new_vm.name))
        except:
            test_util.test_fail('%s vm name: %s is not in list: %s' % (new_vm.uuid, new_vm.name, vm_names))
    
    vm.destroy()
    check_imf2_cmd = "find /|grep imf|grep %s" % (test_lib.lib_get_root_volume_uuid(vm.get_vm()))
    host = test_lib.lib_find_host_by_vm(vm.get_vm()) 
    ret, output, stderr = ssh.execute(check_imf2_cmd, host.managementIp, "root", "password", False, 22)
    test_util.test_logger('expect imf2 exist: %s,%s' % (output, ret))
    if ret != 0:
        test_util.test_fail('imf2 is expected to exist')

    vm.expunge()
    ret, output, stderr = ssh.execute(check_imf2_cmd, host.managementIp, "root", "password", False, 22)
    test_util.test_logger('expect imf2 not exist: %s,%s' % (output, ret))
    if ret == 0:
        test_util.test_fail('imf2 is expected to be deleted')

    test_lib.lib_robot_cleanup(test_obj_dict)
    test_util.test_pass('Clone VM Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
