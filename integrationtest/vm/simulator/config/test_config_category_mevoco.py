'''
check the global_config category is vm
@author YeTian  2018-09-20
'''

import zstackwoodpecker.test_util as test_util
#import test_stub
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.config_operations as conf_ops

def test():

    global deft_mevoco_1
    global deft_mevoco_2
    global deft_mevoco_3
    global deft_mevoco_4
    global deft_mevoco_5
    global deft_mevoco_6
    global deft_mevoco_7
    global deft_mevoco_8
    global deft_mevoco_9
    global deft_mevoco_10
    global deft_mevoco_11
    global deft_mevoco_12

    #get the default value
    deft_mevoco_1 = conf_ops.get_global_config_default_value('mevoco', 'apiRetry.vm')
    deft_mevoco_2 = conf_ops.get_global_config_default_value('mevoco', 'overProvisioning.memory')
    deft_mevoco_3 = conf_ops.get_global_config_default_value('mevoco', 'aio.native')
    deft_mevoco_4 = conf_ops.get_global_config_default_value('mevoco', 'qcow2.allocation')
    deft_mevoco_5 = conf_ops.get_global_config_default_value('mevoco', 'vm.consoleMode')
    deft_mevoco_6 = conf_ops.get_global_config_default_value('mevoco', 'hostAllocatorStrategy')
    deft_mevoco_7 = conf_ops.get_global_config_default_value('mevoco', 'distributeImage.concurrency')
    deft_mevoco_8 = conf_ops.get_global_config_default_value('mevoco', 'apiRetry.interval.vm')
    deft_mevoco_9 = conf_ops.get_global_config_default_value('mevoco', 'qcow2.cluster.size')
    deft_mevoco_10 = conf_ops.get_global_config_default_value('mevoco', 'distributeImage')
    deft_mevoco_11 = conf_ops.get_global_config_default_value('mevoco', 'threshold.primaryStorage.physicalCapacity')
    deft_mevoco_12 = conf_ops.get_global_config_default_value('mevoco', 'overProvisioning.primaryStorage')

   # change the default value

    conf_ops.change_global_config('mevoco', 'apiRetry.vm', '5')
    conf_ops.change_global_config('mevoco', 'overProvisioning.memory', '2.0')
    conf_ops.change_global_config('mevoco', 'aio.native', 'true')
    conf_ops.change_global_config('mevoco', 'qcow2.allocation', 'metadata')
    conf_ops.change_global_config('mevoco', 'vm.consoleMode', 'spice')
    conf_ops.change_global_config('mevoco', 'hostAllocatorStrategy', 'MinimumCPUUsageHostAllocatorStrategy')
    conf_ops.change_global_config('mevoco', 'distributeImage.concurrency', '3')
    conf_ops.change_global_config('mevoco', 'apiRetry.interval.vm', '5')
    conf_ops.change_global_config('mevoco', 'qcow2.cluster.size', '1048576')
    conf_ops.change_global_config('mevoco', 'distributeImage', 'false')
    conf_ops.change_global_config('mevoco', 'threshold.primaryStorage.physicalCapacity', '0.8')
    conf_ops.change_global_config('mevoco', 'overProvisioning.primaryStorage', '2.0')

    # restore defaults

    conf_ops.change_global_config('mevoco', 'apiRetry.vm', '%s' % deft_mevoco_1)
    conf_ops.change_global_config('mevoco', 'overProvisioning.memory', '%s' % deft_mevoco_2)
    conf_ops.change_global_config('mevoco', 'aio.native', '%s' % deft_mevoco_3)
    conf_ops.change_global_config('mevoco', 'qcow2.allocation', '%s' % deft_mevoco_4)
    conf_ops.change_global_config('mevoco', 'vm.consoleMode', '%s' % deft_mevoco_5)
    conf_ops.change_global_config('mevoco', 'hostAllocatorStrategy', '%s' % deft_mevoco_6)
    conf_ops.change_global_config('mevoco', 'distributeImage.concurrency','%s' % deft_mevoco_7)
    conf_ops.change_global_config('mevoco', 'apiRetry.interval.vm', '%s' % deft_mevoco_8)
    conf_ops.change_global_config('mevoco', 'qcow2.cluster.size', '%s' % deft_mevoco_9)
    conf_ops.change_global_config('mevoco', 'distributeImage', '%s' % deft_mevoco_10)
    conf_ops.change_global_config('mevoco', 'threshold.primaryStorage.physicalCapacity', '%s' % deft_mevoco_11)
    conf_ops.change_global_config('mevoco', 'overProvisioning.primaryStorage', '%s' % deft_mevoco_12)

#Will be called only if exception happens in test().
def error_cleanup():
    global deft_mevoco_1

