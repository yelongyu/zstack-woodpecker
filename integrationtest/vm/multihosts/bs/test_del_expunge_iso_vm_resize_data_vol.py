'''
Test for deleting vm iso check vm change os.
@author: SyZhao
'''

import os
import apibinding.inventory as inventory
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_image as test_image
import zstackwoodpecker.zstack_test.zstack_test_image as zstack_image_header
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.image_operations as img_ops

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
image = None

def test():
    global image
    global test_obj_dict

    #run condition
    hosts = res_ops.query_resource(res_ops.HOST)
    if len(hosts) <= 1:
        test_util.test_skip("skip for host_num is not satisfy condition host_num>1")

    bs_cond = res_ops.gen_query_conditions("status", '=', "Connected")
    bss = res_ops.query_resource_fields(res_ops.BACKUP_STORAGE, bs_cond, None, fields=['uuid'])

    #create disk offering
    data_volume_size = 10737418240
    disk_offering_option = test_util.DiskOfferingOption()
    disk_offering_option.set_name('root-disk-iso')
    disk_offering_option.set_diskSize(data_volume_size)
    data_volume_offering = vol_ops.create_volume_offering(disk_offering_option)
    test_obj_dict.add_disk_offering(data_volume_offering)

    #create instance offering
    cpuNum = 2
    memorySize = 2147483648
    name = 'iso-vm-offering'
    new_offering_option = test_util.InstanceOfferingOption()
    new_offering_option.set_cpuNum(cpuNum)
    new_offering_option.set_memorySize(memorySize)
    new_offering_option.set_name(name)
    new_offering = vm_ops.create_instance_offering(new_offering_option)
    test_obj_dict.add_instance_offering(new_offering)

    #add iso
    img_option = test_util.ImageOption()
    img_option.set_name('iso1')
    bs_uuid = res_ops.query_resource_fields(res_ops.BACKUP_STORAGE, [], None)[0].uuid
    img_option.set_backup_storage_uuid_list([bs_uuid])
    img_option.set_url('http://172.20.1.15:7480/iso/CentOS-x86_64-7.2-Minimal.iso')
    image_inv = img_ops.add_iso_template(img_option)
    image_uuid = image_inv.uuid
    image = test_image.ZstackTestImage()
    image.set_image(image_inv)
    image.set_creation_option(img_option)
    test_obj_dict.add_image(image)

    #create vm by iso
    l3_name = os.environ.get('l3VlanNetworkName1')
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    root_disk_uuid = data_volume_offering.uuid
    vm = test_stub.create_vm_with_iso([l3_net_uuid], image_uuid, 'iso-vm', root_disk_uuid, new_offering.uuid)
    host_ip = test_lib.lib_find_host_by_vm(vm.get_vm()).managementIp
    test_obj_dict.add_vm(vm)
    
    #check vm
    vm_inv = vm.get_vm()
    vm_ip = vm_inv.vmNics[0].ip

    #cmd ='[ -e /root ]'
    #ssh_timeout = test_lib.SSH_TIMEOUT
    #test_lib.SSH_TIMEOUT = 3600
    test_lib.lib_set_vm_host_l2_ip(vm_inv)
    test_lib.lib_wait_target_up(vm.get_vm().vmNics[0].ip, 22, 1800)
    #if not test_lib.lib_ssh_vm_cmd_by_agent_with_retry(host_ip, vm_ip, 'root', 'password', cmd):
    #    test_lib.SSH_TIMEOUT = ssh_timeout
    #    test_util.test_fail("iso has been failed to installed.")

    #test_lib.SSH_TIMEOUT = ssh_timeout

    #delete iso
    image.delete()
    test_obj_dict.rm_image(image)

    #expunge iso
    image.expunge()

    #detach iso
    img_ops.detach_iso(vm.vm.uuid)

    #vm ops test
    test_stub.vm_ops_test(vm, "VM_TEST_RESIZE_DVOL")

    vm.destroy()
    vol_ops.delete_disk_offering(root_disk_uuid)
    vm_ops.delete_instance_offering(new_offering.uuid)
    test_obj_dict.rm_vm(vm)
    test_obj_dict.rm_disk_offering(data_volume_offering)
    test_obj_dict.rm_instance_offering(new_offering)

    test_lib.lib_robot_cleanup(test_obj_dict)
    test_util.test_pass('Create VM Image in Image Store Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global image
    global test_obj_dict

    test_lib.lib_error_cleanup(test_obj_dict)
    try:
        image.delete()
    except:
        pass
