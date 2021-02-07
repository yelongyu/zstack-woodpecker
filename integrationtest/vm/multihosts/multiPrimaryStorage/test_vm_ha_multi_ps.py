'''
@author: FangSun
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import apibinding.inventory as inventory
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.primarystorage_operations as ps_ops
import zstackwoodpecker.operations.ha_operations as ha_ops
import zstackwoodpecker.header.vm as vm_header
import zstackwoodpecker.operations.host_operations as host_ops
import random
import time
import os

_config_ = {
        'timeout' : 3000,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
new_ps_list = []
VM_COUNT = 1
DATA_VOLUME_NUMBER = 10

record = dict()


@test_stub.skip_if_have_local
@test_stub.skip_if_only_one_ps
def test():
    ps = res_ops.query_resource(res_ops.PRIMARY_STORAGE)
    for i in ps:
        if i.type =='SharedBlock':
            test_util.test_skip('Skip test on SharedBlock PS.')

    ps_env = test_stub.PSEnvChecker()
    
    mn_ip = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].hostName
    conditions = res_ops.gen_query_conditions('state', '=', 'Enabled')
    conditions = res_ops.gen_query_conditions('status', '=', 'Connected', conditions)
    conditions = res_ops.gen_query_conditions('managementIp', '!=', mn_ip, conditions)
    host = random.choice(res_ops.query_resource(res_ops.HOST, conditions))
    record['host_ip'] = host.managementIp
    record['host_port'] = host.sshPort
    record['host_uuid'] = host.uuid

    test_util.test_dsc("Create {0} vm each with {1} datavolume".format(VM_COUNT, DATA_VOLUME_NUMBER))
    if ps_env.is_sb_ceph_env:
        ps_list = res_ops.query_resource(res_ops.PRIMARY_STORAGE)
        ps = random.choice(ps_list)
        ps_uuid = ps.uuid
        vm_list = test_stub.create_multi_vms(name_prefix='test-', count=VM_COUNT,
                                             data_volume_number=DATA_VOLUME_NUMBER, host_uuid=host.uuid, ps_uuid=ps_uuid, timeout=1800000, bs_type="ImageStoreBackupStorage" if ps.type == "SharedBlock" else "Ceph")
    else:
        vm_list = test_stub.create_multi_vms(name_prefix='test-', count=VM_COUNT,
                                             data_volume_number=DATA_VOLUME_NUMBER, host_uuid=host.uuid, timeout=1800000)

    for vm in vm_list:
        test_obj_dict.add_vm(vm)

    test_util.test_logger("host %s is disconnecting" % host.managementIp)
    for vm in vm_list:
        ha_ops.set_vm_instance_ha_level(vm.get_vm().uuid, "NeverStop")

    #l2_network_interface = os.environ.get('l2ManagementNetworkInterface')
    l2interface = test_lib.lib_get_l2s_by_vm(vm.get_vm())[0].physicalInterface
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
        if test_lib.lib_find_host_by_vm(vm.get_vm()).managementIp == host.managementIp:
            test_util.test_fail("VM is expected to start running on another host")
        vm.set_state(vm_header.RUNNING)
        vm.check()

    cmd = 'PORT=%s bash -ex %s %s' % (host.sshPort, os.environ.get('hostRecoverScript'),host.managementIp)
    test_util.test_logger(cmd)
    os.system(cmd)
    host_ops.reconnect_host(host.uuid)

    test_util.test_pass('Multi PrimaryStorage Vm HA Test Pass')


def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)
    os.system('PORT=%s bash -ex %s %s' % (record['host_port'], os.environ.get('hostRecoverScript'), record['host_ip']))
    host_ops.reconnect_host(record['host_uuid'])
