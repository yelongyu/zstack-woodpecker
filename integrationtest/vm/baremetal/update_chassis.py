import zstackwoodpecker.operations.baremetal_operations as bare_operations
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import test_stub
import os

vm = None

def test():
    global vm
    # Create VM
    vm = test_stub.create_vm()
    vm.check()
    # Create Virtual BMC
    test_stub.create_vbmc(vm = vm, port = 6230)
    # Create Chassis
    chassis = os.environ.get('ipminame')
    test_stub.create_chassis(chassis_name = chassis)
    # Update Chassis
    chassis_uuid = test_lib.lib_get_chassis_by_name(chassis).uuid
    ipmiaddress = os.environ.get('ipmiaddress')
    ipmiuser = os.environ.get('ipmiusername')
    ipmipasswd = os.environ.get('ipmipassword')
    test_stub.delete_vbmc(vm = vm)
    test_stub.create_vbmc(vm = vm, port = 6231)
    bare_operations.update_chassis(chassis_uuid=chassis_uuid, address=ipmiaddress, username=ipmiuser, password=ipmipasswd, port=6231)
    test_stub.hack_ks(port = 6231)
    # First time Provision
    bare_operations.provision_baremetal(chassis_uuid)
    hwinfo = test_stub.check_hwinfo(chassis_uuid)
    if not hwinfo:
        test_util.test_fail('Fail to get hardware info during the first provision')
    new_port = test_lib.lib_get_chassis_by_name(chassis).ipmiPort
    if new_port != "6231":
        test_util.test_fail("Update Chassis's Port failed: port=%s" % new_port)
    test_stub.delete_vbmc(vm = vm)
    bare_operations.delete_chassis(chassis_uuid)
    vm.destroy()
    test_util.test_pass('Update Chassis Test Success')

def error_cleanup():
    global vm
    if vm:
        test_stub.delete_vbmc(vm = vm)
        chassis = os.environ.get('ipminame')
        chassis_uuid = test_lib.lib_get_chassis_by_name(chassis).uuid
        bare_operations.delete_chassis(chassis_uuid)
        vm.destroy()
