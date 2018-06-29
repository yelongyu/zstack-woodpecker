'''
@author:fangxiao
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.operations.iam2_operations as iam2_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import time
import os
import apibinding.api_actions as api_actions
import zstackwoodpecker.operations.vxlan_operations as vxlan_ops
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.operations.deploy_operations as dep_ops
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.vpc_operations as vpc_ops

#test_obj_dict is to track test resource. They will be cleanup if there will be any exception in testing.
test_obj_dict = test_state.TestStateDict()

project_uuid = None
linked_account_uuid = None
project_operator_uuid = None
account_lists = None
test_stub = test_lib.lib_get_test_stub()
vni_range_uuid = None
vxlan_pool_uuid = None
l2_vxlan_network_uuid = None
account1_uuid = None
account2_uuid = None
platform_admin_uuid = None

def test():
    global linked_account_uuid,project_uuid,project_operator_uuid,account_lists,vni_range_uuid,vxlan_pool_uuid,l2_vxlan_network_uuid,account1_uuid,account2_uuid,platform_admin_uuid

    # create vxlan pool and vni range
    zone_uuid = res_ops.get_resource(res_ops.ZONE)[0].uuid
    cluster_uuid = res_ops.get_resource(res_ops.CLUSTER)[0].uuid
    vxlan_pool_name = 'vxlan_pool_name'

    vxlan_pool_uuid = vxlan_ops.create_l2_vxlan_network_pool(vxlan_pool_name,zone_uuid).uuid
    vxlan_ops.create_vni_range('vni_range',20,40,vxlan_pool_uuid)
        
    systemTags = ["l2NetworkUuid::%s::clusterUuid::%s::cidr::{172.20.0.1/16}"%(vxlan_pool_uuid,cluster_uuid)]
    net_ops.attach_l2_vxlan_pool(vxlan_pool_uuid,cluster_uuid,systemTags)
        
    # 1 create project
    project_name = 'test_share_project1'
    project = iam2_ops.create_iam2_project(project_name)
    project_uuid = project.uuid
    cond = res_ops.gen_query_conditions("name",'=',"test_share_project1")
    linked_account_uuid = res_ops.query_resource(res_ops.ACCOUNT,cond)[0].uuid

    # 2 create project operator
    project_operator_name = 'share_username1'
    project_operator_password = 'password'
    attributes = [{"name": "__ProjectOperator__", "value": project_uuid}]
    project_operator_uuid = iam2_ops.create_iam2_virtual_id(project_operator_name,project_operator_password,attributes=attributes).uuid

    # 3 login in project by project operator
    iam2_ops.add_iam2_virtual_ids_to_project([project_operator_uuid],project_uuid)
    project_operator_session_uuid = iam2_ops.login_iam2_virtual_id(project_operator_name,project_operator_password)
    project_login_uuid = iam2_ops.login_iam2_project(project_name,session_uuid=project_operator_session_uuid).uuid
    # todo:use the shared resources
        
    # 4 create platformAdmin and login
    username = 'username'
    password = 'password'
    platform_admin_uuid = iam2_ops.create_iam2_virtual_id(username, password).uuid
    attributes = [{"name":"__PlatformAdmin__"}]
    iam2_ops.add_attributes_to_iam2_virtual_id(platform_admin_uuid, attributes)
    platform_admin_session_uuid = iam2_ops.login_iam2_virtual_id(username, password)

        
    # 5 share platform admin resources to project 
    test_stub.share_admin_resource_include_vxlan_pool([linked_account_uuid],platform_admin_session_uuid)
    # use the shared resources to create vm
    vm = test_stub.create_vm(session_uuid=project_login_uuid)
    volume = test_stub.create_volume(session_uuid=project_login_uuid)
    test_obj_dict.add_volume(volume)
    test_obj_dict.add_vm(vm)
    l2_vxlan_network_uuid = vxlan_ops.create_l2_vxlan_network('l2_vxlan',vxlan_pool_uuid,zone_uuid,session_uuid=project_login_uuid).uuid
    virtual_router_offering_uuid = res_ops.get_resource(res_ops.VR_OFFERING)[0].uuid
    vpc_ops.create_vpc_vrouter('vpc_router',virtual_router_offering_uuid,session_uuid=project_login_uuid)
        
        
    # 6 revoke platform admin resources from project
    test_stub.revoke_admin_resource([linked_account_uuid],platform_admin_session_uuid)
        
       
        
    # 7 share to all
    #create_account
    account1_uuid = acc_ops.create_account('user1','password','Normal').uuid
    account2_uuid = acc_ops.create_account('user2','password','Normal').uuid
        
    account_lists = res_ops.query_resource(res_ops.ACCOUNT)
    for account in account_lists:
        test_stub.share_admin_resource_include_vxlan_pool([account.uuid],platform_admin_session_uuid)
        
            
    # 8 revoke resources from all
    for account in account_lists:
        test_stub.revoke_admin_resource([account.uuid],platform_admin_session_uuid)
        
        
            
    # 9 Negative test
    test_util.test_dsc('Doing negative test.Try to use the resources not shared to create vm')
    try:
        test_stub.create_vm(session_uuid=project_login_uuid)
    except:
        test_util.test_logger('Catch excepted excepttion.can not use the resources not shared to create vm')
    else:
        test_util.test_fail('Catch wrong logic:create vm success with the resources not shared ')
        
    test_util.test_dsc('Doing negative test.Try to use the resources not shared to create volume')
    try:
        test_stub.create_volume(session_uuid=project_login_uuid)
    except:
        test_util.test_logger('Catch excepted excepttion.can not use the resources not shared to create volume')
    else:
        test_util.test_fail('Catch wrong logic:create volume success with the resources not shared ')
    
    test_util.test_dsc('Doing negative test.Try to use the resources not shared to create vxlan network')
    try:
        vxlan_ops.create_l2_vxlan_network('l2_vxlan',vxlan_pool_uuid,zone_uuid,session_uuid=project_login_uuid)
    except:
        test_util.test_logger('Catch excepted excepttion.can not use the resources not shared to create l2 vxlan')
    else:
        test_util.test_fail('Catch wrong logic:create l2 vxlan success with the resources not shared ')
    
    test_util.test_dsc('Doing negative test.Try to use the resources not shared to create vpc_vrouter ')    
    try:
        vpc_ops.create_vpc_vrouter('vpc_router',virtual_router_offerings,session_uuid=project_login_uuid)
    except: 
        test_util.test_logger('Catch excepted excepttion.can not use the resources not shared to create vpc_router')
    else:
        test_util.test_fail('Catch wrong logic:create vpc_router success with the resources not shared ')
            
            
    # 10 delete
    acc_ops.logout(project_login_uuid)
    iam2_ops.delete_iam2_virtual_id(project_operator_uuid)
    iam2_ops.delete_iam2_project(project_uuid)
    iam2_ops.expunge_iam2_project(project_uuid)
    vni_range_uuid = res_ops.get_resource(res_ops.VNI_RANGE)[0].uuid
    vxlan_ops.delete_vni_range(vni_range_uuid)
    vpc_ops.remove_all_vpc_vrouter()
    test_lib.lib_error_cleanup(test_obj_dict)
        
        
    net_ops.delete_l2(vxlan_pool_uuid)
    net_ops.delete_l2(l2_vxlan_network_uuid)
        
        
    acc_ops.delete_account(account1_uuid)
    acc_ops.delete_account(account2_uuid)
    iam2_ops.delete_iam2_virtual_id(platform_admin_uuid)
def error_cleanup():
    global project_uuid,project_operator_uuid, vxlan_pool_uuid,vni_range_uuid,l2_vxlan_network_uuid,account1_uuid,account2_uuid

    if project_operator_uuid:
        iam2_ops.delete_iam2_virtual_id(project_operator_uuid)
    if project_uuid:
        iam2_ops.delete_iam2_project(project_uuid)
        iam2_ops.expunge_iam2_project(project_uuid)
        
                
    if vni_range_uuid:
        vxlan_ops.delete_vni_range(vni_range_uuid)
    vpc_ops.remove_all_vpc_vrouter()
    test_lib.lib_error_cleanup(test_obj_dict)
        
    if vxlan_pool_uuid:
        net_ops.delete_l2(vxlan_pool_uuid)
    if l2_vxlan_network_uuid:
        net_ops.delete_l2(l2_vxlan_network_uuid)
        
    if account1_uuid:
        acc_ops.delete_account(account1_uuid)
    if account2_uuid:
        acc_ops.delete_account(account2_uuid)
    if platform_admin_uuid:
        iam2_ops.delete_iam2_virtual_id(platform_admin_uuid)
