'''

@author: MengLai
Updater: YeTian 2019-03-04
'''
import os
import tempfile
import uuid
import time

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstacklib.utils.ssh as ssh

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
tmp_file = '/tmp/%s' % uuid.uuid1().get_hex()
vm_inv = None


def test():
    global vm_inv
    test_util.test_dsc('Create test vm to test zstack upgrade by -u.')
    image_name = os.environ.get('imageName_i_c7_z_1.8')
    data_image_name = os.environ.get('data_volume_template')

    conditions = res_ops.gen_query_conditions('name', '=', data_image_name)
    data_image_uuid = res_ops.query_resource(res_ops.IMAGE, conditions)[0].uuid
    #iso_path = os.environ.get('iso_path')
    #iso_19_path = os.environ.get('iso_19_path')
    #iso_10_path = os.environ.get('iso_10_path')
    #iso_20_path = os.environ.get('iso_20_path')
    #iso_21_path = os.environ.get('iso_21_path')
    #iso_230_path = os.environ.get('iso_230_path')

    zstack_latest_version = os.environ.get('zstackLatestVersion')
    zstack_latest_path = os.environ.get('zstackLatestInstaller')
    vm_name = os.environ.get('vmName')
    upgrade_script_path = os.environ.get('upgradeScript')

    vm_inv = test_stub.create_vm_scenario(image_name, vm_name)
    vm_uuid = vm_inv.uuid
    ps_uuid = vm_inv.allVolumes[0].primaryStorageUuid
    vm_ip = vm_inv.vmNics[0].ip
    test_lib.lib_wait_target_up(vm_ip, 22)

    test_stub.make_ssh_no_password(vm_ip, tmp_file)
    
    data_volume_inv = vol_ops.create_volume_from_template(data_image_uuid, ps_uuid, name = 'data1')

    #vol_ops.attach_volume(data_volume_inv.uuid, vm_uuid)
    
    mount_point = '/testpath'
    test_stub.attach_mount_volume(data_volume_inv, vm_inv, mount_point)

    iso_19_path = '%s/iso/zstack_19.iso' % mount_point
    iso_10_path = '%s/iso/zstack_10.iso' % mount_point
    iso_20_path = '%s/iso/zstack_20.iso' % mount_point
    iso_21_path = '%s/iso/zstack_21.iso' % mount_point
    iso_230_path = '%s/iso/zstack_230.iso' % mount_point

    test_util.test_dsc('Update MN IP')
    test_stub.update_mn_hostname(vm_ip, tmp_file)
    test_stub.update_mn_ip(vm_ip, tmp_file)
    test_stub.reset_rabbitmq(vm_ip, tmp_file)
    test_stub.start_mn(vm_ip, tmp_file)
    #test_stub.check_installation(vm_ip, tmp_file)

    #test_stub.update_19_iso(vm_ip, tmp_file, iso_19_path, upgrade_script_path)
    test_stub.update_local_iso(vm_ip, tmp_file, iso_19_path, upgrade_script_path)

    #pkg_num = 1.9
    release_ver=['1.9','1.10','2.0.0','2.1.0','2.2.0','2.3.0','2.3.1']
    curren_num = float(os.environ.get('releasePkgNum'))
    for pkg_num in release_ver:
    #while pkg_num <= curren_num:
	#if str(pkg_num) == '1.9':
	#	test_stub.update_19_iso(vm_ip, tmp_file, iso_19_path, upgrade_script_path)
	if str(pkg_num) == '1.10':
		test_stub.update_local_iso(vm_ip, tmp_file, iso_10_path, upgrade_script_path)
	if str(pkg_num) == '2.0.0':
		test_stub.update_local_iso(vm_ip, tmp_file, iso_20_path, upgrade_script_path)
	if str(pkg_num) == '2.1.0':
		test_stub.update_local_iso(vm_ip, tmp_file, iso_21_path, upgrade_script_path)
	if str(pkg_num) == '2.3.0':
		test_stub.update_local_iso(vm_ip, tmp_file, iso_230_path, upgrade_script_path)
        test_util.test_logger('Upgrade zstack to %s' % pkg_num)
        #upgrade_pkg = os.environ.get('zstackPkg_%s' % pkg_num)
        upgrade_pkg = '%s/installation-package/zstack-installer_%s.bin' % (mount_point, pkg_num)
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
