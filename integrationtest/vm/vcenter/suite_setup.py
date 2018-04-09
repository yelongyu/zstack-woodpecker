'''

@author: Frank
'''
import os.path
#import zstacklib.utils.linux as linux
#import zstacklib.utils.http as  http
import zstacktestagent.plugins.host as host_plugin
import zstacktestagent.testagent as testagent

import zstackwoodpecker.operations.scenario_operations as scenario_operations
import zstackwoodpecker.operations.deploy_operations as deploy_operations
import zstackwoodpecker.operations.config_operations as config_operations
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.tag_operations as tag_ops
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.setup_actions as setup_actions
import test_stub


USER_PATH = os.path.expanduser('~')
EXTRA_SUITE_SETUP_SCRIPT = '%s/.zstackwoodpecker/extra_suite_setup_config.sh' % USER_PATH
EXTRA_HOST_SETUP_SCRIPT = '%s/.zstackwoodpecker/extra_host_setup_config.sh' % USER_PATH

def test():
    if test_lib.scenario_config != None and test_lib.scenario_file != None and not os.path.exists(test_lib.scenario_file):
        scenario_operations.deploy_scenario(test_lib.all_scenario_config, test_lib.scenario_file, test_lib.deploy_config)
        test_util.test_skip('Suite Setup Success')
    if test_lib.scenario_config != None and test_lib.scenario_destroy != None:
        scenario_operations.destroy_scenario(test_lib.all_scenario_config, test_lib.scenario_destroy)

    ##If test execution machine is not the same one as Host machine, deploy work is needed to separated to 2 steps(deploy_test_agent, execute_plan_without_deploy_test_agent). And it can not directly call SetupAction.run()
    #setup = setup_actions.SetupAction()
    #setup.plan = test_lib.all_config
    #setup.run()
    test_lib.setup_plan.deploy_test_agent()
    test_lib.setup_plan.execute_plan_without_deploy_test_agent()
    if test_lib.scenario_config != None and test_lib.scenario_file != None and os.path.exists(test_lib.scenario_file):
        mn_ips = deploy_operations.get_nodes_from_scenario_file(test_lib.all_scenario_config, test_lib.scenario_file, test_lib.deploy_config)
        if os.path.exists(EXTRA_SUITE_SETUP_SCRIPT):
            os.system("bash %s '%s'" % (EXTRA_SUITE_SETUP_SCRIPT, mn_ips))
    elif os.path.exists(EXTRA_SUITE_SETUP_SCRIPT):
        os.system("bash %s" % (EXTRA_SUITE_SETUP_SCRIPT))

    deploy_operations.deploy_initial_vcenter(test_lib.deploy_config, test_lib.all_scenario_config, test_lib.scenario_file)
    deploy_operations.deploy_initial_database(test_lib.deploy_config, test_lib.all_scenario_config, test_lib.scenario_file)
    test_stub.check_deployed_vcenter(test_lib.deploy_config, test_lib.all_scenario_config, test_lib.scenario_file)

    image_name = os.environ['vcenterDefaultmplate']
    cond = res_ops.gen_query_conditions('name', '=', image_name)
    image_uuid = res_ops.query_resource(res_ops.IMAGE, cond)[0].uuid
    img_ops.update_image_platform(image_uuid, 'Linux')

    test_util.test_pass('Suite Setup Success')

