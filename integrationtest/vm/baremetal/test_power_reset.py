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
    test_stub.hack_ks(port = 6230)
    chassis_uuid = test_lib.lib_get_chassis_by_name(chassis).uuid

    status = bare_operations.power_off_baremetal(chassis_uuid)
    if status.status == "Chassis Power is off":
        status = bare_operations.power_reset_baremetal(chassis_uuid)
        if status.status != "Chassis Power is on":
            test_util.test_fail('Failed to power reset chassis')
    else:
        test_util.test_fail('Failed to power off chassis')

    test_stub.delete_vbmc(vm = vm)
    bare_operations.delete_chassis(chassis_uuid)
    vm.destroy()
    test_util.test_pass('Test Power Reset Success')

def error_cleanup():
    global vm
    if vm:
        test_stub.delete_vbmc(vm = vm)
        chassis = os.environ.get('ipminame')
        chassis_uuid = test_lib.lib_get_chassis_by_name(chassis).uuid
        bare_operations.delete_chassis(chassis_uuid)
        vm.destroy()
