'''
@author: chenyuan.xu
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.operations.ha_operations as ha_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import time
import random


test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()


def test():

    test_util.test_dsc("create vpc vrouter")

    vr = test_stub.create_vpc_vrouter()

    test_util.test_dsc("attach vpc l3 to vpc vrouter")
    test_stub.attach_l3_to_vpc_vr(vr, test_stub.L3_SYSTEM_NAME_LIST)

    test_util.test_dsc("Create one neverstop vm in random L3")
    vm = test_stub.create_vm_with_random_offering(vm_name='vpc_vm1', l3_name=random.choice(test_stub.L3_SYSTEM_NAME_LIST))
    test_obj_dict.add_vm(vm)
    vm.check()

    host_list = res_ops.query_resource(res_ops.HOST, [], None)
    for host in host_list:
        host_ops.change_host_state(host.uuid, "maintain")
    
    time.sleep(30)
    assert vr.state == 'Stopped'
    assert vm.state == 'Stopped'
 
    for host in host_list:
        host_ops.change_host_state(host.uuid, "enable")

    test_stub.ensure_hosts_connected()
    test_stub.ensure_pss_connected()

    vm.start()
    assert vr.state == 'Running'

    ha_ops.set_vm_instance_ha_level(vm.get_vm().uuid, "NeverStop")
    for host in host_list:
        host_ops.change_host_state(host.uuid, "maintain")
    assert vr.state == 'Stopped'
    assert vm.state == 'Stopped'

    for host in host_list:
        host_ops.change_host_state(host.uuid, "enable")

    test_stub.ensure_hosts_connected()
    test_stub.ensure_pss_connected()
    
    test_lib.lib_wait_target_up(vm.vmNics[0].ip, '22', 120)
    assert vr.state == 'Running'
    
    
    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_vrouter()


def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_vrouter()
    for host in host_list:
        if host.state == 'maintain'
            host_ops.change_host_state(host.uuid, "enable")


