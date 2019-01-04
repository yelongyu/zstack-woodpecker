'''

New Integration Test for create vm with iscsi 6 volumes and detach 6 volumes and reboot vm and attach one volumes .

@author: ye.tian 2018-12-12
'''

import zstackwoodpecker.test_util as test_util
import os
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.operations.tag_operations as tag_ops


_config_ = {
        'timeout' : 2000,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
all_volume_offering_uuid = None
rw_volume_offering_uuid = None
instance_offering_uuid = None

vm = None

def test():
    global vm, all_volume_offering_uuid, rw_volume_offering_uuid, all_volume_uuid, rw_volume_uuid, volume_offering_3, volume_offering_4, volume_offering_5, volume_offering_6 
    global instance_offering_uuid, volume_uuid_3, volume_uuid_4, volume_uuid_5, volume_uuid_6
    
    #create disk offering
    test_util.test_dsc('create disk offering')
    name_all = 'all_disk_offering'	
    volume_bandwidth = 30*1024*1024
    all_volume_offering = test_lib.lib_create_disk_offering(name = name_all, volume_bandwidth = volume_bandwidth)
    all_volume_offering_uuid = all_volume_offering.uuid

    name_rw = 'rw_disk_offering'	
    volume_read_bandwidth = 90*1024*1024
    volume_write_bandwidth = 100*1024*1024
    rw_volume_offering = test_lib.lib_create_disk_offering(name = name_rw, read_bandwidth = volume_read_bandwidth, write_bandwidth = volume_write_bandwidth)
    rw_volume_offering_uuid = rw_volume_offering.uuid
    
    volume_offering_3 = test_lib.lib_create_disk_offering(name = "volume_offering_3")
    volume_offering_4 = test_lib.lib_create_disk_offering(name = "volume_offering_4")
    volume_offering_5 = test_lib.lib_create_disk_offering(name = "volume_offering_5")
    volume_offering_6 = test_lib.lib_create_disk_offering(name = "volume_offering_6")

    #create instance offering 
    test_util.test_dsc('create instance offering')
    read_bandwidth = 50*1024*1024
    write_bandwidth = 60*1024*1024
    net_outbound_bandwidth = 70*1024*1024
    net_inbound_bandwidth = 80*1024*1024
    new_instance_offering = test_lib.lib_create_instance_offering(read_bandwidth = read_bandwidth, write_bandwidth=write_bandwidth, net_outbound_bandwidth = net_outbound_bandwidth, net_inbound_bandwidth = net_inbound_bandwidth)
    instance_offering_uuid = new_instance_offering.uuid

    #create vm with 2 data volumes
    test_util.test_dsc('create vm with volumes qos by normal account a')
    l3net_uuid = res_ops.get_resource(res_ops.L3_NETWORK)[0].uuid
    cond = res_ops.gen_query_conditions('name', '=', 'ttylinux')
    image_uuid = res_ops.query_resource(res_ops.IMAGE, cond)[0].uuid
    vm_creation_option = test_util.VmOption()
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_l3_uuids([l3net_uuid])

    vm = test_stub.create_vm_with_volume(vm_creation_option = vm_creation_option, data_volume_uuids = [all_volume_offering_uuid, rw_volume_offering_uuid, volume_offering_3.uuid, volume_offering_4.uuid, volume_offering_5.uuid, volume_offering_6.uuid])
    vm_inv = vm.get_vm()


    # get the volume uuid
    test_util.test_dsc('get the vm data volumes')
    cond1 = res_ops.gen_query_conditions("diskOfferingUuid", '=', all_volume_offering_uuid)
    cond2 = res_ops.gen_query_conditions("diskOfferingUuid", '=', rw_volume_offering_uuid)
    cond3 = res_ops.gen_query_conditions("diskOfferingUuid", '=', volume_offering_3.uuid)
    cond4 = res_ops.gen_query_conditions("diskOfferingUuid", '=', volume_offering_4.uuid)
    cond5 = res_ops.gen_query_conditions("diskOfferingUuid", '=', volume_offering_5.uuid)
    cond6 = res_ops.gen_query_conditions("diskOfferingUuid", '=', volume_offering_6.uuid)
    all_volume_uuid = res_ops.query_resource(res_ops.VOLUME, cond1)[0].uuid
    rw_volume_uuid = res_ops.query_resource(res_ops.VOLUME, cond2)[0].uuid
    volume_uuid_3 = res_ops.query_resource(res_ops.VOLUME, cond3)[0].uuid
    volume_uuid_4 = res_ops.query_resource(res_ops.VOLUME, cond4)[0].uuid
    volume_uuid_5 = res_ops.query_resource(res_ops.VOLUME, cond5)[0].uuid
    volume_uuid_6 = res_ops.query_resource(res_ops.VOLUME, cond6)[0].uuid

    tag_ops.create_system_tag('VolumeVO', all_volume_uuid, "capability::virtio-scsi")
    tag_ops.create_system_tag('VolumeVO', rw_volume_uuid, "capability::virtio-scsi")
    tag_ops.create_system_tag('VolumeVO', volume_uuid_3, "capability::virtio-scsi")
    tag_ops.create_system_tag('VolumeVO', volume_uuid_4, "capability::virtio-scsi")
    tag_ops.create_system_tag('VolumeVO', volume_uuid_5, "capability::virtio-scsi")
    tag_ops.create_system_tag('VolumeVO', volume_uuid_6, "capability::virtio-scsi")

    vm.check()
    vm.reboot()

    vol_ops.detach_volume(all_volume_uuid, vm_inv.uuid)
    vol_ops.detach_volume(rw_volume_uuid, vm_inv.uuid)
    vol_ops.detach_volume(volume_uuid_3, vm_inv.uuid)
    vol_ops.detach_volume(volume_uuid_4, vm_inv.uuid)
    vol_ops.detach_volume(volume_uuid_5, vm_inv.uuid)
    vol_ops.detach_volume(volume_uuid_6, vm_inv.uuid)
     
    vm.check()
    
    vol_ops.attach_volume(all_volume_uuid, vm_inv.uuid)
    vol_ops.attach_volume(rw_volume_uuid, vm_inv.uuid)
    vol_ops.attach_volume(volume_uuid_3, vm_inv.uuid)
    vol_ops.attach_volume(volume_uuid_4, vm_inv.uuid)
    vol_ops.attach_volume(volume_uuid_5, vm_inv.uuid)
    vol_ops.attach_volume(volume_uuid_6, vm_inv.uuid)

    vm.reboot()
    vm.check()
    
    vol_ops.detach_volume(all_volume_uuid, vm_inv.uuid)
    vm.check()

    vol_ops.attach_volume(all_volume_uuid, vm_inv.uuid)

    vm.destroy()
    vm.check()

    vol_ops.delete_disk_offering(all_volume_offering_uuid)
    vol_ops.delete_disk_offering(rw_volume_offering_uuid)
    vol_ops.delete_disk_offering(volume_offering_3.uuid)
    vol_ops.delete_disk_offering(volume_offering_4.uuid)
    vol_ops.delete_disk_offering(volume_offering_5.uuid)
    vol_ops.delete_disk_offering(volume_offering_6.uuid)
    vol_ops.delete_volume(all_volume_uuid)
    vol_ops.delete_volume(rw_volume_uuid)
    vol_ops.delete_volume(volume_uuid_3)
    vol_ops.delete_volume(volume_uuid_4)
    vol_ops.delete_volume(volume_uuid_5)
    vol_ops.delete_volume(volume_uuid_6)
    vm_ops.delete_instance_offering(instance_offering_uuid)
    test_util.test_pass('Create VM with volumes and detach/attach and after reboot and detach/attach Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm, all_volume_offering_uuid, rw_volume_offering_uuid, all_volume_uuid, rw_volume_uuid, volume_offering_3, volume_offering_4, volume_offering_5, volume_offering_6 
    global instance_offering_uuid, volume_uuid_3, volume_uuid_4, volume_uuid_5, volume_uuid_6
    if vm:
        vm.destroy()
    vol_ops.delete_disk_offering(all_volume_offering_uuid)
    vol_ops.delete_disk_offering(rw_volume_offering_uuid)
    vol_ops.delete_disk_offering(volume_offering_3.uuid)
    vol_ops.delete_disk_offering(volume_offering_4.uuid)
    vol_ops.delete_disk_offering(volume_offering_5.uuid)
    vol_ops.delete_disk_offering(volume_offering_6.uuid)
    vol_ops.delete_volume(all_volume_uuid)
    vol_ops.delete_volume(rw_volume_uuid)
    vol_ops.delete_volume(volume_uuid_3)
    vol_ops.delete_volume(volume_uuid_4)
    vol_ops.delete_volume(volume_uuid_5)
    vol_ops.delete_volume(volume_uuid_6)
    vm_ops.delete_instance_offering(instance_offering_uuid)
