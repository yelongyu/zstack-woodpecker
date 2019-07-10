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


def test():
    global virtual_id_uuid
    
    iam2_ops.clean_iam2_enviroment()
    #create vid
    username = "platform admin test"
    password = 'b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86'
    virtual_id_uuid = iam2_ops.create_iam2_virtual_id(username, password).uuid
    #add role to vid
    cond = res_ops.gen_query_conditions('name','=','Platform admin role')
    platform_admin_role_uuid = res_ops.query_resource(res_ops.ROLE, cond)[0].uuid
    iam2_ops.add_roles_to_iam2_virtual_id([platform_admin_role_uuid], virtual_id_uuid)
    session_uuid = iam2_ops.login_iam2_virtual_id(username, password)
    basic_ops(session_uuid)
    #delete
    acc_ops.logout(session_uuid)
    iam2_ops.delete_iam2_virtual_id(virtual_id_uuid)
    test_util.test_pass('success test iam2 platform admin basic operations!')


def error_cleanup():
    global virtual_id_uuid
    if virtual_id_uuid:
        iam2_ops.delete_iam2_virtual_id(virtual_id_uuid)
