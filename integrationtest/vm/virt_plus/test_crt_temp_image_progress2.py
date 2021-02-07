'''

Test Progress of Create Image Template from Root Volume

@author: quarkonics
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.zstack_test.zstack_test_image as test_image
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm
import zstackwoodpecker.operations.config_operations as conf_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import os
import time
import threading
import tempfile
import uuid
_config_ = {
        'timeout' : 1800,
        'noparallel' : False
        }


test_stub = test_lib.lib_get_test_stub()
#test_obj_dict is to track test resource. They will be cleanup if there will be any exception in testing.
test_obj_dict = test_state.TestStateDict()
origin_interval = None
bs_type = None
threads_num = 1
vms = [None] * threads_num
images = [None] * threads_num
image_jobs = [None] * threads_num
threads = [None] * threads_num
checker_threads = [None] * threads_num
checker_results = [None] * threads_num

def create_temp_image(index):
    global vms
    global images
    image_creation_option = test_util.ImageOption()
    backup_storage_list = test_lib.lib_get_backup_storage_list_by_vm(vms[index].vm)
    image_creation_option.set_backup_storage_uuid_list([backup_storage_list[0].uuid])
    image_creation_option.set_root_volume_uuid(vms[index].vm.rootVolumeUuid)
    image_creation_option.set_name('test_create_image_template_progress%s' % (index))
    bs_type = backup_storage_list[0].type
    if bs_type == 'Ceph':
        origin_interval = conf_ops.change_global_config('ceph', 'imageCache.cleanup.interval', '1')

    images[index] = test_image.ZstackTestImage()
    images[index].set_creation_option(image_creation_option)
    image_jobs[index] = str(uuid.uuid4()).replace('-', '')
    images[index].create(image_jobs[index])
    test_obj_dict.add_image(images[index])

def check_create_temp_image_progress(index):
    global images
    for i in range(0, 600):
        time.sleep(0.1)
        image_cond = res_ops.gen_query_conditions("status", '=', "Creating")
        image_cond = res_ops.gen_query_conditions("name", '=', "test_create_image_template_progress%s" % (index), image_cond)
        image_query = res_ops.query_resource_fields(res_ops.IMAGE, image_cond, \
                None, fields=['uuid'])
        if len(image_query) > 0:
            break

    if len(image_query) <= 0:
        test_util.test_fail("image is not in creating after 10 seconds")

    for i in range(0, 600):
        progress = res_ops.get_task_progress(image_jobs[index]).inventories[0]
        if progress.content != None:
            break
        else:
            test_util.test_logger('task progress still not ready')
        time.sleep(0.1)
    if int(progress.content) < 0 or int(progress.content) > 100:
        test_util.test_fail("Progress of task should be between 0 and 100, while it actually is %s" % (progress.content))

    for i in range(0, 3600):
        last_progress = progress
        progress = res_ops.get_task_progress(image_jobs[index]).inventories[0]
        if progress.content == None:
            break
        if int(progress.content) < int(last_progress.content):
            test_util.test_fail("Progress (%s) of task is smaller than last time (%s)" % (progress.content, last_progress.content))
    image_cond = res_ops.gen_query_conditions("uuid", '=', image_query[0].uuid)
    image_query2 = res_ops.query_resource_fields(res_ops.IMAGE, image_cond, \
                   None, fields=['status'])
    if image_query2[0].status != "Ready":
        test_util.test_fail("Image should be ready when no progress anymore")

    checker_results[index] = 'pass'

def test():
    global vms
    global images
    global threads
    global checker_threads
    global origin_interval
    global bs_type

    test_util.test_dsc('Create test vm and check')
    script_file = tempfile.NamedTemporaryFile(delete=False)
    script_file.write('dd if=/dev/zero of=/home/dd bs=1M count=100')
    script_file.close()

    for i in range(0, threads_num):
        vms[i] = test_stub.create_vlan_vm()
        vms[i].check()
        backup_storage_list = test_lib.lib_get_backup_storage_list_by_vm(vms[i].vm)
	if backup_storage_list[0].type != 'ImageStoreBackupStorage':
            test_util.test_skip("Requires imagestore BS to test, skip testing")
        if not test_lib.lib_execute_shell_script_in_vm(vms[i].get_vm(), script_file.name):
            test_util.test_fail("fail to create data in [vm:] %s" % (vms[i].get_vm().uuid))
        test_obj_dict.add_vm(vms[i])
        vms[i].stop()
        
    os.unlink(script_file.name)

    for i in range(0, threads_num):
        threads[i] = threading.Thread(target=create_temp_image, args=(i, ))
        threads[i].start()

    for i in range(0, threads_num):
        checker_threads[i] = threading.Thread(target=check_create_temp_image_progress, args=(i, ))
        checker_threads[i].start()

    for i in range(0, threads_num):
        checker_threads[i].join()
        threads[i].join()
        images[i].check()
        vms[i].destroy()
        images[i].delete()

    for i in range(0, threads_num):
        if checker_results[i] == None:
            test_util.test_fail("Image checker thread %s fail" % (i))

    if bs_type == 'Ceph':
        time.sleep(60)

    if bs_type == 'Ceph':
        conf_ops.change_global_config('ceph', 'imageCache.cleanup.interval', origin_interval)

    test_util.test_pass('Create Image Template Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    global origin_interval
    global bs_type
    if bs_type == 'Ceph':
        conf_ops.change_global_config('ceph', 'imageCache.cleanup.interval', origin_interval)

    test_lib.lib_error_cleanup(test_obj_dict)

