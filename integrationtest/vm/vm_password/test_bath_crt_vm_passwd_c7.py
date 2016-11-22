'''
Batch creating vm with root password set
@author: SyZhao
'''

import apibinding.inventory as inventory
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import threading
import test_stub


vm_num = 3

vms = []
ts  = []

root_password_list = ["321"]


def create_vm_wrapper(vm_name, image_name, root_password):
    global vms
    vms.append(test_stub.create_vm(vm_name, image_name, root_password))


def test():
    global vms, ts
    test_util.test_dsc('create VM with setting password')

    for root_password in root_password_list:
        test_util.test_dsc("root_password: \"%s\"" %(root_password))
        
        for i in range(vm_num):
            vm_name = "VM%s" %(str(i))
            t = threading.Thread(target=create_vm_wrapper, args=('c7-'+vm_name, "imageName_i_c7", root_password))
            ts.append(t)
            t.start()

        for t in ts:
            t.join()

        for vm in vms:
            if not test_lib.lib_check_login_in_vm(vm.get_vm(), "root", root_password):
                test_util.test_fail("create vm with root password: %s failed", root_password)
            vm.destroy()
            vm.check()
            vm.expunge()
            vm.check()


    test_util.test_pass('Set password when VM is creating is successful.')



#Will be called only if exception happens in test().
def error_cleanup():
    global vms

    for vm in vms:
    if vm:
        vm.destroy()
        vm.expunge()
