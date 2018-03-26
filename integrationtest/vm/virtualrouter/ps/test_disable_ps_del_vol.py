'''
New Integration Test for delete volume under PS disable mode.

@author: SyZhao
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.primarystorage_operations as ps_ops
import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.header.vm as vm_header
import os

_config_ = {
        'timeout' : 1000,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
ps_uuid = None
host_uuid = None
vr_uuid = None

def test():
    global test_obj_dict
    global ps_uuid
    global host_uuid
    global vr_uuid
    test_util.test_dsc('Create test vm and check')

    test_lib.lib_set_delete_policy('vm', 'Delay')
    test_lib.lib_set_delete_policy('volume', 'Delay')

    l3_1_name = os.environ.get('l3VlanNetworkName1')
    vm = test_stub.create_vlan_vm(l3_name=l3_1_name)
    l3_1 = test_lib.lib_get_l3_by_name(l3_1_name)
    vr = test_lib.lib_find_vr_by_l3_uuid(l3_1.uuid)[0]
    vr_uuid = vr.uuid
    
    host = test_lib.lib_get_vm_host(vm.get_vm())
    host_uuid = host.uuid
    test_obj_dict.add_vm(vm)
    vm.check()

    disk_offering = test_lib.lib_get_disk_offering_by_name(os.environ.get('rootDiskOfferingName'))
    volume_creation_option = test_util.VolumeOption()
    volume_creation_option.set_disk_offering_uuid(disk_offering.uuid)
    #volume_creation_option.set_system_tags(['ephemeral::shareable', 'capability::virtio-scsi'])
    volume = test_stub.create_volume(volume_creation_option)
    test_obj_dict.add_volume(volume)
    volume.check()

    #volume.attach(vm1)

    #ps = test_lib.lib_get_primary_storage_by_vm(vm.get_vm())
    #ps_uuid = ps.uuid
    #ps_ops.change_primary_storage_state(ps_uuid, 'disable')
    test_stub.disable_all_pss()
    if not test_lib.lib_wait_target_up(vm.get_vm().vmNics[0].ip, '22', 90):
        test_util.test_fail('VM is expected to running when PS change to disable state')

    vm.set_state(vm_header.RUNNING)
    vm.check()
    volume.delete()
    #volume.expunge()
    volume.check()

    #ps_ops.change_primary_storage_state(ps_uuid, 'enable')
    test_stub.enable_all_pss()
    host_ops.reconnect_host(host_uuid)
    vm_ops.reconnect_vr(vr_uuid)
    vm.destroy()

    test_lib.lib_set_delete_policy('vm', 'Direct')
    test_lib.lib_set_delete_policy('volume', 'Direct')

    test_util.test_pass('Delete volume under PS disable mode Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global ps_uuid

    test_lib.lib_set_delete_policy('vm', 'Direct')
    test_lib.lib_set_delete_policy('volume', 'Direct')

    if ps_uuid != None:
        ps_ops.change_primary_storage_state(ps_uuid, 'enable')
    global host_uuid
    if host_uuid != None:
        host_ops.reconnect_host(host_uuid)
    global vr_uuid
    if vr_uuid != None:
        vm_ops.reconnect_vr(vr_uuid)
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
