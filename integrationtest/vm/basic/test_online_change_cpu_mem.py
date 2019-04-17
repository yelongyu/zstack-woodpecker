'''

New Integration Test for creating KVM VM and online change mem when host's cpu negative number.
and online change cpu when host's mem negative number.

@author: ye.tian  2018-11-28
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
    conf_ops.change_global_config('vm', 'numa', 'true')
    vm = test_stub.create_vm()
    vm.check()
    vm_inv=vm.get_vm()
    vm_uuid=vm_inv.uuid

    #change the vm's mem when host's cpu negative number
    test_util.test_logger('change the vm mem when host cpu negative number')
    big_cpu = 20
    vm_ops.update_vm(vm_uuid, cpu=big_cpu)   
    conf_ops.change_global_config('host', 'cpu.overProvisioning.ratio', '5')
    new_mem = 2*1024*1024*1024
    vm_ops.update_vm(vm_uuid, memory=new_mem)   

    #change the vm's cpu when host's memory  negative number
    test_util.test_logger('change the vm mem when host cpu negative number')
    conf_ops.change_global_config('mevoco', 'overProvisioning.memory', '3')
    vm.stop()
    small_cpu = 2
    big_mem = 1*1024*1024*1024
    vm_ops.update_vm(vm_uuid, cpu=small_cpu,  memory=big_mem)

    vm.start()
    conf_ops.change_global_config('mevoco', 'overProvisioning.memory', '1')
    new_cpu = 2
    vm_ops.update_vm(vm_uuid, cpu=new_cpu)

    #change the vm's cpu when host's memory  negative number
    test_util.test_logger('change the vm mem and cpu when host cpu and memroy are enough')
    conf_ops.change_global_config('mevoco', 'overProvisioning.memory', '1')
    conf_ops.change_global_config('host', 'cpu.overProvisioning.ratio', '10')
    vm.stop()
    cpu1 = 1
    mem1 = 1*1024*1024*1024
    vm_ops.update_vm(vm_uuid, cpu=cpu1,  memory=mem1)

    vm.start()
    cpu2 = 2
    mem2 = 2*1024*1024*1024
    vm_ops.update_vm(vm_uuid, cpu=cpu2, memory=mem2)

    #restore default settings
    conf_ops.change_global_config('vm', 'numa', 'false')
    conf_ops.change_global_config('host', 'cpu.overProvisioning.ratio', '10')
    conf_ops.change_global_config('mevoco', 'overProvisioning.memory', '1')
    vm.destroy()
    vm.check()
    test_util.test_pass('Create VM with spice and spiceStreamingMode is all Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    conf_ops.change_global_config('host', 'cpu.overProvisioning.ratio', '10')
    conf_ops.change_global_config('mevoco', 'overProvisioning.memory', '1')
    conf_ops.change_global_config('vm', 'numa', 'false')
    if vm:
        vm.destroy()
