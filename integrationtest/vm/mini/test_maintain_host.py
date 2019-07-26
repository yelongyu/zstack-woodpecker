'''

New Integration test for testing vm when doing host maintenance.

Test steps:

1. Create 1 VM.
2. change target_host state to maintain. the vm will be stopped.
3. Enable maintained host again.
4. Start the VM
5. The VM can be start.

This case should not be parallely executed with other test case, since it will
impact other vm state in test db.

@author: Youyk
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.header.vm as vm_header
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import zstackwoodpecker.zstack_test.zstack_test_kvm_host as test_kvm_host
import zstackwoodpecker.header.host as host_header
import apibinding.inventory as inventory
import zstacklib.utils.linux as linux
import time
import os
import random

_config_ = {
        'timeout' : 1000,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
host = None

def is_host_connected(host_uuid):
    cond = res_ops.gen_query_conditions('uuid', '=', host_uuid)
    host = res_ops.query_resource(res_ops.HOST, cond)[0]
    if host.status == 'Connected':
        return True

def test():
    global host
    if test_lib.lib_get_active_host_number() < 2:
        test_util.test_fail('Not available host to do maintenance, since there are not 2 hosts')

    vm_cpu = 1
    vm_memory = 1073741824 #1G
    cond = res_ops.gen_query_conditions('name', '=', 'ttylinux')
    image_uuid = res_ops.query_resource(res_ops.IMAGE, cond)[0].uuid
    l3_network_uuid = res_ops.query_resource(res_ops.L3_NETWORK)[0].uuid
    vm = test_stub.create_mini_vm([l3_network_uuid], image_uuid, cpu_num = vm_cpu, memory_size = vm_memory)
    test_obj_dict.add_vm(vm)

    host_uuid = test_lib.lib_get_vm_host(vm.vm).uuid
    host_ops.change_host_state(host_uuid, 'maintain')

    #need to update vm's inventory, since they will be changed by maintenace mode
    vm.update()
#    vm.set_state(vm_header.STOPPED)

    vm.check()

    host_ops.change_host_state(host_uuid, 'enable')
    if not linux.wait_callback_success(is_host_connected, host_uuid, 120):
        test_util.test_fail('host status is not changed to connected, after changing its state to Enable')

    vm.start()
    vm.check()
    vm.destroy()
    test_obj_dict.rm_vm(vm)
    test_util.test_pass('Maintain Host Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
    if host:
        host.change_state(test_kvm_host.ENABLE_EVENT)
