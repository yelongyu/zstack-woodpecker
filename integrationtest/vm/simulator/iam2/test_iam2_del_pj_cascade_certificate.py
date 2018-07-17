'''

Test for iam2 delete project cascade certificate.

@author: ronghao.zhou
'''

import os
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
#import simulator.test_stub as test_stub
import zstackwoodpecker.operations.iam2_operations as iam2_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.account_operations as acc_ops

test_stub = test_lib.lib_get_test_stub()
cert = None

def test():
    global cert

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

    cert = net_ops.create_certificate('certificate_for_pm', 'fake certificate', session_uuid=project_admin_session_uuid)
    acc_ops.logout(project_admin_session_uuid)

    # 4 delete project
    iam2_ops.delete_iam2_project(project_uuid)
    iam2_ops.expunge_iam2_project(project_uuid)

    # 5 check for cascade delete
    cond = res_ops.gen_query_conditions('uuid','=',cert.uuid)
    cert_inv = res_ops.query_resource(res_ops.CERTIFICATE,cond)
    if not cert_inv:
        test_util.test_fail("certificate should not be cascade delete after delete project,test fail ")

    net_ops.delete_certificate(cert.uuid)
    iam2_ops.clean_iam2_enviroment()
    test_util.test_pass('Create Simple VM Stop Start Scheduler Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global  cert
    iam2_ops.clean_iam2_enviroment()
    if cert:
        net_ops.delete_certificate(cert.uuid)

