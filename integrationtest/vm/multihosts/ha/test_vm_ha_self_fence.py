'''

New Integration Test for creating KVM VM.

@author: Quarkonics
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import zstackwoodpecker.header.vm as vm_header
import zstackwoodpecker.operations.ha_operations as ha_ops
import time
import os

vm = None

def test():
    global vm
    vm_creation_option = test_util.VmOption()
    image_name = os.environ.get('imageName_s')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    #l3_name = os.environ.get('l3NoVlanNetworkName1')
    l3_name = os.environ.get('l3VlanNetworkName1')

    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
    instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid
    host_ip = os.environ.get('hostIp2')
    conditions = res_ops.gen_query_conditions('managementIp', '=', host_ip)
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
    ha_ops.set_vm_instance_ha_level(vm.get_vm().uuid, "OnHostFailure")
    l2_network_interface = os.environ.get('l2ManagementNetworkInterface')
    cmd = "ifdown %s && sleep 120 && ifup %s" % (l2_network_interface, l2_network_interface)
    try:
        rsp = test_lib.lib_execute_sh_cmd_by_agent(host_ip, cmd)
	test_util.test_fail("host is expected to shutdown after its network down for a while")
    except:
        test_util.test_logger("host may have been shutdown")
    cmd = "date"
    try:
        rsp = test_lib.lib_execute_sh_cmd_by_agent(host_ip, cmd)
	test_util.test_fail("host is expected to shutdown after its network down for a while")
    except:
        test_util.test_logger("host have been shutdown")

    vm.destroy()

    test_util.test_pass('Test Host Self fence Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    if vm:
        try:
            vm.destroy()
        except:
            pass
