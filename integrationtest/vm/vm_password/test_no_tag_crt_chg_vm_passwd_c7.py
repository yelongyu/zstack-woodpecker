'''
test for changing vm password when imported image has no system tag
@author: SyZhao
'''

import apibinding.inventory as inventory
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import os

test_stub = test_lib.lib_get_specific_stub()

vm = None

root_password_list = ["ab_0123"]

def test():
    global vm
    test_util.test_dsc('create VM with setting password')

    for root_password in root_password_list:
        test_util.test_dsc("root_password: \"%s\"" %(root_password))
        #vm = test_stub.create_vm(vm_name = 'c7-vm-no-sys-tag', image_name = "imageName_i_c7_no_tag", root_password=root_password)
        image_name = "imageName_i_c7_no_tag"
        ps_type = res_ops.query_resource(res_ops.PRIMARY_STORAGE)[0].type
        if ps_type == 'MiniStorage':
            image_name = os.environ.get(image_name)
        vm = test_stub.create_vm(vm_name='c7-vm-no-sys-tag', image_name=image_name)

        backup_storage_list = test_lib.lib_get_backup_storage_list_by_vm(vm.vm)
        for bs in backup_storage_list:
            if bs.type == inventory.IMAGE_STORE_BACKUP_STORAGE_TYPE:
                break
            if bs.type == inventory.SFTP_BACKUP_STORAGE_TYPE:
                break
            if bs.type == inventory.CEPH_BACKUP_STORAGE_TYPE:
                break
        else:
            vm.destroy()
            test_util.test_skip('Not find image store type backup storage.')

        #if not test_lib.lib_check_login_in_vm(vm.get_vm(), "root", root_password):
        #    test_util.test_fail("create vm with root password: %s failed", root_password)

        # stop vm && change vm password
        #vm.stop()
        vm.check()
        vm_ops.set_vm_qga_enable(vm.get_vm().uuid)
        try:
            vm_ops.change_vm_password(vm.get_vm().uuid, "root", root_password)
        except Exception, e:
            test_util.test_pass("negative test of change a no system tag image passed.")

    test_util.test_fail('negative test failed because no system tag image has been set vm password successfully, but it should be a failure.')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    pass
    if vm:
        vm.destroy()
        vm.expunge()
