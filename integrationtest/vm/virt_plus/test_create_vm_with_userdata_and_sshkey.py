'''

New Integration test for testing create a vm with both user data and ssh-key.

@author: Pengtao.Zhang
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.zstack_test.zstack_test_image as test_image
import zstackwoodpecker.header.vm as vm_header
import time
import os
import uuid

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
tmp_file = '/tmp/%s' % uuid.uuid1().get_hex()

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
    instance_offering_name = os.environ.get('instanceOfferingName_m')
    instance_offering_uuid = test_lib.lib_get_instance_offering_by_name(instance_offering_name).uuid

    vm_1 = test_stub.create_vm(image_name = os.environ.get('sshkeyImageName'),instance_offering_uuid = instance_offering_uuid)
    test_obj_dict.add_vm(vm_1)
    time.sleep(90)
    vm_1_ip = vm_1.get_vm().vmNics[0].ip

    vm_2 = test_stub.create_vm(vm_name = 'userdata-and-sshkey-vm',image_name = image_name,system_tags = ["userdata::%s" % os.environ.get('userdata_systemTags'),"%s::%s" % (vm_header.SSHKEY, os.environ.get('sshkeyPubKey'))], instance_offering_uuid = instance_offering_uuid)
    test_obj_dict.add_vm(vm_2)
    time.sleep(90)

    vm_2_ip = vm_2.get_vm().vmNics[0].ip

    for i in range(5):
        ssh_cmd = 'timeout 5 ssh -i %s -oPasswordAuthentication=no -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s echo pass' % (os.environ.get('sshkeyPriKey_file'), vm_2_ip)
        process_result = test_stub.execute_shell_in_process(ssh_cmd, tmp_file)
        if process_result == 0:
            break
        else:
            time.sleep(10)
    else:
        test_util.test_fail("fail to use ssh key connect to VM")

    ssh_cmd = 'ssh -i %s -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null test@%s' % (os.environ.get('sshkeyPriKey_file'), vm_2_ip)
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

    vm_1.destroy()
    test_obj_dict.rm_vm(vm_1)
    vm_2.destroy()
    test_obj_dict.rm_vm(vm_2)
    image.delete()
    image.expunge()
    test_obj_dict.rm_image(image)
    test_util.test_pass('Create VM with userdata  Success')

    #Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
    os.system('rm -f %s' % tmp_file)
