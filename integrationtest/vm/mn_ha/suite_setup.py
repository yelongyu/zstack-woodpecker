'''

@author: Mirabel
'''
import os.path
import zstacklib.utils.linux as linux
import zstacklib.utils.http as  http
import zstacklib.utils.ssh as ssh
import zstacktestagent.plugins.host as host_plugin
import zstacktestagent.testagent as testagent

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

def add_ps_network_gateway_sys_tag():
    '''
        Add system tag for mn to monitor the storage network in network separated.
        Currently, not support multiple PS case
    '''
    pss = res_ops.query_resource(res_ops.PRIMARY_STORAGE)
    if len(pss) > 1:
        test_util.test_logger("add ps gateway skip for multiple ps case.")
        return

    ps = pss[0]
    test_util.test_logger("add system tag: resourceUuid=%s tag=%s" %(ps.uuid, "primaryStorage::gateway::cidr::192.168.0.0/16"))
    tag_ops.create_system_tag('PrimaryStorageVO', ps.uuid, "primaryStorage::gateway::cidr::192.168.0.0/16")


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


    if test_lib.lib_cur_cfg_is_a_and_b(["test-config-vyos-nfs.xml"], \
                                       ["scenario-config-storage-separate-nfs.xml"]):
        config_json = os.environ.get('configJsonSepStor')

    elif test_lib.lib_cur_cfg_is_a_and_b(["test-config-vyos-nonmon-ceph.xml"], \
                                       ["scenario-config-storage-separate-ceph.xml"]):
        config_json = os.environ.get('configJsonNonMon')

    elif test_lib.lib_cur_cfg_is_a_and_b(["test-config-vyos-flat-dhcp-nfs-sep-pub-man.xml"], \
                                         ["scenario-config-nfs-sep-man.xml", \
                                          "scenario-config-nfs-sep-pub.xml"]):
        config_json = os.environ.get('configJsonSepPub')

    elif test_lib.lib_cur_cfg_is_a_and_b(["test-config-vyos-ceph-3-nets-sep.xml"], \
                                         ["scenario-config-ceph-sep-man.xml", \
                                          "scenario-config-ceph-sep-pub.xml", \
                                          "scenario-config-ceph-3-nets-sep.xml"]):
        config_json = os.environ.get('configJsonSepPub')

    elif test_lib.lib_cur_cfg_is_a_and_b(["test-config-vyos-fusionstor-3-nets-sep.xml"], \
                                         ["scenario-config-fusionstor-3-nets-sep.xml"]):
        config_json = os.environ.get('configJson3Net')

    elif test_lib.lib_cur_cfg_is_a_and_b(["test-config-vyos-flat-dhcp-nfs-mul-net-pubs.xml"], \
                                         ["scenario-config-nfs-sep-man.xml", \
                                          "scenario-config-nfs-sep-pub.xml"]):
        config_json = os.environ.get('configJsonAllOne')

    else:
        config_json = os.environ.get('configJson')


    ha_deploy_tool = os.environ.get('zstackHaInstaller')
    mn_img = os.environ.get('mnImage')
    test_stub.deploy_ha_env(test_lib.all_scenario_config, test_lib.scenario_file, test_lib.deploy_config,config_json, ha_deploy_tool, mn_img)

    #if os.path.basename(os.environ.get('WOODPECKER_SCENARIO_CONFIG_FILE')).strip() == "scenario-config-vpc-ceph-3-sites.xml":
    #    test_util.test_logger("@@@DEBUG->IS VPC CEPH@@@")
    #    old_mn_ip = os.environ['zstackHaVip']
    #    test_stub.auto_set_mn_ip(test_lib.scenario_file)
    #    cmd = 'sed -i "s/%s/%s/g" %s' %(old_mn_ip, os.environ['zstackHaVip'], EXTRA_SUITE_SETUP_SCRIPT)
    #    os.system(cmd)

    #node_operations.wait_for_management_server_start(600)
    test_stub.wrapper_of_wait_for_management_server_start(600, EXTRA_SUITE_SETUP_SCRIPT)
    test_util.test_logger("@@@DEBUG->suite_setup@@@ os\.environ\[\'ZSTACK_BUILT_IN_HTTP_SERVER_IP\'\]=%s; os\.environ\[\'zstackHaVip\'\]=%s"	\
                          %(os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'], os.environ['zstackHaVip']) )
    ssh.scp_file("/home/license-10host-10days-hp.txt", "/home/license-10host-10days-hp.txt", os.environ.get('zstackHaVip'), 'root', 'password')
    if os.path.exists(EXTRA_SUITE_SETUP_SCRIPT):
        os.system("bash %s" % EXTRA_SUITE_SETUP_SCRIPT)

    deploy_operations.deploy_initial_database(test_lib.deploy_config, test_lib.all_scenario_config, test_lib.scenario_file)
    for host in testHosts:
        os.system("bash %s %s" % (EXTRA_HOST_SETUP_SCRIPT, host.managementIp_))

    #if test_lib.lib_get_ha_selffencer_maxattempts() != None:
    #    test_lib.lib_set_ha_selffencer_maxattempts('60')
    #    test_lib.lib_set_ha_selffencer_storagechecker_timeout('60')
    #test_lib.lib_set_primary_storage_imagecache_gc_interval(1)
    test_lib.lib_set_reserved_memory('8G')
    
    if test_lib.lib_cur_cfg_is_a_and_b(["test-config-vyos-flat-dhcp-nfs-sep-pub-man.xml"], ["scenario-config-nfs-sep-pub.xml"]) or \
       test_lib.lib_cur_cfg_is_a_and_b(["test-config-vyos-ceph-3-nets-sep.xml"], ["scenario-config-ceph-sep-pub.xml"]) or \
       test_lib.lib_cur_cfg_is_a_and_b(["test-config-vyos-fusionstor-3-nets-sep.xml"], ["scenario-config-fusionstor-3-nets-sep.xml"]):
        add_ps_network_gateway_sys_tag()

    test_util.test_pass('Suite Setup Success')

