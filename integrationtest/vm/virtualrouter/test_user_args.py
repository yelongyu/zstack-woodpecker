'''
@author: MengLai
'''
import commands 
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.vm_operations as vm_ops

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    global test_obj_dict
    vm = test_stub.create_basic_vm()
#    vm = test_stub.create_vm_with_user_args(TestArgsWhenCreateVM)
    test_obj_dict.add_vm(vm)
    vm.check()
    vm_inv = vm.get_vm()
    vm_uuid = vm_inv.uuid
    vm_ip = vm_inv.vmNics[0].ip

#    cmd = "ps -ef | grep qemu-kvm | grep TestArgsWhenCreateVM | grep -v grep"
    cmd = "ps -ef | grep qemu-kvm | grep 'uuid %s' | grep -v grep" % vm_uuid
#    cmd = "ps -ef | grep qemu-kvm | grep 'uuid  %s' | grep TestArgsWhenCreateVM | grep -v grep" % vm_uuid
    test_util.test_dsc('cmd: %s' % cmd)
    (status, output) = commands.getstatusoutput(cmd)

    test_util.test_dsc('status: %s output: %s' % (status, output))
    if len(output) == 0:
        test_util.test_fail('fail to add user arguments when create vm')

    vm.stop()
    vm.check()
    vm.start()
#    vm_ops.start_vm_with_user_args(vm_uuid, system_tags = 'TestArgsWhenStartVM')
    vm.check()

    cmd = "ps -ef | grep qemu-kvm | grep 'uuid %s' | grep -v grep" % vm_uuid
#    cmd = "ps -ef | grep qemu-kvm | grep 'uuid  %s' | grep TestArgsWhenStartVM | grep -v grep" % vm_uuid
    (status, output) = commands.getstatusoutput(cmd)
    if len(output) == 0:
        test_util.test_fail('fail to add user arguments when start vm')
    
    vm.destroy()
    test_obj_dict.rm_vm(vm)
    test_util.test_pass('User Args Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
