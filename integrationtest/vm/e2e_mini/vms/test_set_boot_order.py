# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import os

test_stub = test_lib.lib_get_test_stub()

mini = None
iso_name = os.getenv('testIsoName')
iso_url = os.getenv('testIsoUrl')

def test():
    global mini
    mini = test_stub.MINI()
    mini.add_image(name=iso_name, url=iso_url)
    mini.create_vm(image=iso_name, root_size='2 GB')
    mini.set_boot_order(mini.vm_name, cd_first=True)
    mini.set_boot_order(mini.vm_name, cd_first=False)
    mini.check_browser_console_log()
    test_util.test_pass('Test Set Boot Order Successfully')


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
