'''
test iam2 login by platform admin

# 1  create role
# 2  create platform admin and login
# 3  create project and and add/remove role and attributes to/from it
# 4  create project template from project
# 5  create project template and then create project from template
# 6  create Company and Department
# 7  organization change parent
# 8  create virtual id group and add/remove role and attributes to/from it
# 9  create virtual id and add/remove role or attributes to/from it
# 10  add virtual id to group and project
# 11 change state
# 12 update
# 13 delete
@author: rhZhou
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.operations.iam2_operations as iam2_ops
import zstackwoodpecker.operations.resource_operations as res_ops

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
platform_admin_uuid=None

def test():
    global role_uuid, project_uuid, project_02_uuid, project_template_01_uuid, project_template_02_uuid, \
        company_uuid_01, company_uuid_02, department_01_uuid, department_02_uuid, virtual_id_group_uuid, \
        virtual_id_uuid,platform_admin_uuid

    # 1 create platformAdmin
    username = 'username'
    password = 'password'
    platform_admin_uuid = iam2_ops.create_iam2_virtual_id(username, password).uuid
    attributes = [{"name":"__PlatformAdmin__"}]
    iam2_ops.add_attributes_to_iam2_virtual_id(platform_admin_uuid, attributes)
    platform_admin_session_uuid = iam2_ops.login_iam2_virtual_id(username, password)

    # 2 create role
    statements = [{"effect": "Allow", "actions": ["org.zstack.header.vm.**"]}]
    role_uuid = iam2_ops.create_role('test_role', statements,platform_admin_session_uuid).uuid
    action = "org.zstack.header.image.**"
    statements = [{"effect": "Allow", "actions": [action]}]
    iam2_ops.add_policy_statements_to_role(role_uuid, statements,platform_admin_session_uuid)
    statement_uuid = iam2_ops.get_policy_statement_uuid_of_role(role_uuid, action)
    # statement_uuid= res_ops.get_resource(res_ops.ROLE, uuid=role_uuid)[0].statements[0].uuid
    iam2_ops.remove_policy_statements_from_role(role_uuid, [statement_uuid],platform_admin_session_uuid)

    #3 create project and and add/remove role and attributes to/from it
    project_name='test_project'
    project_uuid = iam2_ops.create_iam2_project(project_name, session_uuid=platform_admin_session_uuid).uuid

    # TODO:there is nothing to do with the below api in the first version of iam2
    # iam2_ops.add_attributes_to_iam2_project(project_uuid,attributes='')
    # iam2_ops.remove_attributes_from_iam2_project(project_uuid,attributes='')

    #4 create project template from project
    project_template_01_uuid = iam2_ops.create_iam2_project_template_from_project('project_template', project_uuid,
                                                                                  'this is a template description',
                                                                                  platform_admin_session_uuid).uuid
    project_template_inv = res_ops.get_resource(res_ops.IAM2_PROJECT_TEMPLATE, uuid=project_template_01_uuid,
                                                session_uuid=platform_admin_session_uuid)[0]
    if not project_template_inv:
        test_util.test_fail("create template from project fail")

    #5 create project template and then create project from template
    project_template_02_uuid = iam2_ops.create_iam2_project_template('project_template_02',
                                                                     session_uuid=platform_admin_session_uuid).uuid
    project_02_uuid = iam2_ops.create_iam2_project_from_template('project_02', project_template_02_uuid,
                                                                 session_uuid=platform_admin_session_uuid).uuid
    project_inv = res_ops.get_resource(res_ops.IAM2_PROJECT, uuid=project_02_uuid,
                                       session_uuid=platform_admin_session_uuid)
    if not project_inv:
        test_util.test_fail("create project from template fail")

    #6 create Company and Department
    company_uuid_01 = iam2_ops.create_iam2_organization('test_company_01', 'Company',
                                                        session_uuid=platform_admin_session_uuid).uuid
    company_uuid_02 = iam2_ops.create_iam2_organization('test_company_02', 'Company',
                                                        session_uuid=platform_admin_session_uuid).uuid
    department_01_uuid = iam2_ops.create_iam2_organization('test_department_01', 'Department',
                                                           parent_uuid=company_uuid_01,
                                                           session_uuid=platform_admin_session_uuid).uuid
    department_02_uuid = iam2_ops.create_iam2_organization('test_department_02', 'Department',
                                                           session_uuid=platform_admin_session_uuid).uuid

    #7 organization change parent
    iam2_ops.change_iam2_organization_parent(company_uuid_02, [department_02_uuid],
                                             session_uuid=platform_admin_session_uuid)
    iam2_ops.change_iam2_organization_parent(company_uuid_02, [department_01_uuid],
                                             session_uuid=platform_admin_session_uuid)
    department_inv = res_ops.get_resource(res_ops.IAM2_ORGANIZATION, uuid=department_01_uuid,
                                          session_uuid=platform_admin_session_uuid)[0]
    if department_inv.parentUuid != company_uuid_02:
        test_util.test_fail('change organization parent fail')
    department_inv = res_ops.get_resource(res_ops.IAM2_ORGANIZATION, uuid=department_02_uuid,
                                          session_uuid=platform_admin_session_uuid)[0]
    if department_inv.parentUuid != company_uuid_02:
        test_util.test_fail('change organization parent fail')

    #8 create virtual id group and add/remove role and attributes to/from it
    virtual_id_group_uuid = iam2_ops.create_iam2_virtual_id_group(project_uuid, 'test_virtual_id_group',
                                                                  session_uuid=platform_admin_session_uuid).uuid
    iam2_ops.add_roles_to_iam2_virtual_id_group([role_uuid], virtual_id_group_uuid,
                                                session_uuid=platform_admin_session_uuid)
    iam2_ops.remove_roles_from_iam2_virtual_idgroup([role_uuid], virtual_id_group_uuid,
                                                    session_uuid=platform_admin_session_uuid)
    # TODO:there is nothing to do with the below api in the first version of iam2
    # iam2_ops.add_attributes_to_iam2_virtual_id_group()
    # iam2_ops.remove_attributes_from_iam2_virtual_id_group()

    #9 create virtual id and add/remove role or attributes to/from it
    virtual_id_uuid = iam2_ops.create_iam2_virtual_id('usernametwo', 'password',
                                                      session_uuid=platform_admin_session_uuid).uuid
    iam2_ops.add_roles_to_iam2_virtual_id([role_uuid], virtual_id_uuid, session_uuid=platform_admin_session_uuid)
    iam2_ops.remove_roles_from_iam2_virtual_id([role_uuid], virtual_id_uuid, session_uuid=platform_admin_session_uuid)
    attributes = [{"name": "__ProjectAdmin__", "value": project_uuid}]
    iam2_ops.add_attributes_to_iam2_virtual_id(virtual_id_uuid, attributes, session_uuid=platform_admin_session_uuid)
    cond = res_ops.gen_query_conditions('virtualIDUuid', '=', virtual_id_uuid)
    cond_02 = res_ops.gen_query_conditions('name', '=', "__ProjectAdmin__", cond)
    attribute_uuid = res_ops.query_resource_fields(res_ops.IAM2_VIRTUAL_ID_ATTRIBUTE, cond_02)[0].uuid
    iam2_ops.remove_attributes_from_iam2_virtual_id(virtual_id_uuid, [attribute_uuid],
                                                    session_uuid=platform_admin_session_uuid)
    # attributes = [{"name": "__ProjectOperator__", "value": project_uuid}]
    # iam2_ops.add_attributes_to_iam2_virtual_id(virtual_id_uuid, attributes, session_uuid=platform_admin_session_uuid)
    # iam2_ops.remove_attributes_from_iam2_virtual_id(virtual_id_uuid, attributes,
    #                                                 session_uuid=platform_admin_session_uuid)
    iam2_ops.add_iam2_virtual_ids_to_organization([virtual_id_uuid],department_01_uuid,session_uuid=platform_admin_session_uuid)

    attributes = [{"name": "__OrganizationSupervisor__", "value":virtual_id_uuid }]
    iam2_ops.add_attributes_to_iam2_organization( department_01_uuid, attributes,session_uuid=platform_admin_session_uuid)
    cond_03=res_ops.gen_query_conditions('name','=',"__OrganizationSupervisor__")
    cond_03=res_ops.gen_query_conditions('value','=',virtual_id_uuid,cond_03)
    attribute_uuid=res_ops.query_resource(res_ops.IAM2_ORGANIZATION_ATTRIBUTE,cond_03,session_uuid=platform_admin_session_uuid)[0].uuid
    iam2_ops.remove_attributes_from_iam2_organization(department_01_uuid, [attribute_uuid],session_uuid=platform_admin_session_uuid)

    iam2_ops.remove_iam2_virtual_ids_from_organization([virtual_id_uuid],department_01_uuid,session_uuid=platform_admin_session_uuid)

    #10 add virtual id to group and project
    iam2_ops.add_iam2_virtual_ids_to_project([virtual_id_uuid], project_uuid, session_uuid=platform_admin_session_uuid)
    iam2_ops.add_iam2_virtual_ids_to_group([virtual_id_uuid], virtual_id_group_uuid,
                                           session_uuid=platform_admin_session_uuid)
    iam2_ops.remove_iam2_virtual_ids_from_group([virtual_id_uuid], virtual_id_group_uuid,
                                                session_uuid=platform_admin_session_uuid)
    iam2_ops.remove_iam2_virtual_ids_from_project([virtual_id_uuid], project_uuid,
                                                  session_uuid=platform_admin_session_uuid)

    #11 change state
    disable = 'disable'
    enable = 'enable'
    Disabled= 'Disabled'

    iam2_ops.change_iam2_organization_state(company_uuid_01, disable, session_uuid=platform_admin_session_uuid)
    res_inv = res_ops.get_resource(res_ops.IAM2_ORGANIZATION, uuid=company_uuid_01,
                                   session_uuid=platform_admin_session_uuid)[0]
    if res_inv.state != Disabled:
        test_util.test_fail("test change iam2 organization state fail")
    iam2_ops.change_iam2_organization_state(company_uuid_01, enable, session_uuid=platform_admin_session_uuid)
    iam2_ops.change_iam2_organization_state(department_01_uuid, disable, session_uuid=platform_admin_session_uuid)
    iam2_ops.change_iam2_organization_state(department_01_uuid, enable, session_uuid=platform_admin_session_uuid)

    iam2_ops.change_iam2_project_state(project_uuid, disable, session_uuid=platform_admin_session_uuid)
    res_inv = res_ops.get_resource(res_ops.IAM2_PROJECT, uuid=project_uuid,
                                   session_uuid=platform_admin_session_uuid)[0]
    if res_inv.state != Disabled:
        test_util.test_fail("test change iam2 project state fail")
    iam2_ops.change_iam2_project_state(project_uuid, enable, session_uuid=platform_admin_session_uuid)

    iam2_ops.change_iam2_virtual_id_state(virtual_id_uuid, disable, session_uuid=platform_admin_session_uuid)
    res_inv = res_ops.get_resource(res_ops.IAM2_VIRTUAL_ID, uuid=virtual_id_uuid,
                                   session_uuid=platform_admin_session_uuid)[0]
    if res_inv.state != Disabled:
        test_util.test_fail("test change iam2 virtual id state fail")
    iam2_ops.change_iam2_virtual_id_state(virtual_id_uuid, enable, session_uuid=platform_admin_session_uuid)

    iam2_ops.change_iam2_virtual_id_group_state(virtual_id_group_uuid, disable,
                                                session_uuid=platform_admin_session_uuid)
    res_inv = res_ops.get_resource(res_ops.IAM2_VIRTUAL_ID_GROUP, uuid=virtual_id_group_uuid,
                                   session_uuid=platform_admin_session_uuid)[0]
    if res_inv.state != Disabled:
        test_util.test_fail("test change iam2 virtual id group state fail")
    iam2_ops.change_iam2_virtual_id_group_state(virtual_id_group_uuid, enable,
                                                session_uuid=platform_admin_session_uuid)

    iam2_ops.change_role_state(role_uuid, disable, session_uuid=platform_admin_session_uuid)
    res_inv = res_ops.get_resource(res_ops.ROLE, uuid=role_uuid, session_uuid=platform_admin_session_uuid)[0]
    if res_inv.state != Disabled:
        test_util.test_fail("test change iam2 role state fail")
    iam2_ops.change_role_state(role_uuid, enable, session_uuid=platform_admin_session_uuid)

    # 12 update
    virtual_id_new_name = 'virtual_id_new_name'
    virtual_id_new_des = 'virtual_id_new_des'
    virtual_id_new_password = 'virtual_id_new_password'

    iam2_ops.update_iam2_virtual_id(virtual_id_uuid, virtual_id_new_name, virtual_id_new_des, virtual_id_new_password,
                                    session_uuid=platform_admin_session_uuid)
    virtual_id_inv = res_ops.get_resource(res_ops.IAM2_VIRTUAL_ID, uuid=virtual_id_uuid,
                             session_uuid=platform_admin_session_uuid)[0]
    if virtual_id_inv.name != virtual_id_new_name:
        test_util.test_fail("update iam2 virtual id name fail")
    try:
        virtual_id_session_uuid = iam2_ops.login_iam2_virtual_id(virtual_id_new_name, virtual_id_new_password)
    except:
        test_util.test_fail("update iam2 virtual id name or password fail.")

    virtual_id_group_new_name = 'virtual_id_group_new_name'
    virtual_id_group_new_des = 'virtual_id_group_new_des'
    iam2_ops.update_iam2_virtual_id_group(virtual_id_group_uuid, virtual_id_group_new_name, virtual_id_group_new_des,
                                          session_uuid=platform_admin_session_uuid)
    virtual_id_group_inv = res_ops.get_resource(res_ops.IAM2_VIRTUAL_ID_GROUP, uuid=virtual_id_group_uuid,
                             session_uuid=platform_admin_session_uuid)[0]
    if virtual_id_group_inv.name != virtual_id_group_new_name:
        test_util.test_fail("update iam2 virtual id group name fail")

    project_new_name = 'project_new_name'
    project_new_dsc = 'project_new_dsc'
    iam2_ops.update_iam2_project(project_uuid, project_new_name, project_new_dsc,
                                 session_uuid=platform_admin_session_uuid)
    project_inv = res_ops.get_resource(res_ops.IAM2_PROJECT, uuid=project_uuid, session_uuid=platform_admin_session_uuid)[0]
    if project_inv.name != project_new_name or project_inv.description != project_new_dsc:
        test_util.test_fail("update project information fail")

    company_new_name = 'company_new_name'
    company_new_dsc = 'company_new_dsc'
    iam2_ops.update_iam2_organization(company_uuid_02, company_new_name, company_new_dsc,
                                      session_uuid=platform_admin_session_uuid)
    organization_inv = res_ops.get_resource(res_ops.IAM2_ORGANIZATION, uuid=company_uuid_02,
                                            session_uuid=platform_admin_session_uuid)[0]
    if organization_inv.name != company_new_name or organization_inv.description != company_new_dsc:
        test_util.test_fail("update organization name fail")

    #13 delete
    iam2_ops.delete_iam2_organization(company_uuid_01, session_uuid=platform_admin_session_uuid)
    iam2_ops.delete_iam2_organization(company_uuid_02, session_uuid=platform_admin_session_uuid)
    iam2_ops.delete_iam2_organization(department_01_uuid, session_uuid=platform_admin_session_uuid)
    iam2_ops.delete_iam2_organization(department_02_uuid, session_uuid=platform_admin_session_uuid)
    iam2_ops.delete_iam2_virtual_id_group(virtual_id_group_uuid, session_uuid=platform_admin_session_uuid)
    iam2_ops.delete_iam2_project(project_uuid, session_uuid=platform_admin_session_uuid)
    iam2_ops.delete_iam2_project(project_02_uuid, session_uuid=platform_admin_session_uuid)
    iam2_ops.expunge_iam2_project(project_uuid,session_uuid=platform_admin_session_uuid)
    iam2_ops.expunge_iam2_project(project_02_uuid,session_uuid=platform_admin_session_uuid)
    iam2_ops.delete_iam2_project_template(project_template_01_uuid, session_uuid=platform_admin_session_uuid)
    iam2_ops.delete_iam2_project_template(project_template_02_uuid, session_uuid=platform_admin_session_uuid)
    iam2_ops.delete_iam2_virtual_id(virtual_id_uuid, session_uuid=platform_admin_session_uuid)
    iam2_ops.delete_role(role_uuid, session_uuid=platform_admin_session_uuid)
    iam2_ops.delete_iam2_virtual_id(platform_admin_uuid)

    test_util.test_pass('success test iam2 login in by admin!')

def error_cleanup():
    global role_uuid, project_uuid, project_02_uuid, project_template_01_uuid, project_template_02_uuid, \
        company_uuid_01, company_uuid_02, department_01_uuid, department_02_uuid, virtual_id_group_uuid, \
        virtual_id_uuid,platform_admin_uuid
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
        iam2_ops.expunge_iam2_project(project_uuid)
    if project_02_uuid:
        iam2_ops.delete_iam2_project(project_02_uuid)
        iam2_ops.expunge_iam2_project(project_02_uuid)
    if project_template_01_uuid:
        iam2_ops.delete_iam2_project_template(project_template_01_uuid)
    if project_template_02_uuid:
        iam2_ops.delete_iam2_project_template(project_template_02_uuid)
    if virtual_id_uuid:
        iam2_ops.delete_iam2_virtual_id(virtual_id_uuid)
    if platform_admin_uuid:
        iam2_ops.delete_iam2_virtual_id(platform_admin_uuid)
    if role_uuid:
        iam2_ops.delete_role(role_uuid)
