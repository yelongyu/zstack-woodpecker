'''

Integration Test for display network switch 

@author: SyZhao
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.node_operations as node_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.tag_operations as tag_ops
import test_stub
import time
import os

vm = None
tag_uuid = None

def test():
    global vm
    global tag_uuid

    test_stub.skip_if_scenario_not_multiple_networks()

    vm = test_stub.create_basic_vm()
    vm.check()

    console = test_lib.lib_get_vm_console_address(vm.get_vm().uuid)
    console_management_ip = console.hostIp 

    cluster = res_ops.get_resource(res_ops.CLUSTER)[0]
    tag_inv = tag_ops.create_system_tag('ClusterVO', vm.get_vm().uuid, "display::network::cidr::172.20.0.0/16")
    tag_uuid = tag_inv.uuid

    console = test_lib.lib_get_vm_console_address(vm.get_vm().uuid)
    console_display_ip = console.hostIp 
    
    if console_management_ip == console_display_ip:
        test_util.test_fail("console ip has not been switched as expected: %s and %s" %(console_management_ip, console_display_ip))

    test_util.test_pass('Create VM Test Success')

#Will be called what ever test result is
def env_recover():
    global tag_uuid
    try:
        if tag_uuid:
            tag_ops.delete_tag(tag_uuid)
    except:
        pass
    

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    if vm:
        try:
            vm.destroy()
        except:
            pass
