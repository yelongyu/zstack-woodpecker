'''

New Integration test for testing create a vm with think Provision root volume on mini.

@author: Pengtao.Zhang
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.zstack_test.zstack_test_image as test_image
import zstackwoodpecker.header.vm as vm_header
import time
import os
import uuid

test_obj_dict = test_state.TestStateDict()

def test():

    create_vm_option = test_util.VmOption()
    create_vm_option.set_name('test_create_ThinProvisioning_vm')
    create_vm_option.set_rootVolume_systemTags(["volumeProvisioningStrategy::ThinProvisioning"])
    vm_1 = test_lib.lib_create_vm(create_vm_option)
    vm_1.check()
    test_obj_dict.add_vm(vm_1)
    vm_1.destroy()
    test_util.test_pass('Create VM Test Success')


    #Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)