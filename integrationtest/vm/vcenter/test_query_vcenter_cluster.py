'''
test for query vcenter cluster
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

    vcenter_cluster_name = os.environ['vcclusterName']

    #query vcenter cluster
    vcenter_cluster_cond = res_ops.gen_query_conditions("name", '=', vcenter_cluster_name)
    vcc_inv = res_ops.query_resource_fields(res_ops.VCENTER_CLUSTER, vcenter_cluster_cond, None, fields=['uuid'])[0]
    vcc_uuid = vcc_inv.uuid
    if not vcc_uuid:
        test_util.test_fail("not found vcenter cluster")



    test_util.test_pass("query vcenter cluster success")



def error_cleanup():
    pass
