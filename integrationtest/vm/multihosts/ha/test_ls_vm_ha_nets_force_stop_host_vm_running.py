'''
New Integration Test for KVM VM ha with multiple networks, force stop host and then
check vm start at other host
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
test_host = None

def test():
    global vm
    global host_uuid
    global test_host
    global host_ip
    global max_attempts
    global storagechecker_timeout

    pss = res_ops.get_resource(res_ops.PRIMARY_STORAGE)
    if pss[0].type != "LocalStorage":
        test_util.test_skip("this test is designed to run on localstorage, skip on other ps type.")

    if test_lib.lib_get_ha_enable() != 'true':
        test_util.test_skip("vm ha not enabled. Skip test")

    vm_creation_option = test_util.VmOption()
    image_name = os.environ.get('imageName_s')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    #l3_name = os.environ.get('l3NoVlanNetworkName1')
    l3_name = os.environ.get('l3VlanNetworkName1')
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    l3_name2 = os.environ.get('l3VlanNetwork2')
    l3_net_uuid2 = test_lib.lib_get_l3_by_name(l3_name2).uuid
    vrs = test_lib.lib_find_vr_by_l3_uuid(l3_net_uuid)
    vr_host_ips = []
    for vr in vrs:
        vr_host_ips.append(test_lib.lib_find_host_by_vr(vr).managementIp)
	if test_lib.lib_is_vm_running(vr) != True:
	    vm_ops.start_vm(vr.uuid)
    time.sleep(60)

    mn_ip = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].hostName
    conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
    instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid
    conditions = res_ops.gen_query_conditions('state', '=', 'Enabled')
    conditions = res_ops.gen_query_conditions('status', '=', 'Connected', conditions)
    conditions = res_ops.gen_query_conditions('managementIp', '!=', mn_ip, conditions)
    for vr_host_ip in vr_host_ips:
        conditions = res_ops.gen_query_conditions('managementIp', '!=', vr_host_ip, conditions)
    host_uuid = res_ops.query_resource(res_ops.HOST, conditions)[0].uuid
    vm_creation_option.set_host_uuid(host_uuid)
    vm_creation_option.set_l3_uuids([l3_net_uuid, l3_net_uuid2])
    vm_creation_option.set_default_l3_uuid(l3_net_uuid)
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_name('multihost_basic_vm')
    vm = test_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()

    if not test_lib.lib_check_vm_live_migration_cap(vm.vm):
        test_util.test_skip('skip ha if live migrate not supported')

    ps = test_lib.lib_get_primary_storage_by_uuid(vm.get_vm().allVolumes[0].primaryStorageUuid)
    if ps.type == inventory.LOCAL_STORAGE_TYPE:
        test_util.test_skip('Skip test on localstorage')

    #vm.check()
    host_ip = test_lib.lib_find_host_by_vm(vm.get_vm()).managementIp
    host_port = test_lib.lib_get_host_port(host_ip)
    test_util.test_logger("host %s is disconnecting" %(host_ip))

    ha_ops.set_vm_instance_ha_level(vm.get_vm().uuid, "NeverStop")

    host_list = test_stub.get_sce_hosts(test_lib.all_scenario_config, test_lib.scenario_file)
    for host in host_list:
        if host.ip_ == host_ip:
            test_host = host
            break
    if not test_host:
        test_util.test_fail('there is no host with ip %s in scenario file.' %(host_ip))

    test_stub.stop_host(test_host, test_lib.all_scenario_config, 'cold')

    test_util.test_logger("wait for 120 seconds")
    time.sleep(120)

    test_stub.start_host(test_host, test_lib.all_scenario_config)

    #vm.update() #bug for host uuid is not updated
    cond = res_ops.gen_query_conditions('uuid', '=', vm.vm.uuid)
    vm_inv = res_ops.query_resource(res_ops.VM_INSTANCE, cond)[0]
    vm_host_ip = test_lib.lib_find_host_by_vm(vm_inv).managementIp
    for i in range(0, 60):
        test_util.test_logger("vm_host_ip:%s; host_ip:%s" %(vm_host_ip, host_ip))
        time.sleep(1)
        vm_inv = res_ops.query_resource(res_ops.VM_INSTANCE, cond)[0]
        vm_host_ip = test_lib.lib_find_host_by_vm(vm_inv).managementIp
        if vm_host_ip != host_ip:
            break
    else:
        test_util.test_fail("VM is expected to start running on another host")
        
    #vm.check() #bug when multi-networks
    if test_lib.lib_wait_target_up(vm_inv.vmNics[0].ip, '22', 120):
        test_util.test_logger("%s can be connected within 120s" %(vm_inv.vmNics[0].ip))
    elif test_lib.lib_wait_target_up(vm_inv.vmNics[1].ip, '22', 120):
        test_util.test_logger("%s can be connected within 120s" %(vm_inv.vmNics[1].ip))
    else:
        test_util.test_fail("Both %s and %s can't be connected." %(vm_inv.vmNics[0].ip, vm_inv.vmNics[1].ip))

    vm.destroy()

    test_util.test_pass('Test VM ha with multiple networks disconnect host Success')



#Will be called only if exception happens in test().
def error_cleanup():
    global vm

    if vm:
        try:
            vm.destroy()
        except:
            pass


def env_recover():
    global test_host
    try:
        test_stub.start_host(host_ip, test_lib.all_scenario_config)
    except:
        pass
