# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import os
import vm

vm_ops = None
network_list = [os.getenv('l3PublicNetworkName'), os.getenv('l3VlanNetworkName1'), os.getenv('l3VlanNetworkName2')]

def test():
    global vm_ops
    vm_ops = vm.VM()
    vm_ops.create_vm(network=network_list)
    vm_ops.check_browser_console_log()
    test_util.test_pass('Create VM With Multi-Networks Successful')


def env_recover():
    global vm_ops
    vm_ops.expunge_vm()
    vm_ops.close()

#Will be called only if exception happens in test().
def error_cleanup():
    global vm_ops
    try:
        vm_ops.expunge_vm()
        vm_ops.close()
    except:
        pass
