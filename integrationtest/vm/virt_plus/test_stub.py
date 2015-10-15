'''

Create an unified test_stub to share test operations

@author: Youyk
'''

import os
import subprocess
import time

import zstacklib.utils.ssh as ssh
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.zstack_test.zstack_test_vm as zstack_vm_header
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.vm_operations as vm_ops

test_file = '/tmp/test.img'
test_time = 60

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
    if host_uuid:
        vm_creation_option.set_host_uuid(host_uuid)
    vm = zstack_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    return vm 

def make_ssh_no_password(vm_inv):
    vm_ip = vm_inv.vmNics[0].ip
    ssh.make_ssh_no_password(vm_ip, test_lib.lib_get_vm_username(vm_inv), \
            test_lib.lib_get_vm_password(vm_inv))

def execute_shell_in_process(cmd, timeout=10):
    process = subprocess.Popen(cmd, executable='/bin/sh', shell=True, universal_newlines=True)

    start_time = time.time()
    while process.poll() is None:
        curr_time = time.time()
        test_time = curr_time - start_time
        if test_time > timeout:
            process.kill()
            test_util.test_logger('[shell:] %s timeout ' % cmd)
            return False
        time.sleep(1)

    test_util.test_logger('[shell:] %s is finished.' % cmd)
    return process.returncode

def create_test_file(vm_inv, bandwidth):
    '''
    the bandwidth is for calculate the test file size, 
    since the test time should be finished in 60s. 
    bandwidth unit is KB.
    '''
    vm_ip = vm_inv.vmNics[0].ip
    file_size = bandwidth * test_time
    seek_size = file_size / 1024 - 1
    timeout = 10

    ssh_cmd = 'ssh  -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm_ip
    cmd = '%s "dd if=/dev/zero of=%s bs=1M count=1 seek=%d"' \
            % (ssh_cmd, test_file, seek_size)
    if  execute_shell_in_process(cmd, timeout) != 0:
        test_util.test_fail('test file is not created')

def test_scp_speed(vm_inv, bandwidth):
    '''
    bandwidth unit is KB
    '''
    timeout = test_time + 30
    vm_ip = vm_inv.vmNics[0].ip
    cmd = 'scp -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s:%s /dev/null' \
            % (vm_ip, test_file)
    start_time = time.time()
    if execute_shell_in_process(cmd, timeout) != 0:
        test_util.test_fail('scp test file failed')

    end_time = time.time()

    scp_time = end_time - start_time
    if scp_time < test_time:
        test_util.test_fail('network QOS test file failed, since the scp time: %d is smaller than the expected test time: %d. It means the bandwidth limitation: %d KB/s is not effect. ' % (scp_time, test_time, bandwidth))
    else:
        test_util.test_logger('network QOS test file pass, since the scp time: %d is bigger than the expected test time: %d. It means the bandwidth limitation: %d KB/s is effect. ' % (scp_time, test_time, bandwidth))

    return True
