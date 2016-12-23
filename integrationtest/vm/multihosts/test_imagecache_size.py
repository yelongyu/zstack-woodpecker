'''

New Integration Test for imagecache size on primarystorate.

@author: Quarkonics
'''

import os
import time

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.primarystorage_operations as ps_ops
import zstackwoodpecker.zstack_test.zstack_test_image as zstack_image_header
import apibinding.inventory as inventory

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    vm = test_stub.create_vr_vm('vm_imagecache', 'imageName_net', 'l3VlanNetwork3')
    test_obj_dict.add_vm(vm)
    vm.check()
    host = test_lib.lib_find_host_by_vm(vm.get_vm())
    ps = test_lib.lib_get_primary_storage_by_vm(vm.get_vm())
    image = test_lib.lib_get_image_by_name(os.environ.get('imageName_net'))

    if ps.type == inventory.LOCAL_STORAGE_TYPE or ps.type == inventory.NFS_PRIMARY_STORAGE_TYPE or ps.type == 'SharedMountPoint':
        image_cache_path = "%s/imagecache/template/%s/" % (ps.mountPath, image.uuid)
        imagecache_file_size = int(test_lib.lib_get_file_size(host, image_cache_path))
        image_actual_size = int(image.actualSize)
        if imagecache_file_size < image.actualSize*0.99 or imagecache_file_size > image.actualSize*1.01:
            test_util.test_fail('image cache size (%s) not match image actual size(%s)' % (imagecache_file_size, image_actual_size))
    else:
        test_util.test_skip("Skip test when primary storage is not local or NFS")
#    elif ps.type == inventory.CEPH_PRIMARY_STORAGE_TYPE:

    test_util.test_pass('imagecache cleanup Pass.')

#Will be called only if exception happens in test().
def error_cleanup():
    pass
