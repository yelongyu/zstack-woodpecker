'''

New Integration test for add image progress.

@author: quarkonics
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_image as zstack_image_header
import apibinding.inventory as inventory
import threading
import os
import time
_config_ = {
        'timeout' : 1800,
        'noparallel' : True
        }

test_obj_dict = test_state.TestStateDict()
threads_num = 5
images = [None] * threads_num
threads = [None] * threads_num
checker_threads = [None] * threads_num

def add_image(bs_uuid, index):
    global images

    image_option = test_util.ImageOption()
    image_option.set_name('test_add_image_progress%s' % (index))
    image_option.set_format('qcow2')
    image_option.set_mediaType('RootVolumeTemplate')
    image_option.set_url(os.environ.get('imageUrl_net'))
    image_option.set_backup_storage_uuid_list([bs_uuid])

    images[index] = zstack_image_header.ZstackTestImage()
    images[index].set_creation_option(image_option)

    images[index].add_root_volume_template()
    test_obj_dict.add_image(images[index])

def check_add_image_progress(index):
    for i in range(0, 100):
        time.sleep(0.1)
        image_cond = res_ops.gen_query_conditions("status", '=', "Downloading")
        image_cond = res_ops.gen_query_conditions("name", '=', 'test_add_image_progress%s' % (index), image_cond)
        image = res_ops.query_resource_fields(res_ops.IMAGE, image_cond, \
                None, fields=['uuid'])
        if len(image) >= 1:
            break

    if len(image) <= 0:
        test_util.test_fail("image is not in creating after 10 seconds")

    for i in range(0, 100):
        progress = res_ops.get_task_progress(image[0].uuid)
        if progress.progress != None:
            break
        else:
            test_util.test_logger('task progress still not ready')
        time.sleep(0.1)

    if int(progress.progress) < 0 or int(progress.progress) > 100:
        test_util.test_fail("Progress of task should be between 0 and 100, while it actually is %s" % (progress.progress))

    for i in range(0, 3600):
        last_progress = progress
        progress = res_ops.get_task_progress(image[0].uuid)
	if progress.progress == None:
            break
        if progress.progress < last_progress.progress:
            test_util.test_fail("Progress of task is smaller than last time")

    image_cond = res_ops.gen_query_conditions("uuid", '=', image_query[0].uuid)
    image_query2 = res_ops.query_resource_fields(res_ops.IMAGE, image_cond, \
                   None, fields=['status'])
    if image_query2[0].status != "Ready":
        test_util.test_fail("Image should be ready when no progress anymore")

def test():
    global threads
    global checker_threads
    bs_cond = res_ops.gen_query_conditions("status", '=', "Connected")
    bss = res_ops.query_resource_fields(res_ops.BACKUP_STORAGE, bs_cond, \
            None)
    if not bss:
        test_util.test_skip("not find available backup storage. Skip test")
    if bss[0].type != inventory.CEPH_BACKUP_STORAGE_TYPE:
        if hasattr(inventory, 'IMAGE_STORE_BACKUP_STORAGE_TYPE') and bss[0].type != inventory.IMAGE_STORE_BACKUP_STORAGE_TYPE:
            test_util.test_skip("not find available imagestore or ceph backup storage. Skip test")

    for i in range(0, threads_num):
        threads[i] = threading.Thread(target=add_image, args=(bss[0].uuid, i, ))
        threads[i].start()
    for i in range(0, threads_num):
        checker_threads[i] = threading.Thread(target=check_add_image_progress, args=(i, ))
        checker_threads[i].start()

    for i in range(0, threads_num):
        checker_threads[i].join()
        threads[i].join()
        images[i].check()
        images[i].delete()

    test_util.test_pass('Add image Progress Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)

