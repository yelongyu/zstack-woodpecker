'''
This case can not execute parallelly
@author: Youyk
'''
import os
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.header.vm as vm_header
import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstacklib.utils.linux as linux
import time

_config_ = {
        'timeout' : 1000,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def is_host_enabled(host_uuid):
    cond = res_ops.gen_query_conditions('uuid', '=', host_uuid)
    host = res_ops.query_resource(res_ops.HOST, cond)[0]
    if host.state == 'Enabled':
        return True

def is_host_disabled(host_uuid):
    cond = res_ops.gen_query_conditions('uuid', '=', host_uuid)
    host = res_ops.query_resource(res_ops.HOST, cond)[0]
    if host.state == 'Disabled':
        return True


def test():
    test_util.test_dsc('Test Host Start/Stop function')
    vm_cpu = 1
    vm_memory = 1073741824 #1G
    cond = res_ops.gen_query_conditions('name', '=', 'ttylinux')
    image_uuid = res_ops.query_resource(res_ops.IMAGE, cond)[0].uuid
    l3_network_uuid = res_ops.query_resource(res_ops.L3_NETWORK)[0].uuid
    vm = test_stub.create_mini_vm([l3_network_uuid], image_uuid, cpu_num = vm_cpu, memory_size = vm_memory)
    test_obj_dict.add_vm(vm)

    host_uuid = test_lib.lib_get_vm_host(vm.vm).uuid
    host_ops.change_host_state(host_uuid, 'disable')
    if not linux.wait_callback_success(is_host_disabled, host_uuid, 120):
        test_util.test_fail('host state is not changed to disabled')

    host_ops.change_host_state(host_uuid, 'enable')
    if not linux.wait_callback_success(is_host_enabled, host_uuid, 120):
        test_util.test_fail('host state is not changed to enabled')

    vm.destroy()
    test_obj_dict.rm_vm(vm)
    test_util.test_pass('Stop/Start Host Test Pass')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
