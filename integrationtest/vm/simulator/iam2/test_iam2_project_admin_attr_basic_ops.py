'''
test iam2 platform admin basic operations
@author: zhaohao.chen
'''
import os
import zstackwoodpecker.test_util as test_util
import apibinding.inventory as inventory
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.operations.iam2_operations as iam2_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.operations.scheduler_operations as schd_ops
import zstackwoodpecker.operations.vxlan_operations as vxlan_ops
import zstackwoodpecker.test_lib as test_lib
import time
from test_iam2_platform_admin_customize_basic_ops import basic_ops

virtual_id_uuid = None
test_stub = test_lib.lib_get_test_stub()
#res_list: l2, l3, image, disk_offering, instance_offering
res_list = [res_ops.L2_NETWORK ,\
            res_ops.L3_NETWORK ,\
            res_ops.IMAGE ,\
            res_ops.DISK_OFFERING ,\
            res_ops.INSTANCE_OFFERING ,\
        ]

def test():
    global virtual_id_uuid
    
    iam2_ops.clean_iam2_enviroment()
    # create vid
    username = "project admin test"
    password = 'b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86'
    virtual_id_uuid = iam2_ops.create_iam2_virtual_id(username, password).uuid
    
    # create project & add vid to project
    prj =  iam2_ops.create_iam2_project('project-test')
    prj_uuid = prj.uuid
    prj_linked_account_uuid = prj.linkedAccountUuid
    iam2_ops.add_iam2_virtual_ids_to_project([virtual_id_uuid], prj_uuid)
 
    # add role to vid & login project
    prj_adm_attr = {'name':'__ProjectAdmin__', 'value':prj_uuid}
    iam2_ops.add_attributes_to_iam2_virtual_id(virtual_id_uuid, [prj_adm_attr])
    vid_session_uuid = iam2_ops.login_iam2_virtual_id(username, password)
    session_uuid = iam2_ops.login_iam2_project('project-test', session_uuid=vid_session_uuid).uuid
    
    #share resources
    res_uuid_list = []
    for res in res_list:
        for inv in res_ops.query_resource(res):
            res_uuid_list.append(inv.uuid)
    acc_ops.share_resources([prj_linked_account_uuid], res_uuid_list)

    #basic_ops test
    basic_ops(session_uuid, prj_linked_account_uuid=prj_linked_account_uuid)
    
    #remove vid from project
    iam2_ops.remove_iam2_virtual_ids_from_project([virtual_id_uuid], prj_uuid)
 
    #delete
    acc_ops.logout(session_uuid)
    iam2_ops.delete_iam2_virtual_id(virtual_id_uuid)
    test_util.test_pass('success test iam2 project admin basic operations!')


def error_cleanup():
    global virtual_id_uuid
    if virtual_id_uuid:
        iam2_ops.delete_iam2_virtual_id(virtual_id_uuid)
