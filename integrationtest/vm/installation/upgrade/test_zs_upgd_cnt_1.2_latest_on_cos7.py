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
import zstacklib.utils.ssh as ssh

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
tmp_file = '/tmp/%s' % uuid.uuid1().get_hex()


def test():
    test_util.test_dsc('Create test vm to test zstack upgrade by -u.')

    if os.path.exists('/home/installation-package/zstack'):
        image_name = os.environ.get('imageName_i_c7_z_1.2')
    elif os.path.exists('/home/installation-package/mevoco'):
        image_name = os.environ.get('imageName_i_c7_m_1.2')

    vm = test_stub.create_vlan_vm(image_name)
    test_obj_dict.add_vm(vm)
    if os.environ.get('zstackManagementIp') == None:
        vm.check()
    else:
        time.sleep(60)

    #vm_inv = vm.get_vm()
    #vm_ip = vm_inv.vmNics[0].ip

    #ssh_cmd = 'ssh  -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm_ip
    #ssh.make_ssh_no_password(vm_ip, test_lib.lib_get_vm_username(vm_inv), \
    #        test_lib.lib_get_vm_password(vm_inv))
    #test_stub.copy_id_dsa(vm_inv, ssh_cmd, tmp_file)
    #test_stub.copy_id_dsa_pub(vm_inv)

    vm_inv = test_stub.create_vm_scenario(image_name, vm_name)
    vm_ip = vm_inv.vmNics[0].ip
    test_lib.lib_wait_target_up(vm_ip, 22)

    test_stub.make_ssh_no_password(vm_ip, tmp_file)

    test_util.test_dsc('Update MN IP')
    test_stub.update_mn_hostname(vm_ip, tmp_file)
    test_stub.update_mn_ip(vm_ip, tmp_file)
    #test_stub.reset_rabbitmq(vm_ip, tmp_file)
    test_stub.start_mn(vm_ip, tmp_file)
    test_stub.check_installation(vm_ip, tmp_file)


    #test_util.test_dsc('Update MN IP')
    #cmd = '%s "zstack-ctl change_ip --ip="%s ' % (ssh_cmd, vm_ip)
    #process_result = test_stub.execute_shell_in_process(cmd, tmp_file)
    #cmd = '%s "zstack-ctl start"' % ssh_cmd
    #process_result = test_stub.execute_shell_in_process(cmd, tmp_file)
    #test_stub.check_installation(ssh_cmd, tmp_file, vm_inv)

    pkg_num = 1.3
    curren_num = float(os.environ.get('releasePkgNum'))
    while pkg_num <= curren_num:
        test_util.test_dsc('Upgrade zstack to %s' % pkg_num)
        upgrade_target_file = '/root/zstack-upgrade-all-in-one.tgz'
        upgrade_pkg = os.environ.get('zstackPkg_%s' % pkg_num)
        test_stub.prepare_upgrade_test_env(vm_inv, upgrade_target_file, upgrade_pkg)
        test_stub.upgrade_zstack(ssh_cmd, upgrade_target_file, tmp_file)
        test_stub.check_zstack_version(ssh_cmd, tmp_file, vm_inv, str(pkg_num))
        test_stub.check_installation(ssh_cmd, tmp_file, vm_inv)
        pkg_num = pkg_num + 0.1

    test_util.test_dsc('Upgrade zstack to latest') 
    upgrade_target_file = '/root/zstack-upgrade-all-in-one.tgz' 
    test_stub.prepare_test_env(vm_inv, upgrade_target_file)
    test_stub.upgrade_zstack(ssh_cmd, upgrade_target_file, tmp_file) 
    zstack_latest_version = os.environ.get('zstackLatestVersion')
    test_stub.check_zstack_version(ssh_cmd, tmp_file, vm_inv, zstack_latest_version)
    test_stub.check_installation(ssh_cmd, tmp_file, vm_inv)

    os.system('rm -f %s' % tmp_file)
    vm.destroy()
    test_util.test_pass('ZStack upgrade Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    os.system('rm -f %s' % tmp_file)
    test_lib.lib_error_cleanup(test_obj_dict)
