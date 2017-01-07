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

test_stub = test_lib.lib_get_test_stub()
#test_obj_dict is to track test resource. They will be cleanup if there will be any exception in testing.
test_obj_dict = test_state.TestStateDict()
origin_interval = None
bs_type = None
vm1 = None
image = None

def create_temp_image():
    global vm1
    global image
    image_creation_option = test_util.ImageOption()
    backup_storage_list = test_lib.lib_get_backup_storage_list_by_vm(vm1.vm)
    image_creation_option.set_backup_storage_uuid_list([backup_storage_list[0].uuid])
    image_creation_option.set_root_volume_uuid(vm1.vm.rootVolumeUuid)
    image_creation_option.set_name('test_create_image_template_progress')
    bs_type = backup_storage_list[0].type
    if bs_type == 'Ceph':
        origin_interval = conf_ops.change_global_config('ceph', 'imageCache.cleanup.interval', '1')

    image = test_image.ZstackTestImage()
    image.set_creation_option(image_creation_option)
    image.create()
    test_obj_dict.add_image(image)


def test():
    global vm1
    global origin_interval
    global bs_type
    global image

    test_util.test_dsc('Create test vm and check')
    vm1 = test_stub.create_vlan_vm()
    vm1.check()
    script_file = tempfile.NamedTemporaryFile(delete=False)
    script_file.write('dd if=/dev/zero of=/home/dd bs=1M count=300')
    script_file.close()

    if not test_lib.lib_execute_shell_script_in_vm(vm1.get_vm(), script_file.name):
        test_util.test_fail("fail to create data in [vm:] %s" % (vm1.get_vm().uuid))
    os.unlink(script_file.name)
    test_obj_dict.add_vm(vm1)
    vm1.stop()

    thread = threading.Thread(target=create_temp_image, args=())
    thread.start()
    for i in range(0, 100):
        time.sleep(0.1)
        image_cond = res_ops.gen_query_conditions("status", '=', "Creating")
        image_cond = res_ops.gen_query_conditions("name", '=', "test_create_image_template_progress", image_cond)
        image_query = res_ops.query_resource_fields(res_ops.IMAGE, image_cond, \
                None, fields=['uuid'])
        if len(image_query) > 0:
            break

    if len(image_query) <= 0:
        test_util.test_fail("image is not in creating after 10 seconds")

    for i in range(0, 100):
        try:
            progress = res_ops.get_task_progress(image_query[0].uuid)
            break
        except:
            test_util.test_logger('task progress still not ready')
        time.sleep(0.1)
    if int(progress.progress) < 0 or int(progress.progress) > 100:
        test_util.test_fail("Progress of task should be between 0 and 100, while it actually is %s" % (progress.progress))

    for i in range(0, 3600):
        try:
            last_progress = progress
            progress = res_ops.get_task_progress(image_query[0].uuid)
            if progress.progress < last_progress.progress:
                test_util.test_fail("Progress of task is smaller than last time")
        except:
            break
    image_cond = res_ops.gen_query_conditions("uuid", '=', image_query[0].uuid)
    image_query2 = res_ops.query_resource_fields(res_ops.IMAGE, image_cond, \
                   None, fields=['status'])
    if image_query2[0].status != "Ready":
        test_util.test_fail("Image should be ready when no progress anymore")

    thread.join()
    image.check()

    vm1.destroy()
    image.delete()
    if bs_type == 'Ceph':
        time.sleep(60)
    image.check()

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

