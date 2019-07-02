'''

New Integration Test for creating KVM VM with windows/ubuntu/fedora/centos images

@author: zhaohao.chen
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.zstack_test.zstack_test_image as test_image
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm
import zstackwoodpecker.operations.config_operations as conf_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import time
import os

WINDOWS_URL = 'http://172.20.1.22/mirror/diskimages/windows-2012-cn-qcow2.qcow2'
UBUNTU_URL = 'http://172.20.1.22/mirror/diskimages/ubuntu14-test.qcow2'
CENTOS_URL = 'http://172.20.1.22/mirror/diskimages/centos7-test.qcow2.no-qemu-ga'
FEDORA_URL = 'http://172.20.1.27/mirror/diskimages/fedora30.qcow2'

WINDOWS = 'windows'
UBUNTU = 'ubuntu'
CENTOS = 'centos'
FEDORA = 'fedora'

image_name_list = [WINDOWS, UBUNTU, CENTOS, FEDORA]
image_url_list = [WINDOWS_URL, UBUNTU_URL, CENTOS_URL, FEDORA_URL]
VM_CPU= 2
VM_MEM = 2147483648 #2GB
image_uuid_list = []
test_obj_dict = test_state.TestStateDict()

def add_image(image_option, image_name, image_url):
    global test_obj_dict
    image_option.set_name(image_name)
    image_option.set_url(image_url)
    image_inv = img_ops.add_image(image_option)
    image_uuid = image_inv.uuid
    image = test_image.ZstackTestImage()
    image.set_image(image_inv)
    image.set_creation_option(image_option)
    test_obj_dict.add_image(image)
    return image_uuid

def create_vm(vm_creation_option, image_uuid, image_name):
    global test_obj_dict
    vm_creation_option.set_image_uuid(image_uuid)
    vm = test_vm.ZstackTestVm()
    vm_creation_option.set_name("vm-%s" % image_name)
    vm.set_creation_option(vm_creation_option)
    vm.create()
    #vm.destroy()
    #vm.expunge()
    
def test():
    #add images
    img_option = test_util.ImageOption()
    bs_uuid = res_ops.query_resource_fields(res_ops.BACKUP_STORAGE, [], None)[0].uuid
    img_option.set_backup_storage_uuid_list([bs_uuid])
    img_option.set_format('qcow2')
    for img_name,img_url in zip(image_name_list, image_url_list):
        image_uuid_list.append(add_image(img_option, img_name, img_url))
        
    #create vms
    vm_creation_option = test_util.VmOption()
    l3_name = os.environ.get('l3VlanNetworkName1')
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    vm_creation_option.set_l3_uuids([l3_net_uuid])
    vm_creation_option.set_cpu_num(VM_CPU)
    vm_creation_option.set_memory_size(VM_MEM)
    for img_uuid,img_name in zip(image_uuid_list, image_name_list):
        create_vm(vm_creation_option, img_uuid, img_name)
    test_util.test_pass('Create VM with %s images Success' % image_name_list)


#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)


