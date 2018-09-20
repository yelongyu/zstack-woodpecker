'''
check the global_config category is networkService
@author YeTian  2018-09-20
'''

import zstackwoodpecker.test_util as test_util
import test_stub
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.config_operations as conf_ops

def test():

    global deft_networkService_1
    global deft_networkService_2
    global deft_networkService_3
    global deft_networkService_4
    #get the default value
    deft_networkService_1 = conf_ops.get_global_config_default_value('networkService', 'defaultDhcpMtu.l2VlanNetwork')
    deft_networkService_2 = conf_ops.get_global_config_default_value('networkService', 'defaultDhcpMtu.dummyNetwork')
    deft_networkService_3 = conf_ops.get_global_config_default_value('networkService', 'defaultDhcpMtu.l2VxlanNetwork')
    deft_networkService_4 = conf_ops.get_global_config_default_value('networkService', 'defaultDhcpMtu.l2NoVlanNetwork')


   # change the default value

    conf_ops.change_global_config('networkService', 'defaultDhcpMtu.l2VlanNetwork', '1000')
    conf_ops.change_global_config('networkService', 'defaultDhcpMtu.dummyNetwork', '1000')
    conf_ops.change_global_config('networkService', 'defaultDhcpMtu.l2VxlanNetwork', '1000')
    conf_ops.change_global_config('networkService', 'defaultDhcpMtu.l2NoVlanNetwork', '1000')


    # restore defaults

    conf_ops.change_global_config('networkService', 'defaultDhcpMtu.l2VlanNetwork', '%s' % deft_networkService_1)
    conf_ops.change_global_config('networkService', 'defaultDhcpMtu.dummyNetwork', '%s' % deft_networkService_2)
    conf_ops.change_global_config('networkService', 'defaultDhcpMtu.l2VxlanNetwork', '%s' % deft_networkService_3)
    conf_ops.change_global_config('networkService', 'defaultDhcpMtu.l2NoVlanNetwork', '%s' % deft_networkService_4)


#Will be called only if exception happens in test().
def error_cleanup():
    global deft_networkService_1

