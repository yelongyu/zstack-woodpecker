'''
check the global_config category is ha
@author YeTian  2018-09-20
'''

import zstackwoodpecker.test_util as test_util
import test_stub
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.config_operations as conf_ops

def test():

    global deft_ha_1
    global deft_ha_2
    global deft_ha_3
    global deft_ha_4
    global deft_ha_5
    global deft_ha_6
    global deft_ha_7
    global deft_ha_8
    global deft_ha_9
    global deft_ha_10
    global deft_ha_11
    global deft_ha_12
    global deft_ha_13

    #get the default value
    deft_ha_1 = conf_ops.get_global_config_default_value('ha', 'host.selfFencer.maxAttempts')
    deft_ha_2 = conf_ops.get_global_config_default_value('ha', 'enable')
    deft_ha_3 = conf_ops.get_global_config_default_value('ha', 'neverStopVm.notification.times')
    deft_ha_4 = conf_ops.get_global_config_default_value('ha', 'neverStopVm.retry.delay')
    deft_ha_5 = conf_ops.get_global_config_default_value('ha', 'host.check.successInterval')
    deft_ha_6 = conf_ops.get_global_config_default_value('ha', 'host.check.maxAttempts')
    deft_ha_7 = conf_ops.get_global_config_default_value('ha', 'host.selfFencer.interval')
    deft_ha_8 = conf_ops.get_global_config_default_value('ha', 'host.check.successTimes')
    deft_ha_9 = conf_ops.get_global_config_default_value('ha', 'host.check.interval')
    deft_ha_10 = conf_ops.get_global_config_default_value('ha', 'neverStopVm.scan.interval')
    deft_ha_11 = conf_ops.get_global_config_default_value('ha', 'host.selfFencer.storageChecker.timeout')
    deft_ha_12 = conf_ops.get_global_config_default_value('ha', 'neverStopVm.gc.maxRetryIntervalTime')
    deft_ha_13 = conf_ops.get_global_config_default_value('ha', 'host.check.successRatio')


   # change the default value

    conf_ops.change_global_config('ha', 'host.selfFencer.maxAttempts', '12')
    conf_ops.change_global_config('ha', 'enable', 'false')
    conf_ops.change_global_config('ha', 'neverStopVm.notification.times', '12')
    conf_ops.change_global_config('ha', 'neverStopVm.retry.delay', '12')
    conf_ops.change_global_config('ha', 'host.check.successInterval', '12')
    conf_ops.change_global_config('ha', 'host.check.maxAttempts', '15')
    conf_ops.change_global_config('ha', 'host.selfFencer.interval', '12')
    conf_ops.change_global_config('ha', 'host.check.successTimes', '12')
    conf_ops.change_global_config('ha', 'host.check.interval', '12')
    conf_ops.change_global_config('ha', 'neverStopVm.scan.interval', '12')
    conf_ops.change_global_config('ha', 'host.selfFencer.storageChecker.timeout', '12')
    conf_ops.change_global_config('ha', 'neverStopVm.gc.maxRetryIntervalTime', '200')
    conf_ops.change_global_config('ha', 'host.check.successRatio', '0.6')



    # restore defaults

    conf_ops.change_global_config('ha', 'host.selfFencer.maxAttempts', '%s' % deft_ha_1)
    conf_ops.change_global_config('ha', 'enable', '%s' % deft_ha_2)
    conf_ops.change_global_config('ha', 'neverStopVm.notification.times', '%s' % deft_ha_3)
    conf_ops.change_global_config('ha', 'neverStopVm.retry.delay', '%s' % deft_ha_4)
    conf_ops.change_global_config('ha', 'host.check.successInterval', '%s' % deft_ha_5)
    conf_ops.change_global_config('ha', 'host.check.maxAttempts', '%s' % deft_ha_6)
    conf_ops.change_global_config('ha', 'host.selfFencer.interval', '%s' % deft_ha_7)
    conf_ops.change_global_config('ha', 'host.check.successTimes', '%s' % deft_ha_8)
    conf_ops.change_global_config('ha', 'host.check.interval', '%s' % deft_ha_9)
    conf_ops.change_global_config('ha', 'neverStopVm.scan.interval', '%s' % deft_ha_10)
    conf_ops.change_global_config('ha', 'host.selfFencer.storageChecker.timeout', '%s' % deft_ha_11)
    conf_ops.change_global_config('ha', 'neverStopVm.gc.maxRetryIntervalTime', '%s' % deft_ha_12)
    conf_ops.change_global_config('ha', 'host.check.successRatio', '%s' % deft_ha_13)


#Will be called only if exception happens in test().
def error_cleanup():
    global deft_ha_1

