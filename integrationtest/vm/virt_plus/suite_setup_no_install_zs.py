'''
deploy virtual router test environment, without reinstall zstack. Will redeploy
database. 

@author: Youyk
'''
import os

import zstackwoodpecker.operations.deploy_operations as deploy_operations
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_util as test_util

USER_PATH = os.path.expanduser('~')
EXTRA_SUITE_SETUP_SCRIPT = '%s/.zstackwoodpecker/extra_suite_setup_config.sh' % USER_PATH

def test():
    #If test execution machine is not the same one as Host machine, deploy work is needed to separated to 2 steps(deploy_test_agent, execute_plan_without_deploy_test_agent). And it can not directly call SetupAction.run()
    test_lib.setup_plan.deploy_db_without_reinstall_zstack()
    deploy_operations.deploy_initial_database(test_lib.deploy_config)
    if os.path.exists(EXTRA_SUITE_SETUP_SCRIPT):
        os.system("bash %s" % EXTRA_SUITE_SETUP_SCRIPT)

    test_util.test_pass('Suite Setup Success')

