'''

VM creation with illegal parameters test for Mini

@author: zhaohao.chen
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import zstackwoodpecker.operations.image_operations as img_ops
import time
import os
import random
import itertools

vm = None

ILLEGAL_LIST = [0,-1,'~','!','@','#','$','%','^','&','*','(',')','_','+','`','-','=','\'','/','\\','.','?','<','>','x',':',';','"','[',']','{','}','|']
IELLEGAL_PARAMETER_LIST = list(itertools.combinations(ILLEGAL_LIST, 2))

def create_vm_test(vm_creation_option, vm_cpu, vm_mem , i):
    global vm
    vm_creation_option.set_cpu_num(vm_cpu)
    vm_creation_option.set_memory_size(vm_mem)
    vm_creation_option.set_name('illegal-%s%s' % (vm_cpu, vm_mem))
    vm = test_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    try:
        vm.create()
    except Exception as e:
        test_util.test_logger('round %s/%s \n%s' % (i,len(IELLEGAL_PARAMETER_LIST),e))
        return
    test_util.test_fail('Create vm with illegal parameter [vm_cpu:%s, vm_mem:%s] sucess' % (vm_cpu, vm_mem))
    
def test():
    vm_creation_option = test_util.VmOption()
    image_name = os.environ.get('imageName_s')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    l3_name = os.environ.get('l3VlanNetworkName1')
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    vm_creation_option.set_l3_uuids([l3_net_uuid])
    vm_creation_option.set_image_uuid(image_uuid)
    #create vms with illegal parameters
    i = 1
    for cpu, mem in IELLEGAL_PARAMETER_LIST:
        create_vm_test(vm_creation_option, cpu, mem, i)
        i += 1
    test_util.test_pass('VM creation with illegal parameters all failed! :)')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    if vm:
        try:
            vm.destroy()
        except:
            pass
