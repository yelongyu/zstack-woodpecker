'''

@author: YeTian  2018-03-29
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
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.operations.backupstorage_operations as bs_ops

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
tmp_file = '/tmp/%s' % uuid.uuid1().get_hex()
vm_inv = None


def test():
    global vm_inv,host_name, host_uuid, host_management_ip, vm_ip, bs_name, bs_uuid
    test_util.test_dsc('Create test vm to test zstack upgrade by -u.')

    image_name = os.environ.get('imageTestAlarm_230_mn')
    iso_path = os.environ.get('iso_path')
    zstack_latest_version = os.environ.get('zstackLatestVersion')
    zstack_latest_path = os.environ.get('zstackLatestInstaller')
    vm_name = os.environ.get('vmName') + image_name
    upgrade_script_path = os.environ.get('upgradeScript')

    vm_inv = test_stub.create_vm_scenario(image_name, vm_name)
    vm_ip = vm_inv.vmNics[0].ip
    test_lib.lib_wait_target_up(vm_ip, 22)
    #vm_ip = '172.20.197.159'
    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = vm_ip
    test_stub.make_ssh_no_password(vm_ip, tmp_file)

    test_util.test_logger('Update MN IP')
    test_stub.update_mn_hostname(vm_ip, tmp_file)
    test_stub.update_mn_ip(vm_ip, tmp_file)
    test_stub.start_mn(vm_ip, tmp_file)


    test_util.test_logger('Update host management IP and reconnect host')
    host_name = 'Host-1'
    cond1 = res_ops.gen_query_conditions('name', '=', host_name)
    test2 = res_ops.query_resource(res_ops.HOST, cond1)
    test_util.test_logger('aaaaa %s' % test2)
    #host_uuid = res_ops.query_resource(res_ops.HOST, conditions)[0].inventories[0]
    management_ip = vm_ip
    host_uuid = scen_ops.query_resource(management_ip, res_ops.HOST, cond1).inventories[0].uuid
    print 'test = ' 
    print  host_uuid
    host_management_ip = vm_ip
    host_ops.update_host(host_uuid, 'managementIp', host_management_ip)
    host_ops.reconnect_host(host_uuid)

    test_util.test_logger('Update bs IP and reconnect bs')
    bs_name = 'BS-1'
    cond2 = res_ops.gen_query_conditions('name', '=', bs_name)
    #bs_uuid = res_ops.query_resource(res_ops.BACKUP_STORAGE, conditions)[0].inventories[0].uuid    
    bs_uuid = scen_ops.query_resource(management_ip, res_ops.BACKUP_STORAGE, cond2).inventories[0].uuid
    bs_ip = vm_ip
    bs_ops.update_image_store_backup_storage_info(bs_uuid, 'hostname', bs_ip)
    bs_ops.reconnect_backup_storage(bs_uuid)

    #test_stub.check_installation(vm_ip, tmp_file)

    test_util.test_logger('Upgrade zstack to latest') 
    test_stub.update_iso(vm_ip, tmp_file, iso_path, upgrade_script_path)
    test_stub.upgrade_zstack(vm_ip, zstack_latest_path, tmp_file) 
    test_stub.check_zstack_version(vm_ip, tmp_file, zstack_latest_version)
    test_stub.start_mn(vm_ip, tmp_file)
    test_stub.check_installation(vm_ip, tmp_file)

    os.system('rm -f %s' % tmp_file)
    test_stub.destroy_vm_scenario(vm_inv.uuid)
    test_util.test_pass('ZStack upgrade Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm_inv
    os.system('rm -f %s' % tmp_file)
    if vm_inv:
        test_stub.destroy_vm_scenario(vm_inv.uuid)
    test_lib.lib_error_cleanup(test_obj_dict)
