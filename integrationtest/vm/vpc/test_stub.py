'''

Create an unified test_stub to share test operations

@author: fang.sun
'''

import zstackwoodpecker.operations.vpc_operations as vpc_ops
import zstackwoodpecker.operations.net_operations as net_ops
import os
import random
import zstackwoodpecker.test_util  as test_util
import zstackwoodpecker.zstack_test.zstack_test_volume as zstack_volume_header
import zstackwoodpecker.zstack_test.zstack_test_eip as zstack_eip_header
import zstackwoodpecker.zstack_test.zstack_test_vip as zstack_vip_header
import zstackwoodpecker.zstack_test.zstack_test_security_group as zstack_sg_header
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.scenario_operations as sce_ops
import zstackwoodpecker.header.host as host_header
import apibinding.inventory as inventory
import zstackwoodpecker.operations.primarystorage_operations as ps_ops
import zstackwoodpecker.operations.ha_operations as ha_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstacklib.utils.xmlobject as xmlobject
import threading
import time
import sys
import telnetlib
import random
from contextlib import contextmanager
from functools import wraps
import itertools
#import traceback

l3_vlan_system_name_list=['l3VlanNetworkName1', "l3VlanNetwork3"]
l3_vxlan_system_name_list= ["l3VxlanNetwork11", "l3VxlanNetwork12"]

Port = test_state.Port

rule1_ports = Port.get_ports(Port.rule1_ports)
rule2_ports = Port.get_ports(Port.rule2_ports)
rule3_ports = Port.get_ports(Port.rule3_ports)
rule4_ports = Port.get_ports(Port.rule4_ports)
rule5_ports = Port.get_ports(Port.rule5_ports)
denied_ports = Port.get_denied_ports()
target_ports = rule1_ports + rule2_ports + rule3_ports + rule4_ports + rule5_ports + denied_ports


def create_vpc_vrouter():
    vr_name= 'test_vpc'
    conf = res_ops.gen_query_conditions('name', '=', 'test_vpc')
    vr_list = res_ops.query_resource(res_ops.VIRTUALROUTER_VM, conf)
    if vr_list:
        return vr_list[0]
    vr_offering = res_ops.get_resource(res_ops.VR_OFFERING)[0]
    return vpc_ops.create_vpc_vrouter(name=vr_name, virtualrouter_offering_uuid=vr_offering.uuid)


def attach_all_l3_to_vpc_vr(vpc_vr):
    l3_vlan_name_list = [os.environ.get(name) for name in l3_vlan_system_name_list]
    l3_vxlan_name_list = [os.environ.get(name) for name in l3_vxlan_system_name_list]

    l3_list = [test_lib.lib_get_l3_by_name(name) for name in l3_vlan_name_list + l3_vxlan_name_list]

    l3_uuid_list = [nic.l3NetworkUuid for nic in vpc_vr.vmNics]
    for l3 in l3_list:
        if l3.uuid not in l3_uuid_list:
            net_ops.attach_l3(l3.uuid, vpc_vr.uuid)
            time.sleep(5)


def create_vm_with_random_offering(vm_name, image_name=None, l3_name=None, session_uuid=None,
                                   instance_offering_uuid=None, host_uuid=None, disk_offering_uuids=None,
                                   root_password=None, ps_uuid=None, system_tags=None):
    if image_name:
        imagename = os.environ.get(image_name)
        image_uuid = test_lib.lib_get_image_by_name(imagename).uuid
    else:
        conf = res_ops.gen_query_conditions('format', '!=', 'iso')
        conf = res_ops.gen_query_conditions('system', '=', 'false', conf)
        image_uuid = random.choice(res_ops.query_resource(res_ops.IMAGE, conf)).uuid

    if l3_name:
        l3name = os.environ.get(l3_name)
        l3_net_uuid = test_lib.lib_get_l3_by_name(l3name).uuid
    else:
        l3_net_uuid = random.choice(res_ops.get_resource(res_ops.L3_NETWORK)).uuid

    if not instance_offering_uuid:
        conf = res_ops.gen_query_conditions('type', '=', 'UserVM')
        instance_offering_uuid = random.choice(res_ops.query_resource(res_ops.INSTANCE_OFFERING, conf)).uuid

    vm_creation_option = test_util.VmOption()
    vm_creation_option.set_l3_uuids([l3_net_uuid])
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_name(vm_name)
    if system_tags:
        vm_creation_option.set_system_tags(system_tags)
    if disk_offering_uuids:
        vm_creation_option.set_data_disk_uuids(disk_offering_uuids)
    if root_password:
        vm_creation_option.set_root_password(root_password)
    if host_uuid:
        vm_creation_option.set_host_uuid(host_uuid)
    if session_uuid:
        vm_creation_option.set_session_uuid(session_uuid)
    if ps_uuid:
        vm_creation_option.set_ps_uuid(ps_uuid)

    vm = test_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    return vm
