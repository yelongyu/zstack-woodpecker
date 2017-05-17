'''
@author: FangSun
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.vm_operations as vm_ops
import time
from multiprocessing.dummy import Pool as ThreadPool

_config_ = {
        'timeout' : 1000,
        'noparallel' : False
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
MEMchange = 126*1024*1024
AlignedMemChange = 128*1024*1024
CPUchange = 1

class VmWrapper(object):
    def __init__(self, vm):
        self.vm = vm
        self.available_cpu_before = None
        self.available_memory_before = None
        self.vm_outer_cpu_before = None
        self.vm_outer_mem_before = None
        self.vm_internal_cpu_before = None
        self.vm_internal_mem_before = None
        self.available_cpu_after = None
        self.available_memory_after = None
        self.vm_outer_cpu_after = None
        self.vm_outer_mem_after = None
        self.vm_internal_cpu_after = None
        self.vm_internal_mem_after = None

    def update_vminfo_before(self):
        (self.available_cpu_before, self.available_memory_before,
         self.vm_outer_cpu_before, self.vm_outer_mem_before,
         self.vm_internal_cpu_before, self.vm_internal_mem_before) = test_stub.check_cpu_mem(self.vm)

    def update_vminfo_after(self):
        (self.available_cpu_after, self.available_memory_after,
         self.vm_outer_cpu_after, self.vm_outer_mem_after,
         self.vm_internal_cpu_after, self.vm_internal_mem_after) = test_stub.check_cpu_mem(self.vm)


def update_cpu_mem(vm):
    vm_instance_offering = test_lib.lib_get_instance_offering_by_uuid(vm.get_vm().instanceOfferingUuid)
    vm_ops.update_vm(vm.get_vm().uuid, vm_instance_offering.cpuNum + CPUchange,
                     vm_instance_offering.memorySize + MEMchange)
    vm.update()
    test_stub.online_hotplug_cpu_memory(vm)
    vm.check()


def test():
    new_offering = test_lib.lib_create_instance_offering(cpuNum = 1,\
            cpuSpeed = 111, memorySize = 1024 * 1024 * 1024)
    test_obj_dict.add_instance_offering(new_offering)
    test_util.test_logger('Create 5 vm for testing')
    wrapped_vm_list = []
    for i in xrange(5):
        vm = test_stub.create_vm(vm_name = 'ckvmoffering-u12-64-{}'.format(i), image_name = "imageName_i_u12", instance_offering_uuid=new_offering.uuid)
        test_obj_dict.add_vm(vm)
        wrapped_vm_list.append(VmWrapper(vm))
    for wrapped_vm in wrapped_vm_list:
        wrapped_vm.vm.check()

    test_util.test_logger('Reserve cpu memory information before hot upgrade')

    for wrapped_vm in wrapped_vm_list:
        wrapped_vm.update_vminfo_before()

    test_util.test_logger('Hot plugin cpu mem in parallel')
    pool = ThreadPool()
    pool.map(update_cpu_mem, [wrapped_vm.vm for wrapped_vm in wrapped_vm_list])
    pool.close()
    pool.join()

    time.sleep(5)

    for wrapped_vm in wrapped_vm_list:
        wrapped_vm.update_vminfo_after()

    for wrapped_vm in wrapped_vm_list:
        assert wrapped_vm.vm_outer_cpu_before == wrapped_vm.vm_outer_cpu_after - 1
        assert wrapped_vm.vm_outer_mem_before == wrapped_vm.vm_outer_mem_after - AlignedMemChange
        assert wrapped_vm.vm_internal_cpu_before == wrapped_vm.vm_internal_cpu_after - 1
        assert wrapped_vm.vm_internal_mem_before == wrapped_vm.vm_internal_mem_after - AlignedMemChange/1024/1024

    assert wrapped_vm.available_cpu_before == wrapped_vm.available_cpu_after + 5
    assert wrapped_vm.available_memory_after + 5*AlignedMemChange/int(test_lib.lib_get_provision_memory_rate()) \
           in range(wrapped_vm.available_memory_before-10, wrapped_vm.available_memory_before+10)

    test_lib.lib_error_cleanup(test_obj_dict)
    test_util.test_pass('VM online change instance offering Test Pass')


def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)

