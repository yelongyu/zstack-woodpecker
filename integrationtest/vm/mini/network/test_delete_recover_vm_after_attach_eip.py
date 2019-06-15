'''
add case to cover bug MINI-696
1. create eip and vm, and attach eip to vm
2. delete and recover vm
3. check whether vm can be started
@author: chen.zhou
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import time
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    pri_l3_name = 'l3VlanNetwork1'
    pri_l3_uuid = test_lib.lib_get_l3_by_name(pri_l3_name).uuid
    l3_uuid_list = [pri_l3_uuid]

    pub_l3_name = 'public network'
    pub_l3_uuid = test_lib.lib_get_l3_by_name(pub_l3_name).uuid
    ip_status = net_ops.get_ip_capacity_by_l3s([pub_l3_uuid])
    if not ip_status.availableCapacity:
        test_util.test_fail('no available pub ip for eip test')

    vip = test_stub.create_vip('vip_for_eip', pub_l3_uuid)
    eip = test_stub.create_eip(eip_name='eip_test', vip_uuid=vip.get_vip().uuid)
    vm = test_stub.create_vm(vm_name = 'vm_for_eip', l3_uuids=l3_uuid_list)
    test_obj_dict.add_vm(vm)
    vm.check()

    vip.attach_eip(eip)
    eip.attach(vm.get_vm().vmNics[0].uuid, vm)
    time.sleep(8)
    if not test_lib.lib_check_directly_ping(vip.get_vip().ip):
        test_util.test_fail('expect to be able to ping vip while it failed')

    vm.destroy()
    time.sleep(2)
    vm.recover()
    vm.check()
    vm.start()
