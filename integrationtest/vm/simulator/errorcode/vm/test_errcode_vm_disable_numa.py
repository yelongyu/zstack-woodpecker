'''
 Update running VM's cpu/memory
 regex: "The state of vm[uuid:%s] is %s. Only these state[Running,Stopped] is allowed to update cpu or memory."
'''
import os
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.operations.errorcode_operations as errc_ops
from apibinding.api import ApiError
import sys
reload(sys)
sys.setdefaultencoding('utf8')

test_stub = test_lib.lib_get_test_stub()
regex = "The state of vm[uuid:%s] is %s. Only these state[Running,Stopped] is allowed to update cpu or memory."

check_message = None
check_message_list = errc_ops.get_elaborations(category = 'VM')
vm = None
def test():
    global vm
    test_stub.check_elaboration_properties()
    for message in check_message_list:
        if regex == message.regex:
            check_message =  message.message_cn.encode('utf8')
            break
    test_util.test_logger('@@@@DEBUG@@@@: %s' % check_message)
    #create vm and update vm's cpu/memory
    vm = test_stub.create_vm()
    vm_uuid = vm.get_vm().uuid
    vm_cpu_num = vm.get_vm().cpuNum + 1
    try:
        vm_ops.update_vm(vm_uuid, cpu=vm_cpu_num) 
    except ApiError as e:
        #ascii->unicode->utf8
        err_msg = str([e]).split('elaboration:')[1].decode('unicode-escape').encode('utf8')
        test_util.test_logger('@@@%s@@@%s@@@' % (check_message, err_msg))
        if check_message in err_msg or err_msg in check_message:
            test_util.test_pass("regex check pass,check_message:%s" % check_message)
        else:
            test_util.test_fail('@@DEBUG@@\n TEST FAILED\n %s' % err_msg)

def error_cleanup():
    if vm:
        vm.destroy()
        vm.expunge()
