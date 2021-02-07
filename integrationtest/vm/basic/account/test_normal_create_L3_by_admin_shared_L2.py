'''

New Integration Test for normal account create L3 by admin shared L2.

@author: ye.tian 2019-04-20
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
#zstack_management_ip = os.environ.get('zstackManagementIp')
test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
test_account_uuid = None

vm = None

def test():
    global vm, session_uuid
    global test_account_uuid, test_account_session
    
    test_util.test_dsc('Test normal account change the qos network and volume ')
    mn_ip = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].hostName
    zstack_management_ip = mn_ip

    #create normal account
    test_util.test_dsc('create normal account')
    account_name = 'test_a'
    account_pass = hashlib.sha512(account_name).hexdigest()
    test_account = acc_ops.create_normal_account(account_name, account_pass)
    test_account_uuid = test_account.uuid
    test_account_session = acc_ops.login_by_account(account_name, account_pass)

    #create L3 flat network
    test_util.test_dsc('create L2_vlan network  names is L2_vlan')
    zone_uuid = res_ops.query_resource(res_ops.ZONE)[0].uuid
    cluster_uuid = res_ops.query_resource(res_ops.CLUSTER)[0].uuid
    
    l2_inv = sce_ops.create_l2_vlan(zstack_management_ip, 'L2_vlan_2215', 'eth0', '2215', zone_uuid)
    l2_uuid = l2_inv.inventory.uuid

    test_util.test_dsc('attach L2 netowrk to cluster')
    sce_ops.attach_l2(zstack_management_ip, l2_uuid, cluster_uuid)

    #share admin resoure to normal account
    test_util.test_dsc('share admin resoure to normal account')
    cond = res_ops.gen_query_conditions('name', '=', 'L2_vlan_2215')
    flat_l2_uuid = res_ops.query_resource(res_ops.L2_NETWORK, cond)[0].uuid
    acc_ops.share_resources([test_account_uuid], [flat_l2_uuid])

    test_util.test_dsc('create L3_flat_network names is L3_flat_network by normal account')
    l3_inv = sce_ops.create_l3(zstack_management_ip, 'l3_flat_network', 'L3BasicNetwork', l2_uuid, 'local.com', session_uuid = test_account_session)
    l3_uuid = l3_inv.inventory.uuid

    l3_dns = '223.5.5.5'
    start_ip = '192.168.129.2'
    end_ip = '192.168.129.10'
    gateway = '192.168.129.1'
    netmask = '255.255.255.0'

    test_util.test_dsc('add DNS and IP_Range for L3_flat_network')
    sce_ops.add_dns_to_l3(zstack_management_ip, l3_uuid, l3_dns, session_uuid = test_account_session)
    sce_ops.add_ip_range(zstack_management_ip,'IP_range', l3_uuid, start_ip, end_ip, gateway, netmask, session_uuid = test_account_session)

    test_util.test_dsc('query flat provider and attach network service to  L3_flat_network')
    provider_name = 'Flat Network Service Provider'
    conditions = res_ops.gen_query_conditions('name', '=', provider_name)
    net_provider_list = sce_ops.query_resource(zstack_management_ip, res_ops.NETWORK_SERVICE_PROVIDER, conditions, session_uuid = test_account_session).inventories[0]
    pro_uuid = net_provider_list.uuid
    sce_ops.attach_flat_network_service_to_l3network(zstack_management_ip, l3_uuid, pro_uuid, session_uuid = test_account_session)

    instance_offerings = res_ops.get_resource(res_ops.INSTANCE_OFFERING)
    for instance_offering in instance_offerings:
        acc_ops.share_resources([test_account_uuid], [instance_offering.uuid])

    #acc_ops.share_resources([test_account_uuid], [instance_offering_uuid])
    cond = res_ops.gen_query_conditions('mediaType', '!=', 'ISO')
    images = res_ops.query_resource(res_ops.IMAGE, cond)
    for image in images:
        acc_ops.share_resources([test_account_uuid], [image.uuid])

    #create vm
    test_util.test_dsc('create vm by normal account test_a')
    vm = test_stub.create_vm(session_uuid = test_account_session)
    
    vm.check()
    vm.destroy(test_account_session)
    net_ops.delete_l2(l2_uuid)
    vm.check()
    acc_ops.delete_account(test_account_uuid)    
    test_util.test_pass('normal account create eip by admin shared vip Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm, test_account_uuid, test_account_session, l2_uuid 
    if vm:
        vm.destroy(test_account_session)
    acc_ops.delete_account(test_account_uuid)
    net_ops.delete_l2(l2_uuid)
