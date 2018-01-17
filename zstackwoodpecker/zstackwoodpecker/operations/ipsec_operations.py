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

def create_ipsec_connection(name, l3_uuid, peer_address, auth_key, vip_uuid, peer_cidrs, policy_mode=None, description=None, session_uuid=None, ike_auth_algorithm=None, ike_encryption_algorithm=None, ike_dh_group=None, policy_auth_algorithm=None, policy_encryption_algorithm=None, pfs=None):
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
    action.ikeAuthAlgorithm = ike_auth_algorithm
    action.ikeEncryptionAlgorithm = ike_encryption_algorithm
    action.ikeDhGroup = ike_dh_group
    action.policyAuthAlgorithm = policy_auth_algorithm
    action.policyEncryptionAlgorithm = policy_encryption_algorithm
    action.pfs = pfs
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

def attach_l3network_to_ipsec_connection(l3network_uuids, ipsec_uuid, session_uuid=None):
    action = api_actions.AttachL3NetworkToIPsecConnectionAction()
    action.timeout = 30000
    action.l3NetworkUuids = l3network_uuids
    action.uuid = ipsec_uuid
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.action_logger('Attach L3Networks %s to Ipsec Connection [uuid:] %s' % \
            (l3network_uuids, ipsec_uuid))
    return evt

def detach_l3network_from_ipsec_connection(l3network_uuids, ipsec_uuid, session_uuid=None):
    action = api_actions.DetachL3NetworkFromIPsecConnectionAction()
    action.timeout = 30000
    action.l3NetworkUuids = l3network_uuids
    action.uuid = ipsec_uuid
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.action_logger('Detach L3Networks %s From Ipsec Connection [uuid:] %s' % \
            (l3network_uuids, ipsec_uuid))
    return evt

def attach_remote_cidr_to_ipsec_connection(peer_cidrs, ipsec_uuid, session_uuid=None):
    action = api_actions.AttachRemoteCIDRToIPsecConnectionAction()
    action.timeout = 30000
    action.peerCidrs = peer_cidrs
    action.uuid = ipsec_uuid
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.action_logger('Attach Peer CIDRs %s to Ipsec Connection [uuid:] %s' % \
            (peer_cidrs, ipsec_uuid))
    return evt

def detach_remote_cidr_from_ipsec_connection(peer_cidrs, ipsec_uuid, session_uuid=None):
    action = api_actions.DetachRemoteCIDRFromIPsecConnectionAction()
    action.timeout = 30000
    action.peerCidrs = peer_cidrs
    action.uuid = ipsec_uuid
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.action_logger('Detach Peer CIDRs %s From Ipsec Connection [uuid:] %s' % \
            (peer_cidrs, ipsec_uuid))
    return evt

