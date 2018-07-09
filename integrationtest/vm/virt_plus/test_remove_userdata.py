'''

New Integration test for testing delete user date.

@author: ChenyuanXu
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.zstack_test.zstack_test_image as test_image
import zstackwoodpecker.operations.tag_operations as tag_ops
import time
import uuid
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    img_option = test_util.ImageOption()
    image_name = 'userdata-image'
    image_url = os.environ.get('userdataImageUrl')
    img_option.set_name(image_name)
    bs_uuid = res_ops.query_resource_fields(res_ops.BACKUP_STORAGE, [], None)[0].uuid
    img_option.set_backup_storage_uuid_list([bs_uuid])
    img_option.set_format('raw')
    img_option.set_url(image_url)
    image_inv = img_ops.add_root_volume_template(img_option)
    image = test_image.ZstackTestImage()
    image.set_image(image_inv)
    image.set_creation_option(img_option)
    test_obj_dict.add_image(image)

    vm = test_stub.create_vm(vm_name = 'userdata-vm',image_name = image_name,system_tags = ["userdata::%s" % os.environ.get('userdata_systemTags')])

    test_obj_dict.add_vm(vm)
    time.sleep(60)

    cond = res_ops.gen_query_conditions('resourceUuid', '=', vm.vm.uuid)
    system_tag = res_ops.query_resource(res_ops.SYSTEM_TAG, cond)
    if system_tag != []:
        test_util.test_logger ('Success get system tags.')
    else:
        test_util.test_fail('Failed to get system tags.')

    sys_tags = res_ops.query_resource(res_ops.SYSTEM_TAG, cond)
    system_tag_uuid = [tag.uuid for tag in sys_tags if 'userdata' in tag.tag][0]
#     system_tag_uuid = res_ops.query_resource(res_ops.SYSTEM_TAG, cond)[0].uuid
    tag_ops.delete_tag(system_tag_uuid)
#     system_tag = res_ops.query_resource(res_ops.SYSTEM_TAG, cond)
    system_tag_after = res_ops.query_resource(res_ops.SYSTEM_TAG, cond)
    system_tag = [tag for tag in system_tag_after if 'userdata' in tag.tag]
    if system_tag == []:
        test_util.test_logger ('Success delete system tags.')
    else:
        test_util.test_fail('Failed to delete system tags.')


    vm.destroy()
    test_obj_dict.rm_vm(vm)
    image.delete()
    image.expunge()
    test_obj_dict.rm_image(image)
    test_util.test_pass('Delete userdata  Success')

    #Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
