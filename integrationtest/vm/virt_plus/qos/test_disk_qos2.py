'''
This case can not execute parallelly
@author: Youyk
'''
import os
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.tag_operations as tag_ops

_config_ = {
        'timeout' : 600,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
new_offering_uuid = None

def test():
    global new_offering_uuid
    test_util.test_dsc('Test VM disk bandwidth QoS by 20MB')

    #unit is KB
    volume_bandwidth = 25*1024*1024
#    new_offering = test_lib.lib_create_instance_offering(volume_bandwidth = volume_bandwidth)
#    new_offering_uuid = new_offering.uuid

    vm = test_stub.create_vm(vm_name = 'vm_volume_qos')
    test_obj_dict.add_vm(vm)

    vm.check()

    volume_creation_option = test_util.VolumeOption()
    disk_offering = test_lib.lib_create_disk_offering(diskSize=1073741824,name="1G")
    volume_creation_option.set_disk_offering_uuid(disk_offering.uuid)
    tag_ops.create_system_tag('DiskOfferingVO', disk_offering.uuid, "volumeTotalBandwidth::26214400")
    
    volume_creation_option.set_name('volume-1')
    volume = test_stub.create_volume(volume_creation_option)
    test_obj_dict.add_volume(volume)
    vm_inv = vm.get_vm()
    test_lib.lib_mkfs_for_volume(volume.get_volume().uuid, vm_inv)
    mount_point = '/tmp/zstack/test'
    test_stub.attach_mount_volume(volume, vm, mount_point)

    test_stub.make_ssh_no_password(vm_inv)
    test_stub.install_fio(vm_inv)
    test_stub.test_fio_bandwidth(vm_inv, volume_bandwidth, mount_point)
    test_lib.lib_robot_cleanup(test_obj_dict)

    test_util.test_pass('VM Disk QoS Test Pass')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
    if new_offering_uuid:
        vm_ops.delete_instance_offering(new_offering_uuid)
