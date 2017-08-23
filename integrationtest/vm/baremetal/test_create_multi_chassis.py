import zstackwoodpecker.operations.baremetal_operations as bare_operations
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import test_stub
import os

vm1 = None
vm2 = None

def test():
    global vm1
    global vm2
    # Create VM
    vm1 = test_stub.create_vm()
    vm1.check()
    vm2 = test_stub.create_vm()
    vm2.check()
    # Create Virtual BMC
    test_stub.create_vbmc(vm = vm1, port = int(os.environ.get('ipmiport')))
    test_stub.create_vbmc(vm = vm2, port = int(os.environ.get('ipmiport2')))
    # Create Chassis
    chassis = os.environ.get('ipminame')
    test_stub.create_chassis(chassis_name = chassis)
    test_stub.hack_ks(port = os.environ.get('ipmiport'))
    chassis_uuid1 = test_lib.lib_get_chassis_by_name(chassis).uuid
    # Provision VM1
    bare_operations.provision_baremetal(chassis_uuid1)
    hwinfo1 = test_stub.check_hwinfo(chassis_uuid1)

    chassis_option = test_util.ChassisOption()
    chassis_option.set_name(os.environ.get('ipminame2'))
    chassis_option.set_ipmi_address(os.environ.get('ipmiaddress'))
    chassis_option.set_ipmi_username(os.environ.get('ipmiusername'))
    chassis_option.set_ipmi_password(os.environ.get('ipmipassword'))
    chassis_option.set_ipmi_port(os.environ.get('ipmiport2'))

    test_stub.create_chassis(chassis_name=chassis, chassis_option=chassis_option)
    test_stub.hack_ks(port = os.environ.get('ipmiport2'))
    chassis_uuid2 = test_lib.lib_get_chassis_by_name(os.environ.get('ipminame2')).uuid
    
    bare_operations.provision_baremetal(chassis_uuid2)
    hwinfo2 = test_stub.check_hwinfo(chassis_uuid2)
    if not hwinfo1 or not hwinfo2:
        test_util.test_fail('Fail to get hardware info during the first provision')
    test_stub.delete_vbmc(vm = vm1)
    test_stub.delete_vbmc(vm = vm2)
    #bare_operations.delete_chassis(chassis_uuid1)
    #bare_operations.delete_chassis(chassis_uuid2)
    vm1.destroy()
    vm2.destroy()
    test_util.test_pass('Create chassis Test Success')

def error_cleanup():
    global vm1
    global vm2
    if vm1 or vm2:
        test_stub.delete_vbmc(vm = vm1)
        test_stub.delete_vbmc(vm = vm2)
        chassis1 = os.environ.get('ipminame')
        chassis2 = os.environ.get('ipminame2')
        chassis_uuid1 = test_lib.lib_get_chassis_by_name(chassis1).uuid
        chassis_uuid2 = test_lib.lib_get_chassis_by_name(chassis2).uuid
        bare_operations.delete_chassis(chassis_uuid1)
        bare_operations.delete_chassis(chassis_uuid2)
        vm1.destroy()

