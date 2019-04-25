'''

New Integration Test for creating KVM VM with ISO.

@author: Pengtao.Zhang
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.zstack_test.zstack_test_image as test_image
import zstackwoodpecker.operations.vm_operations as vm_ops
import test_stub
import time
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    global ssh_timeout
    data_volume_size = 10737418240
    disk_offering_option = test_util.DiskOfferingOption()
    disk_offering_option.set_name('root-disk-iso')
    disk_offering_option.set_diskSize(data_volume_size)
    data_volume_offering = vol_ops.create_volume_offering(disk_offering_option)
    test_obj_dict.add_disk_offering(data_volume_offering)

    cpuNum = 1
    memorySize = 536870912
    name = 'vm-offering-iso'
    new_offering_option = test_util.InstanceOfferingOption()
    new_offering_option.set_cpuNum(cpuNum)
    new_offering_option.set_memorySize(memorySize)
    new_offering_option.set_name(name)
    new_offering = vm_ops.create_instance_offering(new_offering_option)
    test_obj_dict.add_instance_offering(new_offering)

    img_option = test_util.ImageOption()
    img_option.set_name('image-iso')
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
        test_util.test_fail("iso has not been failed to installed.")

    test_lib.SSH_TIMEOUT = ssh_timeout
    vm.destroy()
    test_obj_dict.rm_vm(vm)

    image.delete()
    test_obj_dict.rm_image(image)

    vol_ops.delete_disk_offering(root_disk_uuid)
    test_obj_dict.rm_disk_offering(data_volume_offering)

    vm_ops.delete_instance_offering(new_offering.uuid)
    test_obj_dict.rm_instance_offering(new_offering)

    test_util.test_pass('Create VM with ISO Installation Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)

