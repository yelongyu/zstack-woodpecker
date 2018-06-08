'''

New Integration Test for export iso from image store, just check if exported image's suffix is 'iso'.

@author: Mirabel
'''
import time
import os

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.zstack_test.zstack_test_image as test_image
import zstackwoodpecker.operations.image_operations as img_ops

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    imagestore_backup_storage = test_lib.lib_get_image_store_backup_storage()
    if not imagestore_backup_storage:
        test_util.test_skip('Not find image store type backup storage.')

    img_option = test_util.ImageOption()
    img_option.set_name('iso')
    root_disk_uuid = test_lib.lib_get_disk_offering_by_name(os.environ.get('rootDiskOfferingName')).uuid                       
    bs_uuid = imagestore_backup_storage.uuid          
    img_option.set_backup_storage_uuid_list([bs_uuid])
    command = "command -v genisoimage"
    result = test_lib.lib_execute_ssh_cmd(os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'], 'root', 'password', command)
    if not result:
        command = "yum -y install genisoimage"
        test_lib.lib_execute_ssh_cmd(os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'], 'root', 'password', command)
    command = "genisoimage -o %s/apache-tomcat/webapps/zstack/static/zstack-repo/7/x86_64/os/test.iso /tmp/" % os.environ.get('zstackInstallPath')
    test_lib.lib_execute_ssh_cmd(os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'], 'root', 'password', command)
    img_option.set_url('http://%s:8080/zstack/static/zstack-repo/7/x86_64/os/test.iso' % (os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP']))
    image_inv = img_ops.add_iso_template(img_option)
    image = test_image.ZstackTestImage()
    image.set_image(image_inv)
    image.set_creation_option(img_option)

    test_obj_dict.add_image(image)
    image_url = image.export()
    image.delete_exported_image()
    test_lib.lib_robot_cleanup(test_obj_dict)
    if image_url.endswith('.iso'): 
        test_util.test_pass('Export ISO Image Test Success')
    else:
        test_util.test_fail('Export ISO Image Test Fail, exported ISO image ends with %s' % (image_url.split('.')[-1]))

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
