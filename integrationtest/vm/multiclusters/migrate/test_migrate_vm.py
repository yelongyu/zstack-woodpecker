'''

New Integration Test for migrate between clusters

@author: quarkonics
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import time
import os

vm = None
test_stub = test_lib.lib_get_test_stub()

def test():
    global vm
    vm = test_stub.create_vm('multicluster_basic_vm', os.environ.get('imageName_s'), os.environ.get('l3VlanNetworkName1'))
    test_stub.migrate_vm_to_differnt_cluster(vm)

    vm.check()

    vm.destroy()
    test_util.test_pass('migrate between clusters Test Success')

#Will be called only if exception happens in test().
def error_cleanup():

    #time.sleep(5)
    global vm
    if vm:
        try:
            vm.destroy()
        except:
            pass
