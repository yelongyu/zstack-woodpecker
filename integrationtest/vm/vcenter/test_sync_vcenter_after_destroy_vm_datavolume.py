'''
Sync vcenter test after destroying vm and its attached data volume both.
@author:guocan
'''


import apibinding.inventory as inventory
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.vcenter_operations as vct_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import test_stub

import os
import time

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    global test_obj_dict

    ova_image_name = os.environ['vcenterDefaultmplate']
    network_pattern1 = os.environ['l3vCenterNoVlanNetworkName']
    disk_offering1 = test_lib.lib_get_disk_offering_by_name(os.environ.get('largeDiskOfferingName'))

    test_util.test_dsc('Create vm and attach volume')
    vm = test_stub.create_vm_in_vcenter(vm_name = 'test_for_sync_vcenter_vm', image_name = ova_image_name, l3_name = network_pattern1)
    test_obj_dict.add_vm(vm)
    vm.check()
    volume_creation_option = test_util.VolumeOption()
    volume_creation_option.set_disk_offering_uuid(disk_offering1.uuid)
    volume_creation_option.set_name('vcenter3_volume')
    volume = test_stub.create_volume(volume_creation_option)
    test_obj_dict.add_volume(volume)
    volume.check()
    volume.attach(vm)
    test_util.test_logger(volume.target_vm.state)
    volume.check()

    test_util.test_dsc('Destroy vm and its attached data volume both')
    vm.destroy()
    volume.delete()
    vm.check()
    volume.check()

    test_util.test_dsc('Check in vcenter after destroying vm and its attached data volume both in zstack')
    #connect vcenter
    import ssl
    from pyVmomi import vim
    import atexit
    from pyVim import connect
    import zstackwoodpecker.zstack_test.vcenter_checker.zstack_vcenter_vm_checker as vm_checker
    vcenter_password = os.environ['vcenterpwd']
    vcenter_server = os.environ['vcenter']
    vcenter_username = os.environ['vcenteruser']
    sslContext = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    sslContext.verify_mode = ssl.CERT_NONE
    SI = connect.SmartConnect(host=vcenter_server, user=vcenter_username, pwd=vcenter_password, port=443, sslContext=sslContext)
    if not SI:
        test_util.test_fail("Unable to connect to the vCenter")
    content = SI.RetrieveContent()
    vc_vm = vm_checker.get_obj(content, [vim.VirtualMachine], name='test_for_sync_vcenter_vm')
    test_util.test_logger(vc_vm.summary.runtime.powerState)
    if not (vc_vm.summary.runtime.powerState == 'poweredOff'):
        test_util.test_fail("Vm should stop in vcenter")
    atexit.register(connect.Disconnect, SI)

    test_util.test_dsc('Sync vcenter')
    vc_name = os.environ['vcenter']
    vcenter_uuid = vct_ops.lib_get_vcenter_by_name(vc_name).uuid
    test_util.test_logger(vcenter_uuid)
    vct_ops.sync_vcenter(vcenter_uuid)

    #After synchronization, wait for the database update
    time.sleep(5)

    test_util.test_dsc('check vm and volumes after synchronizing vcenter')
    db_volume = test_lib.lib_get_volume_by_uuid(volume.get_volume().uuid)
    test_util.test_logger(db_volume.status)
    if db_volume.status != 'Deleted':
        test_util.test_fail("check data volume fail")
    db_vm = test_lib.lib_get_vm_by_uuid(vm.vm.uuid)
    if db_vm.state == 'Destroyed':
        test_util.test_logger('check vm success')
    else:
        test_util.test_fail("check vm fail")
   
    vm.recover()
    vct_ops.sync_vcenter(vcenter_uuid)
    time.sleep(5)
    db_vm = test_lib.lib_get_vm_by_uuid(vm.vm.uuid)
    if db_vm.state == 'Stopped' and len(db_vm.allVolumes) == 1 and db_vm.allVolumes[0].type == 'Root' and db_vm.allVolumes[0].status == 'Ready':
        test_util.test_logger('check vm success')
    else:
        test_util.test_fail("check vm fail")

    vm.destroy()
    vm.expunge()
    vct_ops.sync_vcenter(vcenter_uuid)
    time.sleep(5)
    if test_lib.lib_get_vm_by_uuid(vm.vm.uuid):
        test_util.test_fail("check vm fail: vm has been expunged")
    #connect vcenter
    import ssl
    from pyVmomi import vim
    import atexit
    from pyVim import connect
    import zstackwoodpecker.zstack_test.vcenter_checker.zstack_vcenter_vm_checker as vm_checker
    vcenter_password = os.environ['vcenterpwd']
    vcenter_server = os.environ['vcenter']
    vcenter_username = os.environ['vcenteruser']
    sslContext = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    sslContext.verify_mode = ssl.CERT_NONE
    SI = connect.SmartConnect(host=vcenter_server, user=vcenter_username, pwd=vcenter_password, port=443, sslContext=sslContext)
    if not SI:
        test_util.test_fail("Unable to connect to the vCenter")
    content = SI.RetrieveContent()
    vc_vm = vm_checker.get_obj(content, [vim.VirtualMachine], name='test_for_sync_vcenter_vm')
    if not isinstance(vc_vm, list):
        test_util.test_fail("check vm fail: vm has been expunged.")

    volume.expunge()

    test_util.test_pass("Sync vcenter test passed after destroying vm and its attached data volume both.")


def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)

