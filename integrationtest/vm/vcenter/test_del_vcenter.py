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
import time
import os 



def test():

    vcenter_uuid = res_ops.get_resource(res_ops.VCENTER)[0].uuid
    vct_ops.delete_vcenter(vcenter_uuid)
    test_util.test_pass("delete vcenter test passed")



def error_cleanup():
    pass
