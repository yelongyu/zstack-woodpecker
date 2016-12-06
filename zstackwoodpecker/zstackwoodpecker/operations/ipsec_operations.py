'''

All ipsec operations for test.

@author: Quarkonics
'''

import apibinding.api_actions as api_actions
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.test_util as test_util
import account_operations
import apibinding.inventory as inventory

import sys
import traceback

def create_ipsec_connection(name, l3_uuid, peer_address, auth_key, vip_uuid, peer_cidrs, policy_mode=None, description=None, session_uuid=None):
    action = api_actions.CreateIPsecConnectionAction()
    action.timeout = 30000
    action.name = name
    action.l3NetworkUuid = l3_uuid
    action.peerAddress = peer_address
    action.authKey = auth_key
    action.vipUuid = vip_uuid
    action.peerCidrs = peer_cidrs
    action.policyMode = policy_mode
    action.description = description
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.action_logger('Create Ipsec Connection [name:] %s [l3NetworkUuid:] %s [peerAddress:] %s' % \
            (name, l3_uuid, peer_address))
    return evt.inventory

def delete_ipsec_connection(uuid, session_uuid=None):
    action = api_actions.DeleteIPsecConnectionAction()
    action.timeout = 30000
    action.uuid = uuid
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.action_logger('delete Ipsec Connection [uuid:] %s' % \
            (uuid))
    return evt
