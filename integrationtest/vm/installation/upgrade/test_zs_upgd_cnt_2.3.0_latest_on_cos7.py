'''

@author: Yetian update(1) 2018-11-26
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
    test_util.test_dsc('Create test vm to test zstack upgrade by -u.')
    image_name = os.environ.get('imageNameBase_230_mn')
    iso_path = os.environ.get('iso_path')
    iso_232_path = os.environ.get('iso_232_path')
    iso_240_path = os.environ.get('iso_240_path')
    iso_250_path = os.environ.get('iso_250_path')
    iso_260_path = os.environ.get('iso_260_path')
    iso_301_path = os.environ.get('iso_301_path')
    iso_310_path = os.environ.get('iso_310_path')
    zstack_latest_version = os.environ.get('zstackLatestVersion')
    zstack_latest_path = os.environ.get('zstackLatestInstaller')
    vm_name = os.environ.get('vmName')
    upgrade_script_path = os.environ.get('upgradeScript')

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

    #test_stub.update_iso(vm_ip, tmp_file, iso_path, upgrade_script_path)

    #pkg_num = 1.9
    release_ver=['2.3.1','2.3.2','2.4.0','2.5.0','2.6.0','3.0.0','3.0.1','3.1.1']
    curren_num = float(os.environ.get('releasePkgNum'))
    for pkg_num in release_ver:
    #while pkg_num <= curren_num:
	if str(pkg_num) == '2.3.2':
		test_stub.update_iso(vm_ip, tmp_file, iso_232_path, upgrade_script_path)
	if str(pkg_num) == '2.4.0':
		test_stub.update_iso(vm_ip, tmp_file, iso_240_path, upgrade_script_path)
	if str(pkg_num) == '2.5.0':
		test_stub.update_iso(vm_ip, tmp_file, iso_250_path, upgrade_script_path)
	if str(pkg_num) == '2.6.0':
		test_stub.update_iso(vm_ip, tmp_file, iso_260_path, upgrade_script_path)
	if str(pkg_num) == '3.0.1':
		test_stub.update_iso(vm_ip, tmp_file, iso_301_path, upgrade_script_path)
	if str(pkg_num) == '3.1.0':
		test_stub.update_iso(vm_ip, tmp_file, iso_310_path, upgrade_script_path)
        test_util.test_logger('Upgrade zstack to %s' % pkg_num)
        upgrade_pkg = os.environ.get('zstackPkg_%s' % pkg_num)
        test_stub.upgrade_zstack(vm_ip, upgrade_pkg, tmp_file) 
        test_stub.start_mn(vm_ip, tmp_file)
        test_stub.check_zstack_version(vm_ip, tmp_file, str(pkg_num))

    test_util.test_dsc('Upgrade zstack to latest') 
    test_stub.update_iso(vm_ip, tmp_file, iso_path, upgrade_script_path)
    test_stub.upgrade_zstack(vm_ip, zstack_latest_path, tmp_file) 
    test_stub.start_mn(vm_ip, tmp_file)
    test_stub.check_mn_running(vm_ip, tmp_file)
    test_stub.check_zstack_version(vm_ip, tmp_file, zstack_latest_version)
    test_stub.check_installation(vm_ip, tmp_file)

    os.system('rm -f %s' % tmp_file)
    test_stub.destroy_vm_scenario(vm_inv.uuid)
    test_util.test_pass('ZStack upgrade Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm_inv
    os.system('rm -f %s' % tmp_file)
    test_stub.destroy_vm_scenario(vm_inv.uuid)
