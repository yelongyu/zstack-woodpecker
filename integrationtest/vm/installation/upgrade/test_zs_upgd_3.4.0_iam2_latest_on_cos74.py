# -*- coding:utf-8 -*-

'''
Test the upgrade master from 3.4.0.1736 
2 zone, 3 projects, 10 users, 2 project templates, 2 Organization, 4 platform admin
@author: YeTian  2019-05-17
'''
import os
import tempfile
import uuid
import time

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstacklib.utils.ssh as ssh
import zstackwoodpecker.operations.scenario_operations as sce_ops
import zstackwoodpecker.operations.iam2_operations as iam2_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.deploy_operations as dep_ops
import apibinding.api_actions as api_actions
import zstackwoodpecker.operations.account_operations as acc_ops
import hashlib

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
tmp_file = '/tmp/%s' % uuid.uuid1().get_hex()
vm_inv = None


def test():
    global vm_inv, test_a_seesion, test_b_seesion
    test_util.test_dsc('Create test vm to test zstack upgrade by -u.')

    image_name = os.environ.get('imageNameBase_340_mn_c74_iam2')
    c74_iso_path = os.environ.get('c74_iso_path')
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
    test_stub.check_installation(vm_ip, tmp_file)

    test_util.test_logger('Upgrade zstack to latest') 
    test_stub.update_c74_iso(vm_ip, tmp_file, c74_iso_path, upgrade_script_path)
    #test_stub.updatei_21_iso(vm_ip, tmp_file, iso_21_path, upgrade_script_path)
    test_stub.upgrade_zstack(vm_ip, zstack_latest_path, tmp_file) 
    test_stub.check_zstack_version(vm_ip, tmp_file, zstack_latest_version)
    test_stub.start_mn(vm_ip, tmp_file)
    test_stub.check_mn_running(vm_ip, tmp_file)
    test_stub.check_installation(vm_ip, tmp_file)

    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = vm_ip

    #check normal account is not work  and create new normal account
    test_util.test_dsc('check normal account is not work')
    account_name = 'test2_normal_account'
    account_pass = '123456'
    test_account = acc_ops.create_normal_account(account_name, account_pass)
    test_account_uuid = test_account.uuid
    test_account_session = acc_ops.login_by_account(account_name, account_pass)

    account_namea = 'a'
    account_nameb = 'b'
    account_pass = hashlib.sha512('123456').hexdigest()
    test_a_session = acc_ops.login_by_account(account_namea, account_pass)
    test_b_seesion = acc_ops.login_by_account(account_nameb, account_pass)
    conditions = res_ops.gen_query_conditions('name', '=', 'a')
    zstack_management_ip = vm_ip
    a_uuid = sce_ops.query_resource(zstack_management_ip, res_ops.ACCOUNT, conditions, session_uuid = test_a_session).inventories[0].uuid
    try:
        acc_ops.delete_account(a_uuid, session_uuid = test_a_session)   
    except:
	print "Test results were right, normal account a can not delete account a"
    	pass

    test_util.test_dsc('check normal account a whether can delete the host')
    host_uuid = sce_ops.query_resource(zstack_management_ip, res_ops.HOST, session_uuid = test_a_session).inventories[0].uuid
    try:
        host_ops.delete_host(host_uuid, session_uuid = test_a_session)   
    except:
	print "Test results were right, normal account a can not delete host"
	pass

    test_b_session = acc_ops.login_by_account(account_nameb, account_pass)
     
    #check iam2 is not work
    test_util.test_dsc('check iam2 is not work')

    project_name = 'project_a'
    iam2_user1 = 'a1'
    iam2_user2 = 'a2'
    project_a1_session_uuid = iam2_ops.login_iam2_virtual_id(iam2_user1, account_pass)
    project_user1_login_uuid = iam2_ops.login_iam2_project(project_name,session_uuid=project_a1_session_uuid).uuid

    try:
        acc_ops.delete_account(a_uuid, session_uuid = project_user1_login_uuid)   
    except:
	print "Test results were right, normal account a can not delete account a"
    	pass

    test_util.test_dsc('check iam2 a1 whether can delete the host')
    try:
        host_ops.delete_host(host_uuid, session_uuid = project_user1_login_uuid)   
    except:
	print "Test results were right, iam2 a1 can not delete host"
    test_util.test_dsc('check iam2 a1 is not work')


    test_util.test_dsc('check project admin is not work')
    project_admin_name = '平台管理员-all'
    project_admin_session = iam2_ops.login_iam2_virtual_id(project_admin_name, account_pass)   
    acc_ops.delete_account(test_account_uuid, session_uuid = project_admin_session)   

    project_nodeladmin_name = 'nodeladmin'
    project_nodeladmin_session = iam2_ops.login_iam2_virtual_id(project_nodeladmin_name, account_pass)   
    test_util.test_dsc('check nodeladmin whether can delete the normal account a')
    try:
        acc_ops.delete_account(a_uuid, session_uuid = project_nodeladmin_session)   
    except:
	print "Test results were right, normal account a can not delete account a"
    	pass

    test_util.test_dsc('check nodeladminwhether can delete the host')
    try:
        host_ops.delete_host(host_uuid, session_uuid = project_nodeladmin_session)
    except:
	print "Test results were right, nodeladmincan not delete host"
	pass

    os.system('rm -f %s' % tmp_file)
    test_stub.destroy_vm_scenario(vm_inv.uuid)
    test_util.test_pass('ZStack 3.4.0 iam2 to master upgrade Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm_inv
    os.system('rm -f %s' % tmp_file)
    if vm_inv:
        test_stub.destroy_vm_scenario(vm_inv.uuid)
    test_lib.lib_error_cleanup(test_obj_dict)
