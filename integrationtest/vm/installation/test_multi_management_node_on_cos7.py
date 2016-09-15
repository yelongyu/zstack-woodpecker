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

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
tmp_file = '/tmp/%s' % uuid.uuid1().get_hex()


def test():
    def test_fail(msg):
        os.system('rm -f %s' % tmp_file)
        test_util.test_fail(msg)

    test_util.test_dsc('Create 3 CentOS7 vm to test multi management node installation')
    image_name = os.environ.get('imageName_i_c7')
    vm1 = test_stub.create_vlan_vm(image_name)
    test_obj_dict.add_vm(vm1)
    vm2 = test_stub.create_vlan_vm(image_name)
    test_obj_dict.add_vm(vm2)
    vm3 = test_stub.create_vlan_vm(image_name)
    test_obj_dict.add_vm(vm3)
    if os.environ.get('zstackManagementIp') == None:
        vm1.check()
        vm2.check()
        vm3.check()
    else:
        time.sleep(60)

    vm1_inv = vm1.get_vm()
    vm1_ip = vm1_inv.vmNics[0].ip
    vm2_inv = vm2.get_vm()
    vm2_ip = vm2_inv.vmNics[0].ip
    vm3_inv = vm3.get_vm()
    vm3_ip = vm3_inv.vmNics[0].ip
    target_file = '/root/zstack-all-in-one.tgz'
    test_stub.prepare_test_env(vm1_inv, target_file)
    ssh_cmd1 = 'ssh  -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm1_ip
    ssh_cmd2 = 'ssh  -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm2_ip
    ssh_cmd3 = 'ssh  -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm3_ip

    test_util.test_dsc('Install ZStack on vm1')
    test_stub.copy_id_dsa(vm1_inv, ssh_cmd1, tmp_file)
    test_stub.copy_id_dsa_pub(vm1_inv)
    test_stub.execute_all_install(ssh_cmd1, target_file, tmp_file)
    test_stub.check_installation(ssh_cmd1, tmp_file, vm1_inv)

    test_util.test_dsc('Install multi management node on vm2 and vm3')
    host_list = 'root:password@%s root:password@%s' % (vm2_ip, vm3_ip)
    cmd = '%s "zstack-ctl add_multi_management --host-list=%s"' % (ssh_cmd1, host_list)
    process_result = test_stub.execute_shell_in_process(cmd, tmp_file)

    test_util.test_dsc('Check installation on vm1')
    test_stub.check_installation(ssh_cmd1, tmp_file, vm1_inv)

    test_util.test_dsc('Check installation on vm2')
    test_stub.copy_id_dsa(vm2_inv, ssh_cmd2, tmp_file)
    test_stub.copy_id_dsa_pub(vm2_inv)
    test_stub.check_installation(ssh_cmd2, tmp_file, vm2_inv)

    test_util.test_dsc('Check installation on vm3')
    test_stub.copy_id_dsa(vm3_inv, ssh_cmd3, tmp_file)
    test_stub.copy_id_dsa_pub(vm3_inv)
    test_stub.check_installation(ssh_cmd3, tmp_file, vm3_inv)

    os.system('rm -f %s' % tmp_file)
    vm1.destroy()
    test_obj_dict.rm_vm(vm1)
    vm2.destroy()
    test_obj_dict.rm_vm(vm2)
    vm3.destroy()
    test_obj_dict.rm_vm(vm3)
    test_util.test_pass('ZStack multi management nodes installation Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    os.system('rm -f %s' % tmp_file)
    test_lib.lib_error_cleanup(test_obj_dict)
