'''

Create an unified test_stub to share test operations

@author: Youyk
'''

import os
import subprocess
import sys
import time
import threading

import zstacklib.utils.ssh as ssh
import apibinding.api_actions as api_actions
import zstacklib.utils.jsonobject as jsonobject
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.zstack_test.zstack_test_vm as zstack_vm_header
import zstackwoodpecker.zstack_test.zstack_test_volume as zstack_volume_header
import zstackwoodpecker.zstack_test.zstack_test_security_group as zstack_sg_header
import zstackwoodpecker.zstack_test.zstack_test_eip as zstack_eip_header
import zstackwoodpecker.zstack_test.zstack_test_vip as zstack_vip_header
import zstackwoodpecker.zstack_test.zstack_test_load_balancer as zstack_lb_header
import zstackwoodpecker.zstack_test.zstack_test_port_forwarding as zstack_pf_header
import zstackwoodpecker.operations.account_operations as  account_operations
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.operations.longjob_operations as longjob_ops
import zstackwoodpecker.zstack_test.zstack_test_image as test_image
import zstackwoodpecker.operations.primarystorage_operations as ps_ops
import zstackwoodpecker.operations.cdrom_operations as cdrom_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import apibinding.inventory as inventory
import random
import functools
from zstackwoodpecker.operations import vm_operations as vm_ops
from zstackwoodpecker.test_chain import TestChain
import commands
from lib2to3.pgen2.token import STAR
from zstacklib.utils import shell
from collections import OrderedDict
import telnetlib

PfRule = test_state.PfRule
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

def create_lb_vm(l3_name=None, disk_offering_uuids=None, session_uuid = None):
    '''
        Load Balance VM will only use L3VlanNetworkName6
    '''
    image_name = os.environ.get('imageName_net')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    if not l3_name:
        l3_name = os.environ.get('l3VlanNetworkName6')

    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    return create_vm([l3_net_uuid], image_uuid, 'vlan_lb_vm', disk_offering_uuids, session_uuid = session_uuid)

def create_sg_vm(l3_name=None, disk_offering_uuids=None, session_uuid = None):
    '''
        SG test need more network commands in guest. So it needs VR image.
    '''
    image_name = os.environ.get('imageName_net')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    if not l3_name:
        #l3_name = 'guestL3VlanNetwork1'
        l3_name = os.environ.get('l3VlanNetworkName1')

    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    return create_vm([l3_net_uuid], image_uuid, 'vlan_vm', disk_offering_uuids, session_uuid = session_uuid)

def create_windows_vm(l3_name=None, disk_offering_uuids=None, session_uuid = None):
    '''
        Create windows platform type vm.
    '''
    image_name = os.environ.get('imageName_windows')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    if not l3_name:
        #l3_name = 'guestL3VlanNetwork1'
        l3_name = os.environ.get('l3VlanNetworkName1')

    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    return create_vm([l3_net_uuid], image_uuid, 'windows_vm', disk_offering_uuids, session_uuid = session_uuid)

def create_windows_vm_2(l3_name=None, disk_offering_uuids=None, session_uuid = None, instance_offering_uuid = None, system_tags=None):
    '''
        Create windows platform type vm.
    '''
    image_name = os.environ.get('imageName_windows')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    if not l3_name:
        #l3_name = 'guestL3VlanNetwork1'
        l3_name = os.environ.get('l3VlanNetworkName1')

    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    return create_vm([l3_net_uuid], image_uuid, 'windows_vm', disk_offering_uuids, instance_offering_uuid = instance_offering_uuid, session_uuid = session_uuid, system_tags=system_tags, timeout=1200000)

def create_other_vm(l3_name=None, disk_offering_uuids=None, session_uuid = None):
    '''
        Create other platform type vm.
    '''
    image_name = os.environ.get('imageName_other')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    if not l3_name:
        #l3_name = 'guestL3VlanNetwork1'
        l3_name = os.environ.get('l3VlanNetworkName1')

    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    return create_vm([l3_net_uuid], image_uuid, 'other_vm', disk_offering_uuids, session_uuid = session_uuid)

def create_basic_vm(disk_offering_uuids=None, system_tags=None, l3_name=None, session_uuid = None):
    image_name = os.environ.get('imageName_net')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    if not l3_name:
        l3_name = os.environ.get('l3VlanNetworkName1')
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    return create_vm([l3_net_uuid], image_uuid, 'basic_no_vlan_vm', disk_offering_uuids, system_tags=system_tags, session_uuid = session_uuid)

def create_user_vlan_vm(l3_name=None, disk_offering_uuids=None, session_uuid = None):
    image_name = os.environ.get('imageName_net')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    if not l3_name:
        l3_name = os.environ.get('l3NoVlanNetworkName1')

    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    return create_vm([l3_net_uuid], image_uuid, 'user_vlan_vm', disk_offering_uuids, session_uuid = session_uuid)

def create_specified_ps_vm(l3_name=None, ps_uuid=None, session_uuid = None):
    image_name = os.environ.get('imageName_net')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    if not l3_name:
        l3_name = os.environ.get('l3NoVlanNetworkName1')

    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    return create_vm([l3_net_uuid], image_uuid, 'user_vlan_vm', session_uuid = session_uuid, ps_uuid = ps_uuid)


def create_vlan_sg_vm(disk_offering_uuids=None, session_uuid = None):
    image_name = os.environ.get('imageName_net')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    l3_name = os.environ.get('l3VlanNetworkName1')
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    return create_vm([l3_net_uuid], image_uuid, 'vlan_sg_vm', disk_offering_uuids, session_uuid = session_uuid)

def create_dnat_vm(disk_offering_uuids=None, session_uuid = None):
    image_name = os.environ.get('imageName_net')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    l3_name = os.environ.get('l3VlanDNATNetworkName')
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    return create_vm([l3_net_uuid], image_uuid, 'vlan_sg_vm', disk_offering_uuids, session_uuid = session_uuid)

def create_vm_with_user_args(system_tags = None, session_uuid = None):
    image_name = os.environ.get('imageName_net')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    l3_name = os.environ.get('l3VlanNetworkName1')
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    return create_vm([l3_net_uuid], image_uuid, 'user_args_vm', system_tags = system_tags, session_uuid = session_uuid)

# parameter: vmname; l3_net: l3_net_description, or [l3_net_uuid,]; image_uuid:
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
    vm_creation_option.set_timeout(900000)
#     vm_creation_option.set_timeout(600000)

    vm = zstack_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    return vm

def create_vm_with_iso(l3_uuid_list, image_uuid, vm_name = None, root_disk_uuids = None, instance_offering_uuid = None, \
                       disk_offering_uuids = None, default_l3_uuid = None, system_tags = None, \
                       session_uuid = None, ps_uuid=None):
    vm_creation_option = test_util.VmOption()
    conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
    if not instance_offering_uuid:
        instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_l3_uuids(l3_uuid_list)
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_name(vm_name)
    vm_creation_option.set_root_disk_uuid(root_disk_uuids)
    vm_creation_option.set_data_disk_uuids(disk_offering_uuids)
    vm_creation_option.set_default_l3_uuid(default_l3_uuid)
    vm_creation_option.set_system_tags(system_tags)
    vm_creation_option.set_session_uuid(session_uuid)
    vm_creation_option.set_ps_uuid(ps_uuid)
    vm_creation_option.set_timeout(600000)
    vm = zstack_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    return vm

def get_other_ps_uuid():
    cond_ps = res_ops.gen_query_conditions('status', '=', 'connected')
    cond_ps = res_ops.gen_query_conditions('state', '=', 'Enabled', cond_ps)
    all_ps = res_ops.query_resource(res_ops.PRIMARY_STORAGE, cond_ps)
    all_ps_uuids = [ps.uuid for ps in all_ps]
    cond_vm = res_ops.gen_query_conditions('state', '=', 'Running')
    running_vm = res_ops.query_resource(res_ops.VM_INSTANCE, cond_vm)
    ext_ps_uuids = [vm.allVolumes[0].primaryStorageUuid for vm in running_vm]
    other_ps_uuids = list(set(all_ps_uuids) - set(ext_ps_uuids))
    return random.choice(other_ps_uuids if other_ps_uuids else all_ps_uuids)

def create_volume(volume_creation_option=None, session_uuid = None):
    if not volume_creation_option:
        disk_offering = test_lib.lib_get_disk_offering_by_name(os.environ.get('smallDiskOfferingName'))
        volume_creation_option = test_util.VolumeOption()
        volume_creation_option.set_disk_offering_uuid(disk_offering.uuid)
        volume_creation_option.set_name('vr_test_volume')

    volume_creation_option.set_session_uuid(session_uuid)
    if not volume_creation_option.get_primary_storage_uuid():
        volume_creation_option.set_primary_storage_uuid(get_other_ps_uuid())
    volume = zstack_volume_header.ZstackTestVolume()
    volume.set_creation_option(volume_creation_option)
    volume.create()
    return volume

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

def create_vlan_vm_with_volume(l3_name=None, disk_offering_uuids=None, disk_number=None, session_uuid = None):
    if not disk_offering_uuids:
        disk_offering = test_lib.lib_get_disk_offering_by_name(os.environ.get('smallDiskOfferingName'))
        disk_offering_uuids = [disk_offering.uuid]
        if disk_number:
            for i in range(disk_number - 1):
                disk_offering_uuids.append(disk_offering.uuid)

    return create_vlan_vm(l3_name, disk_offering_uuids, \
            session_uuid = session_uuid)

def create_eip(eip_name=None, vip_uuid=None, vnic_uuid=None, vm_obj=None, \
        session_uuid = None):
    if not vip_uuid:
        l3_name = os.environ.get('l3PublicNetworkName')
        l3_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
        vip_uuid = net_ops.acquire_vip(l3_uuid).uuid

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

def get_snat_ip_as_vip(snat_ip):
    vip = zstack_vip_header.ZstackTestVip()
    vip.get_snat_ip_as_vip(snat_ip)
    return vip
    
def create_vr_vm(test_obj_dict, l3_name, session_uuid = None):
    '''
    '''
    vr_l3_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    vrs = test_lib.lib_find_vr_by_l3_uuid(vr_l3_uuid)
    temp_vm = None
    if not vrs:
        #create temp_vm1 for getting vlan1's vr for test pf_vm portforwarding
        temp_vm = create_vlan_vm(l3_name, session_uuid = session_uuid)
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

def share_admin_resource(account_uuid_list):
    def get_uuid(resource):
        temp_list = []
        for item in resource:
            temp_list.append(item.uuid)
        return temp_list

    resource_list = []

    resource_list.extend(get_uuid(res_ops.get_resource(res_ops.INSTANCE_OFFERING)))
    resource_list.extend(get_uuid(res_ops.get_resource(res_ops.IMAGE)))
    resource_list.extend(get_uuid(res_ops.get_resource(res_ops.L3_NETWORK)))
    resource_list.extend(get_uuid(res_ops.get_resource(res_ops.DISK_OFFERING)))
    acc_ops.share_resources(account_uuid_list, resource_list)

def get_vr_by_private_l3_name(l3_name):
    vr_l3_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    vrs = test_lib.lib_find_vr_by_l3_uuid(vr_l3_uuid)
    if not vrs:
        #create temp_vm for getting vlan1's vr 
        temp_vm = create_vlan_vm(l3_name)
        vr = test_lib.lib_find_vr_by_vm(temp_vm.vm)[0]
        temp_vm.destroy()
    else:
        vr = vrs[0]
    return vr

def exercise_parallel(func, ops_num=10, thread_threshold=3):
    for ops_id in range(ops_num):
        thread = threading.Thread(target=func, args=(ops_id, ))
        while threading.active_count() > thread_threshold:
            time.sleep(0.5)
        exc = sys.exc_info()
        thread.start()

    while threading.activeCount() > 1:
        exc = sys.exc_info()
        time.sleep(0.1)

def sleep_util(timestamp):
    while True:
        if time.time() >= timestamp:
            break
        time.sleep(0.5)

def create_test_file(vm_inv, test_file):
    '''
    the bandwidth is for calculate the test file size,
    since the test time should be finished in 60s.
    bandwidth unit is KB.
    '''
    file_size = 1024 * 2
    seek_size = file_size / 1024 - 1

    cmd = 'dd if=/dev/zero of=%s bs=1K count=1 seek=%d' \
           % (test_file, seek_size)

    if not test_lib.lib_execute_command_in_vm(vm_inv, cmd):
        test_util.test_fail('test file is not created')

def attach_mount_volume(volume, vm, mount_point):
    volume.attach(vm)
    import tempfile
    script_file = tempfile.NamedTemporaryFile(delete=False)
    script_file.write('''
mkdir -p %s
device="/dev/`ls -ltr --file-type /dev | awk '$4~/disk/ {print $NF}' | grep -v '[[:digit:]]' | tail -1`"
mount ${device}1 %s
''' % (mount_point, mount_point))
    script_file.close()

    vm_inv = vm.get_vm()
    if not test_lib.lib_execute_shell_script_in_vm(vm_inv, script_file.name):
        test_util.test_fail("mount operation failed in [volume:] %s in [vm:] %s" % (volume.get_volume().uuid, vm_inv.uuid))
        os.unlink(script_file.name)

def scp_file_to_vm(vm_inv, src_file, target_file):
    vm_ip = vm_inv.vmNics[0].ip
    vm_username = test_lib.lib_get_vm_username(vm_inv)
    vm_password = test_lib.lib_get_vm_password(vm_inv)
    ssh.scp_file(src_file, target_file, vm_ip, vm_username, vm_password)

def make_ssh_no_password(vm_inv):
    vm_ip = vm_inv.vmNics[0].ip
    ssh.make_ssh_no_password(vm_ip, test_lib.lib_get_vm_username(vm_inv), \
            test_lib.lib_get_vm_password(vm_inv))

def create_named_vm(vm_name=None, disk_offering_uuids=None, session_uuid = None):

    image_name = os.environ.get('imageName_net')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    l3_name = os.environ.get('l3VlanNetworkName1')
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    if not vm_name:
        vm_name = 'named_vm'
    return create_vm([l3_net_uuid], image_uuid, vm_name, disk_offering_uuids, session_uuid = session_uuid)

def time_convert(log_str):
    time_str = log_str.split()[0]+' '+log_str.split()[1]
    time_microscond = time_str.split(',')[1]
    time_str = time_str.split(',')[0]
    time_tuple = time.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    return int(time.mktime(time_tuple)*1000+int(time_microscond))

def get_stage_time(vm_name, begin_time):
    mn_server_log = "/usr/local/zstacktest/apache-tomcat/logs/management-server.log"
    file_obj = open(mn_server_log)
    for line in file_obj.readlines():
        if line.find('APICreateVmInstanceMsg') != -1 and line.find(vm_name) != -1:
            time_stamp = time_convert(line)
            if int(time_stamp) >= begin_time:
                api_id = line.split('{"', 1)[1].split(',')[-3].split(':')[1].strip('"')
                break
    file_obj.close

    log_str = ''
    select_bs_time = select_bs_end_time = select_bs_begin_time = 0
    allocate_host_time = allocate_host_end_time = allocate_host_begin_time = 0
    allocate_ps_time = allocate_ps_end_time = allocate_ps_begin_time = 0
    local_storage_allocate_capacity_time = local_storage_allocate_capacity_end_time = local_storage_allocate_capacity_begin_time = 0
    allocate_volume_time = allocate_volume_end_time = allocate_volume_begin_time = 0
    allocate_nic_time = allocate_nic_end_time = allocate_nic_begin_time = 0
    instantiate_res_time = instantiate_res_end_time = instantiate_res_begin_time = 0
    instantiate_res_pre_time = instantiate_res_pre_end_time = instantiate_res_pre_begin_time = 0
    create_on_hypervisor_time = create_on_hypervisor_end_time = create_on_hypervisor_begin_time = 0
    instantiate_res_post_time = instantiate_res_post_end_time = instantiate_res_post_begin_time = 0

    file_obj = open(mn_server_log)
    for line in file_obj.readlines():
        if line.find(api_id) != -1 and line.find('SimpleFlowChain') != -1 and line.find('VmImageSelectBackupStorageFlow') != -1 and line.find('start executing flow') != -1:
            select_bs_begin_time = time_convert(line)
        if line.find(api_id) != -1 and line.find('SimpleFlowChain') != -1 and line.find('VmImageSelectBackupStorageFlow') != -1 and line.find('successfully executed flow') != -1:
            select_bs_end_time = time_convert(line)

        if line.find(api_id) != -1 and line.find('SimpleFlowChain') != -1 and line.find('VmAllocateHostFlow') != -1 and line.find('start executing flow') != -1:
            allocate_host_begin_time = time_convert(line)
        if line.find(api_id) != -1 and line.find('SimpleFlowChain') != -1 and line.find('VmAllocateHostFlow') != -1 and line.find('successfully executed flow') != -1:
            allocate_host_end_time = time_convert(line)

        if line.find(api_id) != -1 and line.find('SimpleFlowChain') != -1 and line.find('VmAllocatePrimaryStorageFlow') != -1 and line.find('start executing flow') != -1:
            allocate_ps_begin_time = time_convert(line)
        if line.find(api_id) != -1 and line.find('SimpleFlowChain') != -1 and line.find('VmAllocatePrimaryStorageFlow') != -1 and line.find('successfully executed flow') != -1:
            allocate_ps_end_time = time_convert(line)

        if line.find(api_id) != -1 and line.find('SimpleFlowChain') != -1 and line.find('LocalStorageAllocateCapacityFlow') != -1 and line.find('start executing flow') != -1:
            local_storage_allocate_capacity_begin_time = time_convert(line)
        if line.find(api_id) != -1 and line.find('SimpleFlowChain') != -1 and line.find('LocalStorageAllocateCapacityFlow') != -1 and line.find('successfully executed flow') != -1:
            local_storage_allocate_capacity_end_time = time_convert(line)

        if line.find(api_id) != -1 and line.find('SimpleFlowChain') != -1 and line.find('VmAllocateVolumeFlow') != -1 and line.find('start executing flow') != -1:
            allocate_volume_begin_time = time_convert(line)
        if line.find(api_id) != -1 and line.find('SimpleFlowChain') != -1 and line.find('VmAllocateVolumeFlow') != -1 and line.find('successfully executed flow') != -1:
            allocate_volume_end_time = time_convert(line)

        if line.find(api_id) != -1 and line.find('SimpleFlowChain') != -1 and line.find('VmAllocateNicFlow') != -1 and line.find('start executing flow') != -1:
            allocate_nic_begin_time = time_convert(line)
        if line.find(api_id) != -1 and line.find('SimpleFlowChain') != -1 and line.find('VmAllocateNicFlow') != -1 and line.find('successfully executed flow') != -1:
            allocate_nic_end_time = time_convert(line)


        if line.find(api_id) != -1 and line.find('SimpleFlowChain') != -1 and line.find('VmInstantiateResourcePreFlow') != -1 and line.find('start executing flow') != -1:
            instantiate_res_pre_begin_time = time_convert(line)
        if line.find(api_id) != -1 and line.find('SimpleFlowChain') != -1 and line.find('VmInstantiateResourcePreFlow') != -1 and line.find('successfully executed flow') != -1:
            instantiate_res_pre_end_time = time_convert(line)

        if line.find(api_id) != -1 and line.find('SimpleFlowChain') != -1 and line.find('VmCreateOnHypervisorFlow') != -1 and line.find('start executing flow') != -1:
            create_on_hypervisor_begin_time = time_convert(line)
        if line.find(api_id) != -1 and line.find('SimpleFlowChain') != -1 and line.find('VmCreateOnHypervisorFlow') != -1 and line.find('successfully executed flow') != -1:
            create_on_hypervisor_end_time = time_convert(line)

        if line.find(api_id) != -1 and line.find('SimpleFlowChain') != -1 and line.find('VmInstantiateResourcePostFlow') != -1 and line.find('start executing flow') != -1:
            instantiate_res_post_begin_time = time_convert(line)
        if line.find(api_id) != -1 and line.find('SimpleFlowChain') != -1 and line.find('VmInstantiateResourcePostFlow') != -1 and line.find('successfully executed flow') != -1:
            instantiate_res_post_end_time = time_convert(line)

    file_obj.close()

    if select_bs_end_time != 0 and select_bs_begin_time != 0:
        select_bs_time = select_bs_end_time - select_bs_begin_time
    if allocate_host_end_time != 0 and allocate_host_begin_time != 0:
        allocate_host_time = allocate_host_end_time - allocate_host_begin_time
    if allocate_ps_end_time != 0 and allocate_ps_begin_time != 0:
        allocate_ps_time = allocate_ps_end_time - allocate_ps_begin_time
    if local_storage_allocate_capacity_end_time != 0 and local_storage_allocate_capacity_begin_time != 0:
        local_storage_allocate_capacity_time = local_storage_allocate_capacity_end_time - local_storage_allocate_capacity_begin_time
    if allocate_volume_end_time != 0 and allocate_volume_begin_time != 0:
        allocate_volume_time = allocate_volume_end_time - allocate_volume_begin_time
    if allocate_nic_end_time != 0 and allocate_volume_begin_time != 0:
        allocate_nic_time = allocate_nic_end_time - allocate_nic_begin_time
    if instantiate_res_pre_end_time != 0 and instantiate_res_pre_begin_time != 0:
        instantiate_res_pre_time = instantiate_res_pre_end_time - instantiate_res_pre_begin_time
    if create_on_hypervisor_end_time != 0 and create_on_hypervisor_begin_time != 0:
        create_on_hypervisor_time = create_on_hypervisor_end_time - create_on_hypervisor_begin_time
    if instantiate_res_post_end_time != 0 and instantiate_res_post_begin_time != 0:
        instantiate_res_post_time = instantiate_res_post_end_time - instantiate_res_post_begin_time
    return [select_bs_time, allocate_host_time, allocate_ps_time, local_storage_allocate_capacity_time, allocate_volume_time, allocate_nic_time, instantiate_res_pre_time, create_on_hypervisor_time, instantiate_res_post_time]

def execute_shell_in_process(cmd, timeout=10, logfd=None):
    if not logfd:
        process = subprocess.Popen(cmd, executable='/bin/sh', shell=True, universal_newlines=True)
    else:
        process = subprocess.Popen(cmd, executable='/bin/sh', shell=True, stdout=logfd, stderr=logfd, universal_newlines=True)

    start_time = time.time()
    while process.poll() is None:
        curr_time = time.time()
        TEST_TIME = curr_time - start_time
        if TEST_TIME > timeout:
            process.kill()
            test_util.test_logger('[shell:] %s timeout ' % cmd)
            return False
        time.sleep(1)

    test_util.test_logger('[shell:] %s is finished.' % cmd)
    return process.returncode

def find_ps_local():
    ps_list = res_ops.get_resource(res_ops.PRIMARY_STORAGE)
    for ps in ps_list:
        if ps.type == inventory.LOCAL_STORAGE_TYPE:
            return ps
    test_util.test_logger("Can not find local primary storage ")
    return None

def find_ps_nfs():
    ps_list = res_ops.get_resource(res_ops.PRIMARY_STORAGE)
    for ps in ps_list:
        if ps.type == inventory.NFS_PRIMARY_STORAGE_TYPE:
            return ps
    test_util.test_logger("Can not find NFS primary storage ")
    return None

def ensure_hosts_connected(wait_time):
    for i in range(wait_time):
        time.sleep(1)
        host_list = res_ops.query_resource(res_ops.HOST)
        for host in host_list:
            if not "connected" in host.status.lower():
                test_util.test_logger("found not connected ps status: %s" %(host.status))
                break
        else:
            return
    else:
        test_util.test_fail("host status didn't change to Connected within %s, therefore, failed" % (wait_time))


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
    vm_creation_option.set_timeout(600000)
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

    vm = zstack_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    return vm

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


def generate_pub_test_vm(tbj):
    disk_offering_uuids = [random.choice(res_ops.get_resource(res_ops.DISK_OFFERING)).uuid]
    l3_name_list = ['l3PublicNetworkName', 'l3NoVlanNetworkName1', 'l3NoVlanNetworkName2']

    pub_l3_vm, flat_l3_vm, vr_l3_vm = [create_vm_with_random_offering(vm_name='test_vm',
                                                                      image_name='imageName_net',
                                                                      disk_offering_uuids=random.choice([None, disk_offering_uuids]),
                                                                      l3_name=name) for name in l3_name_list]
    for vm in pub_l3_vm, flat_l3_vm, vr_l3_vm:
        #vm.check = test_lib.checker_wrapper(vm, 'DHCP', vm.get_vm().vmNics[0].l3NetworkUuid)
        vm.check()
        tbj.add_vm(vm)

    return pub_l3_vm, flat_l3_vm, vr_l3_vm


def install_iperf(vm_inv):
    vm_ip = vm_inv.vmNics[0].ip

    ssh_cmd = 'ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm_ip
    cmd = '%s "wget http://dl.fedoraproject.org/pub/epel/7/x86_64/i/iperf-2.0.10-1.el7.x86_64.rpm; rpm -ivh iperf-2.0.10-1.el7.x86_64.rpm"' % (ssh_cmd)
    if execute_shell_in_process(cmd, 150) != 0:
        test_util.test_fail('fail to install iperf.')

def test_iperf_bandwidth(vm1_inv,vm2_inv,vip_ip,server_iperf_port,client_iperf_port,bandwidth,raise_exception=True):
    vm1_ip = vm1_inv.vmNics[0].ip
    vm2_ip = vm2_inv.vmNics[0].ip

    cmd1 = "sshpass -p 'password' ssh root@%s iperf -s -p %s | awk 'NR==7 {print $(NF-1)}'" % (vm1_ip, server_iperf_port)
    process1 = subprocess.Popen(cmd1, executable='/bin/sh', shell=True, stdout=subprocess.PIPE, universal_newlines=True)
    time.sleep(10)
    cmd2 = "iperf -c %s -p %s | awk 'NR==7 {print $(NF-1)}'" % (vip_ip, client_iperf_port)
    ret, output, stderr = ssh.execute(cmd2, vm2_ip, "root", "password", False, 22)
    inboundBandwidth = float(output)*128

    time.sleep(30)
    cmd3 = "pkill -9 iperf"
    ret, output, stderr = ssh.execute(cmd3, vm1_ip, "root", "password", False, 22)
    outboundBandwidth = float(process1.stdout.read())*128

    print ("inboundBandwidth = %s") % inboundBandwidth
    print ("outboundBandwidth = %s") % outboundBandwidth

    if  (inboundBandwidth < bandwidth*1.25 and outboundBandwidth < bandwidth*1.25):
        test_util.test_logger('Successed to set vip qos bandwidth.')
    else:
        test_util.test_fail('Failed to set vip qos bandwidth.')


def skip_if_no_service_in_l3(service_type, l3_name):
    def decorator(test_method):
        @functools.wraps(test_method)
        def wrapper():
            l3 = test_lib.lib_get_l3_by_name(l3_name)
            if not l3:
                test_util.test_skip('Can not find l3!')
            if service_type not in [service.networkServiceType for service in l3.networkServices]:
                test_util.test_skip('Can not find service {} in l3: {}, skip test'.format(service_type, l3_name))
            return test_method()
        return wrapper
    return decorator


def clean_all_vr_vm_before_case_execution(test_method):
    @functools.wraps(test_method)
    def wrapper():
        cond = res_ops.gen_query_conditions('type', '=', 'ApplianceVm')
        vr_vm_list = res_ops.query_resource(res_ops.VM_INSTANCE, cond)
        if vr_vm_list:
            for vr_vm in vr_vm_list:
                vm_ops.destroy_vm(vr_vm.uuid)
        return test_method()
    return wrapper


def remove_all_vr_vm():
    cond = res_ops.gen_query_conditions('type', '=', 'ApplianceVm')
    vr_vm_list = res_ops.query_resource(res_ops.VM_INSTANCE, cond)
    if vr_vm_list:
        for vr_vm in vr_vm_list:
            vm_ops.destroy_vm(vr_vm.uuid)



def get_another_ip_of_host(ip, username, password):
    '''
        This function is only suitable for 2 network cards in the host.
    '''
    cmd = "ip r|grep kernel|grep -v %s|awk '{print $NF}'" %(ip)
    output = test_lib.lib_execute_ssh_cmd(ip, username, password, cmd, timeout=30)
    return output.split(':')[-1].strip()

def set_httpd_in_vm(ip, username, password):
    cmd = "yum install httpd -y"
    if not test_lib.lib_execute_ssh_cmd(ip, username, password, cmd, timeout=600):
       test_util.test_fail('install httpd in vm failed')
    cmd = "systemctl start httpd; iptables -F; echo %s > /var/www/html/index.html" % ip
    test_lib.lib_execute_ssh_cmd(ip, username, password, cmd, timeout=300)

def gen_random_port(start=1, end=100):
#     cmd = "lsof -i -P -n | grep LISTEN | awk -F ':' '{print $2}' | awk '{print $1}'"
    cmd = "netstat -plnt | awk 'NR>2{print $4}'"
    ret = commands.getoutput(cmd).split('\n')
#     ret = list(set(ret))
    port_listening = [int(p.split(':')[-1]) for p in ret if p]
    port_range = xrange(start, end)
    port_val_list = [port for port in port_range if port not in port_listening]
    return random.choice(port_val_list)


class VIPQOS(object):
    def __init__(self):
        self.mn_ip = None
        self.ssh_cmd = 'sshpass -p password ssh -o StrictHostKeyChecking=no root@'
        self.inbound_width = None
        self.outbound_width = None
        self.iperf_url = None
        self.vm_ip = None
        self.vm_ip2 = None
        self.port = None
        self.iperf_port = None
        self.lb = None
        self.vr = None
        self.reconnected = False

    def install_iperf(self, vm_ip):
        iperf_url = os.getenv('iperfUrl')
        iperf_file = iperf_url.split('/')[-1]
        cmd_loc = 'sshpass -p password scp -o StrictHostKeyChecking=no root@%s .' % iperf_url
        if not os.path.exists(iperf_file):
            commands.getstatusoutput(cmd_loc)
        cmd = "sshpass -p password scp -o StrictHostKeyChecking=no %s root@%s:; %s ' rpm -ivh %s'" % (iperf_file, vm_ip, self.ssh_cmd + vm_ip, iperf_file)
        if commands.getstatusoutput(self.ssh_cmd + vm_ip + ' iperf3 -v')[0] != 0:
            ret = commands.getstatusoutput(cmd)
            print '*' * 90
            print ret
            if ret[0] != 0:
                test_util.test_fail('fail to install iperf.')

    def start_iperf_server(self, vm_ip):
        terminate_cmd =  self.ssh_cmd + vm_ip + " pkill -9 iperf3"
        commands.getstatusoutput(terminate_cmd)
        time.sleep(5)
        if self.iperf_port:
            cmd = self.ssh_cmd + self.vm_ip + ' "iperf3 -s -p %s -D"' % self.iperf_port
        else:
            cmd = self.ssh_cmd + self.vm_ip + ' "iperf3 -s -D"'
        commands.getstatusoutput(cmd)

    def create_vm(self, l3_network):
        self.vm = create_vlan_vm(os.getenv(l3_network))
        self.vm.check()
        self.vm_ip = self.vm.vm.vmNics[0].ip
#         time.sleep(60)

    def create_vm2(self, l3_network):
        self.vm2 = create_vlan_vm(os.getenv(l3_network))
        self.vm2.check()
        self.vm_ip2 = self.vm.vm.vmNics[0].ip
#         time.sleep(60)

    def attach_eip_service(self):
        try:
            net_ops.attach_eip_service_to_l3network(self.pri_l3_uuid, self.service_uuid)
        except:
            pass

    def detach_eip_service(self):
        try:
            net_ops.detach_eip_service_from_l3network(self.pri_l3_uuid, self.service_uuid)
        except:
            pass

    def create_vip(self, flat):
        self.mn_ip = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].hostName
        commands.getoutput("iptables -F")
        self.vm_nic_uuid = self.vm.vm.vmNics[0].uuid
        self.pri_l3_uuid = self.vm.vm.vmNics[0].l3NetworkUuid
        if flat:
            cond = res_ops.gen_query_conditions('type', '=', 'Flat')
            self.service_uuid = res_ops.query_resource(res_ops.NETWORK_SERVICE_PROVIDER, cond)[0].uuid
            self.attach_eip_service()
            cond_publ = res_ops.gen_query_conditions('category', '=', 'Public')
            l3_uuid = res_ops.query_resource(res_ops.L3_NETWORK, cond_publ)[0].uuid
        else:
            self.vr = test_lib.lib_find_vr_by_l3_uuid(self.pri_l3_uuid)[0]
            time.sleep(10)
            l3_uuid = test_lib.lib_find_vr_pub_nic(self.vr).l3NetworkUuid
        self.vip = create_vip('vip_for_qos', l3_uuid)
        self.vip_ip = self.vip.get_vip().ip
        self.vip_uuid = self.vip.get_vip().uuid

    def create_eip(self, flat=False):
        self.create_vip(flat)
        eip = create_eip('qos_test', vip_uuid=self.vip.get_vip().uuid, vnic_uuid=self.vm_nic_uuid, vm_obj=self.vm)
        self.vip.attach_eip(eip)
        time.sleep(10)

    def set_vip_qos(self, inbound_width=None, outbound_width=None, port=None, iperf_port=None):
        self.inbound_width = inbound_width * 1024 * 1024
        self.outbound_width = outbound_width * 1024 * 1024
        self.port = port
        self.iperf_port = iperf_port
        net_ops.set_vip_qos(vip_uuid=self.vip_uuid, inboundBandwidth=self.inbound_width, outboundBandwidth=self.outbound_width, port=port)
        time.sleep(10)

    def del_vip_qos(self):
        net_ops.delete_vip_qos(self.vip_uuid, self.port)
        time.sleep(10)

    def create_pf(self):
#         self.create_vip(flat=False)
#         startPort, endPort = Port.get_start_end_ports(Port.rule3_ports)
#         self.iperf_port = gen_random_port(startPort, endPort)
        pf_creation_opt = PfRule.generate_pf_rule_option(self.mn_ip, protocol=inventory.TCP, 
                                                         vip_target_rule=Port.rule3_ports, private_target_rule=Port.rule3_ports, 
                                                         vip_uuid=self.vip.get_vip().uuid, vm_nic_uuid=self.vm_nic_uuid)
        test_pf = zstack_pf_header.ZstackTestPortForwarding()
        test_pf.set_creation_option(pf_creation_opt)
        test_pf.create(self.vm)
        self.vip.attach_pf(test_pf)

    def create_lb(self, port):
#         self.create_vip(flat=False)
        self.iperf_port = port
        self.lb = zstack_lb_header.ZstackTestLoadBalancer()
        self.lb.create('lb for vip qos test', self.vip.get_vip().uuid)
        lb_creation_option = test_lib.lib_create_lb_listener_option(lbl_name='vip qos test',
                                                                    lbl_port = port, lbi_port = port)
        lbl = self.lb.create_listener(lb_creation_option)
        lbl.add_nics([self.vm2.vm.vmNics[0].uuid])

    def check_bandwidth(self, vm_ip, direction, cmd, excepted_bandwidth):
        if self.vr and not self.reconnected:
            vm_ops.reconnect_vr(self.vr.uuid)
            self.reconnected = True
            time.sleep(10)
        for ip in [self.mn_ip, self.vm_ip, self.vm_ip2]:
            if ip:
                self.install_iperf(ip)
        commands.getoutput(self.ssh_cmd + vm_ip +" iptables -F")
        time.sleep(10)
        self.start_iperf_server(vm_ip)
        time.sleep(30)
        actual_bandwidth, bndwth = 0, 0
        for _ in range(5):
            (status, ret) = commands.getstatusoutput(cmd)
            seper = '*' * 80
            print "%s\n%s\n%s" % (seper, ret, seper)
            if direction == 'out':
                pos = -3
            else:
                pos = -4
            summ = ret.split('\n')[pos]
            bndwth = float(summ.split()[-3])
            if summ.split()[-2] == 'Kbits/sec':
                bndwth /= 1024
            elif summ.split()[-2] == 'Gbits/sec':
                bndwth *= 1024
            if status == 0:
                if excepted_bandwidth == 1000:
                    assert bndwth < excepted_bandwidth
                    break
                else:
#                     if abs(bndwth - excepted_bandwidth) / excepted_bandwidth < 0.1:
                    if bndwth <= excepted_bandwidth or (bndwth - excepted_bandwidth) / excepted_bandwidth < 0.1:
                        actual_bandwidth = bndwth
                        break
                    else:
                        time.sleep(10)
            else:
                raise Exception('Execute command %s error: %s' % (cmd, ret))
        if not bndwth:
            test_util.test_fail("Get VIP bandwidth failed")
        if excepted_bandwidth < 1000 and actual_bandwidth == 0:
            test_util.test_fail('Except bandwidth: %s, actual bandwidth: %s.' % (excepted_bandwidth, bndwth))

    def check_outbound_bandwidth(self, vm_ip=None):
        if not vm_ip:
            vm_ip = self.vm_ip
        if self.iperf_port:
            if self.port:
                cmd = "iperf3 -c %s -p %s --cport %s --bind %s -t 5 -O 1 -R" % (self.vip_ip, self.iperf_port, self.port, self.mn_ip)
            else:
                cmd = "iperf3 -c %s -p %s -t 5 -O 1 -R " % (self.vip_ip, self.iperf_port)
        else:
            cmd = "iperf3 -c %s -t 5 -O 1 -R" % self.vip_ip
        self.check_bandwidth(vm_ip, 'out', cmd, self.outbound_width/(1024 * 1024))

    def check_inbound_bandwidth(self, vm_ip=None):
        if not vm_ip:
            vm_ip = self.vm_ip
        if self.iperf_port:
            if self.port:
                cmd = "iperf3 -c %s -p %s --cport %s --bind %s -t 5 -O 1 --get-server-output" % (self.vip_ip, self.iperf_port, self.port, self.mn_ip)
            else:
                cmd = "iperf3 -c %s -p %s -t 5 -O 1 --get-server-output" % (self.vip_ip, self.iperf_port)
        else:
            cmd = "iperf3 -c %s -t 5 -O 1 --get-server-output" % self.vip_ip
        self.check_bandwidth(vm_ip, 'in', cmd, self.inbound_width/(1024 * 1024))


class MulISO(object):
    def __init__(self):
        self.vm1 = None
        self.vm2 = None
        self.cdroms = None
        self.iso_uuids = None
        self.iso = [{'name': 'iso1', 'url': os.getenv('testIsoUrl')},
                    {'name': 'iso2', 'url': os.getenv('testIsoUrl')},
                    {'name': 'iso3', 'url': os.getenv('testIsoUrl')}]

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

    def create_vm(self, vm2=False, system_tags=["cdroms::Empty::Empty::Empty"]):
        self.vm1 = create_basic_vm(system_tags=system_tags, l3_name=os.environ.get('l3PublicNetworkName'))
        self.vm1.check()
        if vm2:
            self.vm2 = create_basic_vm(system_tags=system_tags, l3_name=os.environ.get('l3PublicNetworkName'))
            self.vm2.check()

    def clone_vm(self):
        self.cloned_vm = self.vm1.clone(['cloned-vm1'])
        self.vm1 = self.cloned_vm[0]
        self.vm1.check()

    def create_windows_vm(self, system_tags=["cdroms::Empty::Empty::Empty"]):
        new_offering = test_lib.lib_create_instance_offering(cpuNum = 6, memorySize = 2048 * 1024 * 1024)
        new_offering_uuid = new_offering.uuid
        self.vm1 = create_windows_vm_2(instance_offering_uuid = new_offering_uuid, system_tags=system_tags)
        vm_ops.delete_instance_offering(new_offering_uuid)

    def attach_iso(self, iso_uuid, vm_uuid=None):
        if not vm_uuid:
            vm_uuid = self.vm1.vm.uuid
        img_ops.attach_iso(iso_uuid, vm_uuid)
        self.check_vm_systag(iso_uuid, vm_uuid)
        time.sleep(5)

    def detach_iso(self, iso_uuid, vm_uuid=None):
        if not vm_uuid:
            vm_uuid = self.vm1.vm.uuid
        img_ops.detach_iso(vm_uuid, iso_uuid)
        self.check_vm_systag(iso_uuid, vm_uuid, attach=False)
        time.sleep(5)

    def set_iso_first(self, iso_uuid, vm_uuid=None):
        if not vm_uuid:
            vm_uuid = self.vm1.vm.uuid
        cond = res_ops.gen_query_conditions('vmInstanceUuid', '=', vm_uuid)
        cdroms = cdrom_ops.query_vm_cdrom(cond)
        cdrom_uuid = [cdrom.uuid for cdrom in cdroms if cdrom.isoUuid == iso_uuid][0]
        cdrom_ops.set_default_cdrom(vm_uuid, cdrom_uuid)
#         system_tags = ['iso::%s::0' % iso_uuid]
#         vm_ops.update_vm(vm_uuid, system_tags=system_tags)

    def check_vm_systag(self, iso_uuid, vm_uuid=None, attach=True, order=None):
        if not vm_uuid:
            vm_uuid = self.vm1.vm.uuid
        cond = res_ops.gen_query_conditions('vmInstanceUuid', '=', vm_uuid)
        self.cdroms = cdrom_ops.query_vm_cdrom(cond)
        iso_orders = {cdrom.isoUuid: str(cdrom.deviceId) for cdrom in self.cdroms if cdrom.isoUuid}
#         systags = res_ops.query_resource(res_ops.SYSTEM_TAG, cond)
#         iso_orders = {t.tag.split('::')[-2]: t.tag.split('::')[-1] for t in systags if 'iso' in t.tag}
        if attach:
            assert iso_uuid in iso_orders
        else:
            assert iso_uuid not in iso_orders
        if order:
            assert iso_orders[iso_uuid] == order

    def check_cdrom_not_exist(self):
        for cdrom in self.cdroms:
            cond = res_ops.gen_query_conditions('uuid', '=', cdrom.uuid)
            assert not cdrom_ops.query_vm_cdrom(cond)

    def del_cdrom(self, num=1, vm_uuid=None):
        if not vm_uuid:
            vm_uuid = self.vm1.vm.uuid
        cond = res_ops.gen_query_conditions('vmInstanceUuid', '=', vm_uuid)
        cdroms = cdrom_ops.query_vm_cdrom(cond)
        if num > len(cdroms):
            test_util.test_fail("The number of cdrom to be deleted is greater than its actually cdroms")
        for _ in range(num):
            cdrom_ops.del_vm_cdrom(cdroms.pop().uuid)

    def create_cdrom(self, vm_uuid=None, iso_uuid=None):
        if not vm_uuid:
            vm_uuid = self.vm1.vm.uuid
        cdrom_ops.create_vm_cdrom('new_cdrom', vm_uuid, iso_uuid=iso_uuid)

    def check_vm_cdrom(self, no_media_cdrom=0, check=False):
        actual_no_media_cdrom = 0
        vm_ip = self.vm1.vm.vmNics[0].ip
        for i in range(3):
            cmd_mount = 'sshpass -p password ssh -o StrictHostKeyChecking=no root@%s "umount -f /mnt &> /dev/null;mount /dev/sr%s /mnt"' % (vm_ip, i)
            _ret = commands.getoutput(cmd_mount)
            ret = _ret.split('\n')[-1]
            if 'no medium found' in ret:
                actual_no_media_cdrom += 1
        if check:
            assert actual_no_media_cdrom == no_media_cdrom

    def check_cdroms_number(self, num=1):
        cmd_cdrom = 'sshpass -p password ssh -o LogLevel=quiet -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@%s "ls /dev/ | grep sr | wc -l"' % self.vm1.vm.vmNics[0].ip
        assert int(commands.getoutput(cmd_cdrom)) == num

    def add_route_to_bridge(self, l3_uuid):
        cond = res_ops.gen_query_conditions('uuid', '=', l3_uuid)
        l3_inv = res_ops.query_resource(res_ops.L3_NETWORK, cond)[0]

        l3_cidr = l3_inv.ipRanges[0].networkCidr
        l2_uuid = l3_inv.l2NetworkUuid
        cond = res_ops.gen_query_conditions('uuid', '=', l2_uuid)
        l2_inv = res_ops.query_resource(res_ops.L2_NETWORK, cond)[0]
        vlan_id = l2_inv.vlan

        del_route_cmd = "ip addr del " + l3_cidr + " dev br_eth0_" + str(vlan_id)
        test_util.test_logger(del_route_cmd)
        os.system(del_route_cmd)

        add_route_cmd = "ip addr add " + l3_cidr + " dev br_eth0_" + str(vlan_id)
        test_util.test_logger(add_route_cmd)
        os.system(add_route_cmd)

    def get_wmic_volumenames(self, vm_ip):
        vm_username = os.environ.get('winImageUsername')
        vm_password = os.environ.get('winImagePassword')
        for i in range(15):
            try:
                tn = telnetlib.Telnet(vm_ip, timeout=120)
                tn.read_until("login: ", 30)
                tn.write(vm_username+"\r\n")

                tn.read_until("password: ", 30)
                tn.write(vm_password+"\r\n")
                tn.read_until(vm_username + ">", 30)
                tn.write("wmic cdrom get volumename\r\n")
                ret = tn.read_until(vm_username + ">", 30)
                if ret:
                    tn.write("exit\r\n")
                    tn.close()
                    break
                else:
                    tn.close()
            except:
                test_util.test_logger("retry id: %s" %(int(i)))
                time.sleep(5)
                continue
        cdrome_list = ret.split('\r')
        test_util.test_logger(ret)
        _cdroms_with_media = [x.strip('\n| ') for x in cdrome_list if x.strip('\n| ')][2:-1]
        test_util.test_logger(_cdroms_with_media)
        return len(_cdroms_with_media)

    def check_windows_vm_cdrom(self, cdroms_with_media):
        vm_ip = self.vm1.get_vm().vmNics[0].ip
        l3_uuid = test_lib.lib_get_l3s_uuid_by_vm(self.vm1.get_vm())[0]
        self.add_route_to_bridge(l3_uuid)

        for r in range(2):
            test_lib.lib_wait_target_up(vm_ip, '23', 1200)
            for _ in range(10):
                actual_cdroms_with_media = self.get_wmic_volumenames(vm_ip)
                if actual_cdroms_with_media == cdroms_with_media:
                    break
                else:
                    time.sleep(15)
            else:
                self.vm1.reboot()
        assert actual_cdroms_with_media == cdroms_with_media


class Longjob(object):
    def __init__(self):
        self.vm = None
        self.image_uuid = None
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
        self.vm = create_basic_vm()

    def create_data_volume(self, ceph_pool=None):
        disk_offering = test_lib.lib_get_disk_offering_by_name(os.getenv('rootDiskOfferingName'))
        ps_uuid = self.vm.vm.allVolumes[0].primaryStorageUuid
        volume_option = test_util.VolumeOption()
        volume_option.set_disk_offering_uuid(disk_offering.uuid)
        volume_option.set_name('data-volume-for-crt-image-test')
        if ceph_pool:
            volume_option.set_system_tags(["ceph::pool::%s" % ceph_pool])
            volume_option.set_primary_storage_uuid(ps_uuid)
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
        cond_longjob = res_ops.gen_query_conditions('apiId', '=', long_job.apiId)
        progress_set = set()
        for _ in xrange(600):
            progress_inv = res_ops.get_task_progress(long_job.apiId).inventories
            if not progress_inv:
                time.sleep(3)
                continue
            else:
                progress = progress_inv[0].content
                progress_set.add(progress)
                if '100' in progress or 'image cache' in progress:
                    break
                else:
                    time.sleep(3)
        progress_list = [int(i) for i in progress_set if len(i) <= 3]
        progress_list.sort()
        if self.target_bs.type != inventory.SFTP_BACKUP_STORAGE_TYPE:
            test_util.test_dsc("Task Progress History: %s" % progress_list)
            assert progress_list, 'Get task progress failed!'
        time.sleep(10)
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
        self.image_uuid = image_inv[0].uuid

    def add_image(self):
        name = "longjob_image"
        bs = res_ops.query_resource(res_ops.BACKUP_STORAGE)
        self.target_bs = bs[random.randint(0, len(bs) - 1)]
        job_data = '{"name":"%s", "url":"%s", "mediaType"="RootVolumeTemplate", "format"="qcow2", "platform"="Linux", \
        "backupStorageUuids"=["%s"]}' % (self.image_add_name, self.url, self.target_bs.uuid)
        self.submit_longjob(job_data, name, job_type='image')

    def delete_image(self):
        try:
            img_ops.delete_image(self.image_uuid, backup_storage_uuid_list=[self.target_bs.uuid])
        except:
            pass

    def crt_vm_image(self, target_bs=None):
        name = 'longjob_crt_vol_image'
        bs = res_ops.query_resource(res_ops.BACKUP_STORAGE)
        if not target_bs:
            self.target_bs = bs[random.randint(0, len(bs) - 1)]
        else:
            self.target_bs = target_bs
        job_data = '{"name"="%s", "guestOsType":"Linux","system"="false","platform"="Linux","backupStorageUuids"=["%s"], \
        "rootVolumeUuid"="%s"}' % (self.vm_create_image_name, self.target_bs.uuid, self.vm.vm.rootVolumeUuid)
        self.submit_longjob(job_data, name, job_type='crt_vm_image')

    def crt_vol_image(self):
        name = 'longjob_crt_vol_image'
        bs = res_ops.query_resource(res_ops.BACKUP_STORAGE)
        self.target_bs = bs[random.randint(0, len(bs) - 1)]
        job_data = '{"name"="%s", "guestOsType":"Linux","system"="false","platform"="Linux","backupStorageUuids"=["%s"], \
        "volumeUuid"="%s"}' %(self.vol_create_image_name, self.target_bs.uuid, self.data_volume.get_volume().uuid)
        self.submit_longjob(job_data, name, job_type='crt_vol_image')


def disable_all_pss():
    ps_list = res_ops.query_resource(res_ops.PRIMARY_STORAGE)
    for ps in ps_list:
        ps_uuid = ps.uuid
        ps_ops.change_primary_storage_state(ps_uuid, 'disable')


def maintain_all_pss():
    ps_list = res_ops.query_resource(res_ops.PRIMARY_STORAGE)
    for ps in ps_list:
        ps_uuid = ps.uuid
        ps_ops.change_primary_storage_state(ps_uuid, 'maintain')


def enable_all_pss():
    ps_list = res_ops.query_resource(res_ops.PRIMARY_STORAGE)
    for ps in ps_list:
        ps_uuid = ps.uuid
        ps_ops.change_primary_storage_state(ps_uuid, 'enable')

CEPHPOOLTESTIMAGENAME = 'ceph_pool_capacity_test_image'
CEPHPOOLTESTISONAME = 'ceph_pool_capacity_test_iso'

class PoolCapacity(Longjob):
    def __init__(self, poolName=None, replicatedSize=None, crushRuleSet=None):
        super(PoolCapacity, self).__init__()
        self.vm = None
        self.data_volume = None
        self.bs = None
        self.image = None
        self.pool = None
        self.pool_name = 'data-pool-' + str(time.time()).replace('.', '-')
        self.poolName = poolName
        self.replicatedSize = replicatedSize
        self.crushRuleSet = crushRuleSet
        self.availableCapacity = 0
        self.usedCapacity = 0
        self.crushRuleItemName = None
        self.crushItemOsds = []
        self.crushItemOsdsTotalSize = 0
        self.poolTotalSize = 0

    def get_ceph_pools_cap(self, ceph_mon_cmd):
        result = []
        o = shell.call(ceph_mon_cmd + ' ceph osd dump -f json')
        df = jsonobject.loads(o)
        if not df.pools:
            return result
        for pool in df.pools:
            crush_rule = None
            if pool.crush_ruleset is None:
                crush_rule = pool.crush_rule
            else:
                crush_rule = pool.crush_ruleset
            poolCapacity = PoolCapacity(pool.pool_name, pool.size, crush_rule)
            result.append(poolCapacity)
        # fill crushRuleItemName
        o = shell.call(ceph_mon_cmd + ' ceph osd crush rule dump -f json')
        crushRules = jsonobject.loads(o)
        if not crushRules:
            return result
        for poolCapacity in result:
            if poolCapacity.crushRuleSet is None:
                continue
            def setCrushRuleName(crushRule):
                if not crushRule:
                    return
                for step in crushRule.steps:
                    if step.op == "take":
                        poolCapacity.crushRuleItemName = step.item_name
            [setCrushRuleName(crushRule) for crushRule in crushRules if crushRule.rule_id == poolCapacity.crushRuleSet]
        # fill crushItemOsds
        o = shell.call(ceph_mon_cmd + ' ceph osd tree -f json')
        tree = jsonobject.loads(o)
        if not tree.nodes:
            return result
        def findNodeById(id):
            for node in tree.nodes:
                if node.id == id:
                    return node
        def findAllChilds(node):
            childs = []
            if not node.children:
                return childs
            for childId in node.children:
                child = findNodeById(childId)
                if not child:
                    continue
                childs.append(child)
                if child.children:
                    grandson_childs = findAllChilds(child)
                    childs.extend(grandson_childs)
            return childs
        for poolCapacity in result:
            if not poolCapacity.crushRuleItemName:
                continue
            for node in tree.nodes:
                if node.name != poolCapacity.crushRuleItemName:
                    continue
                if not node.children:
                    continue
                osdNodes = []
                nodes = findAllChilds(node)
                for node in nodes:
                    if node.type != "osd":
                        continue
                    if node.name in osdNodes:
                        continue
                    osdNodes.append(node.name)
                poolCapacity.crushItemOsds = osdNodes
        # fill crushItemOsdsTotalSize, poolTotalSize
        o = shell.call(ceph_mon_cmd + ' ceph osd df -f json')
        osds = jsonobject.loads(o)
        if not osds.nodes:
            return result
        for poolCapacity in result:
            if not poolCapacity.crushItemOsds:
                continue
            for osdName in poolCapacity.crushItemOsds:
                for osd in osds.nodes:
                    if osd.name != osdName:
                        continue
                    poolCapacity.crushItemOsdsTotalSize = poolCapacity.crushItemOsdsTotalSize + osd.kb * 1024
                    poolCapacity.availableCapacity = poolCapacity.availableCapacity + osd.kb_avail * 1024
                    poolCapacity.usedCapacity = poolCapacity.usedCapacity + osd.kb_used * 1024
            if poolCapacity.crushItemOsdsTotalSize != 0 and poolCapacity.replicatedSize != 0:
                poolCapacity.poolTotalSize = poolCapacity.crushItemOsdsTotalSize / poolCapacity.replicatedSize
            if poolCapacity.availableCapacity != 0 and poolCapacity.replicatedSize != 0:
                poolCapacity.availableCapacity = poolCapacity.availableCapacity / poolCapacity.replicatedSize
            if poolCapacity.usedCapacity != 0 and poolCapacity.replicatedSize != 0:
                poolCapacity.usedCapacity = poolCapacity.usedCapacity / poolCapacity.replicatedSize
        return result

    def get_bs(self, bs_type='Ceph'):
        cond_bs_type = res_ops.gen_query_conditions('type', '=', bs_type)
        self.bs = res_ops.query_resource(res_ops.BACKUP_STORAGE, cond_bs_type)[0]

    def add_image(self, bs_type='Ceph', name=CEPHPOOLTESTIMAGENAME, image_format='qcow2', media_type='RootVolumeTemplate', image='imageUrl_net'):
        self.get_bs(bs_type)
        image_option = test_util.ImageOption()
        image_option.set_name(name)
        image_option.set_format(image_format)
        image_option.set_mediaType(media_type)
        image_option.set_url(os.environ.get(image))
        image_option.set_backup_storage_uuid_list([self.bs.uuid])
        self.image = test_image.ZstackTestImage()
        self.image.set_creation_option(image_option)
        self.image.add_root_volume_template()

    def del_image(self):
        self.image.delete()
        if test_lib.lib_get_image_delete_policy() != 'Direct':
            self.image.expunge()

    def get_pool_cap_remote(self, pool_name):
        self.used_cap = None
        self.avail_cap = None
        self.get_bs()
        mon_ip = self.bs.mons[0].monAddr
        login_cmd = "sshpass -p password ssh -o StrictHostKeyChecking=no root@%s" % mon_ip
        ret = self.get_ceph_pools_cap(login_cmd)
        for poolCap in ret:
            if poolCap.poolName == pool_name:
                self.used_cap = str(poolCap.usedCapacity)
                self.avail_cap = str(poolCap.availableCapacity)
#         used_cmd = "sshpass -p password ssh -o StrictHostKeyChecking=no root@%s ceph df | grep %s | awk '{print $3}'" % (mon_ip, pool_name)
#         avail_cmd = "sshpass -p password ssh -o StrictHostKeyChecking=no root@%s ceph df | grep %s | awk '{print $5}'" % (mon_ip, pool_name)
#         self.used_cap = commands.getoutput(used_cmd).split('\n')[-1]
#         self.avail_cap = commands.getoutput(avail_cmd).split('\n')[-1]

    def get_replicated_size(self):
        cmd = "sshpass -p password ssh -o StrictHostKeyChecking=no root@%s ceph osd pool get %s size | awk '{print $2}'" % (self.bs.mons[0].monAddr, self.bs.poolName)
        self.size = int(commands.getoutput(cmd).split('\n')[-1])

    def check_pool_replicated_size(self):
        self.get_bs()
        assert self.bs.poolReplicatedSize == self.size

    def get_ceph_pool(self, pool_type, pool_name=None):
        cond_pool_type = res_ops.gen_query_conditions('type', '=', pool_type)
        cond_pool_name = res_ops.gen_query_conditions('poolName', '=', pool_name)
        if not pool_name:
            self.pool = res_ops.query_resource(res_ops.CEPH_PRIMARY_STORAGE_POOL, cond_pool_type)[0]
        else:
            self.pool = res_ops.query_resource(res_ops.CEPH_PRIMARY_STORAGE_POOL, cond_pool_name)[0]

    def check_pool_cap(self, cap, pool_name=None, bs=False):
        if bs:
            pool_name = self.bs.poolName
        self.get_pool_cap_remote(pool_name)
        test_util.test_dsc('%s, %s, %s' % (cap, self.used_cap, self.avail_cap))
        if 'M' in self.used_cap:
            assert cap[0] // 1024 //1024 == int(self.used_cap[:-1])
        elif 'k' in self.used_cap:
            assert cap[0] // 1024 == int(self.used_cap[:-1])
        elif 'G' in self.used_cap:
            assert cap[0] // 1024 //1024 // 1024 == int(self.used_cap[:-1])
        else:
            assert cap[0] / 1024 / 1024 == int(self.used_cap) / 1024 / 1024
#             assert cap[0] == int(self.used_cap)
        if 'M' in self.avail_cap:
            assert cap[1] // 1024 //1024 == int(self.avail_cap[:-1])
        elif 'k' in self.avail_cap:
            assert cap[1] // 1024 == int(self.avail_cap[:-1])
        elif 'G' in self.avail_cap:
            assert cap[1] // 1024 //1024 // 1024 == int(self.avail_cap[:-1])
        else:
            assert cap[1] / 1024 / 1024 == int(self.avail_cap) / 1024 / 1024
#             assert cap[1] == int(self.avail_cap)

    def attach_iso(self):
        image_uuid = test_lib.lib_get_image_by_name('ceph_pool_capacity_test_iso').uuid
        img_ops.attach_iso(image_uuid, self.vm.vm.uuid)

    def add_ceph_ps_pool(self):
        ps = res_ops.query_resource(res_ops.CEPH_PRIMARY_STORAGE)[0]
        ps_ops.add_ceph_primary_storage_pool(ps.uuid, self.pool_name, isCreate='true')

class BATCHDELSP(TestChain):
    def __init__(self, chain_head=None, chain_length=20):
        self.sp_tree = test_util.SPTREE()
        self.test_obj_dict = None
        self.vm = None
        self.data_volume = None
        self.vol_uuid = None
        self.snapshots = None
        self.snapshot = []
        self.sp_type = 'Hypervisor'
        super(BATCHDELSP, self).__init__(chain_head, chain_length)

    def create_vm(self):
        '''
        {"next": ["create_sp", "revert_sp"]}
        '''
        self.vm = create_basic_vm(l3_name=os.environ.get('l3PublicNetworkName'))
        self.vm.check()
        return self

    def set_ceph_mon_env(self, ps_uuid):
        cond_vol = res_ops.gen_query_conditions('uuid', '=', ps_uuid)
        ps = res_ops.query_resource(res_ops.PRIMARY_STORAGE, cond_vol)[0]
        if ps.type.lower() == 'ceph':
            ps_mon_ip = ps.mons[0].monAddr
            os.environ['cephBackupStorageMonUrls'] = 'root:password@%s' % ps_mon_ip
        return ps.type

    def create_data_volume(self, sharable=False, vms=[]):
        '''
        {"next": ["create_sp", "revert_sp"]}
        '''
        if not self.vm:
            self.create_vm()
        conditions = res_ops.gen_query_conditions('name', '=', os.getenv('rootDiskOfferingName'))
        disk_offering_uuid = res_ops.query_resource(res_ops.DISK_OFFERING, conditions)[0].uuid
        volume_option = test_util.VolumeOption()
        volume_option.set_disk_offering_uuid(disk_offering_uuid)
        ps_uuid = self.vm.vm.allVolumes[0].primaryStorageUuid
        volume_option.set_name('data_volume_for_batch_del_sp_test')
        volume_option.set_primary_storage_uuid(ps_uuid)
        ps_type = self.set_ceph_mon_env(ps_uuid)
        if ps_type == 'LocalStorage':
            volume_option.set_system_tags(['capability::virtio-scsi', 'localStorage::hostUuid::%s' % self.vm.vm.hostUuid])
        if sharable:
            volume_option.set_system_tags(['ephemeral::shareable', 'capability::virtio-scsi'])
        self.data_volume = create_volume(volume_option)
        if vms:
            for vm in vms:
                self.data_volume.attach(vm)
        else:
            self.data_volume.attach(self.vm)
        self.data_volume.check()
        test_lib.lib_mkfs_for_volume(self.data_volume.get_volume().uuid, self.vm.vm, '/mnt')
        return self

    def create_sp(self):
        '''
        {"next": ["create_sp", "revert_sp", "batch_del_sp"],
         "weight": 3}
        '''
        if not self.test_obj_dict:
            self.test_obj_dict = test_state.TestStateDict()
        self.test_obj_dict.add_vm(self.vm)
        if not self.data_volume:
            vol_uuid = self.vm.vm.rootVolumeUuid
        else:
            self.test_obj_dict.add_volume(self.data_volume)
            vol_uuid = self.data_volume.get_volume().uuid
        self.snapshots = self.test_obj_dict.get_volume_snapshot(vol_uuid) if self.vol_uuid != vol_uuid else self.snapshots
        self.vol_uuid = vol_uuid
        self.snapshots.set_utility_vm(self.vm)
        self.snapshots.create_snapshot('snapshot-%s' % time.strftime('%m%d-%H%M%S', time.localtime()))
#         self.snapshots.check()
        curr_sp = self.snapshots.get_current_snapshot()
        self.snapshot.append(curr_sp)
        if curr_sp.get_snapshot().type == 'Storage':
            self.sp_type = curr_sp.get_snapshot().type
            if not self.sp_tree.root:
                self.sp_tree.add('root')
            self.sp_tree.revert(self.sp_tree.root)
        self.sp_tree.add(curr_sp.get_snapshot().uuid)
        self.sp_tree.show_tree()
        return self

    def sp_check(self):
        self.snapshots.check()
        return self

    def revert_sp(self, sp=None, start_vm=False):
        '''
        {"must":{"before": ["create_sp"]},
        "next": ["create_sp", "batch_del_sp"],
        "weight": 2}
        '''
        if self.data_volume:
            try:
                self.data_volume.detach()
            except:
                pass
        else:
            self.vm.stop()
        if not sp:
            sp = random.choice(self.snapshot)
        self.snapshots.use_snapshot(sp)
        if start_vm:
            self.vm.start()
            self.vm.check()
        if self.sp_type != 'Storage':
            self.sp_tree.revert(sp.get_snapshot().uuid)
        if self.data_volume:
            try:
                self.data_volume.attach(self.vm)
            except:
                pass
        self.sp_tree.show_tree()
        return self

    def batch_del_sp(self, snapshot_uuid_list=None, exclude_root=True):
        '''
        {"must":{"before": ["create_sp"]},
        "next": ["create_sp", "revert_sp"],
        "weight": 1}
        '''
        for _ in range(5):
            random.shuffle(self.snapshot)
        if not snapshot_uuid_list:
            snapshot_list = self.snapshot[:random.randint(2, len(self.snapshot))]
            snapshot_uuid_list = [spt.get_snapshot().uuid for spt in snapshot_list]
        spd = {_sp.get_snapshot().uuid: _sp for _sp in self.snapshot}
        if exclude_root:
            if self.sp_tree.root in snapshot_uuid_list:
                snapshot_uuid_list.remove(self.sp_tree.root)
        vol_ops.batch_delete_snapshot(snapshot_uuid_list)
        for spuuid in snapshot_uuid_list:
            assert not res_ops.query_resource(res_ops.VOLUME_SNAPSHOT, res_ops.gen_query_conditions('uuid', '=', spuuid)), \
            'The snapshot with uuid [%s] is still exist!' % spuuid
            if self.sp_tree.delete(spuuid):
                self.snapshots.delete_snapshot(spd[spuuid], False)
        remained_sp =  self.sp_tree.tree.keys()
        if self.sp_type == 'Storage':
            remained_sp.remove(self.sp_tree.root)
        for sud in spd.keys():
            if sud not in remained_sp:
                self.snapshot.remove(spd[sud])
        for sp_uuid in remained_sp:
            snapshot = res_ops.query_resource(res_ops.VOLUME_SNAPSHOT, res_ops.gen_query_conditions('uuid', '=', sp_uuid))
            assert snapshot, 'The snapshot with uuid [%s] was not found!' % sp_uuid
            if snapshot[0].parentUuid:
                assert snapshot[0].parentUuid == self.sp_tree.parent(sp_uuid)
        remained_sp_num = len(self.sp_tree.get_all_nodes())
        if self.sp_type == 'Storage':
            remained_sp_num -= 1
        if not self.data_volume:
            actual_sp_num = len(res_ops.query_resource(res_ops.VOLUME_SNAPSHOT, res_ops.gen_query_conditions('volumeUuid', '=', self.vm.get_vm().allVolumes[0].uuid)))
        else:
            actual_sp_num = len(res_ops.query_resource(res_ops.VOLUME_SNAPSHOT, res_ops.gen_query_conditions('volumeUuid', '=', self.data_volume.get_volume().uuid)))
        assert actual_sp_num == remained_sp_num, 'actual remained snapshots number: %s, snapshot number in sp tree: %s' % (actual_sp_num, remained_sp_num)
        self.sp_tree.show_tree()
        self.snapshots.check()
        return self
