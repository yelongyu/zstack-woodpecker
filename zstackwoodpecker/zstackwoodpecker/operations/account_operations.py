'''
Account operations for wrapping up actions.

@author: Youyk
'''

import apibinding.api_actions as api_actions
import apibinding.inventory as inventory
import traceback
import sys
import zstackwoodpecker.test_util as test_util


def login_as_admin():
    accountName = inventory.INITIAL_SYSTEM_ADMIN_NAME
    password = inventory.INITIAL_SYSTEM_ADMIN_PASSWORD
    return login_by_account(accountName, password)

def login_by_account(name, password, timeout = 160000):
    login = api_actions.LogInByAccountAction()
    login.accountName = name
    login.password = password
    #login.timeout = 15000
    #since system might be hang for a while, when archive system log in 00:00:00
    #, it is better to increase timeout time to 60000 to avoid of no response
    login.timeout = timeout
    session_uuid = login.run().inventory.uuid
    return session_uuid

def login_by_ldap(uid, password, timeout = 60000):
    login = api_actions.LogInByLdapAction()
    login.uid = uid
    login.password = password
    #login.timeout = 15000
    #since system might be hang for a while, when archive system log in 00:00:00
    #, it is better to increase timeout time to 60000 to avoid of no response
    login.timeout = timeout
    session_uuid = login.run().inventory.uuid
    return session_uuid

def logout(session_uuid):
    logout = api_actions.LogOutAction()
    logout.timeout = 160000
    logout.sessionUuid = session_uuid
    logout.run()

def execute_action_with_session(action, session_uuid):
    if session_uuid:
        action.sessionUuid = session_uuid
        evt = action.run()
    else:
        session_uuid = login_as_admin()
        try:
            action.sessionUuid = session_uuid
            evt = action.run()
        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            raise e
        finally:
            logout(session_uuid)

    return evt

#To be added, depended on APIListSessionMsg
def get_account_by_session(session_uuid):
    pass

def create_account(name, password, account_type, session_uuid = None):
    action = api_actions.CreateAccountAction()
    action.name = name
    action.password = password
    action.type = account_type
    test_util.action_logger('Create %s [Account:] %s with [password:] %s' % \
            (account_type, name, password))
    evt = execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[Account:] %s is created.' % evt.inventory.uuid)
    return evt.inventory

def create_admin_account(name, password, session_uuid = None):
    return create_account(name, password, 'SystemAdmin', session_uuid)

def create_normal_account(name, password, session_uuid = None):
    return create_account(name, password, 'Normal', session_uuid)

def delete_account(uuid, session_uuid = None):
    action = api_actions.DeleteAccountAction()
    action.uuid = uuid
    test_util.action_logger('Delete [Account:] %s' % uuid)
    evt = execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[Account:] %s is deleted.' % uuid)
    return evt

def delete_user(uuid, session_uuid = None):
    action = api_actions.DeleteUserAction()
    action.uuid = uuid
    test_util.action_logger('Delete [User:] %s' % uuid)
    evt = execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[User:] %s is deleted.' % uuid)
    return evt

def create_user(name, password, session_uuid = None):
    action = api_actions.CreateUserAction()
    action.name = name
    action.password = password
    test_util.action_logger('Create [User:] %s with [password:] %s' % \
            (name, password))
    evt = execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[User:] %s is created.' % evt.inventory.uuid)
    return evt.inventory

def create_user_group(name, session_uuid = None):
    action = api_actions.CreateUserGroupAction()
    action.name = name
    test_util.action_logger('Create [User Group:] %s ' % name)
    evt = execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[User Group:] %s is created for name: %s .' % \
            (evt.inventory.uuid, name))
    return evt.inventory

def add_user_to_group(user_uuid, group_uuid, session_uuid = None):
    action = api_actions.AddUserToGroupAction()
    action.userUuid = user_uuid
    action.groupUuid = group_uuid
    test_util.action_logger('Add [User:] %s to [User Group:] %s ' % \
            (user_uuid, group_uuid))
    evt = execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[User:] %s has been added to [User Group:] %s.' % \
            (user_uuid, group_uuid))
    return evt.inventory

def reset_account_password(uuid, password, session_uuid = None):
    action = api_actions.ResetAccountPasswordAction()
    action.uuid = uuid
    action.password = password
    test_util.action_logger('Reset [Account:] %s [password:] %s' % \
            (uuid, password))
    evt = execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[Account:] %s password is reset.' % evt.inventory.uuid)
    return evt.inventory

def reset_user_password(uuid, password, session_uuid = None):
    action = api_actions.ResetUserPasswordAction()
    action.uuid = uuid
    action.password = password
    test_util.action_logger('Reset [User:] %s [password:] %s' % \
            (uuid, password))
    evt = execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[User:] %s password is reset.' % evt.inventory.uuid)
    return evt.inventory

def share_resources(account_uuid_list, resource_uuid_list, to_public = None, \
        session_uuid = None):
    action = api_actions.ShareResourceAction()
    action.accountUuids = account_uuid_list
    action.resourceUuids = resource_uuid_list
    action.toPublic = to_public
    evt = execute_action_with_session(action, session_uuid) 
    test_util.action_logger('Share [Resources]: %s to [Accounts]: %s' % \
            (resource_uuid_list, account_uuid_list))
    return evt

def revoke_resources(account_uuid_list,resource_uuid_list,session_uuid = None):
		action = api_actions.RevokeResourceSharingAction()
		action.accountUuids = account_uuid_list
		action.resourceUuids = resource_uuid_list

		evt = execute_action_with_session(action, session_uuid)
		test_util.action_logger('Revoke [Resources]: %s from [Accounts]: %s' % \
			   (resource_uuid_list, account_uuid_list))
		return evt




	
def update_quota(identity_uuid,name,value,session_uuid=None):
   action = api_actions.UpdateQuotaAction()
   action.identityUuid = identity_uuid
   action.name = name
   action.value = value
   action.timeout = 240000
   evt = execute_action_with_session(action,session_uuid)
   test_util.action_logger('Update resource [name:] %s value to %s of account [identityUuid] %s ' % (name,value,identity_uuid))
   return evt.inventory	

#result=create_account('c','password','Normal')
