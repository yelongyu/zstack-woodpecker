'''
test iam2 project admin do negtive operations

# 1 create project
# 2 create projectAdmin
# 3 create virtual ID by projectAdmin
# 4 create PlatformAdmin by PorjectAdmin
# 5 create ProjectAdmin by ProjectAdmin
# 6 create ProjectOperator in other project

@author: rhZhou
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

    project_name_02='test_project_02'
    project_uuid_02 = iam2_ops.create_iam2_project(project_name_02).uuid

    # 2 create projectAdmin
    username = 'username'
    password = 'b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86'
    project_admin_uuid = iam2_ops.create_iam2_virtual_id(username, password).uuid
    iam2_ops.add_iam2_virtual_ids_to_project([project_admin_uuid],project_uuid)
    attributes = [{"name": "__ProjectAdmin__", "value": project_uuid}]
    iam2_ops.add_attributes_to_iam2_virtual_id(project_admin_uuid, attributes)
    project_admin_login_uuid = iam2_ops.login_iam2_virtual_id(username, password)
    project_admin_login_uuid = iam2_ops.login_iam2_project(project_name, project_admin_login_uuid)

    # 3 create virtual ID by projectAdmin
    username_02 = 'username_02'
    try:
        virtual_id_uuid = iam2_ops.create_iam2_virtual_id(username_02, password,
session_uuid=project_admin_login_uuid).uuid
        test_util.test_fail("ProjectAdmin can't create virtual ID")
    except:
        pass

    virtual_id_uuid = iam2_ops.create_iam2_virtual_id(username_02, password).uuid
    iam2_ops.add_iam2_virtual_ids_to_project([virtual_id_uuid],project_uuid)
    iam2_ops.add_iam2_virtual_ids_to_project([virtual_id_uuid],project_uuid_02)

    # 4 create PlatformAdmin by PorjectAdmin
    attributes = [{"name":"__PlatformAdmin__"}]
    try:
        iam2_ops.add_attributes_to_iam2_virtual_id(virtual_id_uuid,attributes,session_uuid=project_admin_login_uuid)
        test_util.test_fail("ProjectAdmin can't create PlatformAdmin")
    except:
        pass

    # 5 create ProjectAdmin by ProjectAdmin
    attributes = [{"name": "__ProjectAdmin__", "value": project_uuid}]
    try:
        iam2_ops.add_attributes_to_iam2_virtual_id(virtual_id_uuid, attributes,session_uuid=project_admin_login_uuid)
        test_util.test_fail("ProjectAdmin can't create ProjectAdmin")
    except:
        pass

    # 6 create ProjectOperator in other project
    attributes = [{"name": "__ProjectOperator__", "value": project_uuid_02}]
    try:
        iam2_ops.add_attributes_to_iam2_virtual_id(virtual_id_uuid, attributes, session_uuid=project_admin_login_uuid)
        test_util.test_fail("ProjectAdmin can't create ProjectOperator in other project")
    except:
        pass

    fake_virtual_uuid='iamafakevirtualiduuid'
    try:
        iam2_ops.add_iam2_virtual_ids_to_project([fake_virtual_uuid],project_uuid,session_uuid=project_admin_login_uuid)
        test_util.test_fail("can't add fake virtual id into project")
    except:
        pass

    iam2_ops.clean_iam2_enviroment()
    test_util.test_pass("success test  ProjectAdmin negtive operations")

def error_cleanup():
    iam2_ops.clean_iam2_enviroment()