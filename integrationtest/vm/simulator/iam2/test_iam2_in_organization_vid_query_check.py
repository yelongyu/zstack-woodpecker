'''
test for iam2 vid added to organization query permission test

# 1.create iam2 VirtID
# 2.create role have IAM2 permission and add role to VirtID
# 3.log in by VirtID
# 4.create organizations & add VirtID to organization
# 5.compare VirtID's query results with admin's(uuid = $organization.uuid)

@author: zhaohao.chen
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.iam2_operations as iam2_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_lib as test_lib

test_stub = test_lib.lib_get_test_stub()
password = 'password'
org_type = 'Company'

check_res_list = [res_ops.IAM2_ORGANIZATION, \
                  res_ops.IAM2_PROJECT, \
                  res_ops.IAM2_VIRTUAL_ID_GROUP, \
                  res_ops.IAM2_VIRTUAL_ID, \
                  ]

IAM2_policy_statements =  [{"name": "role-name",
                            "effect": "Allow",
                            "actions": ["org.zstack.iam2.api.APIQueryIAM2OrganizationMsg",
                                        "org.zstack.iam2.api.APIQueryIAM2VirtualIDMsg",
                                        "org.zstack.iam2.api.APILoginIAM2VirtualIDMsg",
                                        "org.zstack.iam2.api.APIQueryIAM2ProjectMsg",
                                        "org.zstack.iam2.api.APILoginIAM2ProjectMsg",
                                        "org.zstack.iam2.api.APIQueryIAM2VirtualIDGroupMsg",
                                        ]}]

def query_result_check(res_list, session_uuid, cond=[]):
    unexcept_ret_list = []
    for res in res_list:
        if res != res_ops.IAM2_VIRTUAL_ID:
            ret_adm = res_ops.query_resource(res, cond)
        else:
            ret_adm = res_ops.query_resource(res)
        #ret_adm = res_ops.query_resource(res)
        ret_vid = res_ops.query_resource(res, session_uuid=session_uuid)
        for adm,vid in zip(ret_adm,ret_vid):
            test_util.test_logger('@@adm:%s\n @@vid:%s' % (adm.uuid, vid.uuid))
            if adm.uuid != vid.uuid:
                test_util.test_logger('%s Result check fialed!\n admin:%s\n vid:%s' % (res, ret_adm, ret_vid))
                unexcept_ret_list.append(res)
                break
    return unexcept_ret_list

def test():
    iam2_ops.clean_iam2_enviroment()
    #1.create virtualID
    vid_name = 'vid_test'
    vid_uuid = iam2_ops.create_iam2_virtual_id(vid_name, password).uuid
    #2.create role & add role to virtualID
    role_name = 'IAM2_test'
    role_uuid = iam2_ops.create_role(role_name, statements=IAM2_policy_statements).uuid
    iam2_ops.add_roles_to_iam2_virtual_id([role_uuid], vid_uuid)
    #3.create organizations & add virtualID to organization 
    org_add_name = 'org_add'
    org_empty_name = 'org_empty'
    org_add_uuid = iam2_ops.create_iam2_organization(org_add_name, org_type).uuid
    org_empty_uuid = iam2_ops.create_iam2_organization(org_empty_name, org_type).uuid
    iam2_ops.add_iam2_virtual_ids_to_organization([vid_uuid], org_add_uuid)
    #4.login by virtualID
    vid_session_uuid = iam2_ops.login_iam2_virtual_id(vid_name, password)
    #5.check query result 
    cond = res_ops.gen_query_conditions('virtualIDs.uuid','=',vid_uuid)
    ret_list = query_result_check(check_res_list, vid_session_uuid, cond)
    if len(ret_list):
        test_util.test_fail('Test Failed, failed list %s ' % ret_list)
    else:
        test_util.test_pass('Test Pass, Check List %s ' % check_res_list)
   
# Will be called only if exception happens in test().
def error_cleanup():
    global vm
    iam2_ops.clean_iam2_enviroment()
    vm.clean()
