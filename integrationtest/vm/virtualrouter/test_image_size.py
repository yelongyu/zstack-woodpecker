'''

New Integration Test for image size comparison between database and storage.

Step-1 Create a vm1
Step-2 Create a image1 from the vm1's root volume
Step-3 Create another vm2 with the image created by step-2
Step-4 Create a image2 from the vm2 created by step-3
Step-5 Compare the image2 size in backupstorage path and in database, \
check if the size and realsize are same between in backupstorage path \
and in database.

@author: Glody 
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.primarystorage_operations as ps_ops
import zstackwoodpecker.zstack_test.zstack_test_image as zstack_image_header
import zstackwoodpecker.zstack_test.zstack_test_image as test_image
import apibinding.inventory as inventory

import os
import time

_config_ = {
        'timeout' : 600,
        'noparallel' : True
        }
test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    node_ip = "localhost"
    host_username = "root"
    host_password = "password"
    if res_ops.query_resource(res_ops.SFTP_BACKUP_STORAGE):
        bs = res_ops.query_resource(res_ops.SFTP_BACKUP_STORAGE)[0]
    else:
        test_util.test_skip("No sftp backupstorage for test. Skip test")

    image_name = os.environ.get('imageName_net')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    l3_name = os.environ.get('l3VlanNetworkName1')
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    l3_net_list = [l3_net_uuid]
    vm1 = test_stub.create_vm(l3_net_list,image_uuid,'test_image_size_vm1')
    test_obj_dict.add_vm(vm1)
    vm1.stop() #commit backup storage specified need stop vm first
    image_creation_option = test_util.ImageOption()
    image_creation_option.set_backup_storage_uuid_list([bs.uuid])
    image_creation_option.set_root_volume_uuid(vm1.vm.rootVolumeUuid)
    image_creation_option.set_name('create_vm_image_from_root_volume')
    image1 = test_image.ZstackTestImage()
    image1.set_creation_option(image_creation_option)
    image1.create()
    test_obj_dict.add_image(image1)
    image1.check()

    vm1.destroy()

    target_image_name = 'target_comparion_image'
    image_uuid = test_lib.lib_get_image_by_name('create_vm_image_from_root_volume').uuid
    vm2 = test_stub.create_vm(l3_net_list,image_uuid,'test_image_size_vm2')
    test_obj_dict.add_vm(vm2)
    vm2.stop() #commit backup storage specified need stop vm first
    image_creation_option.set_root_volume_uuid(vm2.vm.rootVolumeUuid)
    image_creation_option.set_name(target_image_name)
    image2 = test_image.ZstackTestImage()
    image2.set_creation_option(image_creation_option)
    image2.create()
    test_obj_dict.add_image(image2)

    vm2.destroy()

    cond = res_ops.gen_query_conditions('backupStorageRef.backupStorage.uuid', '=', bs.uuid)
    images =  res_ops.query_resource(res_ops.IMAGE, cond)
    for image in images:
        image_name = image.name
        image_uuid = image.uuid
        image_path = image.backupStorageRefs[0].installPath
        image_size = image.size
        image_actual_size = image.actualSize
        if image_name == target_image_name:
            cmd = "ls -al %s|awk '{print $5}'" %image_path
            rsp = test_lib.lib_execute_ssh_cmd(node_ip, host_username, host_password, cmd, 180)
            #store_actual_size = int(rsp.rstrip())
            store_actual_size = rsp
            if store_actual_size != image_actual_size:
                test_util.test_fail('The image actual size is different. Size in database is %s, in the storage path is %s' %(str(image_actual_size), str(store_actual_size)))
            cmd = "qemu-img info %s|grep 'virtual size'|awk -F'(' '{print $2}'|awk '{print $1}'" %image_path
            rsp = test_lib.lib_execute_ssh_cmd(node_ip, host_username, host_password, cmd, 180)
            #store_size = int(rsp.rstrip())
            store_size = rsp
            if store_size != image_size:
                test_util.test_fail('The image size is different. Size in database is %s, in the storage path is %s' %(str(image_size), str(store_size)))

    image1.delete()
    image2.delete()
    test_lib.lib_robot_cleanup(test_obj_dict)
    test_util.test_pass('imagecache cleanup Pass.')

#Will be called only if exception happens in test().
def error_cleanup():
    pass
