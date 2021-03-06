'''

New Integration Test for creating KVM VM by normal account

@author: Glody
'''
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.operations.ldap_operations as ldp_ops
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib

import os

ldap_server_uuid = None
new_account_uuid = None
new_account_uuid2 = None

def test():
    global ldap_server_uuid
    global new_account_uuid
    global new_account_uuid2
    system_tags = ["ldapCleanBindingFilter::(uidNumber=1002)"]
    ldap_server = ldp_ops.add_ldap_server('ldap1', 'ldap for test', os.environ.get('ldapServerUrl'), os.environ.get('ldapServerBase'), os.environ.get('ldapServerUsername'), os.environ.get('ldapServerPassword'), 'None', system_tags)
    ldap_server_uuid = ldap_server.inventory.uuid
    conditions = res_ops.gen_query_conditions('type', '=', 'SystemAdmin')
    account = res_ops.query_resource(res_ops.ACCOUNT, conditions)[0]

    get_excepted_exception = False
    try:
        ldap_account = ldp_ops.bind_ldap_account(os.environ.get('ldapUid'), account.uuid)
    except:
	get_excepted_exception = True
    if not get_excepted_exception:
        test_util.test_fail('should not be able to bind ldapuid to admin account')

    new_account = acc_ops.create_account('new_account', 'password', 'Normal')
    new_account_uuid = new_account.uuid
    ldap_account = ldp_ops.bind_ldap_account(os.environ.get('ldapUid'), new_account.uuid)
    ldap_account_uuid = ldap_account.inventory.uuid
    session_uuid = acc_ops.login_by_ldap(os.environ.get('ldapUid'), os.environ.get('ldapPassword'))
    acc_ops.logout(session_uuid)

    ldp_ops.clean_invalid_ldap_binding()
    get_excepted_exception = False
    try:
        session_uuid = acc_ops.login_by_ldap(os.environ.get('ldapUid'), os.environ.get('ldapPassword'))
        acc_ops.logout(session_uuid)
    except:
        get_excepted_exception = True

    if not get_excepted_exception:
        test_util.test_fail('should not be able to login with filter account')

    new_account2 = acc_ops.create_account('new_account2', 'password', 'Normal')
    new_account_uuid2 = new_account2.uuid
    ldap_account2 = ldp_ops.bind_ldap_account('ldapfilter', new_account2.uuid)
    ldap_account_uuid2 = ldap_account2.inventory.uuid
    session_uuid2 = acc_ops.login_by_ldap('ldapfilter', 'password')
    acc_ops.logout(session_uuid)

    #Upcate ldap filter    
    system_tags = ["ldapCleanBindingFilter::(homeDirectory=/home/ldapfilter)"]
    ldap_filter = ldp_ops.update_ldap_server(ldap_server_uuid, system_tags)

    ldp_ops.clean_invalid_ldap_binding()

    get_excepted_exception = False
    try:
        session_uuid = acc_ops.login_by_ldap('ldapfilter','password')
        acc_ops.logout(session_uuid)
    except:
        get_excepted_exception = True

    if not get_excepted_exception:
        test_util.test_fail('should not be able to login with filter account')

    ldp_ops.unbind_ldap_account(ldap_account_uuid)
    ldp_ops.unbind_ldap_account(ldap_account_uuid2)
    acc_ops.delete_account(new_account_uuid)
    acc_ops.delete_account(new_account_uuid2)
    ldp_ops.delete_ldap_server(ldap_server_uuid)
    test_util.test_pass('Create VM by normal user account Success')
    acc_ops.logout(session_uuid)

#Will be called only if exception happens in test().
def error_cleanup():
    global ldap_server_uuid
    global new_account_uuid
    global new_account_uuid2
    if ldap_server_uuid:
        ldp_ops.delete_ldap_server(ldap_server_uuid)
    if new_account_uuid:
        acc_ops.delete_account(new_account_uuid)
    if new_account_uuid2:
        acc_ops.delete_account(new_account_uuid2)
