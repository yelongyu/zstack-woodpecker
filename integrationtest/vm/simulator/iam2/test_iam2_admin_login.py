'''
test iam2 login by admin

# 1  create role and add/remove policy
# 2  create project and  add/remove attributes to/from it
# 3  create project template from project
# 4  create project template and then create project from template
# 5  create Company and Department (organization)
# 6  organization change parent
# 7  create virtual id group and add/remove role and attributes to/from it
# 8  create virtual id and add/remove role or attributes to/from it
# 9  add virtual id to organization and set it as OrganizationSupervisor
# 10 add virtual id to group and project
# 11 change state
# 12 update
# 13 delete

@author: rhZhou
'''
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.operations.iam2_operations as iam2_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_util as test_util

role_uuid = None
project_uuid = None
project_02_uuid = None
project_template_01_uuid = None
project_template_02_uuid = None
company_uuid_01 = None
company_uuid_02 = None
department_01_uuid = None
department_02_uuid = None
virtual_id_group_uuid = None
virtual_id_uuid = None


def test():
    global role_uuid, project_uuid, project_02_uuid, project_template_01_uuid, project_template_02_uuid, \
        company_uuid_01, company_uuid_02, department_01_uuid, department_02_uuid, virtual_id_group_uuid, \
        virtual_id_uuid

    # 1 create role and add/remove policy
    statements = [{"effect": "Allow", "actions": ["org.zstack.header.vm.**"]}]
    role_uuid = iam2_ops.create_role('test_role', statements).uuid
    action = "org.zstack.header.image.**"
    statements = [{"effect": "Allow", "actions": [action]}]
    iam2_ops.add_policy_statements_to_role(role_uuid, statements)
    statement_uuid = iam2_ops.get_policy_statement_uuid_of_role(role_uuid, action)
    # statement_uuid= res_ops.get_resource(res_ops.ROLE, uuid=role_uuid)[0].statements[0].uuid
    iam2_ops.remove_policy_statements_from_role(role_uuid, [statement_uuid])

    # 2 create project and  add/remove attributes to/from it
    project_name = 'test_project'
    project_uuid = iam2_ops.create_iam2_project(project_name).uuid

    # TODO:there is nothing to do with the below api in the first version of iam2
    # iam2_ops.add_attributes_to_iam2_project(project_uuid,attributes='')
    # iam2_ops.remove_attributes_from_iam2_project(project_uuid,attributes='')

    # 3 create project template from project
    project_template_01_uuid = iam2_ops.create_iam2_project_template_from_project('project_template', project_uuid,
                                                                                  'this is a template '
                                                                                  'description').uuid
    project_template_inv = res_ops.get_resource(res_ops.IAM2_PROJECT_TEMPLATE, uuid=project_template_01_uuid)
    if not project_template_inv:
        test_util.test_fail("create template from project fail")

    # 4 create project template and then create project from template
    project_template_02_uuid = iam2_ops.create_iam2_project_template('project_template_02').uuid
    project_02_uuid = iam2_ops.create_iam2_project_from_template('project_02', project_template_02_uuid).uuid
    project_inv = res_ops.get_resource(res_ops.IAM2_PROJECT, uuid=project_02_uuid)
    if not project_inv:
        test_util.test_fail("create project from template fail")

    # 5 create Company and Department (organization)
    company_uuid_01 = iam2_ops.create_iam2_organization('test_company_01', 'Company').uuid
    company_uuid_02 = iam2_ops.create_iam2_organization('test_company_02', 'Company').uuid
    department_01_uuid = iam2_ops.create_iam2_organization('test_department_01', 'Department',
                                                           parent_uuid=company_uuid_01).uuid
    department_02_uuid = iam2_ops.create_iam2_organization('test_department_02', 'Department').uuid

    # 6 organization change parent
    iam2_ops.change_iam2_organization_parent(company_uuid_02, [department_02_uuid])
    iam2_ops.change_iam2_organization_parent(company_uuid_02, [department_01_uuid])
    department_inv = res_ops.get_resource(res_ops.IAM2_ORGANIZATION, uuid=department_01_uuid)[0]
    if department_inv.parentUuid != company_uuid_02:
        test_util.test_fail('change organization parent fail')
    department_inv = res_ops.get_resource(res_ops.IAM2_ORGANIZATION, uuid=department_02_uuid)[0]
    if department_inv.parentUuid != company_uuid_02:
        test_util.test_fail('change organization parent fail')

    # 7 create virtual id group and add/remove role and attributes to/from it
    virtual_id_group_uuid = iam2_ops.create_iam2_virtual_id_group(project_uuid, 'test_virtual_id_group').uuid
    iam2_ops.add_roles_to_iam2_virtual_id_group([role_uuid], virtual_id_group_uuid)
    iam2_ops.remove_roles_from_iam2_virtual_idgroup([role_uuid], virtual_id_group_uuid)
    # TODO:there is nothing to do with the below api in the first version of iam2
    # iam2_ops.add_attributes_to_iam2_virtual_id_group()
    # iam2_ops.remove_attributes_from_iam2_virtual_id_group()

    # 8 create virtual id and add/remove role or attributes to/from it
    virtual_id_uuid = iam2_ops.create_iam2_virtual_id('username', 'password').uuid
    iam2_ops.add_roles_to_iam2_virtual_id([role_uuid], virtual_id_uuid)
    iam2_ops.remove_roles_from_iam2_virtual_id([role_uuid], virtual_id_uuid)

    cond = res_ops.gen_query_conditions('virtualIDUuid', '=', virtual_id_uuid)
    attributes = [{"name": "__PlatformAdmin__"}]
    iam2_ops.add_attributes_to_iam2_virtual_id(virtual_id_uuid, attributes)
    cond_01 = res_ops.gen_query_conditions('name', '=', "__PlatformAdmin__", cond)
    attribute_uuid = res_ops.query_resource_fields(res_ops.IAM2_VIRTUAL_ID_ATTRIBUTE, cond_01)[0].uuid
    iam2_ops.remove_attributes_from_iam2_virtual_id(virtual_id_uuid, [attribute_uuid])
    attributes = [{"name": "__ProjectAdmin__", "value": project_uuid}]
    iam2_ops.add_attributes_to_iam2_virtual_id(virtual_id_uuid, attributes)
    cond_02 = res_ops.gen_query_conditions('name', '=', "__ProjectAdmin__", cond)
    attribute_uuid = res_ops.query_resource_fields(res_ops.IAM2_VIRTUAL_ID_ATTRIBUTE, cond_02)[0].uuid
    iam2_ops.remove_attributes_from_iam2_virtual_id(virtual_id_uuid, [attribute_uuid])

    # admin can't create Project operator
    # attributes = [{"name": "__ProjectOperator__", "value": project_uuid}]
    # iam2_ops.add_attributes_to_iam2_virtual_id(virtual_id_uuid, attributes)
    # iam2_ops.remove_attributes_from_iam2_virtual_id(virtual_id_uuid, attributes)

    # 9 add virtual id to organization and set it as OrganizationSupervisor
    iam2_ops.add_iam2_virtual_ids_to_organization([virtual_id_uuid], department_01_uuid)

    attributes = [{"name": "__OrganizationSupervisor__", "value": virtual_id_uuid}]
    iam2_ops.add_attributes_to_iam2_organization(department_01_uuid, attributes)
    cond_03 = res_ops.gen_query_conditions('name', '=', "__OrganizationSupervisor__")
    cond_03 = res_ops.gen_query_conditions('value', '=', virtual_id_uuid, cond_03)
    attribute_uuid = res_ops.query_resource(res_ops.IAM2_ORGANIZATION_ATTRIBUTE, cond_03)[0].uuid
    iam2_ops.remove_attributes_from_iam2_organization(department_01_uuid, [attribute_uuid])

    iam2_ops.remove_iam2_virtual_ids_from_organization([virtual_id_uuid], department_01_uuid)

    # 10 add virtual id to group and project
    iam2_ops.add_iam2_virtual_ids_to_project([virtual_id_uuid], project_uuid)
    iam2_ops.add_iam2_virtual_ids_to_group([virtual_id_uuid], virtual_id_group_uuid)
    iam2_ops.remove_iam2_virtual_ids_from_group([virtual_id_uuid], virtual_id_group_uuid)
    iam2_ops.remove_iam2_virtual_ids_from_project([virtual_id_uuid], project_uuid)

    # 11 change state
    disable = 'disable'
    enable = 'enable'
    Disabled = 'Disabled'
    iam2_ops.change_iam2_organization_state(company_uuid_01, disable)
    res_inv = res_ops.get_resource(res_ops.IAM2_ORGANIZATION, uuid=company_uuid_01)[0]
    if res_inv.state != Disabled:
        test_util.test_fail("test change iam2 organization state fail")
    iam2_ops.change_iam2_organization_state(company_uuid_01, enable)
    iam2_ops.change_iam2_organization_state(department_01_uuid, disable)
    iam2_ops.change_iam2_organization_state(department_01_uuid, enable)

    iam2_ops.change_iam2_project_state(project_uuid, disable)
    res_inv = res_ops.get_resource(res_ops.IAM2_PROJECT, uuid=project_uuid)[0]
    if res_inv.state != Disabled:
        test_util.test_fail("test change iam2 project state fail")
    iam2_ops.change_iam2_project_state(project_uuid, enable)

    iam2_ops.change_iam2_virtual_id_state(virtual_id_uuid, disable)
    res_inv = res_ops.get_resource(res_ops.IAM2_VIRTUAL_ID, uuid=virtual_id_uuid)[0]
    if res_inv.state != Disabled:
        test_util.test_fail("test change iam2 virtual id state fail")
    iam2_ops.change_iam2_virtual_id_state(virtual_id_uuid, enable)

    iam2_ops.change_iam2_virtual_id_group_state(virtual_id_group_uuid, disable)
    res_inv = res_ops.get_resource(res_ops.IAM2_VIRTUAL_ID_GROUP, uuid=virtual_id_group_uuid)[0]
    if res_inv.state != Disabled:
        test_util.test_fail("test change iam2 virtual id group state fail")
    iam2_ops.change_iam2_virtual_id_group_state(virtual_id_group_uuid, enable)

    iam2_ops.change_role_state(role_uuid, disable)
    res_inv = res_ops.get_resource(res_ops.ROLE, uuid=role_uuid)[0]
    if res_inv.state != Disabled:
        test_util.test_fail("test change iam2 role state fail")
    iam2_ops.change_role_state(role_uuid, enable)

    # 12 update
    virtual_id_new_name = 'virtual_id_new_name'
    virtual_id_new_des = 'virtual_id_new_des'
    virtual_id_new_password = 'virtual_id_new_password'

    iam2_ops.update_iam2_virtual_id(virtual_id_uuid, virtual_id_new_name, virtual_id_new_des, virtual_id_new_password)
    virtual_id_inv = res_ops.get_resource(res_ops.IAM2_VIRTUAL_ID, uuid=virtual_id_uuid)[0]
    if virtual_id_inv.name != virtual_id_new_name:
        test_util.test_fail("update iam2 virtual id name fail")
    try:
        iam2_ops.login_iam2_virtual_id('username', 'password')
    except:
        test_util.test_logger("the old username and password can't login")
    try:
        virtual_id_session_uuid = iam2_ops.login_iam2_virtual_id(virtual_id_new_name, virtual_id_new_password)
        acc_ops.logout(virtual_id_session_uuid)
    except:
        test_util.test_fail("update iam2 virtual id name or password fail.")

    virtual_id_group_new_name = 'virtual_id_group_new_name'
    virtual_id_group_new_des = 'virtual_id_group_new_des'
    iam2_ops.update_iam2_virtual_id_group(virtual_id_group_uuid, virtual_id_group_new_name, virtual_id_group_new_des)
    virtual_id_group_inv = res_ops.get_resource(res_ops.IAM2_VIRTUAL_ID_GROUP, uuid=virtual_id_group_uuid)[0]
    if virtual_id_group_inv.name != virtual_id_group_new_name:
        test_util.test_fail("update iam2 virtual id group name fail")

    project_new_name = 'project_new_name'
    project_new_dsc = 'project_new_dsc'
    iam2_ops.update_iam2_project(project_uuid, project_new_name, project_new_dsc)
    project_inv = res_ops.get_resource(res_ops.IAM2_PROJECT, uuid=project_uuid)[0]
    if project_inv.name != project_new_name or project_inv.description != project_new_dsc:
        test_util.test_fail("update project information fail")

    company_new_name = 'company_new_name'
    company_new_dsc = 'company_new_dsc'
    iam2_ops.update_iam2_organization(company_uuid_02, company_new_name, company_new_dsc)
    organization_inv = res_ops.get_resource(res_ops.IAM2_ORGANIZATION, uuid=company_uuid_02)[0]
    if organization_inv.name != company_new_name or organization_inv.description != company_new_dsc:
        test_util.test_fail("update organization name fail")

    # 13 delete
    iam2_ops.delete_iam2_organization(company_uuid_01)
    iam2_ops.delete_iam2_organization(company_uuid_02)
    iam2_ops.delete_iam2_organization(department_01_uuid)
    iam2_ops.delete_iam2_organization(department_02_uuid)
    iam2_ops.delete_iam2_virtual_id_group(virtual_id_group_uuid)
    iam2_ops.delete_iam2_project(project_uuid)
    iam2_ops.delete_iam2_project(project_02_uuid)
    iam2_ops.delete_iam2_project_template(project_template_01_uuid)
    iam2_ops.delete_iam2_project_template(project_template_02_uuid)
    iam2_ops.delete_iam2_virtual_id(virtual_id_uuid)
    iam2_ops.delete_role(role_uuid)

    test_util.test_pass('success test iam2 login in by admin!')


# Will be called only if exception happens in test().
def error_cleanup():
    global role_uuid, project_uuid, project_02_uuid, project_template_01_uuid, project_template_02_uuid, \
        company_uuid_01, company_uuid_02, department_01_uuid, department_02_uuid, virtual_id_group_uuid, \
        virtual_id_uuid
    if company_uuid_01:
        iam2_ops.delete_iam2_organization(company_uuid_01)
    if company_uuid_02:
        iam2_ops.delete_iam2_organization(company_uuid_02)
    if department_01_uuid:
        iam2_ops.delete_iam2_organization(department_01_uuid)
    if department_02_uuid:
        iam2_ops.delete_iam2_organization(department_02_uuid)
    if virtual_id_group_uuid:
        iam2_ops.delete_iam2_virtual_id_group(virtual_id_group_uuid)
    if project_uuid:
        iam2_ops.delete_iam2_project(project_uuid)
    if project_02_uuid:
        iam2_ops.delete_iam2_project(project_02_uuid)
    if project_template_01_uuid:
        iam2_ops.delete_iam2_project_template(project_template_01_uuid)
    if project_template_02_uuid:
        iam2_ops.delete_iam2_project_template(project_template_02_uuid)
    if virtual_id_uuid:
        iam2_ops.delete_iam2_virtual_id(virtual_id_uuid)
    if role_uuid:
        iam2_ops.delete_role(role_uuid)
