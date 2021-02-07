'''

All ldap operations for test.

@author: quarkonics
'''

import apibinding.inventory as inventory
import apibinding.api_actions as api_actions
import zstackwoodpecker.test_util as test_util
import account_operations
import config_operations

import os
import inspect

def add_ldap_server(name, description, url, base, username, password, scope, encryption='None', systemtags=None, session_uuid=None):
    action = api_actions.AddLdapServerAction()
    action.name = name
    action.description = description
    action.url = url
    action.base = base
    action.username = username
    action.password = password
    action.scope = scope
    action.encryption = encryption
    if systemtags != None:
        action.systemTags = systemtags
    test_util.action_logger('Add [ldap Server:] %s' % url)
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[ldap Server:] %s is added.' % url)
    return evt

def delete_ldap_server(uuid, session_uuid=None):
    action = api_actions.DeleteLdapServerAction()
    action.uuid = uuid
    test_util.action_logger('Delete [ldap Server:] %s' % uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[ldap Server:] %s is deleted.' % uuid)
    return evt

def bind_ldap_account(ldap_uid, account_uuid, session_uuid=None):
    action = api_actions.CreateLdapBindingAction()
    action.ldapUid = ldap_uid
    action.accountUuid = account_uuid
    test_util.action_logger('bind [ldapUid:] %s to [accountUuid:] %s' % (ldap_uid, account_uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    return evt

def unbind_ldap_account(uuid, session_uuid=None):
    action = api_actions.DeleteLdapBindingAction()
    action.uuid = uuid
    test_util.action_logger('unbind [ldap account:] %s' % (uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def update_ldap_server(uuid, systemtags, session_uuid=None):
    action = api_actions.UpdateLdapServerAction()
    action.ldapServerUuid = uuid
    action.systemTags = systemtags
    test_util.action_logger('update [ldap clean binding filter:] %s' % (uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def clean_invalid_ldap_binding(session_uuid=None):
    action = api_actions.CleanInvalidLdapBindingAction()
    test_util.action_logger('clean [invalid ldap binding]')
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

