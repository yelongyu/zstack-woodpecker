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
    '''The function is dropped'''
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

def delete_pxe(pxe_uuid, delete_mode="Permissive", session_uuid=None):
    action = api_actions.DeleteBaremetalPxeServerAction()
    action.uuid = pxe_uuid
    action.timeout = 30000
    action.deleteMode = delete_mode
    test_util.action_logger('Delete PXE [uuid:] %s' % pxe_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def stop_pxe(pxe_uuid, session_uuid=None):
    action = api_actions.StopBaremetalPxeServerAction()
    action.uuid = pxe_uuid
    action.timeout = 30000
    test_util.action_logger('Stop PXE [uuid:] %s' % pxe_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def start_pxe(pxe_uuid, session_uuid=None):
    action = api_actions.StartBaremetalPxeServerAction()
    action.uuid = pxe_uuid
    action.timeout = 30000
    test_util.action_logger('Start PXE [uuid:] %s' % pxe_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def update_pxe(pxe_uuid, begin=None, end=None, netmask=None, interface=None, \
        name=None, description=None, session_uuid=None):
    action = api_actions.UpdateBaremetalPxeServerAction()
    action.uuid = pxe_uuid
    if begin:
        action.dhcpRangeBegin = begin
    if end:
        action.dhcpRangeEnd = end
    if netmask:
        action.dhcpRangeNetmask = netmask
    if interface:
        action.dhcpInterface = interface
    if name:
        action.name = name
    if description:
        action.description = description
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
    action.clusterUuid = chassis_option.get_cluster_uuid()
    action.ipmiAddress = chassis_option.get_ipmi_address()
    action.ipmiUsername = chassis_option.get_ipmi_username()
    action.ipmiPassword = chassis_option.get_ipmi_password()
    action.ipmiPort = chassis_option.get_ipmi_port()
    if chassis_option.get_description():
        action.description = chassis_option.get_description()
    action.systemTags = chassis_option.get_system_tags()
    action.userTags = chassis_option.get_user_tags()

    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.action_logger('Add Chassis [uuid:] %s [name:] %s' % \
                            (evt.inventory.uuid, action.name))
    return evt.inventory

def update_chassis(chassis_uuid, address=None, username=None, password=None, port=None, name=None, description=None, session_uuid=None):
    action = api_actions.UpdateBaremetalChassisAction()
    action.uuid = chassis_uuid
    action.timeout = 30000
    if address:
        action.ipmiAddress = address
    if username:
        action.ipmiUsername = username
    if password:
        action.ipmiPassword = password
    if port:
        action.ipmiPort = port
    if name:
        action.name = name
    if description:
        action.description = description
    test_util.action_logger('Update Chassis [uuid:] %s' % chassis_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def delete_chassis(chassis_uuid, delete_mode="Permissive", session_uuid=None):
    action = api_actions.DeleteBaremetalChassisAction()
    action.uuid = chassis_uuid
    action.deleteMode = delete_mode
    action.timeout = 30000
    test_util.action_logger('Delete Chassis [uuid:] %s' % chassis_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def inspect_chassis(chassis_uuid, session_uuid=None):
    action = api_actions.InspectBaremetalChassisAction()
    action.uuid = chassis_uuid
    action.timeout = 30000
    test_util.action_logger('Inspect Chassis [uuid:] %s' % chassis_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def power_on_baremetal(chassis_uuid, session_uuid=None):
    '''The function is dropped'''
    action = api_actions.PowerOnBaremetalChassisAction()
    action.chassisUuid = chassis_uuid
    action.timeout = 30000
    test_util.action_logger('PowerOn Chassis [uuid:] %s' % chassis_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def power_off_baremetal(chassis_uuid, session_uuid=None):
    '''The function is dropped'''
    action = api_actions.PowerOffBaremetalChassisAction()
    action.chassisUuid = chassis_uuid
    action.timeout = 30000
    test_util.action_logger('PowerOff Chassis [uuid:] %s' % chassis_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def power_reset_baremetal(chassis_uuid, session_uuid=None):
    '''The function is dropped'''
    action = api_actions.PowerResetBaremetalChassisAction()
    action.chassisUuid = chassis_uuid
    action.timeout = 30000
    test_util.action_logger('PowerReset Chassis [uuid:] %s' % chassis_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def get_power_status(chassis_uuid, session_uuid=None):
    '''The function is dropped'''
    action = api_actions.GetBaremetalChassisPowerStatusAction()
    action.uuid = chassis_uuid
    action.timeout = 30000
    test_util.action_logger('Get Power Status of Chassis [uuid:] %s' % chassis_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def change_baremetal_chassis_state(chassis_uuid, state_event, session_uuid=None):
    action = api_actions.ChangeBaremetalChassisStateAction()
    action.uuid = chassis_uuid
    action.stateEvent = state_event
    test_util.action_logger('Change State of Chassis [uuid:] %s' % chassis_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def create_baremetal_instance(baremetal_ins_option, session_uuid=None):
    action = api_actions.CreateBaremetalInstanceAction()
    if baremetal_ins_option.get_name():
        action.name = baremetal_ins_option.get_name()
    else:
        action.name = 'baremetal_instance'
    action.chassisUuid = baremetal_ins_option.get_chassis_uuid()
    action.imageUuid = baremetal_ins_option.get_image_uuid()
    action.password = baremetal_ins_option.get_password()
    action.timeout = 30000
    if baremetal_ins_option.get_nic_cfgs():
        action.nicCfgs = baremetal_ins_option.get_nic_cfgs()
    if baremetal_ins_option.get_nic_cfgs():
        action.strategy = baremetal_ins_option.get_strategy()
    action.description = baremetal_ins_option.get_description()
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.action_logger('Create Baremetal Instance [uuid:] %s [name:] %s' % (evt.inventory.uuid, evt.inventory.name)) 
    return evt.inventory 

def destory_baremetal_instance(uuid, delete_mode="Permissive", session_uuid=None):
    action = api_actions.DestroyBaremetalInstanceAction()
    action.uuid = uuid
    action.deleteMode = delete_mode
    action.timeout = 30000
    test_util.action_logger('Destory Baremetal Instance [uuid:] %s' % uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    return evt

def expunge_baremetal_instance(uuid, session_uuid=None):
    action = api_actions.ExpungeBaremetalInstanceAction()
    action.uuid = uuid
    action.timeout = 30000
    test_util.action_logger('Expunge Baremetal Instance [uuid:] %s' % uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def start_baremetal_instance(uuid, pxe_boot=None, session_uuid=None):
    action = api_actions.StartBaremetalInstanceAction()
    action.uuid = uuid
    action.timeout = 30000
    if pxe_boot:
        action.pxeBoot = pxe_boot
    test_util.action_logger('Start Baremetal Instance [uuid:] %s' % uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def stop_baremetal_instance(uuid, stop_type=None, session_uuid=None):
    action = api_actions.StopBaremetalInstanceAction()
    action.uuid = uuid
    action.timeout = 30000
    if stop_type:
        action.type = stop_type
    test_util.action_logger('Stop Baremetal Instance [uuid:] %s' % uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def reboot_baremetal_instance(uuid, session_uuid=None):
    action = api_actions.RebootBaremetalInstanceAction()
    action.uuid = uuid
    action.timeout = 30000
    test_util.action_logger('Reboot Baremetal Instance [uuid:] %s' % uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def recover_baremetal_instance(uuid, session_uuid=None):
    action = api_actions.RecoverBaremetalInstanceAction()
    action.uuid = uuid
    action.timeout = 30000
    test_util.action_logger('Recover Baremetal Instance [uuid:] %s' % uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def request_baremetal_console_access(baremetal_instance_uuid, session_uuid=None):
    action = api_actions.RequestBaremetalConsoleAccessAction()
    action.baremetalInstanceUuid = baremetal_instance_uuid
    action.timeout = 30000
    test_util.action_logger('Request Baremetal Instance Console Access [uuid:] %s' % uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def update_baremetal_instance(uuid, name=None, description=None, password=None, platform=None, session_uuid=None):
    action = api_actions.UpdateBaremetalInstanceAction()
    action.uuid = uuid
    if name:
        action.name = name
    if description:
        action.description = description
    if password:
        action.password = password
    if platform:
        action.platform = platform
    test_util.action_logger('Update Baremetal Instance [uuid:] %s' % uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

