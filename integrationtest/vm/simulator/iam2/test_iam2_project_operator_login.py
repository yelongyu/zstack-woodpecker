'''
test iam2 login by __ProjectOperator__

# 1 create project
# 2 create project operator and virtual id
# 3 login in project by project operator
# 4 create virtual id group
# 5 add virtual id into project and group
# 6 remove virtual id from project and group
# 7 create role
# 8 add/remove roles to/from virtual id(group)
# 9 delete

@auther: fangxiao
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.operations.iam2_operations as iam2_ops
import zstackwoodpecker.operations.resource_operations as res_ops

def test():

    iam2_ops.clean_iam2_enviroment()

    # 1 create project
    project_name = 'test_project'
    project_uuid = iam2_ops.create_iam2_project(project_name).uuid

    # 2 create project operator and virtual id
    project_operator_name = 'username'
    project_operator_password = 'b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86'
    password='b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86'
    attributes = [{"name": "__ProjectOperator__", "value": project_uuid}]
    project_operator_uuid = iam2_ops.create_iam2_virtual_id(project_operator_name,project_operator_password,attributes=attributes).uuid
    virtual_id_uuid = iam2_ops.create_iam2_virtual_id('usernametwo',password).uuid

    # 3 login in project by project operator
    iam2_ops.add_iam2_virtual_ids_to_project([project_operator_uuid],project_uuid)
    project_operator_session_uuid = iam2_ops.login_iam2_virtual_id(project_operator_name,project_operator_password)
    project_login_uuid = iam2_ops.login_iam2_project(project_name,session_uuid=project_operator_session_uuid).uuid

    # 4 create virtual id group
    virtual_id_group_uuid = iam2_ops.create_iam2_virtual_id_group(project_uuid,'test_virtual_id_group',session_uuid=project_login_uuid).uuid

    # 5 add virtual id into project and group
    iam2_ops.add_iam2_virtual_ids_to_project([virtual_id_uuid], project_uuid, session_uuid=project_login_uuid)
    iam2_ops.add_iam2_virtual_ids_to_group([virtual_id_uuid],virtual_id_group_uuid,session_uuid=project_login_uuid)

    # 6 remove virtual id from project and group
    iam2_ops.remove_iam2_virtual_ids_from_group([virtual_id_uuid],virtual_id_group_uuid,session_uuid=project_login_uuid)
    iam2_ops.remove_iam2_virtual_ids_from_project([virtual_id_uuid], project_uuid, session_uuid=project_login_uuid)

    # 7 create role
    statements = [{"effect": "Allow", "actions": ["org.zstack.header.vm.**"]}]
    role_uuid = iam2_ops.create_role('role1', statements,session_uuid=project_login_uuid).uuid

    # 8 add/remove roles to/from virtual id(group)
    iam2_ops.add_roles_to_iam2_virtual_id_group([role_uuid],virtual_id_group_uuid,session_uuid=project_login_uuid)
    iam2_ops.remove_roles_from_iam2_virtual_idgroup([role_uuid],virtual_id_group_uuid,session_uuid=project_login_uuid)
    iam2_ops.add_roles_to_iam2_virtual_id([role_uuid],virtual_id_uuid,session_uuid=project_login_uuid)
    iam2_ops.remove_roles_from_iam2_virtual_id([role_uuid],virtual_id_uuid,session_uuid=project_login_uuid)

    # 9 delete
    iam2_ops.delete_role(role_uuid,session_uuid=project_login_uuid)
    iam2_ops.delete_iam2_virtual_id_group(virtual_id_group_uuid,session_uuid=project_login_uuid)
    acc_ops.logout(project_login_uuid)

    iam2_ops.clean_iam2_enviroment()

    test_util.test_pass('success test iam2 login by project operator')

def error_cleanup():
    iam2_ops.clean_iam2_enviroment()

