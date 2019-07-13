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

ad_server_uuid = None
new_account_uuid = None

def test():
    global ad_server_uuid
    global new_account_uuid

    system_tag = ["ldapUseAsLoginName::cn"]
    ad_server = ldp_ops.add_ldap_server('ad1', 'ad for test', os.environ.get('adServerUrl'), os.environ.get('adServerBase'), os.environ.get('adServerUsername'), os.environ.get('adServerPassword'), 'account', systemtags=system_tag)
    ad_server_uuid = ad_server.inventory.uuid
    conditions = res_ops.gen_query_conditions('type', '=', 'SystemAdmin')
    account = res_ops.query_resource(res_ops.ACCOUNT, conditions)[0]
    account_uuid = account.uuid
    new_account = acc_ops.create_account('new_account', 'password', 'Normal')
    new_account_uuid = new_account.uuid
    ad_account = ldp_ops.bind_ldap_account(os.environ.get('adUserDn'), account.uuid)
    ad_account_uuid = ad_account.inventory.uuid
    session_uuid = acc_ops.login_by_ldap(os.environ.get('adUserCn'), os.environ.get('adPassword'))
    new_account2 = acc_ops.create_account('new_account2', 'password', 'Normal', session_uuid)
    acc_ops.delete_account(new_account2.uuid)
    acc_ops.logout(session_uuid)
    
    get_expected_exception = False
    try:
        session_uuid = acc_ops.login_by_ldap(os.environ.get('adUserCn'), os.environ.get('adPassword')+'1')
        acc_ops.logout(session_uuid)
    except:
        get_excepted_exception = True
    if not get_excepted_exception:
        test_util.test_fail('should not be able to login with wrong password')

    get_expected_exception = False
    try:
        session_uuid = acc_ops.login_by_ldap(os.environ.get('adUserCn'), '')
        acc_ops.logout(session_uuid)
    except:
        get_excepted_exception = True
    if not get_excepted_exception:
        test_util.test_fail('should not be able to login with blank password')

    get_expected_exception = False
    try:
        session_uuid = acc_ops.login_by_ldap(os.environ.get('adUserCn'), None)
        acc_ops.logout(session_uuid)
    except:
        get_excepted_exception = True
    if not get_excepted_exception:
        test_util.test_fail('should not be able to login without password')

    ldp_ops.unbind_ldap_account(ad_account_uuid)
    acc_ops.delete_account(new_account.uuid)
    ldp_ops.delete_ldap_server(ad_server_uuid)
    test_util.test_pass('Login zstack admin by AD Success')
    acc_ops.logout(session_uuid)

#Will be called only if exception happens in test().
def error_cleanup():
    global ad_server_uuid
    global new_account_uuid
    if ad_server_uuid:
        ldp_ops.delete_ldap_server(ad_server_uuid)
    if new_account_uuid:
        acc_ops.delete_account(new_account_uuid)

def env_recover():
    global ad_server_uuid
    global new_account_uuid
    if ad_server_uuid:
        ldp_ops.delete_ldap_server(ad_server_uuid)
    if new_account_uuid:
        acc_ops.delete_account(new_account_uuid)
