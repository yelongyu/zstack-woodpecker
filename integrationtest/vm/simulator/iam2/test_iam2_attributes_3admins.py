# -*- coding: utf-8 -*-
'''
@author: SyZhao
'''
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.operations.iam2_operations as iam2_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.zstack_test.zstack_test_vid as test_vid
import os

case_flavor = dict(system_admin=                   dict(target_role='system_admin'),
                   security_admin=                 dict(target_role='security_admin'),
                   audit_admin=                    dict(target_role='audit_admin'),
                   )
vid_uuid = None

def test():
    global vid_uuid, vid_uuid2

    iam2_ops.clean_iam2_enviroment()

    flavor = case_flavor[os.environ.get('CASE_FLAVOR')]   

    password = 'b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86'
    vid_tst_obj = test_vid.ZstackTestVid()
    if flavor['target_role'] == 'system_admin':
        attributes = [{"name": "__SystemAdmin__"}]
        username = "systemAdmin"
        vid_tst_obj = test_vid.ZstackTestVid()
        virtual_id_uuid = vid_tst_obj.get_vid().uuid
        test_stub.create_system_admin(username, password, vid_tst_obj)
        system_admin_session_uuid = acc_ops.login_by_account(username, password)

        #create systemadmin by systemadmin session
        vid_tst_obj2 = test_vid.ZstackTestVid()
        vid_tst_obj2.create(username, password, session_uuid=system_admin_session_uuid, without_default_role="true")
        vid_uuid2 = vid_tst_obj2.get_vid().uuid
        iam2_ops.add_attributes_to_iam2_virtual_id(vid_uuid2, attributes, session_uuid=system_admin_session_uuid)
        role_uuid = iam2_ops.create_role('systemAdminSubRole', session_uuid=system_admin_session_uuid).uuid
        statements = [{"effect":"Allow","actions":["org.zstack.header.image.**"]}]
        iam2_ops.add_policy_statements_to_role(role_uuid, statements, session_uuid=system_admin_session_uuid)
        iam2_ops.add_roles_to_iam2_virtual_id([role_uuid], vid_test_obj2.get_vid().uuid, session_uuid=system_admin_session_uuid)

    elif flavor['target_role'] == 'security_admin':
        attributes = [{"name": "__SecurityAdmin__"}]
        username = "securityAdmin"
        vid_tst_obj.create(username, password, without_default_role="true")
        vid_uuid = vid_tst_obj.get_vid().uuid
        iam2_ops.add_attributes_to_iam2_virtual_id(vid_uuid, attributes)
    elif flavor['target_role'] == 'audit_admin':
        attributes = [{"name": "__AuditAdmin__"}]
        username = "auditAdmin"
        vid_tst_obj.create(username, password, without_default_role="true")
        vid_uuid = vid_tst_obj.get_vid().uuid
        iam2_ops.add_attributes_to_iam2_virtual_id(vid_uuid, attributes)
    else:
        test_util.test_fail("not a candidate role")


    vid_tst_obj.set_vid_attributes(attributes)
    vid_tst_obj.check()
    vid_tst_obj.delete()

    if vid_tst_obj2:
        vid_tst_obj2.delete()

    test_util.test_pass('success test 3 admins attributes!')

# Will be called only if exception happens in test().
def error_cleanup():
    global vid_uuid
    if vid_uuid:
        iam2_ops.delete_iam2_virtual_id(vid_uuid)
    if vid_uuid2:
        iam2_ops.delete_iam2_virtual_id(vid_uuid2)

