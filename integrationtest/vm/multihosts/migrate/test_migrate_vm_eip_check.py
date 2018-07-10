'''

Test EIP connectability during VM migration. 

Test step:
    1. Create a VM
    2. Create an EIP with VM's nic
    3. Migrate the VM
    4. Check the EIP connectability
    5. Destroy VM

@author: Legion
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import os,sys,time

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    test_util.test_dsc('Create test vm migration with EIP and check.')
    vm = test_stub.create_vr_vm('migrate_vm', 'imageName_s', 'l3VlanNetwork2')
    test_obj_dict.add_vm(vm)
    
    pri_l3_name = os.environ.get('l3VlanNetwork2')
    pri_l3_uuid = test_lib.lib_get_l3_by_name(pri_l3_name).uuid

    pub_l3_name = os.environ.get('l3PublicNetworkName')
    pub_l3_uuid = test_lib.lib_get_l3_by_name(pub_l3_name).uuid

    vm_nic = vm.vm.vmNics[0]
    vm_nic_uuid = vm_nic.uuid
    vip = test_stub.create_vip('create_eip_test', pub_l3_uuid)
    test_obj_dict.add_vip(vip)
    eip = test_stub.create_eip('create eip test', vip_uuid=vip.get_vip().uuid, vnic_uuid=vm_nic_uuid, vm_obj=vm)
    
    vip.attach_eip(eip)
    
    vm.check()

    migration_pid = os.fork()
    if migration_pid == 0:
        test_stub.migrate_vm_to_random_host(vm)
        sys.exit(0)
    for _ in xrange(300):
        if not test_lib.lib_check_directly_ping(vip.get_vip().ip):
            test_util.test_fail('expected to be able to ping vip while it fail')
        time.sleep(1)

    vm.destroy()
    test_obj_dict.rm_vm(vm)

    eip.delete()
    vip.delete()

    test_obj_dict.rm_vip(vip)
    test_util.test_pass('Migrate VM with EIP connectable Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
