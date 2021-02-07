'''

All affinity group operations for test.

@author: Chao
'''

import apibinding.inventory as inventory
import apibinding.api_actions as api_actions
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.account_operations as account_operations
import zstackwoodpecker.operations.resource_operations as res_ops



def create_affinity_group(name, policy, timeout=240000, session_uuid=None):
    action = api_actions.CreateAffinityGroupAction()
    action.name = name
    action.policy = policy
    action.timeout = timeout
    test_util.action_logger('Create Affinity Group')
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def delete_affinity_group(affinity_group_uuid, timeout=240000, session_uuid=None):
    action = api_actions.DeleteAffinityGroupAction()
    action.uuid = affinity_group_uuid
    action.timeout = timeout
    test_util.action_logger('Delete Affinity Group [uuid:] %s' % affinity_group_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def add_vm_to_affinity_group(affinityGroupUuid, vm_uuid, timeout=240000, session_uuid=None):
    action = api_actions.AddVmToAffinityGroupAction()
    action.affinityGroupUuid = affinityGroupUuid
    action.uuid = vm_uuid
    test_util.action_logger('Add VM [uuid:] %s to Affinity Group [uuid:] %s' % (affinityGroupUuid, vm_uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    return evt.inventory

def remove_vm_from_affinity_group(affinityGroupUuid, vm_uuid, timeout=240000, session_uuid=None):
    action = api_actions.RemoveVmFromAffinityGroupAction()
    action.affinityGroupUuid = affinityGroupUuid
    action.uuid = vm_uuid
    test_util.action_logger('Remove VM [uuid:] %s to Affinity Group [uuid:] %s' % (affinityGroupUuid, vm_uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    return evt.inventory

def update_affinity_group(affinityGroupUuid, name, timeout=240000, session_uuid=None):
    action = api_actions.UpdateAffinityGroupAction()
    action.uuid = affinityGroupUuid
    action.name = name
    action.timeout = timeout
    test_util.action_logger('Update Affinity Group [uuid:] %s to name %s' % (affinityGroupUuid, name))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory 
