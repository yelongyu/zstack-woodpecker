'''

Create an unified test_stub to share test operations

@author: Youyk
'''

import os

import apibinding.api_actions as api_actions
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.zone_operations as zone_ops
import zstackwoodpecker.operations.iam2_ticket_operations as ticket_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm
import zstackwoodpecker.zstack_test.zstack_test_volume as test_volume
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.operations.vpc_operations as vpc_ops
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.zstack_test.zstack_test_volume as zstack_volume_header
import zstackwoodpecker.zstack_test.zstack_test_vip as zstack_vip_header
import zstackwoodpecker.zstack_test.zstack_test_eip as zstack_eip_header
import zstackwoodpecker.zstack_test.zstack_test_image as test_image
import zstackwoodpecker.header.vm as vm_header
from zstackwoodpecker.operations import vm_operations as vm_ops
import zstackwoodpecker.operations.longjob_operations as longjob_ops
import zstackwoodpecker.operations.billing_operations as bill_ops
import time
import re
import json
import random

def remove_all_vpc_vrouter():
    cond = res_ops.gen_query_conditions('applianceVmType', '=', 'vpcvrouter')
    vr_vm_list = res_ops.query_resource(res_ops.APPLIANCE_VM, cond)
    if vr_vm_list:
        for vr_vm in vr_vm_list:
            nic_uuid_list = [nic.uuid for nic in vr_vm.vmNics if nic.metaData == '4']
            for nic_uuid in nic_uuid_list:
                net_ops.detach_l3(nic_uuid)
            vm_ops.destroy_vm(vr_vm.uuid)

def share_admin_resource_include_vxlan_pool(account_uuid_list, session_uuid=None):
    instance_offerings = res_ops.get_resource(res_ops.INSTANCE_OFFERING)
    for instance_offering in instance_offerings:
        acc_ops.share_resources(account_uuid_list, [instance_offering.uuid], session_uuid)
    cond1 = res_ops.gen_query_conditions('mediaType', '!=', 'ISO')
    images = res_ops.query_resource(res_ops.IMAGE, cond1)
    for image in images:
        acc_ops.share_resources(account_uuid_list, [image.uuid], session_uuid)

    l3nets = res_ops.get_resource(res_ops.L3_NETWORK)
    for l3net in l3nets:
        acc_ops.share_resources(account_uuid_list, [l3net.uuid], session_uuid)

    l2vxlan_pools = res_ops.get_resource(res_ops.L2_VXLAN_NETWORK_POOL)
    for l2vxlan_pool in l2vxlan_pools:
        acc_ops.share_resources(account_uuid_list, [l2vxlan_pool.uuid], session_uuid)

    virtual_router_offerings = res_ops.get_resource(res_ops.VR_OFFERING)
    for virtual_router_offering in virtual_router_offerings:
        acc_ops.share_resources(account_uuid_list, [virtual_router_offering.uuid], session_uuid)
    volume_offerings = res_ops.get_resource(res_ops.DISK_OFFERING)
    for volume_offering in volume_offerings:
        acc_ops.share_resources(account_uuid_list, [volume_offering.uuid], session_uuid)


def revoke_admin_resource(account_uuid_list, session_uuid=None):
    instance_offerings = res_ops.get_resource(res_ops.INSTANCE_OFFERING)
    for instance_offering in instance_offerings:
        acc_ops.revoke_resources(account_uuid_list, [instance_offering.uuid], session_uuid)
    cond2 = res_ops.gen_query_conditions('mediaType', '!=', 'ISO')
    images = res_ops.query_resource(res_ops.IMAGE, cond2)
    for image in images:
        acc_ops.revoke_resources(account_uuid_list, [image.uuid], session_uuid)
    l3nets = res_ops.get_resource(res_ops.L3_NETWORK)
    for l3net in l3nets:
        acc_ops.revoke_resources(account_uuid_list, [l3net.uuid], session_uuid)

    l2vxlan_pool_uuid = res_ops.get_resource(res_ops.L2_VXLAN_NETWORK_POOL)[0].uuid
    acc_ops.revoke_resources(account_uuid_list, [l2vxlan_pool_uuid], session_uuid)

    virtual_router_offerings = res_ops.get_resource(res_ops.VR_OFFERING)
    for virtual_router_offering in virtual_router_offerings:
        acc_ops.revoke_resources(account_uuid_list, [virtual_router_offering.uuid], session_uuid)
    volume_offerings = res_ops.get_resource(res_ops.DISK_OFFERING)
    for volume_offering in volume_offerings:
        acc_ops.revoke_resources(account_uuid_list, [volume_offering.uuid], session_uuid)

def get_image_by_bs(bs_uuid):
    cond = res_ops.gen_query_conditions('mediaType', '!=', 'ISO')
    cond = res_ops.gen_query_conditions('platform', '=', 'Linux', cond)
    cond = res_ops.gen_query_conditions('system','=','false', cond)
    images = res_ops.query_resource(res_ops.IMAGE, cond)
    for image in images:
        for bs_ref in image.backupStorageRefs:
            if bs_ref.backupStorageUuid == bs_uuid:
                return image.uuid

def create_vm(vm_creation_option=None, volume_uuids=None, root_disk_uuid=None,
              image_uuid=None, ps_uuid=None, session_uuid=None):
    if not vm_creation_option:
        instance_offering_uuid = test_lib.lib_get_instance_offering_by_name(
            os.environ.get('instanceOfferingName_s')).uuid
        cond = res_ops.gen_query_conditions('mediaType', '!=', 'ISO')
        cond = res_ops.gen_query_conditions('platform', '=', 'Linux', cond)
        cond = res_ops.gen_query_conditions('system','=','false',cond)
        l3net_uuid = test_lib.lib_get_l3_by_name(
            os.environ.get('l3VlanNetworkName3')).uuid
	if image_uuid:
	    image_uuid = image_uuid
	else:
            image_uuid = res_ops.query_resource(
            res_ops.IMAGE, cond, session_uuid)[0].uuid
        vm_creation_option = test_util.VmOption()
        vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
        vm_creation_option.set_image_uuid(image_uuid)
        vm_creation_option.set_l3_uuids([l3net_uuid])
        vm_creation_option.set_timeout(864000000)

    if volume_uuids:
        if isinstance(volume_uuids, list):
            vm_creation_option.set_data_disk_uuids(volume_uuids)
        else:
            test_util.test_fail(
                'volume_uuids type: %s is not "list".' % type(volume_uuids))

    if root_disk_uuid:
        vm_creation_option.set_root_disk_uuid(root_disk_uuid)

    if image_uuid:
        vm_creation_option.set_image_uuid(image_uuid)

    if ps_uuid:
        vm_creation_option.set_ps_uuid(ps_uuid)

    if session_uuid:
        vm_creation_option.set_session_uuid(session_uuid)

    vm = test_vm.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    return vm

def create_vr_vm(test_obj_dict,l3_uuid, session_uuid = None):
    '''
    '''
    vrs = test_lib.lib_find_vr_by_l3_uuid(l3_uuid)
    if not vrs:
        #create temp_vm1 for getting vlan1's vr for test pf_vm portforwarding
        instance_offering_uuid = test_lib.lib_get_instance_offering_by_name(
            os.environ.get('instanceOfferingName_s')).uuid
        cond = res_ops.gen_query_conditions('mediaType', '!=', 'ISO')
        cond = res_ops.gen_query_conditions('platform', '=', 'Linux', cond)
        cond = res_ops.gen_query_conditions('system','=','false',cond)
        image_uuid = res_ops.query_resource(res_ops.IMAGE, cond, session_uuid=session_uuid)[0].uuid

        vm_creation_option = test_util.VmOption()
        vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
        vm_creation_option.set_image_uuid(image_uuid)
        vm_creation_option.set_l3_uuids([l3_uuid])
        temp_vm = create_vm(vm_creation_option,session_uuid=session_uuid)
        test_obj_dict.add_vm(temp_vm)
        vr = test_lib.lib_find_vr_by_vm(temp_vm.vm)[0]
        temp_vm.destroy(session_uuid)
        test_obj_dict.rm_vm(temp_vm)
    else:
        vr = vrs[0]
        if not test_lib.lib_is_vm_running(vr):
            test_lib.lib_robot_cleanup(test_obj_dict)
            test_util.test_skip('vr: %s is not running. Will skip test.' % vr.uuid)
    return vr

def create_windows_vm(vm_creation_option=None, volume_uuids=None, root_disk_uuid=None, image_uuid=None, session_uuid=None):
    if not vm_creation_option:
        instance_offering_uuid = test_lib.lib_get_instance_offering_by_name(
            os.environ.get('instanceOfferingName_win')).uuid
        cond = res_ops.gen_query_conditions('mediaType', '!=', 'ISO')
        cond = res_ops.gen_query_conditions('platform', '=', 'Windows', cond)
        image_uuid = res_ops.query_resource(
            res_ops.IMAGE, cond, session_uuid)[0].uuid
        l3net_uuid = test_lib.lib_get_l3_by_name(
            os.environ.get('l3VlanNetworkName3')).uuid
        vm_creation_option = test_util.VmOption()
        vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
        vm_creation_option.set_image_uuid(image_uuid)
        vm_creation_option.set_l3_uuids([l3net_uuid])
    return create_vm(vm_creation_option, volume_uuids, root_disk_uuid, image_uuid, session_uuid)

def create_volume(volume_creation_option=None, session_uuid=None):
    if not volume_creation_option:
        disk_offering = test_lib.lib_get_disk_offering_by_name(
            os.environ.get('smallDiskOfferingName'))
        volume_creation_option = test_util.VolumeOption()
        volume_creation_option.set_disk_offering_uuid(disk_offering.uuid)
        volume_creation_option.set_name('test_volume')

    if session_uuid:
        volume_creation_option.set_session_uuid(session_uuid)

    volume = zstack_volume_header.ZstackTestVolume()
    volume.set_creation_option(volume_creation_option)
    volume.create()
    return volume


def create_vm_with_volume(vm_creation_option=None, data_volume_uuids=None,
                          session_uuid=None):
    if not data_volume_uuids:
        disk_offering = test_lib.lib_get_disk_offering_by_name(
            os.environ.get('smallDiskOfferingName'), session_uuid)
        data_volume_uuids = [disk_offering.uuid]
    return create_vm(vm_creation_option, data_volume_uuids,
                     session_uuid=session_uuid)


def create_vm_with_iso(vm_creation_option=None, session_uuid=None):
    img_option = test_util.ImageOption()
    img_option.set_name('iso')
    root_disk_uuid = test_lib.lib_get_disk_offering_by_name(
        os.environ.get('rootDiskOfferingName')).uuid
    bs_uuid = res_ops.query_resource_fields(res_ops.BACKUP_STORAGE, [],
                                            session_uuid)[0].uuid
    img_option.set_backup_storage_uuid_list([bs_uuid])
    if os.path.exists("%s/apache-tomcat/webapps/zstack/static/zstack-repo/" % (os.environ.get('zstackInstallPath'))):
        os.system("genisoimage -o %s/apache-tomcat/webapps/zstack/static/zstack-repo/7/x86_64/os/test.iso /tmp/" % (os.environ.get('zstackInstallPath')))
        img_option.set_url('http://%s:8080/zstack/static/zstack-repo/7/x86_64/os/test.iso' % (os.environ.get('node1Ip')))
    else:
        os.system("genisoimage -o %s/apache-tomcat/webapps/zstack/static/test.iso /tmp/" % (os.environ.get('zstackInstallPath')))
        img_option.set_url('http://%s:8080/zstack/static/test.iso' % (os.environ.get('node1Ip')))

    image_uuid = img_ops.add_iso_template(img_option).uuid

    return create_vm(vm_creation_option, None, root_disk_uuid, image_uuid,
                     session_uuid=session_uuid)


def create_vm_with_previous_iso(vm_creation_option=None, session_uuid=None):
    cond = res_ops.gen_query_conditions('name', '=', 'iso')
    image_uuid = res_ops.query_resource(res_ops.IMAGE, cond)[0].uuid
    root_disk_uuid = test_lib.lib_get_disk_offering_by_name(
        os.environ.get('rootDiskOfferingName')).uuid
    return create_vm(vm_creation_option, None, root_disk_uuid, image_uuid,
                     session_uuid=session_uuid)

def create_zone(name=None,description=None,session_uuid=None):
    zone_create_option = test_util.ZoneOption()
    zone_create_option.set_name('new_test_zone')
    zone_create_option.set_description('a new zone for deleted test')
    if name:
        zone_create_option.set_name(name)
    if description:
        zone_create_option.set_description(description)
    zone_inv = zone_ops.create_zone(zone_create_option,session_uuid)
    return zone_inv

def create_vm_ticket(virtual_id_uuid , project_uuid , session_uuid , name=None , request_name=None ,execute_times=None,instance_offering_uuid=None , image_uuid = None, l3_network_uuid=None ):
    if not instance_offering_uuid:
        conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
        instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid
    if not image_uuid:
        image_name = os.environ.get('imageName_s')
        image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    if not l3_network_uuid:
        l3_name = os.environ.get('l3VlanNetworkName1')
        l3_network_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    api_body = {"name": "vm", "instanceOfferingUuid": instance_offering_uuid, "imageUuid": image_uuid,
                "l3NetworkUuids": [l3_network_uuid]}
    api_name = 'org.zstack.header.vm.APICreateVmInstanceMsg'
    if not execute_times:
        execute_times = 1
    if not name:
        name = 'ticket_for_test'
    if not request_name:
        request_name = 'create-vm-ticket'
    account_system_type = 'iam2'
    ticket = ticket_ops.create_ticket(name, request_name, api_body, api_name, execute_times, account_system_type,virtual_id_uuid, project_uuid, session_uuid=session_uuid)
    return ticket

def share_admin_resource(account_uuid_list):
    instance_offerings = res_ops.get_resource(res_ops.INSTANCE_OFFERING)
    for instance_offering in instance_offerings:
        acc_ops.share_resources(account_uuid_list, [instance_offering.uuid])
    cond = res_ops.gen_query_conditions('mediaType', '!=', 'ISO')
    images = res_ops.query_resource(res_ops.IMAGE, cond)
    for image in images:
        acc_ops.share_resources(account_uuid_list, [image.uuid])
    l3net_uuid = res_ops.get_resource(res_ops.L3_NETWORK)[0].uuid
    root_disk_uuid = test_lib.lib_get_disk_offering_by_name(
        os.environ.get('rootDiskOfferingName')).uuid
    data_disk_uuid = test_lib.lib_get_disk_offering_by_name(
        os.environ.get('smallDiskOfferingName')).uuid
    acc_ops.share_resources(
        account_uuid_list, [l3net_uuid, root_disk_uuid, data_disk_uuid])

def check_resource_not_exist(uuid,resource_type):
    conditions = res_ops.gen_query_conditions('uuid', '=', uuid)
    resource_inv = res_ops.query_resource(resource_type,conditions)
    if resource_inv:
        test_util.test_fail("resource [%s] is still exist,uuid [%s]"%(resource_type,uuid))


def check_libvirt_host_uuid():
    libvirt_dir = "/etc/libvirt/libvirtd.conf"
    p = re.compile(r'^host_uuid')
    with open(libvirt_dir, 'r') as a:
        lines = a.readlines()
        for line in lines:
            if re.match(p, line):
                return True
    return False

def create_spice_vm(vm_creation_option=None, volume_uuids=None, root_disk_uuid=None,
              image_uuid=None,system_tag="vmConsoleMode::spice", session_uuid=None):
    if not vm_creation_option:
        instance_offering_uuid = test_lib.lib_get_instance_offering_by_name(
            os.environ.get('instanceOfferingName_s')).uuid
        cond = res_ops.gen_query_conditions('mediaType', '!=', 'ISO')
        cond = res_ops.gen_query_conditions('platform', '=', 'Linux', cond)
        image_uuid = res_ops.query_resource(
            res_ops.IMAGE, cond, session_uuid)[0].uuid
        l3net_uuid = res_ops.get_resource(
            res_ops.L3_NETWORK, session_uuid)[0].uuid
        vm_creation_option = test_util.VmOption()
        vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
        vm_creation_option.set_image_uuid(image_uuid)
        vm_creation_option.set_l3_uuids([l3net_uuid])
        vm_creation_option.set_system_tags([system_tag])

    if volume_uuids:
        if isinstance(volume_uuids, list):
            vm_creation_option.set_data_disk_uuids(volume_uuids)
        else:
            test_util.test_fail(
                'volume_uuids type: %s is not "list".' % type(volume_uuids))

    if root_disk_uuid:
        vm_creation_option.set_root_disk_uuid(root_disk_uuid)

    if image_uuid:
        vm_creation_option.set_image_uuid(image_uuid)

    if session_uuid:
        vm_creation_option.set_session_uuid(session_uuid)

    vm = test_vm.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    return vm

def get_vm_console_protocol(uuid, session_uuid=None):
    action = api_actions.GetVmConsoleAddressAction()
    action.timeout = 30000
    action.uuid = uuid
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    test_util.action_logger('Get VM Console protocol:  %s ' % evt.protocol)
    return evt

def create_vnc_vm(vm_creation_option=None, volume_uuids=None, root_disk_uuid=None,
              image_uuid=None,system_tag="vmConsoleMode::vnc", session_uuid=None):
    if not vm_creation_option:
        instance_offering_uuid = test_lib.lib_get_instance_offering_by_name(
            os.environ.get('instanceOfferingName_s')).uuid
        cond = res_ops.gen_query_conditions('mediaType', '!=', 'ISO')
        cond = res_ops.gen_query_conditions('platform', '=', 'Linux', cond)
        image_uuid = res_ops.query_resource(
            res_ops.IMAGE, cond, session_uuid)[0].uuid
        l3net_uuid = res_ops.get_resource(
            res_ops.L3_NETWORK, session_uuid)[0].uuid
        vm_creation_option = test_util.VmOption()
        vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
        vm_creation_option.set_image_uuid(image_uuid)
        vm_creation_option.set_l3_uuids([l3net_uuid])
        vm_creation_option.set_system_tags([system_tag])

    if volume_uuids:
        if isinstance(volume_uuids, list):
            vm_creation_option.set_data_disk_uuids(volume_uuids)
        else:
            test_util.test_fail(
                'volume_uuids type: %s is not "list".' % type(volume_uuids))

    if root_disk_uuid:
        vm_creation_option.set_root_disk_uuid(root_disk_uuid)

    if image_uuid:
        vm_creation_option.set_image_uuid(image_uuid)

    if session_uuid:
        vm_creation_option.set_session_uuid(session_uuid)

    vm = test_vm.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    return vm

def create_ag_vm(vm_creation_option=None, volume_uuids=None, root_disk_uuid=None,
              image_uuid=None, affinitygroup_uuid=None, host_uuid=None, session_uuid=None):
    if not vm_creation_option:
        instance_offering_uuid = test_lib.lib_get_instance_offering_by_name(
            os.environ.get('instanceOfferingName_s')).uuid
        cond = res_ops.gen_query_conditions('mediaType', '!=', 'ISO')
        cond = res_ops.gen_query_conditions('platform', '=', 'Linux', cond)
        cond = res_ops.gen_query_conditions('system', '=', 'false', cond)
        image_uuid = res_ops.query_resource(
            res_ops.IMAGE, cond, session_uuid)[0].uuid
        cond = res_ops.gen_query_conditions('category', '!=', 'System')
        l3net_uuid = res_ops.query_resource(
            res_ops.L3_NETWORK, cond, session_uuid)[0].uuid
        vm_creation_option = test_util.VmOption()
        vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
        vm_creation_option.set_image_uuid(image_uuid)
        vm_creation_option.set_l3_uuids([l3net_uuid])
        vm_creation_option.set_host_uuid(host_uuid)

    if affinitygroup_uuid:
        vm_creation_option.set_system_tags(["affinityGroupUuid::%s" % affinitygroup_uuid])

    if volume_uuids:
        if isinstance(volume_uuids, list):
            vm_creation_option.set_data_disk_uuids(volume_uuids)
        else:
            test_util.test_fail(
                'volume_uuids type: %s is not "list".' % type(volume_uuids))

    if root_disk_uuid:
        vm_creation_option.set_root_disk_uuid(root_disk_uuid)

    if image_uuid:
        vm_creation_option.set_image_uuid(image_uuid)

    if session_uuid:
        vm_creation_option.set_session_uuid(session_uuid)

    vm = test_vm.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    return vm


def create_data_volume_template_from_volume(volume_uuid, backup_storage_uuid_list, name = None, session_uuid = None ):
    volume_temp = vol_ops.create_volume_template(volume_uuid, backup_storage_uuid_list, name, session_uuid)
    return volume_temp

def create_data_volume_from_template(image_uuid, ps_uuid, name = None, host_uuid = None ):
    vol = vol_ops.create_volume_from_template(image_uuid, ps_uuid, name, host_uuid)
    return vol

def export_image_from_backup_storage(image_uuid, bs_uuid, session_uuid = None):
    imageurl = img_ops.export_image_from_backup_storage(image_uuid, bs_uuid, session_uuid)
    return imageurl

def delete_volume_image(image_uuid):
    img_ops.delete_image(image_uuid)

def get_local_storage_volume_migratable_hosts(volume_uuid):
    hosts = vol_ops.get_volume_migratable_host(volume_uuid)
    return hosts

def migrate_local_storage_volume(volume_uuid, host_uuid):
    vol_ops.migrate_volume(volume_uuid, host_uuid)

def delete_volume(volume_uuid):
    evt = vol_ops.delete_volume(volume_uuid)
    return evt

def expunge_volume(volume_uuid):
    evt = vol_ops.expunge_volume(volume_uuid)
    return evt

def recover_volume(volume_uuid):
    evt = vol_ops.recover_volume(volume_uuid)
    return evt

def expunge_image(image_uuid):
    evt = img_ops.expunge_image(image_uuid)
    return evt

def create_vip(vip_name=None, l3_uuid=None, session_uuid = None, required_ip=None):
    if not vip_name:
        vip_name = 'test vip'
    if not l3_uuid:
        l3_name = os.environ.get('l3PublicNetworkName')
        l3_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid

    vip_creation_option = test_util.VipOption()
    vip_creation_option.set_name(vip_name)
    vip_creation_option.set_l3_uuid(l3_uuid)
    vip_creation_option.set_session_uuid(session_uuid)
    vip_creation_option.set_requiredIp(required_ip)

    vip = zstack_vip_header.ZstackTestVip()
    vip.set_creation_option(vip_creation_option)
    vip.create()
    return vip

def create_eip(vip_uuid,eip_name=None,vnic_uuid=None, vm_obj=None, \
        session_uuid = None):

    eip_option = test_util.EipOption()
    eip_option.set_name(eip_name)
    eip_option.set_vip_uuid(vip_uuid)
    eip_option.set_vm_nic_uuid(vnic_uuid)
    eip_option.set_session_uuid(session_uuid)
    eip = zstack_eip_header.ZstackTestEip()
    eip.set_creation_option(eip_option)
    if vnic_uuid and not vm_obj:
        test_util.test_fail('vm_obj can not be None in create_eip() API, when setting vm_nic_uuid.')
    eip.create(vm_obj)
    return eip


def delete_vip(vip_uuid, session_uuid = None):
    action = api_actions.DeleteVipAction()
    action.timeout = 30000
    action.uuid = vip_uuid
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    test_util.action_logger('Delete Vip:  %s ' % vip_uuid)
    return evt 

def create_vpc_vrouter(vr_name='test_vpc'):
    conf = res_ops.gen_query_conditions('name', '=', 'test_vpc')
    vr_list = res_ops.query_resource(res_ops.APPLIANCE_VM, conf)
    if vr_list:
        return ZstackTestVR(vr_list[0])
    vr_offering = res_ops.get_resource(res_ops.VR_OFFERING)[0]
    vr_inv =  vpc_ops.create_vpc_vrouter(name=vr_name, virtualrouter_offering_uuid=vr_offering.uuid)
    return ZstackTestVR(vr_inv)

def query_vpc_vrouter(vr_name):
    conf = res_ops.gen_query_conditions('name', '=', vr_name)
    vr_list = res_ops.query_resource(res_ops.APPLIANCE_VM, conf)
    if vr_list:
        return ZstackTestVR(vr_list[0])

def attach_l3_to_vpc_vr(vpc_vr, l3_list):
    for l3 in l3_list:
        vpc_vr.add_nic(l3.uuid)

def attach_l3_to_vpc_vr_by_uuid(vpc_vr, l3_uuid):
    vpc_vr.add_nic(l3_uuid)

class ZstackTestVR(vm_header.TestVm):
    def __init__(self, vr_inv):
        super(ZstackTestVR, self).__init__()
        self._inv = vr_inv

    def __hash__(self):
        return hash(self.inv.uuid)

    def __eq__(self, other):
        return self.inv.uuid == other.inv.uuid

    @property
    def inv(self):
        return self._inv

    @inv.setter
    def inv(self, value):
        self._inv = value

    def destroy(self, session_uuid = None):
        vm_ops.destroy_vm(self.inv.uuid, session_uuid)
        super(ZstackTestVR, self).destroy()

    def reboot(self, session_uuid = None):
        self.inv = vm_ops.reboot_vm(self.inv.uuid, session_uuid)
        super(ZstackTestVR, self).reboot()

    def reconnect(self, session_uuid = None):
        self.inv = vm_ops.reconnect_vr(self.inv.uuid, session_uuid)

    def migrate(self, host_uuid, timeout = None, session_uuid = None):
        self.inv = vm_ops.migrate_vm(self.inv.uuid, host_uuid, timeout, session_uuid)
        super(ZstackTestVR, self).migrate(host_uuid)

    def migrate_to_random_host(self, timeout = None, session_uuid = None):
        host_uuid = random.choice([host.uuid for host in res_ops.get_resource(res_ops.HOST)
                                                      if host.uuid != test_lib.lib_find_host_by_vm(self.inv).uuid])
        self.inv = vm_ops.migrate_vm(self.inv.uuid, host_uuid, timeout, session_uuid)
        super(ZstackTestVR, self).migrate(host_uuid)

    def update(self):
        '''
        If vm's status was changed by none vm operations, it needs to call
        vm.update() to update vm's infromation.

        The none vm operations: host.maintain() host.delete(), zone.delete()
        cluster.delete()
        '''
        super(ZstackTestVR, self).update()
        if self.get_state != vm_header.EXPUNGED:
            update_inv = test_lib.lib_get_vm_by_uuid(self.inv.uuid)
            if update_inv:
                self.inv = update_inv
                #vm state need to chenage to stopped, if host is deleted
                host = test_lib.lib_find_host_by_vm(update_inv)
                if not host and self.inv.state != vm_header.STOPPED:
                    self.set_state(vm_header.STOPPED)
            else:
                self.set_state(vm_header.EXPUNGED)
            return self.inv

    def add_nic(self, l3_uuid):
        '''
        Add a new NIC device to VM. The NIC device will connect with l3_uuid.
        '''
        self.inv = net_ops.attach_l3(l3_uuid, self.inv.uuid)

    def remove_nic(self, nic_uuid):
        '''
        Detach a NIC from VM.
        '''
        self.inv = net_ops.detach_l3(nic_uuid)


def sleep_util(timestamp):
   while True:
      if time.time() >= timestamp:
         break
      time.sleep(0.5)


class MulISO(object):
    def __init__(self):
        self.vm1 = None
        self.vm2 = None
        self.iso_uuids = None
        self.iso = [{'name': 'iso1', 'url': 'http://zstack.yyk.net/iso/iso1.iso'},
                    {'name': 'iso2', 'url': 'http://zstack.yyk.net/iso/iso2.iso'},
                    {'name': 'iso3', 'url': 'http://zstack.yyk.net/iso/iso3.iso'}]

    def add_iso_image(self):
        bs_uuid = res_ops.query_resource(res_ops.BACKUP_STORAGE)[0].uuid
        images = res_ops.query_resource(res_ops.IMAGE)
        image_names = [i.name for i in  images]
        if self.iso[-1]['name'] not in image_names:
            for iso in self.iso:
                img_option = test_util.ImageOption()
                img_option.set_name(iso['name'])
                img_option.set_backup_storage_uuid_list([bs_uuid])
                testIsoUrl = iso['url']
                img_option.set_url(testIsoUrl)
                image_inv = img_ops.add_iso_template(img_option)
                image = test_image.ZstackTestImage()
                image.set_image(image_inv)
                image.set_creation_option(img_option)

    def get_all_iso_uuids(self):
        cond = res_ops.gen_query_conditions('mediaType', '=', 'ISO')
        iso_images = res_ops.query_resource(res_ops.IMAGE, cond)
        self.iso_uuids = [i.uuid for i in iso_images]
        self.iso_names = [i.name for i in iso_images]

    def check_iso_candidate(self, iso_name, vm_uuid=None, is_candidate=False):
        if not vm_uuid:
            vm_uuid = self.vm1.vm.uuid
        iso_cand = vm_ops.get_candidate_iso_for_attaching(vm_uuid)
        cand_name_list = [i.name for i in iso_cand]
        if is_candidate:
            assert iso_name in cand_name_list
        else:
            assert iso_name not in cand_name_list

    def create_vm(self, vm2=False):
        self.vm1 = create_vm()
        if vm2:
            self.vm2 = create_vm()

    def attach_iso(self, iso_uuid, vm_uuid=None):
        if not vm_uuid:
            vm_uuid = self.vm1.vm.uuid
        img_ops.attach_iso(iso_uuid, vm_uuid)
        self.check_vm_systag(iso_uuid, vm_uuid)

    def detach_iso(self, iso_uuid, vm_uuid=None):
        if not vm_uuid:
            vm_uuid = self.vm1.vm.uuid
        img_ops.detach_iso(vm_uuid, iso_uuid)
        self.check_vm_systag(iso_uuid, vm_uuid, tach='detach')

    def set_iso_first(self, iso_uuid, vm_uuid=None):
        if not vm_uuid:
            vm_uuid = self.vm1.vm.uuid
        system_tags = ['iso::%s::0' % iso_uuid]
        vm_ops.update_vm(vm_uuid, system_tags=system_tags)

    def check_vm_systag(self, iso_uuid, vm_uuid=None, tach='attach', order=None):
        if not vm_uuid:
            vm_uuid = self.vm1.vm.uuid
        cond = res_ops.gen_query_conditions('resourceUuid', '=', vm_uuid)
        systags = res_ops.query_resource(res_ops.SYSTEM_TAG, cond)
        iso_orders = {t.tag.split('::')[-2]: t.tag.split('::')[-1] for t in systags if 'iso' in t.tag}
        if tach == 'attach':
            assert iso_uuid in iso_orders
        else:
            assert iso_uuid not in iso_orders
        if order:
            assert iso_orders[iso_uuid] == order

class Longjob(object):
    def __init__(self):
        self.vm = None
        self.image_name_net = os.getenv('imageName_net')
        self.url = os.getenv('imageUrl_net')
        self.add_image_job_name = 'APIAddImageMsg'
        self.crt_vm_image_job_name = 'APICreateRootVolumeTemplateFromRootVolumeMsg'
        self.crt_vol_image_job_name = 'APICreateDataVolumeTemplateFromVolumeMsg'
        self.vm_create_image_name = 'test-vm-crt-image'
        self.vol_create_image_name = 'test-vol-crt-image'
        self.image_add_name = 'test-image-longjob'
        self.cond_name = "res_ops.gen_query_conditions('name', '=', 'name_to_replace')"

    def create_vm(self):
        self.vm = create_vm()

    def create_data_volume(self):
        disk_offering = test_lib.lib_get_disk_offering_by_name(os.getenv('rootDiskOfferingName'))
        ps_uuid = self.vm.vm.allVolumes[0].primaryStorageUuid
        volume_option = test_util.VolumeOption()
        volume_option.set_disk_offering_uuid(disk_offering.uuid)
        volume_option.set_name('data-volume-for-crt-image-test')
#         volume_option.set_primary_storage_uuid(ps_uuid)
        self.data_volume = create_volume(volume_option)
        self.set_ceph_mon_env(ps_uuid)
        self.data_volume.attach(self.vm)
        self.data_volume.check()

    def set_ceph_mon_env(self, ps_uuid):
        cond_vol = res_ops.gen_query_conditions('uuid', '=', ps_uuid)
        ps = res_ops.query_resource(res_ops.PRIMARY_STORAGE, cond_vol)[0]
        if ps.type.lower() == 'ceph':
            ps_mon_ip = ps.mons[0].monAddr
            os.environ['cephBackupStorageMonUrls'] = 'root:password@%s' % ps_mon_ip

    def submit_longjob(self, job_data, name, job_type=None):
        if job_type == 'image':
            _job_name = self.add_image_job_name
        elif job_type == 'crt_vm_image':
            _job_name = self.crt_vm_image_job_name
        elif job_type == 'crt_vol_image':
            _job_name = self.crt_vol_image_job_name
        long_job = longjob_ops.submit_longjob(_job_name, job_data, name)
        assert long_job.state == "Running"
        time.sleep(5)
        cond_longjob = res_ops.gen_query_conditions('apiId', '=', long_job.apiId)
        longjob = res_ops.query_resource(res_ops.LONGJOB, cond_longjob)[0]
        assert longjob.state == "Succeeded"
        assert longjob.jobResult == "Succeeded"
        job_data_name = job_data.split('"')[3]
        image_inv = res_ops.query_resource(res_ops.IMAGE, eval(self.cond_name.replace('name_to_replace', job_data_name)))
        assert image_inv
        assert image_inv[0].status == 'Ready'
        if job_type == 'crt_vol_image':
            assert image_inv[0].mediaType == 'DataVolumeTemplate'
        else:
            assert image_inv[0].mediaType == 'RootVolumeTemplate'

    def add_image(self):
        name = "longjob_image"
        bs = res_ops.query_resource(res_ops.BACKUP_STORAGE)
        self.target_bs = bs[random.randint(0, len(bs) - 1)]
        job_data = '{"name":"%s", "url":"%s", "mediaType"="RootVolumeTemplate", "format"="qcow2", "platform"="Linux", \
        "backupStorageUuids"=["%s"]}' % (self.image_add_name, self.url, self.target_bs.uuid)
        self.submit_longjob(job_data, name, job_type='image')

    def delete_image(self):
        cond_image = res_ops.gen_query_conditions('name', '=', 'test-image-longjob')
        longjob_image = res_ops.query_resource(res_ops.IMAGE, cond_image)[0]
        try:
            img_ops.delete_image(longjob_image.uuid, backup_storage_uuid_list=[self.target_bs.uuid])
        except:
            pass

    def crt_vm_image(self):
        name = 'longjob_crt_vol_image'
        job_data = '{"name"="%s", "guestOsType":"Linux","system"="false","platform"="Linux","backupStorageUuids"=["%s"], \
        "rootVolumeUuid"="%s"}' % (self.vm_create_image_name, res_ops.query_resource(res_ops.BACKUP_STORAGE)[-1].uuid, self.vm.vm.rootVolumeUuid)
        self.submit_longjob(job_data, name, job_type='crt_vm_image')

    def crt_vol_image(self):
        name = 'longjob_crt_vol_image'
        job_data = '{"name"="%s", "guestOsType":"Linux","system"="false","platform"="Linux","backupStorageUuids"=["%s"], \
        "volumeUuid"="%s"}' %(self.vol_create_image_name, res_ops.query_resource(res_ops.BACKUP_STORAGE)[0].uuid, self.data_volume.get_volume().uuid)
        self.submit_longjob(job_data, name, job_type='crt_vol_image')


class Billing(object):
	def __init__(self):
		self.resourceName = None
		self.timeUnit = "s"
		self.price = 5
	
	def set_resourceName(self,resourceName):
		self.resourceName = resourceName

	def get_resourceName(self):
		return self.resourceName

	def set_price(self,price):
		self.price = price

	def get_price(self):
		return self.price

	def set_timeUnit(self,timeUnit):
		self.timeUnit = timeUnit

	def get_timeUnit(self):
		return self.timeUnit		

class CpuBilling(Billing):
	def __init__(self):
		super(CpuBilling, self).__init__()
		self.resourceName = "cpu"

	def create_resource_type(self):
		return bill_ops.create_resource_price(self.resourceName,self.timeUnit,self.price)

class MemoryBilling(Billing):
	def __init__(self):
		super(MemoryBilling, self).__init__()
		self.resourceName = "memory"
		self.resourceUnit = "G"
	
	def set_resourceUnit(self,resourceUnit):
		self.resourceUnit = resourceUnit

	def get_resourceUnit(self):
		return self.resourceUnit
	
	def create_resource_type(self):
		return bill_ops.create_resource_price(self.resourceName,self.timeUnit,self.price,self.resourceUnit)

class RootVolumeBilling(Billing):
	def __init__(self):
		super(RootVolumeBilling, self).__init__()
		self.resourceName = "rootVolume"
		self.resourceUnit = "G"
	
        def set_resourceUnit(self,resourceUnit):
                self.resourceUnit = resourceUnit

        def get_resourceUnit(self):
                return self.resourceUnit

	def create_resource_type(self):
		return bill_ops.create_resource_price(self.resourceName,self.timeUnit,self.price,self.resourceUnit)

class DataVolumeBilling(Billing):
        def __init__(self):
                super(RootVolumeBilling, self).__init__()
                self.resourceName = "dataVolume"
                self.resourceUnit = "G"

        def set_resourceUnit(self,resourceUnit):
                self.resourceUnit = resourceUnit

        def get_resourceUnit(self):
                return self.resourceUnit

        def create_resource_type(self):
                return bill_ops.create_resource_price(self.resourceName,self.timeUnit,self.price,self.resourceUnit)

class PublicIpBilling(Billing):
	def __init__(self):
		super(PublicIpBilling, self).__init__()
		self.resourceName = "pubIpVmNicBandwidthIn"
		self.resourceUnit = "M"
		self.uuid = None
	
	def set_resourceUnit(self,resourceUnit):
		self.resourceUnit = resourceUnit

	def get_resourceUnit(self):
		return self.resourceUnit

        def create_resource_type(self):
		evt = bill_ops.create_resource_price(self.resourceName,self.timeUnit,self.price,self.resourceUnit)
		self.uuid = evt.uuid
		return evt

	def delete_resource(self):
		return bill_ops.delete_resource_price(self.uuid)

	def query_resource_price(self):
		cond = []
		if self.uuid:
			cond = res_ops.gen_query_conditions('uuid', "=", self.uuid, cond)
		if self.price:
			cond = res_ops.gen_query_conditions('price', "=", self.price, cond)
		if self.resourceName:
			cond = res_ops.gen_query_conditions('resourceName', "=",self.resourceName, cond)
		if self.timeUnit:
			cond = res_ops.gen_query_conditions('timeUnit', "=",self.timeUnit, cond)
		if self.resourceUnit:
			cond = res_ops.gen_query_conditions('resourceUnit', "=",self.resourceUnit, cond)
		return bill_ops.query_resource_price(cond)
		

'''
to be define
'''
class GPUBilling(Billing):
        def __init__(self):
                super(PublicIpBilling, self).__init__()

def create_vm_billing(name, image_uuid, host_uuid, instance_offering_uuid, l3_uuid, session_uuid=None):
	vm_creation_option = test_util.VmOption()
	vm_creation_option.set_name(name)
	vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
	vm_creation_option.set_image_uuid(image_uuid)
	vm_creation_option.set_l3_uuids([l3_uuid])
	if host_uuid:
		vm_creation_option.set_host_uuid(host_uuid)
	if session_uuid:
		vm_creation_option.set_session_uuid(session_uuid)
	vm = create_vm(vm_creation_option)
	return vm

def compare(user_uuid,status):
	prices = bill_ops.calculate_account_spending(user_uuid)
	time.sleep(1)
	prices1 = bill_ops.calculate_account_spending(user_uuid) 
	if status == "clean":
		if prices1.total != prices.total:
			test_util.test_fail("test billing fail,maybe can not calculate when vm %s" %(status))
	else:
		if prices1.total <= prices.total:
			test_util.test_fail("test billing fail,maybe can not calculate when vm %s" %(status))

def get_resource_from_vmm(resource_type,zone_uuid,host_uuid_from_vmm)
	cond = res_ops.gen_query_conditions('zoneUuid', '=', zone_uuid)
        resource_list = res_ops.query_resource(res_ops.resource_type, cond)
	if resource_type == "LocalStorage":
		return judge_PrimaryStorage(resource_list)
	if resource_type == "HOST":
		return judge_HostResource(resource_list,host_uuid_from_vmm)
	

def judge_PrimaryStorage(PrimaryStorageSource):
	flag = 0
        for childStorge in PrimaryStorageSource:
                test_util.test_logger("type is %s" %(childStorge.type))
                if childStorge.type == "LocalStorage"
                        flag = 1
                        break
	return flag

def judge_HostResource(HostSource,host_uuid):
	for host in hosts:
		test_util.test_logger("host uuid is %s" %(host.uuid))
		if host.uuid != host_uuid:
			return host.uuid
		else:
			return None
	











def generate_collectd_conf(host, collectdPath, list_port, host_disks = None,
                           host_nics = None, vm_disks = None, vm_nics = None):

    hostUuid = ''
    hostInstance = ''
    hostCpu = ''
    hostDisks = []
    hostMem = ''
    hostNics = []

    vmUuid = ''
    vmCpu = ''
    vmDisks = []
    vmMem = ''
    vmNics = []

    collectdFile = ''
    collectdModule = ''

    hostInstance = host.managementIp.replace('.','-')
    hostUuid = host.uuid
    hostCpu = host.cpuNum
    hostMem = int(int(host.totalMemoryCapacity) / 1024 / 1024)
    hostDisks = ' '.join(host_disks)
    hostNics = ' '.join(host_nics)
 
    cond = res_ops.gen_query_conditions('hostUuid', '=', hostUuid)
    vminstances = res_ops.query_resource_fields(res_ops.VM_INSTANCE, cond)
 
    collectdFile = os.path.join(collectdPath, hostInstance + '.conf')
    collectdModule = os.path.join(collectdPath, 'modules')
    test_util.test_logger('generate collectd file %s for %s with cpu %s mem %s'\
                          % (collectdFile, hostInstance, hostCpu, hostMem))
 
    fd = open(collectdFile, 'w+')
    fd.write('Interval 10\nFQDNLookup false\nLoadPlugin python\nLoadPlugin network\n')
    fd.write('<Plugin network>\n')
    fd.write('Server \"localhost\" \"' + str(list_port) + '\"\n')
    fd.write('</Plugin>\n')
    fd.write('<Plugin python>\n')
    fd.write('ModulePath \"' + collectdModule + '\"\n')
    fd.write('LogTraces true\n')
    fd.write('Import \"cpu\"\n')
    fd.write('Import \"disk\"\n')
    fd.write('Import \"interface\"\n')
    fd.write('Import \"memory\"\n')
    fd.write('Import \"virt\"\n')
 
    fd.write('<Module cpu>\n')
    fd.write('Instance \"' + hostInstance + '\"\n')
    fd.write('Cpu_Num \"' + str(hostCpu) + '\"\n')
    fd.write('</Module>\n')
 
    fd.write('<Module disk>\n')
    fd.write('Instance \"' + hostInstance + '\"\n')
    fd.write('Disk_Instances \"' + hostDisks + '\"\n')
    fd.write('</Module>\n')
 
    fd.write('<Module interface>\n')
    fd.write('Instance \"' + hostInstance + '\"\n')
    fd.write('Net_Interfaces \"' + hostNics + '\"\n')
    fd.write('</Module>\n')
 
    fd.write('<Module memory>\n')
    fd.write('Instance \"' + hostInstance + '\"\n')
    fd.write('Memory \"' + str(hostMem) + '\"\n')
    fd.write('</Module>\n')
 
    if vminstances:
        fd.write('<Module virt>\n')
        for j in range(0, len(vminstances)):
            vmUuid = vminstances[j].uuid
            vmCpu = vminstances[j].cpuNum
            vmDisks = ' '.join(vm_disks)
            vmMem = int(int(vminstances[j].memorySize ) / 1025 / 1024)
            vmNics = ' '.join(vm_nics) 
 
            fd.write('VM_Instance' + str(j) + '_Name \"' + vmUuid + '\"\n')
            fd.write('VM_Instance' + str(j) + '_Cpu_Num \"' + str(vmCpu) + '\"\n')
            fd.write('VM_Instance' + str(j) + '_Memory \"' + str(vmMem) + '\"\n')
            fd.write('VM_Instance' + str(j) + '_Disks \"' + vmDisks + '\"\n')
            fd.write('VM_Instance' + str(j) + '_Net_Interfaces \"' + vmNics + '\"\n')
 
        fd.write('</Module>\n')
 
    fd.write('</Plugin>\n')
    fd.close()

    return collectdFile

def collectd_trigger(collectdFile):

    cmd = 'collectd -C ' + collectdFile + ' -f'
    try:
        #shell.call(cmd)
        os.system(cmd)
        test_util.test_logger('successfully trigger collectd for conf %s' % collectdFile)
    except:
        test_util.test_logger('fail to execute command %s' % cmd)
        return False

    return True

def collectdmon_trigger(collectdFile):

    cmd = 'collectdmon -- -C ' + collectdFile
    try:
        #shell.call(cmd)
        os.system(cmd)
        test_util.test_logger('successfully trigger collectdmon for conf %s' % collectdFile)
    except:
        test_util.test_logger('fail to execute command %s' % cmd)
        return False

    return True

def collectd_exporter_trigger(list_port, web_port):
    cmd = ''

    if os.path.exists('/var/lib/zstack/kvm/collectd_exporter'):
        cmd = '/var/lib/zstack/kvm/collectd_exporter -collectd.listen-address :' + str(list_port) + ' -web.listen-address :' + str(web_port)
        try:
            os.system(cmd)
            #shell.call(cmd)
            test_util.test_logger('successfully trigger collectd_exporter with listen port %s and web port %s' % (list_port, web_port))
        except:
            test_util.test_logger('fail to execute command %s' % cmd)
            return False
    else:
        test_util.test_logger('no collectd_exporter found under /var/lib/zstack/kvm/')
        return False

    return True

def prometheus_conf_generate(host, web_port, address = None):
    hostInstance = ''
    hostUuid = ''
    dict_prometheus = {}

    prometheus_dir = '/usr/local/zstacktest/prometheus/discovery/hosts/'

    if address:
        ip_addr = address
    else:
        ip_addr = '127.0.0.1'

    hostInstance = host.managementIp.replace('.','-')
    hostUuid = host.uuid

    dict_prometheus['labels'] = {'hostUuid':hostUuid}
    dict_prometheus['targets'] = [str(ip_addr) + ':9100', str(ip_addr) + ':' + str(web_port), str(ip_addr) + ':7069']

    file_path = os.path.join(prometheus_dir, hostUuid + '-' + hostInstance + '.json')

    with open(file_path, 'w+') as fd:
        fd.write('[' + json.dumps(dict_prometheus) + ']')

    test_util.test_logger('successfully deploy host %s with port %s for prometheus' % (hostInstance, web_port))

    return True
