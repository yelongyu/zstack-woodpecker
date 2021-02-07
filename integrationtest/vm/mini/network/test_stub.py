'''
Create an unified test_stub to share test operations

@author: chen.zhou
'''

import zstackwoodpecker.operations.net_operations as net_ops
import os
import random
import zstackwoodpecker.test_util  as test_util
import zstackwoodpecker.zstack_test.zstack_test_volume as zstack_volume_header
import zstackwoodpecker.zstack_test.zstack_test_eip as zstack_eip_header
import zstackwoodpecker.zstack_test.zstack_test_vip as zstack_vip_header
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
import zstackwoodpecker.header.vm as vm_header
import zstacklib.utils.xmlobject as xmlobject
import threading
import time
import sys
import telnetlib
import random
from contextlib import contextmanager
from functools import wraps
import itertools

def create_vm(vm_name, l3_uuids, host_uuid = None, disk_offering_uuids=None):
    vm_creation_option = test_util.VmOption()
    cluster_uuid = res_ops.query_resource(res_ops.CLUSTER)[0].uuid
    cond = res_ops.gen_query_conditions('format', '!=', 'iso')
    image_uuid = res_ops.query_resource(res_ops.IMAGE, cond)[0].uuid

    conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
    instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid
    vm_creation_option.set_cluster_uuid(cluster_uuid)
    vm_creation_option.set_l3_uuids(l3_uuids)
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_name(vm_name)
    vm_creation_option.set_timeout(600000)
    if host_uuid:
        vm_creation_option.set_host_uuid(host_uuid)
    if disk_offering_uuids:
        vm_creation_option.set_data_disk_uuids(disk_offering_uuids)
    vm = test_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    return vm

def create_vip(vip_name=None, l3_uuid=None, session_uuid = None, required_ip=None):
    if not vip_name:
        vip_name = 'test vip'
    if not l3_uuid:
        l3_name = os.environ.get('public network')
        l3_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid

    ip_status = net_ops.get_ip_capacity_by_l3s([l3_uuid])
    if not ip_status.availableCapacity:
        test_util.test_fail('no available pub ip left')

    vip_creation_option = test_util.VipOption()
    vip_creation_option.set_name(vip_name)
    vip_creation_option.set_l3_uuid(l3_uuid)
    vip_creation_option.set_session_uuid(session_uuid)
    vip_creation_option.set_requiredIp(required_ip)

    vip = zstack_vip_header.ZstackTestVip()
    vip.set_creation_option(vip_creation_option)
    vip.create()
    return vip

def create_eip(eip_name=None, vip_uuid=None, vnic_uuid=None, vm_obj=None, session_uuid = None):
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

def run_command_in_vm(vm_inv, command):
    managerip = test_lib.lib_find_host_by_vm(vm_inv).managementIp
    vm_ip = vm_inv.vmNics[0].ip
    return test_lib.lib_ssh_vm_cmd_by_agent(managerip, vm_ip, 'root', 'password', command)