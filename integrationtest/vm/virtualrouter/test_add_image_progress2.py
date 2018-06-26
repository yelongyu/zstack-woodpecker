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
import uuid
_config_ = {
        'timeout' : 1800,
        'noparallel' : True
        }

test_obj_dict = test_state.TestStateDict()
threads_num = 3 
images = [None] * threads_num
image_jobs = [None] * threads_num
threads = [None] * threads_num
checker_threads = [None] * threads_num
checker_results = [None] * threads_num

def add_image(bs_uuid, index):
    global images

    image_option = test_util.ImageOption()
    image_option.set_name('test_add_image_progress%s' % (index))
    image_option.set_format('qcow2')
    image_option.set_mediaType('RootVolumeTemplate')
    image_option.set_url(os.environ.get('imageUrl_net'))
    image_option.set_backup_storage_uuid_list([bs_uuid])
    image_option.set_timeout(600000)

    images[index] = zstack_image_header.ZstackTestImage()
    images[index].set_creation_option(image_option)

    image_jobs[index] = str(uuid.uuid4()).replace('-', '')
    test_util.test_logger(str(index) *10 + image_jobs[index])
    images[index].add_root_volume_template_apiid(image_jobs[index])
    test_obj_dict.add_image(images[index])

def check_add_image_progress(index):
    image_cond = res_ops.gen_query_conditions("status", '=', "Downloading")
    image_cond = res_ops.gen_query_conditions("name", '=', 'test_add_image_progress%s' % (index), image_cond)
    image = res_ops.query_resource_fields(res_ops.IMAGE, image_cond, \
                None, fields=['uuid'])
    if len(image) <= 0:
        test_util.test_fail("image is not in creating after 10 seconds")
        exit()
    if image[0].status == "Ready":
	test_util.test_logger("image has been added")
	exit()
    for i in range(0, 600):
        progresses = res_ops.get_progress(image_jobs[index])
        if len(progresses) <= 0:
            time.sleep(0.1)
            continue
        progress = progresses[0]
        if progress.content != None:
            break
        else:
            test_util.test_logger('task progress still not ready')
        time.sleep(0.1)

    if int(progress.content) < 0 or int(progress.content) > 100:
        test_util.test_fail("Progress of task should be between 0 and 100, while it actually is %s" % (progress.content))

    for i in range(0, 3600):
        time.sleep(1)
        test_util.test_logger(i)
        last_progress = progress
        progresses = res_ops.get_progress(image_jobs[index])
        if len(progresses) <= 0:
            break
        progress = progresses[0]
        test_util.test_logger(progress.content)
	if progress.content == None:
            break

        if int(progress.content) < int(last_progress.content):
            test_util.test_fail("Progress (%s) of task is smaller than last time (%s)" % (progress.content, last_progress.content))

    image_cond = res_ops.gen_query_conditions("uuid", '=', image[0].uuid)
    image_query2 = res_ops.query_resource_fields(res_ops.IMAGE, image_cond)
    time.sleep(1)
    if image_query2[0].status != "Ready":
        test_util.test_fail("Image should be ready when no progress anymore")
    checker_results[index] = 'pass'

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
        threads[i] = threading.Thread(target=add_image, args=(bss[0].uuid, i, ), name="add_image_"+str(i))
        threads[i].start()
    time.sleep(2)
    for i in range(0, threads_num):
        checker_threads[i] = threading.Thread(target=check_add_image_progress, args=(i, ), name="progress_image_"+str(i))
        # checker_threads[i].setDaemon(True)
        checker_threads[i].start()

    for i in range(0, threads_num):
	checker_threads[i].join()
        threads[i].join()
        images[i].check() 
        images[i].delete()

    for i in range(0, threads_num):
        if checker_results[i] == None:
            test_util.test_fail("Image checker thread %s fail" % (i))
    test_util.test_pass('Add image Progress Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)

