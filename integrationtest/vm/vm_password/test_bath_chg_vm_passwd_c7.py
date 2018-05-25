'''
test for batch changing vm password
@author: SyZhao
'''

import apibinding.inventory as inventory
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.vm_operations as vm_ops
import threading
import test_stub
import time


vm_num = 3

vms  = []
ts   = []
invs = []

users   = ["root",      "root"     ]
passwds = ["password",  "95_aaapcn"]


def change_vm_password_wrapper(vm_uuid, usr, passwd, skip_stopped_vm = None, session_uuid = None):
    global invs

    inv = vm_ops.change_vm_password(vm_uuid, usr, passwd, skip_stopped_vm, session_uuid)
    if inv:
        invs.append(inv)



def test():
    global vms, ts, invs
    test_util.test_dsc('create VM with setting password')

    for (usr,passwd) in zip(users, passwds):
        test_util.test_dsc("user:%s; password:%s" %(usr, passwd))

        vms = []
        for i in range(vm_num):
            vms.append(test_stub.create_vm(vm_name = 'c7-vm'+str(i), image_name = "batch_test_image"))
        
        time.sleep(30)
        for vm in vms:
            t = threading.Thread(target=change_vm_password_wrapper, args=(vm.get_vm().uuid, usr, passwd))
            ts.append(t)
            t.start()

        for t in ts:
            t.join()


        for vm in vms:
            if not test_lib.lib_check_login_in_vm(vm.get_vm(), usr, passwd):
                test_util.test_fail("create vm with user:%s password: %s failed", usr, passwd)


        ts   = []
        invs = []

        #When vm is stopped:
        #for vm in vms:
        #    vm.stop()

        for vm in vms:
            t = threading.Thread(target=change_vm_password_wrapper, args=(vm.get_vm().uuid, "root", "password"))
            ts.append(t)
            t.start()

        for t in ts:
            t.join()


        for vm in vms:
            #vm.start()
            vm.check()

            vm.destroy()
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
