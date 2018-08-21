'''
Test chassis operation

@author Glody
'''
import zstackwoodpecker.operations.baremetal_operations as baremetal_operations
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as zstack_vm_header
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import test_stub
import os

vm = None

def test():
    global vm
    mn_ip = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].hostName
    cond = res_ops.gen_query_conditions('managementIp', '=', mn_ip) 
    host = res_ops.query_resource(res_ops.HOST, cond)[0]
    host_uuid = host.uuid
    cond = res_ops.gen_query_conditions('hypervisorType', '=', 'KVM')
    cluster_uuid = res_ops.query_resource(res_ops.CLUSTER, cond)[0].uuid
    vm = test_stub.create_vm(host_uuid = host_uuid, cluster_uuid = cluster_uuid)

    cond = res_ops.gen_query_conditions('hypervisorType', '=', 'baremetal')
    baremetal_cluster_uuid = res_ops.query_resource(res_ops.CLUSTER, cond)[0].uuid
    test_stub.create_vbmc(vm, host.managementIp, 623)
    chassis = test_stub.create_chassis(baremetal_cluster_uuid)
    test_stub.hack_ks(mn_ip)
    chassis_uuid = chassis.uuid 
    baremetal_operations.inspect_chassis(chassis_uuid)
    #hwinfo = test_stub.check_hwinfo(chassis_uuid)
    #if not hwinfo:
    #    test_util.test_fail('Fail to get hardware info during the first provision')
    #test_stub.delete_vbmc(vm, host.managementIp)
    #baremetal_operations.delete_chassis(chassis_uuid)
    #vm.destroy()
    test_util.test_pass('Create chassis Test Success')

def error_cleanup():
    global vm
    if vm:
        test_stub.delete_vbmc(vm = vm)
        chassis = os.environ.get('ipminame')
        chassis_uuid = test_lib.lib_get_chassis_by_name(chassis).uuid
        baremetal_operations.delete_chassis(chassis_uuid)
        vm.destroy()
