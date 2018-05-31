# -*- coding: utf-8 -*-
'''
test iam2 login by admin

每个zone一个或多个cluster，对应1个bs，包含1个ps（local即可）
每个cluster中要有至少2个host。
每个bs中要有2个image。
Vyos模式
创建5个项目，项目和区域的关系如上图。
共创建50个用户，先指定user1为项目1负责人，user11为项目2负责人

@author: Glody
'''
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.operations.iam2_operations as iam2_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_util as test_util
import user_info_generator 

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

    cond = res_ops.gen_query_conditions('name', '=', 'zone1') 
    zone1_uuid = res_ops.query_resource_fields(res_ops.ZONE, cond)[0].uuid
    cond = res_ops.gen_query_conditions('name', '=', 'zone2')
    zone2_uuid = res_ops.query_resource_fields(res_ops.ZONE, cond)[0].uuid
    cond = res_ops.gen_query_conditions('name', '=', 'zone3')
    zone3_uuid = res_ops.query_resource_fields(res_ops.ZONE, cond)[0].uuid

    for char in ['A','B','C','D','E']:
        project_name = 'Project-' + char
        project_uuid = iam2_ops.create_iam2_project(project_name).uuid
 
        if project_name == 'Project-A' or project_name == 'Project-C':
            attributes = [{"name": "__ProjectRelatedZone__", "value": zone1_uuid},{"name": "__ProjectRelatedZone__", "value": zone2_uuid}]
            iam2_ops.add_attributes_to_iam2_project(project_uuid, attributes)

        if project_name == 'Project-B':
            attributes = [{"name": "__ProjectRelatedZone__", "value": zone1_uuid}]
            iam2_ops.add_attributes_to_iam2_project(project_uuid, attributes)

        if project_name == 'Project-D':
            attributes = [{"name": "__ProjectRelatedZone__", "value": zone2_uuid},{"name": "__ProjectRelatedZone__", "value": zone3_uuid}]
            iam2_ops.add_attributes_to_iam2_project(project_uuid, attributes)

        if project_name == 'Project-E':
            attributes = [{"name": "__ProjectRelatedZone__", "value": zone3_uuid}]
            iam2_ops.add_attributes_to_iam2_project(project_uuid, attributes)

    for i in range(1, 61):
        (name, email, phone) = user_info_generator.generate_user_info()
        print name
        print email
        print phone
        virtual_id_uuid = iam2_ops.create_iam2_virtual_id('user-'+str(i), 'b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86').uuid
        #iam2_ops.add_roles_to_iam2_virtual_id([role_uuid], virtual_id_uuid)
        vid_attributes = [{"name": "fullname", "value": name}, {"name": "phone", "value": phone}, {"name": "mail", "value": email}, {"name": "identifier", "value": str(i+10000)} ]
        iam2_ops.add_attributes_to_iam2_virtual_id(virtual_id_uuid, vid_attributes)

        if i > 50:
            platform_attributes = [{"name": "__PlatformAdmin__"}]
            iam2_ops.add_attributes_to_iam2_virtual_id(virtual_id_uuid, platform_attributes)

        project_inv = res_ops.query_resource_fields(res_ops.IAM2_PROJECT) 
        for j in range(0, 5):
            project_uuid = project_inv[j].uuid
            if i == 1:
                iam2_ops.add_iam2_virtual_ids_to_project([virtual_id_uuid], project_uuid)
                proj_attributes = [{"name": "__ProjectAdmin__", "value": project_uuid}]
                iam2_ops.add_attributes_to_iam2_virtual_id(virtual_id_uuid, proj_attributes)
            if i <= 10 and j == 0:
                iam2_ops.add_iam2_virtual_ids_to_project([virtual_id_uuid], project_uuid)
            if i > 10 and i <= 20 and j == 1:
                iam2_ops.add_iam2_virtual_ids_to_project([virtual_id_uuid], project_uuid)
            if i > 20 and i <= 30 and j == 2:
                iam2_ops.add_iam2_virtual_ids_to_project([virtual_id_uuid], project_uuid)
            if i > 30 and i <= 40 and j == 3:
                iam2_ops.add_iam2_virtual_ids_to_project([virtual_id_uuid], project_uuid)
            if i > 40 and i <= 50 and j == 4:
                iam2_ops.add_iam2_virtual_ids_to_project([virtual_id_uuid], project_uuid)

    test_util.test_fail('Create environment with 3 zones 5 projects and 50 users seccess!')


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
