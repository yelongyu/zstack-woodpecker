'''

@author: Frank
'''

import zstackwoodpecker.setup_actions as setup_actions
import zstackwoodpecker.operations.deploy_operations as deploy_operations
import zstackwoodpecker.operations.config_operations as config_operations
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_util as test_util

def test():
    setup = setup_actions.SetupAction()
    setup.plan = test_lib.all_config
    setup.run()

    deploy_operations.deploy_initial_database(test_lib.deploy_config)
    test_util.test_pass('Suite Setup Success')

