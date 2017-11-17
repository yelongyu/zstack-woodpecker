'''

New Integration Test for add image from other imageStore.


@author: Glody 
'''

import os
import time
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.zstack_test.zstack_test_image as zstack_image_header

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    bs = res_ops.query_resource(res_ops.BACKUP_STORAGE)[0]
    if bs.type == "Ceph":
        test_util.test_skip('bs: %s is ceph backup storage. Will skip test.' % bs.uuid)

    ca_str = "-----BEGIN CERTIFICATE-----\nMIIDbzCCAlegAwIBAgIJAMv+fpA4ettyMA0GCSqGSIb3DQEBCwUAME4xCzAJBgNV\nBAYTAkNOMREwDwYDVQQIDAhTaGFuZ2hhaTERMA8GA1UEBwwIU2hhbmdoYWkxGTAX\nBgNVBAMMEHN0b3JlLnpzdGFjay5vcmcwHhcNMTcxMTAzMDgzOTU2WhcNMjcxMTAx\nMDgzOTU2WjBOMQswCQYDVQQGEwJDTjERMA8GA1UECAwIU2hhbmdoYWkxETAPBgNV\nBAcMCFNoYW5naGFpMRkwFwYDVQQDDBBzdG9yZS56c3RhY2sub3JnMIIBIjANBgkq\nhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAv9zyqMT3qjU9P/0xEit9nZo7i7KM/OZ1\ncznCHMu4pKv94499hMBRaczLzy5AbJfyu7it0saHM8yo5OloQ6MrUo6KlINa14n1\nLBCxnmk5yC+tERdFhj2Q90yj69VkI4vqpNB7Q7fICtKBNssGtC2AHZmEJSn3CBmV\nve4v45jZ7jcKMNEqLZuiAbAgqR2hk/haNOLLVJLCRLSvReOUYGwood3c0UPzRpnW\ni4W2fr4AGRHEhdXW+N6qKyXt74fpCKjvtMwA4uMWb3VOLP0ieNYo+Nj4j2GHjhXK\ngf0rwkL2z6YQe+B+4nSopAupeUqnn6av/Bm/Km/rCJKCyIdhIPqXEwIDAQABo1Aw\nTjAdBgNVHQ4EFgQUxU8XEYPqJA5QO1JcCUj7Hyfbw68wHwYDVR0jBBgwFoAUxU8X\nEYPqJA5QO1JcCUj7Hyfbw68wDAYDVR0TBAUwAwEB/zANBgkqhkiG9w0BAQsFAAOC\nAQEAnw06nDAcsZMdQNTYvftcF/QNqnZ/fqkmT9kN2bSpn/x87u8v0/2NeYaTO3+C\n8cimW59vk0hMw0dMiyiPZy3UOvh/D/DxggeIK8N53A9O5gz4uWVLKrzALW5UWVxI\nwUiBxfq07brkm80x01xnpP/V6jZg1ueexDfPZzmMRX1F+iTkJO6S9HM6LIZ+4T/D\nmfPmcw8dsQfkB36oyxPU6kg8meSpKD1esL2ys2oCdARbqwiCmN/kHyxvWo7zVPAD\nxcbANgJHA21KtlkxOKIi2X9N1Oc/uKMISihOcrDRxUI0aZbBGOLzRuIxqx/dO4AY\n/iusohqewQYsHNMtvlEOkzIbIg==\n-----END CERTIFICATE-----"
    zstore_url = "zstore://172.20.1.43/75004f075f454fdd8a2e8c0c684f9bbd/aa25fab627728e78d4f568aad456f0bb0bf556b7"

    image_name = 'test-image-%s' % time.time()
    image_option = test_util.ImageOption()
    image_option.set_name(image_name)
    image_option.set_description('test image from remote imageStore')
    image_option.set_url(zstore_url)
    image_option.set_backup_storage_uuid_list([bs.uuid])
    image_option.set_format('qcow2')
    image_option.set_system_tags("image::cert::%s" %ca_str)
    image_option.set_mediaType('RootVolumeTemplate')
    image_inv = img_ops.add_root_volume_template(image_option)
    time.sleep(10)
    image = zstack_image_header.ZstackTestImage()
    image.set_creation_option(image_option)
    image.set_image(image_inv)
    test_obj_dict.add_image(image)
    image.check()

    vm = test_stub.create_vm(image_name = image_name)
    vm.destroy()

    image.delete()
    test_util.test_pass('Test adding image from remote imageStorage pass.')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
