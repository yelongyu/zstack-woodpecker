'''

@author: Youyk
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstacklib.utils.linux as linux

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def check_dhcp_remove(vm):
    return False == test_lib.lib_check_vm_dhcp(vm)

def check_dhcp_release(vm):
    return False == test_lib.lib_check_dhcp_leases(vm)

def test():
    '''
    Test Description:
        Will check if test VM's mac/ip assignment will be removed in VR's DNS config, after VM is shutdown. And if VM's mac/ip will be added back after it restart. 
    Resource required:
        Need support 2 VMs. 
    '''
    global test_obj_dict
    test_util.test_dsc('Create test vm and check. VR only has DNS and DHCP services')
    vm = test_stub.create_vlan_vm()
    test_obj_dict.add_vm(vm)

    vm.check()
    vm.stop()
    if linux.wait_callback_success(check_dhcp_remove, vm.vm, 5, 0.2):
        test_util.test_logger('[vm:] %s mac/ip was removed in VR /etc/hosts.dhcp' % vm.vm.uuid)
    else:
        test_util.test_logger('check dhcp remove failure, will try to print VR DHCP tables')
        test_lib.lib_print_vr_dhcp_tables(test_lib.lib_find_vr_by_vm(vm.vm)[0])
        test_util.test_fail('[vm:] %s mac was not removed in VR /etc/hosts.dhcp, after vm was stopped.' % vm.vm.uuid)
    if linux.wait_callback_success(check_dhcp_release, vm.vm, 5, 0.2):
        test_util.test_logger('[vm:] %s mac/ip was removed in VR /etc/hosts.leases' % vm.vm.uuid)
    else:
        test_util.test_logger('check dhcp lease failure, will try to print VR DHCP tables')
        test_lib.lib_print_vr_dhcp_tables(test_lib.lib_find_vr_by_vm(vm.vm)[0])
        test_util.test_fail('[vm:] %s mac was not removed in VR /etc/hosts.leases, after vm was stopped.' % vm.vm.uuid)

    vm.start()
    vm.check()
    vm.destroy()
    vm.check()
    test_util.test_pass('Successfully check VM DHCP release when VM stopped')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
