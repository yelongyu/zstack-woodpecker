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
    # First time Provision
    bare_operations.provision_baremetal(chassis_uuid)
    hwinfo = test_stub.check_hwinfo(chassis_uuid)
    if not hwinfo:
        test_util.test_fail('Fail to get hardware info during the first provision')
    #Generate cfgItems
    cfgItems, pxe_mac = test_stub.generate_cfgItems(chassis_uuid)
    host_cfg =  test_stub.create_hostcfg(chassis_uuid=chassis_uuid, unattended=True, password="password", cfgItems=cfgItems)
    
    test_stub.hack_ks(port = 6230, ks_file = str(pxe_mac.replace(':','-')))
    # Second time Provision to install system
    bare_operations.provision_baremetal(chassis_uuid)
    if not test_stub.verify_chassis_status(chassis_uuid, "Rebooting"):
        test_util.test_fail('Chassis failed to Rebooting after the second provision')
    if not test_stub.verify_chassis_status(chassis_uuid, "Provisioning"):
        test_util.test_fail('Chassis failed to Provisioning after the second provision')
    if not test_stub.verify_chassis_status(chassis_uuid, "Provisioned"):
        test_util.test_fail('Chassis failed to Provisioned after the second provision')
    test_util.test_pass('Create PXE Test Success')

def error_cleanup():
    global vm
    if vm:
        test_stub.delete_vbmc(vm = vm)
        vm.destroy()
