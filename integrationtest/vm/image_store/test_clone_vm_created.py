'''

New Integration Test for cloning KVM VM to Created VM.

@author: Mirabel
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import time
import os

test_stub = test_lib.lib_get_test_stub()
vn_prefix = 'vm-clone-%s' % time.time()
vm_names = ['%s-vm1' % vn_prefix, '%s-vm2' % vn_prefix, '%s-vm3' % vn_prefix]
new_vms = None

def test():
    global new_vms
    vm = test_stub.create_vm(vm_name = vn_prefix)
    new_vms = vm.clone(vm_names,'JustCreate')

    if len(new_vms) != len(vm_names):
        test_util.test_fail('only %s VMs have been cloned, which is less than required: %s' % (len(new_vms), vm_names))

    #vm.check()

    for new_vm in new_vms:
	new_vm.update()
        new_vm = new_vm.get_vm()
	if new_vm.state == 'Created':
            test_util.test_logger('VM:%s name: %s is created' % (new_vm.uuid, new_vm.name))
        else:
            test_util.test_fail('%s vm name: %s is not created' % (new_vm.uuid, new_vm.name))

    for new_vm in new_vms:
        new_vm.start()
        new_vm.check()

    test_util.test_pass('Clone KVM VM to Created VM Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global new_vms
    if new_vms:
        for new_vm in new_vms:
            try:
                new_vm.destroy()
            except:
                pass

