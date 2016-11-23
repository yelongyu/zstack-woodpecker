'''
Creating KVM VM with password set.
@author: SyZhao
'''

import apibinding.inventory as inventory
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.vm_operations as vm_ops
import threading
import test_stub


vm_num = 3

vms  = []
ts   = []
invs = []

users   = ["root",      "root"     ]
passwds = ["password",  "95_aaapcn"]


def change_vm_password_wrapper(vm_uuid, usr, passwd, skip_stopped_vm = None, session_uuid = None):
    global invs

    inv = vm_ops.change_vm_password(vm_uuid, usr, passwd, skip_stopped_vm, session_uuid)
    if not inv:
        test_util.test_fail("change vm password failed in wrapper")
    else:
        invs.append(inv)



def test():
    global vms, ts, invs
    test_util.test_dsc('create VM with setting password')

    for (usr,passwd) in zip(users, passwds):
        test_util.test_dsc("user:%s; password:%s" %(usr, passwd))

        for i in range(vm_num):
            vms.append(test_stub.create_vm(vm_name = 'c7-vm'+str(i), image_name = "batch_test_image"))
        
        for vm in vms:
            t = threading.Thread(target=change_vm_password_wrapper, args=(vm.get_vm().uuid, usr, passwd))
            ts.append(t)
            t.start()

        for t in ts:
            t.join()

        for inv in invs:
            if not inv:
                test_util.test_fail("Batch change vm password failed")

        if not test_lib.lib_check_login_in_vm(vm.get_vm(), usr, passwd):
            test_util.test_fail("create vm with user:%s password: %s failed", usr, passwd)


        vms  = []
        ts   = []
        invs = []

        #When vm is stopped:
        vm.stop()
        for vm in vms:
            t = threading.Thread(target=change_vm_password_wrapper, args=(vm.get_vm().uuid, usr, passwd))
            ts.append(t)
            t.start()

        for t in ts:
            t.join()

        for inv in invs:
            if not inv:
                test_util.test_fail("Batch change vm password failed")

        vm.start()
        vm.check()

        for vm in vms:
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
