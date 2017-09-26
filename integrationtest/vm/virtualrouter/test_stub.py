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
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.zstack_test.zstack_test_vm as zstack_vm_header
import zstackwoodpecker.zstack_test.zstack_test_volume as zstack_volume_header
import zstackwoodpecker.zstack_test.zstack_test_security_group as zstack_sg_header
import zstackwoodpecker.zstack_test.zstack_test_eip as zstack_eip_header
import zstackwoodpecker.zstack_test.zstack_test_vip as zstack_vip_header
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import apibinding.inventory as inventory
import random
import functools
from zstackwoodpecker.operations import vm_operations as vm_ops

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

def create_vlan_vm(l3_name=None, disk_offering_uuids=None, system_tags=None, session_uuid = None, instance_offering_uuid = None):
    image_name = os.environ.get('imageName_net')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    if not l3_name:
        l3_name = os.environ.get('l3VlanNetworkName1')

    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    return create_vm([l3_net_uuid], image_uuid, 'vlan_vm', \
            disk_offering_uuids, system_tags=system_tags, \
            instance_offering_uuid = instance_offering_uuid,
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

def create_windows_vm_2(l3_name=None, disk_offering_uuids=None, session_uuid = None, instance_offering_uuid = None):
    '''
        Create windows platform type vm.
    '''
    image_name = os.environ.get('imageName_windows')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    if not l3_name:
        #l3_name = 'guestL3VlanNetwork1'
        l3_name = os.environ.get('l3VlanNetworkName1')

    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    return create_vm([l3_net_uuid], image_uuid, 'windows_vm', disk_offering_uuids, instance_offering_uuid = instance_offering_uuid, session_uuid = session_uuid)

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

def create_basic_vm(disk_offering_uuids=None, session_uuid = None):
    image_name = os.environ.get('imageName_net')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    l3_name = os.environ.get('l3VlanNetworkName1')
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    return create_vm([l3_net_uuid], image_uuid, 'basic_no_vlan_vm', disk_offering_uuids, session_uuid = session_uuid)

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
        system_tags = None, instance_offering_uuid = None, session_uuid = None, ps_uuid=None):
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
    vm = zstack_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    return vm

def create_volume(volume_creation_option=None, session_uuid = None):
    if not volume_creation_option:
        disk_offering = test_lib.lib_get_disk_offering_by_name(os.environ.get('smallDiskOfferingName'))
        volume_creation_option = test_util.VolumeOption()
        volume_creation_option.set_disk_offering_uuid(disk_offering.uuid)
        volume_creation_option.set_name('vr_test_volume')

    volume_creation_option.set_session_uuid(session_uuid)
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
        vm.check = test_lib.checker_wrapper(vm, 'DHCP', vm.get_vm().vmNics[0].l3NetworkUuid)
        vm.check()
        tbj.add_vm(vm)

    return pub_l3_vm, flat_l3_vm, vr_l3_vm


def install_iperf(vm_inv):
    vm_ip = vm_inv.vmNics[0].ip

    ssh_cmd = 'ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm_ip
    cmd = '%s "wget http://dl.fedoraproject.org/pub/epel/7/x86_64/i/iperf-2.0.10-1.el7.x86_64.rpm; rpm -ivh iperf-2.0.10-1.el7.x86_64.rpm"' % (ssh_cmd)
    if execute_shell_in_process(cmd, 150) != 0:
        test_util.test_fail('fail to install iperf.')

def test_iperf_bandwidth(vm1_inv,vm2_inv,vip_ip,server_port,client_port,bandwidth,raise_exception=True):
    vm1_ip = vm1_inv.vmNics[0].ip
    vm2_ip = vm2_inv.vmNics[0].ip

    cmd1 = "sshpass -p 'password' ssh root@%s iperf -s -p %s | awk 'NR==7 {print $(NF-1)}'" % (vm1_ip, server_port)
    process1 = subprocess.Popen(cmd1, executable='/bin/sh', shell=True, stdout=subprocess.PIPE, universal_newlines=True)
    time.sleep(10)
    cmd2 = "iperf -c %s -p %s | awk 'NR==7 {print $(NF-1)}'" % (vip_ip, client_port)
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




