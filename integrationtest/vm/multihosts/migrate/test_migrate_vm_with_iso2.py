'''

New Integration test for testing running vm migration between hosts when attach ISO.

@author: Chenyuan.xu
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.zstack_test.zstack_test_image as test_image
import zstackwoodpecker.test_state as test_state
import apibinding.inventory as inventory
import zstacklib.utils.ssh as ssh
import time
import os

vm = None
test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    #skip ceph in c74
    cmd = "cat /etc/redhat-release | grep '7.4'"
    mn_ip = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].hostName
    rsp = test_lib.lib_execute_ssh_cmd(mn_ip, 'root', 'password', cmd, 180)
    if rsp != False:
        ps = res_ops.query_resource(res_ops.PRIMARY_STORAGE)
        for i in ps:
            if i.type == 'Ceph':
                test_util.test_skip('cannot hotplug iso to the vm in ceph,it is a libvirt bug:https://bugzilla.redhat.com/show_bug.cgi?id=1541702.')

    global vm
    vm = test_stub.create_vr_vm('migrate_vm', 'imageName_net', 'l3VlanNetwork2')
    vm.check()
    ps = test_lib.lib_get_primary_storage_by_uuid(vm.get_vm().allVolumes[0].primaryStorageUuid)
    if ps.type == inventory.LOCAL_STORAGE_TYPE:
        test_util.test_skip('Skip test on localstorage PS')

    vm_inv = vm.get_vm()
    vm_uuid = vm_inv.uuid
    vm_ip = vm_inv.vmNics[0].ip
    host_ip = test_lib.lib_find_host_by_vm(vm.get_vm()).managementIp


    test_util.test_dsc('Add ISO Image')
    #cond = res_ops.gen_query_conditions('name', '=', 'sftp')
    bs_uuid = res_ops.query_resource(res_ops.BACKUP_STORAGE)[0].uuid


    img_option = test_util.ImageOption()
    img_option.set_name('iso')
    img_option.set_backup_storage_uuid_list([bs_uuid])
    testIsoUrl = os.environ.get('testIsoUrl')
    img_option.set_url(testIsoUrl)
    image_inv = img_ops.add_iso_template(img_option)
    image = test_image.ZstackTestImage()
    image.set_image(image_inv)
    image.set_creation_option(img_option)
   
    test_obj_dict.add_image(image)

    test_util.test_dsc('Attach ISO to VM')
    cond = res_ops.gen_query_conditions('name', '=', 'iso')
    iso_uuid = res_ops.query_resource(res_ops.IMAGE, cond)[0].uuid
    img_ops.attach_iso(iso_uuid, vm_uuid)
    
    ssh_timeout = test_lib.SSH_TIMEOUT
    test_lib.SSH_TIMEOUT = 3600
    cmd = "mount /dev/sr0 /mnt"
    if not test_lib.lib_ssh_vm_cmd_by_agent_with_retry(host_ip, vm_ip, 'root', 'password', cmd):
        test_lib.SSH_TIMEOUT = ssh_timeout
        test_util.test_fail("Failed to mount /dev/sr0 /mnt.")

    test_util.test_dsc('Migrate VM')
    test_stub.migrate_vm_to_random_host(vm)
    vm.check()

    host_ip = test_lib.lib_find_host_by_vm(vm.get_vm()).managementIp
    cmd = "umount /mnt"
    if not test_lib.lib_ssh_vm_cmd_by_agent_with_retry(host_ip, vm_ip, 'root', 'password', cmd):
        test_lib.SSH_TIMEOUT = ssh_timeout
        test_util.test_fail("Failed to umount /mnt.")

    img_ops.detach_iso(vm_uuid)
    img_ops.attach_iso(iso_uuid, vm_uuid)

    cmd = "mount /dev/sr0 /mnt"
    if not test_lib.lib_ssh_vm_cmd_by_agent_with_retry(host_ip, vm_ip, 'root', 'password', cmd):
        test_lib.SSH_TIMEOUT = ssh_timeout
        test_util.test_fail("Failed to mount /dev/sr0 /mnt.")

    cmd = "cat /mnt/Licenses.txt"
    if not test_lib.lib_ssh_vm_cmd_by_agent_with_retry(host_ip, vm_ip, 'root', 'password', cmd):
        test_lib.SSH_TIMEOUT = ssh_timeout
        test_util.test_fail("Licenses.txt doesn't exist.")

    img_ops.detach_iso(vm_uuid)
    image.delete()
    image.expunge()
    test_obj_dict.rm_image(image)
    vm.destroy()
    test_util.test_pass('Migrate VM Test Success When Attach ISO')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
