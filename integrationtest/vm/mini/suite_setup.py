'''
TestSuite for basic infrustrature
@author: SyZhao
'''
import os.path
import zstacklib.utils.linux as linux
import zstacklib.utils.http as  http
import zstacklib.utils.ssh as ssh
import zstacktestagent.plugins.host as host_plugin
import zstacktestagent.testagent as testagent
import zstacklib.utils.xmlobject as xmlobject

import zstackwoodpecker.operations.scenario_operations as scenario_operations
import zstackwoodpecker.operations.deploy_operations as deploy_operations
import zstackwoodpecker.operations.config_operations as config_operations
import zstackwoodpecker.operations.node_operations as node_operations
import zstackwoodpecker.operations.tag_operations as tag_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_util as test_util
import test_stub

USER_PATH = os.path.expanduser('~')
EXTRA_SUITE_SETUP_SCRIPT = '%s/.zstackwoodpecker/extra_suite_setup_config.sh' % USER_PATH
EXTRA_HOST_SETUP_SCRIPT = '%s/.zstackwoodpecker/extra_host_setup_config.sh' % USER_PATH


def test():
    if test_lib.scenario_config == None or test_lib.scenario_file ==None:
        test_util.test_fail('Suite Setup Fail without scenario')

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


    test_stub.deploy_2ha(test_lib.all_scenario_config, test_lib.scenario_file, test_lib.deploy_config)
    mn_ip1 = test_stub.get_host_by_index_in_scenario_file(test_lib.all_scenario_config, test_lib.scenario_file, 0).ip_
    mn_ip2 = test_stub.get_host_by_index_in_scenario_file(test_lib.all_scenario_config, test_lib.scenario_file, 1).ip_

    if not xmlobject.has_element(test_lib.deploy_config, 'backupStorages.miniBackupStorage'):
        host_ip1 = test_stub.get_host_by_index_in_scenario_file(test_lib.all_scenario_config, test_lib.scenario_file, 2).ip_
        test_stub.recover_vlan_in_host(host_ip1, test_lib.all_scenario_config, test_lib.deploy_config)

    test_stub.wrapper_of_wait_for_management_server_start(600, EXTRA_SUITE_SETUP_SCRIPT)
    test_util.test_logger("@@@DEBUG->suite_setup@@@ os\.environ\[\'ZSTACK_BUILT_IN_HTTP_SERVER_IP\'\]=%s; os\.environ\[\'zstackHaVip\'\]=%s"	\
                          %(os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'], os.environ['zstackHaVip']) )
    ssh.scp_file("/home/license-10host-10days-hp.txt", "/home/license-10host-10days-hp.txt", mn_ip1, 'root', 'password')
    ssh.scp_file("/home/license-10host-10days-hp.txt", "/home/license-10host-10days-hp.txt", mn_ip2, 'root', 'password')
    if os.path.exists(EXTRA_SUITE_SETUP_SCRIPT):
        os.system("bash %s %s" % (EXTRA_SUITE_SETUP_SCRIPT, mn_ip1, "disaster-recovery"))
        os.system("bash %s %s" % (EXTRA_SUITE_SETUP_SCRIPT, mn_ip2, "disaster-recovery"))

    deploy_operations.deploy_initial_database(test_lib.deploy_config, test_lib.all_scenario_config, test_lib.scenario_file)
    for host in testHosts:
        os.system("bash %s %s" % (EXTRA_HOST_SETUP_SCRIPT, host.managementIp_))

    test_lib.lib_set_primary_storage_imagecache_gc_interval(1)
    #test_lib.lib_set_reserved_memory('1G')

    if test_lib.lib_cur_cfg_is_a_and_b(["test-config-vyos-local-ps.xml"], ["scenario-config-upgrade-3.1.1.xml"]):
        cmd = r"sed -i '$a\172.20.198.8 rsync.repo.zstack.io' /etc/hosts"
        ssh.execute(cmd, mn_ip1, "root", "password", False, 22)
        ssh.execute(cmd, mn_ip2, "root", "password", False, 22)

    test_util.test_pass('Suite Setup Success')

