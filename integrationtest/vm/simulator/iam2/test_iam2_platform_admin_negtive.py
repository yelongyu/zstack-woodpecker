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



def test():
    iam2_ops.clean_iam2_enviroment()
    # 1 create platformAdmin
    username = 'username'
    password = 'b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86'
    platform_admin_uuid = iam2_ops.create_iam2_virtual_id(username, password).uuid
    attributes = [{"name": "__PlatformAdmin__"}]
    iam2_ops.add_attributes_to_iam2_virtual_id(platform_admin_uuid, attributes)
    platform_admin_session_uuid = iam2_ops.login_iam2_virtual_id(username, password)

    # 2 create platformAdmin by platformAdmin
    username_02 = 'username_02'
    password_02 = 'b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86'
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
    acc_ops.logout(platform_admin_session_uuid)
    iam2_ops.delete_iam2_virtual_id(platform_admin_uuid)

    try:
        iam2_ops.login_iam2_virtual_id(username,password)
        test_util.test_fail("the platform admin is Deleted,can't login,but now login success,test fail")
    except:
        pass

    iam2_ops.clean_iam2_enviroment()
    test_util.test_pass("success test platform admin negtive operations")

def error_cleanup():
    iam2_ops.clean_iam2_enviroment()
