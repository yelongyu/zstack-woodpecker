'''

Create an unified test_stub to share test operations

@author: Youyk
'''

import os
import subprocess
import time
import uuid

import zstacklib.utils.ssh as ssh
import zstacklib.utils.jsonobject as jsonobject
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.zstack_test.zstack_test_vm as zstack_vm_header
import zstackwoodpecker.zstack_test.zstack_test_volume as zstack_volume_header
import zstackwoodpecker.zstack_test.zstack_test_eip as zstack_eip_header
import zstackwoodpecker.zstack_test.zstack_test_vip as zstack_vip_header
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.vm_operations as vm_ops

test_file = '/tmp/test.img'
TEST_TIME = 120

def create_vlan_vm_with_volume(l3_name=None, disk_offering_uuids=None, disk_number=None, session_uuid = None):
    if not disk_offering_uuids:
        disk_offering = test_lib.lib_get_disk_offering_by_name(os.environ.get('smallDiskOfferingName'))
        disk_offering_uuids = [disk_offering.uuid]
        if disk_number:
            for i in range(disk_number - 1):
                disk_offering_uuids.append(disk_offering.uuid)

    return create_vlan_vm(l3_name, disk_offering_uuids, \
            session_uuid = session_uuid)

def create_vlan_vm(l3_name=None, disk_offering_uuids=None, system_tags=None, session_uuid = None, instance_offering_uuid = None):
    image_name = os.environ.get('imageName_net')
    if not l3_name:
        l3_name = os.environ.get('l3VlanNetworkName1')

    return create_vm('vlan_vm', image_name, l3_name, \
            disk_offering_uuids=disk_offering_uuids, system_tags=system_tags, \
            instance_offering_uuid = instance_offering_uuid,
            session_uuid = session_uuid)

def create_vm(vm_name='virt-vm', \
        image_name = None, \
        l3_name = None, \
        instance_offering_uuid = None, \
        host_uuid = None, \
        disk_offering_uuids=None, system_tags=None, session_uuid = None):

    if not image_name:
        image_name = os.environ.get('imageName_net') 
    if not l3_name:
        l3_name = os.environ.get('l3PublicNetworkName')

    vm_creation_option = test_util.VmOption()
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    l3_names = l3_name.split(',')
    print 'shuang: %s' % (l3_names)
    l3_net_uuids = []
    for l3_n in l3_names:
        l3_net_uuid = test_lib.lib_get_l3_by_name(l3_n).uuid
        l3_net_uuids.append(l3_net_uuid)
    if not instance_offering_uuid:
	instance_offering_name = os.environ.get('instanceOfferingName_s')
        instance_offering_uuid = test_lib.lib_get_instance_offering_by_name(instance_offering_name).uuid

    vm_creation_option.set_l3_uuids(l3_net_uuids)
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_name(vm_name)
    vm_creation_option.set_system_tags(system_tags)
    vm_creation_option.set_data_disk_uuids(disk_offering_uuids)
    if host_uuid:
        vm_creation_option.set_host_uuid(host_uuid)
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

def copy_key_file(vm_inv):
    vm_ip = vm_inv.vmNics[0].ip

    cmd = 'scp  -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null /root/.ssh/id_rsa %s:/root/.ssh/id_rsa' % vm_ip
    timeout = 10
    if  execute_shell_in_process(cmd, timeout) != 0:
        test_util.test_fail('test file is not created')

def test_scp_vm_outbound_speed(vm_inv, bandwidth, raise_exception = True):
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
        if not raise_exception:
            test_util.test_logger('network outbound QOS test file failed, since the scp time: %d is smaller than the expected test time: %d. It means the bandwidth limitation: %d KB/s is not effect. ' % (scp_time, TEST_TIME, bandwidth))
            return False
        test_util.test_fail('network outbound QOS test file failed, since the scp time: %d is smaller than the expected test time: %d. It means the bandwidth limitation: %d KB/s is not effect. ' % (scp_time, TEST_TIME, bandwidth))
    else:
        test_util.test_logger('network outbound QOS test file pass, since the scp time: %d is bigger than the expected test time: %d. It means the bandwidth limitation: %d KB/s is effect. ' % (scp_time, TEST_TIME, bandwidth))

    return True

def test_scp_vm_inbound_speed(vm_inv, bandwidth, raise_exception = True):
    '''
    bandwidth unit is KB
    '''
    timeout = TEST_TIME + 30
    vm_ip = vm_inv.vmNics[0].ip
    file_size = bandwidth * TEST_TIME
    seek_size = file_size / 1024 - 1
    cmd = 'dd if=/dev/zero of=%s bs=1M count=1 seek=%d' \
            % (test_file, seek_size)
    os.system(cmd)
    cmd = 'scp -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s %s:/dev/null' \
            % (test_file, vm_ip)
    start_time = time.time()
    if execute_shell_in_process(cmd, timeout) != 0:
        test_util.test_fail('scp test file failed')

    end_time = time.time()
    os.system('rm -f %s' % test_file)

    scp_time = end_time - start_time
    if scp_time < TEST_TIME:
        if not raise_exception:
            test_util.test_logger('network inbound QOS test file failed, since the scp time: %d is smaller than the expected test time: %d. It means the bandwidth limitation: %d KB/s is not effect. ' % (scp_time, TEST_TIME, bandwidth))
            return False
        test_util.test_fail('network inbound QOS test file failed, since the scp time: %d is smaller than the expected test time: %d. It means the bandwidth limitation: %d KB/s is not effect. ' % (scp_time, TEST_TIME, bandwidth))
    else:
        test_util.test_logger('network inbound QOS test file pass, since the scp time: %d is bigger than the expected test time: %d. It means the bandwidth limitation: %d KB/s is effect. ' % (scp_time, TEST_TIME, bandwidth))

    return True

def test_scp_outbound_speed(source_ip, target_ip, bandwidth, raise_exception = True):
    '''
    bandwidth unit is KB
    '''
    timeout = TEST_TIME + 30
    cmd = 'ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s "scp -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s %s:%s"' \
            % (source_ip, test_file, target_ip, test_file)
    start_time = time.time()
    os.system(cmd)

    end_time = time.time()

    scp_time = end_time - start_time
    if scp_time < TEST_TIME:
        if not raise_exception:
            test_util.test_logger('network outbound QOS test file failed, since the scp time: %d is smaller than the expected test time: %d. It means the bandwidth limitation: %d KB/s is not effect. ' % (scp_time, TEST_TIME, bandwidth))
            return False
        test_util.test_fail('network outbound QOS test file failed, since the scp time: %d is smaller than the expected test time: %d. It means the bandwidth limitation: %d KB/s is not effect. ' % (scp_time, TEST_TIME, bandwidth))
    else:
        test_util.test_logger('network outbound QOS test file pass, since the scp time: %d is bigger than the expected test time: %d. It means the bandwidth limitation: %d KB/s is effect. ' % (scp_time, TEST_TIME, bandwidth))

    return True

def install_fio(vm_inv):
    timeout = TEST_TIME + 30 
    vm_ip = vm_inv.vmNics[0].ip

    cmd = 'scp /etc/yum.repos.d/zstack-internal-yum.repo root@%s:/etc/yum.repos.d/zstack-internal-yum.repo' % vm_ip
    if execute_shell_in_process(cmd, timeout) != 0:
        test_util.test_fail('fail to scp zstack-internal-yum.repo.')

    ssh_cmd = 'ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm_ip
    cmd = '%s "mv /etc/yum.repos.d/CentOS-Base.repo /etc/yum.repos.d/epel.repo /etc"' \
            % (ssh_cmd)
    if  execute_shell_in_process(cmd, timeout) != 0:
        test_util.test_fail('fail to move CentOS-Base.repo epel.repo.')

    cmd = '%s "yum clean metadata"' \
            % (ssh_cmd)
    if  execute_shell_in_process(cmd, timeout) != 0:
        test_util.test_fail('fail to clean metadata.')

    cmd = '%s "which fio || yum install -y fio --disableplugin=fastestmirror"' \
            % (ssh_cmd)
    if  execute_shell_in_process(cmd, timeout) != 0:
        test_util.test_fail('fio installation failed.')

def test_fio_iops(vm_inv, iops, raise_exception = True):
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
        if not raise_exception:
            test_util.test_logger('fio test failed.')
            return False
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
        if not raise_exception:
            test_util.test_logger('Did not get bandwidth for fio test')
            return False
        test_util.test_fail('Did not get bandwidth for fio test')

    if bw == iops or bw < (iops - 10):
        test_util.test_logger('disk iops: %s is <= setting: %s' % (bw, iops))
        return True
    else:
        test_util.test_logger('disk iops :%s is not same with %s' % (bw, iops))
        if raise_exception:
            test_util.test_fail('fio bandwidth test fails')
        return False

def test_fio_bandwidth(vm_inv, bandwidth, path = '/tmp', raise_exception=True):
    def cleanup_log():
        logfd.close()
        os.system('rm -f %s' % tmp_file)

    timeout = TEST_TIME + 360
    vm_ip = vm_inv.vmNics[0].ip

    ssh_cmd = 'ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm_ip

    if '/dev/' in path:
        cmd1 = """%s "fio -ioengine=libaio -bs=1M -direct=1 -thread -rw=read -size=100M -filename=%s -name='EBS 1M read' -iodepth=64 -runtime=60 -numjobs=4 -group_reporting|grep iops" """ \
                % (ssh_cmd, path)
        cmd2 = """%s "fio -ioengine=libaio -bs=1M -direct=1 -thread -rw=read -size=900M -filename=%s -name='EBS 1M read' -iodepth=64 -runtime=60 -numjobs=4 -group_reporting|grep iops" """ \
                % (ssh_cmd, path)
    else:
        cmd1 = """%s "fio -ioengine=libaio -bs=1M -direct=1 -thread -rw=write -size=100M -filename=%s/test1.img -name='EBS 1M write' -iodepth=64 -runtime=60 -numjobs=4 -group_reporting|grep iops" """ \
                % (ssh_cmd, path)
        cmd2 = """%s "fio -ioengine=libaio -bs=1M -direct=1 -thread -rw=write -size=900M -filename=%s/test2.img -name='EBS 1M write' -iodepth=64 -runtime=60 -numjobs=4 -group_reporting|grep iops" """ \
                % (ssh_cmd, path)

    tmp_file = '/tmp/%s' % uuid.uuid1().get_hex()
    logfd = open(tmp_file, 'w', 0)
    #rehearsal
    execute_shell_in_process(cmd1, timeout)

    if  execute_shell_in_process(cmd2, timeout, logfd) != 0:
        logfd.close()
        logfd = open(tmp_file, 'r')
        test_util.test_logger('test_fio_bandwidth log: %s ' % '\n'.join(logfd.readlines()))
        cleanup_log()
        if not raise_exception:
            test_util.test_logger('fio test failed.')
            return False
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
        if not raise_exception:
            test_util.test_logger('Did not get bandwidth for fio test')
            return False
        test_util.test_fail('Did not get bandwidth for fio test')

    threshold = bandwidth/1024/2
    bw_up_limit = bandwidth/1024 + threshold
    bw_down_limit = bandwidth/1024 - threshold
    if bw > bw_down_limit and bw < bw_up_limit:
        test_util.test_logger('disk bandwidth:%s is between %s and %s' \
                % (bw, bw_down_limit, bw_up_limit))
        return True
    else:
        test_util.test_logger('disk bandwidth:%s is not between %s and %s' \
                % (bw, bw_down_limit, bw_up_limit))
        if raise_exception:
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

def migrate_vm_to_random_host(vm, timeout = None):
    test_util.test_dsc("migrate vm to random host")
    target_host = test_lib.lib_find_random_host(vm.vm)
    current_host = test_lib.lib_find_host_by_vm(vm.vm)
    vm.migrate(target_host.uuid, timeout)

    new_host = test_lib.lib_get_vm_host(vm.vm)
    if not new_host:
        test_util.test_fail('Not find available Hosts to do migration')

    if new_host.uuid != target_host.uuid:
        test_util.test_fail('[vm:] did not migrate from [host:] %s to target [host:] %s, but to [host:] %s' % (vm.vm.uuid, current_host.uuid, target_host.uuid, new_host.uuid))
    else:
        test_util.test_logger('[vm:] %s has been migrated from [host:] %s to [host:] %s' % (vm.vm.uuid, current_host.uuid, target_host.uuid))

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

def create_vip(vip_name=None, l3_uuid=None, session_uuid = None):
    if not vip_name:
        vip_name = 'test vip'
    if not l3_uuid:
        l3_name = os.environ.get('l3PublicNetworkName')
        l3_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid

    vip_creation_option = test_util.VipOption()
    vip_creation_option.set_name(vip_name)
    vip_creation_option.set_l3_uuid(l3_uuid)
    vip_creation_option.set_session_uuid(session_uuid)

    vip = zstack_vip_header.ZstackTestVip()
    vip.set_creation_option(vip_creation_option)
    vip.create()

    return vip

def attach_mount_volume(volume, vm, mount_point):
    volume.attach(vm)
    import tempfile
    script_file = tempfile.NamedTemporaryFile(delete=False)
    script_file.write('''
mkdir -p %s
device="/dev/`ls -ltr --file-type /dev | grep disk | awk '{print $NF}' | grep -v '[[:digit:]]' | tail -1`"
mount ${device}1 %s
''' % (mount_point, mount_point))
    script_file.close()

    vm_inv = vm.get_vm()
    if not test_lib.lib_execute_shell_script_in_vm(vm_inv, script_file.name):
        test_util.test_fail("mount operation failed in [volume:] %s in [vm:] %s" % (volume.get_volume().uuid, vm_inv.uuid))

        os.unlink(script_file.name)

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

def setup_fake_df(host, total, avail):
    rsp = test_lib.lib_execute_sh_cmd_by_agent(host.managementIp, "ls /usr/bin/df.real")
    if rsp.return_code != 0:
        rsp = test_lib.lib_execute_sh_cmd_by_agent(host.managementIp, 'cp /usr/bin/df /usr/bin/df.real')
    used = int(total) - int(avail)

    rsp = test_lib.lib_execute_sh_cmd_by_agent(host.managementIp, '''echo "echo 'Filesystem     1K-blocks    Used Available Use% Mounted on'" >/usr/bin/df.fake''')
    rsp = test_lib.lib_execute_sh_cmd_by_agent(host.managementIp, '''echo "echo '/dev/vda1      %s %s %s   2%% /'" >>/usr/bin/df.fake''' % (total, used, avail))
    rsp = test_lib.lib_execute_sh_cmd_by_agent(host.managementIp, 'rm -rf /usr/bin/df; ln -s /usr/bin/df.fake /usr/bin/df; chmod a+x /usr/bin/df')

def remove_fake_df(host):
    rsp = test_lib.lib_execute_sh_cmd_by_agent(host.managementIp, "ls /usr/bin/df.real")
    if rsp.return_code == 0:
        rsp = test_lib.lib_execute_sh_cmd_by_agent(host.managementIp, 'rm -rf /usr/bin/df; ln -s /usr/bin/df.real /usr/bin/df')

def setup_fake_fs(host, total, path):
    rsp = test_lib.lib_execute_sh_cmd_by_agent(host.managementIp, "mount -t tmpfs -o size=%s tmpfs %s" % (total, path))

def remove_fake_fs(host, path):
    rsp = test_lib.lib_execute_sh_cmd_by_agent(host.managementIp, "umount %s" % (path))

def setup_fake_ceph(host, total, avail):
    test_lib.lib_install_testagent_to_host(host)
    rsp = test_lib.lib_execute_sh_cmd_by_agent(host.managementIp, "ls /usr/bin/ceph.real")
    if rsp.return_code != 0:
        rsp = test_lib.lib_execute_sh_cmd_by_agent(host.managementIp, 'cp /usr/bin/ceph /usr/bin/ceph.real')
    used = int(total) - int(avail)

    rsp = test_lib.lib_execute_sh_cmd_by_agent(host.managementIp, '''echo '[ "$1 $2 $3" != "df -f json" ] && ceph.real "$@"'  >/usr/bin/ceph.fake''')
    rsp = test_lib.lib_execute_sh_cmd_by_agent(host.managementIp, '''echo '[ "$1 $2 $3" != "df -f json" ] && exit'  >>/usr/bin/ceph.fake''')
    rsp = test_lib.lib_execute_sh_cmd_by_agent(host.managementIp, "/usr/bin/ceph.real df -f json")
    df = jsonobject.loads(rsp.stdout)
    df.stats.total_bytes = total
    df.stats.total_avail_bytes = avail
    rsp = test_lib.lib_execute_sh_cmd_by_agent(host.managementIp, '''echo "echo ''" >>/usr/bin/ceph.fake''')
    string = jsonobject.dumps(df).replace('"', '\\"')
    rsp = test_lib.lib_execute_sh_cmd_by_agent(host.managementIp, '''echo "echo '%s'" >>/usr/bin/ceph.fake''' % (string))
    rsp = test_lib.lib_execute_sh_cmd_by_agent(host.managementIp, 'rm -rf /usr/bin/ceph; ln -s /usr/bin/ceph.fake /usr/bin/ceph; chmod a+x /usr/bin/ceph')

def remove_fake_ceph(host):
    rsp = test_lib.lib_execute_sh_cmd_by_agent(host.managementIp, "ls /usr/bin/ceph.real")
    if rsp.return_code == 0:
        rsp = test_lib.lib_execute_sh_cmd_by_agent(host.managementIp, 'rm -rf /usr/bin/ceph; ln -s /usr/bin/ceph.real /usr/bin/ceph')
