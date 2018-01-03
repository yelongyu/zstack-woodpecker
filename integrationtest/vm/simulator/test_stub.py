'''

Create an unified test_stub to share test operations

@author: Youyk
'''

import os

import apibinding.api_actions as api_actions
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm
import zstackwoodpecker.zstack_test.zstack_test_volume as test_volume
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.zstack_test.zstack_test_volume as zstack_volume_header
import re

def create_vm(vm_creation_option=None, volume_uuids=None, root_disk_uuid=None,
              image_uuid=None, session_uuid=None):
    if not vm_creation_option:
        instance_offering_uuid = test_lib.lib_get_instance_offering_by_name(
            os.environ.get('instanceOfferingName_s')).uuid
        cond = res_ops.gen_query_conditions('mediaType', '!=', 'ISO')
        cond = res_ops.gen_query_conditions('platform', '=', 'Linux', cond)
        l3net_uuid = test_lib.lib_get_l3_by_name(
            os.environ.get('l3VlanNetwork3')).uuid
        image_uuid = res_ops.query_resource(
            res_ops.IMAGE, cond, session_uuid)[0].uuid
        vm_creation_option = test_util.VmOption()
        vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
        vm_creation_option.set_image_uuid(image_uuid)
        vm_creation_option.set_l3_uuids([l3net_uuid])

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

def create_windows_vm(vm_creation_option=None, volume_uuids=None, root_disk_uuid=None, image_uuid=None, session_uuid=None):
    if not vm_creation_option:
        instance_offering_uuid = test_lib.lib_get_instance_offering_by_name(
            os.environ.get('instanceOfferingName_win')).uuid
        cond = res_ops.gen_query_conditions('mediaType', '!=', 'ISO')
        cond = res_ops.gen_query_conditions('platform', '=', 'Windows', cond)
        image_uuid = res_ops.query_resource(
            res_ops.IMAGE, cond, session_uuid)[0].uuid
        l3net_uuid = test_lib.lib_get_l3_by_name(
            os.environ.get('l3VlanNetwork3')).uuid
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
    os.system("echo fake iso for test only >  %s/apache-tomcat/webapps/zstack/static/test.iso" %
              (os.environ.get('zstackInstallPath')))
    img_option.set_url('http://%s:8080/zstack/static/test.iso' %
                       (os.environ.get('node1Ip')))
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

