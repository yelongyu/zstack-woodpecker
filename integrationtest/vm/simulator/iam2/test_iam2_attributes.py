# -*- coding: utf-8 -*-
'''
@author: Glody
'''
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.operations.iam2_operations as iam2_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.zstack_test.zstack_test_vid as test_vid
import os

case_flavor = dict(platform_admin=                   dict(target_role='platform_admin'),
                   project_admin=                    dict(target_role='project_admin'),
                   project_operator=                 dict(target_role='project_operator'),
                   )
project_uuid = None
virtual_id_uuid = None

def test():
    global project_uuid, virtual_id_uuid
    flavor = case_flavor[os.environ.get('CASE_FLAVOR')]   
    zone_uuid = res_ops.query_resource(res_ops.ZONE)[0].uuid
    project_name = 'test_project_01'
    attributes = [{"name": "__ProjectRelatedZone__", "value": zone_uuid}]
    project_obj = iam2_ops.create_iam2_project(project_name, attributes=attributes)
    project_uuid = project_obj.uuid
    project_linked_account_uuid = project_obj.linkedAccountUuid
    name = 'username'
    password = 'b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86'
    vid = test_vid.ZstackTestVid()
    vid.create(name, password)
    virtual_id_uuid = vid.get_vid().uuid
    if flavor['target_role'] == 'platform_admin':
        attributes = [{"name": "__PlatformAdmin__"}]
    if flavor['target_role'] == 'project_admin':
        #attributes = [{"name": "__ProjectAdmin__", "value": project_linked_account_uuid}]
        attributes = [{"name": "__ProjectAdmin__", "value": project_uuid}]
    if flavor['target_role'] == 'project_operator':
        attributes = [{"name": "__ProjectAdmin__", "value": project_uuid}]
    iam2_ops.add_attributes_to_iam2_virtual_id(vid.get_vid().uuid, attributes)
    if flavor['target_role'] == 'project_admin' or flavor['target_role'] == 'project_operator':
        iam2_ops.add_iam2_virtual_ids_to_project([vid.get_vid().uuid], project_uuid)
    vid.set_vid_attributes(attributes)
    vid.check()
    test_util.test_pass('success test iam2 attributes!')

# Will be called only if exception happens in test().
def error_cleanup():
    global project_uuid, project_admin_uuid, virtual_id_uuid
    if virtual_id_uuid:
        iam2_ops.delete_iam2_virtual_id(virtual_id_uuid)
    if project_uuid:
        iam2_ops.delete_iam2_project(project_uuid)
        iam2_ops.expunge_iam2_project(project_uuid)

