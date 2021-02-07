
		
'''
@author: fangxiao

'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.iam2_operations as iam2_ops
import zstackwoodpecker.operations.affinitygroup_operations as ag_ops
import zstackwoodpecker.operations.resource_operations as res_ops

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()


affinity_group_inv = None
project_uuid = None
project_operator_uuid = None
def test():
    global affinity_group_inv,project_uuid,project_operator_uuid



    # 1 create project
    project_name = 'test_project6'
    project_uuid = iam2_ops.create_iam2_project(project_name).uuid

    # 2 create project operator 
    project_operator_name = 'username6'
    project_operator_password = 'b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86'
    attributes = [{"name": "__ProjectOperator__", "value": project_uuid}]
    project_operator_uuid = iam2_ops.create_iam2_virtual_id(project_operator_name,project_operator_password,attributes=attributes).uuid

    # 3 login in project by project operator
    iam2_ops.add_iam2_virtual_ids_to_project([project_operator_uuid],project_uuid)
    project_operator_session_uuid = iam2_ops.login_iam2_virtual_id(project_operator_name,project_operator_password)
    project_login_uuid = iam2_ops.login_iam2_project(project_name,session_uuid=project_operator_session_uuid).uuid

    # 4 create affinity group and add vm into affinity group
    ag1 = ag_ops.create_affinity_group(name="ag1",policy="antiHard",session_uuid=project_login_uuid)
    vm1 = test_stub.create_ag_vm(affinitygroup_uuid=ag1.uuid)
    test_obj_dict.add_vm(vm1)

    # 5 delete and expunge the project and check the affinity group
    iam2_ops.delete_iam2_project(project_uuid)
    iam2_ops.expunge_iam2_project(project_uuid)
    cond = res_ops.gen_query_conditions("appliance",'=',"CUSTOMER")
    affinity_group_inv = res_ops.query_resource(res_ops.AFFINITY_GROUP,cond)
    if affinity_group_inv:
        test_util.test_fail(
            "affinity_group [%s] is still exist after expunge the project[%s]" % (affinity_group_inv[0].uuid,project_login_uuid))

    # 6 delete 
    iam2_ops.delete_iam2_virtual_id(project_operator_uuid)

def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
    if affinity_group_inv:
        ag_ops.delete_affinity_group(affinity_group_inv[0].uuid)
    if project_uuid:
        iam2_ops.delete_iam2_project(project_uuid)
        iam2_ops.expunge_iam2_project(project_uuid)
    if project_operator_uuid:
        iam2_ops.delete_iam2_virtual_id(project_operator_uuid)
		
        

