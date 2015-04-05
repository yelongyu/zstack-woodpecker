'''

@author: Frank
'''
from zstackwoodpecker import test_util
import os.path
from zstacklib.utils import linux
from zstacklib.utils import http
from zstacktestagent.plugins import host as host_plugin
from zstacktestagent import testagent

import zstackwoodpecker.operations.deploy_operations as deploy_operations
import zstackwoodpecker.operations.config_operations as config_operations

import zstackwoodpecker.test_lib as test_lib

def test():
    #This vlan creation is not a must, if testing is under nested virt env. But it is required on physical host without enough physcial network devices and your test execution machine is not the same one as Host machine. 
    #linux.create_vlan_eth("eth0", 10, "10.0.0.200", "255.255.255.0")
    #linux.create_vlan_eth("eth0", 11, "10.0.1.200", "255.255.255.0")
    #linux.create_vlan_eth("eth0", 10)
    #linux.create_vlan_eth("eth0", 11)

    #If test execution machine is not the same one as Host machine, deploy work is needed to separated to 2 steps(deploy_test_agent, execute_plan_without_deploy_test_agent). And it can not directly call SetupAction.run()
    test_lib.setup_plan.deploy_test_agent()
    #cmd = host_plugin.CreateVlanDeviceCmd()
    
    #hosts = test_lib.lib_get_all_hosts_from_plan()
    #if type(hosts) != type([]):
    #    hosts = [hosts]
    #for host in hosts:
    #    cmd.ethname = 'eth0'
    #    cmd.vlan = 10
    #    http.json_dump_post(testagent.build_http_path(host.managementIp_, host_plugin.CREATE_VLAN_DEVICE_PATH), cmd)
    #    cmd.vlan = 11
    #    http.json_dump_post(testagent.build_http_path(host.managementIp_, host_plugin.CREATE_VLAN_DEVICE_PATH), cmd)

    test_lib.setup_plan.execute_plan_without_deploy_test_agent()
    deploy_operations.deploy_initial_database(test_lib.deploy_config)
    test_util.test_pass('ZStack POC Test Suite Setup Success')

