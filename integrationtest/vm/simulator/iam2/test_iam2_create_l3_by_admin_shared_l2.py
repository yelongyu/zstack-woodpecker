'''

@date 2019-04-21  normal account create vm use by self L3 network, admin share L2
@auth  yetian
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
import zstackwoodpecker.operations.scenario_operations as sce_ops
import hashlib

_config_ = {
        'timeout' : 2000,
        'noparallel' : True
        }

#test_obj_dict is to track test resource. They will be cleanup if there will be any exception in testing.
test_obj_dict = test_state.TestStateDict()

zstack_management_ip = os.environ.get('zstackManagementIp')
project_uuid = None
linked_account_uuid = None
project_operator_uuid = None
test_stub = test_lib.lib_get_test_stub()
l2_vlan_network_uuid = None
test_account_uuid = None

def test():
    global linked_account_uuid,project_uuid,project_operator_uuid,account_lists,l2_uuid,account1_uuid,account2_uuid

    zone_uuid = res_ops.get_resource(res_ops.ZONE)[0].uuid
    cluster_uuid = res_ops.get_resource(res_ops.CLUSTER)[0].uuid
    # 1 create project
    project_name = 'test_shared_project1'
    project = iam2_ops.create_iam2_project(project_name)
    project_uuid = project.uuid
    linked_account_uuid = project.linkedAccountUuid

    # 2 create project operator
    project_operator_name = 'username_share1'
    project_operator_password = 'password'
    attributes = [{"name": "__ProjectOperator__", "value": project_uuid}]
    project_operator_uuid = iam2_ops.create_iam2_virtual_id(project_operator_name,project_operator_password,attributes=attributes).uuid
    # 3 login in project by project operator
    iam2_ops.add_iam2_virtual_ids_to_project([project_operator_uuid],project_uuid)
    project_operator_session_uuid = iam2_ops.login_iam2_virtual_id(project_operator_name,project_operator_password)
    project_login_uuid = iam2_ops.login_iam2_project(project_name,session_uuid=project_operator_session_uuid).uuid

    l2_inv = net_ops.create_l2_vlan('L2_vlan_2221', 'eth0', zone_uuid, '2221')   
    l2_uuid = l2_inv.inventory.uuid

    test_util.test_dsc('share admin resoure to normal account')
    cond = res_ops.gen_query_conditions('name', '=', 'L2_vlan_2221')
    flat_l2_uuid = res_ops.query_resource(res_ops.L2_NETWORK, cond)[0].uuid
    acc_ops.share_resources([linked_account_uuid], [flat_l2_uuid])

    # ut_util.test_dsc('create L3_flat_network names is L3_flat_network by normal account')
    l3_inv = sce_ops.create_l3(zstack_management_ip, 'l3_flat_network', 'L3BasicNetwork', flat_l2_uuid, 'local.com', session_uuid = project_login_uuid)
    l3_uuid = l3_inv.inventory.uuid

    l3_dns = '223.5.5.5'
    start_ip = '192.168.123.2'
    end_ip = '192.168.123.10'
    gateway = '192.168.123.1'
    netmask = '255.255.255.0'

    test_util.test_dsc('add DNS and IP_Range for L3_flat_network')
    sce_ops.add_dns_to_l3(zstack_management_ip, l3_uuid, l3_dns, session_uuid = project_login_uuid)
    sce_ops.add_ip_range(zstack_management_ip,'IP_range', l3_uuid, start_ip, end_ip, gateway, netmask, session_uuid = project_login_uuid)
    sce_ops.attach_l2(zstack_management_ip, flat_l2_uuid, cluster_uuid)  

    test_util.test_dsc('query flat provider and attach network service to  L3_flat_network')
    provider_name = 'Flat Network Service Provider'
    conditions = res_ops.gen_query_conditions('name', '=', provider_name)
    net_provider_list = sce_ops.query_resource(zstack_management_ip, res_ops.NETWORK_SERVICE_PROVIDER, conditions, session_uuid = project_login_uuid).inventories[0]
    pro_uuid = net_provider_list.uuid
    sce_ops.attach_flat_network_service_to_l3network(zstack_management_ip, l3_uuid,pro_uuid, session_uuid = project_login_uuid)

    test_stub.share_admin_resource_1([linked_account_uuid])
    print "xcy"
    print "l3_uuid"
    vm = test_stub.create_vm(l3net_uuid=l3_uuid, session_uuid=project_login_uuid)
    test_obj_dict.add_vm(vm)

    #create normal account
    test_util.test_dsc('create normal account')
    account_name = 'test_abc'
    #account_pass = hashlib.sha512(account_name).hexdigest()
    account_pass = 'password'
    test_account = acc_ops.create_normal_account(account_name, account_pass)
    test_account_uuid = test_account.uuid
    test_account_session = acc_ops.login_by_account(account_name, account_pass)

    test_util.test_dsc('share admin resoure to normal account test_abc')
    test_stub.share_admin_resource_1([test_account_uuid])

    l2_inv1 = sce_ops.create_l2_vlan(zstack_management_ip, 'L2_vlan_2215', 'eth0', '2215', zone_uuid)
    l2_uuid1 = l2_inv1.inventory.uuid

    test_util.test_dsc('attach L2 netowrk to cluster')
    sce_ops.attach_l2(zstack_management_ip, l2_uuid1, cluster_uuid)

    #share admin resoure to normal account
    test_util.test_dsc('share L2 L2_vlan_2215 to normal account test_a')
    cond = res_ops.gen_query_conditions('name', '=', 'L2_vlan_2215')
    flat_l2_uuid1 = res_ops.query_resource(res_ops.L2_NETWORK, cond)[0].uuid
    acc_ops.share_resources([test_account_uuid], [flat_l2_uuid1])

    test_account_session = acc_ops.login_by_account(account_name, account_pass)
    l3_inv1 = sce_ops.create_l3(zstack_management_ip, 'l3_flat_network1', 'L3BasicNetwork', flat_l2_uuid1, 'local.com', session_uuid = test_account_session)
    l3_uuid1 = l3_inv1.inventory.uuid

    l3_dns = '223.5.5.5'
    start_ip = '192.168.126.2'
    end_ip = '192.168.126.10'
    gateway = '192.168.126.1'
    netmask = '255.255.255.0'

    test_util.test_dsc('add DNS and IP_Range for L3_flat_network1')
    sce_ops.add_dns_to_l3(zstack_management_ip, l3_uuid1, l3_dns, session_uuid = test_account_session)
    sce_ops.add_ip_range(zstack_management_ip,'IP_range', l3_uuid1, start_ip, end_ip, gateway, netmask, session_uuid = test_account_session)
#    sce_ops.attach_l2(zstack_management_ip, flat_l2_uuid1, cluster_uuid)

    test_util.test_dsc('query flat provider and attach network service to  L3_flat_network')
    provider_name = 'Flat Network Service Provider'
    conditions = res_ops.gen_query_conditions('name', '=', provider_name)
    net_provider_list = sce_ops.query_resource(zstack_management_ip, res_ops.NETWORK_SERVICE_PROVIDER, conditions, session_uuid = test_account_session).inventories[0]
    pro_uuid = net_provider_list.uuid
    sce_ops.attach_flat_network_service_to_l3network(zstack_management_ip, l3_uuid1,pro_uuid, session_uuid = test_account_session)

    vm2 = test_stub.create_vm(l3net_uuid=l3_uuid1, session_uuid = test_account_session)

    test_util.test_dsc('test success normal acount create L3 by admin share L2 ')
    test_obj_dict.add_vm(vm2)

    # 9 delete
    acc_ops.logout(project_login_uuid)
    iam2_ops.delete_iam2_virtual_id(project_operator_uuid)
    iam2_ops.delete_iam2_project(project_uuid)
    iam2_ops.expunge_iam2_project(project_uuid)
    test_lib.lib_error_cleanup(test_obj_dict)

    net_ops.delete_l2(l2_uuid)
    net_ops.delete_l2(l2_uuid1)

    acc_ops.delete_account(test_account_uuid)
        
def error_cleanup():
    global project_uuid,project_operator_uuid, test_account_uuid, l2_uuid, l2_uuid1

    if project_operator_uuid:
        iam2_ops.delete_iam2_virtual_id(project_operator_uuid)
    if project_uuid:
        iam2_ops.delete_iam2_project(project_uuid)
        iam2_ops.expunge_iam2_project(project_uuid)
    test_lib.lib_error_cleanup(test_obj_dict)
    if l2_uuid:
        net_ops.delete_l2(l2_uuid)
    if l2_uuid1:
        net_ops.delete_l2(l2_uuid1)
    if test_account_uuid:
        acc_ops.delete_account(test_account_uuid) 
