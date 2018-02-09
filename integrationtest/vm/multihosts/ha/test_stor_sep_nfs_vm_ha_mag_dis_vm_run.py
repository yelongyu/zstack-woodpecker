'''
@Integration Test
@Scenario: management network and storage network separation for NFS
           Disconnect storage network and check vm ha start on other
           host
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
max_time = 300
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

    allow_ps_list = [inventory.NFS_PRIMARY_STORAGE_TYPE]
    test_lib.skip_test_when_ps_type_not_in_list(allow_ps_list)
    
    test_stub.skip_if_not_storage_network_separate(test_lib.all_scenario_config)

    if test_lib.lib_get_ha_enable() != 'true':
        test_util.test_skip("vm ha not enabled. Skip test")

    vm_creation_option = test_util.VmOption()
    image_name = os.environ.get('imageName_net')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    l3_name = os.environ.get('l3VlanNetworkName1')
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    test_lib.clean_up_all_vr()

    mn_ip = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].hostName
    conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
    instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid
    conditions = res_ops.gen_query_conditions('state', '=', 'Enabled')
    conditions = res_ops.gen_query_conditions('status', '=', 'Connected', conditions)
    conditions = res_ops.gen_query_conditions('managementIp', '!=', mn_ip, conditions)
    host_uuid = res_ops.query_resource(res_ops.HOST, conditions)[0].uuid
    vm_creation_option.set_host_uuid(host_uuid)
    vm_creation_option.set_l3_uuids([l3_net_uuid])
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_name('multihost_basic_vm')
    vm = test_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()

    vr_hosts = test_stub.get_host_has_vr()
    mn_hosts = test_stub.get_host_has_mn()
    nfs_hosts = test_stub.get_host_has_nfs()
    #test_stub.test_skip('debug')
    if not test_stub.ensure_vm_not_on(vm.get_vm().uuid, vm.get_vm().hostUuid, vr_hosts+mn_hosts+nfs_hosts):
        test_util.test_fail("Not find out a suitable host")

    #vm.check()
    host_ip = test_lib.lib_find_host_by_vm(vm.get_vm()).managementIp
    test_util.test_logger("host %s is disconnecting" %(host_ip))

    ha_ops.set_vm_instance_ha_level(vm.get_vm().uuid, "NeverStop")

    #test_stub.down_host_network(host_ip, test_lib.all_scenario_config)
    host_username = os.environ.get('hostUsername')
    host_password = os.environ.get('hostPassword')
    t = test_stub.async_exec_ifconfig_nic_down_up(120, host_ip, host_username, host_password, "br_zsn0")

    vm_stop_time = None
    cond = res_ops.gen_query_conditions('uuid', '=', vm.vm.uuid)
    for i in range(0, max_time):
        vm_stop_time = i
        if res_ops.query_resource(res_ops.VM_INSTANCE, cond)[0].state == "Unknown":
            break
        time.sleep(1)

    if vm_stop_time is None:
        vm_stop_time = max_time
        
    for i in range(vm_stop_time, max_time):
        if res_ops.query_resource(res_ops.VM_INSTANCE, cond)[0].state == "Running":
            break
        time.sleep(1)
    else:
        test_util.test_fail("vm has not been changed to running as expected within %s s." %(max_time))

    vm.destroy()
    t.join()

    test_util.test_pass('Test VM ha change to running within 300s Success')

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
    pass
    #cmd = 'bash -ex %s %s' % (os.environ.get('hostRecoverScript'), host_ip)
    #test_util.test_logger(cmd)
    #os.system(cmd)
    conditions = res_ops.gen_query_conditions('managementIp', '=', host_ip)
    kvm_host_uuid = res_ops.query_resource(res_ops.HOST, conditions)[0].uuid
    host_ops.reconnect_host(kvm_host_uuid)
