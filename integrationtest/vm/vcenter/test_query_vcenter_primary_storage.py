'''
test query for vcenter primary storage
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
import os 



def test():
    vcenter_primary_storage_name = os.environ['vcvmfsdatastore']
    #query vcenter cluster
    vcenter_primary_storage_cond = res_ops.gen_query_conditions("name", '=', vcenter_primary_storage_name)
    vcps_inv = res_ops.query_resource_fields(res_ops.VCENTER_PRIMARY_STORAGE, vcenter_primary_storage_cond, None, fields=['uuid'])[0]
    vcps_uuid = vcps_inv.uuid
    if not vcps_uuid:
        test_util.test_fail("not found vcenter primary storage")



    test_util.test_pass("query vcenter primary storage success")



def error_cleanup():
    pass
