'''
test pub vm connectivity
1. check whether vm can reach public ip
2. check whether two vms can ping each other successfully

@author: chen.zhou
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.resource_operations as res_ops
import time
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def check_vm1_ping_vm2(vm_inv, target_ip):
    try:
        test_stub.run_command_in_vm(vm_inv, 'ping -c 4 %s'%target_ip)
    except:
        test_util.test_logger('ping %s failed' % target_ip)
        return False
    else:
        test_util.test_logger('ping %s successfully' % target_ip)
        return True

def test():
    pub_l3_name = os.environ.get('l3PublicNetworkName')
    pub_l3_uuid = test_lib.lib_get_l3_by_name(pub_l3_name).uuid

    vm1 = test_stub.create_vm('pub_vm_1', [pub_l3_uuid])
    test_obj_dict.add_vm(vm1)
    vm1.check()

    vm2 = test_stub.create_vm('pub_vm_2', [pub_l3_uuid])
    test_obj_dict.add_vm(vm2)
    vm2.check()

    test_util.test_dsc("test two vm connectivity")

    vm1_ip = vm1.get_vm().vmNics[0].ip
    vm2_ip = vm2.get_vm().vmNics[0].ip

    for vm in (vm1,vm2):
        test_stub.run_command_in_vm(vm.get_vm(), 'iptables -F')

    # ping DNS 223.5.5.5 to test whether vm can reach public ip
        test_stub.run_command_in_vm(vm.get_vm(), 'ping -c 4 223.5.5.5')

    # check tcp connection between vm1 and vm2
    #   test_util.test_dsc('Start to ssh %s' % vm.get_vm().vmNics[0].ip)
    #   if test_stub.run_command_in_vm(vm.get_vm(), 'sshpass -p password ssh root@%s' % vm.get_vm().vmNics[0].ip) == 'false':
    #       test_util.test_fail('two vms can not ssh each other' )

    test_util.test_dsc('Start to check ping connection between vm1 and vm2')
    # check ping connection bewteen vm1 and vm2
    rsp = check_vm1_ping_vm2(vm1.get_vm(), vm2_ip)
    if rsp == False:
        test_util.test_fail('ping %s failed' % vm2_ip)
    rsp_1 = check_vm1_ping_vm2(vm2.get_vm(), vm1_ip)
    if rsp_1 == False:
        test_util.test_fail('ping %s failed' % vm1_ip)

def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)