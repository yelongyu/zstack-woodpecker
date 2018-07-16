'''

@author: Frank
'''

import os
import zstackwoodpecker.operations.deploy_operations as deploy_operations
import zstackwoodpecker.operations.config_operations as config_operations
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_util as test_util

USER_PATH = os.path.expanduser('~')
EXTRA_SUITE_SETUP_SCRIPT = '%s/.zstackwoodpecker/extra_suite_setup_config.sh' % USER_PATH
EXTRA_ARM_SETUP_SCRIPT = '%s/.zstackwoodpecker/extra_arm_setup_config.sh' % USER_PATH

def test():
    try:
        test_lib.setup_plan.deploy_test_agent()
    except:
        pass
    if os.path.exists(EXTRA_ARM_SETUP_SCRIPT):
        os.system("bash %s" % EXTRA_ARM_SETUP_SCRIPT)

    test_lib.setup_plan.execute_plan_without_deploy_test_agent()

    if os.path.exists(EXTRA_SUITE_SETUP_SCRIPT):
        os.system("bash %s" % EXTRA_SUITE_SETUP_SCRIPT)
    deploy_operations.deploy_initial_database(test_lib.deploy_config)
    test_util.test_pass('Suite Setup Success')

