'''

@author: Youyk
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

    test_util.test_dsc('Create 2 CentOS6 vm to test zstack installation. Rabbitmq server is on different node with zstack management node. ZStack management node will also be started in 2 hosts.')
    image_name = os.environ.get('imageName_i_c6')
    vm1 = test_stub.create_vlan_vm(image_name)
    test_obj_dict.add_vm(vm1)
    vm2 = test_stub.create_vlan_vm(image_name)
    test_obj_dict.add_vm(vm2)
    vm1.check()
    vm2.check()

    vm1_inv = vm1.get_vm()
    vm1_ip = vm1_inv.vmNics[0].ip
    vm2_inv = vm2.get_vm()
    vm2_ip = vm2_inv.vmNics[0].ip
    target_file = '/root/zstack-all-in-one.tgz'
    test_stub.prepare_test_env(vm1_inv, target_file)
    ssh_cmd1 = 'ssh  -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm1_ip
    ssh_cmd2 = 'ssh  -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm2_ip
    test_stub.only_install_zstack(ssh_cmd1, target_file, tmp_file)

    test_stub.copy_id_dsa(vm1_inv, ssh_cmd1, tmp_file)
    test_stub.copy_id_dsa_pub(vm2_inv)

    cmd = '%s "zstack-ctl install_db --host=%s"' % (ssh_cmd1, vm2_ip)
    process_result = test_stub.execute_shell_in_process(cmd, tmp_file)
    if process_result != 0:
        test_fail('zstack install db failed in vm:%s' % vm2_inv.uuid)
    test_util.test_dsc("install db on vm2 success")

    cmd = '%s "zstack-ctl deploydb --host=%s"' % (ssh_cmd1, vm2_ip)
    process_result = test_stub.execute_shell_in_process(cmd, tmp_file)
    if process_result != 0:
        test_fail('zstack deploy db failed in vm:%s' % vm2_inv.uuid)
    test_util.test_dsc("deploy db on vm2 success")

    cmd = '%s "zstack-ctl install_rabbitmq --host=%s"' % (ssh_cmd1, vm2_ip)
    process_result = test_stub.execute_shell_in_process(cmd, tmp_file)
    if process_result != 0:
        test_fail('zstack install rabbitmq failed in vm:%s' % vm1_inv.uuid)
    test_util.test_dsc("install rabbitmq on vm2 success")

    cmd = '%s "rabbitmqctl add_user zstack zstack123; rabbitmqctl set_user_tags zstack administrator; rabbitmqctl change_password zstack zstack123; rabbitmqctl set_permissions -p / zstack \\\".*\\\" \\\".*\\\" \\\".*\\\""' % ssh_cmd2
    process_result = test_stub.execute_shell_in_process(cmd, tmp_file)
    if process_result != 0:
        test_fail('zstack set rabbitmq username/password failed in vm:%s' % vm2_inv.uuid)

    test_util.test_dsc("set rabbitmq permissions on vm2 success")

    cmd = '%s "zstack-ctl configure CloudBus.rabbitmqUsername=zstack; zstack-ctl configure CloudBus.rabbitmqPassword=zstack123; zstack-ctl save_config"' % ssh_cmd1
    process_result = test_stub.execute_shell_in_process(cmd, tmp_file)
    if process_result != 0:
        test_fail('set rabbitmq config failed in vm:%s' % vm1_inv.uuid)
    test_util.test_dsc("config rabbitmq configure on vm1 success")

    cmd = '%s "zstack-ctl install_management_node --remote=%s"' % (ssh_cmd1, vm2_ip)
    process_result = test_stub.execute_shell_in_process(cmd, tmp_file)
    if process_result != 0:
        test_fail('zstack install mn failed in vm:%s' % vm2_inv.uuid)
    test_util.test_dsc("install mn on vm2 success")

    cmd = '%s "zstack-ctl configure --duplicate-to-remote=%s"' % (ssh_cmd1, vm2_ip)
    process_result = test_stub.execute_shell_in_process(cmd, tmp_file)
    if process_result != 0:
        test_fail('zstack install mn failed in vm:%s' % vm2_inv.uuid)
    test_util.test_dsc("duplicate zstack mn configure to vm2 success")

    cmd = '%s "zstack-ctl configure management.server.ip=%s"' % (ssh_cmd2, vm2_ip)
    process_result = test_stub.execute_shell_in_process(cmd, tmp_file)
    if process_result != 0:
        test_fail('set zstack-ctl config failed in vm:%s' % vm2_inv.uuid)

    cmd = '%s "zstack-ctl install_ui --host=%s"' % (ssh_cmd1, vm2_ip)
    process_result = test_stub.execute_shell_in_process(cmd, tmp_file)
    if process_result != 0:
        test_fail('zstack install ui failed in vm:%s' % vm2_inv.uuid)
    test_util.test_dsc("install ui to vm2 success")

    cmd = '%s "zstack-ctl install_ui --host=%s"' % (ssh_cmd1, vm1_ip)
    process_result = test_stub.execute_shell_in_process(cmd, tmp_file)
    if process_result != 0:
        test_fail('zstack install ui failed in vm:%s' % vm1_inv.uuid)
    test_util.test_dsc("install ui to vm1 success")

    cmd = '%s "zstack-ctl start_node"' % ssh_cmd1
    process_result = test_stub.execute_shell_in_process(cmd, tmp_file)
    if process_result != 0:
        if 'no management-node-ready message received within' in open(tmp_file).read():
            times = 20
            cmd = '%s "zstack-ctl status"' % ssh_cmd1
            while (times > 0):
                time.sleep(10)
                process_result = test_stub.execute_shell_in_process(cmd, tmp_file, 10, True)
                times -= 1
                if process_result == 0:
                    test_util.test_logger("management node1 start after extra %d seconds" % (20 - times + 1) * 10 )
                    break
            else:
                test_fail('start node failed in vm:%s' % vm1_inv.uuid)

    cmd = '%s "zstack-ctl start_node --remote=%s"' % (ssh_cmd1, vm2_ip)
    process_result = test_stub.execute_shell_in_process(cmd, tmp_file)
    if process_result != 0:
        if 'no management-node-ready message received within' in open(tmp_file).read():
            times = 20
            cmd = '%s "zstack-ctl status"' % ssh_cmd2
            while (times > 0):
                time.sleep(10)
                process_result = test_stub.execute_shell_in_process(cmd, tmp_file, 10, True)
                times -= 1
                if process_result == 0:
                    test_util.test_logger("management node2 start after extra %d seconds" % (20 - times + 1) * 10 )
                    break
            else:
                test_fail('start remote node failed in vm:%s' % vm1_inv.uuid)

    test_stub.check_installation(ssh_cmd1, tmp_file)
    test_stub.check_installation(ssh_cmd2, tmp_file)

    os.system('rm -f %s' % tmp_file)
    vm1.destroy()
    test_obj_dict.rm_vm(vm1)
    vm2.destroy()
    test_obj_dict.rm_vm(vm2)
    test_util.test_pass('ZStack multi nodes installation Test Success on 2 CentOS6.')

#Will be called only if exception happens in test().
def error_cleanup():
    os.system('rm -f %s' % tmp_file)
    test_lib.lib_error_cleanup(test_obj_dict)
