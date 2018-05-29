'''

VPC DNS operations for test.

@author: Hengguo Ge
'''

import apibinding.inventory as inventory
import apibinding.api_actions as api_actions
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.account_operations as account_operations
import zstackwoodpecker.operations.config_operations as config_operations

def add_dns_to_vpc_router(vpc_router_uuid, dns, session_uuid=None):
    action = api_actions.AddDnsToVpcRouterAction()
    action.timeout = 300000
    action.uuid = vpc_router_uuid
    action.dns = dns
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def remove_dns_from_vpc_router(vpc_router_uuid, dns, session_uuid=None):
    action = api_actions.RemoveDnsFromVpcRouterAction()
    action.timeout = 300000
    action.uuid = vpc_router_uuid
    action.dns = dns
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def query_vpc_router(vpc_router_uuid, session_uuid=None):
    action = api_actions.QueryVpcRouterAction()
    action.timeout = 300000
    action.uuid = vpc_router_uuid
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def add_dns_to_l3_network(vpc_network_uuid, dns, system_tags=None, use_tags=None, session_uuid=None):
    action = api_actions.AddDnsToL3NetworkAction()
    action.timeout = 300000
    action.l3NetworkUuid = vpc_network_uuid
    action.dns = dns
    action.systemTags = system_tags
    action.userTags = use_tags
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def remove_dns_from_l3_network(vpc_network_uuid, dns, system_tags=None, use_tags=None, session_uuid=None):
    action = api_actions.RemoveDnsFromL3NetworkAction()
    action.timeout = 300000
    action.l3NetworkUuid = vpc_network_uuid
    action.dns = dns
    action.systemTags = system_tags
    action.userTags = use_tags
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory