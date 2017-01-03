'''
test query for vcenter backup storage
@author: SyZhao
'''

import apibinding.inventory as inventory
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.vcenter_operations as vct_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstacklib.utils.ssh as ssh
import test_stub
import time
import os 


vcenter_uuid = None
vcenter_backup_storage_name = r"vCenter[VM-VCENTER1]"


def test():
    global vcenter_uuid

    vcenter1_name = os.environ['vcenter1_name']
    vcenter1_domain_name = os.environ['vcenter1_ip']
    vcenter1_username = os.environ['vcenter1_domain_name']
    vcenter1_password = os.environ['vcenter1_password']


    zone_uuid = res_ops.get_resource(res_ops.ZONE)[0].uuid
    inv = vct_ops.add_vcenter(vcenter1_name, vcenter1_domain_name, vcenter1_username, vcenter1_password, True, zone_uuid)
    vcenter_uuid = inv.uuid

    if vcenter_uuid == None:
        test_util.test_fail("vcenter_uuid is None")


    vcenter_backup_storage_cond = res_ops.gen_query_conditions("name", '=', vcenter_backup_storage_name) 
    vcbs_inv = res_ops.query_resource_fields(res_ops.VCENTER_BACKUP_STORAGE, vcenter_backup_storage_cond, None, fields=['uuid'])[0]
    vcbs_uuid = vcbs_inv.uuid
    if not vcbs_uuid:
        test_util.test_fail("not found vcenter backup storage")

 
    vct_ops.delete_vcenter(vcenter_uuid)
    test_util.test_pass("add && delete vcenter test passed.")



def error_cleanup():
    global vcenter_uuid
    if vcenter_uuid:
        vct_ops.delete_vcenter(vcenter_uuid)
