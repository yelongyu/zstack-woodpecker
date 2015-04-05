'''

Test utility for destroy all current user vms, not including appliance VMs.

@author: Youyk
'''

import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_util as test_util
import threading
import time

def test():
    vms = test_lib.lib_get_all_user_vms()
    for vm in vms:
        thread = threading.Thread(target=vm_ops.destroy_vm, args=(vm.uuid,))
        thread.start()

    while threading.active_count() > 1:
        time.sleep(0.2)

    test_util.test_pass('Destroy User VMs Success')
