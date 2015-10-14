'''

Create an unified test_stub to share test operations

@author: Youyk
'''

import os

import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.zstack_test.zstack_test_vm as zstack_vm_header
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.vm_operations as vm_ops

def create_vm(vm_name='virt-vm', \
        image_name = os.environ.get('imageName_s'), \
        l3_name = os.environ.get('l3PublicNetworkName'), \
        instance_offering_uuid = None, \
        host_uuid = None,
        disk_offering_uuids=None, system_tags=None, session_uuid = None, ):

    vm_creation_option = test_util.VmOption()
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
    if not instance_offering_uuid:
        instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid

    vm_creation_option.set_l3_uuids([l3_net_uuid])
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_name(vm_name)
    if not host_uuid:
        vm_creation_option.set_host(host_uuid)
    vm = zstack_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    return vm 

def create_instance_offering(cpuNum = 1, cpuSpeed = 10, \
        memorySize = 512000000, name = 'new_instance', \
        volume_iops = None, volume_bandwidth = None, \
        net_bandwidth = None):
    new_offering_option = test_util.InstanceOfferingOption()
    new_offering_option.set_cpuNum(cpuNum)
    new_offering_option.set_cpuSpeed(cpuSpeed)
    new_offering_option.set_memorySize(memorySize)
    new_offering_option.set_name(name)
    new_offering = vm_ops.create_instance_offering(new_offering_option)
    if volume_iops:
        test_lib.lib_limit_volume_total_iops(volume_iops)
    if volume_bandwidth:
        test_lib.lib_limit_volume_bandwidth(volume_bandwidth)
    if net_bandwidth:
        test_lib.lib_limit_network_bandwidth(net_bandwidth)
    return new_offering

