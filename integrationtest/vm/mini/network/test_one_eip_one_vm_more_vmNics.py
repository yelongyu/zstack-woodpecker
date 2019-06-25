'''
test to attach and detach eip to and from every vnic in one vm
1. create vip and eip
2. create vm with 5 VlanNetwork
3. test to attach and detach eip to and from every vnic

@author: chen.zhou
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.resource_operations as res_ops
import time
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

l3_list=['l3VlanNetwork1', 'l3VlanNetwork2', 'l3VlanNetwork3', 'l3VlanNetwork4', 'l3VlanNetwork5']
pri_l3_uuid_list=[]

def test():
    for l3_name in l3_list:
        pri_l3_uuid_list.append(test_lib.lib_get_l3_by_name(l3_name).uuid)

    pub_l3_name = 'public network'
    pub_l3_uuid = test_lib.lib_get_l3_by_name(pub_l3_name).uuid

    vip = test_stub.create_vip('vip_test', pub_l3_uuid)
    test_obj_dict.add_vip(vip)
    test_util.test_dsc('successfully create vip')

    eip = test_stub.create_eip('eip', vip.get_vip().uuid)
    vm = test_stub.create_vm('vm_with_more_vnics', pri_l3_uuid_list)
    test_obj_dict.add_vm(vm)
    vm.check()

    vip.attach_eip(eip)
    # start to attach eip to every vnic respectively
    vinc_list = vm.get_vm().vmNics

    for vnic in vinc_list:
        eip.attach(vnic.uuid, vm)
        time.sleep(5)
        eip.detach()
        time.sleep(5)

def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
