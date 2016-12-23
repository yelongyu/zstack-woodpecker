'''

New Integration Test for imagecache size on primarystorate.

@author: Quarkonics
'''

import os
import time

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.zstack_test.zstack_test_image as test_image
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.operations.primarystorage_operations as ps_ops
import zstackwoodpecker.zstack_test.zstack_test_image as zstack_image_header
import apibinding.inventory as inventory

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    vm1 = test_stub.create_vr_vm('vm_imagecache', 'imageName_net', 'l3VlanNetwork3')
    test_obj_dict.add_vm(vm1)
    vm1.check()
    vm1.stop()
    image_creation_option = test_util.ImageOption()
    backup_storage_list = test_lib.lib_get_backup_storage_list_by_vm(vm1.get_vm())
    image_creation_option.set_backup_storage_uuid_list([backup_storage_list[0].uuid])
    image_creation_option.set_root_volume_uuid(vm1.get_vm().rootVolumeUuid)
    image_creation_option.set_name('test_create_image_template_imagecache')

    image = test_image.ZstackTestImage()
    image.set_creation_option(image_creation_option)
    image.create()
    test_obj_dict.add_image(image)
    image.check()
    vm2 = test_stub.create_vm('vm_imagecache2', 'test_create_image_template_imagecache', os.environ.get('l3VlanNetwork3'))
    test_obj_dict.add_vm(vm2)

    host = test_lib.lib_find_host_by_vm(vm2.get_vm())
    ps = test_lib.lib_get_primary_storage_by_vm(vm2.get_vm())
    image = test_lib.lib_get_image_by_name('test_create_image_template_imagecache')
    img_ops.sync_image_size(image.uuid)
    image = test_lib.lib_get_image_by_name('test_create_image_template_imagecache')
    img_ops.delete_image(image.uuid)

    if ps.type == inventory.LOCAL_STORAGE_TYPE or ps.type == inventory.NFS_PRIMARY_STORAGE_TYPE or ps.type == 'SharedMountPoint':
        image_cache_path = "%s/imagecache/template/%s/" % (ps.mountPath, image.uuid)
        imagecache_file_size = int(test_lib.lib_get_file_size(host, image_cache_path))
        image_actual_size = int(image.actualSize)
        if imagecache_file_size < image.actualSize*0.99 or imagecache_file_size > image.actualSize*1.01:
            test_util.test_fail('image cache size (%s) not match image actual size(%s)' % (imagecache_file_size, image_actual_size))
    else:
        test_util.test_skip("Skip test when primary storage is not local or NFS")
#    elif ps.type == inventory.CEPH_PRIMARY_STORAGE_TYPE:

    test_lib.lib_error_cleanup(test_obj_dict)
    test_util.test_pass('imagecache cleanup Pass.')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
    pass
