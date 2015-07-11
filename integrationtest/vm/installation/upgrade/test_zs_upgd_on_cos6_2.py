'''

@author: Youyk
'''
import os
import tempfile
import uuid

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
tmp_file = '/tmp/%s' % uuid.uuid1().get_hex()


def test():
    test_util.test_dsc('Create test vm to test zstack all installation in CentOS6.')
    image_name = os.environ.get('imageName_i_c6')
    vm = test_stub.create_vlan_vm(image_name)
    test_obj_dict.add_vm(vm)
    vm.check()

    vm_inv = vm.get_vm()
    vm_ip = vm_inv.vmNics[0].ip
    target_file = '/root/zstack-all-in-one.tgz'
    test_stub.prepare_test_env(vm_inv, target_file)
    ssh_cmd = 'ssh  -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm_ip
    test_stub.execute_all_install(ssh_cmd, target_file, tmp_file)
    test_stub.check_installation(ssh_cmd, tmp_file)

    cmd = '%s "zstack-ctl upgrade_management_node --host=%s"' % (ssh_cmd, vm_ip)
    process_result = test_stub.execute_shell_in_process(cmd, tmp_file)
    if process_result != 0:
        test_fail('zstack upgrade management node failed in vm:%s' % vm_inv.uuid)

    cmd = '%s "zstack-ctl upgrade_db --host=%s"' % (ssh_cmd, vm_ip)
    process_result = test_stub.execute_shell_in_process(cmd, tmp_file)
    if process_result != 0:
        test_fail('zstack upgrade database failed in vm:%s' % vm_inv.uuid)

    cmd = '%s "zstack-ctl start_node"' % ssh_cmd
    process_result = test_stub.execute_shell_in_process(cmd, tmp_file)
    if process_result != 0:
        if 'no management-node-ready message received within' in open(tmp_file).read():
            times = 30
            cmd = '%s "zstack-ctl status"' % ssh_cmd
            while (times > 0):
                time.sleep(10)
                process_result = test_stub.execute_shell_in_process(cmd, tmp_file, 10, True)
                times -= 1
                if process_result == 0:
                    test_util.test_logger("management node start after extra %d seconds" % (30 - times + 1) * 10 )
                    break
            else:
                test_fail('start node failed in vm:%s' % vm_inv.uuid)

    test_stub.check_installation(ssh_cmd, tmp_file)
    os.system('rm -f %s' % tmp_file)
    vm.destroy()
    test_util.test_pass('ZStack installation Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    os.system('rm -f %s' % tmp_file)
    test_lib.lib_error_cleanup(test_obj_dict)
