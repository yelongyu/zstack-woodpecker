'''

Test IPsec

@author: Quarkonics
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.ipsec_operations as ipsec_ops
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    mevoco1_ip = os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP']
    mevoco2_ip = os.environ['secondZStackMnIp']
    test_util.test_dsc('Create test vm in mevoco1')
    vm1 = test_stub.create_vlan_vm(os.environ.get('l3VlanNetworkName1'))
    test_obj_dict.add_vm(vm1)
    vm1.check()
    pri_l3_uuid1 = vm1.vm.vmNics[0].l3NetworkUuid
    vr1 = test_lib.lib_find_vr_by_l3_uuid(pri_l3_uuid1)[0]
    l3_uuid1 = test_lib.lib_find_vr_pub_nic(vr1).l3NetworkUuid
    vip1 = test_stub.create_vip('ipsec1_vip', l3_uuid1)
    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco2_ip
    test_util.test_dsc('Create test vm in mevoco2')
    vm2 = test_stub.create_vlan_vm(os.environ.get('l3VlanDNATNetworkName'))
    test_obj_dict.add_vm(vm2)
    vm2.check()
    pri_l3_uuid2 = vm2.vm.vmNics[0].l3NetworkUuid
    vr2 = test_lib.lib_find_vr_by_l3_uuid(pri_l3_uuid2)[0]
    l3_uuid2 = test_lib.lib_find_vr_pub_nic(vr2).l3NetworkUuid
    vip2 = test_stub.create_vip('ipsec2_vip', l3_uuid2)

    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco1_ip
    test_util.test_dsc('Create ipsec in mevoco1')
    ipsec_ops.create_ipsec_connection('ipsec1', l3_uuid1, vip2.get_vip().ip, '123456', vip1.get_vip().uuid, os.environ['secondZStackCidrs'])

    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco2_ip
    test_util.test_dsc('Create ipsec in mevoco2')
    ipsec_ops.create_ipsec_connection('ipsec1', l3_uuid2, vip1.get_vip().ip, '123456', vip2.get_vip().uuid, os.environ['firstZStackCidrs'])

    if not test_lib.lib_check_ping(vm1.vm, vm2.vm.vmNics[0].ip):
        test_util.test_fail('vm in mevoco1[MN:%s] could not connect to vm in mevoco2[MN:%s]' % (mevoco1_ip, mevoco2_ip))

    test_util.test_pass('Create Ipsec Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
