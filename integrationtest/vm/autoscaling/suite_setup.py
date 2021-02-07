'''
setup virtual router suite environment, including start zstack node, deploy
initial database, setup vlan devices.


@author: Frank
'''
import os
import zstacklib.utils.linux as linux
import zstacklib.utils.http as  http
import zstacktestagent.plugins.host as host_plugin
import zstacktestagent.testagent as testagent

import zstackwoodpecker.operations.scenario_operations as scenario_operations
import zstackwoodpecker.operations.deploy_operations as deploy_operations
import zstackwoodpecker.operations.config_operations as config_operations
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.config_operations as conf_ops
import zstackwoodpecker.zstack_test.zstack_test_load_balancer as zstack_lb_header

USER_PATH = os.path.expanduser('~')
EXTRA_SUITE_SETUP_SCRIPT = '%s/.zstackwoodpecker/extra_suite_setup_config.sh' % USER_PATH
EXTRA_HOST_SETUP_SCRIPT = '%s/.zstackwoodpecker/extra_host_setup_config.sh' % USER_PATH
test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
def test():
    if test_lib.scenario_config != None and test_lib.scenario_file != None and not os.path.exists(test_lib.scenario_file):
        scenario_operations.deploy_scenario(test_lib.all_scenario_config, test_lib.scenario_file, test_lib.deploy_config)
        test_util.test_skip('Suite Setup Success')
    if test_lib.scenario_config != None and test_lib.scenario_destroy != None:
        scenario_operations.destroy_scenario(test_lib.all_scenario_config, test_lib.scenario_destroy)

    nic_name = "eth0"
    if test_lib.scenario_config != None and test_lib.scenario_file != None and os.path.exists(test_lib.scenario_file):
        nic_name = "zsn0"
        linux.create_vlan_eth(nic_name, 1010)
        linux.create_vlan_eth(nic_name, 1011)
    #This vlan creation is not a must, if testing is under nested virt env. But it is required on physical host without enough physcial network devices and your test execution machine is not the same one as Host machine. 
    #linux.create_vlan_eth("eth0", 10, "10.0.0.200", "255.255.255.0")
    #linux.create_vlan_eth("eth0", 11, "10.0.1.200", "255.255.255.0")
    #no matter if current host is a ZStest host, we need to create 2 vlan devs for future testing connection for novlan test cases.
    linux.create_vlan_eth(nic_name, 10)
    linux.create_vlan_eth(nic_name, 11)
    #If test execution machine is not the same one as Host machine, deploy work is needed to separated to 2 steps(deploy_test_agent, execute_plan_without_deploy_test_agent). And it can not directly call SetupAction.run()
    test_lib.setup_plan.deploy_test_agent()
    cmd = host_plugin.CreateVlanDeviceCmd()
    
    hosts = test_lib.lib_get_all_hosts_from_plan()
    if type(hosts) != type([]):
        hosts = [hosts]
    for host in hosts:
        cmd.ethname = nic_name
        cmd.vlan = 10
        http.json_dump_post(testagent.build_http_path(host.managementIp_, host_plugin.CREATE_VLAN_DEVICE_PATH), cmd)
        cmd.vlan = 11
        http.json_dump_post(testagent.build_http_path(host.managementIp_, host_plugin.CREATE_VLAN_DEVICE_PATH), cmd)

    test_lib.setup_plan.execute_plan_without_deploy_test_agent()
    conf_ops.change_global_config("applianceVm", "agent.deployOnStart", 'true')
    if os.path.exists(EXTRA_SUITE_SETUP_SCRIPT):
        os.system("bash %s" % EXTRA_SUITE_SETUP_SCRIPT)
    deploy_operations.deploy_initial_database(test_lib.deploy_config, test_lib.all_scenario_config, test_lib.scenario_file)
    for host in hosts:
        os.system("bash %s %s" % (EXTRA_HOST_SETUP_SCRIPT, host.managementIp_))
    
    test_util.test_dsc("create vpc vrouter")
    vr = test_stub.create_vpc_vrouter()
    test_util.test_dsc("Try to create one vm in random L3 not attached")
    with test_lib.expected_failure("create one vm in random L3 not attached", Exception):
        test_stub.create_vm_with_random_offering(vm_name='vpc_vm1', l3_name=random.choice(test_stub.L3_SYSTEM_NAME_LIST))
    test_util.test_dsc("attach vpc l3 to vpc vrouter")
    test_stub.attach_l3_to_vpc_vr(vr, test_stub.L3_SYSTEM_NAME_LIST)

    test_util.test_dsc("create cloud router")
    vm1 = test_stub.create_vlan_vm(os.environ.get('l3NoVlanNetworkName2'))
    test_obj_dict.add_vm(vm1)
    vm1.clean()

    test_util.test_dsc("create load balance")
    l3_public_name = os.environ.get('l3PublicNetworkName')
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_public_name).uuid

    vip = test_stub.create_vip('vip_for_lb_test', l3_net_uuid)
    test_obj_dict.add_vip(vip)

    lb = zstack_lb_header.ZstackTestLoadBalancer()
    lb.create('autoscaling lb test', vip.get_vip().uuid)
    test_obj_dict.add_load_balancer(lb)

    lb_creation_option = test_lib.lib_create_lb_listener_option('check vm http healthy','tcp',22,80)
    lbl = lb.create_listener(lb_creation_option)


    delete_policy = test_lib.lib_set_delete_policy('vm', 'Direct')
    delete_policy = test_lib.lib_set_delete_policy('volume', 'Direct')
    delete_policy = test_lib.lib_set_delete_policy('image', 'Direct')
#    if test_lib.lib_get_ha_selffencer_maxattempts() != None:
#        test_lib.lib_set_ha_selffencer_maxattempts('60')
#	test_lib.lib_set_ha_selffencer_storagechecker_timeout('60')
    #test_lib.lib_set_primary_storage_imagecache_gc_interval(1)
    test_util.test_pass('Suite Setup Success')

