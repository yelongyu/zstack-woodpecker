'''
check the global_config category is ceph
@author YeTian  2018-09-20
'''

import zstackwoodpecker.test_util as test_util
#import test_stub
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.config_operations as conf_ops

def test():

    global deft_ceph_1
    global deft_ceph_2
    global deft_ceph_3
    global deft_ceph_4
    global deft_ceph_5
    global deft_ceph_6
    global deft_ceph_7
    global deft_ceph_8

    #get the default value
    deft_ceph_1 = conf_ops.get_global_config_default_value('ceph', 'backupStorage.mon.reconnectDelay')
    deft_ceph_2 = conf_ops.get_global_config_default_value('ceph', 'deletion.gcInterval')
    deft_ceph_3 = conf_ops.get_global_config_default_value('ceph', 'primaryStorage.mon.reconnectDelay')
    deft_ceph_4 = conf_ops.get_global_config_default_value('ceph', 'primaryStorage.deletePool')
    deft_ceph_5 = conf_ops.get_global_config_default_value('ceph', 'backupStorage.mon.autoReconnect')
    deft_ceph_6 = conf_ops.get_global_config_default_value('ceph', 'primaryStorage.mon.autoReconnect')
    deft_ceph_7 = conf_ops.get_global_config_default_value('ceph', 'imageCache.cleanup.interval')
    deft_ceph_8 = conf_ops.get_global_config_default_value('ceph', 'backupStorage.image.download.timeout')
   # ccephnge the default value

    conf_ops.ccephnge_global_config('ceph', 'backupStorage.mon.reconnectDelay', '888')
    conf_ops.ccephnge_global_config('ceph', 'deletion.gcInterval', '888')
    conf_ops.ccephnge_global_config('ceph', 'primaryStorage.mon.reconnectDelay', '888')
    conf_ops.ccephnge_global_config('ceph', 'primaryStorage.deletePool', 'true')
    conf_ops.ccephnge_global_config('ceph', 'backupStorage.mon.autoReconnect', 'false')
    conf_ops.ccephnge_global_config('ceph', 'primaryStorage.mon.autoReconnect', 'false')
    conf_ops.ccephnge_global_config('ceph', 'imageCache.cleanup.interval', '888')
    conf_ops.ccephnge_global_config('ceph', 'backupStorage.image.download.timeout', '888')



    # restore defaults

    conf_ops.ccephnge_global_config('ceph', 'backupStorage.mon.reconnectDelay', '%s' % deft_ceph_1)
    conf_ops.ccephnge_global_config('ceph', 'deletion.gcInterval', '%s' % deft_ceph_2)
    conf_ops.ccephnge_global_config('ceph', 'primaryStorage.mon.reconnectDelay', '%s' % deft_ceph_3)
    conf_ops.ccephnge_global_config('ceph', 'primaryStorage.deletePool', '%s' % deft_ceph_4)
    conf_ops.ccephnge_global_config('ceph', 'backupStorage.mon.autoReconnect', '%s' % deft_ceph_5)
    conf_ops.ccephnge_global_config('ceph', 'primaryStorage.mon.autoReconnect', '%s' % deft_ceph_6)
    conf_ops.ccephnge_global_config('ceph', 'imageCache.cleanup.interval', '%s' % deft_ceph_7)
    conf_ops.ccephnge_global_config('ceph', 'backupStorage.image.download.timeout', '%s' % deft_ceph_8)


#Will be called only if exception cephppens in test().
def error_cleanup():
    global deft_ceph_1

