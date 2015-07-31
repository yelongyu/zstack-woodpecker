'''

New Integration Test for testing deleting image, before delete VM

@author: Youyk
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.header.vm as vm_header
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.export_operations as exp_ops
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.zstack_test.zstack_test_image as test_image_header
import time
import os

_config_ = {
        'timeout' : 500,
        'noparallel' : True
        }

test_obj_dict = test_state.TestStateDict()
image_obj = test_image_header.ZstackTestImage()

def test():
    global image_obj
    curr_deploy_conf = exp_ops.export_zstack_deployment_config(test_lib.deploy_config)

    vm_creation_option = test_util.VmOption()
    image_name = os.environ.get('imageName_net')
    image_inv = test_lib.lib_get_image_by_name(image_name)
    image_uuid = image_inv.uuid

    image_crt_opt = test_util.ImageOption()
    image_crt_opt.set_name(image_inv.name)
    image_crt_opt.set_url(image_inv.url)
    image_crt_opt.set_format(image_inv.format)
    image_crt_opt.set_system(image_inv.system)
    image_crt_opt.set_mediaType(image_inv.mediaType)
    image_crt_opt.set_guest_os_type(image_inv.type)
    bss = image_inv.backupStorageRefs
    bss_uuids = []
    for bs in bss:
        bss_uuids.append(bs.backupStorageUuid)

    image_crt_opt.set_backup_storage_uuid_list(bss_uuids)
    image_obj.set_creation_option(image_crt_opt)

    conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
    instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_name('multizones_basic_vm')
    vm1 = test_lib.lib_create_vm(vm_creation_option)
    test_obj_dict.add_vm(vm1)

    test_util.test_dsc('delete image')
    img_ops.delete_image(image_uuid)
    #in bug, when destroy vm after delete related image, destroy vm will fail
    test_util.test_dsc('destroy vm')
    vm1.destroy()
    test_obj_dict.rm_vm(vm1)
    test_util.test_dsc('add image back')
    image_obj.add_root_volume_template()
    
    test_lib.lib_robot_cleanup(test_obj_dict)
    test_util.test_pass('Delete Image Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global image_obj
    test_lib.lib_error_cleanup(test_obj_dict)
    try:
        image_obj.add_root_volume_template()
    except Exception as e:
        test_util.test_warn('meet exception when try to recover image template')
        raise e
