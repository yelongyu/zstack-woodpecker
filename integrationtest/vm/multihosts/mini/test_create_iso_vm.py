'''

VM creation with ISO test for Mini

@author: Jiajun
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import zstackwoodpecker.operations.image_operations as img_ops
import time
import os
import random

vm = None

VM_CPU = [1, 2, 3, 4, 7, 8, 15, 16, 20, 32]

# 256M, 512M, 1G, 2G
VM_MEM = [268435456, 536870912, 1073741824, 2147483648]

# 4G, 8G, 16G
VM_ROOT_DISK = [4294967296, 8589934592, 17179869184]

def deploy_vdbench(vm):
    host = test_lib.lib_get_vm_host(vm.get_vm())
    cmd = "yum install -y java wget"
    cmd_result = test_lib.lib_ssh_vm_cmd_by_agent_with_retry(host.managementIp, vm.get_vm().vmNics[0].ip, test_lib.lib_get_vm_username(vm.get_vm()), test_lib.lib_get_vm_password(vm.get_vm()), cmd)
    cmd = "wget -np -r -nH --cut-dirs=2 http://172.20.1.27/mirror/vdbench/"
    cmd_result = test_lib.lib_ssh_vm_cmd_by_agent_with_retry(host.managementIp, vm.get_vm().vmNics[0].ip, test_lib.lib_get_vm_username(vm.get_vm()), test_lib.lib_get_vm_password(vm.get_vm()), cmd)

def test():
    global vm
    vm_creation_option = test_util.VmOption()
    #image_name = os.environ.get('imageName_s')
    #image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    l3_name = os.environ.get('l3VlanNetworkName1')

    # add iso
    img_option = test_util.ImageOption()
    img_option.set_name('iso1')
    bs_uuid = res_ops.query_resource_fields(res_ops.BACKUP_STORAGE, [], None)[0].uuid
    img_option.set_backup_storage_uuid_list([bs_uuid])
    img_option.set_url(os.environ.get('isoForVmUrl'))
    image_inv = img_ops.add_iso_template(img_option)
    image_uuid = image_inv.uuid

    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    vm_creation_option.set_l3_uuids([l3_net_uuid])
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_name('multihost_basic_vm')

    #image = test_image.ZstackTestImage()
    #image.set_image(image_inv)
    #image.set_creation_option(img_option)

    for i in range(1, 6):
        vm_creation_option.set_cpu_num(random.choice(VM_CPU))
        vm_creation_option.set_memory_size(random.choice(VM_MEM))
        vm_creation_option.set_root_disk_size(random.choice(VM_ROOT_DISK))
        vm = test_vm_header.ZstackTestVm()
        vm.set_creation_option(vm_creation_option)
        vm.create()
        vm.check()
        deploy_vdbench(vm)
        vm.destroy()
        time.sleep(5)
    test_util.test_pass('Create VM with ISO Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    if vm:
        try:
            vm.destroy()
        except:
            pass
