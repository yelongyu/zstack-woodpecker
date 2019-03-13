'''
test iam2 system admin by admin

# 1 create system admin with name/username/password/description/phone/email/number/authorities.
# 2 verify authorities to system admin.
# 3 change system admin authorities and verify.
# 4 change the password of the system admin and verify.
# 5 delete system admin.

@author: SyZhao
'''
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.operations.iam2_operations as iam2_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_util as test_util

role_uuid = None
virtual_id_uuid = None


def test():
    global role_uuid, virtual_id_uuid

    iam2_ops.clean_iam2_enviroment()

    statements = [{"effect": "Allow", "actions": ["org.zstack.header.vm.**"]}]
    role_uuid = iam2_ops.create_role('test_role', statements).uuid
    action = "org.zstack.header.image.**"
    statements = [{"effect": "Allow", "actions": [action]}]
    iam2_ops.add_policy_statements_to_role(role_uuid, statements)
    statement_uuid = iam2_ops.get_policy_statement_uuid_of_role(role_uuid, action)
    # statement_uuid= res_ops.get_resource(res_ops.ROLE, uuid=role_uuid)[0].statements[0].uuid
    iam2_ops.remove_policy_statements_from_role(role_uuid, [statement_uuid])


    # 13 delete
    iam2_ops.delete_iam2_virtual_id(virtual_id_uuid)
    iam2_ops.delete_role(role_uuid)

    iam2_ops.clean_iam2_enviroment()
    test_util.test_pass('success test iam2 login in by admin!')


def error_cleanup():
    pass
