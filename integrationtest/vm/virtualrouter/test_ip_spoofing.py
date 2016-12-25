'''
@author: MengLai
'''
import os
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    global test_obj_dict
    vm = test_stub.create_basic_vm()
    test_obj_dict.add_vm(vm)
    vm.check()
    vm_inv = vm.get_vm()
    vm_ip = vm_inv.vmNics[0].ip
    node_ip = os.environ.get('node1Ip')

    cmd = "ping %s -c 10" % node_ip
    rsp = test_lib.lib_execute_ssh_cmd(vm_ip, 'root', 'password', cmd, 180)    
    if rsp == False:
        test_util.test_fail('vm fail to ping %s' % node_ip)
    if '0% packet loss' not in rsp:
        test_util.test_fail('vm fail to get 100% packet') 

    new_vm_ip = '172.20.1.1'
    if new_vm_ip == vm_ip:
        new_vm_ip = '172.20.1.2' 
    cmd = "ifconfig eth0 %s" % new_vm_ip
    rsp = test_lib.lib_execute_ssh_cmd(vm_ip, 'root', 'password', cmd, 180)

    cmd = "ping %s -c 10" % node_ip
    rsp = test_lib.lib_execute_ssh_cmd(new_vm_ip, 'root', 'password', cmd, 1800)
    if rsp == True:
        test_util.test_fail('vm is expected to fail to ping %s' % node_ip)
    if '100% packet loss' not in rsp:
        test_util.test_fail('vm is expected to get 0% packet')
    
    vm.destroy()
    test_obj_dict.rm_vm(vm)
    test_util.test_pass('IP Spoofing Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
