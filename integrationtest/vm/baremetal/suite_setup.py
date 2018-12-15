'''

@author: Frank
'''

import os
import zstackwoodpecker.setup_actions as setup_actions
import zstackwoodpecker.operations.scenario_operations as scenario_operations
import zstackwoodpecker.operations.deploy_operations as deploy_operations
import zstackwoodpecker.operations.config_operations as config_operations
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_util as test_util
import zstacklib.utils.http as  http
import zstacklib.utils.linux as linux
import zstacklib.utils.shell as shell
import zstacktestagent.plugins.host as host_plugin
import zstacktestagent.testagent as testagent
import test_stub

USER_PATH = os.path.expanduser('~')
EXTRA_SUITE_SETUP_SCRIPT = '%s/.zstackwoodpecker/extra_suite_setup_config.sh' % USER_PATH

def test():
    if test_lib.scenario_config != None and test_lib.scenario_file != None and not os.path.exists(test_lib.scenario_file):
        scenario_operations.deploy_scenario(test_lib.all_scenario_config, test_lib.scenario_file, test_lib.deploy_config)
        test_util.test_skip('Suite Setup Success')
    if test_lib.scenario_config != None and test_lib.scenario_destroy != None:
        scenario_operations.destroy_scenario(test_lib.all_scenario_config, test_lib.scenario_destroy)

    test_lib.setup_plan.deploy_test_agent()
    test_lib.setup_plan.execute_plan_without_deploy_test_agent()

    #Suite setup for mnha2 scenario
    if os.path.basename(os.environ.get('WOODPECKER_SCENARIO_CONFIG_FILE')).strip() == "scenario-config-mnha2.xml":
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

        test_stub.deploy_2ha(test_lib.all_scenario_config, test_lib.scenario_file)
        mn_ip1 = test_stub.get_host_by_index_in_scenario_file(test_lib.all_scenario_config, test_lib.scenario_file, 0).ip_
        mn_ip2 = test_stub.get_host_by_index_in_scenario_file(test_lib.all_scenario_config, test_lib.scenario_file, 1).ip_
        host_ip1 = test_stub.get_host_by_index_in_scenario_file(test_lib.all_scenario_config, test_lib.scenario_file, 2).ip_
        test_stub.recover_vlan_in_host(host_ip1, test_lib.all_scenario_config, test_lib.deploy_config)

        #test_stub.wrapper_of_wait_for_management_server_start(600, EXTRA_SUITE_SETUP_SCRIPT)
        test_util.test_logger("@@@DEBUG->suite_setup@@@ os\.environ\[\'ZSTACK_BUILT_IN_HTTP_SERVER_IP\'\]=%s; os\.environ\[\'zstackHaVip\'\]=%s"    \
                          %(os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'], os.environ['zstackHaVip']) )
        #ssh.scp_file("/home/license-10host-10days-hp.txt", "/home/license-10host-10days-hp.txt", mn_ip1, 'root', 'password')
        #ssh.scp_file("/home/license-10host-10days-hp.txt", "/home/license-10host-10days-hp.txt", mn_ip2, 'root', 'password')
        if os.path.exists(EXTRA_SUITE_SETUP_SCRIPT):
            os.system("bash %s '%s' %s" % (EXTRA_SUITE_SETUP_SCRIPT, mn_ip1, 'baremetal'))
            os.system("bash %s '%s' %s" % (EXTRA_SUITE_SETUP_SCRIPT, mn_ip2, 'baremetal'))
            test_stub.deploy_vbmc(host_ip1)

    elif test_lib.scenario_config != None and test_lib.scenario_file != None and os.path.exists(test_lib.scenario_file):
        mn_ips = deploy_operations.get_nodes_from_scenario_file(test_lib.all_scenario_config, test_lib.scenario_file, test_lib.deploy_config)
        host_ips = deploy_operations.get_hosts_from_scenario_file(test_lib.all_scenario_config, test_lib.scenario_file, test_lib.deploy_config)
        if os.path.exists(EXTRA_SUITE_SETUP_SCRIPT):
            os.system("bash %s '%s' %s" % (EXTRA_SUITE_SETUP_SCRIPT, mn_ips, 'baremetal'))
            test_stub.deploy_vbmc(host_ips)

    deploy_operations.deploy_initial_database(test_lib.deploy_config, test_lib.all_scenario_config, test_lib.scenario_file)

    #Deploy network has not DHCP service, which need to setup static ip
    if os.path.exists(test_lib.scenario_file):
        test_stub.setup_static_ip(test_lib.scenario_file)

    delete_policy = test_lib.lib_set_delete_policy('vm', 'Direct')
    delete_policy = test_lib.lib_set_delete_policy('volume', 'Direct')
    delete_policy = test_lib.lib_set_delete_policy('image', 'Direct')
    if test_lib.lib_get_ha_selffencer_maxattempts() != None:
	test_lib.lib_set_ha_selffencer_maxattempts('60')
	test_lib.lib_set_ha_selffencer_storagechecker_timeout('60')
    test_lib.lib_set_primary_storage_imagecache_gc_interval(1)
    test_util.test_pass('Suite Setup Success')
