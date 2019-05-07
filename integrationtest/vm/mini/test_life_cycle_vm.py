'''

VM life cycle test for Mini

@author: Zhaohao
'''
import apibinding.inventory as inventory
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import time
import os
import random

vm = None
#state
RUNNING = inventory.RUNNING
STOPPED = inventory.STOPPED
DESTROYED = inventory.DESTROYED
PAUSED = inventory.PAUSED
EXPUNGED = 'EXPUNGED'

VM_CPU = [1, 2, 3, 4, 7, 8, 15, 16, 20, 32]

# 128M, 256M, 512M, 1G, 2G
VM_MEM = [134217728, 268435456, 536870912, 1073741824, 2147483648]

def random_operations(vm):
    path = []
    count = 1
    RUNNING_OPS = {vm.suspend:'SUSPEND', vm.reboot:'REBOOT', vm.stop:'STOP', vm.destroy:'DESTROY'}
    #STOPPED_OPS = {vm.reinit:'REINIT', vm.start:'START', vm.destroy:'DESTROY'}
    STOPPED_OPS = {vm.start:'START', vm.destroy:'DESTROY'}
    SUSPENDED_OPS = {vm.resume:'RESUME', vm.destroy:'DESTROY'}
    DESTROYED_OPS = {vm.recover:'RECOVER', vm.expunge:'EXPUNGED'}
    while vm.state!=EXPUNGED:
        if vm.state == RUNNING:
            op = random.choice(RUNNING_OPS.keys())
            op()
            path.append("{}.{}".format(str(count), RUNNING_OPS[op]))
            count += 1
            continue
        elif vm.state == STOPPED:
            op = random.choice(STOPPED_OPS.keys())
            op()
            path.append("{}.{}".format(str(count), STOPPED_OPS[op]))
            count += 1
            continue
        elif vm.state == PAUSED:
            op = random.choice(SUSPENDED_OPS.keys())
            op()
            path.append("{}.{}".format(str(count), SUSPENDED_OPS[op]))
            count += 1
            continue
        elif vm.state == DESTROYED:
            op = random.choice(DESTROYED_OPS.keys())
            op()
            path.append("{}.{}".format(str(count), DESTROYED_OPS[op]))
            count += 1
            continue  
        else:
            return '\n'.join(path)
    return '\n'.join(path)

def test():
    global vm
    vm_creation_option = test_util.VmOption()
    image_name = os.environ.get('imageName_s')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    l3_name = os.environ.get('l3VlanNetworkName1')

    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    vm_creation_option.set_l3_uuids([l3_net_uuid])
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_name('Mini_basic_vm')

    for i in range(1, 10):
        vm_creation_option.set_cpu_num(random.choice(VM_CPU))
        vm_creation_option.set_memory_size(random.choice(VM_MEM))
        vm = test_vm_header.ZstackTestVm()
        vm.set_creation_option(vm_creation_option)
        vm.create()
        vm.check()
	test_util.test_logger('===path%s===\n%s' % (i, random_operations(vm)))
        #vm.expunge()
        time.sleep(5)
    test_util.test_pass('Mini VM Life Cycle Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    if vm:
        try:
            vm.destroy()
        except:
            pass
