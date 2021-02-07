'''

@author: Pengtao.Zhang
'''

import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_util as test_util
from zstackwoodpecker.operations import net_operations as net_ops
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.zstack_test.zstack_test_image as test_image
import zstackwoodpecker.operations.resource_operations as res_ops
import zstacklib.utils.ssh as ssh
import time
import os


test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()


def test():

    img_option = test_util.ImageOption()
    ipv6_image_url = os.environ.get('ipv6ImageUrl')
    image_name = os.environ.get('ipv6ImageName')
    img_option.set_name(image_name)
    bs_uuid = res_ops.query_resource_fields(res_ops.BACKUP_STORAGE, [], None)[0].uuid
    img_option.set_backup_storage_uuid_list([bs_uuid])
    img_option.set_format('qcow2')
    img_option.set_url(ipv6_image_url)
    image_inv = img_ops.add_root_volume_template(img_option)
    image = test_image.ZstackTestImage()
    image.set_image(image_inv)
    image.set_creation_option(img_option)
    test_obj_dict.add_image(image)
    vm1 = test_stub.create_vm(l3_name = "%s,%s" %(os.environ.get('l3PublicNetworkName1'), os.environ.get('l3PublicNetworkName')), vm_name = 'IPv6 2 stack test ipv4 and ipv6', image_name = image_name)
    vm2 = test_stub.create_vm(l3_name = os.environ.get('l3PublicNetworkName1'), vm_name = 'IPv6 2 stack test ipv6', image_name = image_name)
    time.sleep(90) #waiting for vm bootup
    vm1_nic1 = vm1.get_vm().vmNics[0].ip
    vm1_nic2 = vm1.get_vm().vmNics[1].ip
    vm2_nic1 = vm2.get_vm().vmNics[0].ip
    for ip in (vm1_nic1, vm1_nic2):
        if "." in ip:
            ipv4 = ip
    print "vm1_nic1 : %s, vm1_nic2: %s, vm2_nic1 :%s, ipv4 :%s." %(vm1_nic1, vm1_nic2, vm2_nic1,ipv4)
    cmd = "ping6 -c 4 %s" %(vm2_nic1)
    (retcode, output, erroutput) = ssh.execute(cmd, ipv4, "root", "password", True, 22)
    print "retcode is: %s; output is : %s.; erroutput is: %s" %(retcode, output , erroutput)
    if retcode != 0:
        test_util.test_fail('Test Create IPv6 VM Failed.')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
