'''
test iam2 login by platform admin

# 1 create project
# 2 create virtual id
# 3 create project admin
# 4 login in project by project admin
# 5 create virtual id group
# 6 create role
# 7 add virtual id into project and group
# 8 add/remove roles to/from virtual id (group)
# 9 create/delete project operator
# 10 remove virtual ids from group and project
# 11 delete

@author: rhZhou
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
import zstackwoodpecker.test_lib as test_lib

project_uuid = None
virtual_id_uuid = None
project_admin_uuid = None
test_stub = test_lib.lib_get_test_stub()


def test():
    global project_uuid, project_admin_uuid, virtual_id_uuid

    # 1 create project
    project_name = 'test_project'
    project = iam2_ops.create_iam2_project(project_name)
    project_uuid = project.uuid
    project_linked_account_uuid = project.linkedAccountUuid

    # 2 create virtual id
    project_admin_name = 'username'
    project_admin_password = 'password'
    project_admin_uuid = iam2_ops.create_iam2_virtual_id(project_admin_name, project_admin_password).uuid
    virtual_id_uuid = iam2_ops.create_iam2_virtual_id('usernametwo', 'password').uuid

    # 3 create project admin
    iam2_ops.add_iam2_virtual_ids_to_project([project_admin_uuid],project_uuid)
    attributes = [{"name": "__ProjectAdmin__", "value": project_uuid}]
    iam2_ops.add_attributes_to_iam2_virtual_id(project_admin_uuid, attributes)

    # 4 login in project by project admin
    project_admin_session_uuid = iam2_ops.login_iam2_virtual_id(project_admin_name, project_admin_password)
    project_login_uuid = iam2_ops.login_iam2_project(project_name, session_uuid=project_admin_session_uuid).uuid
    # iam2_ops.remove_attributes_from_iam2_virtual_id(virtual_id_uuid, attributes)


    # Image related ops: Add, Delete, Expunge, sync image size, Update QGA, delete, expunge
    bs = res_ops.query_resource(res_ops.BACKUP_STORAGE)[0]
    image_option = test_util.ImageOption()
    image_option.set_name('fake_image')
    image_option.set_description('fake image')
    image_option.set_format('raw')
    image_option.set_mediaType('RootVolumeTemplate')
    image_option.set_backup_storage_uuid_list([bs.uuid])
    image_option.url = "http://fake/fake.raw"
    image_option.set_session_uuid(project_login_uuid)
    image_uuid = img_ops.add_image(image_option).uuid
    img_ops.sync_image_size(image_uuid, session_uuid=project_login_uuid)
    img_ops.change_image_state(image_uuid, 'disable', session_uuid=project_login_uuid)
    img_ops.change_image_state(image_uuid, 'enable', session_uuid=project_login_uuid)
    if bs.type == inventory.IMAGE_STORE_BACKUP_STORAGE_TYPE:
        img_ops.export_image_from_backup_storage(image_uuid, bs.uuid, session_uuid=project_login_uuid)
        img_ops.delete_exported_image_from_backup_storage(image_uuid, bs.uuid, session_uuid=project_login_uuid)
    img_ops.set_image_qga_enable(image_uuid, session_uuid=project_login_uuid)
    img_ops.set_image_qga_disable(image_uuid, session_uuid=project_login_uuid)
    img_ops.delete_image(image_uuid, session_uuid=project_login_uuid)
    img_ops.expunge_image(image_uuid, session_uuid=project_login_uuid)

    # Volume related ops: Create, Delete, Expunge, Attach, Dettach, Enable, Disable
    disk_offering_uuid = res_ops.query_resource(res_ops.DISK_OFFERING)[0].uuid
    acc_ops.share_resources([project_linked_account_uuid], [disk_offering_uuid])
    volume_option = test_util.VolumeOption()
    volume_option.set_disk_offering_uuid(disk_offering_uuid)
    volume_option.set_name('data_volume_project_management')
    volume_option.set_session_uuid(project_login_uuid)
    data_volume = vol_ops.create_volume_from_offering(volume_option)
    vol_ops.stop_volume(data_volume.uuid, session_uuid=project_login_uuid)
    vol_ops.start_volume(data_volume.uuid, session_uuid=project_login_uuid)
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
    vm_creation_option.set_session_uuid(project_login_uuid)
    vm = test_stub.create_vm(image_uuid = image_uuid, session_uuid=project_login_uuid) 
    vm_uuid = vm.get_vm().uuid
    vol_ops.attach_volume(data_volume.uuid, vm_uuid, session_uuid=project_login_uuid)
    vol_ops.detach_volume(data_volume.uuid, vm_uuid, session_uuid=project_login_uuid)
    vol_ops.delete_volume(data_volume.uuid, session_uuid=project_login_uuid)
    vol_ops.expunge_volume(data_volume.uuid, session_uuid=project_login_uuid)

    # VM related ops: Create, Delete, Expunge, Start, Stop, Suspend, Resume, Migrate
    vm_ops.stop_vm(vm_uuid, session_uuid=project_login_uuid)
    vm_ops.start_vm(vm_uuid, session_uuid=project_login_uuid)
    candidate_hosts = vm_ops.get_vm_migration_candidate_hosts(vm_uuid)
    if candidate_hosts != None and test_lib.lib_check_vm_live_migration_cap(vm.get_vm()):
        vm_ops.migrate_vm(vm_uuid, candidate_hosts.inventories[0].uuid, session_uuid=project_login_uuid)
    vm_ops.stop_vm(vm_uuid, force='cold', session_uuid=project_login_uuid)
    vm_ops.start_vm(vm_uuid, session_uuid=project_login_uuid)
    vm_ops.suspend_vm(vm_uuid, session_uuid=project_login_uuid)
    vm_ops.resume_vm(vm_uuid, session_uuid=project_login_uuid)
    vm_ops.destroy_vm(vm_uuid, session_uuid=project_login_uuid)
    vm_ops.expunge_vm(vm_uuid, session_uuid=project_login_uuid)

    # L2 related ops:

    # L3 related ops:

    # network service ops:

    # zwatch ops:

    # scheduler ops:

    # certificate

    # 11 delete
    acc_ops.logout(project_login_uuid)
    iam2_ops.delete_iam2_virtual_id(virtual_id_uuid)
    iam2_ops.delete_iam2_virtual_id(project_admin_uuid)
    iam2_ops.delete_iam2_project(project_uuid)
    iam2_ops.expunge_iam2_project(project_uuid)

    test_util.test_pass('success test iam2 login in by project admin!')


def error_cleanup():
    global project_uuid, project_admin_uuid, virtual_id_uuid
    if virtual_id_uuid:
        iam2_ops.delete_iam2_virtual_id(virtual_id_uuid)
    if project_admin_uuid:
        iam2_ops.delete_iam2_virtual_id(project_admin_uuid)
    if project_uuid:
        iam2_ops.delete_iam2_project(project_uuid)
        iam2_ops.expunge_iam2_project(project_uuid)
