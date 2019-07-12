'''
test one eip attach to two vm respectively
1. create vip and eip
2. create vm1, vm2
3. attach eip to vm1, then detach eip from vm1 and check eip connectivity
4. attach eip to vm2, check eip connectivity

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
    pri_l3_name = 'l3VlanNetwork1'
    pri_l3_uuid = test_lib.lib_get_l3_by_name(pri_l3_name).uuid
    l3_uuids = [pri_l3_uuid]

    pub_l3_name = 'public network'
    pub_l3_uuid = test_lib.lib_get_l3_by_name(pub_l3_name).uuid
    ip_status = net_ops.get_ip_capacity_by_l3s([pub_l3_uuid])
    if not ip_status.availableCapacity:
        test_util.test_fail('no available pub ip for eip test')

    vip_option = test_util.VipOption()
    vip_option.set_l3_uuid(pub_l3_uuid)
    vip_option.set_name('vip_for_one_eip_two_vm')
    vip = test_vip_header.ZstackTestVip()
    vip.set_creation_option(vip_option)
    vip.create()
    test_obj_dict.add_vip(vip)
    test_util.test_dsc('successfully create vip')

    eip_option = test_util.EipOption()
    eip_option.set_vip_uuid(vip.get_vip().uuid)
    eip_option.set_name('eip_for_two_vm')
    eip_option.set_description('This is an eip in mini for two vm')
    eip = test_eip_header.ZstackTestEip()
    eip.set_creation_option(eip_option)
    eip.create()
    test_util.test_dsc('successfully create eip')

    # create two vm
    test_util.test_dsc('start to create vm1, vm2')
    cluster_uuid = res_ops.query_resource(res_ops.CLUSTER)[0].uuid
    cond = res_ops.gen_query_conditions('format', '!=', 'iso')
    image_uuid = res_ops.query_resource(res_ops.IMAGE, cond)[0].uuid

    vm_option = test_util.VmOption()
    vm_option.set_name('vm_for_one_eip')
    vm_option.set_cluster_uuid(cluster_uuid)
    vm_option.set_image_uuid(image_uuid)
    vm_option.set_l3_uuids(l3_uuids)
    vm_option.set_cpu_num(1)
    vm_option.set_memory_size(536870912)
    vm1 = test_vm_header.ZstackTestVm()
    vm1.set_creation_option(vm_option)
    vm1.create()
    test_obj_dict.add_vm(vm1)
    vm1.check()
    test_util.test_dsc('Successfully create vm1')
    vm2 = test_vm_header.ZstackTestVm()
    vm2.set_creation_option(vm_option)
    vm2.create()
    test_obj_dict.add_vm(vm2)
    vm2.check()
    test_util.test_dsc('Successfully create vm2')

    test_util.test_dsc('attach eip to vm1')
    net_ops.attach_eip(eip.get_eip().uuid, vm1.get_vm().vmNics[0].uuid)
    #vip.check()
    net_ops.detach_eip(eip.get_eip().uuid)
    #vip.check()

    time.sleep(6)
    if test_lib.lib_check_directly_ping(vip.get_vip().ip):
        test_util.test_fail('not expect to be able to ping vip while it succeeded')

    net_ops.attach_eip(eip.get_eip().uuid, vm2.get_vm().vmNics[0].uuid)

    time.sleep(8)
    if not test_lib.lib_check_directly_ping(vip.get_vip().ip):
        test_util.test_fail('expect to be able to ping vip while it failed')

    eip.delete()
    vip.delete()
    vm1.destroy()
    vm2.destroy()

    test_util.test_pass('case one eip two vm passed')

def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)

