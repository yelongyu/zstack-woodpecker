'''
New Integration Test for KVM VR&VM none network disconnect and connected again, check vm stop, VR start again.
In addition, this test is sepcific for smp and local.
@author: SyZhao
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import zstackwoodpecker.header.vm as vm_header
import zstackwoodpecker.operations.ha_operations as ha_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import apibinding.inventory as inventory
import time
import os

vm = None
host_uuid = None
host_ip = None
max_attempts = None
storagechecker_timeout = None
test_stub = test_lib.lib_get_test_stub()

def test():
    global vm
    global host_uuid
    global host_ip
    global max_attempts
    global storagechecker_timeout

    must_ps_list = [inventory.LOCAL_STORAGE_TYPE, 'SharedMountPoint']
    test_lib.skip_test_if_any_ps_not_deployed(must_ps_list)

    if test_lib.lib_get_ha_enable() != 'true':
        test_util.test_skip("vm ha not enabled. Skip test")

    vm_creation_option = test_util.VmOption()
    image_name = os.environ.get('imageName_net')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    l3_name = os.environ.get('l3VlanNetworkName1')
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    test_lib.clean_up_all_vr()
    #vrs = test_lib.lib_find_vr_by_l3_uuid(l3_net_uuid)
    #vr_host_ips = []
    #for vr in vrs:
    #    vr_host_ips.append(test_lib.lib_find_host_by_vr(vr).managementIp)
    #    if test_lib.lib_is_vm_running(vr) != True:
    #        vm_ops.start_vm(vr.uuid)
    #time.sleep(60)

    mn_ip = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].hostName
    conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
    instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid
    conditions = res_ops.gen_query_conditions('state', '=', 'Enabled')
    conditions = res_ops.gen_query_conditions('status', '=', 'Connected', conditions)
    conditions = res_ops.gen_query_conditions('managementIp', '!=', mn_ip, conditions)
    #for vr_host_ip in vr_host_ips:
    #    conditions = res_ops.gen_query_conditions('managementIp', '!=', vr_host_ip, conditions)
    host_uuid = res_ops.query_resource(res_ops.HOST, conditions)[0].uuid
    vm_creation_option.set_host_uuid(host_uuid)
    vm_creation_option.set_l3_uuids([l3_net_uuid])
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_name('ls_vm_none_status')
    vm = test_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()

    vr_hosts = test_stub.get_host_has_vr()
    mn_hosts = test_stub.get_host_has_mn()
    nfs_hosts = test_stub.get_host_has_nfs()
    if not test_stub.ensure_vm_not_on(vm.get_vm().uuid, vm.get_vm().hostUuid, vr_hosts+mn_hosts+nfs_hosts):
        test_util.test_fail("Not find out a suitable host")
    host_uuid = test_lib.lib_find_host_by_vm(vm.get_vm()).uuid
    test_stub.ensure_all_vrs_on_host(host_uuid)
    #vrs = test_lib.lib_find_vr_by_l3_uuid(l3_net_uuid)
    #target_host_uuid = test_lib.lib_find_host_by_vm(vm.get_vm()).uuid
    #for vr in vrs:
    #    if test_lib.lib_find_host_by_vr(vr).managementIp != test_lib.lib_find_host_by_vm(vm.get_vm()).managementIp:
    #        vm_ops.migrate_vm(vr.uuid, target_host_uuid)

    #vm.check()
    host_ip = test_lib.lib_find_host_by_vm(vm.get_vm()).managementIp
    test_util.test_logger("host %s is disconnecting" %(host_ip))

    test_stub.down_host_network(host_ip, test_lib.all_scenario_config)

    cond = res_ops.gen_query_conditions('name', '=', 'ls_vm_none_status')
    cond = res_ops.gen_query_conditions('uuid', '=', vm.vm.uuid, cond)

    for i in range(0, 240):
        vm_stop_time = i
        if res_ops.query_resource(res_ops.VM_INSTANCE, cond)[0].state == "Unknown":
            test_stub.up_host_network(host_ip, test_lib.all_scenario_config)
            time.sleep(1)
            test_stub.recover_smp_nfs_server(host_ip)
            conditions = res_ops.gen_query_conditions('managementIp', '=', host_ip)
            kvm_host_uuid = res_ops.query_resource(res_ops.HOST, conditions)[0].uuid
            host_ops.reconnect_host(kvm_host_uuid)
            break
        time.sleep(1)

    if vm_stop_time is None:
        vm_stop_time = 240

    for i in range(vm_stop_time, 240):
        if res_ops.query_resource(res_ops.VM_INSTANCE, cond)[0].state == "Running":
            break
        time.sleep(1)
    else:
        test_util.test_fail("vm has not been changed to running as expected within 240s.")

    vm.destroy()

    test_util.test_pass('Test VM none change to Stopped within 240s Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm

    if vm:
        try:
            vm.destroy()
        except:
            pass


def env_recover():
    global host_ip
    try:
        test_stub.up_host_network(host_ip, test_lib.all_scenario_config)
        time.sleep(1)
        test_stub.recover_smp_nfs_server(host_ip)
    except:
        pass
    conditions = res_ops.gen_query_conditions('managementIp', '=', host_ip)
    kvm_host_uuid = res_ops.query_resource(res_ops.HOST, conditions)[0].uuid
    host_ops.reconnect_host(kvm_host_uuid)
