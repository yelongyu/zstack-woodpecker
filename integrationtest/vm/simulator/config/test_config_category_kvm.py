'''
check the global_config category is kvm
@author YeTian  2018-09-20
'''

import zstackwoodpecker.test_util as test_util
#import test_stub
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.config_operations as conf_ops

def test():

    global deft_kvm_1
    global deft_kvm_2
    global deft_kvm_3
    global deft_kvm_4
    global deft_kvm_5
    global deft_kvm_6
    global deft_kvm_7
    global deft_kvm_8
    global deft_kvm_9
    global deft_kvm_10
    global deft_kvm_11
    global deft_kvm_12
    global deft_kvm_13
    global deft_kvm_14
    global deft_kvm_15
    global deft_kvm_16

    #get the default value
    deft_kvm_1 = conf_ops.get_global_config_default_value('kvm', 'host.DNSCheckAliyun')
    deft_kvm_2 = conf_ops.get_global_config_default_value('kvm', 'ignoreMsrs')
    deft_kvm_3 = conf_ops.get_global_config_default_value('kvm', 'vm.cpuMode')
    deft_kvm_4 = conf_ops.get_global_config_default_value('kvm', 'vm.cacheMode')
    deft_kvm_5 = conf_ops.get_global_config_default_value('kvm', 'host.DNSCheck163')
    deft_kvm_6 = conf_ops.get_global_config_default_value('kvm', 'reservedCpu')
    deft_kvm_7 = conf_ops.get_global_config_default_value('kvm', 'checkHostCpuModelName')
    deft_kvm_8 = conf_ops.get_global_config_default_value('kvm', 'vmSyncOnHostPing')
    deft_kvm_9 = conf_ops.get_global_config_default_value('kvm', 'redhat.liveSnapshotOn')
    deft_kvm_10 = conf_ops.get_global_config_default_value('kvm', 'testSshPortOpenTimeout')
    deft_kvm_11 = conf_ops.get_global_config_default_value('kvm', 'vm.migrationQuantity')
    deft_kvm_12 = conf_ops.get_global_config_default_value('kvm', 'testSshPortOnConnectTimeout')
    deft_kvm_13 = conf_ops.get_global_config_default_value('kvm', 'reservedMemory')
    deft_kvm_14 = conf_ops.get_global_config_default_value('kvm', 'host.syncLevel')
    deft_kvm_15 = conf_ops.get_global_config_default_value('kvm', 'dataVolume.maxNum')
    deft_kvm_16 = conf_ops.get_global_config_default_value('kvm', 'host.DNSCheckList')


   # change the default value

    conf_ops.change_global_config('kvm', 'host.DNSCheckAliyun', 'ztack.org')
    conf_ops.change_global_config('kvm', 'ignoreMsrs', 'true')
    conf_ops.change_global_config('kvm', 'vm.cpuMode', 'host-model')
    conf_ops.change_global_config('kvm', 'vm.cacheMode', 'writethrough')
    conf_ops.change_global_config('kvm', 'host.DNSCheck163', 'zstack.org')
    conf_ops.change_global_config('kvm', 'reservedCpu', '1024')
    conf_ops.change_global_config('kvm', 'checkHostCpuModelName', 'true')
    conf_ops.change_global_config('kvm', 'vmSyncOnHostPing', 'false')
    conf_ops.change_global_config('kvm', 'redhat.liveSnapshotOn', 'true')
    conf_ops.change_global_config('kvm', 'testSshPortOpenTimeout', '150')
    conf_ops.change_global_config('kvm', 'vm.migrationQuantity', '4')
    conf_ops.change_global_config('kvm', 'testSshPortOnConnectTimeout', '4')
    conf_ops.change_global_config('kvm', 'reservedMemory', '2G')
    conf_ops.change_global_config('kvm', 'host.syncLevel', '5')
    conf_ops.change_global_config('kvm', 'dataVolume.maxNum', '22')
    conf_ops.change_global_config('kvm', 'host.DNSCheckList', 'qq.com,cctv.com')



    # restore defaults

    conf_ops.change_global_config('kvm', 'host.DNSCheckAliyun', '%s' % deft_kvm_1)
    conf_ops.change_global_config('kvm', 'ignoreMsrs', '%s' % deft_kvm_2)
    conf_ops.change_global_config('kvm', 'vm.cpuMode', '%s' % deft_kvm_3)
    conf_ops.change_global_config('kvm', 'vm.cacheMode', '%s' % deft_kvm_4)
    conf_ops.change_global_config('kvm', 'host.DNSCheck163', '%s' % deft_kvm_5)
    conf_ops.change_global_config('kvm', 'reservedCpu', '%s' % deft_kvm_6)
    conf_ops.change_global_config('kvm', 'checkHostCpuModelName', '%s' % deft_kvm_7)
    conf_ops.change_global_config('kvm', 'vmSyncOnHostPing', '%s' % deft_kvm_8)
    conf_ops.change_global_config('kvm', 'redhat.liveSnapshotOn', '%s' % deft_kvm_9)
    conf_ops.change_global_config('kvm', 'testSshPortOpenTimeout', '%s' % deft_kvm_10)
    conf_ops.change_global_config('kvm', 'vm.migrationQuantity', '%s' % deft_kvm_11)
    conf_ops.change_global_config('kvm', 'testSshPortOnConnectTimeout', '%s' % deft_kvm_12)
    conf_ops.change_global_config('kvm', 'reservedMemory', '%s' % deft_kvm_13)
    conf_ops.change_global_config('kvm', 'host.syncLevel', '%s' % deft_kvm_14)
    conf_ops.change_global_config('kvm', 'dataVolume.maxNum', '%s' % deft_kvm_15)
    conf_ops.change_global_config('kvm', 'host.DNSCheckList', '%s' % deft_kvm_16)


#Will be called only if exception happens in test().
def error_cleanup():
    global deft_kvm_1

