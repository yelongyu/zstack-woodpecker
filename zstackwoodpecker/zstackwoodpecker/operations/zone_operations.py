'''

All zone operations for test.

@author: Youyk
'''

import apibinding.api_actions as api_actions
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.operations.deploy_operations as dep_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_util as test_util
import account_operations
import apibinding.inventory as inventory

import sys
import traceback

def create_zone(zone_option, session_uuid=None):
    action = api_actions.CreateZoneAction()
    action.timeout = 30000
    action.name = zone_option.get_name()
    action.description = zone_option.get_description()
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.action_logger('Add Zone [uuid:] %s [name:] %s' % \
            (evt.uuid, action.name))
    return evt.inventory

def delete_zone(zone_uuid, session_uuid=None):
    action = api_actions.DeleteZoneAction()
    action.uuid = zone_uuid
    action.timeout = 600000
    test_util.action_logger('Delete Zone [uuid:] %s' % zone_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def change_zone_state(zone_uuid, state, session_uuid=None):
    action = api_actions.ChangeZoneStateAction()
    action.uuid = zone_uuid
    action.stateEvent = state
    action.timeout = 300000
    test_util.action_logger('Change Zone [uuid:] %s to [state:] %s' % (zone_uuid, state))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def add_zone_resource(deploy_config, zone_name):
    session_uuid = acc_ops.login_as_admin()
    try:
        test_util.test_dsc('-------add zone operation-------')
        dep_ops.add_zone(None, deploy_config, session_uuid, zone_name = zone_name)
        test_util.test_dsc('-------add l2 operation-------')
        dep_ops.add_l2_network(None, deploy_config, session_uuid, \
                zone_name = zone_name)
        test_util.test_dsc('-------add primary storage operation-------')
        dep_ops.add_primary_storage(None, deploy_config, session_uuid, \
                zone_name = zone_name)
        test_util.test_dsc('-------add cluster operation-------')
        dep_ops.add_cluster(None, deploy_config, session_uuid, \
                zone_name = zone_name)
        test_util.test_dsc('-------add host operation-------')
        dep_ops.add_host(None, deploy_config, session_uuid, \
                zone_name = zone_name)
        test_util.test_dsc('-------add l3 operation-------')
        dep_ops.add_l3_network(None, deploy_config, session_uuid, \
                zone_name = zone_name)
        test_util.test_dsc('-------add virtual router offering operation-------')
        dep_ops.add_virtual_router(None, deploy_config, session_uuid, \
                zone_name = zone_name)
        zone = res_ops.get_resource(res_ops.ZONE, session_uuid, \
                name = zone_name)[0]
    except Exception as e:
        test_util.test_logger('[Error] zstack deployment meets exception when adding zone resource .')
        traceback.print_exc(file=sys.stdout)
        raise e
    finally:
        acc_ops.logout(session_uuid)

    test_util.action_logger('Complete add zone resources for [uuid:] %s' \
            % zone.uuid)



