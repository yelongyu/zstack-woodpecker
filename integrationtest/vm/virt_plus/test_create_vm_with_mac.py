'''

New Integration Test for creating KVM VM.

@author: Legion
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import time
import os
import commands

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
MAC = "10:20:30:ab:cd:ef"

def test():
    cond_l3 = res_ops.gen_query_conditions('name', '=', os.environ.get('l3PublicNetworkName'))
    l3_uuid = res_ops.query_resource(res_ops.L3_NETWORK, cond_l3)[0].uuid
    sys_tag = ["customMac::%s::%s" % (l3_uuid, MAC)]
    vm = test_stub.create_vm(vm_name = 'test-vm-created-with-mac', system_tags = sys_tag)
    test_obj_dict.add_vm(vm)
    vm.check()
    vm_ip = vm.vm.vmNics[0].ip
    cmd = 'sshpass -p password ssh -o StrictHostKeyChecking=no root@%s ip a | grep %s' % (vm_ip, MAC) 
    ret = commands.getoutput(cmd)
    vm.destroy()
    if not ret:
        test_util.test_fail('Create VM with Mac Test Fail')
    else:
        test_util.test_pass('Create VM with Mac Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
