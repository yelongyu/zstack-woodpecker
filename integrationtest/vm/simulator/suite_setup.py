'''

@author: Frank
'''

import os
import subprocess
import zstackwoodpecker.operations.scenario_operations as scenario_operations
import zstackwoodpecker.operations.deploy_operations as deploy_operations
import zstackwoodpecker.operations.config_operations as config_operations
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_util as test_util

USER_PATH = os.path.expanduser('~')
EXTRA_SUITE_SETUP_SCRIPT = '%s/.zstackwoodpecker/extra_suite_setup_config.sh' % USER_PATH
def test():
    os.system('pkill -f ./test_rest_server.py')
    process = subprocess.Popen("./test_rest_server.py", cwd=os.environ.get('woodpecker_root_path')+'/dailytest/', universal_newlines=True)
    test_util.test_pass('Suite Setup Success')
    if test_lib.scenario_config != None and test_lib.scenario_file != None and not os.path.exists(test_lib.scenario_file):
        scenario_operations.deploy_scenario(test_lib.all_scenario_config, test_lib.scenario_file, test_lib.deploy_config)
        test_util.test_skip('Suite Setup Success')
    if test_lib.scenario_config != None and test_lib.scenario_destroy != None:
        scenario_operations.destroy_scenario(test_lib.all_scenario_config, test_lib.scenario_destroy)

    test_lib.setup_plan.execute_plan_without_deploy_test_agent()

    if test_lib.scenario_config != None and test_lib.scenario_file != None and os.path.exists(test_lib.scenario_file):
        mn_ips = deploy_operations.get_nodes_from_scenario_file(test_lib.all_scenario_config, test_lib.scenario_file, test_lib.deploy_config)
        if os.path.exists(EXTRA_SUITE_SETUP_SCRIPT):
            os.system("bash %s '%s' %s" % (EXTRA_SUITE_SETUP_SCRIPT, mn_ips,'project-management'))
    elif os.path.exists(EXTRA_SUITE_SETUP_SCRIPT):
        os.system("bash %s '' '%s'" % (EXTRA_SUITE_SETUP_SCRIPT,'project-management'))

    if os.environ.get('ZSTACK_SIMULATOR') == "yes":
        deploy_operations.deploy_simulator_database(test_lib.deploy_config, test_lib.all_scenario_config, test_lib.scenario_file)
    deploy_operations.deploy_initial_database(test_lib.deploy_config, test_lib.all_scenario_config, test_lib.scenario_file)
    test_util.test_pass('Suite Setup Success')
