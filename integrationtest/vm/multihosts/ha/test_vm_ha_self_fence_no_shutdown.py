'''

New Integration Test VM ha host self fencing: host not shutdown itself if network just down for a little while.

@author: Quarkonics
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
import time
import os

vm = None
host_uuid = None
host_ip = None
max_attempts = None
storagechecker_timeout = None

def test():
    global vm
    global host_uuid
    global host_ip
    global max_attempts
    global storagechecker_timeout

    if test_lib.lib_get_ha_enable() != 'true':
        test_util.test_skip("vm ha not enabled. Skip test")

    max_attempts = test_lib.lib_get_ha_selffencer_maxattempts()
    test_lib.lib_set_ha_selffencer_maxattempts('12')
    storagechecker_timeout = test_lib.lib_get_ha_selffencer_storagechecker_timeout()
    test_lib.lib_set_ha_selffencer_storagechecker_timeout('15')

    vm_creation_option = test_util.VmOption()
    image_name = os.environ.get('imageName_s')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    #l3_name = os.environ.get('l3NoVlanNetworkName1')
    l3_name = os.environ.get('l3VlanNetworkName1')
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    vrs = test_lib.lib_find_vr_by_l3_uuid(l3_net_uuid)
    for vr in vrs:
	if test_lib.lib_is_vm_running(vr) == True:
	    vm_ops.start_vm(vr.uuid)
    time.sleep(60)

    conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
    instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid
    conditions = res_ops.gen_query_conditions('state', '=', 'Enabled')
    conditions = res_ops.gen_query_conditions('status', '=', 'Connected', conditions)
    conditions = res_ops.gen_query_conditions('managementIp', '!=', os.environ.get('hostIp'), conditions)
    host_uuid = res_ops.query_resource(res_ops.HOST, conditions)[0].uuid
    vm_creation_option.set_host_uuid(host_uuid)
    vm_creation_option.set_l3_uuids([l3_net_uuid])
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_name('multihost_basic_vm')
    vm = test_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    #vm.check()
    host_ip = test_lib.lib_find_host_by_vm(vm.get_vm()).managementIp
    host_uuid = test_lib.lib_find_host_by_vm(vm.get_vm()).uuid
    ha_ops.set_vm_instance_ha_level(vm.get_vm().uuid, "OnHostFailure")
    l2_network_interface = os.environ.get('l2ManagementNetworkInterface')

    cmd = "ifdown %s && sleep 30 && ifup %s" % (l2_network_interface, l2_network_interface)
    try:
	rsp = test_lib.lib_execute_sh_cmd_by_agent(host_ip, cmd)
	test_util.test_logger("host is not expected to shutdown after its network down just for a little while")
    except:
        test_util.test_fail("host may have been shutdown, while it's not expected to shutdown")

    cmd = "date"
    try:
	rsp = test_lib.lib_execute_sh_cmd_by_agent(host_ip, cmd)
        test_util.test_logger("host is still alive")
    except:
	test_util.test_fail("host is not expected to shutdown after its network down just for a little while")

    vm.destroy()

    test_lib.lib_set_ha_selffencer_maxattempts(max_attempts)
    test_lib.lib_set_ha_selffencer_storagechecker_timeout(storagechecker_timeout)

    time.sleep(60)
    test_util.test_pass('Test Host Self fence Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    global host_ip
    global host_uuid
    global max_attempts
    global storagechecker_timeout

    if vm:
        try:
            vm.destroy()
        except:
            pass

    test_lib.lib_set_ha_selffencer_maxattempts(max_attempts)
    test_lib.lib_set_ha_selffencer_storagechecker_timeout(storagechecker_timeout)
