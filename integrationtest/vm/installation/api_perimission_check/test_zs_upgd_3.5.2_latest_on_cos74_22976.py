'''
#Cover 22976
based on test_zs_upgd_3.5.2_latest_on_cos74.py
Test the upgrade master from 3.5.2.53 & check API permissions
@author: Zhaohao
'''
import os
import tempfile
import uuid
import time

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstacklib.utils.ssh as ssh
import zstackwoodpecker.operations.scenario_operations as scen_ops

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
tmp_file = '/tmp/%s' % uuid.uuid1().get_hex()
vm_inv = None

def test():
    global vm_inv
    test_util.test_dsc('Create test vm to test zstack upgrade by -u.')

    image_name = os.environ.get('imageNameBase_352_mn_c74')
    c74_iso_path = os.environ.get('c74_iso_path')
    #iso_21_path = os.environ.get('iso_21_path')
    zstack_latest_version = os.environ.get('zstackLatestVersion')
    zstack_latest_path = os.environ.get('zstackLatestInstaller')
    vm_name = os.environ.get('vmName')
    upgrade_script_path = os.environ.get('upgradeScript')

    vm_inv = test_stub.create_vm_scenario(image_name, vm_name)
    vm_ip = vm_inv.vmNics[0].ip
    test_lib.lib_wait_target_up(vm_ip, 22)

    test_stub.make_ssh_no_password(vm_ip, tmp_file)

    test_util.test_logger('Update MN IP')
    test_stub.update_mn_hostname(vm_ip, tmp_file)
    test_stub.update_mn_ip(vm_ip, tmp_file)
    test_stub.stop_mn(vm_ip, tmp_file)
    test_stub.start_node(vm_ip, tmp_file)
    test_stub.start_mn(vm_ip, tmp_file)
    test_stub.check_mn_running(vm_ip, tmp_file)
    test_stub.create_vid(vm_ip, 'vid_test')
    pms1 = test_stub.get_vid_permissions(vm_ip, 'vid_test')
    #test_stub.check_installation(vm_ip, tmp_file)

    test_util.test_logger('Upgrade zstack to latest') 
    test_stub.update_c74_iso(vm_ip, tmp_file, c74_iso_path, upgrade_script_path)
    #test_stub.updatei_21_iso(vm_ip, tmp_file, iso_21_path, upgrade_script_path)
    test_stub.upgrade_zstack(vm_ip, zstack_latest_path, tmp_file) 
    test_stub.check_zstack_version(vm_ip, tmp_file, zstack_latest_version)
    test_stub.start_mn(vm_ip, tmp_file)
    test_stub.check_mn_running(vm_ip, tmp_file)

    pms2 = test_stub.get_vid_permissions(vm_ip, 'vid_test')
    test_stub.check_permissions(pms1, pms2)
    #test_stub.check_installation(vm_ip, tmp_file)

    os.system('rm -f %s' % tmp_file)
    test_stub.destroy_vm_scenario(vm_inv.uuid)
    test_util.test_pass('ZStack 3.5.2 to master upgrade Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm_inv
    os.system('rm -f %s' % tmp_file)
    if vm_inv:
        test_stub.destroy_vm_scenario(vm_inv.uuid)
    test_lib.lib_error_cleanup(test_obj_dict)
