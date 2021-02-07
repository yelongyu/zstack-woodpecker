'''
Test to add and delete more dns on an l3network

@author: chen.zhou
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.account_operations as acc_ops
import apibinding.api_actions as api_actions
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import time
import os

l2 = None
l2_name = 'mini_l2_network_test'
l3 = None
l3_name = 'mini_l3_network_test'
l3_dns_list = ['4.2.2.2', '1.1.1.1', '4.4.4.4']
l3_dns_list_end = []

def remove_dns_from_l3_network(l3_uuid, dns, system_tags=None, use_tags=None, session_uuid=None):
    action = api_actions.RemoveDnsFromL3NetworkAction()
    action.timeout = 300000
    action.l3NetworkUuid = l3_uuid
    action.dns = dns
    action.systemTags = system_tags
    action.userTags = use_tags
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def test():
    global l3, l2
    # 1. create l2 vlan network
    test_util.test_dsc('create L2_vlan network mini_l2_network_test')
    zone_uuid = res_ops.query_resource(res_ops.ZONE)[0].uuid
    cluster_uuid = res_ops.query_resource(res_ops.CLUSTER)[0].uuid
    l2 = net_ops.create_l2_vlan(l2_name, 'zsn0', zone_uuid, '1999')
    l2_uuid = l2.inventory.uuid
    net_ops.attach_l2(l2_uuid, cluster_uuid)

    # 2. create a l3 flat network
    test_util.test_dsc('1. create l3 network')
    l3 = net_ops.create_l3(l3_name, l2_uuid, Type='L3BasicNetwork', category='Private')
     
    #3. add dns to l3 flat network
    test_util.test_dsc('2. add dns to l3 network')
    for dns in l3_dns_list:
        net_ops.add_dns_to_l3(l3.uuid, dns)
    
    test_util.test_dsc('3. get dns list and check')
    cond = res_ops.gen_query_conditions('uuid', '=', l3.uuid)
    l3_dns_info = res_ops.query_resource(res_ops.L3_NETWORK, cond)[0].dns

    for l3_dns in l3_dns_info:
        l3_dns_list_end.append(l3_dns)

    if l3_dns_list_end != l3_dns_list:
        test_util.test_fail('add dns to network failed')
    else:
        for l3_dns in l3_dns_list:
            remove_dns_from_l3_network(l3.uuid, l3_dns)
        l3_dns_latest = res_ops.query_resource(res_ops.L3_NETWORK, cond)[0].dns

        if l3_dns_latest != []:
            test_util.test_dsc('remove dns from l3network failed')
        else:
            test_util.test_dsc('remove dns from l3network passed')
        test_util.test_dsc('delete l2, l3 network after test')
        net_ops.delete_l3(l3.uuid)
        net_ops.delete_l2(l2_uuid)
        test_util.test_pass('add dns to network passed')

def error_cleanup():
    global l3, l2
    if l2:
        net_ops.delete_l2(l2.inventory.uuid)
    if l3:
        net_ops.delete_l3(l3.uuid)