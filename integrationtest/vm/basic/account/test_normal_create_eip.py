'''

New Integration Test for normal account create eip by admin shared vip.

@author: ye.tian 2018-11-29
'''

import hashlib
import zstackwoodpecker.test_util as test_util
import os
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.operations.scenario_operations as sce_ops
import zstackwoodpecker.operations.net_operations as net_ops

_config_ = {
        'timeout' : 2000,
        'noparallel' : True
        }
zstack_management_ip = os.environ.get('zstackManagementIp')
test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
test_account_uuid = None

vm = None

def test():
    global vm, session_uuid
    global test_account_uuid, test_account_session
    
    test_util.test_dsc('Test normal account change the qos network and volume ')

    #create normal account
    test_util.test_dsc('create normal account')
    account_name = 'a'
    account_pass = hashlib.sha512(account_name).hexdigest()
    test_account = acc_ops.create_normal_account(account_name, account_pass)
    test_account_uuid = test_account.uuid
    test_account_session = acc_ops.login_by_account(account_name, account_pass)

    #create L3 flat network
    test_util.test_dsc('create L2_vlan network  names is L2_vlan')
    zone_uuid = res_ops.query_resource(res_ops.ZONE)[0].uuid
    cluster_uuid = res_ops.query_resource(res_ops.CLUSTER)[0].uuid
    
    l2_inv = sce_ops.create_l2_vlan(zstack_management_ip, 'L2_vlan', 'eth0', '2205', zone_uuid)
    l2_uuid = l2_inv.inventory.uuid

    test_util.test_dsc('attach L2 netowrk to cluster')
    sce_ops.attach_l2(zstack_management_ip, l2_uuid, cluster_uuid)

    test_util.test_dsc('create L3_flat_network names is L3_flat_network')
    l3_inv = sce_ops.create_l3(zstack_management_ip, 'l3_flat_network', 'L3BasicNetwork', l2_uuid, 'local.com')
    l3_uuid = l3_inv.inventory.uuid

    l3_dns = '223.5.5.5'
    start_ip = '192.168.109.2'
    end_ip = '192.168.109.10'
    gateway = '192.168.109.1'
    netmask = '255.255.255.0'

    test_util.test_dsc('add DNS and IP_Range for L3_flat_network')
    sce_ops.add_dns_to_l3(zstack_management_ip, l3_uuid, l3_dns)
    sce_ops.add_ip_range(zstack_management_ip,'IP_range', l3_uuid, start_ip, end_ip, gateway, netmask)

    test_util.test_dsc('query flat provider and attach network service to  L3_flat_network')
    provider_name = 'Flat Network Service Provider'
    conditions = res_ops.gen_query_conditions('name', '=', provider_name)
    net_provider_list = sce_ops.query_resource(zstack_management_ip, res_ops.NETWORK_SERVICE_PROVIDER, conditions).inventories[0]
    pro_uuid = net_provider_list.uuid
    sce_ops.attach_flat_network_service_to_l3network(zstack_management_ip, l3_uuid, pro_uuid)
    
    l2_inv2 = sce_ops.create_l2_vlan(zstack_management_ip, 'L2_vlan_2206', 'eth0', '2206', zone_uuid)
    l2_uuid2 = l2_inv2.inventory.uuid

    test_util.test_dsc('attach L2 netowrk to cluster')
    sce_ops.attach_l2(zstack_management_ip, l2_uuid2, cluster_uuid)

    test_util.test_dsc('create L3_flat_network names is L3_flat_network')
    l3_inv2 = sce_ops.create_l3(zstack_management_ip, 'l3_flat_2', 'L3BasicNetwork', l2_uuid2, 'local.com')
    l3_uuid2 = l3_inv2.inventory.uuid

    l3_dns2 = '223.5.5.5'
    start_ip2 = '192.168.110.2'
    end_ip2 = '192.168.110.10'
    gateway2 = '192.168.110.1'
    netmask2 = '255.255.255.0'

    test_util.test_dsc('add DNS and IP_Range for L3_flat_network')
    sce_ops.add_dns_to_l3(zstack_management_ip, l3_uuid2, l3_dns2)
    sce_ops.add_ip_range(zstack_management_ip,'IP_range2', l3_uuid2, start_ip2, end_ip2, gateway2, netmask2)

    test_util.test_dsc('query flat provider and attach network service to  L3_flat_network')
    provider_name = 'Flat Network Service Provider'
    conditions = res_ops.gen_query_conditions('name', '=', provider_name)
    net_provider_list = sce_ops.query_resource(zstack_management_ip, res_ops.NETWORK_SERVICE_PROVIDER, conditions).inventories[0]
    pro_uuid = net_provider_list.uuid
    sce_ops.attach_flat_network_service_to_l3network(zstack_management_ip, l3_uuid2, pro_uuid)
    
    #share admin resoure to normal account
    test_util.test_dsc('share admin resoure to normal account')
    cond = res_ops.gen_query_conditions('name', '=', 'l3_flat_network')
    flat_uuid = res_ops.query_resource(res_ops.L3_NETWORK, cond)[0].uuid
    acc_ops.share_resources([test_account_uuid], [flat_uuid])

    instance_offerings = res_ops.get_resource(res_ops.INSTANCE_OFFERING)
    for instance_offering in instance_offerings:
        acc_ops.share_resources([test_account_uuid], [instance_offering.uuid])

    #acc_ops.share_resources([test_account_uuid], [instance_offering_uuid])
    cond = res_ops.gen_query_conditions('mediaType', '!=', 'ISO')
    images = res_ops.query_resource(res_ops.IMAGE, cond)
    for image in images:
        acc_ops.share_resources([test_account_uuid], [image.uuid])

    #create vm
    test_util.test_dsc('create vm by normal account a')
    vm = test_stub.create_vm(session_uuid = test_account_session)
    vm_inv = vm.get_vm()
    vm_nic = vm.vm.vmNics[0]
    vm_nic_uuid = vm_nic.uuid

    vip = test_stub.create_vip('vip', l3_uuid2)
    res_ops.change_recource_owner(test_account_uuid, vip.vip.uuid)
    eip = test_stub.create_eip('eip_a', vip_uuid=vip.vip.uuid, session_uuid = test_account_session)

    net_ops.attach_eip(eip.eip.uuid, vm_nic_uuid, session_uuid = test_account_session)
    net_ops.detach_eip(eip.eip.uuid, session_uuid = test_account_session)
    net_ops.delete_eip(eip.eip.uuid, session_uuid = test_account_session)
    
    vip.delete()
    vm.check()
    vm.destroy(test_account_session)
    net_ops.delete_l2(l2_uuid)
    net_ops.delete_l2(l2_uuid2)
    vm.check()
    acc_ops.delete_account(test_account_uuid)    
    test_util.test_pass('normal account create eip by admin shared vip Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm, test_account_uuid, test_account_session, vip, eip, l2_uuid, l2_uuid
    if vm:
        vm.destroy(test_account_session)
    acc_ops.delete_account(test_account_uuid)
    vip.delete()
    net_ops.delete_eip(eip.eip.uuid, session_uuid = test_account_session)
    net_ops.delete_l2(l2_uuid)
    net_ops.delete_l2(l2_uuid2)
