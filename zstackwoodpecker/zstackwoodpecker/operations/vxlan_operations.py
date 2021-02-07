'''
All vxlan operations for test.
@author: SyZhao
'''

import apibinding.api_actions as api_actions
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.test_util as test_util
import account_operations
import apibinding.inventory as inventory

import sys
import traceback


def create_l2_vxlan_network_pool(name, zone_uuid, session_uuid=None):
    action = api_actions.CreateL2VxlanNetworkPoolAction()
    action.timeout = 30000
    action.name = name
    action.zoneUuid = zone_uuid
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.action_logger('Create L2 Vxlan network [name:] %s, [zone_uuid:] %s' \
                             %(name, zone_uuid))
    return evt.inventory


def create_vni_range(name, start_vni, end_vni, l2_network_uuid, session_uuid=None):
    action = api_actions.CreateVniRangeAction()
    action.timeout = 30000
    action.name = name
    action.startVni = start_vni
    action.endVni = end_vni
    action.l2NetworkUuid = l2_network_uuid
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.action_logger('Create vni range [name:] %s, [startVni:] %s, [endVni:] %s, [l2NetworkUuid:] %s' \
                             %(name, start_vni, end_vni, l2_network_uuid))
    return evt.inventory


def create_l2_vxlan_network(name, pool_uuid, zone_uuid, session_uuid=None):
    action = api_actions.CreateL2VxlanNetworkAction()
    action.timeout = 30000
    action.name = name 
    action.poolUuid = pool_uuid
    action.zoneUuid = zone_uuid
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.action_logger('Create L2 Vxlan network [name:] %s, [poolUuid:] %s, [zoneUuid:] %s' \
                             %(name, pool_uuid, zone_uuid))
    return evt.inventory


def delete_vni_range(uuid, session_uuid=None):
    action = api_actions.DeleteVniRangeAction()
    action.timeout = 30000
    action.uuid = uuid
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.action_logger('Delete vni range uuid=%s' %(uuid))
    return evt.inventory


