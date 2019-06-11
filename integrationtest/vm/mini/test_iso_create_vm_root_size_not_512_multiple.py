'''

New Integration Test for creating KVM VM with ISO, the Root Disk Size is not a multiple of 512.

@author: Legion
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

test_stub = test_lib.lib_get_test_stub('mini')
test_obj_dict = test_state.TestStateDict()

def test():
    global ssh_timeout
    data_volume_size = 11111111111
    disk_offering_option = test_util.DiskOfferingOption()
    disk_offering_option.set_name('root-disk-iso')
    disk_offering_option.set_diskSize(data_volume_size)
    data_volume_offering = vol_ops.create_volume_offering(disk_offering_option)
    test_obj_dict.add_disk_offering(data_volume_offering)

    cpuNum = 2
    memorySize = 536870912
    name = 'vm-offering-for-iso-vm'
    new_offering_option = test_util.InstanceOfferingOption()
    new_offering_option.set_cpuNum(cpuNum)
    new_offering_option.set_memorySize(memorySize)
    new_offering_option.set_name(name)
    new_offering = vm_ops.create_instance_offering(new_offering_option)
    test_obj_dict.add_instance_offering(new_offering)

    img_option = test_util.ImageOption()
    img_option.set_name('iso_for_install_vm_test')
    bs_uuid = res_ops.query_resource_fields(res_ops.BACKUP_STORAGE, [], None)[0].uuid
    img_option.set_backup_storage_uuid_list([bs_uuid])
    img_option.set_url(os.environ.get('imageServer')+'/iso/iso_for_install_vm_test.iso')
    image_inv = img_ops.add_iso_template(img_option)
    image_uuid = image_inv.uuid
    image = test_image.ZstackTestImage()
    image.set_image(image_inv)
    image.set_creation_option(img_option)
    test_obj_dict.add_image(image)

    l3_name = os.environ.get('l3VlanNetworkName1')
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    root_disk_uuid = data_volume_offering.uuid
    vm = test_stub.create_vm_with_iso([l3_net_uuid], image_uuid, 'vm-iso', root_disk_uuid, new_offering.uuid)
    host_ip = test_lib.lib_find_host_by_vm(vm.get_vm()).managementIp
    test_obj_dict.add_vm(vm)
    
    test_util.test_dsc('wait for iso installation')    
    vm_inv = vm.get_vm()
    vm_ip = vm_inv.vmNics[0].ip

    #test_lib.lib_wait_target_up(vm_ip, '22', 2400)
    #vm.check()

    #cmd ='[ -e /root ] && echo yes || echo no' 
    cmd ='[ -e /root ]'
    #ssh_num = 0
    #ssh_ok = 0
    #while ssh_num <= 5 and ssh_ok == 0 :
    #    rsp = test_lib.lib_execute_ssh_cmd(vm_ip, 'root', 'password', cmd, 180)
    #    if rsp == False:
    #        time.sleep(30)
    #    else:
    #        ssh_ok = 1
    #        break  
    #    ssh_num = ssh_num + 1

    #if ssh_ok == 0:
    #    test_util.test_fail('fail to ssh to VM')
    ssh_timeout = test_lib.SSH_TIMEOUT
    test_lib.SSH_TIMEOUT = 3600
    test_lib.lib_set_vm_host_l2_ip(vm_inv)
    if not test_lib.lib_ssh_vm_cmd_by_agent_with_retry(host_ip, vm_ip, 'root', 'password', cmd):
        test_lib.SSH_TIMEOUT = ssh_timeout
        test_util.test_fail("ISO installation failed.")

    # Create root volume template
    image_creation_option = test_util.ImageOption()
    backup_storage_list = test_lib.lib_get_backup_storage_list_by_vm(vm.vm)
    image_creation_option.set_backup_storage_uuid_list([backup_storage_list[0].uuid])
    image_creation_option.set_root_volume_uuid(vm.vm.rootVolumeUuid)
    image_creation_option.set_name('test_create_image_template')
    bs_type = backup_storage_list[0].type
    if bs_type == 'Ceph':
        origin_interval = conf_ops.change_global_config('ceph', 'imageCache.cleanup.interval', '1')

    template = test_image.ZstackTestImage()
    template.set_creation_option(image_creation_option)
    template.create()

    test_obj_dict.add_image(template)
#     template.check()


    # Create VM with root volume template
    test_util.test_dsc('Use new created Image to create a VM')
    new_img_uuid = template.image.uuid

    vm_creation_option = vm.get_creation_option()
    vm_creation_option.set_name('vm_created_from_iso_vm_template')
    vm_creation_option.set_root_disk_uuid(None)
    vm_creation_option.set_image_uuid(new_img_uuid)

    vm2 = test_vm.ZstackTestVm()
    vm2.set_creation_option(vm_creation_option)
    vm2.create()
    test_obj_dict.add_vm(vm2)
    vm2.check()
    vm.check()
    vm2.destroy()

    vm.destroy()
    template.delete()
    if bs_type == 'Ceph':
        time.sleep(60)
#     template.check()

    if bs_type == 'Ceph':
        conf_ops.change_global_config('ceph', 'imageCache.cleanup.interval', origin_interval)

    test_lib.SSH_TIMEOUT = ssh_timeout
    vm.destroy()
    test_obj_dict.rm_vm(vm)

    image.delete()
    test_obj_dict.rm_image(image)

    vol_ops.delete_disk_offering(root_disk_uuid)
    test_obj_dict.rm_disk_offering(data_volume_offering)

    vm_ops.delete_instance_offering(new_offering.uuid)
    test_obj_dict.rm_instance_offering(new_offering)

    test_util.test_pass('Create VM with ISO and the given Root Disk Size not 512 multiple Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)

