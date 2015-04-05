'''

@author: Youyk
'''
import os
import tempfile
import subprocess
import time
import uuid

import zstacklib.utils.ssh as ssh
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as zstack_vm_header

test_obj_dict = test_state.TestStateDict()

def create_vlan_vm(l3_name=None, disk_offering_uuids=None):
    image_name = os.environ.get('imageName_i_c6')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    if not l3_name:
        l3_name = os.environ.get('l3VlanNetworkName1')

    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    return create_vm([l3_net_uuid], image_uuid, 'zstack_installation_vm', \
            disk_offering_uuids)

def create_vm(l3_uuid_list, image_uuid, vm_name = None, \
        disk_offering_uuids = None, default_l3_uuid = None):
    vm_creation_option = test_util.VmOption()
    conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
    instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_l3_uuids(l3_uuid_list)
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_name(vm_name)
    vm_creation_option.set_data_disk_uuids(disk_offering_uuids)
    vm_creation_option.set_default_l3_uuid(default_l3_uuid)
    vm = zstack_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    return vm

def check_str(string):
    if string == None:
        return ""
    return string

def execute_shell_in_process(cmd, tmp_file):
    logfd = open(tmp_file, 'w', 0)
    process = subprocess.Popen(cmd, executable='/bin/sh', shell=True, stdout=logfd, stderr=logfd, universal_newlines=True)

    timeout = 3600
    start_time = time.time()
    while process.poll() is None:
        curr_time = time.time()
        test_time = curr_time - start_time
        if test_time > timeout:
            process.terminate()
            logfd.close()
            logfd = open(tmp_file, 'r')
            test_util.test_logger('[shell:] %s [timeout logs:] %s' % (cmd, '\n'.join(logfd.readlines())))
            logfd.close()
            os.system('rm -f %s' % tmp_file)
            test_util.test_fail('[shell:] %s timeout, after %d seconds' % (cmd, timeout))
        print('Installation: %d' % int(test_time))
        time.sleep(1)

    logfd.close()
    logfd = open(tmp_file, 'r')
    test_util.test_logger('[shell:] %s [logs]: %s' % (cmd, '\n'.join(logfd.readlines())))
    logfd.close()
    return process.returncode

def test():
    test_util.test_dsc('Create test vm to test zstack installation.')
    vm = create_vlan_vm()
    test_obj_dict.add_vm(vm)
    vm.check()

    vm_inv = vm.get_vm()
    vm_ip = vm_inv.vmNics[0].ip
    zstack_install_script = test_lib.test_config.zstackInstaller.text_
    target_file = '/root/zstack_installer.sh'
    test_lib.lib_scp_file_to_vm(vm_inv, zstack_install_script, target_file)

    ssh.make_ssh_no_password(vm_ip, test_lib.lib_get_vm_username(vm_inv), \
            test_lib.lib_get_vm_password(vm_inv))

    env_var = "ZSTACK_ALL_IN_ONE='%s' ZSTACK_PYPI_URL='%s' WEBSITE='%s'" % \
            (check_str(os.environ.get('ZSTACK_ALL_IN_ONE')), \
            check_str(os.environ.get('ZSTACK_PYPI_URL')), \
            check_str(os.environ.get('WEBSITE')))
    ssh_cmd = 'ssh  -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm_ip
    cmd = '%s "%s bash %s -d -a"' % (ssh_cmd, env_var, target_file)
    tmp_file = '/tmp/%s' % uuid.uuid1().get_hex()
    process_result = execute_shell_in_process(cmd, tmp_file)

    if process_result != 0:
        cmd = '%s "cat /tmp/zstack_installation.log"' % ssh_cmd
        execute_shell_in_process(cmd, tmp_file)
        test_util.test_fail('zstack installation failed')

    cmd = '%s "/usr/bin/zstack-cli LogInByAccount accountName=admin password=password"' % ssh_cmd
    process_result = execute_shell_in_process(cmd, tmp_file)
    if process_result != 0:
        test_util.test_fail('zstack-cli login failed')

    cmd = '%s "/usr/bin/zstack-cli CreateZone name=zone1 description=zone1"' % ssh_cmd
    process_result = execute_shell_in_process(cmd, tmp_file)
    if process_result != 0:
        test_util.test_fail('zstack-cli create zone failed')

    cmd = '%s "/usr/bin/zstack-cli QueryZone name=zone1 description=zone1"' % ssh_cmd
    process_result = execute_shell_in_process(cmd, tmp_file)
    if process_result != 0:
        test_util.test_fail('zstack-cli Query zone failed')

    os.system('rm -f %s' % tmp_file)
    vm.destroy()
    test_util.test_pass('ZStack installation Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
