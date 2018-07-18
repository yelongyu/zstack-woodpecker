'''
@author: yuling.ren

test for iam2 delete project cascade vm

# 1 create project
# 2 create projectAdmin  into project
# 3 create vm
# 4 delete project
# 5 recover project
# 6 expunge project


'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.iam2_operations as iam2_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_lib as test_lib

test_stub = test_lib.lib_get_test_stub()
vm = None

def test():
    global vm
    iam2_ops.clean_iam2_enviroment()
    zone_uuid = res_ops.get_resource(res_ops.ZONE)[0].uuid

    # 1 create project
    project_name = 'test_project'
    password = \
        'b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86'
    project = iam2_ops.create_iam2_project(project_name)
    project_uuid = project.uuid
    linked_account_uuid = project.linkedAccountUuid
    attributes = [{"name": "__ProjectRelatedZone__", "value": zone_uuid}]
    iam2_ops.add_attributes_to_iam2_project(project_uuid, attributes)
    test_stub.share_admin_resource_include_vxlan_pool([linked_account_uuid])

    # 2 create projectAdmin  into project
    project_admin_name = 'projectadmin'
    project_admin_uuid = iam2_ops.create_iam2_virtual_id(project_admin_name, password).uuid
    iam2_ops.add_iam2_virtual_ids_to_project([project_admin_uuid], project_uuid)
    attributes = [{"name": "__ProjectAdmin__", "value": project_uuid}]
    iam2_ops.add_attributes_to_iam2_virtual_id(project_admin_uuid, attributes)
    project_admin_session_uuid = iam2_ops.login_iam2_virtual_id(project_admin_name,password)
    project_admin_session_uuid = iam2_ops.login_iam2_project(project_name,project_admin_session_uuid).uuid
    res_ops.query_resource(res_ops.L2_VXLAN_NETWORK_POOL)

    # 3 create vm
    vm = test_stub.create_vm(session_uuid = project_admin_session_uuid)

    # 4 delete project
    iam2_ops.delete_iam2_project(project_uuid)
    cond = res_ops.gen_query_conditions('uuid','=',vm.get_vm().uuid)
    vm_inv = res_ops.query_resource(res_ops.VM_INSTANCE,cond)[0]
    if vm_inv.state == 'Running':
        test_util.test_fail("the vm is still running after delete project,test fail")

    # 5 recover project
    vm.update()
    iam2_ops.recover_iam2_project(project_uuid)
    vm.start()

    # 6 expunge project
    iam2_ops.delete_iam2_project(project_uuid)
    iam2_ops.expunge_iam2_project(project_uuid)
    vm.update()

    # query vm
    cond = res_ops.gen_query_conditions('uuid','=',vm.get_vm().uuid)
    vm_inv = res_ops.query_resource(res_ops.VM_INSTANCE,cond)[0]
    if vm_inv.state != 'Destroyed':
        test_util.test_fail('The vminstance created by project is not Destroyed ,the state now is %s , test fail'% vm_inv.state)

    vm.clean()
    iam2_ops.clean_iam2_enviroment()
    test_util.test_pass('success')

# Will be called only if exception happens in test().
def error_cleanup():
    global vm
    iam2_ops.clean_iam2_enviroment()
    vm.clean()
