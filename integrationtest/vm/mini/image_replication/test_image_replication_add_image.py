'''

New Integration test for image replication.

@author: Legion
'''

import os
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib

test_stub_vr = test_lib.lib_get_test_stub('virtualrouter')
longjob = test_stub_vr.Longjob(name='centos_vdbench', url=os.getenv('imageUrl_vdbench'))
test_stub = test_lib.lib_get_test_stub()

def test():
    global vm
    vm = test_lib.lib_create_vm()
    #vm = test_stub.create_vr_vm('migrate_vm', 'imageName_s', 'l3VlanNetwork2')
    vm.check()

    test_stub.migrate_vm_to_random_host(vm)

    vm.check()

    vm.destroy()
    test_util.test_pass('Migrate VM Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    if vm:
        try:
            vm.destroy()
        except:
            pass
