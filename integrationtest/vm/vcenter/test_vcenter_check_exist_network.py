'''
test for add and delete vcenter
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

    vc_network = os.environ['vcenterDefaultNetwork']

    #insert the basic operations for the newly join in vcenter resourse
    vm_network_list = []
    vm_network_names = res_ops.query_resource_fields(res_ops.L3_NETWORK, [], None, fields=['name'])
    for vm_network in vm_network_names:
        vm_network_list.append(vm_network.name)

    test_util.test_logger( ", ".join( [ str(vm_network_tmp) for vm_network_tmp in vm_network_list ] ) )

    if vc_network not in vm_network_list:
        test_util.test_fail("newly joined vcenter missing vm network1, test failed")

    test_util.test_pass("query network test passed.")



def error_cleanup():
    pass
