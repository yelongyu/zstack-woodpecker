'''
@author: zhaohao.chen
'''

import apibinding.inventory as inventory
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import zstackwoodpecker.operations.vm_operations as vm_ops
import time
import os
import random

test_obj_dict = test_state.TestStateDict()

def test():
    VM_CPU= 8
    VM_MEM = 2147483648 #2GB 

    vm_creation_option = test_util.VmOption()
    backup_creation_option = test_util.BackupOption()
    image_name = os.environ.get('imageName_s')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    l3_name = os.environ.get('l3VlanNetworkName1')
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    #1.create VM with thick provision root volume
    vm_creation_option.set_l3_uuids([l3_net_uuid])
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_cpu_num(VM_CPU)
    vm_creation_option.set_memory_size(VM_MEM)
    vm_creation_option.set_name('MINI_Backup_test_thick')
    vm_thick = test_vm_header.ZstackTestVm()
    vm_thick.set_creation_option(vm_creation_option)
    vm_thick.create()
    vm_thick.check()
    test_obj_dict.add_vm(vm_thick)
    vm_thick_root_volume_uuid = vm_thick.vm.rootVolumeUuid

    #2.create VM with thin provision root volume
    vm_creation_option.set_rootVolume_systemTags(["volumeProvisioningStrategy::ThinProvisioning"])
    vm_thin = test_vm_header.ZstackTestVm()
    vm_thin.set_creation_option(vm_creation_option)
    vm_creation_option.set_name('MINI_Backup_test_thin')
    vm_thin.create()
    vm_thin.check()
    test_obj_dict.add_vm(vm_thin)
    vm_thin_root_volume_uuid = vm_thin.vm.rootVolumeUuid
    
    #3.backup thick/thin vm test
    bs_uuid = res_ops.query_resource(res_ops.BACKUP_STORAGE)[0].uuid
    backup_creation_option.set_backupStorage_uuid(bs_uuid)
    try:
        backup_creation_option.set_volume_uuid(vm_thick_root_volume_uuid)
        backup_name_thick = "mini_thick_vm_backup%s" % time.time()
        backup_name_thin = "mini_thin_vm_backup%s" % time.time()
        backup_creation_option.set_name(backup_name_thick)
        backup_thick = vm_ops.create_vm_backup(backup_creation_option)
        backup_creation_option.set_name(backup_name_thin)
        backup_creation_option.set_volume_uuid(vm_thin_root_volume_uuid)
        backup_thin = vm_ops.create_vm_backup(backup_creation_option)
        cond_thick = res_ops.gen_query_conditions('name', '=', backup_name_thick)
        cond_thin = res_ops.gen_query_conditions('name', '=', backup_name_thin)
    except:
        test_util.test_fail("Fail to create VM backup")
    if not res_ops.query_resource(res_ops.VOLUME_BACKUP, cond_thick):
        test_util.test_fail("Fail to create thick VM[%s] backup" % vm_thick.vm.uuid)
    elif not res_ops.query_resource(res_ops.VOLUME_BACKUP, cond_thin):
        test_util.test_fail("Fail to create thin VM[%s] backup" % vm_thin.vm.uuid)
    else:
        test_util.test_pass("Create thick&thin VM backup Test Pass")

def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)

def env_recover():
    pass 
