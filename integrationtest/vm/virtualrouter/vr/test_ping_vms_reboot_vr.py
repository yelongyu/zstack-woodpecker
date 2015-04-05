'''
1. Create 2 Test VMs with VR. 
2. After 2 VMs created, reboot VR. 
3. After VR reboot completed, check 2 VMs status
4. ping VM2 from VM1


@author: Youyk
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.vm_operations as vm_ops
import threading
import time

_config_ = {
        'timeout' : 1000,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    test_util.test_dsc('Create test vm1 and check')
    vm1 = test_stub.create_vlan_vm()
    test_obj_dict.add_vm(vm1)
    test_util.test_dsc('Create test vm2 and check')
    vm2 = test_stub.create_vlan_vm()
    test_obj_dict.add_vm(vm2)

    vm1.check()
    vm2.check()

    vrs = test_lib.lib_find_vr_by_vm(vm1.vm)
    if len(vrs) != 1:
        test_util.test_logger('more than 1 VR are found for vm1: %s. Will test the 1st one: %s.' % (vm1.vm.uuid, vr.uuid))

    vr = vrs[0]
    vr_mgmt_ip = test_lib.lib_find_vr_mgmt_ip(vr)
    if not test_lib.lib_check_testagent_status(vr_mgmt_ip):
        test_util.test_fail('vr: %s is not reachable, since can not reach its test agent. Give up test and test failure. ' % vr.uuid)
    test_lib.lib_install_testagent_to_vr_with_vr_vm(vr)
    #Need to put the vr restart into thread. Since vr reboot API is a sync API. 
    thread = threading.Thread(target=vm_ops.reboot_vm, args=(vr.uuid,))
    thread.start()
    #check vr vr service port
    if not test_lib.lib_wait_target_down(vr_mgmt_ip, '7272', 60):
        test_util.test_fail('vr: %s is not shutdown in 60 seconds. Fail to reboot it. ' % vr.uuid)

    if not test_lib.lib_wait_target_up(vr_mgmt_ip, '7272', 120):
        test_util.test_fail('vr: %s is not startup in 120 seconds. Fail to reboot it. ' % vr.uuid)

    #avoid of possible apt conflicting between install testagent and appliancevm
    #time.sleep(60)
    vm1.check()
    vm2.check()

    test_util.test_dsc('Ping from vm1 to vm2.')
    test_lib.lib_check_ping(vm1.vm, vm2.vm.vmNics[0].ip)
    vm1.destroy()
    vm2.destroy()
    test_util.test_pass('Create vlan VirtualRouter VM (and reboot VR after VM created) Test with snat ping between two VMs Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)

