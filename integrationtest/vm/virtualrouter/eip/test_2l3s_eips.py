'''
    Test Description:
        Will create 1 VM with 2 l3 networks. Assign 2 vip and 2 eips to each l3.


@author: Youyk
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import apibinding.inventory as inventory
import zstackwoodpecker.operations.config_operations as conf_ops

import os

_config_ = {
        'timeout' : 1000,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
eip_snatInboundTraffic_default_value = None
pf_snatInboundTraffic_default_value = None

def test():
    global eip_snatInboundTraffic_default_value
    global pf_snatInboundTraffic_default_value
    #enable snatInboundTraffic and save global config value
    eip_snatInboundTraffic_default_value = \
            conf_ops.change_global_config('eip', 'snatInboundTraffic', 'true')
    pf_snatInboundTraffic_default_value = \
            conf_ops.change_global_config('portForwarding', \
            'snatInboundTraffic', 'true')

    image_name = os.environ.get('imageName_net')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    l3_name = os.environ.get('l3VlanNetworkName1')
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    l3_net_list = [l3_net_uuid]
    l3_name = os.environ.get('l3VlanDNATNetworkName')
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    l3_net_list.append(l3_net_uuid)

    vm = test_stub.create_vm(l3_net_list, image_uuid, '2_l3_pf_vm')
    test_obj_dict.add_vm(vm)

    l3_name = os.environ.get('l3NoVlanNetworkName1')
    vr_l3_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    vrs = test_lib.lib_find_vr_by_l3_uuid(vr_l3_uuid)
    temp_vm1 = None
    if not vrs:
        #create temp_vm2 for getting novlan's vr for test pf_vm portforwarding
        temp_vm1 = test_stub.create_user_vlan_vm()
        test_obj_dict.add_vm(temp_vm1)
        vr1 = test_lib.lib_find_vr_by_vm(temp_vm1.vm)[0]
    else:
        vr1 = vrs[0]

    #we do not need temp_vm1, since we just use their VRs.
    if temp_vm1:
        temp_vm1.destroy()
        test_obj_dict.rm_vm(temp_vm1)

    vr1_pub_ip = test_lib.lib_find_vr_pub_ip(vr1)
    
    vm.check()

    vm_nic1 = vm.vm.vmNics[0]
    vm_nic1_uuid = vm_nic1.uuid
    vm_nic2 = vm.vm.vmNics[1]
    vm_nic2_uuid = vm_nic2.uuid
    pri_l3_uuid = vm_nic1.l3NetworkUuid
    vr = test_lib.lib_find_vr_by_l3_uuid(pri_l3_uuid)[0]
    vr_pub_nic = test_lib.lib_find_vr_pub_nic(vr)
    l3_uuid = vr_pub_nic.l3NetworkUuid
    vip1 = test_stub.create_vip('vip1_2l3s_vm_test', l3_uuid)
    test_obj_dict.add_vip(vip1)
    vip1_uuid = vip1.get_vip().uuid
    vip2 = test_stub.create_vip('vip2_2l3s_vm_test', l3_uuid)
    test_obj_dict.add_vip(vip2)
    vip2_uuid = vip2.get_vip().uuid

    eip1 = test_stub.create_eip('2l3 eip test1', vip_uuid=vip1.get_vip().uuid)
    vip1.attach_eip(eip1)
    vip1.check()
    eip1.attach(vm_nic1_uuid, vm)
    vip1.check()

    eip2 = test_stub.create_eip('2l3 eip test2', vip_uuid=vip2.get_vip().uuid)
    vip2.attach_eip(eip2)
    vip2.check()
    eip2.attach(vm_nic2_uuid, vm)
    vip2.check()

    vm.stop()
    vm.start()

    vm.check()
    vip1.check()
    vip2.check()

    eip1.detach()
    eip2.detach()

    vip1.check()
    vip2.check()

    vip1.delete()
    test_obj_dict.rm_vip(vip1)
    vip2.delete()
    test_obj_dict.rm_vip(vip2)
    vm.destroy()
    test_obj_dict.rm_vm(vm)
    conf_ops.change_global_config('eip', 'snatInboundTraffic', \
            eip_snatInboundTraffic_default_value )
    conf_ops.change_global_config('portForwarding', 'snatInboundTraffic', \
            pf_snatInboundTraffic_default_value)
    test_util.test_pass('Create 1 VM with 2 l3_network with 2 VIP PF testing successfully.')

#Will be called only if exception happens in test().
def error_cleanup():
    global eip_snatInboundTraffic_default_value
    global pf_snatInboundTraffic_default_value
    conf_ops.change_global_config('eip', 'snatInboundTraffic', \
            eip_snatInboundTraffic_default_value )
    conf_ops.change_global_config('portForwarding', 'snatInboundTraffic', \
            pf_snatInboundTraffic_default_value)
    test_lib.lib_error_cleanup(test_obj_dict)
