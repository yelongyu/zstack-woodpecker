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
import time
import threading

test_stub = test_lib.lib_get_test_stub()
#test_obj_dict is to track test resource. They will be cleanup if there will be any exception in testing.
test_obj_dict = test_state.TestStateDict()
origin_interval = None
bs_type = None
vm1 = None

def create_temp_image():
    global vm1
    image_creation_option = test_util.ImageOption()
    backup_storage_list = test_lib.lib_get_backup_storage_list_by_vm(vm1.vm)
    image_creation_option.set_backup_storage_uuid_list([backup_storage_list[0].uuid])
    image_creation_option.set_root_volume_uuid(vm1.vm.rootVolumeUuid)
    image_creation_option.set_name('test_create_image_template')
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

    test_util.test_dsc('Create test vm and check')
    vm1 = test_stub.create_vlan_vm()
    vm1.check()
    test_obj_dict.add_vm(vm1)
    vm1.stop()

    thread = threading.Thread(target=create_temp_image, args=())
    thread.start()
    time.sleep(5)
    image_cond = res_ops.gen_query_conditions("status", '=', "Downloading")
    image = res_ops.query_resource_fields(res_ops.IMAGE, image_cond, \
            None, fields=['uuid'])
    progress = res_ops.get_task_progress(image[0].uuid)
    if int(progress.progress) < 0 or int(progress.progress) > 100:
        test_util.test_fail("Progress of task should be between 0 and 100, while it actually is %s" % (progress.progress))
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

