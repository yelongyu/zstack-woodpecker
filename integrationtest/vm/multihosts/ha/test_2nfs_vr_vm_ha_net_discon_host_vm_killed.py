'''
New Integration Test for KVM VM ha network disconnect and check vm has been killed on original host
In addition, this test is sepcific for 2nfs.
@author: turnyouon
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

    must_ps_list = [inventory.NFS_PRIMARY_STORAGE_TYPE]
    test_lib.skip_test_if_any_ps_not_deployed(must_ps_list)

    if test_lib.lib_get_ha_enable() != 'true':
        test_util.test_skip("vm ha not enabled. Skip test")

    vm_creation_option = test_util.VmOption()
    image_name = os.environ.get('imageName_net')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    #l3_name = os.environ.get('l3NoVlanNetworkName1')
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
    vm_creation_option.set_name('multihost_basic_vm')
    vm = test_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()

    vm_creation_option.set_name('multihost_basic_vm2')
    vm2 = test_vm_header.ZstackTestVm()
    vm2.set_creation_option(vm_creation_option)
    vm2.create()

    vm_creation_option.set_name('multihost_basic_vm3')
    vm3 = test_vm_header.ZstackTestVm()
    vm3.set_creation_option(vm_creation_option)
    vm3.create()

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
    host_port = test_lib.lib_get_host_port(host_ip)
    test_util.test_logger("host %s is disconnecting" %(host_ip))

    ha_ops.set_vm_instance_ha_level(vm.get_vm().uuid, "NeverStop")
    ha_ops.set_vm_instance_ha_level(vm2.get_vm().uuid, "NeverStop")
    ha_ops.set_vm_instance_ha_level(vm3.get_vm().uuid, "NeverStop")

    test_stub.down_host_network(host_ip, test_lib.all_scenario_config)

    #Here we wait for 180 seconds for all vms have been killed, but test result show:
    #no need to wait, the reaction of killing the vm is very quickly.
    test_util.test_logger("wait for 30 seconds")
    time.sleep(30)

    if test_stub.check_vm_running_on_host(vm.vm.uuid, host_ip):
	test_util.test_fail("VM1 is expected to start running on another host")
    if test_stub.check_vm_running_on_host(vm2.vm.uuid, host_ip):
	test_util.test_fail("VM2 is expected to start running on another host")
    if test_stub.check_vm_running_on_host(vm3.vm.uuid, host_ip):
	test_util.test_fail("VM3 is expected to start running on another host")

    test_stub.up_host_network(host_ip, test_lib.all_scenario_config)
    conditions = res_ops.gen_query_conditions('managementIp', '=', host_ip)
    kvm_host_uuid = res_ops.query_resource(res_ops.HOST, conditions)[0].uuid
    host_ops.reconnect_host(kvm_host_uuid)

    vm.set_state(vm_header.RUNNING)
    vm2.set_state(vm_header.RUNNING)
    vm3.set_state(vm_header.RUNNING)
    time.sleep(60)
    vm.check()
    vm2.check()
    vm3.check()
    vm.destroy()
    vm2.destroy()
    vm3.destroy()

    test_util.test_pass('Test VM ha on host failure Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    global host_uuid
    global host_ip
    global max_attempts
    global storagechecker_timeout

    if vm:
        try:
            vm.destroy()
        except:
            pass


def env_recover():
    global host_ip
    test_util.test_logger("recover host: %s" % (host_ip))

    try:
        test_stub.up_host_network(host_ip, test_lib.all_scenario_config)
    except:
        pass

    conditions = res_ops.gen_query_conditions('managementIp', '=', host_ip)
    kvm_host_uuid = res_ops.query_resource(res_ops.HOST, conditions)[0].uuid
    host_ops.reconnect_host(kvm_host_uuid)
