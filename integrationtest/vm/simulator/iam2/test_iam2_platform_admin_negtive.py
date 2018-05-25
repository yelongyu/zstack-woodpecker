'''
test iam2 platform admin do negtive operations

# 1 create platformAdmin
# 2 create platformAdmin by platformAdmin
# 3 delete platformAdmin by platformAdmin

@author: rhZhou
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.operations.iam2_operations as iam2_ops
import zstackwoodpecker.operations.resource_operations as res_ops

platform_admin_uuid = None
virtual_id_uuid = None


def test():
    global platform_admin_uuid, virtual_id_uuid

    # 1 create platformAdmin
    username = 'username'
    password = 'password'
    platform_admin_uuid = iam2_ops.create_iam2_virtual_id(username, password).uuid
    attributes = [{"name": "__PlatformAdmin__"}]
    iam2_ops.add_attributes_to_iam2_virtual_id(platform_admin_uuid, attributes)
    platform_admin_session_uuid = iam2_ops.login_iam2_virtual_id(username, password)

    # 2 create platformAdmin by platformAdmin
    username_02 = 'username_02'
    password_02 = 'password'
    virtual_id_uuid = iam2_ops.create_iam2_virtual_id(username_02, password_02,
                                                      session_uuid=platform_admin_session_uuid).uuid
    try:
        iam2_ops.add_attributes_to_iam2_virtual_id(virtual_id_uuid, attributes,
                                                   session_uuid=platform_admin_session_uuid)
        test_util.test_fail("platformAdmin can't create platformAdmin")
    except:
        pass

    # 3 delete platformAdmin by platformAdmin
    iam2_ops.add_attributes_to_iam2_virtual_id(virtual_id_uuid, attributes)
    try:
        iam2_ops.remove_attributes_from_iam2_virtual_id(virtual_id_uuid, attributes,
                                                        session_uuid=platform_admin_session_uuid)
        test_util.test_fail("platformAdmin can't cancel platformAdmin")
    except:
        pass

    iam2_ops.delete_iam2_virtual_id(platform_admin_uuid)
    iam2_ops.delete_iam2_virtual_id(virtual_id_uuid)
    test_util.test_pass("success test platform admin negtive operations")


def error_cleanup():
    global platform_admin_uuid, virtual_id_uuid
    if platform_admin_uuid:
        iam2_ops.delete_iam2_virtual_id(platform_admin_uuid)
    if virtual_id_uuid:
        iam2_ops.delete_iam2_virtual_id(virtual_id_uuid)
