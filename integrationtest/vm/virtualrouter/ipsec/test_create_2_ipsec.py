'''

Test IPsec

@author: Quarkonics
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.ipsec_operations as ipsec_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict1 = test_state.TestStateDict()
test_obj_dict2 = test_state.TestStateDict()
test_obj_dict3 = test_state.TestStateDict()
ipsec11 = None
ipsec12 = None
ipsec2 = None
ipsec3 = None
mevoco1_ip = None
mevoco2_ip = None
mevoco3_ip = None

def test():
    global mevoco1_ip
    global mevoco2_ip
    global mevoco3_ip
    global ipsec11
    global ipsec12
    global ipsec2
    global ipsec3
    mevoco1_ip = os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP']
    mevoco2_ip = os.environ['secondZStackMnIp']
    mevoco3_ip = os.environ['thirdZStackMnIp']
    test_util.test_dsc('Create test vm in mevoco1')
    vm1 = test_stub.create_vlan_vm(os.environ.get('l3VlanNetworkName1'))
    test_obj_dict1.add_vm(vm1)
    vm1.check()
    pri_l3_uuid1 = vm1.vm.vmNics[0].l3NetworkUuid
    vr1 = test_lib.lib_find_vr_by_l3_uuid(pri_l3_uuid1)[0]
    l3_uuid1 = test_lib.lib_find_vr_pub_nic(vr1).l3NetworkUuid
    vip11 = test_stub.create_vip('ipsec1_vip', l3_uuid1)
    vip12 = test_stub.create_vip('ipsec1_vip', l3_uuid1)
    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco2_ip
    test_util.test_dsc('Create test vm in mevoco2')
    vm2 = test_stub.create_vlan_vm(os.environ.get('l3VlanDNATNetworkName'))
    test_obj_dict2.add_vm(vm2)
    vm2.check()
    pri_l3_uuid2 = vm2.vm.vmNics[0].l3NetworkUuid
    vr2 = test_lib.lib_find_vr_by_l3_uuid(pri_l3_uuid2)[0]
    l3_uuid2 = test_lib.lib_find_vr_pub_nic(vr2).l3NetworkUuid
    vip2 = test_stub.create_vip('ipsec2_vip', l3_uuid2)

    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco3_ip
    test_util.test_dsc('Create test vm in mevoco3')
    vm3 = test_stub.create_vlan_vm(os.environ.get('l3VlanNetworkName3'))
    test_obj_dict2.add_vm(vm3)
    vm3.check()
    pri_l3_uuid3 = vm3.vm.vmNics[0].l3NetworkUuid
    vr3 = test_lib.lib_find_vr_by_l3_uuid(pri_l3_uuid3)[0]
    l3_uuid3 = test_lib.lib_find_vr_pub_nic(vr3).l3NetworkUuid
    vip3 = test_stub.create_vip('ipsec3_vip', l3_uuid3)

    cond = res_ops.gen_query_conditions('uuid', '=', pri_l3_uuid1)
    first_zstack_cidrs = res_ops.query_resource(res_ops.L3_NETWORK, cond)[0].ipRanges[0].networkCidr
    cond = res_ops.gen_query_conditions('uuid', '=', pri_l3_uuid2)
    second_zstack_cidrs = res_ops.query_resource(res_ops.L3_NETWORK, cond)[0].ipRanges[0].networkCidr
    cond = res_ops.gen_query_conditions('uuid', '=', pri_l3_uuid3)
    third_zstack_cidrs = res_ops.query_resource(res_ops.L3_NETWORK, cond)[0].ipRanges[0].networkCidr

    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco1_ip
    test_util.test_dsc('Create ipsec in mevoco1')
    #ipsec11 = ipsec_ops.create_ipsec_connection('ipsec11', pri_l3_uuid1, vip2.get_vip().ip, '123456', vip11.get_vip().uuid, [os.environ['secondZStackCidrs']])
    ipsec11 = ipsec_ops.create_ipsec_connection('ipsec11', pri_l3_uuid1, vip2.get_vip().ip, '123456', vip11.get_vip().uuid, second_zstack_cidrs)
    #ipsec12 = ipsec_ops.create_ipsec_connection('ipsec12', pri_l3_uuid1, vip3.get_vip().ip, '123456', vip12.get_vip().uuid, [os.environ['thirdZStackCidrs']])
    ipsec12 = ipsec_ops.create_ipsec_connection('ipsec12', pri_l3_uuid1, vip3.get_vip().ip, '123456', vip12.get_vip().uuid, third_zstack_cidrs)

    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco2_ip
    test_util.test_dsc('Create ipsec in mevoco2')
    #ipsec2 = ipsec_ops.create_ipsec_connection('ipsec2', pri_l3_uuid2, vip11.get_vip().ip, '123456', vip2.get_vip().uuid, [os.environ['firstZStackCidrs']])
    ipsec2 = ipsec_ops.create_ipsec_connection('ipsec2', pri_l3_uuid2, vip11.get_vip().ip, '123456', vip2.get_vip().uuid, first_zstack_cidrs)

    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco3_ip
    test_util.test_dsc('Create ipsec in mevoco3')
    #ipsec3 = ipsec_ops.create_ipsec_connection('ipsec3', pri_l3_uuid3, vip12.get_vip().ip, '123456', vip3.get_vip().uuid, [os.environ['firstZStackCidrs']])
    ipsec3 = ipsec_ops.create_ipsec_connection('ipsec3', pri_l3_uuid3, vip12.get_vip().ip, '123456', vip3.get_vip().uuid, first_zstack_cidrs)

    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco1_ip
    if not test_lib.lib_check_ping(vm1.vm, vm2.vm.vmNics[0].ip):
        test_util.test_fail('vm in mevoco1[MN:%s] could not connect to vm in mevoco2[MN:%s]' % (mevoco1_ip, mevoco2_ip))
    if not test_lib.lib_check_ping(vm1.vm, vm3.vm.vmNics[0].ip):
        test_util.test_fail('vm in mevoco1[MN:%s] could not connect to vm in mevoco3[MN:%s]' % (mevoco1_ip, mevoco3_ip))

    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco2_ip
    if not test_lib.lib_check_ping(vm2.vm, vm1.vm.vmNics[0].ip):
        test_util.test_fail('vm in mevoco2[MN:%s] could not connect to vm in mevoco1[MN:%s]' % (mevoco2_ip, mevoco1_ip))

    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco3_ip
    if not test_lib.lib_check_ping(vm3.vm, vm1.vm.vmNics[0].ip):
        test_util.test_fail('vm in mevoco3[MN:%s] could not connect to vm in mevoco1[MN:%s]' % (mevoco3_ip, mevoco1_ip))

    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco1_ip
    ipsec_ops.delete_ipsec_connection(ipsec11.uuid)

    if test_lib.lib_check_ping(vm1.vm, vm2.vm.vmNics[0].ip, no_exception=True):
        test_util.test_fail('vm in mevoco1[MN:%s] could still connect to vm in mevoco2[MN:%s] after Ipsec is deleted' % (mevoco1_ip, mevoco2_ip))

    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco2_ip
    if test_lib.lib_check_ping(vm2.vm, vm1.vm.vmNics[0].ip, no_exception=True):
        test_util.test_fail('vm in mevoco2[MN:%s] could still connect to vm in mevoco1[MN:%s] after Ipsec is deleted' % (mevoco2_ip, mevoco1_ip))

    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco1_ip
    if not test_lib.lib_check_ping(vm1.vm, vm3.vm.vmNics[0].ip):
        test_util.test_fail('vm in mevoco1[MN:%s] could not connect to vm in mevoco3[MN:%s]' % (mevoco1_ip, mevoco3_ip))

    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco3_ip
    ipsec_ops.delete_ipsec_connection(ipsec3.uuid)

    if test_lib.lib_check_ping(vm1.vm, vm3.vm.vmNics[0].ip, no_exception=True):
        test_util.test_fail('vm in mevoco1[MN:%s] could still connect to vm in mevoco3[MN:%s] after Ipsec is deleted' % (mevoco1_ip, mevoco3_ip))

    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco1_ip
    ipsec_ops.delete_ipsec_connection(ipsec12.uuid)
    test_lib.lib_error_cleanup(test_obj_dict1)
    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco2_ip
    ipsec_ops.delete_ipsec_connection(ipsec2.uuid)
    test_lib.lib_error_cleanup(test_obj_dict2)
    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco1_ip
    test_util.test_pass('Create Ipsec Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global mevoco1_ip
    global mevoco2_ip
    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco1_ip
    global test_obj_dict1
    test_lib.lib_error_cleanup(test_obj_dict1)

    global ipsec11
    if ipsec11 != None:
        ipsec_ops.delete_ipsec_connection(ipsec11.uuid)

    global ipsec12
    if ipsec12 != None:
        ipsec_ops.delete_ipsec_connection(ipsec12.uuid)

    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco2_ip
    global test_obj_dict2
    test_lib.lib_error_cleanup(test_obj_dict2)

    global ipsec2
    if ipsec2 != None:
        ipsec_ops.delete_ipsec_connection(ipsec2.uuid)

    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco3_ip
    global test_obj_dict3
    test_lib.lib_error_cleanup(test_obj_dict3)

    global ipsec3
    if ipsec3 != None:
        ipsec_ops.delete_ipsec_connection(ipsec3.uuid)
