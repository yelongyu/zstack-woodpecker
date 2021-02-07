'''
test for checking if template existed in newly add vcenter
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
    vc_ova_template = os.environ['vcenterDefaultmplate']

    #insert the basic operations for the newly join in vcenter resourse
    image_list = []
    image_names = res_ops.query_resource_fields(res_ops.IMAGE, [], None, fields=['name'])
    for image_name in image_names:
        image_list.append(image_name.name)

    test_util.test_logger( ", ".join( [ str(image_name_tmp) for image_name_tmp in image_list ] ) )

    if vc_ova_template not in image_list:
        test_util.test_fail("newly joined vcenter missing fingerprint vm1, test failed")

    test_util.test_pass("query template test passed.")



def error_cleanup():
    pass
