# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib

test_stub = test_lib.lib_get_test_stub()

mini = None
iso_name = 'test-iso'
iso_url = 'http://192.168.200.100/mirror/iso/CentOS-7-x86_64-DVD-1810.iso'

def test():
    global mini
    mini = test_stub.MINI()
    mini.add_image(name=iso_name, url=iso_url)
    mini.create_vm(image=iso_name, root_size='2 GB')
    mini.check_browser_console_log()
    test_util.test_pass('Create VM with ISO Image Successfully')


def env_recover():
    global mini
    mini.expunge_vm()
    mini.expunge_image()
    mini.close()

#Will be called only if exception happens in test().
def error_cleanup():
    global mini
    try:
        mini.expunge_vm()
        mini.expunge_image()
        mini.close()
    except:
        pass
