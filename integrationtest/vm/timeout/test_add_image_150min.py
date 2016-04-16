'''

New Integration Test for adding image in 2.5 hours.

@author: Youyk
'''

import os
import time

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_image as zstack_image_header

_config_ = {
        'timeout' : 9500,
        'noparallel' : False
        }

def test():
    bs_cond = res_ops.gen_query_conditions("status", '=', "Connected")
    bss = res_ops.query_resource_fields(res_ops.BACKUP_STORAGE, bs_cond, \
            None, fields=['uuid'])
    if not bss:
        test_util.test_skip("not find available backup storage. Skip test")

    image_option = test_util.ImageOption()
    image_option.set_name('test_150min_downloading_image')
    image_option.set_format('qcow2')
    image_option.set_mediaType('RootVolumeTemplate')
    image_option.set_url(os.environ.get('timeout150MinImageUrl'))
    image_option.set_backup_storage_uuid_list([bss[0].uuid])
    image_option.set_timeout(12000)

    new_image = zstack_image_header.ZstackTestImage()
    new_image.set_creation_option(image_option)

    time1 = time.time()
    new_image.add_root_volume_template()
    time2 = time.time()

    cost_time = time2 - time1
    if cost_time < 7200:
        test_util.test_fail('The test image is added less than 2 hours: \
%s, which does not meet the test criterial.' % cost_time)

    new_image.delete()
    new_image.expunge([bss[0].uuid])
    test_util.test_pass('Add Image with 150 mins Pass.')

#Will be called only if exception happens in test().
def error_cleanup():
    pass
