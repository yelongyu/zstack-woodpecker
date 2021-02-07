'''
check the global_config category is zwatch
@author YeTian  2018-09-20
'''

import zstackwoodpecker.test_util as test_util
#import test_stub
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.config_operations as conf_ops

def test():

    global deft_zwatch_1
    global deft_zwatch_2
    global deft_zwatch_3
    global deft_zwatch_4
    global deft_zwatch_5
    global deft_zwatch_6
    #get the default value
    deft_zwatch_1 = conf_ops.get_global_config_default_value('zwatch', 'resolution.defaultAlgorithm.maxSamples')
    deft_zwatch_2 = conf_ops.get_global_config_default_value('zwatch', 'managementServerDirectoriesToMonitor')
    deft_zwatch_3 = conf_ops.get_global_config_default_value('zwatch', 'alarm.repeatInterval')
    deft_zwatch_4 = conf_ops.get_global_config_default_value('zwatch', 'scrape.interval')
    deft_zwatch_5 = conf_ops.get_global_config_default_value('zwatch', 'evaluation.interval')
    deft_zwatch_6 = conf_ops.get_global_config_default_value('zwatch', 'evaluation.threadNum')


   # change the default value

    conf_ops.change_global_config('zwatch', 'resolution.defaultAlgorithm.maxSamples', '200')
    conf_ops.change_global_config('zwatch', 'managementServerDirectoriesToMonitor', '/usr/local,/opt/')
    conf_ops.change_global_config('zwatch', 'alarm.repeatInterval', '3600')
    conf_ops.change_global_config('zwatch', 'scrape.interval', '30')
    conf_ops.change_global_config('zwatch', 'evaluation.interval', '20')
    conf_ops.change_global_config('zwatch', 'evaluation.threadNum', '10')


    # restore defaults

    conf_ops.change_global_config('zwatch', 'resolution.defaultAlgorithm.maxSamples', '%s' % deft_zwatch_1)
    conf_ops.change_global_config('zwatch', 'managementServerDirectoriesToMonitor', '%s' % deft_zwatch_2)
    conf_ops.change_global_config('zwatch', 'alarm.repeatInterval', '%s' % deft_zwatch_3)
    conf_ops.change_global_config('zwatch', 'scrape.interval', '%s' % deft_zwatch_4)
    conf_ops.change_global_config('zwatch', 'evaluation.interval', '%s' % deft_zwatch_5)
    conf_ops.change_global_config('zwatch', 'evaluation.threadNum', '%s' % deft_zwatch_6)


#Will be called only if exception happens in test().
def error_cleanup():
    global deft_zwatch_1

