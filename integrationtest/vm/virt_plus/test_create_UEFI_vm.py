'''

New Integration test for testing create a vm with UEFI BIOS.

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
import subprocess
import time
import os
import uuid

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    image_name = 'UEFI-image'
    vm = test_stub.create_vm(image_name = os.environ.get('imageName_linux_UEFI'))
    test_obj_dict.add_vm(vm)
    vm.check()
    time.sleep(90)
    vm_ip = vm.get_vm().vmNics[0].ip
    print "vm_ip is : %s" % (vm_ip)
    retcode = subprocess.call(["ping", "-c","4",vm_ip])
    if retcode != 0:
        test_util.test_fail('Create VM Test linux UEFI failed.')
    else:
        test_util.test_pass('Create VM Test linux UEFI Success.')


    vm.destroy()
    test_util.test_pass('Create VM Test linux UEFI Success')

    #Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
