'''
Restart zstack management nodes. The difference compared with suite_setup is 
restart case won't redeploy database. 


@author: yyk
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib

def test():
    test_lib.setup_plan.disable_db_deployment()
    test_lib.setup_plan.execute_plan_without_deploy_test_agent()
    test_util.test_pass('zstack nodes restart Success')

