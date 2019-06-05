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
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import zstackwoodpecker.zstack_test.zstack_test_vip as test_vip_header
import zstackwoodpecker.zstack_test.zstack_test_eip as test_eip_header
import time
import os

test_obj_dict = test_state.TestStateDict()

def test():
    test_util.test_dsc('Start to test eip in mini')
    pri_l3_name = 'l3VlanNetwork1'
    pri_l3_uuid = test_lib.lib_get_l3_by_name(pri_l3_name).uuid

    pub_l3_name = 'public network'
    pub_l3_uuid = test_lib.lib_get_l3_by_name(pub_l3_name).uuid
    ip_status = net_ops.get_ip_capacity_by_l3s([pub_l3_uuid])
    if not ip_status.availableCapacity:
        test_util.test_fail('no available pub ip for eip test')
    
    l3_uuids = [pri_l3_uuid]
    test_util.test_dsc('successfully get l3 uuid')

    cluster_uuid = res_ops.query_resource(res_ops.CLUSTER)[0].uuid
    image_uuid = res_ops.query_resource(res_ops.IMAGE)[0].uuid
    
    test_util.test_dsc('start to create vm')
    vm_option = test_util.VmOption()
    vm_option.set_name('vm_for_mini_eip_test')
    vm_option.set_cluster_uuid(cluster_uuid)
    vm_option.set_image_uuid(image_uuid)
    vm_option.set_l3_uuids(l3_uuids)
    vm_option.set_cpu_num(1)
    vm_option.set_memory_size(536870912)
    vm = test_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_option)
    vm.create()
    test_obj_dict.add_vm(vm)
    vm.check()
    test_util.test_dsc('successfully create vm for eip')
            
    vip_option = test_util.VipOption()
    vip_option.set_l3_uuid(pub_l3_uuid)
    vip_option.set_name('vip_for_mini_eip')
    vip = test_vip_header.ZstackTestVip()
    vip.set_creation_option(vip_option)
    vip.create()
    test_obj_dict.add_vip(vip)
    test_util.test_dsc('successfully create vip')

    eip_option = test_util.EipOption()
    eip_option.set_vip_uuid(vip.get_vip().uuid)
    eip_option.set_name('eip_for_mini_test')
    eip_option.set_description('This is an eip in mini')
    eip = test_eip_header.ZstackTestEip()
    eip.set_creation_option(eip_option)
    eip.create()
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