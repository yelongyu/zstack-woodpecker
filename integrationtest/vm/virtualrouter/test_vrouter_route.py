'''
New Integration Test for VRouterRoute and VRouterRouteTable.

@author: Glody
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    test_util.test_dsc('Check vm connection with vrouter route')
    vm1 = test_stub.create_vlan_vm(os.environ.get('l3VlanNetworkName1'))
    test_obj_dict.add_vm(vm1)
    vm1_ip = vm1.get_vm().vmNics[0].ip
    vr1 = test_lib.lib_find_vr_by_vm(vm1.vm)[0]
    vr1_uuid = vr1.uuid
    vr1_mgmt_ip = test_lib.lib_find_vr_mgmt_ip(vr1)
    l3network1_uuid = vm1.get_vm().vmNics[0].l3NetworkUuid
    cond = res_ops.gen_query_conditions('uuid', '=', l3network1_uuid)
    l3network1_cidr = res_ops.query_resource(res_ops.L3_NETWORK, cond)[0].ipRanges[0].networkCidr
    vm2 = test_stub.create_vlan_vm(os.environ.get('l3VlanNetworkName3'))
    test_obj_dict.add_vm(vm2)
    vm2_ip = vm2.get_vm().vmNics[0].ip
    vr2 = test_lib.lib_find_vr_by_vm(vm2.vm)[0]
    vr2_uuid = vr2.uuid
    vr2_mgmt_ip = test_lib.lib_find_vr_mgmt_ip(vr2)
    l3network2_uuid = vm2.get_vm().vmNics[0].l3NetworkUuid
    cond = res_ops.gen_query_conditions('uuid', '=', l3network2_uuid)
    l3network2_cidr = res_ops.query_resource(res_ops.L3_NETWORK, cond)[0].ipRanges[0].networkCidr

    vm1.check()
    vm2.check()

    #Attach the network service to l3 network
    cond = res_ops.gen_query_conditions('type', '=', 'vrouter')
    service_uuid = res_ops.query_resource(res_ops.NETWORK_SERVICE_PROVIDER, cond)[0].uuid
    network_services_json = "{'%s':['VRouterRoute']}"% service_uuid
    net_ops.detach_network_service_from_l3network(l3network1_uuid, service_uuid)
    net_ops.attach_network_service_to_l3network(l3network1_uuid, service_uuid)
    net_ops.detach_network_service_from_l3network(l3network2_uuid, service_uuid)
    net_ops.attach_network_service_to_l3network(l3network2_uuid, service_uuid)

    #Create route table and route entry for each vrouter
    route_table1 = net_ops.create_vrouter_route_table('route_table1')
    route_entry1 = net_ops.add_vrouter_route_entry(route_table1.uuid, l3network2_cidr, vr2_mgmt_ip)
    route_table2 = net_ops.create_vrouter_route_table('route_table2')
    route_entry2 = net_ops.add_vrouter_route_entry(route_table2.uuid, l3network1_cidr, vr1_mgmt_ip)

    #Attach the route table to vrouter and check the network
    #net_ops.detach_vrouter_route_table_from_vrouter(route_table1.uuid, vr1_uuid)
    net_ops.attach_vrouter_route_table_to_vrouter(route_table1.uuid, vr1_uuid)
    #net_ops.detach_vrouter_route_table_from_vrouter(route_table2.uuid, vr2_uuid)
    net_ops.attach_vrouter_route_table_to_vrouter(route_table2.uuid, vr2_uuid)
    if not test_lib.lib_check_ping(vm1.vm, vm2_ip, no_exception=True):
        test_util.test_fail('Exception: [vm:] %s ping [vr:] %s fail. But it should ping successfully.' % (vm1.vm.uuid, vm2_ip))
    if not test_lib.lib_check_ping(vm1.vm, vr_internal_ip, no_exception=True):
        test_util.test_fail('Exception: [vm:] %s ping [vr:] %s fail. But it should ping successfully.' % (vm2.vm.uuid, vm1_ip))

    #Dettach the route table to vrouter and check the network
    net_ops.detach_vrouter_route_table_from_vrouter(route_table1.uuid, vr1_uuid)
    if test_lib.lib_check_ping(vm1.vm, vm2_ip, no_exception=True):
        test_util.test_fail('Exception: [vm:] %s ping [vr:] %s successfully. But it should ping fail because the route table is detached.' % (vm1.vm.uuid, vm2_ip))
    net_ops.detach_vrouter_route_table_from_vrouter(route_table2.uuid, vr2_uuid)
    if test_lib.lib_check_ping(vm1.vm, vm2_ip, no_exception=True):
        test_util.test_fail('Exception: [vm:] %s ping [vr:] %s successfully. But it should ping fail because the route table is detached.' % (vm2.vm.uuid, vm1_ip))

    #Delete route entry and table, and distory vm
    net_ops.delete_vrouter_route_entry(route_entry1.uuid)
    net_ops.delete_vrouter_route_entry(route_entry2.uuid)
    net_ops.delete_vrouter_route_table(route_table1.uuid)
    net_ops.delete_vrouter_route_table(route_table2.uuid)
    vm1.destroy()
    vm2.destroy()
    test_util.test_pass('Check VRouter route Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
