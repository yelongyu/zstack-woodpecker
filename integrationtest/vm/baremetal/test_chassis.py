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
    instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING)[0].uuid
    cond = res_ops.gen_query_conditions('name', '=', 'medium-image')
    image_uuid = res_ops.query_resource(res_ops.IMAGE, cond)[0].uuid
    cond = res_ops.gen_query_conditions('hypervisorType', '=', 'KVM')
    cluster_uuid = res_ops.query_resource(res_ops.CLUSTER, cond)[0].uuid
    cond = res_ops.gen_query_conditions('name', '=', 'public network')
    l3_uuid = res_ops.query_resource(res_ops.L3_NETWORK, cond)[0].uuid
    vm_creation_option = test_util.VmOption()
    vm_creation_option.set_name('vm_for_baremetal')
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_cluster_uuid(cluster_uuid)
    vm_creation_option.set_l3_uuids([l3_uuid])
    vm_creation_option.set_host_uuid(host_uuid)
    vm = zstack_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()

    cond = res_ops.gen_query_conditions('hypervisorType', '=', 'baremetal')
    baremetal_cluster_uuid = res_ops.query_resource(res_ops.CLUSTER, cond)[0].uuid
    test_stub.create_vbmc(vm, host.managementIp, 6230)
    # Create Chassis
    chassis_option = test_util.ChassisOption()
    chassis_option.set_name(os.environ.get('ipminame'))
    chassis_option.set_ipmi_address('127.0.0.1')
    chassis_option.set_ipmi_username(os.environ.get('ipmiusername'))
    chassis_option.set_ipmi_password(os.environ.get('ipmipassword'))
    chassis_option.set_ipmi_port('6230')
    chassis_option.set_cluster_uuid(baremetal_cluster_uuid)
    chassis = baremetal_operations.create_chassis(chassis_option)

    #test_stub.hack_ks(port = 6230)
    chassis_uuid = chassis.uuid 
    # First time Provision
    baremetal_operations.inspect_chassis(chassis_uuid)
    #hwinfo = test_stub.check_hwinfo(chassis_uuid)
    #if not hwinfo:
    #    test_util.test_fail('Fail to get hardware info during the first provision')
    test_stub.delete_vbmc(vm, host.managementIp)
    baremetal_operations.delete_chassis(chassis_uuid)
    vm.destroy()
    test_util.test_pass('Create chassis Test Success')

def error_cleanup():
    global vm
    if vm:
        test_stub.delete_vbmc(vm = vm)
        chassis = os.environ.get('ipminame')
        chassis_uuid = test_lib.lib_get_chassis_by_name(chassis).uuid
        baremetal_operations.delete_chassis(chassis_uuid)
        vm.destroy()
