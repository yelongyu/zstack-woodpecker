'''

VM prometheus data test for Mini

@author: Zhaohao
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.zwatch_operations as zw_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import time
import os
import random

vm = None

VM_CPU = [1, 2, 3, 4, 7, 8, 15, 16, 20, 32]

# 128M, 256M, 512M, 1G, 2G
VM_MEM = [134217728, 268435456, 536870912, 1073741824, 2147483648]

PRO_LIST=["CPUAllUsedUtilization",
          "DiskAllReadBytes",
          "DiskAllWriteBytes",
          "NetworkAllInBytes",
          "NetworkAllOutBytes",
          "MemoryUsedInPercent"]

def prometheus_test(vm_uuid):
    result_dict = {"VM":vm_uuid, "result":{}}
    for item in PRO_LIST:
        result_dict["result"][item] = False
        data_list = zw_ops.get_metric_data("ZStack/VM", item)
        for data in data_list:
            if vm_uuid == data["labels"]["VMUuid"]:
                result_dict["result"][item] = True
                break
    if False in result_dict["result"].values():
        test_util.test_fail("Mini vm %s prometheus check FAIL\n%s" % (vm_uuid, result_dict))
        return
    else:
        test_util.test_logger("Mini vm %s prometheus check PASS\n%s" % (vm_uuid, result_dict))
        return

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
        vm_uuid = vm.get_vm()['uuid']
        vm.check()
        time.sleep(30)
        prometheus_test(vm_uuid)
        vm.destroy()
        vm.expunge()
        time.sleep(30)

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    if vm:
        try:
            vm.destroy()
        except:
            pass
