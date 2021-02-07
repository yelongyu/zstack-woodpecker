'''
test for iam2 no organization vid query permission test

# 1.create iam2 VirtID
# 2.create role have IAM2 permission and add role to VirtID
# 3.log in by VirtID
# 4.compare VirtID's query results with admin's

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

def query_result_check(res_list, session_uuid):
    unexpected_ret_list = []
    for res in res_list:
        #test_util.test_logger(res_ops.query_resource(res_list[0]))
        ret_adm = res_ops.query_resource(res)
        ret_vid = res_ops.query_resource(res, session_uuid=session_uuid)
        if len(ret_adm) != len(ret_vid):
            unexpected_ret_list.append((ret_adm, ret_vid))
    return unexpected_ret_list

def test():
    iam2_ops.clean_iam2_enviroment()
    #1.create virtualIDs
    vid_name = 'vid_test'
    vid_uuid = iam2_ops.create_iam2_virtual_id(vid_name, password).uuid
    vid_name_2 = 'vid_test_2'
    iam2_ops.create_iam2_virtual_id(vid_name_2, password)
    #2.create role & add role to virtualID
    role_name = 'IAM2_test'
    role_uuid = iam2_ops.create_role(role_name, statements=IAM2_policy_statements).uuid
    iam2_ops.add_roles_to_iam2_virtual_id([role_uuid], vid_uuid)
    #3.login by virtualID
    vid_session_uuid = iam2_ops.login_iam2_virtual_id(vid_name, password)
    #4.check query result 
    ret_list = query_result_check(check_res_list, vid_session_uuid)
    if len(ret_list):
        test_util.test_fail('Test Failed, failed list %s ' % ret_list)
    else:
        test_util.test_pass('Test Pass, Check List %s ' % check_res_list)
   
# Will be called only if exception happens in test().
def error_cleanup():
    global vm
    iam2_ops.clean_iam2_enviroment()
    vm.clean()
