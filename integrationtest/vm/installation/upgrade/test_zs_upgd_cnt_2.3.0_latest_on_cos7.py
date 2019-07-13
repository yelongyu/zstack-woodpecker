'''

@author: MengLai
Updater: YeTian 2019-03-04  use the local iso and bin upgrade the latest version by iso
'''
import os
import tempfile
import uuid
import time

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.operations.scenario_operations as sce_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstacklib.utils.ssh as ssh

zstack_management_ip = os.environ.get('zstackManagementIp')
test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
tmp_file = '/tmp/%s' % uuid.uuid1().get_hex()
vm_inv = None


def test():
    global vm_inv, data_volume_uuid
    test_util.test_dsc('Create test vm to test zstack upgrade by -u.')
    image_name = os.environ.get('imageNameBase_230_mn')
    data_image_name = os.environ.get('data_volume_template')

    conditions = res_ops.gen_query_conditions('name', '=', data_image_name)
    data_image_uuid = sce_ops.query_resource(zstack_management_ip, res_ops.IMAGE, conditions).inventories[0].uuid
    iso_path = os.environ.get('iso_path')

    zstack_latest_version = os.environ.get('zstackLatestVersion')
    zstack_latest_path = os.environ.get('zstackLatestInstaller')
    vm_name = os.environ.get('vmName')
    upgrade_script_path = os.environ.get('upgradeScript')
    #host_name = 'hpe-sh27-ls'
    #vm_inv = test_stub.create_vm_scenario(image_name, vm_name, host_name)
    vm_inv = test_stub.create_vm_scenario(image_name, vm_name)
    vm_uuid = vm_inv.uuid
    ps_uuid = vm_inv.allVolumes[0].primaryStorageUuid
    print ps_uuid
    host_uuid = vm_inv.hostUuid
    print host_uuid
    print data_image_uuid
    vm_ip = vm_inv.vmNics[0].ip
    test_lib.lib_wait_target_up(vm_ip, 22)

    test_stub.make_ssh_no_password(vm_ip, tmp_file)
    test_util.test_dsc('create data volume from template') 
    data_volume_name='Test_installation_data_volume_for_nightly'
    data_volume_inv = sce_ops.create_volume_from_template(zstack_management_ip, data_image_uuid, ps_uuid, data_volume_name, host_uuid)
    data_volume_uuid = data_volume_inv.uuid

    #test_util.test_dsc('query data volume') 
    #data_volume_name = 'Test_installation_data_volume_for_nightly'
    #conditions = res_ops.gen_query_conditions('name', '=', data_volume_name)
    #data_volume_uuid = res_ops.query_resource(res_ops.VOLUME, conditions)[0].uuid

    test_util.test_dsc('attach the data volume to vm') 
    sce_ops.attach_volume(zstack_management_ip, data_volume_uuid, vm_uuid)
    
    test_util.test_dsc('mount the disk in vm') 
    mount_point = '/testpath'
    test_stub.mount_volume(vm_ip, mount_point, tmp_file)

    iso_232_path = '%s/iso/zstack_230.iso' % mount_point
    iso_240_path = '%s/iso/zstack_240.iso' % mount_point
    iso_250_path = '%s/iso/zstack_250.iso' % mount_point
    iso_260_path = '%s/iso/zstack_260.iso' % mount_point
    iso_301_path = '%s/iso/zstack_301.iso' % mount_point
    iso_310_path = '%s/iso/zstack_310.iso' % mount_point
    iso_320_path = '%s/iso/zstack_320.iso' % mount_point
    iso_330_path = '%s/iso/zstack_330.iso' % mount_point

    test_util.test_dsc('Update MN IP')
    test_stub.update_mn_hostname(vm_ip, tmp_file)
    test_stub.update_mn_ip(vm_ip, tmp_file)
    test_stub.reset_rabbitmq(vm_ip, tmp_file)
    test_stub.start_mn(vm_ip, tmp_file)
    test_stub.stop_mn(vm_ip, tmp_file)
    #test_stub.check_installation(vm_ip, tmp_file)

    #test_stub.update_local_iso(vm_ip, tmp_file, iso_19_path, upgrade_script_path)

    release_ver=['2.3.1','2.3.2','2.4.0','2.5.0','2.6.0','3.0.0','3.0.1','3.1.0','3.1.3','3.2.0','3.3.0']
    curren_num = float(os.environ.get('releasePkgNum'))
    for pkg_num in release_ver:
	if str(pkg_num) == '2.3.2':
		test_stub.update_local_iso(vm_ip, tmp_file, iso_232_path, upgrade_script_path)
	if str(pkg_num) == '2.4.0':
		test_stub.update_local_iso(vm_ip, tmp_file, iso_240_path, upgrade_script_path)
	if str(pkg_num) == '2.5.0':
		test_stub.update_local_iso(vm_ip, tmp_file, iso_250_path, upgrade_script_path)
	if str(pkg_num) == '2.6.0':
		test_stub.update_local_iso(vm_ip, tmp_file, iso_260_path, upgrade_script_path)
	if str(pkg_num) == '3.0.1':
		test_stub.update_local_iso(vm_ip, tmp_file, iso_301_path, upgrade_script_path)
	if str(pkg_num) == '3.1.0':
		test_stub.update_local_iso(vm_ip, tmp_file, iso_310_path, upgrade_script_path)
	if str(pkg_num) == '3.2.0':
		test_stub.update_local_iso(vm_ip, tmp_file, iso_320_path, upgrade_script_path)
	if str(pkg_num) == '3.3.0':
		test_stub.update_local_iso(vm_ip, tmp_file, iso_330_path, upgrade_script_path)
        test_util.test_logger('Upgrade zstack to %s' % pkg_num)
        upgrade_pkg = '%s/installation-package/zstack-installer-%s.bin' % (mount_point, pkg_num)
        test_stub.upgrade_old_zstack(vm_ip, upgrade_pkg, tmp_file) 
        test_stub.start_node(vm_ip, tmp_file)
        test_stub.start_mn(vm_ip, tmp_file)
        test_stub.check_zstack_version(vm_ip, tmp_file, str(pkg_num))
        test_stub.stop_mn(vm_ip, tmp_file)

    test_util.test_dsc('Upgrade zstack to latest') 

    test_stub.update_iso(vm_ip, tmp_file, iso_path, upgrade_script_path)
    test_stub.upgrade_zstack(vm_ip, zstack_latest_path, tmp_file) 
    test_stub.start_node(vm_ip, tmp_file)
    test_stub.start_mn(vm_ip, tmp_file)
    test_stub.check_mn_running(vm_ip, tmp_file)
    test_stub.check_zstack_version(vm_ip, tmp_file, zstack_latest_version)
    test_stub.check_installation(vm_ip, tmp_file)

    os.system('rm -f %s' % tmp_file)
    sce_ops.detach_volume(zstack_management_ip, data_volume_uuid, vm_uuid)
    sce_ops.delete_volume(zstack_management_ip, data_volume_uuid)
    sce_ops.expunge_volume(zstack_management_ip, data_volume_uuid)
    test_stub.destroy_vm_scenario(vm_inv.uuid)
    test_util.test_pass('''ZStack upgrade '2.3.1','2.3.2','2.4.0','2.5.0','2.6.0','3.0.0','3.0.1','3.1.0','3.1.3','3.2.0','3.3.0'Test Success''')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm_inv, data_volume_uuid
    os.system('rm -f %s' % tmp_file)
    vol_ops.delete_volume(data_volume_uuid)
    vol_ops.expunge_volume(data_volume_uuid)
    test_stub.destroy_vm_scenario(vm_inv.uuid)
