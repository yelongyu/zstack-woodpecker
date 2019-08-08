'''
test iam2 login by system admin
@author: SyZhao
'''
import os
import zstackwoodpecker.test_util as test_util
import apibinding.inventory as inventory
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.operations.iam2_operations as iam2_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.operations.account_operations as acc_ops
from zstackwoodpecker.operations import vm_operations as vm_ops
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.test_lib as test_lib

project_uuid = None
virtual_id_uuid = None
test_stub = test_lib.lib_get_test_stub()


def test():
    global virtual_id_uuid
    
    iam2_ops.clean_iam2_enviroment()

    flavor = case_flavor[os.environ.get('CASE_FLAVOR')]   

    username = "systemAdmin"
    password = 'b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86'
    vid_tst_obj = test_vid.ZstackTestVid()
    virtual_id_uuid = vid_tst_obj.get_vid().uuid
    test_stub.create_system_admin(username, password, vid_tst_obj)
    systemadminrole_uuid='2069fe8ff0fb49efac0d4db3650a8076'
    iam2_ops.add_roles_to_iam2_virtual_id([systemadminrole_uuid], virtual_id_uuid)

    system_admin_session_uuid = acc_ops.login_by_account(username, password)

    # Image related ops: Add, Delete, Expunge, sync image size, Update QGA, delete, expunge
    bs = res_ops.query_resource(res_ops.BACKUP_STORAGE)[0]
    image_option = test_util.ImageOption()
    image_option.set_name('fake_image')
    image_option.set_description('fake image')
    image_option.set_format('raw')
    image_option.set_mediaType('RootVolumeTemplate')
    image_option.set_backup_storage_uuid_list([bs.uuid])
    image_option.url = "http://fake/fake.raw"
    image_option.set_session_uuid(system_admin_session_uuid)
    image_uuid = img_ops.add_image(image_option).uuid
    img_ops.sync_image_size(image_uuid, session_uuid=system_admin_session_uuid)
    img_ops.change_image_state(image_uuid, 'disable', session_uuid=system_admin_session_uuid)
    img_ops.change_image_state(image_uuid, 'enable', session_uuid=system_admin_session_uuid)
    if bs.type == inventory.IMAGE_STORE_BACKUP_STORAGE_TYPE:
        img_ops.export_image_from_backup_storage(image_uuid, bs.uuid, session_uuid=system_admin_session_uuid)
        img_ops.delete_exported_image_from_backup_storage(image_uuid, bs.uuid, session_uuid=system_admin_session_uuid)
    img_ops.set_image_qga_enable(image_uuid, session_uuid=system_admin_session_uuid)
    img_ops.set_image_qga_disable(image_uuid, session_uuid=system_admin_session_uuid)
    img_ops.delete_image(image_uuid, session_uuid=system_admin_session_uuid)
    img_ops.expunge_image(image_uuid, session_uuid=system_admin_session_uuid)

    # Volume related ops: Create, Delete, Expunge, Attach, Dettach, Enable, Disable
    disk_offering_uuid = res_ops.query_resource(res_ops.DISK_OFFERING)[0].uuid
    acc_ops.share_resources([project_linked_account_uuid], [disk_offering_uuid])
    volume_option = test_util.VolumeOption()
    volume_option.set_disk_offering_uuid(disk_offering_uuid)
    volume_option.set_name('data_volume_project_management')
    volume_option.set_session_uuid(system_admin_session_uuid)
    data_volume = vol_ops.create_volume_from_offering(volume_option)
    vol_ops.stop_volume(data_volume.uuid, session_uuid=system_admin_session_uuid)
    vol_ops.start_volume(data_volume.uuid, session_uuid=system_admin_session_uuid)
    vm_creation_option = test_util.VmOption()
    l3_net_uuid = test_lib.lib_get_l3_by_name(os.environ.get('l3VlanNetwork3')).uuid
    acc_ops.share_resources([project_linked_account_uuid], [l3_net_uuid])
    vm_creation_option.set_l3_uuids([l3_net_uuid])
    image_uuid = test_lib.lib_get_image_by_name("centos").uuid
    vm_creation_option.set_image_uuid(image_uuid)
    acc_ops.share_resources([project_linked_account_uuid], [image_uuid])
    instance_offering_uuid = test_lib.lib_get_instance_offering_by_name(os.environ.get('instanceOfferingName_s')).uuid
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    acc_ops.share_resources([project_linked_account_uuid], [instance_offering_uuid])
    vm_creation_option.set_name('vm_for_project_management')
    vm_creation_option.set_session_uuid(system_admin_session_uuid)
    vm = test_stub.create_vm(image_uuid = image_uuid, session_uuid=system_admin_session_uuid) 
    vm_uuid = vm.get_vm().uuid
    vol_ops.attach_volume(data_volume.uuid, vm_uuid, session_uuid=system_admin_session_uuid)
    vol_ops.detach_volume(data_volume.uuid, vm_uuid, session_uuid=system_admin_session_uuid)
    vol_ops.delete_volume(data_volume.uuid, session_uuid=system_admin_session_uuid)
    vol_ops.expunge_volume(data_volume.uuid, session_uuid=system_admin_session_uuid)

    # VM related ops: Create, Delete, Expunge, Start, Stop, Suspend, Resume, Migrate
    vm_ops.stop_vm(vm_uuid, session_uuid=system_admin_session_uuid)
    vm_ops.start_vm(vm_uuid, session_uuid=system_admin_session_uuid)
    candidate_hosts = vm_ops.get_vm_migration_candidate_hosts(vm_uuid)
    if candidate_hosts != None and test_lib.lib_check_vm_live_migration_cap(vm.get_vm()):
        vm_ops.migrate_vm(vm_uuid, candidate_hosts.inventories[0].uuid, session_uuid=system_admin_session_uuid)
    vm_ops.stop_vm(vm_uuid, force='cold', session_uuid=system_admin_session_uuid)
    vm_ops.start_vm(vm_uuid, session_uuid=system_admin_session_uuid)
    vm_ops.suspend_vm(vm_uuid, session_uuid=system_admin_session_uuid)
    vm_ops.resume_vm(vm_uuid, session_uuid=system_admin_session_uuid)
    vm_ops.destroy_vm(vm_uuid, session_uuid=system_admin_session_uuid)
    vm_ops.expunge_vm(vm_uuid, session_uuid=system_admin_session_uuid)

    # L2 related ops: create, delete
    zone_uuid = res_ops.get_resource(res_ops.ZONE)[0].uuid
    try:
        l2 = net_ops.create_l2_novlan('l2_for_pm', 'eth0', zone_uuid, session_uuid=system_admin_session_uuid)
        test_util.test_fail("Expect exception: project admin not allowed to create Novlan L2 except vxlan")
    except:
        pass

    try:
        l2 = net_ops.create_l2_vlan('l2_for_pm', 'eth0', zone_uuid, 1234, session_uuid=system_admin_session_uuid)
        test_util.test_fail("Expect exception: project admin not allowed to create vlan L2 except vxlan")
    except:
        pass

    # 11 delete
    acc_ops.logout(system_admin_session_uuid)
    iam2_ops.delete_iam2_virtual_id(virtual_id_uuid)

    test_util.test_pass('success test iam2 login in by project admin!')


def error_cleanup():
    global virtual_id_uuid
    if virtual_id_uuid:
        iam2_ops.delete_iam2_virtual_id(virtual_id_uuid)
