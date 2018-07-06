'''

Create an unified test_stub to share test operations

@author: Quarkonics
'''
import os
import random
import zstackwoodpecker.test_util  as test_util
import zstackwoodpecker.zstack_test.zstack_test_volume as zstack_volume_header
import zstackwoodpecker.zstack_test.zstack_test_security_group as zstack_sg_header
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.zstack_test.zstack_test_image as test_image
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.operations.datamigrate_operations as datamigr_ops
import zstackwoodpecker.operations.longjob_operations as longjob_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.operations.nas_operations as nas_ops
import zstackwoodpecker.operations.hybrid_operations as hyb_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import zstackwoodpecker.header.host as host_header
import threading
import time
import sys
#import traceback

hybrid_test_stub = test_lib.lib_get_test_stub('hybrid')


def create_x86_vm(vm_creation_option=None, volume_uuids=None, root_disk_uuid=None,
              image_uuid=None, session_uuid=None):
    if not vm_creation_option:
        instance_offering_uuid = test_lib.lib_get_instance_offering_by_name(
            os.environ.get('instanceOfferingName_s')).uuid
        image_name = os.environ.get('imageName_s')
        image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
        l3_name = os.environ.get('l3VlanNetworkName1')
        l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
        conditions = res_ops.gen_query_conditions('name', '=', 'x86_cluster')
        cluster_uuid = res_ops.query_resource(res_ops.CLUSTER, conditions)[0].uuid
        vm_creation_option = test_util.VmOption()
        vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
        vm_creation_option.set_image_uuid(image_uuid)
        vm_creation_option.set_l3_uuids([l3_net_uuid])
        vm_creation_option.set_cluster_uuid(cluster_uuid)
        vm_creation_option.set_name("x86_test_vm")
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

    vm = test_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    return vm

def create_arm_vm(vm_creation_option=None, volume_uuids=None, root_disk_uuid=None,
              image_uuid=None, session_uuid=None):
    if not vm_creation_option:
        instance_offering_uuid = test_lib.lib_get_instance_offering_by_name(
            os.environ.get('instanceOfferingName_s')).uuid
        image_name = os.environ.get('imageName_s')
        image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
        l3_name = os.environ.get('l3VlanNetworkName1')
        l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
        conditions = res_ops.gen_query_conditions('name', '=', 'arm_cluster')
        cluster_uuid = res_ops.query_resource(res_ops.CLUSTER, conditions)[0].uuid
        vm_creation_option = test_util.VmOption()
        vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
        vm_creation_option.set_image_uuid(image_uuid)
        vm_creation_option.set_l3_uuids([l3_net_uuid])
        vm_creation_option.set_cluster_uuid(cluster_uuid)
        vm_creation_option.set_name("arm_test_vm")
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

    vm = test_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    return vm


def create_volume(volume_creation_option=None, session_uuid = None):
    if not volume_creation_option:
        disk_offering = test_lib.lib_get_disk_offering_by_name(os.getenv('smallDiskOfferingName'))
        host_uuid = res_ops.get_resource(res_ops.HOST)[0].uuid
        cond = res_ops.gen_query_conditions('type','=','LocalStorage')
        ps_uuid = res_ops.query_resource(res_ops.PRIMARY_STORAGE,cond)[0].uuid
        system_tags = ["localStorage::hostUuid::%s"%host_uuid]
        volume_creation_option = test_util.VolumeOption()
        volume_creation_option.set_disk_offering_uuid(disk_offering.uuid)
        volume_creation_option.set_name('test_volume')
        volume_creation_option.set_primary_storage_uuid(ps_uuid)
        volume_creation_option.set_system_tags(system_tags)

    volume_creation_option.set_session_uuid(session_uuid)
    volume = zstack_volume_header.ZstackTestVolume()
    volume.set_creation_option(volume_creation_option)
    volume.create()
    return volume

def migrate_vm_to_random_host(vm):
    test_util.test_dsc("migrate vm to random host")
    if not test_lib.lib_check_vm_live_migration_cap(vm.vm):
        test_util.test_skip('skip migrate if live migrate not supported')
    target_host = test_lib.lib_find_random_host(vm.vm)
    current_host = test_lib.lib_find_host_by_vm(vm.vm)
    vm.migrate(target_host.uuid)

    new_host = test_lib.lib_get_vm_host(vm.vm)
    if not new_host:
        test_util.test_fail('Not find available Hosts to do migration')

    if new_host.uuid != target_host.uuid:
        test_util.test_fail('[vm:] %s did not migrate from [host:] %s to target [host:] %s, but to [host:] %s' % (vm.vm.uuid, current_host.uuid, target_host.uuid, new_host.uuid))
    else:
        test_util.test_logger('[vm:] %s has been migrated from [host:] %s to [host:] %s' % (vm.vm.uuid, current_host.uuid, target_host.uuid))

