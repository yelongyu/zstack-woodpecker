'''

All console operations for test.

@author: Quarkonics
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

def request_console_access(uuid, session_uuid=None):
    action = api_actions.RequestConsoleAccessAction()
    action.timeout = 30000
    action.vmInstanceUuid = uuid
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.action_logger('Request Console Access [hostname:] %s [port:] %s [token:] %s' % \
            (evt.inventory.hostname, evt.inventory.port, evt.inventory.token))
    return evt.inventory

def get_vm_console_address(uuid, session_uuid=None):
    action = api_actions.GetVmConsoleAddressAction()
    action.timeout = 30000
    action.uuid = uuid
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.action_logger('Get VM Console Address [hostname:] %s [port:] %s' % \
            (evt.hostIp, evt.port))
    return evt

def set_vm_console_password(uuid, console_password, session_uuid=None):
    action = api_actions.SetVmConsolePasswordAction()
    action.timeout = 30000
    action.uuid = uuid
    action.consolePassword = console_password
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.action_logger('Set VM [uuid:] %s Console Password [%s]' % \
            (uuid, console_password))
    return evt

def delete_vm_console_password(uuid, session_uuid=None):
    action = api_actions.DeleteVmConsolePasswordAction()
    action.timeout = 30000
    action.uuid = uuid
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.action_logger('Delete VM [uuid:%s] Console Password' % \
            (uuid))
    return evt

def get_vm_console_password(uuid, session_uuid=None):
    action = api_actions.GetVmConsolePasswordAction()
    action.timeout = 30000
    action.uuid = uuid
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.action_logger('Get VM [uuid:] Console Password [%s]' % \
            (uuid, evt.consolePassword))
    return evt.consolePassword

def get_console_proxy_agent(session_uuid=None):
    action = api_actions.QueryConsoleProxyAgentAction()
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.action_logger('Query Console Prosy')
    return evt
