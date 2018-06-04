'''
test iam2 project retired

# 1 create project
# 2 add project retired policy
# 3 login project
# 4 change retired policy
# 5 query project

@author: rhZhou
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.iam2_operations as iam2_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import time

project_uuid = None


def test():
    global project_uuid

    # 1 create project
    project_name = 'test_project'
    project_uuid = iam2_ops.create_iam2_project(project_name).uuid

    # 2 add project retired policy
    attributes = [{"name": "__RetirePolicy__", "value": "NoLogin after 20s"}]
    iam2_ops.add_attributes_to_iam2_project(project_uuid, attributes)

    time.sleep(20)

    # 3 login project
    try:
        iam2_ops.login_iam2_project(project_name)
        test_util.test_fail("login project success ,the retire policy is useless")
    except:
        test_util.test_logger("can't login project,retire policy is useful")

    # 4 change retired policy
    enable = 'enable'
    disable = 'disable'
    cond=res_ops.gen_query_conditions('name','=','__RetirePolicy__')
    cond=res_ops.gen_query_conditions('value','=','NoLogin after 20s',cond)
    attribute_uuid=res_ops.query_resource(res_ops.IAM2_PROJECT_ATTRIBUTE,cond)[0].uuid
    iam2_ops.remove_attributes_from_iam2_project(project_uuid, [attribute_uuid])
    iam2_ops.change_iam2_project_state(project_uuid, enable)

    attributes = [{"name": "__RetirePolicy__", "value": "DeleteProject after 20s"}]
    iam2_ops.add_attributes_to_iam2_project(project_uuid, attributes)

    time.sleep(20)

    # 5 query project
    project_inv = res_ops.get_resource(res_ops.IAM2_PROJECT,uuid=project_uuid)[0]
    if project_inv.state != 'Deleted':
        iam2_ops.delete_iam2_project(project_uuid)
        iam2_ops.expunge_iam2_project(project_uuid)
        test_util.test_fail("the project [%s] is still available after 20s " % project_uuid)

    test_util.test_pass("success test project retired")


def error_cleanup():
    global project_uuid
    if project_uuid:
        iam2_ops.delete_iam2_project(project_uuid)
        iam2_ops.expunge_iam2_project(project_uuid)
