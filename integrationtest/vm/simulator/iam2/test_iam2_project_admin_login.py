'''
test iam2 login by platform admin

# 1 create project
# 2 create virtual id
# 3 create project admin
# 4 login in project by project admin
# 5 create virtual id group
# 6 create role
# 7 add virtual id into project and group
# 8 add/remove roles to/from virtual id (group)
# 9 create/delete project operator
# 10 remove virtual ids from group and project
# 11 delete

@author: rhZhou
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.operations.iam2_operations as iam2_ops
import zstackwoodpecker.operations.resource_operations as res_ops

role_uuid = None
project_uuid = None
virtual_id_group_uuid = None
virtual_id_uuid = None
project_admin_uuid = None


def test():
    global role_uuid, project_uuid, project_admin_uuid, virtual_id_uuid, virtual_id_group_uuid

    # 1 create project
    project_name = 'test_project'
    project_uuid = iam2_ops.create_iam2_project(project_name).uuid

    # 2 create virtual id
    project_admin_name = 'username'
    project_admin_password = 'password'
    project_admin_uuid = iam2_ops.create_iam2_virtual_id(project_admin_name, project_admin_password).uuid
    virtual_id_uuid = iam2_ops.create_iam2_virtual_id('usernametwo', 'password').uuid

    # 3 create project admin
    iam2_ops.add_iam2_virtual_ids_to_project([project_admin_uuid],project_uuid)
    attributes = [{"name": "__ProjectAdmin__", "value": project_uuid}]
    iam2_ops.add_attributes_to_iam2_virtual_id(project_admin_uuid, attributes)

    # 4 login in project by project admin
    project_admin_session_uuid = iam2_ops.login_iam2_virtual_id(project_admin_name, project_admin_password)
    project_login_uuid = iam2_ops.login_iam2_project(project_name, session_uuid=project_admin_session_uuid).uuid
    # iam2_ops.remove_attributes_from_iam2_virtual_id(virtual_id_uuid, attributes)

    # 5 create virtual id group
    virtual_id_group_uuid = iam2_ops.create_iam2_virtual_id_group(project_uuid, 'test_virtual_id_group',session_uuid=project_login_uuid).uuid

    # 6 add virtual id into project and group
    # TODO:add query
    iam2_ops.add_iam2_virtual_ids_to_project([virtual_id_uuid], project_uuid, session_uuid=project_login_uuid)
    iam2_ops.add_iam2_virtual_ids_to_group([virtual_id_uuid], virtual_id_group_uuid,
                                           session_uuid=project_login_uuid)

    # 7 create role
    statements = [{"effect": "Allow", "actions": ["org.zstack.header.vm.**"]}]
    role_uuid = iam2_ops.create_role('test_role', statements,session_uuid=project_login_uuid).uuid

    # 8 add/remove roles to/from virtual id (group)
    iam2_ops.add_roles_to_iam2_virtual_id_group([role_uuid], virtual_id_group_uuid,
                                                session_uuid=project_login_uuid)
    iam2_ops.remove_roles_from_iam2_virtual_idgroup([role_uuid], virtual_id_group_uuid,
                                                    session_uuid=project_login_uuid)
    iam2_ops.add_roles_to_iam2_virtual_id([role_uuid], virtual_id_uuid, session_uuid=project_login_uuid)
    iam2_ops.remove_roles_from_iam2_virtual_id([role_uuid], virtual_id_uuid, session_uuid=project_login_uuid)

    # 9 create/delete project operator
    attributes = [{"name": "__ProjectOperator__", "value": project_uuid}]
    iam2_ops.add_attributes_to_iam2_virtual_id(virtual_id_uuid,attributes,session_uuid=project_login_uuid)
    cond = res_ops.gen_query_conditions('virtualIDUuid', '=', virtual_id_uuid)
    cond_02 = res_ops.gen_query_conditions('name', '=', "__ProjectOperator__", cond)
    attribute_uuid = res_ops.query_resource_fields(res_ops.IAM2_VIRTUAL_ID_ATTRIBUTE, cond_02)[0].uuid
    iam2_ops.remove_attributes_from_iam2_virtual_id(virtual_id_uuid,[attribute_uuid],session_uuid=project_login_uuid)

    # 10 remove virtual ids from group and project
    iam2_ops.remove_iam2_virtual_ids_from_group([virtual_id_uuid], virtual_id_group_uuid,
                                                session_uuid=project_login_uuid)
    iam2_ops.remove_iam2_virtual_ids_from_project([virtual_id_uuid], project_uuid,
                                                  session_uuid=project_login_uuid)

    # 11 delete
    acc_ops.logout(project_login_uuid)
    iam2_ops.delete_role(role_uuid)
    iam2_ops.delete_iam2_virtual_id_group(virtual_id_group_uuid)
    iam2_ops.delete_iam2_virtual_id(virtual_id_uuid)
    iam2_ops.delete_iam2_virtual_id(project_admin_uuid)
    iam2_ops.delete_iam2_project(project_uuid)

    test_util.test_pass('success test iam2 login in by project admin!')


def error_cleanup():
    global role_uuid, project_uuid, project_admin_uuid, virtual_id_uuid, virtual_id_group_uuid
    if role_uuid:
        iam2_ops.delete_role(role_uuid)
    if virtual_id_group_uuid:
        iam2_ops.delete_iam2_virtual_id_group(virtual_id_group_uuid)
    if virtual_id_uuid:
        iam2_ops.delete_iam2_virtual_id(virtual_id_uuid)
    if project_admin_uuid:
        iam2_ops.delete_iam2_virtual_id(project_admin_uuid)
    if project_uuid:
        iam2_ops.delete_iam2_project(project_uuid)
