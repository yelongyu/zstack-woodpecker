'''
@author: FangSun
'''

import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import os
import random
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.vm_operations as vm_ops
import time


_config_ = {
        'timeout': 1000,
        'noparallel': True
        }


test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()



case_flavor = dict(c6_cpu=            dict(image='imageName_i_c6', add_cpu=True, add_memory=False, need_online=False),
                   c7_cpu=            dict(image='imageName_i_c7', add_cpu=True, add_memory=False, need_online=False),
                   u12_cpu=           dict(image='imageName_i_u12', add_cpu=True, add_memory=False, need_online=True),
                   u13_cpu=           dict(image='imageName_i_u13', add_cpu=True, add_memory=False, need_online=True),
                   u14_cpu=           dict(image='imageName_i_u14', add_cpu=True, add_memory=False, need_online=True),
                   u15_cpu=           dict(image='imageName_i_u15', add_cpu=True, add_memory=False, need_online=True),
                   u16_cpu=           dict(image='imageName_i_u16', add_cpu=True, add_memory=False, need_online=True),
                   c6_mem=            dict(image='imageName_i_c6', add_cpu=False, add_memory=True, need_online=False),
                   c7_mem=            dict(image='imageName_i_c7', add_cpu=False, add_memory=True, need_online=True),
                   u12_mem=           dict(image='imageName_i_u12', add_cpu=False, add_memory=True, need_online=True),
                   u16_mem=           dict(image='imageName_i_u16', add_cpu=False, add_memory=True, need_online=True),
                   c6_cpu_mem=        dict(image='imageName_i_c6', add_cpu=True, add_memory=True, need_online=False),
                   c7_cpu_mem=        dict(image='imageName_i_c7', add_cpu=True, add_memory=True, need_online=True),
                   u12_cpu_mem=       dict(image='imageName_i_u12', add_cpu=True, add_memory=True, need_online=True),
                   u13_cpu_mem=       dict(image='imageName_i_u13', add_cpu=True, add_memory=True, need_online=True),
                   u14_cpu_mem=       dict(image='imageName_i_u14', add_cpu=True, add_memory=True, need_online=True),
                   u15_cpu_mem=       dict(image='imageName_i_u15', add_cpu=True, add_memory=True, need_online=True),
                   u16_cpu_mem=       dict(image='imageName_i_u16', add_cpu=True, add_memory=True, need_online=True),
                   )




def test():
    flavor = case_flavor[os.environ.get('CASE_FLAVOR')]
    test_util.test_dsc("STEP1: Ceate vm instance offering")
    vm_instance_offering = test_lib.lib_create_instance_offering(cpuNum=1, memorySize=1024*1024*1024)
    test_obj_dict.add_instance_offering(vm_instance_offering)

    test_util.test_dsc("STEP2: Ceate vm and wait until it up for testing image_name : {}".format(flavor['image']))
    vm = test_stub.create_vm(vm_name='test_vm', image_name=flavor['image'],
                             instance_offering_uuid=vm_instance_offering.uuid)
    test_obj_dict.add_vm(vm)
    vm.check()

    cpu_change = random.randint(1, 5) if flavor['add_cpu'] else 0
    mem_change = random.randint(1, 500)*1024*1024 if flavor['add_memory'] else 0

    test_util.test_dsc("STEP3: Hot Plugin CPU: {} and Memory: {} and check capacity".format(cpu_change, mem_change))

    with test_stub.CapacityCheckerContext(vm, cpu_change, mem_change):
        vm_ops.update_vm(vm.get_vm().uuid, vm_instance_offering.cpuNum+cpu_change,
                         vm_instance_offering.memorySize+mem_change)
        vm.update()
        if flavor['need_online']:
            test_stub.online_hotplug_cpu_memory(vm)
        time.sleep(10)

    test_util.test_dsc("STEP4: Destroy test object")
    test_lib.lib_error_cleanup(test_obj_dict)
    test_util.test_pass('VM online change instance offering Test Pass')


def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
