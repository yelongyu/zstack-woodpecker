'''
New Integration Test for KVM VM ha with multiple networks, disconnect host network and then
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
max_time = 360
storagechecker_timeout = None
test_stub = test_lib.lib_get_test_stub()

def test():
    global vm
    global host_uuid
    global host_ip
    global max_attempts
    global storagechecker_timeout

    allow_ps_list = [inventory.CEPH_PRIMARY_STORAGE_TYPE, inventory.NFS_PRIMARY_STORAGE_TYPE, 'SharedMountPoint']
    test_lib.skip_test_when_ps_type_not_in_list(allow_ps_list)

    if test_lib.lib_get_ha_enable() != 'true':
        test_util.test_skip("vm ha not enabled. Skip test")

    vm_creation_option = test_util.VmOption()
    image_name = os.environ.get('imageName_net')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    #l3_name = os.environ.get('l3NoVlanNetworkName1')
    l3_name = os.environ.get('l3VlanNetworkName1')
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    l3_name2 = os.environ.get('l3VlanNetwork2')
    l3_net_uuid2 = test_lib.lib_get_l3_by_name(l3_name2).uuid
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
    vm_creation_option.set_l3_uuids([l3_net_uuid, l3_net_uuid2])
    vm_creation_option.set_default_l3_uuid(l3_net_uuid)
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_name('multihost_basic_vm')
    vm = test_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()

    test_stub.ensure_host_has_no_vr(host_uuid)

    #vm.check()
    host_ip = test_lib.lib_find_host_by_vm(vm.get_vm()).managementIp
    host_port = test_lib.lib_get_host_port(host_ip)
    test_util.test_logger("host %s is disconnecting" %(host_ip))

    ha_ops.set_vm_instance_ha_level(vm.get_vm().uuid, "NeverStop")

    test_stub.down_host_network(host_ip, test_lib.all_scenario_config)

    test_util.test_logger("wait for 240 seconds")
    time.sleep(240)

    test_stub.up_host_network(host_ip, test_lib.all_scenario_config)
    
    #vm.update() #bug for host uuid is not updated
    cond = res_ops.gen_query_conditions('uuid', '=', vm.vm.uuid)
    vm_inv = res_ops.query_resource(res_ops.VM_INSTANCE, cond)[0]
    vm_host_ip = test_lib.lib_find_host_by_vm(vm_inv).managementIp
    for i in range(0, max_time):
        test_util.test_logger("vm_host_ip:%s; host_ip:%s" %(vm_host_ip, host_ip))
        time.sleep(1)
        vm_inv = res_ops.query_resource(res_ops.VM_INSTANCE, cond)[0]
        vm_host_ip = test_lib.lib_find_host_by_vm(vm_inv).managementIp
        if vm_host_ip != host_ip:
            break
    else:
        test_util.test_fail("VM is expected to start running on another host")

    test_lib.lib_set_vm_host_l2_ip(vm_inv)
        
    #vm.check() #bug when multi-networks
    #if test_lib.lib_wait_target_up(vm_inv.vmNics[0].ip, '22', 120):
    #    test_util.test_logger("%s can be connected within 120s" %(vm_inv.vmNics[0].ip))
    #elif test_lib.lib_wait_target_up(vm_inv.vmNics[1].ip, '22', 120):
    #    test_util.test_logger("%s can be connected within 120s" %(vm_inv.vmNics[1].ip))
    #else:
    #    test_util.test_fail("Both %s and %s can't be connected." %(vm_inv.vmNics[0].ip, vm_inv.vmNics[1].ip))
    ssh_timeout = test_lib.SSH_TIMEOUT
    test_lib.SSH_TIMEOUT = 120
    if not test_lib.lib_ssh_vm_cmd_by_agent_with_retry(vm_host_ip, vm_inv.vmNics[0].ip, 'root', 'password', "pwd"):
        test_lib.SSH_TIMEOUT = ssh_timeout
        test_util.test_fail("vm can't be access by %s." %(vm_inv.vmNics[0].ip))

    if not test_lib.lib_ssh_vm_cmd_by_agent_with_retry(vm_host_ip, vm_inv.vmNics[1].ip, 'root', 'password', "pwd"):
        test_lib.SSH_TIMEOUT = ssh_timeout
        test_util.test_fail("vm can't be access by %s." %(vm_inv.vmNics[1].ip))

    test_lib.SSH_TIMEOUT = ssh_timeout

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
    try:
        test_stub.up_host_network(host_ip, test_lib.all_scenario_config)
    except:
        pass
