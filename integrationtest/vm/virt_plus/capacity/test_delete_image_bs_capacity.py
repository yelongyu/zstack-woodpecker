'''

New Integration Test for bs capacity when delete added image.

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

_config_ = {
        'timeout' : 200,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
test_image = '/tmp/zstack_wp_test_local_uri.img'
delete_policy = None

def test():
    global delete_policy
    delete_policy = test_lib.lib_set_delete_policy('image', 'Direct')

    os.system('dd if=/dev/zero of=%s bs=1M count=1 seek=300' % test_image)
    time.sleep(1)
    bs = res_ops.query_resource(res_ops.BACKUP_STORAGE)[0]
    img_ops.reconnect_sftp_backup_storage(bs.uuid)
    time.sleep(1)
    image_name = 'test-image-%s' % time.time()
    image_option = test_util.ImageOption()
    image_option.set_name(image_name)
    image_option.set_description('test image which is upload from local filesystem.')
    image_option.set_url('file://%s' % test_image)
    bs = res_ops.query_resource(res_ops.BACKUP_STORAGE)[0]
    avail_cap = bs.availableCapacity
    total_cap = bs.totalCapacity

    image_option.set_backup_storage_uuid_list([bs.uuid])
    image_option.set_format('raw')
    image_option.set_mediaType('RootVolumeTemplate')
    image_inv = img_ops.add_root_volume_template(image_option)
    time.sleep(10)
    image = zstack_image_header.ZstackTestImage()
    image.set_creation_option(image_option)
    image.set_image(image_inv)
    test_obj_dict.add_image(image)

    bs = res_ops.query_resource(res_ops.BACKUP_STORAGE)[0]
    avail_cap1 = bs.availableCapacity
    total_cap1 = bs.totalCapacity

    if total_cap != total_cap1:
        test_util.test_fail('Backup storage total capacity is not same, after adding new image: %s. The previous value: %s, the current value: %s' % (image_inv.uuid, total_cap, total_cap1))

    if avail_cap <= avail_cap1 :
        test_util.test_fail('Backup storage available capacity is not correct, after adding new image: %s. The previous value: %s, the current value: %s' % (image_inv.uuid, avail_cap, avail_cap1))

    image.delete()
    bs = res_ops.query_resource(res_ops.BACKUP_STORAGE)[0]
    avail_cap2 = bs.availableCapacity
    total_cap2 = bs.totalCapacity

    if total_cap != total_cap2 :
        test_util.test_fail('Backup storage total capacity is not same, after deleting new image: %s. The previous value: %s, the current value: %s' % (image_inv.uuid, total_cap, total_cap2))

    if avail_cap > (avail_cap2 + 1024000) or avail_cap < avail_cap2:
        test_util.test_fail('Backup storage available capacity is not correct, after adding and deleting new image: %s. The previous value: %s, the current value: %s' % (image_inv.uuid, avail_cap, avail_cap2))

    os.system('rm -f %s' % test_image)
    test_lib.lib_set_delete_policy('image', delete_policy)
    test_util.test_pass('Test backup storage capacity for adding/deleting image pass.')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
    os.system('rm -f %s' % test_image)
    test_lib.lib_set_delete_policy('image', delete_policy)
