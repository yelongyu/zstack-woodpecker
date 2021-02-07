'''
test eip connection in mini environment
1. create vm of vlan network
2. create vip and eip
3. check eip connectivity
4. attach eip to vmNic
5. check eip connectivity

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
    test_util.test_dsc('Start to test eip in mini')
    pri_l3_name = 'l3VlanNetwork1'
    pri_l3_uuid = test_lib.lib_get_l3_by_name(pri_l3_name).uuid

    pub_l3_name = 'public network'
    pub_l3_uuid = test_lib.lib_get_l3_by_name(pub_l3_name).uuid

    l3_uuids = [pri_l3_uuid]
    test_util.test_dsc('successfully get l3 uuid')

    test_util.test_dsc('start to create vm')
    vm = test_stub.create_vm('vm_for_eip_test', l3_uuids)
    test_obj_dict.add_vm(vm)
    vm.check()
    test_util.test_dsc('successfully create vm for eip')

    vip = test_stub.create_vip('vip_for_eip', pub_l3_uuid)
    test_obj_dict.add_vip(vip)
    test_util.test_dsc('successfully create vip')

    eip = test_stub.create_eip('eip_in_mini', vip.get_vip().uuid)
    time.sleep(6)

    if test_lib.lib_check_directly_ping(vip.get_vip().ip):
        test_util.test_fail('not expected to be able to ping vip while it succeed')
    test_util.test_dsc('successfully create eip')

    vm_nic = vm.vm.vmNics[0]
    vm_nic_uuid = vm_nic.uuid
    net_ops.attach_eip(eip.get_eip().uuid, vm_nic_uuid)
    time.sleep(6)

    if not test_lib.lib_check_directly_ping(vip.get_vip().ip):
        test_util.test_fail('expect to be able to ping vip while it failed')
    else:
        test_util.test_dsc('Successfully attach eip to vm')

    vm.destroy()
    test_obj_dict.rm_vm(vm)
    if test_lib.lib_check_directly_ping(vip.get_vip().ip):
        test_util.test_fail('not expected to be able to ping vip while it succeed')

    eip.delete()
    vip.delete()

    test_obj_dict.rm_vip(vip)
    test_util.test_pass('Successfully test eip connectivity')

def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
