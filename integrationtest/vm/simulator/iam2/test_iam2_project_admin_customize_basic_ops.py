'''
test iam2 platform admin basic operations
@author: zhaohao.chen
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
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.test_lib as test_lib
virtual_id_uuid = None
test_stub = test_lib.lib_get_test_stub()
#res_list: l2, l3, image, disk_offering, instance_offering
res_list = [res_ops.L2_NETWORK ,\
            res_ops.L3_NETWORK ,\
            res_ops.IMAGE ,\
            res_ops.DISK_OFFERING ,\
            res_ops.INSTANCE_OFFERING ,\
        ]

cond = res_ops.gen_query_conditions('name', '=', 'Project admin role')
prj_statement = res_ops.query_resource(res_ops.ROLE, cond)[0].statements[0].statement

def test():
    global virtual_id_uuid
    
    iam2_ops.clean_iam2_enviroment()
    #create vid
    username = "project admin test"
    password = 'b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86'
    virtual_id_uuid = iam2_ops.create_iam2_virtual_id(username, password).uuid
    #create project
    prj =  iam2_ops.create_iam2_project('project-test')
    prj_uuid = prj.uuid
    prj_linked_account_uuid = prj.linkedAccountUuid
    #add role to vid
    role_name = 'project_admin_customize'
    role_uuid = iam2_ops.create_role(role_name, statements=[prj_statement]).uuid
    res_ops.change_recource_owner(prj_linked_account_uuid,role_uuid)
    iam2_ops.add_roles_to_iam2_virtual_id([role_uuid], virtual_id_uuid)
    #add virtualID to project
    iam2_ops.add_iam2_virtual_ids_to_project([virtual_id_uuid], prj_uuid)
    #login
    session_uuid = iam2_ops.login_iam2_virtual_id(username, password)
    session_uuid = iam2_ops.login_iam2_project('project-test', session_uuid=session_uuid).uuid
    #share resources
    res_uuid_list = []
    for res in res_list:
        for inv in res_ops.query_resource(res):
            res_uuid_list.append(inv.uuid)
    acc_ops.share_resources([prj_linked_account_uuid], res_uuid_list)

    # Image related ops: Add, Delete, Expunge, sync image size, Update QGA, delete, expunge
    bs = res_ops.query_resource(res_ops.BACKUP_STORAGE)[0]
    image_option = test_util.ImageOption()
    image_option.set_name('fake_image')
    image_option.set_description('fake image')
    image_option.set_format('raw')
    image_option.set_mediaType('RootVolumeTemplate')
    image_option.set_backup_storage_uuid_list([bs.uuid])
    image_option.url = "http://fake/fake.raw"
    image_option.set_session_uuid(session_uuid)
    image_uuid = img_ops.add_image(image_option).uuid
    img_ops.sync_image_size(image_uuid, session_uuid=session_uuid)
    img_ops.change_image_state(image_uuid, 'disable', session_uuid=session_uuid)
    img_ops.change_image_state(image_uuid, 'enable', session_uuid=session_uuid)
    if bs.type == inventory.IMAGE_STORE_BACKUP_STORAGE_TYPE:
        img_ops.export_image_from_backup_storage(image_uuid, bs.uuid, session_uuid=session_uuid)
        img_ops.delete_exported_image_from_backup_storage(image_uuid, bs.uuid, session_uuid=session_uuid)
    img_ops.set_image_qga_enable(image_uuid, session_uuid=session_uuid)
    img_ops.set_image_qga_disable(image_uuid, session_uuid=session_uuid)
    img_ops.delete_image(image_uuid, session_uuid=session_uuid)
    img_ops.expunge_image(image_uuid, session_uuid=session_uuid)

    # Volume related ops: Create, Delete, Expunge, Attach, Dettach, Enable, Disable
    disk_offering_uuid = res_ops.query_resource(res_ops.DISK_OFFERING)[0].uuid
    volume_option = test_util.VolumeOption()
    volume_option.set_disk_offering_uuid(disk_offering_uuid)
    volume_option.set_name('data_volume_iam2_pf_adm')
    volume_option.set_session_uuid(session_uuid)
    data_volume = vol_ops.create_volume_from_offering(volume_option)
    vol_ops.stop_volume(data_volume.uuid, session_uuid=session_uuid)
    vol_ops.start_volume(data_volume.uuid, session_uuid=session_uuid)
    vm_creation_option = test_util.VmOption()
    l3_net_uuid = test_lib.lib_get_l3_by_name(os.environ.get('l3VlanNetwork3')).uuid
    vm_creation_option.set_l3_uuids([l3_net_uuid])
    image_uuid = test_lib.lib_get_image_by_name("centos").uuid
    vm_creation_option.set_image_uuid(image_uuid)
    instance_offering_uuid = test_lib.lib_get_instance_offering_by_name(os.environ.get('instanceOfferingName_s')).uuid
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_name('vm_iam2_pf_adm')
    vm_creation_option.set_session_uuid(session_uuid)
    vm = test_stub.create_vm(image_uuid = image_uuid, session_uuid=session_uuid) 
    vm_uuid = vm.get_vm().uuid
    vol_ops.attach_volume(data_volume.uuid, vm_uuid, session_uuid=session_uuid)
    vol_ops.detach_volume(data_volume.uuid, vm_uuid, session_uuid=session_uuid)
    vol_ops.delete_volume(data_volume.uuid, session_uuid=session_uuid)
    vol_ops.expunge_volume(data_volume.uuid, session_uuid=session_uuid)

    # L2 related ops: create, delete
    #zone_uuid = res_ops.get_resource(res_ops.ZONE)[0].uuid
    #l2 = net_ops.create_l2_novlan('l2_iam2_pf_adm', 'eth0', zone_uuid, session_uuid=session_uuid)
    #l2 = net_ops.create_l2_vlan('l2_iam2_pf_adm', 'eth0', zone_uuid, 1234, session_uuid=session_uuid)

    #L3 related ops:create, attach, detach, delete
    l2_uuid = res_ops.query_resource(res_ops.L2_NETWORK)[0].uuid
    ip_range_option = test_util.IpRangeOption()
    l3_name = 'l3_test'
    l3_uuid =  net_ops.create_l3(l3_name, l2_uuid).uuid
    ip_range_option.set_name('iprange_test')
    ip_range_option.set_l3_uuid(l3_uuid)
    ip_range_option.set_startIp('192.168.0.10')
    ip_range_option.set_endIp('192.168.0.11')
    ip_range_option.set_gateway('192.168.0.1')
    ip_range_option.set_netmask('255.255.255.0')
    net_ops.add_ip_range(ip_range_option)
    nics = net_ops.attach_l3(l3_uuid, vm_uuid).vmNics
    for nic in nics:
        if nic.l3NetworkUuid == l3_uuid:
            nic_uuid = nic.uuid
            break
    net_ops.detach_l3(nic_uuid)
    net_ops.delete_l3(l3_uuid)

    # VM related ops: Create, Delete, Expunge, Start, Stop, Suspend, Resume, Migrate
    vm_ops.stop_vm(vm_uuid, session_uuid=session_uuid)
    vm_ops.start_vm(vm_uuid, session_uuid=session_uuid)
    candidate_hosts = vm_ops.get_vm_migration_candidate_hosts(vm_uuid)
    if candidate_hosts != None and test_lib.lib_check_vm_live_migration_cap(vm.get_vm()):
        vm_ops.migrate_vm(vm_uuid, candidate_hosts.inventories[0].uuid, session_uuid=session_uuid)
    vm_ops.stop_vm(vm_uuid, force='cold', session_uuid=session_uuid)
    vm_ops.start_vm(vm_uuid, session_uuid=session_uuid)
    vm_ops.suspend_vm(vm_uuid, session_uuid=session_uuid)
    vm_ops.resume_vm(vm_uuid, session_uuid=session_uuid)
    vm_ops.destroy_vm(vm_uuid, session_uuid=session_uuid)
    vm_ops.expunge_vm(vm_uuid, session_uuid=session_uuid)
        
    #delete
    acc_ops.logout(session_uuid)
    iam2_ops.delete_iam2_virtual_id(virtual_id_uuid)

    test_util.test_pass('success test iam2 platform admin basic operations!')


def error_cleanup():
    global virtual_id_uuid
    if virtual_id_uuid:
        iam2_ops.delete_iam2_virtual_id(virtual_id_uuid)
