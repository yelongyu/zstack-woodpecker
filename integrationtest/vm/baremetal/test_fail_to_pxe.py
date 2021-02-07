import zstackwoodpecker.operations.baremetal_operations as bare_operations
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import test_stub
import os

vm = None


def test():
    global vm
    pxe_uuid = test_lib.lib_get_pxe_by_name(os.environ.get('pxename')).uuid
    # Create VM
    vm = test_stub.create_vm()
    vm.check()
    # Create Virtual BMC
    test_stub.create_vbmc(vm=vm, port=6230)
    # Create Chassis
    chassis = os.environ.get('ipminame')
    test_stub.create_chassis(chassis_name=chassis)
    test_stub.hack_ks(port=6230)
    chassis_uuid = test_lib.lib_get_chassis_by_name(chassis).uuid
    # First time Provision
    bare_operations.provision_baremetal(chassis_uuid)
    bare_operations.stop_pxe(pxe_uuid)
    if not test_stub.verify_chassis_status(chassis_uuid, "PxeBootFailed"):
        test_util.test_fail(
            'Chassis failed to get PxeBootFailed after the first provision')
    bare_operations.start_pxe(pxe_uuid)
    if test_lib.lib_get_pxe_by_name(os.environ.get('pxename')).status != "Running":
                    test_util.test_fail('Fail to start PXE')
    test_stub.delete_vbmc(vm=vm)
    bare_operations.delete_chassis(chassis_uuid)
    vm.destroy()
    test_util.test_pass('Create chassis Test Success')


def error_cleanup():
    global vm
    if vm:
        test_stub.delete_vbmc(vm=vm)
        chassis = os.environ.get('ipminame')
        chassis_uuid = test_lib.lib_get_chassis_by_name(chassis).uuid
        bare_operations.delete_chassis(chassis_uuid)
        vm.destroy()
