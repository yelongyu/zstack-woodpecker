'''
check the global_config category is sharedblock
@author YeTian  2018-09-20
'''

import zstackwoodpecker.test_util as test_util
#import test_stub
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.config_operations as conf_ops

def test():

    global deft_sharedblock_1
    global deft_sharedblock_2
    global deft_sharedblock_3
    global deft_sharedblock_4
    global deft_sharedblock_5
    global deft_sharedblock_6
    global deft_sharedblock_7

    #get the default value
    deft_sharedblock_1 = conf_ops.get_global_config_default_value('sharedblock', 'deletion.gcInterval')
    deft_sharedblock_2 = conf_ops.get_global_config_default_value('sharedblock', 'disable.host.when.storage.failure')
    deft_sharedblock_3 = conf_ops.get_global_config_default_value('sharedblock', 'qcow2.allocation')
    deft_sharedblock_4 = conf_ops.get_global_config_default_value('sharedblock', 'fencer.check.io')
    deft_sharedblock_5 = conf_ops.get_global_config_default_value('sharedblock', 'snapshot.shrink')
    deft_sharedblock_6 = conf_ops.get_global_config_default_value('sharedblock', 'snapshot.compare')
    deft_sharedblock_7 = conf_ops.get_global_config_default_value('sharedblock', 'qcow2.cluster.size')
   # change the default value

    conf_ops.change_global_config('sharedblock', 'deletion.gcInterval', '1800')
    conf_ops.change_global_config('sharedblock', 'disable.host.when.storage.failure', 'true')
    conf_ops.change_global_config('sharedblock', 'qcow2.allocation', 'none')
    conf_ops.change_global_config('sharedblock', 'fencer.check.io', 'true')
    conf_ops.change_global_config('sharedblock', 'snapshot.shrink', 'true')
    conf_ops.change_global_config('sharedblock', 'snapshot.compare', 'false')
    conf_ops.change_global_config('sharedblock', 'qcow2.cluster.size', '1024')

    # restore defaults

    conf_ops.change_global_config('sharedblock', 'deletion.gcInterval', '%s' % deft_sharedblock_1)
    conf_ops.change_global_config('sharedblock', 'disable.host.when.storage.failure', '%s' % deft_sharedblock_2)
    conf_ops.change_global_config('sharedblock', 'qcow2.allocation', '%s' % deft_sharedblock_3)
    conf_ops.change_global_config('sharedblock', 'fencer.check.io', '%s' % deft_sharedblock_4)
    conf_ops.change_global_config('sharedblock', 'snapshot.shrink', '%s' % deft_sharedblock_5)
    conf_ops.change_global_config('sharedblock', 'snapshot.compare', '%s' % deft_sharedblock_6)
    conf_ops.change_global_config('sharedblock', 'qcow2.cluster.size', '%s' % deft_sharedblock_7)


#Will be called only if exception sharedblockppens in test().
def error_cleanup():
    global deft_sharedblock_1

