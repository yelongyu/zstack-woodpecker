'''
@author: yuling.ren

test for iam2 delete project cascade volume

# 1 create project
# 2 create projectAdmin  into project
# 3 create volume
# 4 delete project
# 5 expunge project

'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.iam2_operations as iam2_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_lib as test_lib


test_stub = test_lib.lib_get_test_stub()
vm = None
volume = None


def test():
    global vm, volume
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
    project_admin_session_uuid = iam2_ops.login_iam2_virtual_id(project_admin_name, password)
    project_admin_session_uuid = iam2_ops.login_iam2_project(project_name, project_admin_session_uuid).uuid
    res_ops.query_resource(res_ops.L2_VXLAN_NETWORK_POOL)

    # 3 create volume
    vm = test_stub.create_vm(session_uuid=project_admin_session_uuid)
    volume = test_stub.create_volume(session_uuid=project_admin_session_uuid)
    volume.attach(vm)

    # 4 delete project
    iam2_ops.delete_iam2_project(project_uuid)
    cond = res_ops.gen_query_conditions('uuid', '=', volume.get_volume().uuid)
    vol_inv = res_ops.query_resource(res_ops.VOLUME, cond)
    if not vol_inv:
        test_util.test_fail("can't query volume after delete the project ,test fail")

    # 5 expunge project
    iam2_ops.expunge_iam2_project(project_uuid)

    # query volume
    cond = res_ops.gen_query_conditions('uuid', '=', volume.get_volume().uuid)
    vol_inv = res_ops.query_resource(res_ops.VOLUME, cond)[0]
    if vol_inv.status != 'Deleted':
        test_util.test_fail(
            'The volume created in project is still not deleted after the project is expunge ,now status is %s' %
            vol_inv.status)

    volume.expunge()
    vm.clean()
    iam2_ops.clean_iam2_enviroment()
    test_util.test_pass('success')


# Will be called only if exception happens in test().
def error_cleanup():
    global vm, volume
    iam2_ops.clean_iam2_enviroment()
    if vm:
        vm.clean()
    if volume:
        try:
            volume.delete()
        except:
            volume.expunge()
