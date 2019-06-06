# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import os

test_stub = test_lib.lib_get_test_stub()

mini = None
qga_image_name = os.getenv('testQGAImageName')
qga_image_url = os.getenv('testQGAImageUrl')

def test():
    global mini
    mini = test_stub.MINI()
    mini.add_image(name=qga_image_name, url=qga_image_url)
    mini.create_vm(image=qga_image_name)
    mini.set_qga(mini.vm_name, qga=True)
    mini.change_vm_password(mini.vm_name)
    mini.change_vm_password(mini.vm_name, password='password')
    mini.set_qga(mini.vm_name, qga=False)
    mini.check_browser_console_log()
    test_util.test_pass('Test Change VM Password Successfully')


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
