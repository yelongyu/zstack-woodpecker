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

EXTRA_SUITE_SETUP_SCRIPT = '%s/.zstackwoodpecker/extra_suite_setup_config.sh' % USER_PATH

def test():
    #This vlan creation is not a must, if testing is under nested virt env. But it is required on physical host without enough physcial network devices and your test execution machine is not the same one as Host machine. 
    #linux.create_vlan_eth("eth0", 10, "10.0.0.200", "255.255.255.0")
    #linux.create_vlan_eth("eth0", 11, "10.0.1.200", "255.255.255.0")

    #If test execution machine is not the same one as Host machine, deploy work is needed to separated to 2 steps(deploy_test_agent, execute_plan_without_deploy_test_agent). And it can not directly call SetupAction.run()

    test_lib.setup_plan.deploy_test_agent()

    test_lib.setup_plan.execute_plan_without_deploy_test_agent()
    if os.path.exists(EXTRA_SUITE_SETUP_SCRIPT):
        os.system("bash %s" % EXTRA_SUITE_SETUP_SCRIPT)

    deploy_operations.deploy_initial_database(test_lib.deploy_config)
    test_util.test_pass('Suite Setup Success')

