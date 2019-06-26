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

vm = None
def test():
    global vm

    VM_CPU= 8
    #VM_MEM = 17179869184 #16GB 
    VM_MEM = 2147483648 #2GB 

    vm_creation_option = test_util.VmOption()
    backup_creation_option = test_util.BackupOption()
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
    vm_root_volume_uuid = vm.vm.rootVolumeUuid
    bs_uuid = res_ops.query_resource(res_ops.BACKUP_STORAGE)[0].uuid
    backup_creation_option.set_backupStorage_uuid(bs_uuid)
    backup_creation_option.set_volume_uuid(vm_root_volume_uuid)
    backup_name = "mini_vm_backup%s" % time.time()
    backup_creation_option.set_name(backup_name)
    cond = res_ops.gen_query_conditions('name', '=', backup_name)
    #Create VM rootvolume backup
    try:
        invs = vm_ops.create_vm_backup(backup_creation_option)
    except:
        test_util.test_fail("Fail to create VM[%s] backup" % vm.vm.uuid)
    if not invs:
        test_util.test_fail("Fail to create VM[%s] backup" % vm.vm.uuid)
    elif not res_ops.query_resource(res_ops.VOLUME_BACKUP, cond):
        test_util.test_fail("Fail to create VM[%s] backup" % vm.vm.uuid)
    else:
        test_util.test_pass("Create VM[%s] backup Test Pass" % vm.vm.uuid)

def error_cleanup():
    global vm
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)

def env_recover():
    pass 
