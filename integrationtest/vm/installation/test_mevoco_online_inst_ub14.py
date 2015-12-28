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
    test_util.test_dsc('Create test vm to test Mevoco online installation in Ubuntu 14.04.')
    image_name = os.environ.get('imageName_i_u14')
    vm = test_stub.create_vlan_vm(image_name)
    test_obj_dict.add_vm(vm)
    vm.check()

    vm_inv = vm.get_vm()
    vm_ip = vm_inv.vmNics[0].ip
    test_stub.prepare_mevoco_test_env(vm_inv)
    ssh_cmd = 'ssh  -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm_ip
    test_stub.execute_mevoco_online_install(ssh_cmd, tmp_file)
    test_stub.check_installation(ssh_cmd, tmp_file, vm_inv)

    os.system('rm -f %s' % tmp_file)
    vm.destroy()
    test_util.test_pass('Mevoco installation Test Success on Ubuntu 14.04')

#Will be called only if exception happens in test().
def error_cleanup():
    os.system('rm -f %s' % tmp_file)
    test_lib.lib_error_cleanup(test_obj_dict)
