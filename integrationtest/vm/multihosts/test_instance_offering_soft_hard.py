import os
import time

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.primarystorage_operations as ps_ops
import zstackwoodpecker.zstack_test.zstack_test_image as zstack_image_header
import apibinding.inventory as inventory
import zstackwoodpecker.operations.tag_operations as tag_ops

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    # create_instanceoffering_min_cpu with tag_soft
    instance_offering_option = test_util.InstanceOfferingOption()
    instance_offering_option.set_cpuNum(1)
    instance_offering_option.set_memorySize(1*1024*1024*1024)
    instance_offering_option.set_allocatorStrategy("MinimumCPUUsageHostAllocatorStrategy")
    instance_offering_option.set_type("UserVm")
    instance_offering_option.set_name('cpu')
    cpu_off = vm_ops.create_instance_offering(instance_offering_option)
    test_obj_dict.add_instance_offering(cpu_off)
    cpu_tag = tag_ops.create_system_tag(resourceType="InstanceOfferingVO",resourceUuid=cpu_off.uuid,tag="minimumCPUUsageHostAllocatorStrategyMode::soft")

    # create_instanceoffering_min_memory with tag_soft
    instance_offering_option.set_cpuNum(1)
    instance_offering_option.set_memorySize(1*1024*1024*1024)
    instance_offering_option.set_allocatorStrategy("MinimumMemoryUsageHostAllocatorStrategy")
    instance_offering_option.set_type("UserVm")
    instance_offering_option.set_name('memory')
    memory_off = vm_ops.create_instance_offering(instance_offering_option)
    test_obj_dict.add_instance_offering(cpu_off)
    memory_tag = tag_ops.create_system_tag(resourceType="InstanceOfferingVO",resourceUuid=memory_off.uuid,tag="minimumMemoryUsageHostAllocatorStrategyMode::soft")
    
    # kill prometheus
    cmd = "kill -9 `netstat -nlp | awk -F'[ /]*' '/9090/{print $(NF-2)}'`"
    mn_ip = os.environ["ZSTACK_BUILT_IN_HTTP_SERVER_IP"]
    test_lib.lib_execute_ssh_cmd(mn_ip,"root","password",cmd)
    
    condition = res_ops.gen_query_conditions('name', '=', 'ttylinux')
    img_name = res_ops.query_resource(res_ops.IMAGE,condition)[0].name
    l3_name = res_ops.query_resource(res_ops.L3_NETWORK)[0].name
    try:
        vm = test_stub.create_vm_with_instance_offering("cpu_1",img_name,l3_name,cpu_off)
        test_obj_dict.add_vm(vm)
    except Exception as e:
        test_util.test_fail(e)

    try:
        vm = test_stub.create_vm_with_instance_offering("memory_1",img_name,l3_name,memory_off)
        test_obj_dict.add_vm(vm)
    except Exception as e:
        test_util.test_fail(e)

    tag_ops.update_system_tag(cpu_tag.uuid,tag="minimumCPUUsageHostAllocatorStrategyMode::hard")
    tag_ops.update_system_tag(memory_tag.uuid,tag="minimumMemoryUsageHostAllocatorStrategyMode::hard")

    try:
	vm = test_stub.create_vm_with_instance_offering("cpu_2",img_name,l3_name,cpu_off)
        test_obj_dict.add_vm(vm)
        test_util.test_fail("hard model can not create vm")
    except Exception as e:
        test_util.test_logger(e)

    try:
        vm = test_stub.create_vm_with_instance_offering("memory_2",img_name,l3_name,memory_off)
	test_obj_dict.add_vm(vm)
        test_util.test_fail("hard model can not create vm")
    except Exception as e:
        test_util.test_logger(e)

    test_lib.lib_execute_ssh_cmd(mn_ip,"root","password","zstack-ctl restart_node",timeout=300)
    test_lib.lib_error_cleanup(test_obj_dict)
    test_util.test_pass("test instanceoffering soft->hard and create vm case pass")

def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)


