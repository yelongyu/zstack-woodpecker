'''
Test MN monitor VM lifecycle START->RUNNING->STOPPED->RUNNING->PAUSED->RUNNING->PAUSED->STOPPED
@author:Mengying.li
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import time

test_stub = test_lib.lib_get_specific_stub()

vm=None

def test():
    global vm
    vm=test_stub.create_vm()
    vm.check()
    vm_inv=vm.get_vm()
    vm_uuid=vm_inv.uuid
    vm_state = vm.get_vm().state

    host_inv = test_lib.lib_find_host_by_vm(vm_inv)
    host_ip= host_inv.managementIp
    host_username=host_inv.username
    host_password=host_inv.password

    test_util.test_dsc('use virsh to stop vm in host')
    cmd='virsh destroy %s'% (vm_uuid)
    result=test_lib.lib_execute_ssh_cmd(host_ip, host_username, host_password, cmd, 180)
    if result == False :
        test_util.test_fail('Fail to execute cmd')

    for i in range(0, 60):
        vm.update()
        if vm.get_vm().state == 'Stopped':
            break
        time.sleep(1)

    if vm.get_vm().state != 'Stopped':
        test_util.test_fail('VM is expected to in state stopped, while its %s' % (vm.get_vm().state))


    test_util.test_dsc('use virsh to start vm in host')
    cmd = 'virsh start %s' % vm_uuid
    result=test_lib.lib_execute_ssh_cmd(host_ip, host_username, host_password, cmd,180)
    if result == False:
        test_util.test_fail('Fail to execute cmd')

    for i in range(0, 60):
        vm.update()
        if vm.get_vm().state == 'Running':
            break
        time.sleep(1)

    if vm.get_vm().state != 'Running':
        test_util.test_fail('VM is expected to in state running, while its %s' % (vm.get_vm().state))

    test_util.test_dsc('use virsh to suspend vm in host')
    cmd = 'virsh suspend %s' % vm_uuid
    result=test_lib.lib_execute_ssh_cmd(host_ip, host_username, host_password, cmd,180)
    if result == False:
        test_util.test_fail('Fail to execute cmd')

    for i in range(0, 60):
        vm.update()
        test_util.test_logger('%s' % vm.get_vm().state)

        if vm.get_vm().state == 'Paused':
            break
        time.sleep(1)

    if vm.get_vm().state != 'Paused':
        test_util.test_fail('VM is expected to in state suspended while its %s' % (vm.get_vm().state))

    test_util.test_dsc('use virsh to resume vm in host')
    cmd = 'virsh resume %s' % vm_uuid
    result=test_lib.lib_execute_ssh_cmd(host_ip, host_username, host_password, cmd,180)
    if result == False:
        test_util.test_fail('Fail to execute cmd')

    for i in range(0, 60):
        vm.update()
        if vm.get_vm().state == 'Running':
            break
        time.sleep(1)

    test_util.test_dsc('use virsh to suspend vm in host')
    if vm.get_vm().state != 'Running':
        test_util.test_fail('VM is expected to in state running while its %s' % (vm.get_vm().state))

    cmd = 'virsh suspend %s' % vm_uuid
    result=test_lib.lib_execute_ssh_cmd(host_ip, host_username, host_password, cmd,180)
    if result == False:
        test_util.test_fail('Fail to execute cmd')

    for i in range(0, 60):
        vm.update()
        test_util.test_logger('%s' % vm.get_vm().state)

        if vm.get_vm().state == 'Paused':
            break
        time.sleep(1)

    if vm.get_vm().state != 'Paused':
        test_util.test_fail('VM is expected to in state suspended while its %s' % (vm.get_vm().state))

    test_util.test_dsc('use virsh to stop vm in host')
    cmd='virsh destroy %s'% (vm_uuid)
    result=test_lib.lib_execute_ssh_cmd(host_ip, host_username, host_password, cmd, 180)
    if result == False :
        test_util.test_fail('Fail to execute cmd')

    for i in range(0, 60):
        vm.update()
        if vm.get_vm().state == 'Stopped':
            break
        time.sleep(1)

    if vm.get_vm().state != 'Stopped':
        test_util.test_fail('VM is expected to in state stopped, while its %s' % (vm.get_vm().state))

    vm.destroy()
    vm.check()
    test_util.test_pass('Test Success')

def error_cleanup():
     global vm
     if vm:
        vm.destroy()


