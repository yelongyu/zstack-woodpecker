'''

Create an unified test_stub to share test operations

@author: quarkonics
'''

import os
import subprocess
import time
import uuid

import zstacklib.utils.ssh as ssh
import zstacklib.utils.shell as shell
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.zstack_test.zstack_test_vm as zstack_vm_header
import zstackwoodpecker.zstack_test.zstack_test_volume as zstack_volume_header
import zstackwoodpecker.zstack_test.zstack_test_eip as zstack_eip_header
import zstackwoodpecker.zstack_test.zstack_test_vip as zstack_vip_header
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.account_operations as acc_ops
import telnetlib


shell.logcmd = False
interval = 0.5

test_file = '/tmp/test.img'
TEST_TIME = 120
original_root_password = "password"


def create_vm(vm_name='virt-vm', \
        image_name = None, \
        l3_name = None, \
        instance_offering_uuid = None, \
        host_uuid = None, \
        disk_offering_uuids=None, system_tags=None, \
        root_password=None, session_uuid = None):


    if not image_name:
        image_name = os.environ.get('imageName_net') 
    elif os.environ.get(image_name):
        image_name = os.environ.get(image_name)

    if not l3_name:
        l3_name = os.environ.get('l3PublicNetworkName')

    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    if not instance_offering_uuid:
	instance_offering_name = os.environ.get('instanceOfferingName_m')
        instance_offering_uuid = test_lib.lib_get_instance_offering_by_name(instance_offering_name).uuid

    vm_creation_option = test_util.VmOption()
    vm_creation_option.set_l3_uuids([l3_net_uuid])
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_name(vm_name)
    vm_creation_option.set_system_tags(system_tags)
    vm_creation_option.set_data_disk_uuids(disk_offering_uuids)
    if root_password:
        vm_creation_option.set_root_password(root_password)
    if host_uuid:
        vm_creation_option.set_host_uuid(host_uuid)
    if session_uuid:
        vm_creation_option.set_session_uuid(session_uuid)

    vm = zstack_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    return vm 


def create_user_in_vm(vm, username, password):
    """
    create non-root user with password setting
    """
    global original_root_password
    test_util.test_logger("create_user_in_vm: %s:%s" %(username, password))

    vm_ip = vm.vmNics[0].ip

    cmd = "adduser %s" % (username)
    ret, output, stderr = ssh.execute(cmd, vm_ip, "root", original_root_password, False, 22)
    if ret != 0:
        test_util.test_fail("User created failure, cmd[%s], output[%s], stderr[%s]" %(cmd, output, stderr))

    cmd = "echo -e \'%s\n%s\' | passwd %s" % (password, password, username)
    ret, output, stderr = ssh.execute(cmd, vm_ip, "root", original_root_password, False, 22)
    if ret != 0:
        test_util.test_fail("set non-root password failure, cmd[%s], output[%s], stderr[%s]" %(cmd, output, stderr))



def share_admin_resource(account_uuid_list):
    instance_offerings = res_ops.get_resource(res_ops.INSTANCE_OFFERING)
    for instance_offering in instance_offerings:
        acc_ops.share_resources(account_uuid_list, [instance_offering.uuid])
    cond = res_ops.gen_query_conditions('mediaType', '!=', 'ISO')
    images =  res_ops.query_resource(res_ops.IMAGE, cond)
    for image in images:
        acc_ops.share_resources(account_uuid_list, [image.uuid])

    root_disk_uuid = test_lib.lib_get_disk_offering_by_name(os.environ.get('rootDiskOfferingName')).uuid
    data_disk_uuid = test_lib.lib_get_disk_offering_by_name(os.environ.get('smallDiskOfferingName')).uuid

    share_list = [root_disk_uuid, data_disk_uuid]

    #l3net_uuids = res_ops.get_resource(res_ops.L3_NETWORK).uuid
    l3nets = res_ops.get_resource(res_ops.L3_NETWORK)
    for l3net in l3nets:
        l3net_uuid = l3net.uuid
        share_list.append(l3net_uuid)
    acc_ops.share_resources(account_uuid_list, share_list)


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

def online_hotplug_cpu_memory(vm):
    script_file = "%s/%s" % (os.environ.get('woodpecker_root_path'), '/tools/online_hotplug_cpu_memory.sh')
    test_lib.lib_execute_shell_script_in_vm(vm.get_vm(), script_file)

def wait_for_certain_vm_state(vm, state='running', timeout=120):
    state = state.lower()
    for _ in xrange(timeout):
        if vm.get_vm().state.lower() == state:
            return
        else:
            time.sleep(interval)

def wait_until_vm_reachable(vm, timeout=120):
    vm_ip = vm.get_vm().vmNics[0].ip
    ping_cmd = "ping %s -c 1 | grep 'ttl='" % vm_ip
    for _ in xrange(timeout):
        if shell.call(ping_cmd, exception=False):
            break
        else:
            time.sleep(interval)


class CapacityCheckerContext(object):

    def __init__(self, vm, cpu_change, mem_change):
        self.vm = vm
        self.cpu_change = cpu_change
        assert cpu_change >= 0
        self.mem_change = mem_change
        assert mem_change >= 0
        self.mem_aligned_change = None
        self.available_cpu_before = None
        self.available_memory_before = None
        self.vm_outer_cpu_before = None
        self.vm_outer_mem_before = None
        self.vm_internal_cpu_before = None
        self.vm_internal_mem_before = None
        self.available_cpu_after = None
        self.available_memory_after = None
        self.vm_outer_cpu_after = None
        self.vm_outer_mem_after = None
        self.vm_internal_cpu_after = None
        self.vm_internal_mem_after = None

    def __enter__(self):
        test_util.test_logger("CPU_CHANGE={}, MEM_CHANGE={}".format(self.cpu_change, self.mem_change))
        self.get_capacity_before_action()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        if exception_type:
            raise exception_type, exception_value, traceback
        else:
            self.get_capacity_after_action()
            self.calculate_mem_aligned_change()
            self.check_capacity()

    def check_capacity(self):
        #test_util.test_logger("{},{},{}".format(self.available_memory_before,self.available_memory_after,
        #                                        self.mem_aligned_change))
        test_util.test_logger("vm_outer_cpu_before={}\n "
                              "vm_outer_cpu_after={}\n "
                              "vm_outer_mem_before={}\n "
                              "vm_outer_mem_after={}\n "
                              "vm_internal_cpu_before={}\n "
                              "vm_internal_cpu_after={}\n "
                              "vm_internal_mem_before={}\n "
                              "vm_internal_mem_after={}\n "
                              "available_cpu_before={}\n "
                              "available_cpu_after={}\n "
                              "available_memory_before={}\n "
                              "available_memory_after={}".
                              format(self.vm_outer_cpu_before, self.vm_outer_cpu_after,
                                     self.vm_outer_mem_before, self.vm_outer_mem_after,
                                     self.vm_internal_cpu_before, self.vm_internal_cpu_after,
                                     self.vm_internal_mem_before, self.vm_internal_mem_after,
                                     self.available_cpu_before, self.available_cpu_after,
                                     self.available_memory_before, self.available_memory_after,
                                     ))
        assert self.vm_outer_cpu_before == self.vm_outer_cpu_after - self.cpu_change
        assert self.vm_outer_mem_before == self.vm_outer_mem_after - self.mem_aligned_change
        assert self.vm_internal_cpu_before == self.vm_internal_cpu_after - self.cpu_change
        assert self.vm_internal_mem_before == self.vm_internal_mem_after - self.mem_aligned_change/1024/1024
        assert self.available_cpu_before == self.available_cpu_after + self.cpu_change
        assert self.available_memory_after + int(self.mem_aligned_change/float(test_lib.lib_get_provision_memory_rate())) \
               in range(self.available_memory_before-2, self.available_memory_before+2)

    def get_capacity_before_action(self):
        (self.available_cpu_before, self.available_memory_before,
         self.vm_outer_cpu_before, self.vm_outer_mem_before,
         self.vm_internal_cpu_before, self.vm_internal_mem_before) = check_cpu_mem(self.vm)

    def get_capacity_after_action(self):
        (self.available_cpu_after, self.available_memory_after,
         self.vm_outer_cpu_after, self.vm_outer_mem_after,
         self.vm_internal_cpu_after, self.vm_internal_mem_after) = check_cpu_mem(self.vm)

    def calculate_mem_aligned_change(self):
        mem_change = self.mem_change/1024/1024
        if mem_change == 0:
            self.mem_aligned_change = 0
            return self.mem_aligned_change
        if mem_change < 128:
            self.mem_aligned_change = 128 * 1024 * 1024
            return self.mem_aligned_change
        reminder = mem_change % 128
        counter = mem_change / 128
        if reminder < 64:
            self.mem_aligned_change = 128 * 1024 * 1024 * counter
        else:
            self.mem_aligned_change = 128 * 1024 * 1024 * (counter + 1)
        return self.mem_aligned_change
