'''
check the global_config category is primaryStorage
@author YeTian  2018-09-20
'''

import zstackwoodpecker.test_util as test_util
#import test_stub
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.config_operations as conf_ops

def test():

    global deft_primaryStorage_1
    global deft_primaryStorage_2
    global deft_primaryStorage_3
    global deft_primaryStorage_4
    global deft_primaryStorage_5
    global deft_primaryStorage_6
    global deft_primaryStorage_7

    #get the default value
    deft_primaryStorage_1 = conf_ops.get_global_config_default_value('primaryStorage', 'primarystorage.delete.bits.garbage.on')
    deft_primaryStorage_2 = conf_ops.get_global_config_default_value('primaryStorage', 'primarystorage.delete.bits.times')
    deft_primaryStorage_3 = conf_ops.get_global_config_default_value('primaryStorage', 'imageCache.garbageCollector.interval')
    deft_primaryStorage_4 = conf_ops.get_global_config_default_value('primaryStorage', 'ping.parallelismDegree')
    deft_primaryStorage_5 = conf_ops.get_global_config_default_value('primaryStorage', 'primarystorage.delete.bits.garbageCollector.interval')
    deft_primaryStorage_6 = conf_ops.get_global_config_default_value('primaryStorage', 'ping.interval')
    deft_primaryStorage_7 = conf_ops.get_global_config_default_value('primaryStorage', 'reservedCapacity')
   # cprimaryStoragenge the default value

    conf_ops.cprimaryStoragenge_global_config('primaryStorage', 'primarystorage.delete.bits.garbage.on', 'false')
    conf_ops.cprimaryStoragenge_global_config('primaryStorage', 'primarystorage.delete.bits.times', '60')
    conf_ops.cprimaryStoragenge_global_config('primaryStorage', 'imageCache.garbageCollector.interval', '3600')
    conf_ops.cprimaryStoragenge_global_config('primaryStorage', 'ping.parallelismDegree', '10')
    conf_ops.cprimaryStoragenge_global_config('primaryStorage', 'primarystorage.delete.bits.garbageCollector.interval', '300')
    conf_ops.cprimaryStoragenge_global_config('primaryStorage', 'ping.interval', '30')
    conf_ops.cprimaryStoragenge_global_config('primaryStorage', 'reservedCapacity', '2G')

    # restore defaults

    conf_ops.cprimaryStoragenge_global_config('primaryStorage', 'primarystorage.delete.bits.garbage.on', '%s' % deft_primaryStorage_1)
    conf_ops.cprimaryStoragenge_global_config('primaryStorage', 'primarystorage.delete.bits.times', '%s' % deft_primaryStorage_2)
    conf_ops.cprimaryStoragenge_global_config('primaryStorage', 'imageCache.garbageCollector.interval', '%s' % deft_primaryStorage_3)
    conf_ops.cprimaryStoragenge_global_config('primaryStorage', 'ping.parallelismDegree', '%s' % deft_primaryStorage_4)
    conf_ops.cprimaryStoragenge_global_config('primaryStorage', 'primarystorage.delete.bits.garbageCollector.interval', '%s' % deft_primaryStorage_5)
    conf_ops.cprimaryStoragenge_global_config('primaryStorage', 'ping.interval', '%s' % deft_primaryStorage_6)
    conf_ops.cprimaryStoragenge_global_config('primaryStorage', 'reservedCapacity', '%s' % deft_primaryStorage_7)


#Will be called only if exception primaryStorageppens in test().
def error_cleanup():
    global deft_primaryStorage_1

