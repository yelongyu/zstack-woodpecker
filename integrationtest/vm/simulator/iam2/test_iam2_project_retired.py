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
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import time

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()


def test():
    global test_obj_dict

    iam2_ops.clean_iam2_enviroment()

    # 1 create project
    project_name = 'test_project'
    project = iam2_ops.create_iam2_project(project_name)
    project_uuid = project.uuid
    linked_account_uuid = project.linkedAccountUuid
    zone_inv = res_ops.query_resource(res_ops.ZONE)
    attributes = [{"name": "__ProjectRelatedZone__", "value": zone_inv[0].uuid}]
    iam2_ops.add_attributes_to_iam2_project(project_uuid, attributes)
    test_stub.share_admin_resource_include_vxlan_pool([linked_account_uuid])

    # 2 update project quota
    acc_ops.update_quota(linked_account_uuid, 'volume.data.num', '1')
    cond = res_ops.gen_query_conditions('identityUuid', '=', linked_account_uuid)
    cond = res_ops.gen_query_conditions('name', '=', 'volume.data.num', cond)
    project_quota = res_ops.query_resource(res_ops.QUOTA, cond)

    if project_quota:
        if project_quota[0].value != 1:
            test_util.test_fail("update project quata fail")

    # 3 create virtual id and login project
    username = 'username'
    password = \
        'b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86'
    attributes = [{"name": "__ProjectOperator__", "value": project_uuid}]
    virtual_id_uuid = iam2_ops.create_iam2_virtual_id(username, password, attributes=attributes).uuid
    iam2_ops.add_iam2_virtual_ids_to_project([virtual_id_uuid], project_uuid)

    virtual_id_session = iam2_ops.login_iam2_virtual_id(username, password)
    virtual_id_session = iam2_ops.login_iam2_project(project_name, virtual_id_session).uuid
    volume = test_stub.create_volume(session_uuid=virtual_id_session)
    test_obj_dict.add_volume(volume)
    try:
        volume = test_stub.create_volume(session_uuid=virtual_id_session)
        test_obj_dict.add_volume(volume)
        test_util.test_fail("create more than one data volume in project ,test fail")
    except:
        test_util.test_dsc("success test limit create only 1 vm")

    acc_ops.logout(virtual_id_session)

    # 4 add project retired policy
    attributes = [{"name": "__RetirePolicy__", "value": "NoLogin after 20s"}]
    iam2_ops.add_attributes_to_iam2_project(project_uuid, attributes)

    time.sleep(20)

    # 5 login project
    virtual_id_session = iam2_ops.login_iam2_virtual_id(username, password)
    try:
        iam2_ops.login_iam2_project(project_name, session_uuid=virtual_id_session)
        test_util.test_fail("login project success ,the retire policy is useless")
    except:
        test_util.test_logger("can't login project,retire policy is useful")

    # 6 change retired policy
    enable = 'enable'
    disable = 'disable'
    cond = res_ops.gen_query_conditions('name', '=', '__RetirePolicy__')
    cond = res_ops.gen_query_conditions('value', '=', 'NoLogin after 20s', cond)
    attribute_uuid = res_ops.query_resource(res_ops.IAM2_PROJECT_ATTRIBUTE, cond)[0].uuid
    iam2_ops.remove_attributes_from_iam2_project(project_uuid, [attribute_uuid])
    iam2_ops.change_iam2_project_state(project_uuid, enable)

    attributes = [{"name": "__RetirePolicy__", "value": "DeleteProject after 20s"}]
    iam2_ops.add_attributes_to_iam2_project(project_uuid, attributes)

    time.sleep(20)

    # 7 query project
    project_inv = res_ops.get_resource(res_ops.IAM2_PROJECT, uuid=project_uuid)[0]
    if project_inv.state != 'Deleted':
        iam2_ops.delete_iam2_project(project_uuid)
        iam2_ops.expunge_iam2_project(project_uuid)
        test_util.test_fail("the project [%s] is still available after 20s " % project_uuid)

    test_lib.lib_robot_cleanup(test_obj_dict)
    iam2_ops.clean_iam2_enviroment()

    test_util.test_pass("success test project retired")


def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
    iam2_ops.clean_iam2_enviroment()
