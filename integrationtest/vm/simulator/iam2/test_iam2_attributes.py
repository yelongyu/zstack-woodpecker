# -*- coding: utf-8 -*-
'''
@author: Glody
'''
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.operations.iam2_operations as iam2_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.zstack_test.zstack_test_vid as test_vid

def test():

    zone_uuid = res_ops.query_resource(res_ops.ZONE)[0].uuid
    project_name = 'test_project_01'
    attributes = [{"name": "__ProjectRelatedZone__", "value": zone_uuid}]
    project_obj = iam2_ops.create_iam2_project(project_name, attributes=attributes)
    project_uuid = project_obj.uuid
    project_linked_account_uuid = project_obj.linkedAccountUuid

    name = 'username'
    name1 = 'username1'
    name2 = 'username2'
    password = 'b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86'

    vid = test_vid.ZstackTestVid()
    vid.create(name, password)
    attributes = [{"name": "__PlatformAdmin__"}]
    iam2_ops.add_attributes_to_iam2_virtual_id(vid.get_vid().uuid, attributes)
    vid.set_vid_attributes(attributes)
    vid.check()
    attributes = [{"name": "__ProjectAdmin__", "value": project_linked_account_uuid}]

    vid1 = test_vid.ZstackTestVid()
    vid1.create(name1, password)
    iam2_ops.add_iam2_virtual_ids_to_project([vid1.get_vid().uuid], project_uuid)
    attributes = [{"name": "__ProjectAdmin__", "value": project_uuid}]
    iam2_ops.add_attributes_to_iam2_virtual_id(vid1.get_vid().uuid, attributes)
    vid1.set_vid_attributes(attributes)
    vid1.check()

    vid2 = test_vid.ZstackTestVid()
    vid2.create(name2, password)
    iam2_ops.add_iam2_virtual_ids_to_project([vid2.get_vid().uuid], project_uuid)
    attributes = [{"name": "__ProjectOperator__", "value": project_uuid}]
    iam2_ops.add_attributes_to_iam2_virtual_id(vid2.get_vid().uuid, attributes)
    vid2.set_vid_attributes(attributes)
    vid2.check()


# Will be called only if exception happens in test().
def error_cleanup():
    pass
