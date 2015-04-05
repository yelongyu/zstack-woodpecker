'''

Create an unified test_stub to share test operations

@author: Youyk
'''
import os
import random
import zstackwoodpecker.test_util  as test_util
import zstackwoodpecker.zstack_test.zstack_test_volume as zstack_volume_header
import zstackwoodpecker.zstack_test.zstack_test_security_group as zstack_sg_header
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import zstackwoodpecker.header.host as host_header
#import traceback
#import sys

import zstackwoodpecker.test_state as test_state
Port = test_state.Port

rule1_ports = Port.get_ports(Port.rule1_ports)
rule2_ports = Port.get_ports(Port.rule2_ports)
rule3_ports = Port.get_ports(Port.rule3_ports)
rule4_ports = Port.get_ports(Port.rule4_ports)
rule5_ports = Port.get_ports(Port.rule5_ports)
denied_ports = Port.get_denied_ports()
#rule1_ports = [1, 22, 100]
#rule2_ports = [9000, 9499, 10000]
#rule3_ports = [60000, 60010, 65535]
#rule4_ports = [5000, 5501, 6000]
#rule5_ports = [20000, 28999, 30000]
#test_stub.denied_ports = [101, 4999, 8990, 15000, 30001, 49999]
target_ports = rule1_ports + rule2_ports + rule3_ports + rule4_ports + rule5_ports + denied_ports

def create_volume(volume_creation_option=None):
    if not volume_creation_option:
        disk_offering = test_lib.lib_get_disk_offering_by_name(os.environ.get('smallDiskOfferingName'))
        volume_creation_option = test_util.VolumeOption()
        volume_creation_option.set_disk_offering_uuid(disk_offering.uuid)
        volume_creation_option.set_name('vr_test_volume')

    volume = zstack_volume_header.ZstackTestVolume()
    volume.set_creation_option(volume_creation_option)
    volume.create()
    return volume

def create_vr_vm(vm_name, image_name, l3_name):
    vm_creation_option = test_util.VmOption()
    imagename = os.environ.get(image_name)
    image_uuid = test_lib.lib_get_image_by_name(imagename).uuid
    #l3_name = os.environ.get('l3NoVlanNetworkName1')
    l3name = os.environ.get(l3_name)

    l3_net_uuid = test_lib.lib_get_l3_by_name(l3name).uuid
    conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
    instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid
    vm_creation_option.set_l3_uuids([l3_net_uuid])
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_name(vm_name)
    vm = test_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    return vm

def migrate_vm_to_random_host(vm):
    test_util.test_dsc("migrate pf_vm to random host")
    target_host = test_lib.lib_find_random_host(vm.vm)
    vm.migrate(target_host.uuid)

    new_host = test_lib.lib_get_vm_host(vm.vm)
    if not new_host:
        test_util.test_fail('Not find available Hosts to do migration')

    if new_host.uuid != target_host.uuid:
        test_util.test_fail('[vm:] did not migrate from [host:] %s to target [host:] %s, but to [host:] %s' % (vm.vm.uuid, current_host.uuid, target_host.uuid, new_host.uuid))
    else:
        test_util.test_logger('[vm:] %s has been migrated from [host:] %s to [host:] %s' % (vm.vm.uuid, current_host.uuid, target_host.uuid))


def create_sg(sg_creation_option=None):
    if not sg_creation_option:
        sg_creation_option = test_util.SecurityGroupOption()
        sg_creation_option.set_name('test_sg')
        sg_creation_option.set_description('test sg description')

    sg = zstack_sg_header.ZstackTestSecurityGroup()
    sg.set_creation_option(sg_creation_option)
    sg.create()
    return sg
