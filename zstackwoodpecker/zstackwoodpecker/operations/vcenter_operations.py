'''

All vcenter operations for test.

@author: SyZhao
'''

import apibinding.inventory as inventory
import apibinding.api_actions as api_actions
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.account_operations as account_operations



def add_vcenter(name, domain_name, username, password, https, zone_uuid, timeout=240000, session_uuid=None):
    action = api_actions.AddVCenterAction()
    action.name = name
    action.domainName = domain_name
    action.username = username
    action.password = password
    action.https = https
    action.zoneUuid = zone_uuid
    action.timeout = timeout
    test_util.action_logger('Add VCenter')
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory


def delete_vcenter(vcenter_uuid, timeout=240000, session_uuid=None):
    action = api_actions.DeleteVCenterAction()
    action.uuid = vcenter_uuid
    action.timeout = timeout
    test_util.action_logger('Delete VCenter [uuid:] %s' % vcenter_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

