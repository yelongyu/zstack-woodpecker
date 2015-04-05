'''
@author yyou
'''
import zstackwoodpecker.operations.deploy_operations as deploy_operations
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_util as test_util

def test():
    #This vlan creation is not a must, if testing is under nested virt env. But it is required on physical host without enough physcial network devices and your test execution machine is not the same one as Host machine. 

    #If test execution machine is not the same one as Host machine, deploy work is needed to separated to 2 steps(deploy_test_agent, execute_plan_without_deploy_test_agent). And it can not directly call SetupAction.run()
    test_lib.setup_plan.deploy_test_agent()
    test_lib.setup_plan.execute_plan_without_deploy_test_agent()
    deploy_operations.deploy_initial_database(test_lib.deploy_config)
    test_util.test_pass('ZStack Installation Suite Setup Success')
