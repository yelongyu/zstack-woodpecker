'''
test for iam2 vid added to project query result check

# 1.create iam2 VirtIDs
# 2.create role have IAM2 permission and add role to VirtID
# 3.log in by VirtID
# 4.create organizations & add VirtIDs to organizations
# 5.create project & add VirtIDs to project
# 6.check VirtIDs' query virtualID results

@author: zhaohao.chen
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.iam2_operations as iam2_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_lib as test_lib

test_stub = test_lib.lib_get_test_stub()
password = 'password'
org_type = 'Company'

IAM2_policy_statements =  [{"name": "role-name",
                            "effect": "Allow",
                            "actions": ["org.zstack.iam2.api.APIQueryIAM2OrganizationMsg",
                                        "org.zstack.iam2.api.APIQueryIAM2VirtualIDMsg",
                                        "org.zstack.iam2.api.APILoginIAM2VirtualIDMsg",
                                        "org.zstack.iam2.api.APIQueryIAM2ProjectMsg",
                                        "org.zstack.iam2.api.APILoginIAM2ProjectMsg",
                                        "org.zstack.iam2.api.APIQueryIAM2VirtualIDGroupMsg"]}]

def test():
    iam2_ops.clean_iam2_enviroment()
    #1.create virtualIDs
    vid_name_1 = 'vid_test_1'
    vid_name_2 = 'vid_test_2'
    vid_name_3 = 'vid_test_3'
    vid_uuid_1 = iam2_ops.create_iam2_virtual_id(vid_name_1, password).uuid
    vid_uuid_2 = iam2_ops.create_iam2_virtual_id(vid_name_2, password).uuid
    vid_uuid_3 = iam2_ops.create_iam2_virtual_id(vid_name_3, password).uuid
    #2.create role & add role to virtualID
    role_name = 'IAM2_test'
    role_uuid = iam2_ops.create_role(role_name, statements=IAM2_policy_statements).uuid
    iam2_ops.add_roles_to_iam2_virtual_id([role_uuid], vid_uuid_1)
    iam2_ops.add_roles_to_iam2_virtual_id([role_uuid], vid_uuid_2)
    iam2_ops.add_roles_to_iam2_virtual_id([role_uuid], vid_uuid_3)
    #3.create organizations & add virtualIDs to organizations
    org_name_1 = 'org_1'
    org_name_2 = 'org_2'
    org_name_3 = 'org_3'
    org_uuid_1 = iam2_ops.create_iam2_organization(org_name_1, org_type).uuid
    org_uuid_2 = iam2_ops.create_iam2_organization(org_name_2, org_type).uuid
    org_uuid_3 = iam2_ops.create_iam2_organization(org_name_3, org_type).uuid
    iam2_ops.add_iam2_virtual_ids_to_organization([vid_uuid_1], org_uuid_1)
    iam2_ops.add_iam2_virtual_ids_to_organization([vid_uuid_2], org_uuid_2)
    iam2_ops.add_iam2_virtual_ids_to_organization([vid_uuid_3], org_uuid_3)
    #4.create project & add v1,v2 to project
    project_name = 'prj_test'
    project_uuid = iam2_ops.create_iam2_project(project_name).uuid
    iam2_ops.add_iam2_virtual_ids_to_project([vid_uuid_1, vid_uuid_2], project_uuid)
    #5.login by virtualID
    vid_session_uuid_1 = iam2_ops.login_iam2_virtual_id(vid_name_1, password)
    vid_session_uuid_2 = iam2_ops.login_iam2_virtual_id(vid_name_2, password)
    vid_session_uuid_3 = iam2_ops.login_iam2_virtual_id(vid_name_3, password)
    project_login_uuid_1 = iam2_ops.login_iam2_project(project_name, vid_session_uuid_1).uuid
    project_login_uuid_2 = iam2_ops.login_iam2_project(project_name, vid_session_uuid_2).uuid
    #6.check query result 
    #ret_1 = res_ops.query_resource(res_ops.IAM2_VIRTUAL_ID, session_uuid=vid_session_uuid_1)
    ret_1 = res_ops.query_resource(res_ops.IAM2_VIRTUAL_ID, session_uuid=project_login_uuid_1)
    #ret_2 = res_ops.query_resource(res_ops.IAM2_VIRTUAL_ID, session_uuid=vid_session_uuid_2)
    ret_2 = res_ops.query_resource(res_ops.IAM2_VIRTUAL_ID, session_uuid=project_login_uuid_2)
    cond = res_ops.gen_query_conditions('projects.uuid','=',project_uuid)
    ret_admin = res_ops.query_resource(res_ops.IAM2_VIRTUAL_ID,cond)
    if len(ret_admin) != len(ret_2) or len(ret_admin) != len(ret_1):
        test_util.test_fail('Test Failed, length of query result is not %s\n v1:%s\n v2:%s\n' % (len(ret_admin),len(ret_1),len(ret_2)))
    for r1,r2 in zip(ret_1,ret_2):
        if r1.uuid != r2.uuid:
           test_util.test_fail('Test Failed, r1:%s\n r2:%s' % (r1.uuid, r2.uuid))
    test_util.test_pass('Test Pass')

# Will be called only if exception happens in test().
def error_cleanup():
    global vm
    iam2_ops.clean_iam2_enviroment()
    vm.clean()
