'''

Create an unified test_stub to share test operations

@author: fang.sun
'''

import zstackwoodpecker.operations.vpc_operations as vpc_ops
import zstackwoodpecker.operations.vpcdns_operations as vpcdns_ops
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
import zstackwoodpecker.operations.autoscaling_operations as autoscaling
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
#import traceback

l3_vlan_system_name_list=['l3VlanNetworkName1', "l3VlanNetwork2"]
#l3_vxlan_system_name_list= ["l3VxlanNetwork11", "l3VxlanNetwork12"]
L3_SYSTEM_NAME_LIST = tuple(l3_vlan_system_name_list)

vpc1_l3_list = ['l3VlanNetworkName1', "l3VlanNetwork2", "l3VxlanNetwork11", "l3VxlanNetwork12"]
vpc2_l3_list = ['l3VlanNetwork3', "l3VlanNetwork4", "l3VxlanNetwork13", "l3VxlanNetwork14"]
vpc3_l3_list = ['l3VlanNetwork5', "l3VlanNetwork6", "l3VxlanNetwork15", "l3VxlanNetwork16"]

all_vpc_l3_list = ['l3VlanNetworkName1'] + ["l3VlanNetwork{}".format(i) for i in xrange(2,10)] + \
                  ["l3VxlanNetwork{}".format(i) for i in xrange(11,20)] + ['l3NoVlanNetworkName1']


Port = test_state.Port

rule1_ports = Port.get_ports(Port.rule1_ports)
rule2_ports = Port.get_ports(Port.rule2_ports)
rule3_ports = Port.get_ports(Port.rule3_ports)
rule4_ports = Port.get_ports(Port.rule4_ports)
rule5_ports = Port.get_ports(Port.rule5_ports)
denied_ports = Port.get_denied_ports()
target_ports = rule1_ports + rule2_ports + rule3_ports + rule4_ports + rule5_ports + denied_ports

def create_vr_vm(vm_name, image_name, l3_name):
    imagename = os.environ.get(image_name)
    l3name = os.environ.get(l3_name)
    vm = create_vm(vm_name, imagename, l3name)
    return vm

def create_vm(vm_name, image_name, l3_name, host_uuid = None, disk_offering_uuids=None):
    vm_creation_option = test_util.VmOption()
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
    instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid
    vm_creation_option.set_l3_uuids([l3_net_uuid])
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

def create_vpc_vrouter(vr_name='test_vpc'):
    conf = res_ops.gen_query_conditions('name', '=', 'test_vpc')
    vr_list = res_ops.query_resource(res_ops.APPLIANCE_VM, conf)
    if vr_list:
        return ZstackTestVR(vr_list[0])
    vr_offering = res_ops.get_resource(res_ops.VR_OFFERING)[0]
    vr_inv =  vpc_ops.create_vpc_vrouter(name=vr_name, virtualrouter_offering_uuid=vr_offering.uuid)
    dns_server = os.getenv('DNSServer')
    vpcdns_ops.add_dns_to_vpc_router(vr_inv.uuid, dns_server)
    return ZstackTestVR(vr_inv)


def attach_l3_to_vpc_vr(vpc_vr, l3_system_name_list=L3_SYSTEM_NAME_LIST):
    l3_name_list = [os.environ.get(name) for name in l3_system_name_list]
    l3_list = [test_lib.lib_get_l3_by_name(name) for name in l3_name_list]
    for l3 in l3_list:
        vpc_vr.add_nic(l3.uuid)



def create_vm_with_random_offering(vm_name, image_name=None, l3_name=None, session_uuid=None,
                                   instance_offering_uuid=None, host_uuid=None, disk_offering_uuids=None,
                                   root_password=None, ps_uuid=None, system_tags=None):
    if image_name:
        imagename = os.environ.get(image_name)
    else:
        imagename = os.environ.get("imageName_net")

    image_uuid = test_lib.lib_get_image_by_name(imagename).uuid

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
        test_util.test_fail('[vm:] did not migrate from [host:] %s to target [host:] %s, but to [host:] %s' % (vm.vm.uuid, current_host.uuid, target_host.uuid, new_host.uuid))
    else:
        test_util.test_logger('[vm:] %s has been migrated from [host:] %s to [host:] %s' % (vm.vm.uuid, current_host.uuid, target_host.uuid))


def run_command_in_vm(vm_inv, command):
    managerip = test_lib.lib_find_host_by_vm(vm_inv).managementIp
    vm_ip = vm_inv.vmNics[0].ip
    return test_lib.lib_ssh_vm_cmd_by_agent(managerip, vm_ip, 'root', 'password', command)


def remove_all_vpc_vrouter():
    
    cond = res_ops.gen_query_conditions('applianceVmType', '=', 'vpcvrouter')
    vr_vm_list = res_ops.query_resource(res_ops.APPLIANCE_VM, cond)
    if vr_vm_list:
        for vr_vm in vr_vm_list:
            nic_uuid_list = [nic.uuid for nic in vr_vm.vmNics if nic.metaData == '4']
            for nic_uuid in nic_uuid_list:
                net_ops.detach_l3(nic_uuid)
            vm_ops.destroy_vm(vr_vm.uuid)



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


def create_multi_volumes(count=10, host_uuid=None, ps=None):
    volume_list = []
    for i in xrange(count):
        disk_offering = random.choice(res_ops.get_resource(res_ops.DISK_OFFERING))
        volume_creation_option = test_util.VolumeOption()
        volume_creation_option.set_disk_offering_uuid(disk_offering.uuid)
        if ps:
            volume_creation_option.set_primary_storage_uuid(ps.uuid)
            if ps.type == inventory.LOCAL_STORAGE_TYPE:
                if not host_uuid:
                    host_uuid = random.choice(res_ops.get_resource(res_ops.HOST)).uuid
            volume_creation_option.set_system_tags(['localStorage::hostUuid::{}'.format(host_uuid)])
        volume = create_volume(volume_creation_option)
        volume_list.append(volume)
    for volume in volume_list:
        volume.check()
    if ps:
        for volume in volume_list:
            assert volume.get_volume().primaryStorageUuid == ps.uuid
    return volume_list

def create_sg(sg_creation_option=None, session_uuid = None):
    if not sg_creation_option:
        sg_creation_option = test_util.SecurityGroupOption()
        sg_creation_option.set_name('test_sg')
        sg_creation_option.set_description('test sg description')

    sg_creation_option.set_session_uuid(session_uuid)
    sg = zstack_sg_header.ZstackTestSecurityGroup()
    sg.set_creation_option(sg_creation_option)
    sg.create()
    return sg


def check_icmp_between_vms(vm1, vm2, expected_result='PASS'):
    vm1_inv, vm2_inv = [vm.get_vm() for vm in (vm1, vm2)]
    if expected_result is 'PASS':
        test_lib.lib_check_ping(vm1_inv, vm2_inv.vmNics[0].ip)
        test_lib.lib_check_ping(vm2_inv, vm1_inv.vmNics[0].ip)
    elif expected_result is 'FAIL':
        with test_lib.expected_failure("ping from vm1 to vm2", Exception):
            test_lib.lib_check_ping(vm1_inv, vm2_inv.vmNics[0].ip)
        with test_lib.expected_failure('ping from vm2 to vm1', Exception):
            test_lib.lib_check_ping(vm2_inv, vm1_inv.vmNics[0].ip)
    else:
        test_util.test_fail('The expected result should either PASS or FAIL')


def check_tcp_between_vms(vm1, vm2, allowed_port_list, denied_port_list):
    vm1_inv, vm2_inv = [vm.get_vm() for vm in (vm1, vm2)]
    test_lib.lib_check_ports_in_a_command(vm1_inv, vm1_inv.vmNics[0].ip,
                                          vm2_inv.vmNics[0].ip, allowed_port_list, denied_port_list, vm2_inv)

    test_lib.lib_check_ports_in_a_command(vm2_inv, vm2_inv.vmNics[0].ip,
                                          vm1_inv.vmNics[0].ip, allowed_port_list, denied_port_list, vm1_inv)

def create_vlan_vm(l3_name=None, disk_offering_uuids=None, system_tags=None, strategy_type='InstantStart', session_uuid = None, instance_offering_uuid = None):
    image_name = os.environ.get('imageName_net')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    if not l3_name:
        l3_name = os.environ.get('l3VlanNetworkName1')

    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    return create_vm([l3_net_uuid], image_uuid, 'vlan_vm', \
            disk_offering_uuids, system_tags=system_tags, \
            instance_offering_uuid = instance_offering_uuid,\
            strategy_type=strategy_type,
            session_uuid = session_uuid)

def create_vm(l3_uuid_list, image_uuid, vm_name = None, \
        disk_offering_uuids = None, default_l3_uuid = None, \
        system_tags = None, instance_offering_uuid = None, strategy_type='InstantStart', session_uuid = None, ps_uuid=None, timeout=None):
    vm_creation_option = test_util.VmOption()
    conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
    if not instance_offering_uuid:
        instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_l3_uuids(l3_uuid_list)
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_name(vm_name)
    vm_creation_option.set_data_disk_uuids(disk_offering_uuids)
    vm_creation_option.set_default_l3_uuid(default_l3_uuid)
    vm_creation_option.set_system_tags(system_tags)
    vm_creation_option.set_session_uuid(session_uuid)
    vm_creation_option.set_ps_uuid(ps_uuid)
    vm_creation_option.set_strategy_type(strategy_type)
    vm_creation_option.set_timeout(600000)

    #vm = zstack_vm_header.ZstackTestVm()
    vm = test_vm_header.ZstackTestVm()	
    vm.set_creation_option(vm_creation_option)
    vm.create()
    return vm

def check_autoscaling_init_vmm_number(initvm_number,autoscaling_groupUuid):
    for i in range(10):
        conf = res_ops.gen_query_conditions('state', '=','Running')
        mix_vmm_total = res_ops.query_resource_count(res_ops.VM_INSTANCE, conf)
        test_util.test_logger("%s" %(mix_vmm_total))
        vmm_virtualrouter_total = res_ops.query_resource_count(res_ops.VIRTUALROUTER_VM, conf)
        vmm_total = mix_vmm_total - vmm_virtualrouter_total
        if vmm_total != initvm_number:
            if i < 9:
                time.sleep(5)
                continue
            test_util.test_dsc("autoscaling group init vmm fail")
            autoscaling.delete_autoScaling_group(autoscaling_groupUuid)
            test_util.test_fail("autoscaling group init vmm fail")
        else:
            test_util.test_logger("autoscaling group init vmm sucessfully")
            break

def check_deleteautoscaling_vmm_number():
    for i in range(10):
        conf = res_ops.gen_query_conditions('state', '=','Running')
        mix_vmm_total = res_ops.query_resource_count(res_ops.VM_INSTANCE, conf)
        test_util.test_logger("%s" %(mix_vmm_total))
        vmm_virtualrouter_total = res_ops.query_resource_count(res_ops.VIRTUALROUTER_VM, conf)
        if mix_vmm_total != vmm_virtualrouter_total:
            if i < 9:
                time.sleep(5)
                continue
            test_util.test_dsc("autoscaling delete vmm fail")
            test_util.test_fail("Test AutoScaling Group Failed")
        else:
            test_util.test_logger("autoscaling delete vmm sucessfully")
            break

def check_add_newinstance_vmm_number(max_number,expect_number,autoscaling_groupUuid):
        conf = res_ops.gen_query_conditions('state', '=','Running')
        vmm_total = res_ops.query_resource_count(res_ops.VM_INSTANCE, conf)
        test_util.test_logger("%s" %(vmm_total))
        vmm_virtualrouter_total = res_ops.query_resource_count(res_ops.VIRTUALROUTER_VM, conf)
	vmm_total = vmm_total - vmm_virtualrouter_total
        if vmm_total == expect_number and vmm_total <= max_number:
             test_util.test_dsc("autoscaling add new instance successfully")
	elif vmm_total > max_number:
             autoscaling.delete_autoScaling_group(autoscaling_groupUuid)
	     test_util.test_fail("autoscaling create vm can not GreaterThan %s" %(max_number))
        elif vmm_total != expect_number:
             autoscaling.delete_autoScaling_group(autoscaling_groupUuid)
             test_util.test_fail("autoscaling add new instance fail")

def check_removalinstance_vmm_number(min_number,expect_number,autoscaling_groupUuid):
	conf = res_ops.gen_query_conditions('state', '=','Running')
        vmm_total = res_ops.query_resource_count(res_ops.VM_INSTANCE, conf)
        test_util.test_logger("%s" %(vmm_total))
        vmm_virtualrouter_total = res_ops.query_resource_count(res_ops.VIRTUALROUTER_VM, conf)
        vmm_total = vmm_total - vmm_virtualrouter_total
        if vmm_total == expect_number and vmm_total >= min_number:
             test_util.test_dsc("autoscaling removal instance  successfully")
        elif vmm_total < min_number:
             autoscaling.delete_autoScaling_group(autoscaling_groupUuid)
             test_util.test_fail("autoscaling create vm can not LessThan %s" %(min_number))
        elif vmm_total != expect_number:
             autoscaling.delete_autoScaling_group(autoscaling_groupUuid)
             test_util.test_fail("autoscaling removal instance fail")


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

