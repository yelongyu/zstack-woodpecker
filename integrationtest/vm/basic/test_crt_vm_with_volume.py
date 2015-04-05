'''

Creating VM with providing data volume offereing UUID

@author: Youyk
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import test_stub

vm = None

def test():
    global vm
    vm = test_stub.create_vm_with_volume()
    vm.check()
    volumes_number = len(test_lib.lib_get_all_volumes(vm.vm))
    if volumes_number != 2:
        test_util.test_fail('Did not find 2 volumes for [vm:] %s. But we assigned 1 data volume when create the vm. We only catch %s volumes' % (vm.vm.uuid, volumes_number))
    else:
        test_util.test_logger('Find 2 volumes for [vm:] %s.' % vm.vm.uuid)

    vm.destroy()
    vm.check()
    test_util.test_pass('Create VM Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    if vm:
        vm.destroy()
