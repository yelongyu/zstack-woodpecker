'''
Test for sync vcenter after adding host to vcenter cluster and add portgroup

@author:
'''
import apibinding.inventory as inventory
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.vcenter_operations as vct_ops
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.operations.deploy_operations as deploy_operations
import test_stub

import os
import time

portgroup = []
vswitch = []


def test():
    global portgroup
    global vswitch

    vcenter = os.environ.get('vcenter')
    SI = vct_ops.connect_vcenter(vcenter)
    content = SI.RetrieveContent()
    vc_cluster = vct_ops.get_cluster(content)[0]
    #add host to vcenter cluster
    host_name = os.environ.get('hostName4')
    managementIp = deploy_operations.get_host_from_scenario_file(host_name, test_lib.all_scenario_config, test_lib.scenario_file,test_lib.deploy_config)
    vc_host = vct_ops.add_host(vc_cluster, managementIp)
    #add vswitch and portgroup
    vswitch1 = vct_ops.add_vswitch(vc_host, 'vSwitch1')
    vswitch.append('vSwitch1')
    for port_group in ['port_group0', 'port_group1', 'port_group2', 'port_group3']:
        vct_ops.add_portgroup(vc_host, 'vSwitch0', port_group)
        portgroup.append(port_group)

    #sync vcenter
    vcenter_uuid = vct_ops.lib_get_vcenter_by_name(vcenter).uuid
    vct_ops.sync_vcenter(vcenter_uuid)
    time.sleep(5)

    #check
    assert managementIp == vct_ops.lib_get_vcenter_host_by_ip(managementIp).name
    assert vct_ops.lib_get_vcenter_host_by_ip(managementIp).hypervisorType == "ESX"

    assert 'port_group0' == vct_ops.lib_get_vcenter_l2_by_name('port_group0').name
    assert "L3-" + 'port_group0' == vct_ops.lib_get_vcenter_l3_by_name("L3-" +'port_group0' ).name
    vct_ops.remove_portgroup(vc_host, 'port_group0')
    portgroup.remove('port_group0')
    for port_group in portgroup:
        assert vct_ops.lib_get_vcenter_l2_by_name(port_group) == None

    vct_ops.add_portgroup(vc_host, 'vSwitch1', 'port_group0',0)
    vct_ops.sync_vcenter(vcenter_uuid)
    time.sleep(5)

    assert vct_ops.lib_get_vcenter_l2_by_name('port_group0') == None

    #cleanup
    vct_ops.remove_vswitch(vc_host,'vSwitch1')
    for name in portgroup:
        vct_ops.remove_portgroup(vc_host, name)
    vct_ops.remove_host(vc_host)

    #recover the test environment
    vc_origin_host = vct_ops.get_host(content)[0]
    #delete the virtualrouter network corresponding portgroups
    vct_ops.remove_portgroup(vc_origin_host, name=os.environ['l2vCenterPublicNetworkName'])
    vct_ops.remove_portgroup(vc_origin_host, name=os.environ['l2vCenterNoVlanNetworkName'])
    vct_ops.sync_vcenter(vcenter_uuid)
    #recover virtualrouter network
    deploy_operations.add_vcenter_l2l3_network(test_lib.all_scenario_config, test_lib.scenario_file,test_lib.deploy_config, acc_ops.login_as_admin())
    deploy_operations.add_vcenter_vrouter(test_lib.all_scenario_config, test_lib.scenario_file,test_lib.deploy_config, acc_ops.login_as_admin())
    vct_ops.sync_vcenter(vcenter_uuid)

    test_util.test_pass('Sync vcenter after adding host to vcenter cluster and add portgroup successfully')


def error_cleanup():
    global portgroup
    global vswitch
    for name in portgroup:
        vct_ops.remove_portgroup(vc_host, name)
    for name in vswitch:
        vct_ops.remove_vswitch(vc_host, name)
