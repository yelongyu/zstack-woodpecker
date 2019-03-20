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
    global vid_uuid
    flavor = case_flavor[os.environ.get('CASE_FLAVOR')]   

    vid_tst_obj = test_vid.ZstackTestVid()
    password = 'b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86'
    if flavor['target_role'] == 'system_admin':
        attributes = [{"name": "__SystemAdmin__"}]
        username = "systemAdmin"
    elif flavor['target_role'] == 'security_admin':
        attributes = [{"name": "__SecurityAdmin__"}]
        username = "securityAdmin"
    elif flavor['target_role'] == 'audit_admin':
        attributes = [{"name": "__AuditAdmin__"}]
        username = "auditAdmin"
    else:
        test_util.test_fail("not a candidate role")

    vid_tst_obj.create(username, password)
    vid_uuid = vid_tst_obj.get_vid().uuid
    iam2_ops.add_attributes_to_iam2_virtual_id(vid_uuid, attributes)
    read_only_admin_session_uuid = iam2_ops.login_iam2_virtual_id(username, password)

    vid.set_vid_attributes(attributes)
    vid_tst_obj.check()

    test_util.test_pass('success test 3 admins attributes!')

# Will be called only if exception happens in test().
def error_cleanup():
    global vid_uuid
    if vid_uuid:
        iam2_ops.delete_iam2_virtual_id(vid_uuid)

