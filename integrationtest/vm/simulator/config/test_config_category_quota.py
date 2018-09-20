'''
check the global_config category is quota
@author YeTian  2018-09-20
'''

import zstackwoodpecker.test_util as test_util
import test_stub
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.config_operations as conf_ops

def test():

    global deft_quota_1
    global deft_quota_2
    global deft_quota_3
    global deft_quota_4
    global deft_quota_5
    global deft_quota_6
    global deft_quota_7
    global deft_quota_8
    global deft_quota_9
    global deft_quota_10
    global deft_quota_11
    global deft_quota_12
    global deft_quota_13
    global deft_quota_14
    global deft_quota_15
    global deft_quota_16
    global deft_quota_17
    global deft_quota_18
    global deft_quota_19
    global deft_quota_20
    global deft_quota_21
    global deft_quota_22
    global deft_quota_23
    global deft_quota_24

    #get the default value
    deft_quota_1 = conf_ops.get_global_config_default_value('quota', 'image.size')
    deft_quota_2 = conf_ops.get_global_config_default_value('quota', 'sns.endpoint.num')
    deft_quota_3 = conf_ops.get_global_config_default_value('quota', 'vm.memorySize')
    deft_quota_4 = conf_ops.get_global_config_default_value('quota', 'eip.num')
    deft_quota_5 = conf_ops.get_global_config_default_value('quota', 'image.num')
    deft_quota_6 = conf_ops.get_global_config_default_value('quota', 'pci.num')
    deft_quota_7 = conf_ops.get_global_config_default_value('quota', 'vip.num')
    deft_quota_8 = conf_ops.get_global_config_default_value('quota', 'affinitygroup.num')
    deft_quota_9 = conf_ops.get_global_config_default_value('quota', 'volume.data.num')
    deft_quota_10 = conf_ops.get_global_config_default_value('quota', 'l3.num')
    deft_quota_11 = conf_ops.get_global_config_default_value('quota', 'securityGroup.num')
    deft_quota_12 = conf_ops.get_global_config_default_value('quota', 'scheduler.num')
    deft_quota_13 = conf_ops.get_global_config_default_value('quota', 'portForwarding.num')
    deft_quota_14 = conf_ops.get_global_config_default_value('quota', 'zwatch.event.num')
    deft_quota_15 = conf_ops.get_global_config_default_value('quota', 'listener.num')
    deft_quota_16 = conf_ops.get_global_config_default_value('quota', 'zwatch.alarm.num')
    deft_quota_17 = conf_ops.get_global_config_default_value('quota', 'vm.cpuNum')
    deft_quota_18 = conf_ops.get_global_config_default_value('quota', 'vm.totalNum')
    deft_quota_19 = conf_ops.get_global_config_default_value('quota', 'snapshot.volume.num')
    deft_quota_20 = conf_ops.get_global_config_default_value('quota', 'loadBalancer.num')
    deft_quota_21 = conf_ops.get_global_config_default_value('quota', 'vm.num')
    deft_quota_22 = conf_ops.get_global_config_default_value('quota', 'volume.capacity')
    deft_quota_23 = conf_ops.get_global_config_default_value('quota', 'vxlan.num')
    deft_quota_24 = conf_ops.get_global_config_default_value('quota', 'scheduler.trigger.num')


   # change the default value

    conf_ops.change_global_config('quota', 'image.size', '1048576')
    conf_ops.change_global_config('quota', 'sns.endpoint.num', '78')
    conf_ops.change_global_config('quota', 'vm.memorySize', '1048576')
    conf_ops.change_global_config('quota', 'eip.num', '78')
    conf_ops.change_global_config('quota', 'image.num', '78')
    conf_ops.change_global_config('quota', 'pci.num', '78')
    conf_ops.change_global_config('quota', 'vip.num', '78')
    conf_ops.change_global_config('quota', 'affinitygroup.num', '78')
    conf_ops.change_global_config('quota', 'volume.data.num', '78')
    conf_ops.change_global_config('quota', 'l3.num', '78')
    conf_ops.change_global_config('quota', 'securityGroup.num', '78')
    conf_ops.change_global_config('quota', 'scheduler.num', '78')
    conf_ops.change_global_config('quota', 'portForwarding.num', '78')
    conf_ops.change_global_config('quota', 'zwatch.event.num', '78')
    conf_ops.change_global_config('quota', 'listener.num', '78')
    conf_ops.change_global_config('quota', 'zwatch.alarm.num', '78')
    conf_ops.change_global_config('quota', 'vm.cpuNum', '78')
    conf_ops.change_global_config('quota', 'vm.totalNum', '78')
    conf_ops.change_global_config('quota', 'snapshot.volume.num', '78')
    conf_ops.change_global_config('quota', 'loadBalancer.num', '78')
    conf_ops.change_global_config('quota', 'vm.num', '78')
    conf_ops.change_global_config('quota', 'volume.capacity', '1048576')
    conf_ops.change_global_config('quota', 'vxlan.num', '78')
    conf_ops.change_global_config('quota', 'scheduler.trigger.num', '78')

    # restore defaults

    conf_ops.change_global_config('quota', 'image.size', '%s' % deft_quota_1)
    conf_ops.change_global_config('quota', 'sns.endpoint.num', '%s' % deft_quota_2)
    conf_ops.change_global_config('quota', 'vm.memorySize', '%s' % deft_quota_3)
    conf_ops.change_global_config('quota', 'eip.num', '%s' % deft_quota_4)
    conf_ops.change_global_config('quota', 'image.num', '%s' % deft_quota_5)
    conf_ops.change_global_config('quota', 'pci.num', '%s' % deft_quota_6)
    conf_ops.change_global_config('quota', 'vip.num', '%s' % deft_quota_7)
    conf_ops.change_global_config('quota', 'affinitygroup.num', '%s' % deft_quota_8)
    conf_ops.change_global_config('quota', 'volume.data.num', '%s' % deft_quota_9)
    conf_ops.change_global_config('quota', 'l3.num', '%s' % deft_quota_10)
    conf_ops.change_global_config('quota', 'securityGroup.num', '%s' % deft_quota_11)
    conf_ops.change_global_config('quota', 'scheduler.num', '%s' % deft_quota_12)
    conf_ops.change_global_config('quota', 'portForwarding.num', '%s' % deft_quota_13)
    conf_ops.change_global_config('quota', 'zwatch.event.num', '%s' % deft_quota_14)
    conf_ops.change_global_config('quota', 'listener.num', '%s' % deft_quota_15)
    conf_ops.change_global_config('quota', 'zwatch.alarm.num', '%s' % deft_quota_16)
    conf_ops.change_global_config('quota', 'vm.cpuNum', '%s' % deft_quota_17)
    conf_ops.change_global_config('quota', 'vm.totalNum', '%s' % deft_quota_18)
    conf_ops.change_global_config('quota', 'snapshot.volume.num', '%s' % deft_quota_19)
    conf_ops.change_global_config('quota', 'loadBalancer.num', '%s' % deft_quota_20)
    conf_ops.change_global_config('quota', 'vm.num', '%s' % deft_quota_21)
    conf_ops.change_global_config('quota', 'volume.capacity', '%s' % deft_quota_22)
    conf_ops.change_global_config('quota', 'vxlan.num', '%s' % deft_quota_23)
    conf_ops.change_global_config('quota', 'scheduler.trigger.num', '%s' % deft_quota_24)


#Will be called only if exception happens in test().
def error_cleanup():
    global deft_quota_1

