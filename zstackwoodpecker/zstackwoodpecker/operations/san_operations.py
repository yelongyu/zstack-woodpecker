'''

SAN storage operations for test.

@author: czhou25
'''

import apibinding.api_actions as api_actions
import zstackwoodpecker.test_util as test_util
import apibinding.inventory as inventory
import account_operations

def add_iscsi_server(iscsi_option):
    action = api_actions.AddIscsiServerAction()
    action.ip = iscsi_option.get_ip()
    action.port = iscsi_option.get_port()
    action.chapUserName = iscsi_option.get_chapUserName()
    action.chapUserPassword = iscsi_option.get_chapUserPassword()
    timeout = iscsi_option.get_timeout()
    if not timeout:
        action.timeout = 240000
    else:
        action.timeout = timeout

    name = iscsi_option.get_name()
    if not name:
        action.name = 'iscsi_test'
    else:
        action.name = name

    evt = account_operations.execute_action_with_session(action, iscsi_option.get_session_uuid())

    test_util.test_logger('[iscsi server:] %s is created.' % evt.inventory.uuid)
    return evt.inventory

def attach_iscsi_to_cluster(iscsi_uuid, cluster_uuid, session_uuid=None):
    action = api_actions.AttachIscsiServerToClusterAction()
    action.uuid = iscsi_uuid
    action.clusterUuid = cluster_uuid
    action.timeout = 240000
    test_util.action_logger('Attach ISCSI [uuid:] %s to [Cluster:] %s' % (iscsi_uuid, cluster_uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory
