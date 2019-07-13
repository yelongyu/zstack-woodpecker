'''

Integration test for checking root volume VirtIO bus type on mini.

@author: zhaohao.chen
'''

import apibinding.inventory as inventory
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_volume as test_volume_header
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import time
import os
import random

PROVISION = ["volumeProvisioningStrategy::ThinProvisioning","volumeProvisioningStrategy::ThickProvisioning"]
volume_name_thin = "volume_thin"
volume_name_thick = "volume_thick"
VM_CPU= 2
VM_MEM = 2147483648 #2GB 
vm = None

def virtio_bus_type_check(vm):
    vm_uuid = vm.get_vm().uuid
    cmd = "virsh dumpxml %s|grep bus|grep scsi" % vm_uuid
    cond = res_ops.gen_query_conditions('uuid', '=', vm_uuid) 
    host_uuid = res_ops.query_resource_fields(res_ops.VM_INSTANCE, cond)[0].hostUuid
    cond = res_ops.gen_query_conditions('uuid', '=', host_uuid)
    host_ip = res_ops.query_resource_fields(res_ops.HOST, cond)[0].managementIp
    ret = test_lib.lib_execute_ssh_cmd(host_ip, 'root', 'password', cmd)
    test_util.test_logger(cmd)
    if ret:
        test_util.test_fail("root volume of %s is not virtio-BLK" % vm.get_vm().name)
        
def test():
    global vm
    #create thin & thick vm
    vm_creation_option = test_util.VmOption()
    image_name = os.environ.get('imageName_s')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    l3_name = os.environ.get('l3VlanNetworkName1')
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid

    #thin
    vm_creation_option.set_l3_uuids([l3_net_uuid])
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_cpu_num(VM_CPU)
    vm_creation_option.set_memory_size(VM_MEM)
    vm_creation_option.set_rootVolume_systemTags([PROVISION[0]])
    vm_creation_option.set_name('MINI_test_vblk_thin')
    vm = test_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    vm.check()     
    virtio_bus_type_check(vm)

    #thick
    vm_creation_option.set_rootVolume_systemTags([PROVISION[1]])
    vm_creation_option.set_name('MINI_test_vblk_thick')
    vm = test_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    vm.check()     
    virtio_bus_type_check(vm)
    
    test_util.test_pass("Mini Root Volume VBLK Check Test Success")

def error_cleanup():
    pass
