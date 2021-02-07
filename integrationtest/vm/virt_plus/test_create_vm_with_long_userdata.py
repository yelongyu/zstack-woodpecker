'''

New Integration test for testing create a vm with long userdate string.

@author: Glody
'''
import apibinding.inventory as inventory
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.zstack_test.zstack_test_image as test_image
import time
import os
import uuid

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
tmp_file = '/tmp/%s' % uuid.uuid1().get_hex()

def test():

    allow_ps_list = [inventory.LOCAL_STORAGE_TYPE]
    test_lib.skip_test_when_ps_type_not_in_list(allow_ps_list)

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

    vm = test_stub.create_vm(vm_name = 'userdata-vm',image_name = image_name,system_tags = ["userdata::%s" % os.environ.get('long_userdata_systemTags')])

    test_obj_dict.add_vm(vm)
    time.sleep(90)

    vm_ip = vm.get_vm().vmNics[0].ip
    ssh_cmd = 'ssh -i %s -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null test@%s' % (os.environ.get('sshkeyPriKey_file'), vm_ip)

    for i in range(5):
        cmd = '%s cat /tmp/helloworld_config' % ssh_cmd
        process_result = test_stub.execute_shell_in_process(cmd, tmp_file)
        if process_result == 0:
            break
        else:
            time.sleep(10)
    else:
        test_util.test_fail("fail to cat /tmp/helloworld_config")

    for i in range(5):
        cmd = '%s find /tmp/temp' % ssh_cmd
        process_result = test_stub.execute_shell_in_process(cmd, tmp_file)
        if process_result == 0:
            break
        else:
            time.sleep(10)
    else:
        test_util.test_fail("fail to find /tmp/temp")    

    vm.destroy()
    test_obj_dict.rm_vm(vm)
    image.delete()
    image.expunge()
    test_obj_dict.rm_image(image)
    test_util.test_pass('Create VM with long userdata string Success')

    #Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
