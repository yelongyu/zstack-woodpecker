'''

New Integration test for testing stopped vm migration between hosts.

@author: quarkonics
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.volume_operations as vol_ops

vm = None
test_stub = test_lib.lib_get_test_stub()

def test():
    global vm
    vm = test_stub.create_vr_vm('migrate_stopped_m', 'imageName_s', 'l3VlanNetwork2')
    vm.check()
    target_host = test_lib.lib_find_random_host(vm.vm)
    vm.stop()
    vol_ops.migrate_volume(vm.get_vm().allVolumes[0].uuid, target_host.uuid)
    vm.check()
    vm.start()
    vm.check()

    vm.destroy()
    test_util.test_pass('Migrate Stopped VM Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    if vm:
        try:
            vm.destroy()
        except:
            pass
