'''

Create an unified test_stub to share test operations

@author: Youyk
'''

import os
import subprocess
import time
import uuid

import zstacklib.utils.ssh as ssh
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.zstack_test.zstack_test_vm as zstack_vm_header
import zstackwoodpecker.zstack_test.zstack_test_volume as zstack_volume_header
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.vm_operations as vm_ops

test_file = '/tmp/test.img'
TEST_TIME = 60

def create_vm(vm_name='virt-vm', \
        image_name = None, \
        l3_name = None, \
        instance_offering_uuid = None, \
        host_uuid = None,
        disk_offering_uuids=None, system_tags=None, session_uuid = None, ):

    if not image_name:
        image_name = os.environ.get('imageName_net') 
    if not l3_name:
        l3_name = os.environ.get('l3PublicNetworkName')

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

def create_test_file(vm_inv, bandwidth):
    '''
    the bandwidth is for calculate the test file size, 
    since the test time should be finished in 60s. 
    bandwidth unit is KB.
    '''
    vm_ip = vm_inv.vmNics[0].ip
    file_size = bandwidth * TEST_TIME
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
    timeout = TEST_TIME + 30
    vm_ip = vm_inv.vmNics[0].ip
    cmd = 'scp -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s:%s /dev/null' \
            % (vm_ip, test_file)
    start_time = time.time()
    if execute_shell_in_process(cmd, timeout) != 0:
        test_util.test_fail('scp test file failed')

    end_time = time.time()

    scp_time = end_time - start_time
    if scp_time < TEST_TIME:
        test_util.test_fail('network QOS test file failed, since the scp time: %d is smaller than the expected test time: %d. It means the bandwidth limitation: %d KB/s is not effect. ' % (scp_time, TEST_TIME, bandwidth))
    else:
        test_util.test_logger('network QOS test file pass, since the scp time: %d is bigger than the expected test time: %d. It means the bandwidth limitation: %d KB/s is effect. ' % (scp_time, TEST_TIME, bandwidth))

    return True

def install_fio(vm_inv):
    timeout = TEST_TIME + 30 
    vm_ip = vm_inv.vmNics[0].ip

    ssh_cmd = 'ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm_ip
    cmd = '%s "which fio || yum install -y fio"' \
            % (ssh_cmd)
    if  execute_shell_in_process(cmd, timeout) != 0:
        test_util.test_fail('fio installation failed.')

def test_fio_iops(vm_inv, iops):
    def cleanup_log():
        logfd.close()
        os.system('rm -f %s' % tmp_file)

    timeout = TEST_TIME + 120
    vm_ip = vm_inv.vmNics[0].ip

    ssh_cmd = 'ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm_ip
    cmd1 = """%s "fio -ioengine=libaio -bs=4k -direct=1 -thread -rw=write -size=256M -filename=/tmp/test1.img -name='EBS 4k write' -iodepth=64 -runtime=60 -numjobs=4 -group_reporting|grep iops" """ \
            % (ssh_cmd)
    cmd2 = """%s "fio -ioengine=libaio -bs=4k -direct=1 -thread -rw=write -size=256M -filename=/tmp/test2.img -name='EBS 4k write' -iodepth=64 -runtime=60 -numjobs=4 -group_reporting|grep iops" """ \
            % (ssh_cmd)


    tmp_file = '/tmp/%s' % uuid.uuid1().get_hex()
    logfd = open(tmp_file, 'w', 0)
    #rehearsal
    execute_shell_in_process(cmd1, timeout)

    if  execute_shell_in_process(cmd2, timeout, logfd) != 0:
        logfd.close()
        logfd = open(tmp_file, 'r')
        test_util.test_logger('test_fio_bandwidth log: %s ' % '\n'.join(logfd.readlines()))
        cleanup_log()
        test_util.test_fail('fio test failed.')

    logfd.close()
    logfd = open(tmp_file, 'r')
    result_lines = logfd.readlines()
    test_util.test_logger('test_fio_bandwidth log: %s ' % '\n'.join(result_lines))
    bw=0
    for line in result_lines: 
        if  'iops' in line:
            test_util.test_logger('test_fio_bandwidth: %s' % line)
            results = line.split()
            for result in results:
                if 'iops=' in result:
                    bw = int(float(result[5:]))

    #cleanup_log()
    if bw == 0:
        test_util.test_fail('Did not get bandwidth for fio test')

    if bw == iops or bw < (iops - 10):
        test_util.test_logger('disk iops: %s is <= setting: %s' % (bw, iops))
        return True
    else:
        test_util.test_logger('disk iops :%s is not same with %s' % (bw, iops))
        test_util.test_fail('fio bandwidth test fails')
        return False

def test_fio_bandwidth(vm_inv, bandwidth):
    def cleanup_log():
        logfd.close()
        os.system('rm -f %s' % tmp_file)

    timeout = TEST_TIME + 120
    vm_ip = vm_inv.vmNics[0].ip

    ssh_cmd = 'ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm_ip
    cmd1 = """%s "fio -ioengine=libaio -bs=1M -direct=1 -thread -rw=write -size=100M -filename=/tmp/test1.img -name='EBS 1M write' -iodepth=64 -runtime=60 -numjobs=4 -group_reporting|grep iops" """ \
            % (ssh_cmd)
    cmd2 = """%s "fio -ioengine=libaio -bs=1M -direct=1 -thread -rw=write -size=1G -filename=/tmp/test2.img -name='EBS 1M write' -iodepth=64 -runtime=60 -numjobs=4 -group_reporting|grep iops" """ \
            % (ssh_cmd)


    tmp_file = '/tmp/%s' % uuid.uuid1().get_hex()
    logfd = open(tmp_file, 'w', 0)
    #rehearsal
    execute_shell_in_process(cmd1, timeout)

    if  execute_shell_in_process(cmd2, timeout, logfd) != 0:
        logfd.close()
        logfd = open(tmp_file, 'r')
        test_util.test_logger('test_fio_bandwidth log: %s ' % '\n'.join(logfd.readlines()))
        cleanup_log()
        test_util.test_fail('fio test failed.')

    logfd.close()
    logfd = open(tmp_file, 'r')
    result_lines = logfd.readlines()
    test_util.test_logger('test_fio_bandwidth log: %s ' % '\n'.join(result_lines))
    bw=0
    for line in result_lines: 
        if  'iops' in line:
            test_util.test_logger('test_fio_bandwidth: %s' % line)
            results = line.split()
            for result in results:
                if 'bw=' in result:
                    bw = int(float(result[3:].split('KB')[0]))

    #cleanup_log()
    if bw == 0:
        test_util.test_fail('Did not get bandwidth for fio test')

    bw_up_limit = bandwidth/1024 + 10240
    bw_down_limit = bandwidth/1024 - 10240
    if bw > bw_down_limit and bw < bw_up_limit:
        test_util.test_logger('disk bandwidth:%s is between %s and %s' \
                % (bw, bw_down_limit, bw_up_limit))
        return True
    else:
        test_util.test_logger('disk bandwidth:%s is not between %s and %s' \
                % (bw, bw_down_limit, bw_up_limit))
        test_util.test_fail('fio bandwidth test fails')
        return False

def create_volume(volume_creation_option=None, session_uuid = None):
    if not volume_creation_option:
        disk_offering_uuid = res_ops.query_resource(res_ops.DISK_OFFERING)[0].uuid
        volume_creation_option = test_util.VolumeOption()
        volume_creation_option.set_disk_offering_uuid(disk_offering_uuid)
        volume_creation_option.set_name('vr_test_volume')

    volume_creation_option.set_session_uuid(session_uuid)
    volume = zstack_volume_header.ZstackTestVolume()
    volume.set_creation_option(volume_creation_option)
    volume.create()
    return volume

