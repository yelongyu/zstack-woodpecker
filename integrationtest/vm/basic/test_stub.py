'''

Create an unified test_stub to share test operations

@author: Youyk
'''

import os

import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm
import zstackwoodpecker.zstack_test.zstack_test_volume as test_volume
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.account_operations as acc_ops


def create_vm(vm_creation_option=None, volume_uuids=None, root_disk_uuid=None, \
        image_uuid=None, session_uuid=None):
    if not vm_creation_option:
        instance_offering_uuid = res_ops.get_resource(res_ops.INSTANCE_OFFERING, session_uuid)[0].uuid
        cond = res_ops.gen_query_conditions('mediaType', '!=', 'ISO')
        image_uuid = res_ops.query_resource(res_ops.IMAGE, cond, session_uuid)[0].uuid
        l3net_uuid = res_ops.get_resource(res_ops.L3_NETWORK, session_uuid)[0].uuid
        vm_creation_option = test_util.VmOption()
        vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
        vm_creation_option.set_image_uuid(image_uuid)
        vm_creation_option.set_l3_uuids([l3net_uuid])

    if volume_uuids:
        if isinstance(volume_uuids, list):
            vm_creation_option.set_data_disk_uuids(volume_uuids)
        else:
            test_util.test_fail('volume_uuids type: %s is not "list".' % type(volume_uuids))

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

def create_volume(volume_creation_option = None, session_uuid = None):
    if not volume_creation_option:
        disk_offering = test_lib.lib_get_disk_offering_by_name(os.environ.get('smallDiskOfferingName'))
        volume_creation_option = test_util.VolumeOption()
        volume_creation_option.set_disk_offering_uuid(disk_offering.uuid)
        volume_creation_option.set_name('test_volume')

    if session_uuid:
        volume_creation_option.set_session_uuid(session_uuid)

    volume = test_volume.ZstackTestVolume()
    volume.set_creation_option(volume_creation_option)
    volume.create()
    return volume

def create_vm_with_volume(vm_creation_option = None, data_volume_uuids = None, \
        session_uuid = None):
    if not data_volume_uuids:
        disk_offering = test_lib.lib_get_disk_offering_by_name(os.environ.get('smallDiskOfferingName'), session_uuid)
        data_volume_uuids = [disk_offering.uuid]
    return create_vm(vm_creation_option, data_volume_uuids, \
            session_uuid = session_uuid)

def create_vm_with_iso(vm_creation_option = None, session_uuid = None):
    img_option = test_util.ImageOption()
    img_option.set_name('iso')
    root_disk_uuid = test_lib.lib_get_disk_offering_by_name(os.environ.get('rootDiskOfferingName')).uuid
    bs_uuid = res_ops.query_resource_fields(res_ops.BACKUP_STORAGE, [], \
            session_uuid)[0].uuid
    img_option.set_backup_storage_uuid_list([bs_uuid])
    os.system("echo fake iso for test only >  %s/apache-tomcat/webapps/zstack/static/test.iso" % (os.environ.get('zstackInstallPath')))
    img_option.set_url('http://%s:8080/zstack/static/test.iso' % (os.environ.get('node1Ip')))
    image_uuid = img_ops.add_iso_template(img_option).uuid

    return create_vm(vm_creation_option, None, root_disk_uuid, image_uuid, \
            session_uuid = session_uuid)

def create_vm_with_previous_iso(vm_creation_option = None, session_uuid = None):
    cond = res_ops.gen_query_conditions('name', '=', 'iso')
    image_uuid = res_ops.query_resource(res_ops.IMAGE, cond)[0].uuid
    root_disk_uuid = test_lib.lib_get_disk_offering_by_name(os.environ.get('rootDiskOfferingName')).uuid
    return create_vm(vm_creation_option, None, root_disk_uuid, image_uuid, \
            session_uuid = session_uuid)

def share_admin_resource(account_uuid_list):
    instance_offering_uuid = res_ops.get_resource(res_ops.INSTANCE_OFFERING)[0].uuid
    cond = res_ops.gen_query_conditions('mediaType', '!=', 'ISO')
    image_uuid = res_ops.query_resource(res_ops.IMAGE, cond)[0].uuid
    l3net_uuid = res_ops.get_resource(res_ops.L3_NETWORK)[0].uuid
    root_disk_uuid = test_lib.lib_get_disk_offering_by_name(os.environ.get('rootDiskOfferingName')).uuid
    data_disk_uuid = test_lib.lib_get_disk_offering_by_name(os.environ.get('smallDiskOfferingName')).uuid
    acc_ops.share_resources(account_uuid_list, [instance_offering_uuid, image_uuid, l3net_uuid, root_disk_uuid, data_disk_uuid])

