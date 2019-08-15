'''

@author: Lei Liu
'''
import os.path
import zstacklib.utils.linux as linux
import zstacklib.utils.http as  http
import zstacktestagent.plugins.host as host_plugin
import zstacktestagent.testagent as testagent

import zstackwoodpecker.operations.scenario_operations as scenario_operations
import zstackwoodpecker.operations.deploy_operations as deploy_operations
import zstackwoodpecker.operations.config_operations as config_operations
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.tag_operations as tag_ops

USER_PATH = os.path.expanduser('~')
EXTRA_SUITE_SETUP_SCRIPT = '%s/.zstackwoodpecker/extra_suite_setup_config.sh' % USER_PATH
EXTRA_HOST_SETUP_SCRIPT = '%s/.zstackwoodpecker/extra_host_setup_config.sh' % USER_PATH

def test():
    if test_lib.scenario_config != None and test_lib.scenario_file != None and not os.path.exists(test_lib.scenario_file):
        scenario_operations.deploy_scenario(test_lib.all_scenario_config, test_lib.scenario_file, test_lib.deploy_config)
        test_util.test_skip('Suite Setup Success')
    if test_lib.scenario_config != None and test_lib.scenario_destroy != None:
        scenario_operations.destroy_scenario(test_lib.all_scenario_config, test_lib.scenario_destroy)

    nic_name = "eth0"
    if test_lib.scenario_config != None and test_lib.scenario_file != None and os.path.exists(test_lib.scenario_file):
        nic_name = "zsn0"

    #This vlan creation is not a must, if testing is under nested virt env. But it is required on physical host without enough physcial network devices and your test execution machine is not the same one as Host machine. 
    #no matter if current host is a ZStest host, we need to create 2 vlan devs for future testing connection for novlan test cases.
    linux.create_vlan_eth(nic_name, 10)
    linux.create_vlan_eth(nic_name, 11)

    #If test execution machine is not the same one as Host machine, deploy work is needed to separated to 2 steps(deploy_test_agent, execute_plan_without_deploy_test_agent). And it can not directly call SetupAction.run()
    test_lib.setup_plan.deploy_test_agent()
    cmd = host_plugin.CreateVlanDeviceCmd()
    cmd.ethname = nic_name
    cmd.vlan = 10
    
    cmd2 = host_plugin.CreateVlanDeviceCmd()
    cmd2.ethname = nic_name
    cmd2.vlan = 11
    testHosts = test_lib.lib_get_all_hosts_from_plan()
    if type(testHosts) != type([]):
        testHosts = [testHosts]
    for host in testHosts:
        http.json_dump_post(testagent.build_http_path(host.managementIp_, host_plugin.CREATE_VLAN_DEVICE_PATH), cmd)
        http.json_dump_post(testagent.build_http_path(host.managementIp_, host_plugin.CREATE_VLAN_DEVICE_PATH), cmd2)

    test_lib.setup_plan.execute_plan_without_deploy_test_agent()
    if test_lib.scenario_config != None and test_lib.scenario_file != None and os.path.exists(test_lib.scenario_file):
        mn_ips = deploy_operations.get_nodes_from_scenario_file(test_lib.all_scenario_config, test_lib.scenario_file, test_lib.deploy_config)
        if os.path.exists(EXTRA_SUITE_SETUP_SCRIPT):
            os.system("bash %s '%s'" % (EXTRA_SUITE_SETUP_SCRIPT, mn_ips))
    elif os.path.exists(EXTRA_SUITE_SETUP_SCRIPT):
        os.system("bash %s" % (EXTRA_SUITE_SETUP_SCRIPT))

    deploy_operations.deploy_initial_database(test_lib.deploy_config, test_lib.all_scenario_config, test_lib.scenario_file)
    for host in testHosts:
        os.system("bash %s %s" % (EXTRA_HOST_SETUP_SCRIPT, host.managementIp_))

    mn_ip = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].hostName
    if test_lib.ver_ge_zstack_2_0(mn_ip):
        test_lib.lib_set_allow_live_migration_local_storage('true')
    #test_lib.lib_set_primary_storage_imagecache_gc_interval(1)
    test_lib.ensure_recover_script_l2_correct()

    if test_lib.lib_is_storage_network_separate():
        add_ps_network_gateway_sys_tag()

    test_util.test_pass('Suite Setup Success')

