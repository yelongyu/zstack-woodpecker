'''

All Baremetal operations for test.

@author: czhou25
'''

import apibinding.inventory as inventory
import apibinding.api_actions as api_actions
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
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
                                        (evt.inventory.uuid, action.name))
    return evt.inventory

def create_hostcfg(hostcfg_option, session_uuid=None):
    action = api_actions.CreateBaremetalHostCfgAction()
    action.timeout = 30000
    action.chassisUuid = hostcfg_option.get_chassis_uuid()
    action.password = hostcfg_option.get_password()
    action.unattended = hostcfg_option.get_unattended()
    action.cfgItems = hostcfg_option.get_cfgItems()
    action.systemTags = hostcfg_option.get_system_tags()
    action.userTags = hostcfg_option.get_user_tags()

    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.action_logger('Add Baremetal HostCfg [uuid:] %s for [chassis:] %s' % \
                                        (evt.inventory.uuid, action.chassisUuid))
    
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
    action = api_actions.StartBaremetalPxeServerAction()
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

def create_chassis(chassis_option, session_uuid=None):
    action = api_actions.CreateBaremetalChassisAction()
    action.timeout = 240000
    name = chassis_option.get_name()
    if not name:
        action.name = 'chassis_default_name'
    else:
        action.name = name
    action.ipmiAddress = chassis_option.get_ipmi_address()
    action.ipmiUsername = chassis_option.get_ipmi_username()
    action.ipmiPassword = chassis_option.get_ipmi_password()
    action.ipmiPort = chassis_option.get_ipmi_port()
    action.description = chassis_option.get_description()
    action.systemTags = chassis_option.get_system_tags()
    action.userTags = chassis_option.get_user_tags()

    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.action_logger('Add Chassis [uuid:] %s [name:] %s' % \
                            (evt.inventory.uuid, action.name))
    return evt.inventory

def update_chassis(chassis_uuid, address, username, password, port, \
                   session_uuid=None):
    action = api_actions.UpdateBaremetalChassisAction()
    action.uuid = chassis_uuid
    action.timeout = 30000
    action.ipmiAddress = address
    action.ipmiUsername = username
    action.ipmiPassword = password
    action.ipmiPort = port
    test_util.action_logger('Update Chassis [uuid:] %s' % chassis_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def delete_chassis(chassis_uuid, session_uuid=None):
    action = api_actions.DeleteBaremetalChassisAction()
    action.uuid = chassis_uuid
    action.timeout = 30000
    test_util.action_logger('Delete Chassis [uuid:] %s' % chassis_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def provision_baremetal(chassis_uuid, session_uuid=None):
    action = api_actions.ProvisionBaremetalHostAction()
    action.chassisUuid = chassis_uuid
    action.timeout = 30000
    test_util.action_logger('Provision Chassis [uuid:] %s' % chassis_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def power_on_baremetal(chassis_uuid, session_uuid=None):
    action = api_actions.PowerOnBaremetalHostAction()
    action.chassisUuid = chassis_uuid
    action.timeout = 30000
    test_util.action_logger('PowerOn Chassis [uuid:] %s' % chassis_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def power_off_baremetal(chassis_uuid, session_uuid=None):
    action = api_actions.PowerOffBaremetalHostAction()
    action.chassisUuid = chassis_uuid
    action.timeout = 30000
    test_util.action_logger('PowerOff Chassis [uuid:] %s' % chassis_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def power_reset_baremetal(chassis_uuid, session_uuid=None):
    action = api_actions.PowerResetBaremetalHostAction()
    action.chassisUuid = chassis_uuid
    action.timeout = 30000
    test_util.action_logger('PowerReset Chassis [uuid:] %s' % chassis_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def get_power_status(chassis_uuid, session_uuid=None):
    action = api_actions.PowerStatusBaremetalHostAction()
    action.chassisUuid = chassis_uuid
    action.timeout = 30000
    test_util.action_logger('Get Power Status of Chassis [uuid:] %s' % chassis_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory
