'''

All Baremetal operations for test.

@author: czhou25
'''

import apibinding.inventory as inventory
import apibinding.api_actions as api_actions
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.account_operations as account_operations
import zstackwoodpecker.operations.config_operations as config_operations

import os
import inspect

def create_pxe(pxe_option, session_uuid=None):
    action = api_actions.CreateBaremetalPxeServerAction()
    action.timeout = 30000
    name = pxe_option.get_name()
    if not name:
        action.name = 'pxe_default_name'
    else:
        action.name = name

    action.dhcpInterface = pxe_option.get_dhcp_interface()
    action.dhcpRangeBegin = pxe_option.get_dhcp_range_begin()
    action.dhcpRangeEnd = pxe_option.get_dhcp_range_end()
    action.dhcpRangeNetmask = pxe_option.get_dhcp_netmask()
    action.description = pxe_option.get_description()
    action.systemTags = pxe_option.get_system_tags()
    action.userTags = pxe_option.get_user_tags()

    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.action_logger('Add PXE Server [uuid:] %s [name:] %s' % \
                                        (evt.uuid, action.name))
    return evt.inventory

def delete_pxe(pxe_uuid, session_uuid=None):
    action = api_actions.DeleteBaremetalPxeServerAction()
    action.uuid = pxe_uuid
    action.timeout = 30000
    test_util.action_logger('Delete PXE [uuid:] %s' % pxe_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def stop_pxe(pxe_uuid, force=None, session_uuid=None):
    action = api_actions.StopBaremetalPxeServerAction()
    action.uuid = pxe_uuid
    action.type = force
    action.timeout = 30000
    test_util.action_logger('Stop PXE [uuid:] %s' % pxe_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def start_pxe(pxe_uuid, session_uuid=None):
    action = api_actions.StartBaremetalPxeServerActio()
    action.uuid = pxe_uuid
    action.timeout = 30000
    test_util.action_logger('Start PXE [uuid:] %s' % pxe_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def update_pxe(pxe_uuid, begin, end, netmask, session_uuid=None):
    action = api_actions.UpdateBaremetalPxeServerAction()
    action.uuid = pxe_uuid
    action.dhcpRangeBegin = begin
    action.dhcpRangeEnd = end
    action.dhcpRangeNetmask = netmask
    action.timeout = 240000
    test_util.action_logger('Update PXE [uuid:] %s' % pxe_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory
