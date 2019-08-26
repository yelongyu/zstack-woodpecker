'''

New Integration Test for KVM VM sshkey injection.

@author: quarkonics
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import zstackwoodpecker.operations.host_operations as host_ops
import time
import os
import tempfile
import uuid
import apibinding.api_actions as api_actions
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.zstack_test.zstack_test_image as test_image

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
tmp_file = '/tmp/%s' % uuid.uuid1().get_hex()

def test():
    instance_offering_name = os.environ.get('instanceOfferingName_m')
    instance_offering_uuid = test_lib.lib_get_instance_offering_by_name(instance_offering_name).uuid
#add a image which can use root/password login
    img_option = test_util.ImageOption()
    image_name = 'test'
    image_url = 'http://192.168.200.100/mirror/diskimages/CentOS7.4-Cloudinit-QGA-8G.qcow2'
    img_option.set_name(image_name)
    bs_uuid = res_ops.query_resource_fields(res_ops.BACKUP_STORAGE, [], None)[0].uuid
    img_option.set_backup_storage_uuid_list([bs_uuid])
    img_option.set_format('qcow2')
    img_option.set_url(image_url)
    image_inv = img_ops.add_root_volume_template(img_option)
    image = test_image.ZstackTestImage()
    image.set_image(image_inv)
    image.set_creation_option(img_option)
    test_obj_dict.add_image(image)
    

    vm = test_stub.create_vm(image_name = image_name, instance_offering_uuid = instance_offering_uuid)
    test_obj_dict.add_vm(vm)
    time.sleep(60)
    vm_ip = vm.get_vm().vmNics[0].ip
#delete existing instances 
    cmd = 'rm -rf /var/lib/cloud/instances'
    test_lib.lib_execute_ssh_cmd(vm_ip, 'root', 'password', cmd)    
    time.sleep(10)
    test_lib.lib_add_vm_sshkey(vm.get_vm().uuid, os.environ.get('sshkeyPubKey'))
    host = test_lib.lib_get_vm_host(vm.get_vm())
    host_uuid = host.uuid
    host_ops.reconnect_host(host_uuid)
    vm.reboot()
    test_lib.lib_wait_target_up(vm_ip, '22', 240)
    time.sleep(10)
    for i in range(5):
        ssh_cmd = 'timeout 5 ssh -i %s -oPasswordAuthentication=no -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s echo pass' % (os.environ.get('sshkeyPriKey_file'), vm_ip)
        process_result = test_stub.execute_shell_in_process(ssh_cmd, tmp_file)
        if process_result == 0:
            break
        else:
            time.sleep(10)
    else:
        test_util.test_fail("fail to use ssh key connect to VM")

    vm.destroy()
    test_util.test_pass('Create VM Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
    os.system('rm -f %s' % tmp_file)
