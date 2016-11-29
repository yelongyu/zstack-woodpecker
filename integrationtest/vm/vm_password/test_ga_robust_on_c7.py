'''
test for batch changing vm password
@author: SyZhao
'''

import apibinding.inventory as inventory
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstacklib.utils.ssh as ssh
import threading
import test_stub


vm_num = 3
max_cnt = 100
keep_vm_num = 8
ga_process_not_alive_num = 0

vms  = []
ts   = []
invs = []


def check_qemu_ga_is_alive(vm):
    global ga_process_not_alive_num
    vm.check()
    cmd = "ps -aux|grep ga|grep qemu"
    ret, output, stderr = ssh.execute(cmd, vm.get_vm().vmNics[0].ip, "root", "password", False, 22)
    if ret != 0:
        test_util.test_logger("qemu-ga is not alived when exception triggered: ip:%s; cmd:%s; user:%s; password:%s; stdout:%s, stderr:%s" %(vm.get_vm().vmNics[0].ip, cmd, "root", "password", output, stderr))
        ga_process_not_alive_num = ga_process_not_alive_num + 1
    return ret


def change_vm_password_wrapper(vm_uuid, usr, passwd, skip_stopped_vm = None, session_uuid = None):
    global invs

    inv = vm_ops.change_vm_password(vm_uuid, usr, passwd, skip_stopped_vm, session_uuid)
    if inv:
        invs.append(inv)


def vm_reboot_wrapper(vm, cnt):
    test_util.test_logger("loop cnt:%d" %(int(cnt)))
    if vm:
        vm.check()
        vm.stop()
        vm.check()
        vm.start()
        vm.check()
    else:
        test_util.test_logger("vm is null")




def test():
    global vms, ts, invs
    global ga_process_not_alive_num
    test_util.test_dsc('create VM with setting password')

    for i in range(vm_num):
        vms.append(test_stub.create_vm(vm_name = 'c7-vm'+str(i), image_name = "batch_test_image"))
    
    for vm in vms:
        t = threading.Thread(target=change_vm_password_wrapper, args=(vm.get_vm().uuid, "root", "password"))
        ts.append(t)
        t.start()

    for t in ts:
        t.join()

    for cnt in range(max_cnt):
        test_util.test_dsc("this is loop:%d" %(cnt))

        for vm in vms:
            t = threading.Thread(target=vm_reboot_wrapper, args=(vm, cnt))
            ts.append(t)
            t.start()

        for t in ts:
            t.join()

        for vm in vms:
            if check_qemu_ga_is_alive(vm) != 0:
                keep_vm_num = keep_vm_num-1
                vms.remove(vm)
                vms.append(test_stub.create_vm(vm_name = 'c7-vm-new', image_name = "batch_test_image"))
                if keep_vm_num >= 0:
                    continue
                else:
                    vm.destroy()
                    vm.expunge()
            

    for vm in vms:
        if vm:
            vm.destroy()
            vm.expunge()

    test_util.test_fail('total vm reboot times:%s; ga not existed vm:%s' %(vm_num*max_cnt, ga_process_not_alive_num))

#Will be called only if exception happens in test().
def error_cleanup():
    global vms
    pass
    #for vm in vms:
    #    if vm:
    #        vm.destroy()
    #        vm.expunge()
