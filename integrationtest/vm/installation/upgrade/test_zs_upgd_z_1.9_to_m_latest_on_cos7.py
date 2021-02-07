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
vm_inv = None


def test():
    global vm_inv
    if os.path.exists('/home/zstack-package/') != True:
        test_util.test_skip("current test suite is zstack, but this case is for mevoco. Skip test")

    test_util.test_dsc('Create test vm to test zstack upgrade by -u.')

    image_name = os.environ.get('imageName_i_c7_z_1.9')
    iso_path = os.environ.get('iso_path')
    zstack_latest_version = os.environ.get('zstackLatestVersion')
    zstack_latest_path = os.environ.get('zstackLatestInstaller')
    vm_name = os.environ.get('vmName')
    upgrade_script_path = os.environ.get('upgradeScript')

    vm_inv = test_stub.create_vm_scenario(image_name, vm_name)
    vm_ip = vm_inv.vmNics[0].ip
    test_lib.lib_wait_target_up(vm_ip, 22)

    test_stub.make_ssh_no_password(vm_ip, tmp_file)

    test_util.test_dsc('Update MN IP')
    test_stub.update_mn_ip(vm_ip, tmp_file)
    test_stub.start_mn(vm_ip, tmp_file)
    test_stub.check_installation(vm_ip, tmp_file)
    #test_stub.create_sftp_backup_storage(vm_ip, tmp_file)

    test_util.test_dsc('Upgrade zstack to latest mevoco') 
    test_stub.update_iso(vm_ip, tmp_file, iso_path, upgrade_script_path)
    test_stub.upgrade_zstack(vm_ip, zstack_latest_path, tmp_file) 
    test_stub.check_zstack_version(vm_ip, tmp_file, zstack_latest_version)
    test_stub.start_mn(vm_ip, tmp_file)
    test_stub.check_mn_running(vm_ip, tmp_file)
    #test_stub.check_zstack_or_mevoco(vm_ip, tmp_file, 'ZStack-enterprise')
    #test_stub.check_zstack_or_mevoco(vm_ip, tmp_file, 'ZStack')
    test_stub.check_installation(vm_ip, tmp_file)
    #test_stub.reconnect_backup_storage(vm_ip, tmp_file)
    #test_stub.delete_backup_storage(vm_ip, tmp_file)

    os.system('rm -f %s' % tmp_file)
    test_stub.destroy_vm_scenario(vm_inv.uuid)
    test_util.test_pass('ZStack upgrade Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm_inv
    os.system('rm -f %s' % tmp_file)
    test_stub.destroy_vm_scenario(vm_inv.uuid)
