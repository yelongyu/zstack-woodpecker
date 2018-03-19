'''

Test IPsec connection with 2 snat ip

@author: moyu
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.ipsec_operations as ipsec_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.tag_operations as tag_ops
import zstackwoodpecker.zstack_test.zstack_test_vip as zstack_vip_header
import os
import time
test_lib.TestHarness = test_lib.TestHarnessVR


test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    zstack_pri_name = os.environ['l3VlanDNATNetworkName']
    zstack_image = os.environ['imageName_net']

    zstack_vr_name = os.environ['virtualRouterOfferingName_s']
    cond = res_ops.gen_query_conditions('name', '=', zstack_vr_name)
    zstack_vr_instance = res_ops.query_resource(res_ops.INSTANCE_OFFERING, cond)[0]

    cond = res_ops.gen_query_conditions('name', '=', zstack_pri_name)
    zstack_pri = res_ops.query_resource(res_ops.L3_NETWORK, cond)[0]
    zstack_pri_uuid = zstack_pri.uuid
    zstack_tag = "guestL3Network::" + zstack_pri_uuid
    tag_ops.create_system_tag("InstanceOfferingVO", zstack_vr_instance.uuid, zstack_tag)



    vcenter_pri_name = os.environ['l3vCenterNoVlanNetworkName']
    vcenter_image = os.environ['image_dhcp_name']

    vcenter_vr_name = os.environ['vCenterVirtualRouterOfferingName']
    cond = res_ops.gen_query_conditions('name', '=', vcenter_vr_name)
    vcenter_vr_instance = res_ops.query_resource(res_ops.INSTANCE_OFFERING, cond)[0]

    cond = res_ops.gen_query_conditions('name', '=', vcenter_pri_name)
    vcenter_pri = res_ops.query_resource(res_ops.L3_NETWORK, cond)[0]
    vcenter_pri_uuid = vcenter_pri.uuid
    vcenter_tag = "guestL3Network::" + vcenter_pri_uuid
    tag_ops.create_system_tag("InstanceOfferingVO", vcenter_vr_instance.uuid, vcenter_tag)


    test_util.test_dsc('Create test vm')
    vm1 = test_stub.create_vm(vm_name='test_ipsec_1', image_name = zstack_image, l3_name=zstack_pri_name)
    test_obj_dict.add_vm(vm1)
    vm2 = test_stub.create_vm_in_vcenter(vm_name='test_ipsec_2', image_name = vcenter_image, l3_name=vcenter_pri_name)
    test_obj_dict.add_vm(vm2)
    time.sleep(50)
    
    test_util.test_dsc('Create 2 vip with 2 snat ip')
    pri_l3_uuid1 = vm1.vm.vmNics[0].l3NetworkUuid
    vr1 = test_lib.lib_find_vr_by_l3_uuid(pri_l3_uuid1)[0]
    l3_uuid1 = test_lib.lib_find_vr_pub_nic(vr1).l3NetworkUuid
    vr1_pub_ip = test_lib.lib_find_vr_pub_ip(vr1)
    vip1 = zstack_vip_header.ZstackTestVip()
    vip1.get_snat_ip_as_vip(vr1_pub_ip)
    vip1.isVcenter = True
    test_obj_dict.add_vip(vip1)

    pri_l3_uuid2 = vm2.vm.vmNics[0].l3NetworkUuid
    vr2 = test_lib.lib_find_vr_by_l3_uuid(pri_l3_uuid2)[0]
    l3_uuid2 = test_lib.lib_find_vr_pub_nic(vr2).l3NetworkUuid
    vr2_pub_ip = test_lib.lib_find_vr_pub_ip(vr2)
    vip2 = zstack_vip_header.ZstackTestVip()
    vip2.get_snat_ip_as_vip(vr2_pub_ip)
    vip2.isVcenter = True
    test_obj_dict.add_vip(vip2)

    test_util.test_dsc('Create ipsec with 2 vip')

    zstack_pri_cidr = zstack_pri.ipRanges[0].networkCidr

    vcenter_pri_cidr = vcenter_pri.ipRanges[0].networkCidr

    ipsec1 = ipsec_ops.create_ipsec_connection('zstack_vcenter', pri_l3_uuid1, vip2.get_vip().ip, '123456', vip1.get_vip().uuid, [vcenter_pri_cidr])
    ipsec2 = ipsec_ops.create_ipsec_connection('vcenter_zstack', pri_l3_uuid2, vip1.get_vip().ip, '123456', vip2.get_vip().uuid, [zstack_pri_cidr])
 
    #conditions = res_ops.gen_query_conditions('name', '=', 'test_ipsec_1')
    #vm1 = res_ops.query_resource(res_ops.VM_INSTANCE, conditions)[0]
    #conditions = res_ops.gen_query_conditions('name', '=', 'test_ipsec_2')
    #vm2 = res_ops.query_resource(res_ops.VM_INSTANCE, conditions)[0]

    if not test_lib.lib_check_ping(vm1.vm, vm2.vm.vmNics[0].ip):
        test_util.test_fail('vm1 in zstack could not connect to vm2 in vcenter with IPsec')

    if not test_lib.lib_check_ping(vm2.vm, vm1.vm.vmNics[0].ip):
        test_util.test_fail('vm2 in vcenter could not connect to vm1 in zstack with IPsec')

    ipsec_ops.delete_ipsec_connection(ipsec1.uuid)
    ipsec_ops.delete_ipsec_connection(ipsec2.uuid)
    test_lib.lib_error_cleanup(test_obj_dict)
    test_util.test_pass('Create Ipsec Success')





def error_cleanup():
    pass
