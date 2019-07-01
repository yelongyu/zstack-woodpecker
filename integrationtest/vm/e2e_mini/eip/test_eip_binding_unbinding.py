# -*- coding:UTF-8 -*-
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import os

vm = test_lib.lib_get_specific_stub(suite_name='e2e_mini/vms', specific_name='vm')
eip = test_lib.lib_get_specific_stub(suite_name='e2e_mini/eip', specific_name='eip')
network = os.getenv('l3NoVlanNetworkName1')

eip_ops = None
vm_ops = None

def test():
    global eip_ops
    global vm_ops
    eip_ops = eip.EIP()
    vm_ops = vm.VM(uri=eip_ops.uri, initialized=True)
    eip_ops.create_eip()
    vm_ops.create_vm(network=network)
    eip_ops.eip_binding(eip_ops.eip_name, vm_ops.vm_name)
    eip_ops.eip_unbinding(eip_ops.eip_name)
    eip_ops.check_browser_console_log()
    test_util.test_pass('Test EIP Binding Unbinding Successful')

def env_recover():
    global eip_ops
    global vm_ops
    eip_ops.delete_eip()
    vm_ops.delete_vm()
    eip_ops.close()

def error_cleanup():
    global eip_ops
    global vm_ops
    try:
        eip_ops.delete_eip()
        vm_ops.delete_vm()
        eip_ops.close()
    except:
        pass
