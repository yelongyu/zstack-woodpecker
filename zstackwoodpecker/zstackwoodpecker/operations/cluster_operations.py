'''

All cluster operations for test.

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

def create_cluster(cluster_option, session_uuid=None):
    action = api_actions.CreateClusterAction()
    action.timeout = 30000
    action.name = cluster_option.get_name()
    action.description = cluster_option.get_description()
    action.hypervisorType = cluster_option.get_hypervisor_type()
    action.type = cluster_option.get_type()
    action.zoneUuid = cluster_option.get_zone_uuid()
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.action_logger('Create Cluster [uuid:] %s [name:] %s' % \
            (evt.uuid, action.name))
    return evt.inventory

def create_mini_cluster(mini_cluster_option, session_uuid=None):
    action = api_actions.CreateMiniClusterAction()
    action.timeout = 900000
    action.zoneUuid = mini_cluster_option.get_zone_uuid()
    action.name = mini_cluster_option.get_name()
    action.username = mini_cluster_option.get_username()
    action.password = mini_cluster_option.get_password()
    action.hostManagementIps = mini_cluster_option.get_host_management_ips()
    action.sshPort = mini_cluster_option.get_sshPort()
    action.hypervisorType = mini_cluster_option.get_hypervisor_type()
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.action_logger('Create Mini cluster [uuid:] %s with [ips:] %s' % \
                (evt.uuid, " ".join(action.hostManagementIps)))
    return evt.inventory

def delete_cluster(cluster_uuid, session_uuid=None):
    action = api_actions.DeleteClusterAction()
    action.uuid = cluster_uuid
    action.timeout = 600000
    test_util.action_logger('Delete Cluster [uuid:] %s' % cluster_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def change_cluster_state(cluster_uuid, state, session_uuid=None):
    action = api_actions.ChangeClusterStateAction()
    action.uuid = cluster_uuid
    action.stateEvent = state
    action.timeout = 300000
    test_util.action_logger('Change Cluster [uuid:] %s to [state:] %s' % (cluster_uuid, state))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def add_cluster_resource(deploy_config, cluster_name, zone_name = None):
    session_uuid = acc_ops.login_as_admin()
    try:
        dep_ops.add_cluster(deploy_config, session_uuid, \
                zone_name = zone_name, cluster_name = cluster_name)
        dep_ops.add_host(deploy_config, session_uuid, \
                zone_name = zone_name, cluster_name = cluster_name)
        cluster = res_ops.get_resource(res_ops.CLUSTER, session_uuid, \
                name = cluster_name)[0]
    except Exception as e:
        test_util.test_logger('[Error] zstack deployment meets exception when adding cluster resource .')
        traceback.print_exc(file=sys.stdout)
        raise e
    finally:
        acc_ops.logout(session_uuid)

    test_util.action_logger('Complete add cluster resources for [uuid:] %s' \
            % cluster.uuid)



