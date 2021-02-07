'''

VM CDROM operations.

@author: Legion
'''

from apibinding.api import ApiError
import apibinding.inventory as inventory
import apibinding.api_actions as api_actions
import zstackwoodpecker.test_util as test_util
import account_operations


def create_vm_cdrom(name, vm_uuid, iso_uuid=None, session_uuid=None):
    action = api_actions.CreateVmCdRomAction()
    action.name = name
    action.vmInstanceUuid = vm_uuid
    action.isoUuid = iso_uuid
    test_util.action_logger('Create vm [uuid: %s] CDROM %s' % (vm_uuid, name))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.test_logger('vm [uuid: %s] CDROM %s is created.' % (vm_uuid, name))
    return evt.inventory

def del_vm_cdrom(uuid, session_uuid=None):
    action = api_actions.DeleteVmCdRomAction()
    action.uuid = uuid
    test_util.action_logger('Delete CDROM [uuid: %s]' % uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.test_logger('CDROM [uuid: %s] is deleted.' % uuid)
    return evt.inventory

def query_vm_cdrom(conditions=[], session_uuid=None):
    action = api_actions.QueryVmCdRomAction()
    action.conditions = conditions
    test_util.action_logger('Query CDROM')
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def set_default_cdrom(vm_uuid, cdrom_uuid, session_uuid=None):
    action = api_actions.SetVmInstanceDefaultCdRomAction()
    action.vmInstanceUuid = vm_uuid
    action.uuid = cdrom_uuid
    test_util.action_logger('Set default CDROM [uuid: %s] of vm [uuid: %s]' % (cdrom_uuid, vm_uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.test_logger('vm [uuid: %s] default CDROM is set to %s.' % (vm_uuid, cdrom_uuid))
    return evt.inventory

def update_vm_cdrom(uuid, name, session_uuid=None):
    action = api_actions.UpdateVmCdRomAction()
    action.uuid = uuid
    action.name = name
    test_util.action_logger('Update CDROM')
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory
