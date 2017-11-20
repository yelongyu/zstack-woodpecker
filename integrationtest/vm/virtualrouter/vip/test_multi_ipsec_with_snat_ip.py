'''

Test multiple IPsec connection with 1 snat ip

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
ipsec1 = None
ipsec2 = None
ipsec3 = None
ipsec4 = None
mevoco1_ip = None
mevoco2_ip = None

def test():
    global mevoco1_ip
    global mevoco2_ip
    global ipsec1
    global ipsec2
    global ipsec3
    global ipsec4
    mevoco1_ip = os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP']
    mevoco2_ip = os.environ['secondZStackMnIp']
    test_util.test_dsc('Create test vm in mevoco1')
    vm1 = test_stub.create_vlan_vm(os.environ.get('l3VlanNetworkName1'))
    test_obj_dict1.add_vm(vm1)
    vm1.check()
    pri_l3_uuid1 = vm1.vm.vmNics[0].l3NetworkUuid
    vr1 = test_lib.lib_find_vr_by_l3_uuid(pri_l3_uuid1)[0]
    l3_uuid1 = test_lib.lib_find_vr_pub_nic(vr1).l3NetworkUuid
    vr1_pub_ip = test_lib.lib_find_vr_pub_ip(vr1)

    vip1 = test_stub.get_snat_ip_as_vip(vr1_pub_ip)
 
    cond = res_ops.gen_query_conditions('uuid', '=', pri_l3_uuid1)
    first_zstack_cidrs = res_ops.query_resource(res_ops.L3_NETWORK, cond)[0].ipRanges[0].networkCidr
    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco2_ip
    test_util.test_dsc('Create test vm in mevoco2')
    vm2 = test_stub.create_vlan_vm(os.environ.get('l3VlanDNATNetworkName'))
    test_obj_dict2.add_vm(vm2)
    vm2.check()
    pri_l3_uuid2 = vm2.vm.vmNics[0].l3NetworkUuid
    vr2 = test_lib.lib_find_vr_by_l3_uuid(pri_l3_uuid2)[0]
    l3_uuid2 = test_lib.lib_find_vr_pub_nic(vr2).l3NetworkUuid
    vip2 = test_stub.create_vip('ipsec2_vip', l3_uuid2)
    cond = res_ops.gen_query_conditions('uuid', '=', pri_l3_uuid2)
    second_zstack_cidrs = res_ops.query_resource(res_ops.L3_NETWORK, cond)[0].ipRanges[0].networkCidr
 
    test_util.test_dsc('Create test vm in mevoco2')
    vm3 = test_stub.create_vlan_vm(os.environ.get('l3VlanNetworkName4'))
    test_obj_dict2.add_vm(vm3)
    vm3.check()
    pri_l3_uuid3 = vm3.vm.vmNics[0].l3NetworkUuid
    vr3 = test_lib.lib_find_vr_by_l3_uuid(pri_l3_uuid2)[0]
    l3_uuid3 = test_lib.lib_find_vr_pub_nic(vr3).l3NetworkUuid
    vip3 = test_stub.create_vip('ipsec3_vip', l3_uuid3)
    cond = res_ops.gen_query_conditions('uuid', '=', pri_l3_uuid3)
    third_zstack_cidrs = res_ops.query_resource(res_ops.L3_NETWORK, cond)[0].ipRanges[0].networkCidr

    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco1_ip
    test_util.test_dsc('Create ipsec in mevoco1')
    ipsec1 = ipsec_ops.create_ipsec_connection('ipsec1', pri_l3_uuid1, vip2.get_vip().ip, '123456', vip1.get_vip().uuid, [second_zstack_cidrs]) 
    ipsec3 = ipsec_ops.create_ipsec_connection('ipsec3', pri_l3_uuid1, vip3.get_vip().ip, '123456', vip1.get_vip().uuid, [third_zstack_cidrs]) 

    vip1_uuid = vip1.get_vip().uuid
    vip1_db = test_lib.lib_get_vip_by_uuid(vip1_uuid)
    assert "IPsec" in vip1_db.useFor
    assert vip1_db.useFor.count("IPsec") == 1

    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco2_ip
    test_util.test_dsc('Create ipsec in mevoco2')
    ipsec2 = ipsec_ops.create_ipsec_connection('ipsec2', pri_l3_uuid2, vip1.get_vip().ip, '123456', vip2.get_vip().uuid, [first_zstack_cidrs]) 
    ipsec4 = ipsec_ops.create_ipsec_connection('ipsec4', pri_l3_uuid3, vip1.get_vip().ip, '123456', vip3.get_vip().uuid, [first_zstack_cidrs]) 

    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco1_ip
    if not test_lib.lib_check_ping(vm1.vm, vm2.vm.vmNics[0].ip):
        test_util.test_fail('vm in mevoco1[MN:%s] could not connect to vm in mevoco2[MN:%s]' % (mevoco1_ip, mevoco2_ip))

    if not test_lib.lib_check_ping(vm1.vm, vm3.vm.vmNics[0].ip):
        test_util.test_fail('vm in mevoco1[MN:%s] could not connect to vm in mevoco2[MN:%s]' % (mevoco1_ip, mevoco2_ip))

    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco2_ip
    if not test_lib.lib_check_ping(vm2.vm, vm1.vm.vmNics[0].ip):
        test_util.test_fail('vm in mevoco1[MN:%s] could not connect to vm in mevoco2[MN:%s]' % (mevoco2_ip, mevoco1_ip))
 
    if not test_lib.lib_check_ping(vm3.vm, vm1.vm.vmNics[0].ip):
        test_util.test_fail('vm in mevoco1[MN:%s] could not connect to vm in mevoco2[MN:%s]' % (mevoco2_ip, mevoco1_ip))

    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco1_ip
    ipsec_ops.delete_ipsec_connection(ipsec1.uuid)
    ipsec_ops.delete_ipsec_connection(ipsec3.uuid)

    if test_lib.lib_check_ping(vm1.vm, vm2.vm.vmNics[0].ip, no_exception=True):
        test_util.test_fail('vm in mevoco1[MN:%s] could still connect to vm in mevoco2[MN:%s] after Ipsec is deleted' % (mevoco1_ip, mevoco2_ip))

    if test_lib.lib_check_ping(vm1.vm, vm3.vm.vmNics[0].ip, no_exception=True):
        test_util.test_fail('vm in mevoco1[MN:%s] could still connect to vm in mevoco2[MN:%s] after Ipsec is deleted' % (mevoco1_ip, mevoco2_ip))

    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco2_ip
    if test_lib.lib_check_ping(vm2.vm, vm1.vm.vmNics[0].ip, no_exception=True):
        test_util.test_fail('vm in mevoco2[MN:%s] could still connect to vm in mevoco1[MN:%s] after Ipsec is deleted' % (mevoco2_ip, mevoco1_ip))
    if test_lib.lib_check_ping(vm3.vm, vm1.vm.vmNics[0].ip, no_exception=True):
        test_util.test_fail('vm in mevoco2[MN:%s] could still connect to vm in mevoco1[MN:%s] after Ipsec is deleted' % (mevoco2_ip, mevoco1_ip))

    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco1_ip
    test_lib.lib_error_cleanup(test_obj_dict1)
    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco2_ip
    ipsec_ops.delete_ipsec_connection(ipsec2.uuid)
    ipsec_ops.delete_ipsec_connection(ipsec4.uuid)
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

    global ipsec1
    if ipsec1 != None:
        ipsec_ops.delete_ipsec_connection(ipsec1.uuid)
    global ipsec3
    if ipsec3 != None:
        ipsec_ops.delete_ipsec_connection(ipsec3.uuid)

    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco2_ip
    global test_obj_dict2
    test_lib.lib_error_cleanup(test_obj_dict2)

    global ipsec2
    if ipsec2 != None:
        ipsec_ops.delete_ipsec_connection(ipsec2.uuid)
    global ipsec4
    if ipsec4 != None:
        ipsec_ops.delete_ipsec_connection(ipsec4.uuid)
