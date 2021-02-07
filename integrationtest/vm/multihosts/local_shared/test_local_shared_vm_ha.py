'''
@author: FangSun
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import os
import zstackwoodpecker.operations.primarystorage_operations as ps_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import apibinding.inventory as inventory
import zstackwoodpecker.operations.vm_operations as vm_ops
import time
import random
import zstackwoodpecker.header.vm as vm_header
import zstackwoodpecker.operations.host_operations as host_ops

_config_ = {
        'timeout' : 3000,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
record = {}


@test_stub.skip_if_not_local_shared
def test():

    mn_ip = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].hostName
    conditions = res_ops.gen_query_conditions('state', '=', 'Enabled')
    conditions = res_ops.gen_query_conditions('status', '=', 'Connected', conditions)
    conditions = res_ops.gen_query_conditions('managementIp', '!=', mn_ip, conditions)
    host = random.choice(res_ops.query_resource(res_ops.HOST, conditions))
    record['host_ip'] = host.managementIp
    record['host_port'] = host.sshPort
    record['host_uuid'] = host.uuid

    vm_list=list(test_stub.generate_local_shared_test_vms(test_obj_dict, vm_ha=True, host_uuid=host.uuid))
    (vm_root_local, vm_root_local_data_local,
     vm_root_local_data_shared, vm_root_local_data_mixed,
     vm_root_shared, vm_root_shared_data_local,
     vm_root_shared_data_shared, vm_root_shared_data_mixed) = vm_list

    l2interface = test_lib.lib_get_l2s_by_vm(vm_list[0].get_vm())[0].physicalInterface
    l2_network_interface = test_stub.get_host_l2_nic_name(l2interface)
    cmd = "ifdown %s && sleep 180 && ifup %s" % (l2_network_interface, l2_network_interface)
    host_username = os.environ.get('hostUsername')
    host_password = os.environ.get('hostPassword')
    rsp = test_lib.lib_execute_ssh_cmd(host.managementIp, host_username, host_password, cmd, 240)
    if not rsp:
        test_util.test_logger("host is expected to shutdown after its network down for a while")

    test_util.test_logger("wait for 180 seconds")
    time.sleep(180)
    for vm in vm_list:
        vm.update()

    for vm in (vm_root_shared,vm_root_shared_data_shared):
        if test_lib.lib_find_host_by_vm(vm.get_vm()).managementIp == host.managementIp:
            test_util.test_fail("VM is expected to start running on another host")
            vm.set_state(vm_header.RUNNING)
            vm.check()

    for vm in (vm_root_local, vm_root_local_data_local, vm_root_local_data_shared,
               vm_root_local_data_mixed, vm_root_shared_data_local, vm_root_shared_data_mixed):
        assert vm.get_vm().state == inventory.STOPPED

    cmd = 'PORT=%s bash -ex %s %s' % (host.sshPort, os.environ.get('hostRecoverScript'),host.managementIp)
    test_util.test_logger(cmd)
    os.system(cmd)
    host_ops.reconnect_host(host.uuid)


def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)
    os.system('PORT=%s bash -ex %s %s' % (record['host_port'], os.environ.get('hostRecoverScript'), record['host_ip']))
    host_ops.reconnect_host(record['host_uuid'])
