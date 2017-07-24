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
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import zstackwoodpecker.operations.scenario_operations as sce_ops
import zstackwoodpecker.header.host as host_header
import apibinding.inventory as inventory
import zstackwoodpecker.operations.primarystorage_operations as ps_ops
import zstacklib.utils.xmlobject as xmlobject
import threading
import time
import sys
import telnetlib
import random
#import traceback


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
    imagename = os.environ.get(image_name)
    l3name = os.environ.get(l3_name)

    return create_vm(vm_name, imagename, l3name)

def create_vm(vm_name, image_name, l3_name):
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
    vm = test_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    return vm

def create_vm_with_iso(vm_name, l3_name, session_uuid = None):
    img_option = test_util.ImageOption()
    img_option.set_name('fake_iso')
    root_disk_uuid = test_lib.lib_get_disk_offering_by_name(os.environ.get('mediumDiskOfferingName')).uuid
    bs_uuid = res_ops.query_resource_fields(res_ops.BACKUP_STORAGE, [], \
            session_uuid)[0].uuid
    img_option.set_backup_storage_uuid_list([bs_uuid])
    mn_ip = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].hostName
    img_option.set_url('http://%s:8080/zstack/static/zstack-dvd/ks.cfg' % (mn_ip))
    image_uuid = img_ops.add_iso_template(img_option).uuid

    vm_creation_option = test_util.VmOption()
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
    instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid
    vm_creation_option.set_l3_uuids([l3_net_uuid])
    vm_creation_option.set_root_disk_uuid(root_disk_uuid)
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_name(vm_name)
    vm = test_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    return vm

def create_iso_vm_with_random_offering(vm_name, l3_name=None, session_uuid=None, root_disk_uuid=None,
                                       instance_offering_uuid=None, host_uuid=None, disk_offering_uuids=None,
                                       root_password=None, ps_uuid=None, system_tags=None):
    img_option = test_util.ImageOption()
    img_option.set_name('fake_iso')
    bs_uuid = res_ops.query_resource_fields(res_ops.BACKUP_STORAGE, [], session_uuid)[0].uuid
    img_option.set_backup_storage_uuid_list([bs_uuid])
    mn_ip = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].hostName
    img_option.set_url('http://%s:8080/zstack/static/zstack-dvd/ks.cfg' % (mn_ip))
    image_uuid = img_ops.add_iso_template(img_option).uuid

    if l3_name:
        l3name = os.environ.get(l3_name)
        l3_net_uuid = test_lib.lib_get_l3_by_name(l3name).uuid
    else:
        l3_net_uuid = random.choice(res_ops.get_resource(res_ops.L3_NETWORK)).uuid

    if not root_disk_uuid:
        root_disk_uuid = test_lib.lib_get_disk_offering_by_name(os.environ.get('mediumDiskOfferingName')).uuid

    if not instance_offering_uuid:
        conf = res_ops.gen_query_conditions('type', '=', 'UserVM')
        instance_offering_uuid = random.choice(res_ops.query_resource(res_ops.INSTANCE_OFFERING, conf)).uuid

    vm_creation_option = test_util.VmOption()
    vm_creation_option.set_l3_uuids([l3_net_uuid])
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_name(vm_name)
    vm_creation_option.set_root_disk_uuid(root_disk_uuid)
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



def create_vm_with_random_offering(vm_name, image_name=None, l3_name=None, session_uuid=None,
                                   instance_offering_uuid=None, host_uuid=None, disk_offering_uuids=None,
                                   root_password=None, ps_uuid=None, system_tags=None):
    if image_name:
        imagename = os.environ.get(image_name)
        image_uuid = test_lib.lib_get_image_by_name(imagename).uuid
    else:
        image_uuid = random.choice(res_ops.get_resource(res_ops.IMAGE)).uuid

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


def create_multi_vms(name_prefix='', count=10, host_uuid=None, ps_uuid=None, data_volume_number=0, ps_uuid_for_data_vol=None):
    vm_list = []
    for i in xrange(count):
        if not data_volume_number:
            vm = create_vm_with_random_offering(name_prefix+"{}".format(i), image_name='imageName_net',
                                                l3_name='l3VlanNetwork2', host_uuid=host_uuid, ps_uuid=ps_uuid)
        else:
            disk_offering_list = res_ops.get_resource(res_ops.DISK_OFFERING)
            disk_offering_uuids = [random.choice(disk_offering_list).uuid for _ in xrange(data_volume_number)]
            if ps_uuid_for_data_vol:
                vm = create_vm_with_random_offering(name_prefix+"{}".format(i), image_name='imageName_net',
                                                    l3_name='l3VlanNetwork2', host_uuid=host_uuid, ps_uuid=ps_uuid,
                                                    disk_offering_uuids=disk_offering_uuids,
                                                    system_tags=['primaryStorageUuidForDataVolume::{}'.format(ps_uuid_for_data_vol)])
            else:
                vm = create_vm_with_random_offering(name_prefix+"{}".format(i), image_name='imageName_net',
                                                    l3_name='l3VlanNetwork2', host_uuid=host_uuid, ps_uuid=ps_uuid,
                                                    disk_offering_uuids=disk_offering_uuids)

        vm_list.append(vm)
    for vm in vm_list:
        vm.check()
    if host_uuid:
        for vm in vm_list:
            assert vm.get_vm().hostUuid == host_uuid
    if ps_uuid:
        for vm in vm_list:
            root_volume = test_lib.lib_get_root_volume(vm.get_vm())
            assert root_volume.primaryStorageUuid == ps_uuid

    if ps_uuid_for_data_vol:
        for vm in vm_list:
            data_volume_list = [volume for volume in vm.get_vm().allVolumes if volume.type != 'Root']
            for data_volume in data_volume_list:
                assert data_volume.primaryStorageUuid == ps_uuid_for_data_vol

    return vm_list


def create_multi_volume(count=10, host_uuid=None, ps=None):
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

def add_primaryStorage(first_ps=None):
    cluster_uuid = first_ps.attachedClusterUuids[0]
    ps_config = test_util.PrimaryStorageOption()
    if first_ps.type == inventory.LOCAL_STORAGE_TYPE:
        ps_config.set_name("local-ps2")
        ps_config.set_description("test")
        ps_config.set_zone_uuid(first_ps.zoneUuid)
        ps_config.set_type(first_ps.type)
        ps_config.set_url("/home/local-ps2")

    ps = ps_ops.create_local_primary_storage(ps_config)
    ps_ops.attach_primary_storage(ps.uuid, cluster_uuid)
    ps.attachedClusterUuids.append(cluster_uuid)
    return ps



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

def create_sg(sg_creation_option=None):
    if not sg_creation_option:
        sg_creation_option = test_util.SecurityGroupOption()
        sg_creation_option.set_name('test_sg')
        sg_creation_option.set_description('test sg description')

    sg = zstack_sg_header.ZstackTestSecurityGroup()
    sg.set_creation_option(sg_creation_option)
    sg.create()
    return sg

def create_delete_account(account_name='test', session_uuid=None):
    try:
        account_inv = acc_ops.create_normal_account(account_name, 'password', session_uuid)
    except:
	test_util.test_logger('ignore exception')
    try:
        acc_ops.delete_account(account_inv.uuid, session_uuid)
    except:
        test_util.test_logger('ignore exception')

def exercise_connection(ops_num=120, thread_threshold=10):
    session_uuid = acc_ops.login_as_admin()
    for ops_id in range(ops_num):
        thread = threading.Thread(target=create_delete_account, args=(ops_id, session_uuid, ))
        while threading.active_count() > thread_threshold:
            time.sleep(0.5)
        exc = sys.exc_info()
        thread.start()

    while threading.activeCount() > 1:
        exc = sys.exc_info()
        time.sleep(0.1)
    acc_ops.logout(session_uuid)


def check_cpu_mem(vm, shutdown=False, window=False):
    zone_uuid = vm.get_vm().zoneUuid

    available_cpu, available_memory = check_available_cpu_mem(zone_uuid)
    vm_outer_cpu, vm_outer_mem = vm.get_vm().cpuNum, vm.get_vm().memorySize
    vm_internal_cpu, vm_internal_mem = check_vm_internal_cpu_mem(vm, shutdown, window)

    return available_cpu, available_memory, vm_outer_cpu, vm_outer_mem, vm_internal_cpu, vm_internal_mem


def check_available_cpu_mem(zone_uuid):
    available_cpu = test_lib.lib_get_cpu_memory_capacity([zone_uuid]).availableCpu
    available_memory = test_lib.lib_get_cpu_memory_capacity([zone_uuid]).availableMemory
    return available_cpu, available_memory


def check_window_vm_internal_cpu_mem(vm):
    vm_ip = vm.get_vm().vmNics[0].ip
    test_lib.lib_wait_target_up(vm_ip, '23', 360)
    vm_username = os.environ.get('winImageUsername')
    vm_password = os.environ.get('winImagePassword')
    tn=telnetlib.Telnet(vm_ip)
    tn.read_until("login: ")
    tn.write(vm_username+"\r\n")
    tn.read_until("password: ")
    tn.write(vm_password+"\r\n")
    tn.read_until(vm_username+">")
    tn.write("wmic cpu get NumberOfCores\r\n")
    vm_cpuinfo=tn.read_until(vm_username+">")
    tn.write("wmic computersystem get TotalPhysicalMemory\r\n")
    vm_meminfo=tn.read_until(vm_username+">")
    tn.close()
    test_util.test_logger(vm_cpuinfo.strip().split()[-2])
    test_util.test_logger(vm_meminfo.strip().split()[-2])
    return int(vm_cpuinfo.strip().split()[-2]), int(vm_meminfo.strip().split()[-2])/1024/1024


def check_vm_internal_cpu_mem(vm, shutdown, window):
    if window:
        return check_window_vm_internal_cpu_mem(vm)
    managerip = test_lib.lib_find_host_by_vm(vm.get_vm()).managementIp
    vm_ip = vm.get_vm().vmNics[0].ip
    get_cpu_cmd = "cat /proc/cpuinfo| grep 'processor'| wc -l"
    if not shutdown:
        get_mem_cmd = "free -m |grep Mem"
    else:
        get_mem_cmd = "dmidecode -t 17 | grep 'Size:'"
    res = test_lib.lib_ssh_vm_cmd_by_agent(managerip, vm_ip, 'root',
                'password', get_cpu_cmd)
    vm_cpu = int(res.result.strip())
    res = test_lib.lib_ssh_vm_cmd_by_agent(managerip, vm_ip, 'root',
                'password', get_mem_cmd)
    vm_mem = int(res.result.split()[1])
    return vm_cpu, vm_mem


class TwoPrimaryStorageEnv(object):
    def __init__(self, test_object_dict, first_ps_vm_number=0, second_ps_vm_number=0, first_ps_volume_number=0, second_ps_volume_number=0,
                 vm_creation_with_volume_number=0):
        self.first_ps_vm_number = first_ps_vm_number
        self.second_ps_vm_number = second_ps_vm_number
        self.first_ps_volume_number = first_ps_volume_number
        self.second_ps_volume_number = second_ps_volume_number
        self.vm_creation_with_volume_number = vm_creation_with_volume_number
        self.test_object_dict = test_object_dict
        self.host_uuid = None
        self.first_ps = None
        self.second_ps = None
        self.first_ps_vm_list = []
        self.second_ps_vm_list = []
        self.first_ps_volume_list = []
        self.second_ps_volume_list = []
        self.new_ps = False

    def check_env(self):
        ps_list = res_ops.get_resource(res_ops.PRIMARY_STORAGE)
        self.first_ps = ps_list[0]
        if len(ps_list) == 2:
            self.second_ps = ps_list[1]
        if self.first_ps.type == inventory.LOCAL_STORAGE_TYPE:
            self.host_uuid = random.choice(res_ops.get_resource(res_ops.HOST)).uuid

    def deploy_env(self):
        if self.first_ps_vm_number:
            self.first_ps_vm_list = create_multi_vms(name_prefix="vm_in_first_ps-", count=self.first_ps_vm_number,
                                                     host_uuid=self.host_uuid, ps_uuid=self.first_ps.uuid,
                                                     data_volume_number=self.vm_creation_with_volume_number)
            for vm in self.first_ps_vm_list:
                self.test_object_dict.add_vm(vm)

        if self.first_ps_volume_number:
            self.first_ps_volume_list = create_multi_volume(count=self.first_ps_volume_number, host_uuid=self.host_uuid,
                                                            ps=self.first_ps)
            for volume in self.first_ps_volume_list:
                self.test_object_dict.add_volume(volume)

        if not self.second_ps:
            self.second_ps = add_primaryStorage(self.first_ps)
            self.new_ps = True

        if self.second_ps_vm_number:
            self.second_ps_vm_list = create_multi_vms(name_prefix="vm_in_second_ps-", count=self.second_ps_vm_number,
                                                      host_uuid=self.host_uuid, ps_uuid=self.second_ps.uuid)
            for vm in self.second_ps_vm_list:
                self.test_object_dict.add_vm(vm)

        if self.second_ps_volume_number:
            self.second_ps_volume_list = create_multi_volume(count=self.second_ps_volume_number, host_uuid=self.host_uuid,
                                                             ps=self.second_ps)
            for volume in self.second_ps_volume_list:
                self.test_object_dict.add_volume(volume)

    def get_vm_list_from_ps(self, ps):
        if ps is self.first_ps:
            return self.first_ps_vm_list
        elif ps is self.second_ps:
            return self.second_ps_vm_list
        else:
            raise NameError


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


def get_ps_vm_creation():
    if find_ps_local() and find_ps_nfs():
        return find_ps_local(), find_ps_nfs()
    else:
        return random.sample(res_ops.get_resource(res_ops.PRIMARY_STORAGE), 2)


def check_vm_running_on_host(vm_uuid, host_ip):
    cmd = "virsh list|grep %s|awk '{print $3}'" %(vm_uuid)
    host_username = os.environ.get('hostUsername')
    host_password = os.environ.get('hostPassword')
    vm_is_exist = True if test_lib.lib_execute_ssh_cmd(host_ip, host_username, host_password, cmd) else False

    return vm_is_exist

def stop_host(host_vm, scenarioConfig, force=None):
    host_vm_uuid = host_vm.uuid_
    mn_ip = scenarioConfig.basicConfig.zstackManagementIp.text_
    try:
        host_inv = sce_ops.stop_vm(mn_ip, host_vm_uuid,force=force)
        test_lib.lib_wait_target_down(mn_ip, '22', 120)
        return host_inv
    except:
        test_util.test_logger("Fail to stop host [%s]" % host_vm.ip_)
        return False

def start_host(host_vm, scenarioConfig):
    host_vm_uuid = host_vm.uuid_
    mn_ip = scenarioConfig.basicConfig.zstackManagementIp.text_
    try:
        host_inv = sce_ops.start_vm(mn_ip, host_vm_uuid)
        return host_inv
    except:
        test_util.test_logger("Fail to start host [%s]" % host_vm.ip_)
        return False

def recover_host(host_vm, scenarioConfig, deploy_config):
    stop_host(host_vm, scenarioConfig)
    host_inv = start_host(host_vm, scenarioConfig)
    if not host_inv:
       return False
    recover_host_vlan(host_vm, scenarioConfig, deploy_config)

def recover_host_vlan(host_vm, scenarioConfig, deploy_config):
    host_ip = host_vm.ip_
    test_lib.lib_wait_target_up(host_ip, '22', 120)
    host_config = sce_ops.get_scenario_config_vm(host_vm.name_,scenarioConfig)
    for l3network in xmlobject.safe_list(host_config.l3Networks.l3Network):
        if hasattr(l3network, 'l2NetworkRef'):
            for l2networkref in xmlobject.safe_list(l3network.l2NetworkRef):
                nic_name = sce_ops.get_ref_l2_nic_name(l2networkref.text_, deploy_config)
                if nic_name.find('.') >= 0 :
                    vlan = nic_name.split('.')[1]
                    test_util.test_logger('[vm:] %s %s is created.' % (host_ip, nic_name.replace("eth", "zsn")))
                    cmd = 'vconfig add %s %s' % (nic_name.split('.')[0].replace("eth", "zsn"), vlan)
                    test_lib.lib_execute_ssh_cmd(host_ip, host_config.imageUsername_, host_config.imagePassword_, cmd)
    return True

host_username = os.environ.get('physicalHostUsername')
host_password = os.environ.get('physicalHostPassword')
host_password2 = os.environ.get('physicalHostPassword2')

def down_host_network(host_ip, scenarioConfig):
    zstack_management_ip = scenarioConfig.basicConfig.zstackManagementIp.text_
    cond = res_ops.gen_query_conditions('vmNics.ip', '=', host_ip)
    host_vm_inv = sce_ops.query_resource(zstack_management_ip, res_ops.VM_INSTANCE, cond).inventories[0]
    cond = res_ops.gen_query_conditions('uuid', '=', host_vm_inv.hostUuid)
    host_inv = sce_ops.query_resource(zstack_management_ip, res_ops.HOST, cond).inventories[0]

    host_vm_config = sce_ops.get_scenario_config_vm(host_vm_inv.name_, scenarioConfig)

    cmd = "virsh domiflist %s|sed -n '3p'|awk '{print $1}'|xargs -i virsh domif-setlink %s {} down" % (host_vm_inv.uuid, host_vm_inv.uuid)
    if test_lib.lib_execute_ssh_cmd(host_inv.managementIp, host_username, host_password, "pwd"):
        test_lib.lib_execute_ssh_cmd(host_inv.managementIp, host_username, host_password, cmd)
    elif test_lib.lib_execute_ssh_cmd(host_inv.managementIp, host_username, host_password2, "pwd"):
        test_lib.lib_execute_ssh_cmd(host_inv.managementIp, host_username, host_password2, cmd)
    else:
        test_util.test_fail("The candidate password are both not for the physical host %s, tried password %s;%s with username %s" %(host_inv.managementIp, host_password, host_password2, host_username))

def up_host_network(host_ip, scenarioConfig):
    zstack_management_ip = scenarioConfig.basicConfig.zstackManagementIp.text_
    cond = res_ops.gen_query_conditions('vmNics.ip', '=', host_ip)
    host_vm_inv = sce_ops.query_resource(zstack_management_ip, res_ops.VM_INSTANCE, cond).inventories[0]
    cond = res_ops.gen_query_conditions('uuid', '=', host_vm_inv.hostUuid)
    host_inv = sce_ops.query_resource(zstack_management_ip, res_ops.HOST, cond).inventories[0]

    host_vm_config = sce_ops.get_scenario_config_vm(host_vm_inv.name_, scenarioConfig)

    cmd = "virsh domiflist %s|sed -n '3p'|awk '{print $1}'|xargs -i virsh domif-setlink %s {} up" % (host_vm_inv.uuid, host_vm_inv.uuid)
    if test_lib.lib_execute_ssh_cmd(host_inv.managementIp, host_username, host_password, "pwd"):
        test_lib.lib_execute_ssh_cmd(host_inv.managementIp, host_username, host_password, cmd)
    elif test_lib.lib_execute_ssh_cmd(host_inv.managementIp, host_username, host_password2, "pwd"):
        test_lib.lib_execute_ssh_cmd(host_inv.managementIp, host_username, host_password2, cmd)
    else:
        test_util.test_fail("The candidate password are both not for the physical host %s, tried password %s;%s with username %s" %(host_inv.managementIp, host_password, host_password2, host_username))

def execute_cmd_in_host(host_vm, scenarioConfig, cmd):
    zstack_management_ip = scenarioConfig.basicConfig.zstackManagementIp.text_
    cond = res_ops.gen_query_conditions('vmNics.ip', '=', host_vm.ip_)
    host_vm_inv = sce_ops.query_resource(zstack_management_ip, res_ops.VM_INSTANCE, cond).inventories[0]
    cond = res_ops.gen_query_conditions('uuid', '=', host_vm_inv.hostUuid)
    host_inv = sce_ops.query_resource(zstack_management_ip, res_ops.HOST, cond).inventories[0]
    host_vm_config = sce_ops.get_scenario_config_vm(host_vm_inv.name_, scenarioConfig)
    sce_ops.execute_in_vm_console(zstack_management_ip, host_inv.managementIp, host_vm_inv.uuid, host_vm_config, cmd)

def get_host_network_status(host_ip, scenarioConfig):
    zstack_management_ip = scenarioConfig.basicConfig.zstackManagementIp.text_
    cond = res_ops.gen_query_conditions('vmNics.ip', '=', host_ip)
    host_vm_inv = sce_ops.query_resource(zstack_management_ip, res_ops.VM_INSTANCE, cond).inventories[0]
    cond = res_ops.gen_query_conditions('uuid', '=', host_vm_inv.hostUuid)
    host_inv = sce_ops.query_resource(zstack_management_ip, res_ops.HOST, cond).inventories[0]

    host_vm_config = sce_ops.get_scenario_config_vm(host_vm_inv.name_, scenarioConfig)

    cmd = "virsh domiflist %s|sed -n '3p'|awk '{print $1}'|xargs -i virsh domif-getlink %s {}" % (host_vm_inv.uuid, host_vm_inv.uuid)
    if test_lib.lib_execute_ssh_cmd(host_inv.managementIp, host_username, host_password, "pwd"):
        test_lib.lib_execute_ssh_cmd(host_inv.managementIp, host_username, host_password, cmd)
    elif test_lib.lib_execute_ssh_cmd(host_inv.managementIp, host_username, host_password2, "pwd"):
        test_lib.lib_execute_ssh_cmd(host_inv.managementIp, host_username, host_password2, cmd)
    else:
        test_util.test_fail("The candidate password are both not for the physical host %s, tried password %s;%s with username %s" %(host_inv.managementIp, host_password, host_password2, host_username))


def get_sce_hosts(scenarioConfig, scenarioFile):
    host_list = []

    if scenarioConfig == None or scenarioFile == None or not os.path.exists(scenarioFile):
        return host_list

    for host in xmlobject.safe_list(scenarioConfig.deployerConfig.hosts.host):
        for vm in xmlobject.safe_list(host.vms.vm):
            with open(scenarioFile, 'r') as fd:
                xmlstr = fd.read()
                fd.close()
                scenario_file = xmlobject.loads(xmlstr)
                for s_vm in xmlobject.safe_list(scenario_file.vms.vm):
                    if s_vm.name_ == vm.name_:
                        host_list.append(s_vm)
    return host_list


def ensure_host_has_no_vr(host_uuid):
    cond = res_ops.gen_query_conditions('type', '=', 'ApplianceVm')
    cond1 = res_ops.gen_query_conditions('hostUuid', '=', host_uuid, cond)
    vr_list = res_ops.query_resource(res_ops.VM_INSTANCE, cond1)
    if not vr_list:
        test_util.test_logger("host originally has no vr need to migrate.")
        return

    cond2 = res_ops.gen_query_conditions('uuid', '!=', host_uuid)
    cadidate_host_uuid = res_ops.query_resource(res_ops.HOST, cond2)[0].uuid

    for vr in vr_list:
        vm_ops.migrate_vm(vr.uuid, cadidate_host_uuid)


def ensure_all_vrs_on_host(host_uuid):
    cond = res_ops.gen_query_conditions('type', '=', 'ApplianceVm')
    vr_list = res_ops.query_resource(res_ops.VM_INSTANCE, cond)
    if not vr_list:
        test_util.test_logger("no vr in current env.")
        return

    for vr in vr_list:
        vm_ops.migrate_vm(vr.uuid, host_uuid)


def ensure_host_not_nfs_provider(host_uuid):
    cond = res_ops.gen_query_conditions('type', '=', 'NFS')
    primarystorage = res_ops.query_resource(res_ops.PRIMARY_STORAGE, cond)
    for nfs_ps in primarystorage:
        nfs_ps_url = nfs_ps.url
        nfs_host_ip, nfs_path = nfs_ps_url.split(':', 1)

    nfs_host_uuid = test_lib.lib_get_host_by_ip(nfs_host_ip)
    mn_ip = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].hostName
    cond1 = res_ops.gen_query_conditions('state', '=', 'Enabled')
    cond1 = res_ops.gen_query_conditions('status', '=', 'Connected', cond1)
    cond1 = res_ops.gen_query_conditions('managementIp', '!=', mn_ip, cond1)
    cond1 = res_ops.gen_query_conditions('managementIp', '!=', nfs_host_ip, cond1)
    candidate_host_uuid = res_ops.query_resource(res_ops.HOST, cond1)[0].uuid
    if host_uuid == nfs_host_uuid:
        vm_ops.migrate_vm(vm.uuid, candidate_host_uuid)


def async_exec_ifconfig_nic_down_up(sleep_time, ip, host_username, host_password, nic):
    def _wrapper(sleep_time, ip, host_username, host_password, nic):
        cmd = "ifconfig %s down; sleep %s; ifconfig %s up" %(nic, sleep_time, nic)
        test_lib.lib_execute_ssh_cmd(ip, host_username, host_password, cmd,  timeout=sleep_time+20)

    t = threading.Thread(target=_wrapper, args=(sleep_time, ip, host_username, host_password, nic))
    t.start()

    return t


def skip_if_not_storage_network_separate(scenarioConfig):
    is_storage_network_separated = False
    for host in xmlobject.safe_list(scenarioConfig.deployerConfig.hosts.host):
        for vm in xmlobject.safe_list(host.vms.vm):
            for l3Network in xmlobject.safe_list(vm.l3Networks.l3Network):
                if xmlobject.has_element(l3Network, 'primaryStorageRef'):
                    is_storage_network_separated = True
                    break
    if not is_storage_network_separated:
        test_util.test_skip("not found separate network in scenario config.")


def get_host_l2_nic_name(l2interface):
    if test_lib.scenario_config != None and test_lib.scenario_file != None and os.path.exists(test_lib.scenario_file):
        l2_network_interface = l2interface.replace("eth", "zsn")
        return l2_network_interface
    else:
        return l2interface

    
