'''

Test EIP with TCP connection and SG rule coexist

@author: Youyk
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.operations.config_operations as conf_ops
import zstackwoodpecker.zstack_test.zstack_test_sg_vm as zstack_sg_vm_header
import apibinding.inventory as inventory

import os

_config_ = {
        'timeout' : 1000,
        'noparallel' : True
        }

Port = test_state.Port
test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
eip_snatInboundTraffic_default_value = None
pf_snatInboundTraffic_default_value = None

def test():
    global eip_snatInboundTraffic_default_value
    global pf_snatInboundTraffic_default_value
    vm = test_stub.create_dnat_vm()
    test_obj_dict.add_vm(vm)

    #disable snatInboundTraffic and save global config value
    eip_snatInboundTraffic_default_value = \
            conf_ops.change_global_config('eip', 'snatInboundTraffic', 'false')
    pf_snatInboundTraffic_default_value = \
            conf_ops.change_global_config('portForwarding', \
            'snatInboundTraffic', 'false')

    l3_name = os.environ.get('l3VlanNetworkName1')
    vr1_l3_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    vrs = test_lib.lib_find_vr_by_l3_uuid(vr1_l3_uuid)
    temp_vm1 = None
    if not vrs:
        #create temp_vm1 for getting vlan1's vr for test vm portforwarding
        temp_vm1 = test_stub.create_vlan_vm()
        test_obj_dict.add_vm(temp_vm1)
        vr1 = test_lib.lib_find_vr_by_vm(temp_vm1.vm)[0]
    else:
        vr1 = vrs[0]

    l3_name = os.environ.get('l3NoVlanNetworkName1')
    vr2_l3_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    vrs = test_lib.lib_find_vr_by_l3_uuid(vr2_l3_uuid)
    temp_vm2 = None
    if not vrs:
        #create temp_vm2 for getting novlan's vr for test vm portforwarding
        temp_vm2 = test_stub.create_user_vlan_vm()
        test_obj_dict.add_vm(temp_vm2)
        vr2 = test_lib.lib_find_vr_by_vm(temp_vm2.vm)[0]
    else:
        vr2 = vrs[0]

    if temp_vm1:
        temp_vm1.destroy()
        test_obj_dict.rm_vm(temp_vm1)
    if temp_vm2:
        temp_vm2.destroy()
        test_obj_dict.rm_vm(temp_vm2)

    vr1_pub_ip = test_lib.lib_find_vr_pub_ip(vr1)
    vr2_pub_ip = test_lib.lib_find_vr_pub_ip(vr2)
    
    vm.check()

    vm_nic = vm.vm.vmNics[0]
    vm_nic_uuid = vm_nic.uuid
    pri_l3_uuid = vm_nic.l3NetworkUuid
    vr = test_lib.lib_find_vr_by_l3_uuid(pri_l3_uuid)[0]
    vr_pub_nic = test_lib.lib_find_vr_pub_nic(vr)
    l3_uuid = vr_pub_nic.l3NetworkUuid
    vip = test_stub.create_vip('eip_sg_test', l3_uuid)
    test_obj_dict.add_vip(vip)
    vip_uuid = vip.get_vip().uuid

    eip = test_stub.create_eip('eip sg test', vip_uuid, vm_nic_uuid, vm)
    vip.attach_eip(eip)

    sg1 = test_stub.create_sg()
    test_obj_dict.add_sg(sg1.security_group.uuid)
    sg_vm = zstack_sg_vm_header.ZstackTestSgVm()
    sg_vm.check()

    vm_nics = (vm_nic_uuid, vm)
    rule1 = test_lib.lib_gen_sg_rule(Port.rule1_ports, inventory.TCP, inventory.INGRESS, vr1_pub_ip)
    rule2 = test_lib.lib_gen_sg_rule(Port.rule2_ports, inventory.TCP, inventory.INGRESS, vr2_pub_ip)
    sg1.add_rule([rule1])

    test_util.test_dsc("Add nic to security group 1.")
    test_util.test_dsc("EIP connection is allowed from VR1, but denied from VR2.")
    sg_vm.attach(sg1, [vm_nics])
    vip.check()

    test_util.test_dsc("Remove rule1 from security group 1.")
    test_util.test_dsc("EIP is still allowed from all VR")
    sg1.delete_rule([rule1])
    vip.check()

    test_util.test_dsc("Add rule2")
    test_util.test_dsc("EIP is not allowed by VR2, VR1 is allowed. ")
    sg1.add_rule([rule2])
    vip.check()

    test_util.test_dsc("Delete SG")
    sg_vm.delete_sg(sg1)
    test_util.test_dsc("PF rule is allowed")
    vip.check()

    vm.destroy()
    test_obj_dict.rm_vm(vm)
    vip.check()
    eip.delete()

    vip.delete()
    test_obj_dict.rm_vip(vip)
    conf_ops.change_global_config('eip', 'snatInboundTraffic', \
            eip_snatInboundTraffic_default_value )
    conf_ops.change_global_config('portForwarding', 'snatInboundTraffic', \
            pf_snatInboundTraffic_default_value)

    test_util.test_pass("Test EIP and SG coexistance Successfully")

#Will be called only if exception happens in test().
def error_cleanup():
    global eip_snatInboundTraffic_default_value
    global pf_snatInboundTraffic_default_value
    conf_ops.change_global_config('eip', 'snatInboundTraffic', \
            eip_snatInboundTraffic_default_value )
    conf_ops.change_global_config('portForwarding', 'snatInboundTraffic', \
            pf_snatInboundTraffic_default_value)
    test_lib.lib_error_cleanup(test_obj_dict)
