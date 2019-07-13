'''
test for iam2 no organization vid query permission test

# 1.create VitrualID
# 2.create role without any statements & attach to VirtualID 
# 3.create project & add VirtualID to project
# 4.login platform/project by VirtualID test

@author: zhaohao.chen
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.iam2_operations as iam2_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_lib as test_lib

test_stub = test_lib.lib_get_test_stub()
def test():
    iam2_ops.clean_iam2_enviroment()
    #1.creat VitrualID
    vid_name = 'vid_test'
    password = 'password'
    vid_uuid = iam2_ops.create_iam2_virtual_id(vid_name, password).uuid
    #2.create role without any statements & attach to VirtualID
    role_name = 'void'
    role_uuid = iam2_ops.create_role(role_name).uuid
    iam2_ops.add_roles_to_iam2_virtual_id([role_uuid], vid_uuid)
    #3.create project & add VirtualID to project
    prj_name = 'prj_name'
    prj_uuid = iam2_ops.create_iam2_project(prj_name).uuid
    iam2_ops.add_iam2_virtual_ids_to_project([vid_uuid], prj_uuid)
    #4.login test
    try:
        vid_session_uuid = iam2_ops.login_iam2_virtual_id(vid_name, password)
    except Exception as e:
        test_util.test_fail('%s\n\n Login platform failed!' % e)
    try:
        prj_session_uuid = iam2_ops.login_iam2_project(prj_name, session_uuid=vid_session_uuid).uuid
    except Exception as e:
        test_util.test_fail('%s\n\n Login project failed!' % e)
    test_util.test_pass('Login test success!')
# Will be called only if exception happens in test().
def error_cleanup():
    global vm
    iam2_ops.clean_iam2_enviroment()
    vm.clean()
