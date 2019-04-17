'''
check the global_config category is image
@author YeTian  2018-09-20
'''

import zstackwoodpecker.test_util as test_util
#import test_stub
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.config_operations as conf_ops

def test():

    global deft_image_1
    global deft_image_2
    global deft_image_3
    global deft_image_4
    global deft_image_5
    #get the default value
    deft_image_1 = conf_ops.get_global_config_default_value('image', 'deletionPolicy')
    deft_image_2 = conf_ops.get_global_config_default_value('image', 'deletion.gcInterval')
    deft_image_3 = conf_ops.get_global_config_default_value('image', 'expungeInterval')
    deft_image_4 = conf_ops.get_global_config_default_value('image', 'expungePeriod')
    deft_image_5 = conf_ops.get_global_config_default_value('image', 'enableResetPassword')


   # change the default value

    conf_ops.change_global_config('image', 'deletionPolicy', 'Direct')
    conf_ops.change_global_config('image', 'deletion.gcInterval', '1800')
    conf_ops.change_global_config('image', 'expungeInterval', '1800')
    conf_ops.change_global_config('image', 'expungePeriod', '3600')
    conf_ops.change_global_config('image', 'enableResetPassword', 'false')


    # restore defaults

    conf_ops.change_global_config('image', 'deletionPolicy', '%s' % deft_image_1)
    conf_ops.change_global_config('image', 'deletion.gcInterval', '%s' % deft_image_2)
    conf_ops.change_global_config('image', 'expungeInterval', '%s' % deft_image_3)
    conf_ops.change_global_config('image', 'expungePeriod', '%s' % deft_image_4)
    conf_ops.change_global_config('image', 'enableResetPassword', '%s' % deft_image_5)


#Will be called only if exception happens in test().
def error_cleanup():
    global deft_image_1

