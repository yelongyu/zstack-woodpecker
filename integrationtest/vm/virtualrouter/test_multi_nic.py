'''
New Integration Test for Multi Nics.

@author: Glody
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstacklib.utils.ssh as ssh
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    test_util.test_dsc('Create vrouter vm and check multi nics')
    vm1 = test_stub.create_vlan_vm(os.environ.get('l3VlanNetworkName1'))
    test_obj_dict.add_vm(vm1)
    vm1_ip = vm1.get_vm().vmNics[0].ip
    vr1 = test_lib.lib_find_vr_by_vm(vm1.vm)[0]
    vr1_uuid = vr1.uuid
    vr1_pub_ip = test_lib.lib_find_vr_pub_ip(vr1)
    vr1_private_ip = test_lib.lib_find_vr_private_ip(vr1)
    l3network1_uuid = vm1.get_vm().vmNics[0].l3NetworkUuid
    cond = res_ops.gen_query_conditions('uuid', '=', l3network1_uuid)
    l3network1_cidr = res_ops.query_resource(res_ops.L3_NETWORK, cond)[0].ipRanges[0].networkCidr

    cond = res_ops.gen_query_conditions('name', '=', 'l3_user_defined_vlan1')
    second_public_l3network_uuid = res_ops.query_resource(res_ops.L3_NETWORK, cond)[0].uuid
    second_public_l3network_cidr = res_ops.query_resource(res_ops.L3_NETWORK, cond)[0].ipRanges[0].networkCidr
    net_ops.attach_l3(second_public_l3network_uuid, vr1_uuid) 

    cond = res_ops.gen_query_conditions('l3NetworkUuid', '=', second_public_l3network_uuid)
    second_nic_ip = res_ops.query_resource(res_ops.VM_NIC, cond)[0].ip    
    second_nic_uuid =  res_ops.query_resource(res_ops.VM_NIC, cond)[0].uuid
   
    #Attach the network service to l3 network
    cond = res_ops.gen_query_conditions('type', '=', 'vrouter')
    service_uuid = res_ops.query_resource(res_ops.NETWORK_SERVICE_PROVIDER, cond)[0].uuid
    network_services_json = "{'%s':['VRouterRoute']}"% service_uuid
    net_ops.detach_network_service_from_l3network(l3network1_uuid, service_uuid)
    net_ops.attach_network_service_to_l3network(l3network1_uuid, service_uuid)
    net_ops.detach_network_service_from_l3network(second_public_l3network_uuid, service_uuid)
    net_ops.attach_network_service_to_l3network(second_public_l3network_uuid, service_uuid)

    #Create route table and route entry for each vrouter
    route_table1 = net_ops.create_vrouter_route_table('route_table1')
    route_table1_uuid = route_table1.uuid
    route_entry1 = net_ops.add_vrouter_route_entry(route_table1_uuid, second_public_l3network_cidr, second_nic_ip)

    #Attach the route table to vrouter and check the network
    #net_ops.detach_vrouter_route_table_from_vrouter(route_table1_uuid, vr1_uuid)
    net_ops.attach_vrouter_route_table_to_vrouter(route_table1_uuid, vr1_uuid)

    #Add vroute private ip to vm route
    cmd = 'ip r del default; ip r add default via %s' %vr1_private_ip
    rsp = test_lib.lib_execute_ssh_cmd(vm1_ip, 'root', 'password', cmd, 180)

    #Dettach the route table to vrouter and check the network
    #net_ops.detach_vrouter_route_table_from_vrouter(route_table1_uuid, vr1_uuid)

    #net_ops.detach_l3(nic_uuid)

    #vm1.check()

    #vm1.destroy()
    test_util.test_pass('Check Multi Nics Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
