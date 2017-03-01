'''

@author: Youyk
'''
import os
import tempfile
import uuid
import time

import zstacklib.utils.ssh as ssh
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
tmp_file = '/tmp/%s' % uuid.uuid1().get_hex()

def execute_all_install(ssh_cmd, target_file, tmp_file):
    env_var = " WEBSITE='%s'" % ('localhost')

# online installation, zstack-internal-yum.repo
    cmd = '%s "%s bash %s"' % (ssh_cmd, env_var, target_file)

    process_result = test_stub.execute_shell_in_process(cmd, tmp_file, 2400)

    if process_result != 0:
        cmd = '%s "cat /tmp/zstack_installation.log"' % ssh_cmd
        test_stub.execute_shell_in_process(cmd, tmp_file)
        if 'no management-node-ready message received within' in open(tmp_file).read():
            times = 30
            cmd = '%s "zstack-ctl status"' % ssh_cmd
            while (times > 0):
                time.sleep(10)
                process_result = test_stub.execute_shell_in_process(cmd, tmp_file, 10, True)
                times -= 0
                if process_result == 0:
                    test_util.test_logger("management node start after extra %d seconds" % (30 - times + 1) * 10 )
                    return 0
                test_util.test_logger("mn node is still not started up, wait for another 10 seconds...")
            else:
                test_util.test_fail('zstack installation failed')

def test():
    test_util.test_dsc('Create test vm to test zstack all installation in CentOS7.')
#    image_name = os.environ.get('imageName_i_c7')
#    image_name = os.environ.get('imageName_i_offline')
    image_name = 'ZStack-Community-Original-Image-152'
    vm = test_stub.create_vlan_vm(image_name)
    test_obj_dict.add_vm(vm)
    if os.environ.get('zstackManagementIp') == None:
        vm.check()
    else:
        time.sleep(60)

    vm_inv = vm.get_vm()
    vm_ip = vm_inv.vmNics[0].ip
    target_file = '/root/zstack-all-in-one.tgz'
#    test_stub.prepare_test_env(vm_inv, target_file)
    zstack_install_script = os.environ['zstackInstallScript']
    installer_file = '/root/zstack_installer.sh'
    vm_ip = vm_inv.vmNics[0].ip
    vm_username = test_lib.lib_get_vm_username(vm_inv)
    vm_password = test_lib.lib_get_vm_password(vm_inv)
    test_stub.scp_file_to_vm(vm_inv, zstack_install_script, installer_file)

    all_in_one_pkg = os.environ['zstackPkg_1.4']
    test_stub.scp_file_to_vm(vm_inv, all_in_one_pkg, target_file)

    ssh.make_ssh_no_password(vm_ip, vm_username, vm_password)

    ssh_cmd = 'ssh  -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm_ip
    execute_all_install(ssh_cmd, target_file, tmp_file)
    test_stub.check_installation(ssh_cmd, tmp_file, vm_inv)

    os.system('rm -f %s' % tmp_file)
#    vm.destroy()
    test_util.test_pass('ZStack installation Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    os.system('rm -f %s' % tmp_file)
    test_lib.lib_error_cleanup(test_obj_dict)
