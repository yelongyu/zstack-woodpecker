'''
Test for deleting iso vm ops related test.

The sequence is as follows:
- add iso from url named iso1
- create vm based on iso1 named vm1
- clone vm by vm1 named clonedVm1
- delete iso1
- do vm all ops test on clonedVm1
- expunge iso1
- do vm all ops test on clonedVm1
- create image by clonedVm1 imgName1
- export image of imgName1
- create vm by imgName1 named vmFromImg1
- delete imgName1
- expunge imgName1
- do vm all ops test on vmFromImg1

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
    #skip ceph in c74
    cmd = "cat /etc/redhat-release | grep '7.4'"
    mn_ip = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].hostName
    rsp = test_lib.lib_execute_ssh_cmd(mn_ip, 'root', 'password', cmd, 180)
    if rsp != False:
        ps = res_ops.query_resource(res_ops.PRIMARY_STORAGE)
        for i in ps:
            if i.type == 'Ceph':
                test_util.test_skip('cannot hotplug iso to the vm in ceph,it is a libvirt bug:https://bugzilla.redhat.com/show_bug.cgi?id=1541702.')

    global image
    global test_obj_dict
    allow_bs_list = [inventory.IMAGE_STORE_BACKUP_STORAGE_TYPE, inventory.CEPH_BACKUP_STORAGE_TYPE]
    test_lib.skip_test_when_bs_type_not_in_list(allow_bs_list)

    allow_ps_list = [inventory.CEPH_PRIMARY_STORAGE_TYPE, inventory.NFS_PRIMARY_STORAGE_TYPE, 'SharedMountPoint']
    test_lib.skip_test_when_ps_type_not_in_list(allow_ps_list)

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
    memorySize = 1024*1024*1024
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
    img_option.set_url(os.environ.get('isoForVmUrl'))
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

    #clone vm
    cloned_vm_name = ['cloned_vm_name']
    cloned_vm_obj = vm.clone(cloned_vm_name)[0]
    test_obj_dict.add_vm(cloned_vm_obj)

    #delete iso
    image.delete()
    test_obj_dict.rm_image(image)

    #vm ops test
    test_stub.vm_ops_test(cloned_vm_obj, "VM_TEST_ALL")

    #expunge iso
    image.expunge()

    #detach iso
    img_ops.detach_iso(vm.vm.uuid)

    #vm ops test
    test_stub.vm_ops_test(cloned_vm_obj, "VM_TEST_ALL")

    #create image by vm root volume
    cloned_vm_img_name = "cloned_vm_image1"
    img_option2 = test_util.ImageOption()
    img_option2.set_backup_storage_uuid_list([bs_uuid])
    img_option2.set_root_volume_uuid(cloned_vm_obj.vm.rootVolumeUuid)
    img_option2.set_name(cloned_vm_img_name)
    image1 = test_image.ZstackTestImage()
    image1.set_creation_option(img_option2)
    image1.create()
    image1.check()
    test_obj_dict.add_image(image1)

    bs_list = res_ops.query_resource(res_ops.BACKUP_STORAGE)
    if inventory.IMAGE_STORE_BACKUP_STORAGE_TYPE == bs_list[0] and len(bs_list) == 1 :
        #export image
        image1.export()

    #create vm 
    vm2 = test_stub.create_vm('image-vm', cloned_vm_img_name, l3_name)

    #delete image
    image1.delete()
    test_obj_dict.rm_image(image1)

    #vm ops test
    test_stub.vm_ops_test(vm2, "VM_TEST_ALL")

    #expunge image
    image1.expunge()

    #vm ops test
    test_stub.vm_ops_test(vm2, "VM_TEST_ALL")

    vm.destroy()
    vm2.destroy()
    cloned_vm_obj.destroy()

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
        image1.delete()
    except:
        pass
