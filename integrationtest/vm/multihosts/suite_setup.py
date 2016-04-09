'''

@author: Frank
'''
import os.path
import zstacklib.utils.linux as linux
import zstacklib.utils.http as  http
import zstacktestagent.plugins.host as host_plugin
import zstacktestagent.testagent as testagent

import zstackwoodpecker.operations.deploy_operations as deploy_operations
import zstackwoodpecker.operations.config_operations as config_operations
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_util as test_util

USER_PATH = os.path.expanduser('~')
EXTRA_SUITE_SETUP_SCRIPT = '%s/.zstackwoodpecker/extra_suite_setup_config.sh' % USER_PATH
def test():
    #This vlan creation is not a must, if testing is under nested virt env. But it is required on physical host without enough physcial network devices and your test execution machine is not the same one as Host machine. 
    #no matter if current host is a ZStest host, we need to create 2 vlan devs for future testing connection for novlan test cases.
    linux.create_vlan_eth("eth0", 10)
    linux.create_vlan_eth("eth0", 11)

    #If test execution machine is not the same one as Host machine, deploy work is needed to separated to 2 steps(deploy_test_agent, execute_plan_without_deploy_test_agent). And it can not directly call SetupAction.run()
    test_lib.setup_plan.deploy_test_agent()
    cmd = host_plugin.CreateVlanDeviceCmd()
    cmd.ethname = 'eth0'
    cmd.vlan = 10
    
    cmd2 = host_plugin.CreateVlanDeviceCmd()
    cmd2.ethname = 'eth0'
    cmd2.vlan = 11
    testHosts = test_lib.lib_get_all_hosts_from_plan()
    if type(testHosts) != type([]):
        testHosts = [testHosts]
    for host in testHosts:
        http.json_dump_post(testagent.build_http_path(host.managementIp_, host_plugin.CREATE_VLAN_DEVICE_PATH), cmd)
        http.json_dump_post(testagent.build_http_path(host.managementIp_, host_plugin.CREATE_VLAN_DEVICE_PATH), cmd2)

    test_lib.setup_plan.execute_plan_without_deploy_test_agent()
    deploy_operations.deploy_initial_database(test_lib.deploy_config)
    if os.path.exists(EXTRA_SUITE_SETUP_SCRIPT):
        os.system("bash %s" % EXTRA_SUITE_SETUP_SCRIPT)
    if test_lib.lib_get_ha_selffencer_maxattempts() != None:
        test_lib.lib_set_ha_selffencer_maxattempts('60')
    test_util.test_pass('Suite Setup Success')

