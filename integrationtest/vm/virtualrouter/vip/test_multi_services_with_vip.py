'''

Test PF, LB, IPsec with 1 snat ip

@author: czhou25
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.ipsec_operations as ipsec_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_port_forwarding as zstack_pf_header
import zstackwoodpecker.zstack_test.zstack_test_load_balancer as zstack_lb_header
import apibinding.inventory as inventory
import os
import time

test_stub = test_lib.lib_get_test_stub()
test_obj_dict1 = test_state.TestStateDict()
test_obj_dict2 = test_state.TestStateDict()
ipsec1 = None
ipsec2 = None
mevoco1_ip = None
mevoco2_ip = None
PfRule = test_state.PfRule
Port = test_state.Port


def test():
    global mevoco1_ip
    global mevoco2_ip
    global ipsec1
    global ipsec2
    mevoco1_ip = os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP']
    mevoco2_ip = os.environ['secondZStackMnIp']
    test_util.test_dsc('Create test vm in mevoco1')
    vm1 = test_stub.create_vlan_vm(os.environ.get('l3VlanNetworkName1'))
    test_obj_dict1.add_vm(vm1)
    vm1.check()
    vm_nic1 = vm1.get_vm().vmNics[0]
    vm_nic1_uuid = vm_nic1.uuid
    vm3 = test_stub.create_vlan_vm(os.environ.get('l3VlanNetworkName1'))
    test_obj_dict1.add_vm(vm3)
    vm3.check()
    vm_nic3 = vm3.get_vm().vmNics[0]
    vm_nic3_uuid = vm_nic3.uuid
    pri_l3_uuid1 = vm1.vm.vmNics[0].l3NetworkUuid
    vr1 = test_lib.lib_find_vr_by_l3_uuid(pri_l3_uuid1)[0]
    l3_uuid1 = test_lib.lib_find_vr_pub_nic(vr1).l3NetworkUuid
    vr1_pub_ip = test_lib.lib_find_vr_pub_ip(vr1)
    vip1 = test_stub.create_vip('vip for multi-services', l3_uuid1)
    vip_uuid = vip1.get_vip().uuid
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
 
    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco1_ip

    test_util.test_dsc('Create PF in mevoco1')
    l3_name = os.environ.get('l3NoVlanNetworkName1')
    vr = test_stub.create_vr_vm(test_obj_dict1, l3_name)
    l3_name = os.environ.get('l3VlanNetworkName4')
    vr = test_stub.create_vr_vm(test_obj_dict1, l3_name) 
    vr_pub_ip = test_lib.lib_find_vr_pub_ip(vr)
    pf_creation_opt1 = PfRule.generate_pf_rule_option(vr_pub_ip, protocol=inventory.TCP, vip_target_rule=Port.rule4_ports, private_target_rule=Port.rule4_ports, vip_uuid=vip_uuid)
    test_pf1 = zstack_pf_header.ZstackTestPortForwarding()
    test_pf1.set_creation_option(pf_creation_opt1)
    test_pf1.create()
    vip1.attach_pf(test_pf1)
    vip1.check()
    test_pf1.attach(vm_nic1_uuid, vm1)
    vip1.check()

    test_util.test_dsc('Create LB in mevoco1')
    lb = zstack_lb_header.ZstackTestLoadBalancer()
    lb.create('create lb test', vip1.get_vip().uuid)
    test_obj_dict1.add_load_balancer(lb)
    vip1.attach_lb(lb)
    lb_creation_option = test_lib.lib_create_lb_listener_option(lbl_port = 222, lbi_port = 22)
    lbl = lb.create_listener(lb_creation_option)
    lbl.add_nics([vm_nic1_uuid, vm_nic3_uuid])
    lb.check()
    vip1.check()

    test_util.test_dsc('Create ipsec in mevoco1')
    ipsec1 = ipsec_ops.create_ipsec_connection('ipsec1', pri_l3_uuid1, vip2.get_vip().ip, '123456', vip1.get_vip().uuid, [second_zstack_cidrs]) 

    vip1_db = test_lib.lib_get_vip_by_uuid(vip_uuid)
    assert "IPsec" in vip1_db.useFor
    assert vip1_db.useFor.count("IPsec") == 1

    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco2_ip
    test_util.test_dsc('Create ipsec in mevoco2')
    ipsec2 = ipsec_ops.create_ipsec_connection('ipsec2', pri_l3_uuid2, vip1.get_vip().ip, '123456', vip2.get_vip().uuid, [first_zstack_cidrs]) 

    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco1_ip
    if not test_lib.lib_check_ping(vm1.vm, vm2.vm.vmNics[0].ip):
        test_util.test_fail('vm in mevoco1[MN:%s] could not connect to vm in mevoco2[MN:%s]' % (mevoco1_ip, mevoco2_ip))

    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco2_ip
    if not test_lib.lib_check_ping(vm2.vm, vm1.vm.vmNics[0].ip):
        test_util.test_fail('vm in mevoco1[MN:%s] could not connect to vm in mevoco2[MN:%s]' % (mevoco2_ip, mevoco1_ip))
 
    # delete ipsec
    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco1_ip
    ipsec_ops.delete_ipsec_connection(ipsec1.uuid)
    

    if test_lib.lib_check_ping(vm1.vm, vm2.vm.vmNics[0].ip, no_exception=True):
        test_util.test_fail('vm in mevoco1[MN:%s] could still connect to vm in mevoco2[MN:%s] after Ipsec is deleted' % (mevoco1_ip, mevoco2_ip))

    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco2_ip
    if test_lib.lib_check_ping(vm2.vm, vm1.vm.vmNics[0].ip, no_exception=True):
        test_util.test_fail('vm in mevoco2[MN:%s] could still connect to vm in mevoco1[MN:%s] after Ipsec is deleted' % (mevoco2_ip, mevoco1_ip))

    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco1_ip

    vip1_db = test_lib.lib_get_vip_by_uuid(vip_uuid)
    assert "IPsec" not in vip1_db.useFor
    # delete PF
    test_pf1.delete()
    vip1_db = test_lib.lib_get_vip_by_uuid(vip_uuid)
    assert "PortForwarding" not in vip1_db.useFor

    # delete LB
    lb.delete()
    vip1_db = test_lib.lib_get_vip_by_uuid(vip_uuid)
    assert vip1_db.useFor is None

    test_lib.lib_error_cleanup(test_obj_dict1)
    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco2_ip
    ipsec_ops.delete_ipsec_connection(ipsec2.uuid)
    vip2.delete()
    test_lib.lib_error_cleanup(test_obj_dict2)
    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco1_ip
    vip1.delete()
    test_util.test_pass('Create multiple service with 1 snat IP Success')

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

    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco2_ip
    global test_obj_dict2
    test_lib.lib_error_cleanup(test_obj_dict2)

    global ipsec2
    if ipsec2 != None:
        ipsec_ops.delete_ipsec_connection(ipsec2.uuid)
