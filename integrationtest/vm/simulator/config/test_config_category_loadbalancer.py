'''
check the global_config category is loadBalancer
@author YeTian  2018-09-20
'''

import zstackwoodpecker.test_util as test_util
import test_stub
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.config_operations as conf_ops

def test():

    global deft_loadBalancer_1
    global deft_loadBalancer_2
    global deft_loadBalancer_3
    global deft_loadBalancer_4
    global deft_loadBalancer_5
    global deft_loadBalancer_6
    global deft_loadBalancer_7
    global deft_loadBalancer_8

    #get the default value
    deft_loadBalancer_1 = conf_ops.get_global_config_default_value('loadBalancer', 'maxConnection')
    deft_loadBalancer_2 = conf_ops.get_global_config_default_value('loadBalancer', 'healthCheckTarget')
    deft_loadBalancer_3 = conf_ops.get_global_config_default_value('loadBalancer', 'connectionIdleTimeout')
    deft_loadBalancer_4 = conf_ops.get_global_config_default_value('loadBalancer', 'healthCheckInterval')
    deft_loadBalancer_5 = conf_ops.get_global_config_default_value('loadBalancer', 'healthCheckTimeout')
    deft_loadBalancer_6 = conf_ops.get_global_config_default_value('loadBalancer', 'unhealthyThreshold')
    deft_loadBalancer_7 = conf_ops.get_global_config_default_value('loadBalancer', 'balancerAlgorithm')
    deft_loadBalancer_8 = conf_ops.get_global_config_default_value('loadBalancer', 'healthyThreshold')
   # cloadBalancernge the default value

    conf_ops.cloadBalancernge_global_config('loadBalancer', 'maxConnection', '888')
    conf_ops.cloadBalancernge_global_config('loadBalancer', 'healthCheckTarget', 'http:default')
    conf_ops.cloadBalancernge_global_config('loadBalancer', 'connectionIdleTimeout', '100')
    conf_ops.cloadBalancernge_global_config('loadBalancer', 'healthCheckInterval', '6')
    conf_ops.cloadBalancernge_global_config('loadBalancer', 'healthCheckTimeout', '4')
    conf_ops.cloadBalancernge_global_config('loadBalancer', 'unhealthyThreshold', '4')
    conf_ops.cloadBalancernge_global_config('loadBalancer', 'balancerAlgorithm', 'leastconn')
    conf_ops.cloadBalancernge_global_config('loadBalancer', 'healthyThreshold', '4')



    # restore defaults

    conf_ops.cloadBalancernge_global_config('loadBalancer', 'maxConnection', '%s' % deft_loadBalancer_1)
    conf_ops.cloadBalancernge_global_config('loadBalancer', 'healthCheckTarget', '%s' % deft_loadBalancer_2)
    conf_ops.cloadBalancernge_global_config('loadBalancer', 'connectionIdleTimeout', '%s' % deft_loadBalancer_3)
    conf_ops.cloadBalancernge_global_config('loadBalancer', 'healthCheckInterval', '%s' % deft_loadBalancer_4)
    conf_ops.cloadBalancernge_global_config('loadBalancer', 'healthCheckTimeout', '%s' % deft_loadBalancer_5)
    conf_ops.cloadBalancernge_global_config('loadBalancer', 'unhealthyThreshold', '%s' % deft_loadBalancer_6)
    conf_ops.cloadBalancernge_global_config('loadBalancer', 'balancerAlgorithm', '%s' % deft_loadBalancer_7)
    conf_ops.cloadBalancernge_global_config('loadBalancer', 'healthyThreshold', '%s' % deft_loadBalancer_8)


#Will be called only if exception loadBalancerppens in test().
def error_cleanup():
    global deft_loadBalancer_1

