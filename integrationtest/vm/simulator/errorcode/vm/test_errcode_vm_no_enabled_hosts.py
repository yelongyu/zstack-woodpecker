'''
  change all Hosts state to 'Maintenance' and start vm
  regex: "no Enabled hosts found in the \[[0-9]*] candidate hosts"
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
regex = "no Enabled hosts found in the \[[0-9]*] candidate hosts"

check_message = None
check_message_list = errc_ops.get_elaborations(category = 'VM')
vm = None

hosts = res_ops.query_resource(res_ops.HOST)
host_num = str(len(hosts))
maintain = 'maintain'
enable = 'enable'

def test():
    global vm
    test_stub.check_elaboration_properties()
    for message in check_message_list:
        if regex == message.regex:
            check_message =  message.message_cn.encode('utf8').replace('%1$s', host_num)
            break
    test_util.test_logger('@@@@DEBUG@@@@: %s' % check_message)
    #change all hosts state to maintain
    vm = test_stub.create_vm()
    vm_uuid = vm.get_vm().uuid
    for host in hosts:
        host_ops.change_host_state(host.uuid, maintain)
    try:
        vm_ops.start_vm(vm_uuid)
    except ApiError as e:
        #ascii->unicode->utf8
        err_msg = str([e]).decode('unicode-escape').encode('utf8')
        test_util.test_logger('@@@%s@@@%s@@@' % (check_message, err_msg))
        if check_message in err_msg or err_msg in check_message:
            test_util.test_pass("regex check pass,check_message:%s" % check_message)
        else:
            test_util.test_fail('@@DEBUG@@\n TEST FAILED\n %s' % err_msg)

def error_cleanup():
    if vm:
        vm.destroy()
        vm.expunge()
    for host in hosts:
        host_ops.change_host_state(host.uuid, enable)

def env_recover():
    if vm:
        vm.destroy()
        vm.expunge()
    for host in hosts:
        host_ops.change_host_state(host.uuid, enable)
