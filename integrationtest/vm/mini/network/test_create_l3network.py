'''

Test to create a new l3network with dns, ip range and network services

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
l3 = None

def attach_network_service_to_l3network(l3_uuid, providers, session_uuid=None):
    #providers = {provider_uuid:['network_service']}
    action = api_actions.AttachNetworkServiceToL3NetworkAction()
    action.networkServices = providers
    action.l3NetworkUuid = l3_uuid
    action.timeout = 12000
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    test_util.action_logger('add network services to l3 network: %s' % l3_uuid)
    return evt

def test():

    # create l3 network
    global l3, l2

    name = 'mini_network_test'
    test_util.test_dsc('create L2_vlan network mini_l2_network_test')
    zone_uuid = res_ops.query_resource(res_ops.ZONE)[0].uuid
    cluster_uuid = res_ops.query_resource(res_ops.CLUSTER)[0].uuid
    l2 = net_ops.create_l2_vlan('l2_vlan', 'zsn0', zone_uuid, '1998')
    l2_uuid = l2.inventory.uuid
    net_ops.attach_l2(l2_uuid, cluster_uuid)

    type='L3BasicNetwork'
    categry='Private'
    l3=net_ops.create_l3(name, l2_uuid, category=categry, Type=type)

    # add dns to l3 network
    l3_dns = '223.5.5.5'
    net_ops.add_dns_to_l3(l3.uuid, l3_dns)
    test_util.test_dsc('add DNS and IP_Range for L3_flat_network')

    # add ip range to l3 network
    ip_range_option = test_util.IpRangeOption()
    ip_range_option.set_l3_uuid(l3.uuid)
    ip_range_option.set_startIp('192.168.40.2')
    ip_range_option.set_endIp('192.168.40.20')
    ip_range_option.set_gateway('192.168.40.1')
    ip_range_option.set_netmask('255.255.255.0')
    ip_range_option.set_name('ip_range_test')

    net_ops.add_ip_range(ip_range_option)

    #attach network service to l3 network
    cond = res_ops.gen_query_conditions('type', '=', 'flat')
    provider1_uuid = res_ops.query_resource(res_ops.NETWORK_SERVICE_PROVIDER, cond)[0].uuid
    cond = res_ops.gen_query_conditions('type', '=', 'SecurityGroup')
    provider2_uuid = res_ops.query_resource(res_ops.NETWORK_SERVICE_PROVIDER, cond)[0].uuid
    providers = {provider1_uuid:['DHCP','Eip'], provider2_uuid:['SecurityGroup']}
    attach_network_service_to_l3network(l3.uuid, providers)
    test_util.test_dsc('a network with dns, ip range and network services has been created successfully')
    net_ops.delete_l3(l3.uuid)
    net_ops.delete_l2(l2_uuid)
    test_util.test_dsc('delete l3 network after test')

def error_cleanup():
    global l3, l2
    if l2:
        net_ops.delete_l2(l2_uuid)
    if l3:
        net_ops.delete_l3(l3.uuid)
                                              


