'''

@author: quarkonics
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
    #If test execution machine is not the same one as Host machine, deploy work is needed to separated to 2 steps(deploy_test_agent, execute_plan_without_deploy_test_agent). And it can not directly call SetupAction.run()
    test_lib.setup_plan.deploy_test_agent()
    test_lib.setup_plan.execute_plan_without_deploy_test_agent()
    deploy_operations.deploy_initial_database(test_lib.deploy_config)
    if os.path.exists(EXTRA_SUITE_SETUP_SCRIPT):
        os.system("bash %s" % EXTRA_SUITE_SETUP_SCRIPT)
    if test_lib.lib_get_ha_selffencer_maxattempts() != None:
        test_lib.lib_set_ha_selffencer_maxattempts('60')
	test_lib.lib_set_ha_selffencer_storagechecker_timeout('60')
    #test_lib.lib_set_primary_storage_imagecache_gc_interval(1)
    test_lib.lib_set_provision_storage_rate(6)
    test_lib.lib_set_provision_memory_rate(3)
    test_lib.lib_set_vm_numa('true')
    test_util.test_pass('Suite Setup Success')

