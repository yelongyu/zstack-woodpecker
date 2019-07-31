'''

Integration test for testing max allowed vscsi data volume to be attached on mini.

@author: zhaohao.chen
'''

import apibinding.inventory as inventory
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_volume as test_volume_header
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import zstackwoodpecker.operations.volume_operations as vol_ops
import time
import os
import random

PROVISION = ["volumeProvisioningStrategy::ThinProvisioning","volumeProvisioningStrategy::ThickProvisioning"]
VIRTIOSCSI = "capability::virtio-scsi"
round_num = 30
volume = None
vm = None

def test():
    global round_num
    global volume
    global vm
    VM_CPU = 2
    VM_MEM = 2147483648
    volume_creation_option = test_util.VolumeOption()
    ps_uuid = res_ops.query_resource(res_ops.PRIMARY_STORAGE)[0].uuid
    volume_creation_option.set_primary_storage_uuid(ps_uuid)
    
    #1.create vm
    vm_creation_option = test_util.VmOption()
    image_name = os.environ.get('imageName_s')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    l3_name = os.environ.get('l3VlanNetworkName1')
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    vm_creation_option.set_l3_uuids([l3_net_uuid])
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_name('Mini_vm_datavolume_test')
    vm_creation_option.set_cpu_num(VM_CPU)
    vm_creation_option.set_memory_size(VM_MEM)
    vm = test_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    vm.check()
    vm_uuid = vm.get_vm().uuid
    #create thin/thick data volume with random disksize and random provision type
    #and attach to vm
    for i in range(round_num):
        volume_name = "volume_%s" % i
        volume_creation_option.set_name(volume_name)
        max_size = (res_ops.query_resource(res_ops.PRIMARY_STORAGE)[0].availableCapacity - 1048576)/(20 * 512)
        disk_size = random.randint(2048, max_size) * 512
        volume_creation_option.set_diskSize(disk_size)
        volume_creation_option.set_system_tags([random.choice(PROVISION), VIRTIOSCSI])
        volume = test_volume_header.ZstackTestVolume()
        volume.set_volume(vol_ops.create_volume_from_diskSize(volume_creation_option))
        volume.check() 
        try:
            volume.attach(vm)
        except Exception as e:
            test_util.test_logger(e)
            test_util.test_pass('Allowed max num of attached vscsi is %s' % i)
    test_util.test_fail("Allowed max num of attached vscsi may is not %s" % round_num )

def error_cleanup():
    global volume
    global vm
    if volume:
        try:
            volume.delete()
            volume.expunge()
        except:
            pass
    if vm:
        try:
            vm.destroy()
            vm.expunge()
        except:
            pass

