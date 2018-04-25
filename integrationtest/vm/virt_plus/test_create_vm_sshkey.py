'''

New Integration Test for KVM VM sshkey injection.

@author: quarkonics
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import zstackwoodpecker.header.vm as vm_header
import time
import os
import tempfile
import uuid

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
tmp_file = '/tmp/%s' % uuid.uuid1().get_hex()

def test():
    instance_offering_name = os.environ.get('instanceOfferingName_m')
    instance_offering_uuid = test_lib.lib_get_instance_offering_by_name(instance_offering_name).uuid

    vm = test_stub.create_vm(image_name = os.environ.get('sshkeyImageName'), system_tags = ["%s::%s" % (vm_header.SSHKEY, os.environ.get('sshkeyPubKey'))], instance_offering_uuid = instance_offering_uuid)
    test_obj_dict.add_vm(vm)
    vm_ip = vm.get_vm().vmNics[0].ip
    test_lib.lib_wait_target_up(vm_ip, '22', 240)
    time.sleep(10)
   
    for i in range(5):
        ssh_cmd = 'timeout 5 ssh -i %s -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s echo pass' % (os.environ.get('sshkeyPriKey_file'), vm_ip)
        process_result = test_stub.execute_shell_in_process(ssh_cmd, tmp_file)
        if process_result == 0:
            break
        else:
            time.sleep(10)
    else:
        test_util.test_fail("fail to use ssh key connect to VM")

    vm.destroy()
    test_util.test_pass('Create VM Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
    os.system('rm -f %s' % tmp_file)
