'''

New Integration Test for add image from other imageStore.

@author: Glody 
'''

import os
import time
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.zstack_test.zstack_test_image as zstack_image_header

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    has_iamgestore = False
    bs_lst = res_ops.query_resource(res_ops.BACKUP_STORAGE)
    for _bs in range(len(bs_lst)):
        if _bs.type == "ImageStore":
            has_iamgestore = True
                bs = _bs
    if has_iamgestore == False:
        test_util.test_skip('Here does not have ImageStore backup storage. Will skip test.')
    ca_str = os.environ.get('zstore_ca').replace('\\n','\n')
    zstore_url = os.environ.get('zstore_url') 

    image_name = 'test-image-%s' % time.time()
    image_option = test_util.ImageOption()
    image_option.set_name(image_name)
    image_option.set_description('test image from remote imageStore')
    image_option.set_url(zstore_url)
    image_option.set_backup_storage_uuid_list([bs.uuid])
    image_option.set_format('qcow2')
    image_option.set_system_tags("image::cert::%s" %ca_str)
    image_option.set_mediaType('RootVolumeTemplate')
    image_inv = img_ops.add_root_volume_template(image_option)
    time.sleep(10)
    image = zstack_image_header.ZstackTestImage()
    image.set_creation_option(image_option)
    image.set_image(image_inv)
    test_obj_dict.add_image(image)
    image.check()

    vm = test_stub.create_vm(image_name = image_name)
    vm.destroy()

    image.delete()
    test_util.test_pass('Test adding image from remote imageStorage pass.')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
