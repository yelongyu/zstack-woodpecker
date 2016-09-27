'''

New Integration Test for creating KVM VM by normal account

@author: Youyk
'''
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.operations.ldap_operations as ldp_ops
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib

import os

ldap_server_uuid = None
new_account_uuid = None

def test():
    global ldap_server_uuid
    global new_account_uuid

    ldap_server = ldp_ops.add_ldap_server('ldap1', 'ldap for test', os.environ.get('ldapServerUrl2'), os.environ.get('ldapServerBase2'), os.environ.get('ldapServerUsername2'), os.environ.get('ldapServerPassword2'), 'TLS')
    ldap_server_uuid = ldap_server.inventory.uuid
    conditions = res_ops.gen_query_conditions('type', '=', 'SystemAdmin')
    account = res_ops.query_resource(res_ops.ACCOUNT, conditions)[0]

    get_expected_exception = False
    try:
        ldap_account = ldp_ops.bind_ldap_account(os.environ.get('ldapUid'), account.uuid)
    except:
	get_expected_exception = True
    if not get_expected_exception:
        test_util.test_fail('should not be able to bind ldapuid to admin account')

    new_account = acc_ops.create_account('new_account', 'password', 'Normal')
    new_account_uuid = new_account.uuid
    ldap_account = ldp_ops.bind_ldap_account(os.environ.get('ldapUid2'), new_account.uuid)
    ldap_account_uuid = ldap_account.inventory.uuid
    session_uuid = acc_ops.login_by_ldap(os.environ.get('ldapUid2'), os.environ.get('ldapPassword2'))
    acc_ops.logout(session_uuid)
    ldp_ops.unbind_ldap_account(ldap_account_uuid)
    acc_ops.delete_account(new_account.uuid)
    ldp_ops.delete_ldap_server(ldap_server_uuid)
    test_util.test_pass('Create VM by normal user account Success')
    acc_ops.logout(session_uuid)

#Will be called only if exception happens in test().
def error_cleanup():
    global ldap_server_uuid
    global new_account_uuid
    if ldap_server_uuid:
        ldp_ops.delete_ldap_server(ldap_server_uuid)
    if new_account_uuid:
        acc_ops.delete_account(new_account_uuid)
