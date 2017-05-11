'''
@author: FangSun
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import os

def create_onlinechange_vm(test_stub=None, test_obj_dict=None):
    cond = res_ops.gen_query_conditions('state', '=', 'Enabled')
    cond = res_ops.gen_query_conditions('status', '=', 'Connected', cond)
    host = res_ops.query_resource_with_num(res_ops.HOST, cond, limit=1)
    if not host:
        test_util.test_skip('No Enabled/Connected host was found, skip test.' )
        return True
    host = host[0]
    test_offering = test_lib.lib_create_instance_offering(cpuNum=1, cpuSpeed=16,
                                                          memorySize=1024 * 1024 * 1024, name='test_offering')

    l3_name = os.environ.get('l3VlanNetworkName1')
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    l3_net_list = [l3_net_uuid]
    test_obj_dict.add_instance_offering(test_offering)
    vm = test_stub.create_vm(vm_name='test_update_instance_offering', host_uuid=host.uuid,
                             instance_offering_uuid=test_offering.uuid,
                             l3_name=l3_net_list)
    test_obj_dict.add_vm(vm)
    vm.check()
    return vm


def check_cpu_mem(vm):
    zone_uuid = vm.get_vm().zoneUuid

    total_cpu_used, total_mem_used = check_total_cpu_mem(zone_uuid)
    vm_outer_cpu, vm_outer_mem = vm.get_vm().cpuNum, vm.get_vm().memorySize
    vm_internal_cpu, vm_internal_mem = check_vm_internal_cpu_mem(vm)

    return total_cpu_used, total_mem_used, vm_outer_cpu, vm_outer_mem, vm_internal_cpu, vm_internal_mem


def check_total_cpu_mem(zone_uuid):
    total_cpu_used = test_lib.lib_get_cpu_memory_capacity([zone_uuid]).totalCpu
    total_mem_used = test_lib.lib_get_cpu_memory_capacity([zone_uuid]).totalMemory
    return total_cpu_used, total_mem_used


def check_vm_internal_cpu_mem(vm):
    out = test_lib.lib_execute_command_in_vm(vm.get_vm(), "cat /proc/cpuinfo| grep 'processor'| wc -l")
    vm_cpu = int(out.strip())
    out = test_lib.lib_execute_command_in_vm(vm.get_vm(), "free -m |grep Mem")
    vm_mem = int(out.split(" ")[1])
    return vm_cpu, vm_mem
