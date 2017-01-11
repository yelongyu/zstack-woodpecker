'''

@author: MengLai
'''
import os
import tempfile
import uuid
import time

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.console_operations as cons_ops 
import zstacklib.utils.ssh as ssh

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
tmp_file = '/tmp/%s' % uuid.uuid1().get_hex()

def test():
    test_util.test_dsc('Create test vm to test zstack installation with console proxy.')

    image_name = os.environ.get('imageName_i_offline')

    vm = test_stub.create_vlan_vm(image_name)
    test_obj_dict.add_vm(vm)
    if os.environ.get('zstackManagementIp') == None:
        vm.check()
    else:
        time.sleep(60)

    vm_inv = vm.get_vm()
    vm_ip = vm_inv.vmNics[0].ip
    vip = '172.20.198.1'
    if vip == vm_ip:
        vip = '172.20.198.2'

    ssh_cmd = 'ssh  -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm_ip
    ssh.make_ssh_no_password(vm_ip, test_lib.lib_get_vm_username(vm_inv), test_lib.lib_get_vm_password(vm_inv))
    cmd = '%s ifconfig eth0:0 %s up' % (ssh_cmd, vip)
    process_result = test_stub.execute_shell_in_process(cmd, tmp_file)

    target_file = '/root/zstack-all-in-one.tgz'
    test_stub.prepare_test_env(vm_inv, target_file)
    args = '-o -C %s -I %s' % (vip, vm_ip)
    test_stub.execute_install_with_args(ssh_cmd, args, target_file, tmp_file)
    test_stub.check_installation(ssh_cmd, tmp_file, vm_inv)

    cmd = '%s cat /usr/local/zstack/apache-tomcat/webapps/zstack/WEB-INF/classes/zstack.properties | grep \'consoleProxyOverriddenIp = %s\'' % (ssh_cmd, vip)
    (process_result, check_result) = test_stub.execute_shell_in_process_stdout(cmd, tmp_file)
    check_result = check_result[:-1]
    test_util.test_dsc('cat result: |%s|' % check_result)
    expect_result = "consoleProxyOverriddenIp = %s" % vip
    if check_result != expect_result:
        test_util.test_fail('Fail to install ZStack with console proxy')

    os.system('rm -f %s' % tmp_file)
    vm.destroy()
    test_util.test_pass('ZStack installation Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    os.system('rm -f %s' % tmp_file)
    test_lib.lib_error_cleanup(test_obj_dict)
