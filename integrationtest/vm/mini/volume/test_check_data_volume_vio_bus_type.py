'''

Integration test for checking data volume VirtIO bus type on mini.

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
VM_CPU= 2
VM_MEM = 2147483648 #2GB 
volume = None
vm = None

def scsi_check(vol_name, vm, scsi=True):
    vm_uuid = vm.get_vm().uuid
    cmd = "virsh dumpxml %s|grep bus|grep scsi" % vm_uuid
    test_util.test_logger('cmd: %s' % cmd)
    cond = res_ops.gen_query_conditions('uuid', '=', vm_uuid) 
    host_uuid = res_ops.query_resource_fields(res_ops.VM_INSTANCE, cond)[0].hostUuid
    cond = res_ops.gen_query_conditions('uuid', '=', host_uuid)
    host_ip = res_ops.query_resource_fields(res_ops.HOST, cond)[0].managementIp
    ret = test_lib.lib_execute_ssh_cmd(host_ip, 'root', 'password', cmd)
    test_util.test_logger('host: %s \nret: %s' % (host_ip, ret))
    if scsi:
        if not ret:
            test_util.test_fail("%s is not scsi" % vol_name)
    else:
        if ret:
            test_util.test_fail("%s is not vblk" % vol_name)

def vol_create(vol_name, volume_creation_option, systemtags):
    volume_creation_option.set_name(vol_name)
    #max_size = (res_ops.query_resource(res_ops.PRIMARY_STORAGE)[0].availableCapacity - 1048576)/2
    max_size = (res_ops.query_resource(res_ops.PRIMARY_STORAGE)[0].availableCapacity - 1048576)/1024
    #disk_size = random.randint(1048576, max_size)
    disk_size = random.randint(2048, max_size) * 512
    volume_creation_option.set_diskSize(disk_size)
    volume_creation_option.set_system_tags(systemtags)
    volume = test_volume_header.ZstackTestVolume()
    volume.set_volume(vol_ops.create_volume_from_diskSize(volume_creation_option))
    return volume

def test():
    global volume
    global vm
    #1.create vm
    vm_creation_option = test_util.VmOption()
    image_name = os.environ.get('imageName_s')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    l3_name = os.environ.get('l3VlanNetworkName1')
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    vm_creation_option.set_l3_uuids([l3_net_uuid])
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_cpu_num(VM_CPU)
    vm_creation_option.set_memory_size(VM_MEM)
    vm_creation_option.set_name('MINI_test')
    vm = test_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    vm.check()     
    #2.create thin/thick volume & check scsi
    volume_creation_option = test_util.VolumeOption()
    ps_uuid = res_ops.query_resource(res_ops.PRIMARY_STORAGE)[0].uuid
    volume_creation_option.set_primary_storage_uuid(ps_uuid)
    #thin & scsi
    volume = vol_create('vol_thin_scsi', volume_creation_option, [PROVISION[0], VIRTIOSCSI])
    volume.check() 
    volume.attach(vm)
    scsi_check('vol_thin_scsi', vm)
    volume.detach(vm.get_vm().uuid)
    #thick & scsi
    volume = vol_create('vol_thick_scsi', volume_creation_option, [PROVISION[1], VIRTIOSCSI]) 
    volume.check() 
    volume.attach(vm)
    scsi_check('vol_thick_scsi', vm)
    volume.detach(vm.get_vm().uuid)
    #thin & vblk
    volume = vol_create('vol_thin_vblk', volume_creation_option, [PROVISION[0]]) 
    volume.check() 
    volume.attach(vm)
    scsi_check('vol_thin_vblk', vm, scsi=False)
    volume.detach(vm.get_vm().uuid)
    #thick & vblk 
    volume = vol_create('vol_thick_vblk', volume_creation_option, [PROVISION[1]]) 
    volume.check() 
    volume.attach(vm)
    scsi_check('vol_thick_vblk', vm, scsi=False)
    volume.detach(vm.get_vm().uuid)

    test_util.test_pass("Mini Data Volume VirtIO Bus Type Check Test Success")

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
            vm.delete()
            vm.expunge()
        except:
            pass
