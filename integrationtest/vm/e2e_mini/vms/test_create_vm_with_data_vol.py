# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib

test_stub = test_lib.lib_get_test_stub()

mini = None

def test():
    global mini
    mini = test_stub.MINI()
    mini.create_vm(provisioning=u'厚置备', data_size='2 GB')
    mini.create_vm(provisioning=u'精简置备', data_size='2 GB', view='list')
    test_util.test_pass('Create VM with Data Volume Successful')


def env_recover():
    global mini
    mini.delete_vm(corner_btn=False)
    mini.close()

#Will be called only if exception happens in test().
def error_cleanup():
    global mini
    try:
        mini.delete_vm(corner_btn=False)
        mini.close()
    except:
        pass
