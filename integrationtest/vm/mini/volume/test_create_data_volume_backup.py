'''

Integration test for testing create thick/thick root volume backup on mini.

@author: zhaohao.chen
'''

import apibinding.inventory as inventory
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import zstackwoodpecker.zstack_test.zstack_test_volume as test_volume_header
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import time
import os
import random

test_obj_dict = test_state.TestStateDict()
def test():
    VM_CPU= 8
    VM_MEM = 2147483648 #2GB 

    #1.create VM
    vm_creation_option = test_util.VmOption()
    image_name = os.environ.get('imageName_s')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    l3_name = os.environ.get('l3VlanNetworkName1')
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    vm_creation_option.set_l3_uuids([l3_net_uuid])
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_cpu_num(VM_CPU)
    vm_creation_option.set_memory_size(VM_MEM)
    vm_creation_option.set_name('MINI_Backup_test')
    vm = test_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    vm.check()
    test_obj_dict.add_vm(vm)

    #2.create thin/thick data volume & attach to vm
    volume_creation_option = test_util.VolumeOption()
    ps_uuid = res_ops.query_resource(res_ops.PRIMARY_STORAGE)[0].uuid
    volume_creation_option.set_primary_storage_uuid(ps_uuid)
    disk_size = 107374182400 #100GB
    volume_creation_option.set_diskSize(disk_size)
    volume_name_thick = "mini_data_volume_thick"
    volume_name_thin = "mini_data_volume_thin"
    #thick
    volume_creation_option.set_name(volume_name_thick)
    volume_thick = test_volume_header.ZstackTestVolume()
    volume_thick.set_volume(vol_ops.create_volume_from_diskSize(volume_creation_option))
    volume_thick.attach(vm)
    volume_thick_uuid = volume_thick.volume.uuid
    #thin
    volume_creation_option.set_name(volume_name_thin)
    volume_creation_option.set_system_tags(["volumeProvisioningStrategy::ThinProvisioning"])
    volume_thin = test_volume_header.ZstackTestVolume()
    volume_thin.set_volume(vol_ops.create_volume_from_diskSize(volume_creation_option))
    volume_thin.attach(vm)
    volume_thin_uuid = volume_thin.volume.uuid

    #3.create thick/thin data volume backup
    backup_creation_option = test_util.BackupOption()
    bs_uuid = res_ops.query_resource(res_ops.BACKUP_STORAGE)[0].uuid
    backup_creation_option.set_backupStorage_uuid(bs_uuid)
    try:
        #thick
        backup_name_thick = "mini_volume_backup_thick%s" % time.time()
        backup_creation_option.set_name(backup_name_thick)
        backup_creation_option.set_volume_uuid(volume_thick_uuid)
        cond_thick = res_ops.gen_query_conditions('name', '=', backup_name_thick)
        backup_thick = vol_ops.create_backup(backup_creation_option)
        #thin
        backup_name_thin = "mini_volume_backup_thin%s" % time.time()
        backup_creation_option.set_name(backup_name_thin)
        backup_creation_option.set_volume_uuid(volume_thin_uuid)
        cond_thin = res_ops.gen_query_conditions('name', '=', backup_name_thin)
        backup_thin = vol_ops.create_backup(backup_creation_option)
    except:
        test_util.test_fail("Fail to create volume backup" )
    if not res_ops.query_resource(res_ops.VOLUME_BACKUP, cond_thick):
        test_util.test_fail("Fail to create thick data volume[%s] backup" % volume_thick_uuid)
    elif not res_ops.query_resource(res_ops.VOLUME_BACKUP, cond_thin):
        test_util.test_fail("Fail to create thin data volume[%s] backup" % volume_thin_uuid)
    else:
        test_util.test_pass("Create thick&thin volume backup Test Pass")

def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)

def env_recover():
    pass 
