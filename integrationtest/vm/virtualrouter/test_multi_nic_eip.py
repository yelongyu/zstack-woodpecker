'''
New Integration Test for Multi Nics.

@author: Glody
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.tag_operations as tag_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstacklib.utils.ssh as ssh
import os
import time

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    test_util.test_dsc('Create vrouter vm and check multi nics')
    vm1 = test_stub.create_vlan_vm(os.environ.get('l3VlanNetworkName1'))
    test_obj_dict.add_vm(vm1)
    vm1_ip = vm1.get_vm().vmNics[0].ip
    vm1_nic_uuid = vm1.get_vm().vmNics[0].uuid
    vr1 = test_lib.lib_find_vr_by_vm(vm1.vm)[0]
    vr1_uuid = vr1.uuid
    vr1_pub_ip = test_lib.lib_find_vr_pub_ip(vr1)
    vr1_private_ip = test_lib.lib_find_vr_private_ip(vr1)
    l3network1_uuid = vm1.get_vm().vmNics[0].l3NetworkUuid
    cond = res_ops.gen_query_conditions('uuid', '=', l3network1_uuid)
    l3network1_cidr = res_ops.query_resource(res_ops.L3_NETWORK, cond)[0].ipRanges[0].networkCidr

    cond = res_ops.gen_query_conditions('uuid', '=', vr1_uuid)
    vr_offering_mn_network_uuid = res_ops.query_resource(res_ops.APPLIANCE_VM, cond)[0].managementNetworkUuid
    vr1_pub_uuid = res_ops.query_resource(res_ops.APPLIANCE_VM, cond)[0].managementNetworkUuid
    vr_offering_image_uuid = res_ops.query_resource(res_ops.APPLIANCE_VM, cond)[0].imageUuid
    vr_offering_zone_uuid = res_ops.query_resource(res_ops.APPLIANCE_VM, cond)[0].zoneUuid
    vr1_nics = res_ops.query_resource(res_ops.APPLIANCE_VM, cond)[0].vmNics

    cond = res_ops.gen_query_conditions('name', '=', os.environ.get('l3PublicNetworkName'))
    public_l3network_uuid = res_ops.query_resource(res_ops.L3_NETWORK, cond)[0].uuid
    cond = res_ops.gen_query_conditions('name', '=', os.environ.get('l3NoVlanNetworkName1'))
    second_public_l3network_uuid = res_ops.query_resource(res_ops.L3_NETWORK, cond)[0].uuid
    second_public_l3network_cidr = res_ops.query_resource(res_ops.L3_NETWORK, cond)[0].ipRanges[0].networkCidr

    #Attach second public network to vrouter
    second_public_l3network_attached = False
    for vm_nic in vr1_nics:
        if vm_nic.l3NetworkUuid == second_public_l3network_uuid:
            second_public_l3network_attached = True
    if not second_public_l3network_attached:
        net_ops.attach_l3(second_public_l3network_uuid, vr1_uuid) 

    #Get vr1 nic_uuid on second public network
    cond = res_ops.gen_query_conditions('uuid', '=', vr1_uuid)
    vr1_nics = res_ops.query_resource(res_ops.APPLIANCE_VM, cond)[0].vmNics
    vr1_second_pub_nic_uuid = ''
    for vm_nic in vr1_nics:
        if vm_nic.l3NetworkUuid == second_public_l3network_uuid:
           vr1_second_pub_nic_uuid = vm_nic.uuid
    #Create new vrouter offering
    vr_offering_name = "virtual_router_offering1"
    vr_offering_cpu_num = 2
    vr_offering_mem_size = 536870912 #512MB
    vr_offering = net_ops.create_virtual_router_offering(vr_offering_name, vr_offering_cpu_num, vr_offering_mem_size, vr_offering_image_uuid, vr_offering_zone_uuid, vr_offering_mn_network_uuid, second_public_l3network_uuid)

    vr_offering_uuid = vr_offering.uuid
    cond = res_ops.gen_query_conditions('name', '=', os.environ.get('l3VlanNetworkName4'))
    user_defined_l3network_uuid = res_ops.query_resource(res_ops.L3_NETWORK, cond)[0].uuid

    #Attach Virtual Router Offering
    tag = tag_ops.create_system_tag('InstanceOfferingVO',vr_offering_uuid, 'guestL3Network::%s' % user_defined_l3network_uuid)

    #Create vms for each public network eip attach
    vm2 = test_stub.create_vlan_vm(os.environ.get('l3VlanDNATNetworkName'))
    vm2_ip = vm2.get_vm().vmNics[0].ip
    vm2_nic_uuid = vm2.get_vm().vmNics[0].uuid
    l3network2_uuid = vm2.get_vm().vmNics[0].l3NetworkUuid
    vm3 = test_stub.create_vlan_vm(os.environ.get('l3VlanNetworkName4'))
    vm3_ip = vm3.get_vm().vmNics[0].ip
    vm3_nic_uuid = vm3.get_vm().vmNics[0].uuid
    l3network3_uuid = vm3.get_vm().vmNics[0].l3NetworkUuid    

    #Create eip for each vms, vm1 has 2 eip on each public network
    vip11 = test_stub.create_vip('vm1_vip1', public_l3network_uuid)
    vip11_uuid = vip11.get_vip().uuid
    eip11 = test_stub.create_eip('vm1_eip1', vip11_uuid, vm_obj=vm1)
    vip11.attach_eip(eip11)
    eip11_pub_ip = eip11.get_eip().vipIp
    vip11.check()
    eip11.attach(vm1_nic_uuid, vm1)
    vip12 = test_stub.create_vip('vm1_vip2', second_public_l3network_uuid)
    vip12_uuid = vip12.get_vip().uuid
    eip12 = test_stub.create_eip('vm1_eip2', vip12_uuid, vm_obj=vm1)
    vip12.attach_eip(eip12)
    eip12_pub_ip = eip12.get_eip().vipIp
    vip12.check()
    eip12.attach(vm1_nic_uuid, vm1)
    vip2 = test_stub.create_vip('vm2_vip', public_l3network_uuid)
    vip2_uuid = vip2.get_vip().uuid
    eip2 = test_stub.create_eip('vm2_eip', vip2_uuid, vm_obj=vm2)
    vip2.attach_eip(eip2)
    eip2_pub_ip = eip2.get_eip().vipIp
    vip2.check()
    eip2.attach(vm2_nic_uuid, vm2)
    vip3 = test_stub.create_vip('vm3_vip', second_public_l3network_uuid)
    vip3_uuid = vip3.get_vip().uuid
    eip3 = test_stub.create_eip('vm3_eip', vip3_uuid, vm_obj=vm3)
    vip3.attach_eip(eip3)
    eip3_pub_ip = eip3.get_eip().vipIp
    vip3.check()
    eip3.attach(vm3_nic_uuid, vm3)
    
    time.sleep(20) #waiting for eip binding

    #Check if the network is able to ping with eip
    user_name = "root"
    user_password = "password"
    rsp_ping = os.system("sshpass -p '%s' ssh %s@%s 'ping -c 4 %s'"%(user_password, user_name, vm1_ip, eip2_pub_ip))
    if rsp_ping != 0:
        test_util.test_fail('Exception: [vm ip:] %s ping [Eip:] %s fail. But it should ping successfully.' % (vm1_ip, eip2_pub_ip))
    rsp_ping = os.system("sshpass -p '%s' ssh %s@%s 'ping -c 4 %s'"%(user_password, user_name, vm1_ip, eip3_pub_ip))
    if rsp_ping != 0:
        test_util.test_fail('Exception: [vm ip:] %s ping [Eip:] %s fail. But it should ping successfully.' % (vm1_ip, eip3_pub_ip))
    rsp_ping = os.system("sshpass -p '%s' ssh %s@%s 'ping -c 4 %s'"%(user_password, user_name, vm2_ip, eip11_pub_ip))
    if rsp_ping != 0:
        test_util.test_fail('Exception: [vm ip:] %s ping [Eip:] %s fail. But it should ping successfully.' % (vm2_ip, eip11_pub_ip))
    rsp_ping = os.system("sshpass -p '%s' ssh %s@%s 'ping -c 4 %s'"%(user_password, user_name, vm3_ip, eip12_pub_ip))
    if rsp_ping != 0:
        test_util.test_fail('Exception: [vm ip:] %s ping [Eip:] %s fail. But it should ping successfully.' % (vm3_ip, eip12_pub_ip))

    #Delete vips and vr offering
    vip11.delete()
    vip12.delete()
    vip2.delete()
    vip3.delete()
    vm_ops.delete_instance_offering(vr_offering_uuid)

    #Dettach the route table to vrouter and second public nework
    if vr1_second_pub_nic_uuid != '':
        net_ops.detach_l3(vr1_second_pub_nic_uuid)

    vm1.destroy()
    vm2.destroy()
    vm3.destroy()
    net_ops.destroy_vrouter(vr1_uuid)
    test_util.test_pass('Check Multi Nics Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
