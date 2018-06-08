'''

New Integration Test for add image from MN local URI.

The file should be placed in MN.

@author: Youyk
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
test_image = '/tmp/zstack_wp_test_local_uri.img'

def test():
    bs = res_ops.query_resource(res_ops.BACKUP_STORAGE)[0]
    if bs.type == "Ceph":
        test_util.test_skip('bs: %s is ceph backup storage. Will skip test.' % bs.uuid)
    
    command = 'dd if=/dev/zero of=%s bs=1M count=1 seek=300' % test_image
    test_lib.lib_execute_ssh_cmd(bs.hostname, 'root', 'password', command)
    image_name = 'test-image-%s' % time.time()
    image_option = test_util.ImageOption()
    image_option.set_name(image_name)
    image_option.set_description('test image which is upload from local filesystem.')
    image_option.set_url('file://%s' % test_image)
    image_option.set_backup_storage_uuid_list([bs.uuid])
    image_option.set_format('raw')
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
    command = 'ls %s' % test_image
    if not test_lib.lib_execute_ssh_cmd(bs.hostname, 'root', 'password', command):
       test_util.test_fail('test image disappeared, after add image.')
    command = 'rm -f %s' % test_image
    result = test_lib.lib_execute_ssh_cmd(bs.hostname, 'root', 'password', command)
    test_util.test_pass('Test adding image from local storage pass.')


#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
    os.system('rm -f %s' % test_image)
