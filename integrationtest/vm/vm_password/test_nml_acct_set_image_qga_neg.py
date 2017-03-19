'''
negative test for changing password by normal account after executing enable image
@author: SyZhao
'''

import apibinding.inventory as inventory
import hashlib
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstacklib.utils.ssh as ssh
import test_stub



lib_test_stub = test_lib.lib_get_test_stub()

vm = None
test_account_uuid = None
test_account_session = None
image_uuid = None

users   = [ "root"     ]
passwds = [ "abc_123"  ]

exist_users = ["root"]

def test():
    global vm, test_account_uuid, test_account_session, image_uuid
    import uuid
    account_name = uuid.uuid1().get_hex()
    account_pass = uuid.uuid1().get_hex()
    account_pass = hashlib.sha512(account_name).hexdigest()
    test_account = acc_ops.create_normal_account(account_name, account_pass)
    test_account_uuid = test_account.uuid
    test_account_session = acc_ops.login_by_account(account_name, account_pass)
    test_stub.share_admin_resource([test_account_uuid])

    img_cond = res_ops.gen_query_conditions("name", '=', "centos7-installation-no-system-tag")
    img_inv = res_ops.query_resource_fields(res_ops.IMAGE, img_cond, None)
    image_uuid = img_inv[0].uuid
    try:
        img_ops.set_image_qga_enable(image_uuid, session_uuid = test_account_session)
    except:
        test_util.test_pass('Enable and change vm password by normal user account Success')
    
    test_util.test_fail('It should be raise exception when setImageQga after image is shared to this normal account, however, got no exception.')


#Will be called only if exception happens in test().
def error_cleanup():
    global vm, test_account_uuid, test_account_session, image_uuid
    if image_uuid:
        img_ops.set_image_qga_disable(image_uuid, session_uuid = test_account_session)
    if vm:
        vm.destroy(test_account_session)
    if test_account_uuid:
        acc_ops.delete_account(test_account_uuid)
