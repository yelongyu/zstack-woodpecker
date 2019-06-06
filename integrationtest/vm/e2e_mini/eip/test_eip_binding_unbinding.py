# -*- coding:UTF-8 -*-
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import os

test_stub = test_lib.lib_get_test_stub()
network = os.getenv('l3NoVlanNetworkName1')

mini = None

def test():
    global mini
    mini = test_stub.MINI()
    mini.create_eip()
    mini.create_vm(network=network)
    mini.eip_binding(mini.eip_name, mini.vm_name)
    mini.eip_unbinding(mini.eip_name)
    mini.check_browser_console_log()
    test_util.test_pass('Test EIP Binding Unbinding Successful')

def env_recover():
    global mini
    mini.delete_eip()
    mini.delete_vm()
    mini.close()

def error_cleanup():
    global mini
    try:
        mini.delete_eip()
        mini.delete_vm()
        mini.close()
    except:
        pass
