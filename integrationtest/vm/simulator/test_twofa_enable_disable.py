'''
New Test For Two Factor Enable Disable 

@author: Glody
'''
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.operations.config_operations as conf_ops
import apibinding.api_actions as api_actions
import apibinding.inventory as inventory
import threading
import time
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    #Enable twofa and check login
    password = 'b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86'
    session_uuid = acc_ops.login_as_admin()
    twofa_enabled = conf_ops.get_global_config_value('twofa', 'twofa.enable')
    if twofa_enabled == 'false':
        conf_ops.change_global_config('twofa', 'twofa.enable', 'true') 
    twofa = acc_ops.get_twofa_auth_secret('admin', password, session_uuid = session_uuid)
    secret = twofa.secret
    twofa_status = twofa.status
    if twofa_status != 'NewCreated':
        test_util.test_fail("The twofa auth secret statue should be 'NewCreated' but it's %s" %twofa_status) 
    security_code = test_stub.get_security_code(secret)
    session1_uuid = acc_ops.login_by_account('admin', password, system_tags=['twofatoken::%s' %security_code]) 
    if session1_uuid != None:
        test_util.test_logger("Enable twofa and login with security code passed")

    twofa_status = acc_ops.get_twofa_auth_secret('admin', password, session_uuid = session_uuid).status
    if twofa_status != 'Logined':
        test_util.test_fail("The twofa auth secret statue should be 'Logined' but it's %s" %twofa_status)

    #Disable twofa and check login again
    conf_ops.change_global_config('twofa', 'twofa.enable', 'false', session_uuid = session_uuid)
    session2_uuid = acc_ops.login_as_admin()
    if session2_uuid != None:
        test_util.test_pass("Disable twofa and login without security code passed")

    test_util.test_fail("Fail to login without security code after twofa disabled")

def error_cleanup():
    pass

