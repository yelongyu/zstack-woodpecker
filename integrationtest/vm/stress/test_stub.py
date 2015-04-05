'''

Create an unified test_stub for stress test.

@author: Youyk
'''

import zstackwoodpecker.operations.resource_operations as res_ops
import os
import time
import random

import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.zstack_test.zstack_test_vm as zstack_vm_header
import zstackwoodpecker.zstack_test.zstack_test_volume as zstack_volume_header
import zstackwoodpecker.zstack_test.zstack_test_security_group as zstack_sg_header
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

def create_random_vm():
    instance_offering_uuid = random.choice(res_ops.get_resource(res_ops.INSTANCE_OFFERING, session_uuid=None)).uuid
    image_uuid = random.choice(res_ops.get_resource(res_ops.IMAGE, session_uuid=None)).uuid
    l3net_uuid = random.choice(res_ops.get_resource(res_ops.L3_NETWORK, session_uuid=None)).uuid
    vm_creation_option = test_util.VmOption()
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_l3_uuids([l3net_uuid])

    vm = test_vm.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    return vm

def create_vlan_vm(l3_name=None, disk_offering_uuids=None):
    image_name = os.environ.get('imageName_f')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    if not l3_name:
        l3_name = os.environ.get('l3VlanNetworkName_1')

    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid

    return create_vm([l3_net_uuid], image_uuid, 'vlan_vm', disk_offering_uuids)

def create_sg_vm(l3_name=None, disk_offering_uuids=None):
    '''
        SG test need more network commands in guest. So it needs VR image.
    '''
    image_name = os.environ.get('virtualRouterImageName')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    if not l3_name:
        #l3_name = 'guestL3VlanNetwork1'
        l3_name = os.environ.get('l3VlanNetworkName_1')

    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    return create_vm([l3_net_uuid], image_uuid, 'vlan_vm', disk_offering_uuids)

def create_basic_vm(disk_offering_uuids=None):
    image_name = os.environ.get('imageName_f')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    l3_name = os.environ.get('l3PubNetworkName')
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    return create_vm([l3_net_uuid], image_uuid, 'basic_no_vlan_vm', disk_offering_uuids)

def create_vlan_sg_vm(disk_offering_uuids=None):
    image_name = os.environ.get('virtualRouterImageName')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    l3_name = os.environ.get('l3VlanNetworkName_1')
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    return create_vm([l3_net_uuid], image_uuid, 'vlan_sg_vm', disk_offering_uuids)

# parameter: vmname; l3_net: l3_net_description, or [l3_net_uuid,]; image_uuid:
def create_vm(l3_uuid_list, image_uuid, vm_name=None, disk_offering_uuids=None):
    vm_creation_option = test_util.VmOption()
    conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
    instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_l3_uuids(l3_uuid_list)
    vm_creation_option.set_image_uuid(image_uuid)
    if vm_name:
        vm_name = vm_name + str(time.time())

    vm_creation_option.set_name(vm_name)
    vm_creation_option.set_data_disk_uuids(disk_offering_uuids)
    vm = zstack_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    return vm

def create_volume(volume_creation_option=None):
    if not volume_creation_option:
        disk_offering = test_lib.lib_get_disk_offering_by_name(os.environ.get('diskOfferingName-s'))
        volume_creation_option = test_util.VolumeOption()
        volume_creation_option.set_disk_offering_uuid(disk_offering.uuid)
        volume_creation_option.set_name('vr_test_volume')

    volume = zstack_volume_header.ZstackTestVolume()
    volume.set_creation_option(volume_creation_option)
    volume.create()
    return volume

def create_sg(sg_creation_option=None):
    if not sg_creation_option:
        sg_creation_option = test_util.SecurityGroupOption()
        sg_creation_option.set_name('test_sg')
        sg_creation_option.set_description('test sg description')

    sg = zstack_sg_header.ZstackTestSecurityGroup()
    sg.set_creation_option(sg_creation_option)
    sg.create()
    return sg

def create_vlan_vm_with_volume(l3_name=None, disk_offering_uuids=None, disk_number=None):
    if not disk_offering_uuids:
        disk_offering = test_lib.lib_get_disk_offering_by_name(os.environ.get('diskOfferingName-s'))
        disk_offering_uuids = [disk_offering.uuid]
        #current ZStack doesn't support create several same volume when creating VM by providing several same uuids.
        if disk_number:
            for i in range(disk_number - 1):
                disk_offering_uuids.append(disk_offering.uuid)

    return create_vlan_vm(l3_name, disk_offering_uuids)

