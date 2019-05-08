'''
Test for migrate vm which installed by iso

@author: chenyuan.xu
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.zstack_test.zstack_test_image as test_image
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_lib as test_lib

vm = None
test_obj_dict = test_state.TestStateDict()
test_stub = test_lib.lib_get_test_stub()

def test():
    global vm
    global test_obj_dict
    test_util.test_dsc('Add iso which reboot --eject.')
    conditions = res_ops.gen_query_conditions('type', '=', 'Ceph')
    pss = res_ops.query_resource(res_ops.PRIMARY_STORAGE, conditions)
    if len(pss) == 0:
        test_util.test_skip('Skip due to no ceph storage available')

    img_option = test_util.ImageOption()
    image_name = 'centos-7-auto-eject'
    img_option.set_name(image_name)
    bs_uuid = res_ops.query_resource_fields(res_ops.BACKUP_STORAGE, [], None)[0].uuid
    img_option.set_backup_storage_uuid_list([bs_uuid])
    img_option.set_format('iso')
    img_option.set_url(os.environ.get('imageServer')+'iso/CentOS-7-auto-eject-xcy.iso')
    image_inv = img_ops.add_root_volume_template(img_option)
    image = test_image.ZstackTestImage()
    image.set_image(image_inv)
    image.set_creation_option(img_option)
    test_obj_dict.add_image(image)

    #create disk offering
    data_volume_size = 10737418240
    disk_offering_option = test_util.DiskOfferingOption()
    disk_offering_option.set_name('root-disk-iso')
    disk_offering_option.set_diskSize(data_volume_size)
    data_volume_offering = vol_ops.create_volume_offering(disk_offering_option)
    test_obj_dict.add_disk_offering(data_volume_offering)

    vm_offering = test_stub.add_test_vm_offering(1, 1024*1024*1024, 'iso-vm-offering')
    vm = test_stub.create_vm_with_iso_for_test(vm_offering.uuid, image_inv.uuid, data_volume_offering.uuid, 'migrate_vm')
    vm.check()

    host = test_lib.lib_find_host_by_vm(vm.get_vm())
    cmd = 'virsh dumpxml %s > vm.xml;cat vm.xml |grep "target dev"' % vm.get_vm().uuid
    output = test_lib.lib_execute_ssh_cmd(host.managementIp, host.username, host.password, cmd, 180)
    if "tray='open'" in output:
        test_util.test_fail("There still has tray=open in vm xml.")
    cmd = 'cat vm.xml |grep "source protocol"'
    output = test_lib.lib_execute_ssh_cmd(host.managementIp, host.username, host.password, cmd, 180)
    if 'name' not in output:
        test_util.test_fail("Source name is missing in vm xml.")

    test_stub.migrate_vm_to_random_host(vm)

    vm.check()

    vm.destroy()
    test_util.test_pass('Migrate VM Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    if vm:
        try:
            vm.destroy()
        except:
            pass

