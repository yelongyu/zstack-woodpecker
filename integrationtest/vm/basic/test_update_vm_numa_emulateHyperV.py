'''

New Integration Test for creating KVM VM and set numa emulateHyperV for it.

@author: Pengtao.Zhang
'''

import zstackwoodpecker.test_util as test_util
import test_stub
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.config_operations as conf_ops
import zstackwoodpecker.operations.vm_operations as vm_ops

_config_ = {
        'timeout' : 360,
        'noparallel' : False
        }

vm = None

def test():
    global vm
    vm = test_stub.create_vm()
    vm.check()
    vm_inv=vm.get_vm()
    vm_uuid=vm_inv.uuid
    conf_ops.change_cluster_config('vm', 'numa', 'true', vm_uuid)
    conf_ops.change_cluster_config('vm', 'emulateHyperV', 'true', vm_uuid)
    vm.reboot()
    vm.check()

    test_util.test_logger('change the vm cpu memeory after enable numa')
    new_cpu = 2
    new_mem = 1*1024*1024*1024
    vm_ops.update_vm(vm_uuid, cpu=new_cpu,  memory=new_mem)

    conf_ops.change_cluster_config('vm', 'numa', 'false', vm_uuid)
    conf_ops.change_cluster_config('vm', 'emulateHyperV', 'false', vm_uuid)
    test_util.test_logger('change the vm cpu memeory after disable numa')
    new_cpu1 = 3
    new_mem1 = 2*1024*1024*1024

    try:
        vm_ops.update_vm(vm_uuid, cpu=new_cpu1,  memory=new_mem1)
    except:
        test_util.test_logger('can not change cpu and mem while numa is disabled')

    vm.destroy()
    vm.check()
    test_util.test_pass('Create VM with spice and spiceStreamingMode is all Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    if vm:
        vm.destroy()
