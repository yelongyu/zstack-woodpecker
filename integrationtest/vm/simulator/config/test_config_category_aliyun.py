'''
check the global_config category is aliyun
@author YeTian  2018-09-20
'''

import zstackwoodpecker.test_util as test_util
import test_stub
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.config_operations as conf_ops

def test():

    global deft_aliyun_1
    global deft_aliyun_2
    global deft_aliyun_3
    global deft_aliyun_4
    global deft_aliyun_5
    #get the default value
    deft_aliyun_1 = conf_ops.get_global_config_default_value('aliyun', 'upload.ecs.image.format')
    deft_aliyun_2 = conf_ops.get_global_config_default_value('aliyun', 'aliyun.openapi.page.size')
    deft_aliyun_3 = conf_ops.get_global_config_default_value('aliyun', 'aliyun.api.console.domain')
    deft_aliyun_4 = conf_ops.get_global_config_default_value('aliyun', 'aliyun.api.console.domain.check.timeout')
    deft_aliyun_5 = conf_ops.get_global_config_default_value('aliyun', 'user.define.api.endpoint')


   # change the default value

    conf_ops.change_global_config('aliyun', 'upload.ecs.image.format', 'qcow2')
    conf_ops.change_global_config('aliyun', 'aliyun.openapi.page.size', '30')
    conf_ops.change_global_config('aliyun', 'aliyun.api.console.domain', 'aliyun:443')
    conf_ops.change_global_config('aliyun', 'aliyun.api.console.domain.check.timeout', '300')
    conf_ops.change_global_config('aliyun', 'user.define.api.endpoint', 'test')


    # restore defaults

    conf_ops.change_global_config('aliyun', 'upload.ecs.image.format', '%s' % deft_aliyun_1)
    conf_ops.change_global_config('aliyun', 'aliyun.openapi.page.size', '%s' % deft_aliyun_2)
    conf_ops.change_global_config('aliyun', 'aliyun.api.console.domain', '%s' % deft_aliyun_3)
    conf_ops.change_global_config('aliyun', 'aliyun.api.console.domain.check.timeout', '%s' % deft_aliyun_4)
    conf_ops.change_global_config('aliyun', 'user.define.api.endpoint', '%s' % deft_aliyun_5)


#Will be called only if exception happens in test().
def error_cleanup():
    global deft_aliyun_1

