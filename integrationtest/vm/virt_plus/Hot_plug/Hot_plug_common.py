'''
@author: FangSun
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops


def create_onlinechange_vm(test_stub=None, test_obj_dict=None):
    cond = res_ops.gen_query_conditions('state', '=', 'Enabled')
    cond = res_ops.gen_query_conditions('status', '=', 'Connected', cond)
    host = res_ops.query_resource_with_num(res_ops.HOST, cond, limit=1)
    if not host:
        test_util.test_skip('No Enabled/Connected host was found, skip test.' )
        return True
    host = host[0]
    test_offering = test_lib.lib_create_instance_offering(cpuNum=1,
                                                          memorySize=1024 * 1024 * 1024, name='test_offering')
    test_obj_dict.add_instance_offering(test_offering)
    vm = test_stub.create_vm(vm_name='test_update_instance_offering', host_uuid=host.uuid,
                             instance_offering_uuid=test_offering.uuid)
    test_obj_dict.add_vm(vm)
    vm.check()
    return vm


def check_cpu_mem(vm):
    zone_uuid = vm.get_vm().zoneUuid

    available_cpu, available_memory = check_available_cpu_mem(zone_uuid)
    vm_outer_cpu, vm_outer_mem = vm.get_vm().cpuNum, vm.get_vm().memorySize
    vm_internal_cpu, vm_internal_mem = check_vm_internal_cpu_mem(vm)

    return available_cpu, available_memory, vm_outer_cpu, vm_outer_mem, vm_internal_cpu, vm_internal_mem


def check_available_cpu_mem(zone_uuid):
    available_cpu = test_lib.lib_get_cpu_memory_capacity([zone_uuid]).availableCpu
    available_memory = test_lib.lib_get_cpu_memory_capacity([zone_uuid]).availableMemory
    return available_cpu, available_memory


def check_vm_internal_cpu_mem(vm):
    managerip = test_lib.lib_find_host_by_vm(vm.get_vm()).managementIp
    vm_ip = vm.get_vm().vmNics[0].ip
    get_cpu_cmd = "cat /proc/cpuinfo| grep 'processor'| wc -l"
    get_mem_cmd = "free -m |grep Mem"
    res = test_lib.lib_ssh_vm_cmd_by_agent(managerip, vm_ip, 'root',
                'password', get_cpu_cmd)
    vm_cpu = int(res.result.strip())
    res = test_lib.lib_ssh_vm_cmd_by_agent(managerip, vm_ip, 'root',
                'password', get_mem_cmd)
    vm_mem = int(res.result.split()[1])
    return vm_cpu, vm_mem

