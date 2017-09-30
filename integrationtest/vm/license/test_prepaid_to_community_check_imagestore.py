'''

New Integration Test for License.

@author: ye
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.license_operations as lic_ops
import zstackwoodpecker.operations.zone_operations as zone_ops
import zstackwoodpecker.operations.backupstorage_operations as bs_ops
import zstackwoodpecker.operations.image_operations as img_ops
import time
import datetime
import os
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_image as zstack_image_header

test_stub = test_lib.lib_get_test_stub()

def test():

    global bs_username, bs_hostname, bs_password, bs_name, bs_username, bs_url, bs_sshport
    global new_image    

    file_path = test_stub.gen_license('woodpecker', 'woodpecker@zstack.io', '1', 'Prepaid', '1', '')
    test_stub.load_license(file_path)
    issued_date = test_stub.get_license_info().issuedDate
    expired_date = test_stub.license_date_cal(issued_date, 86400 * 1)
    test_stub.check_license("woodpecker@zstack.io", 1, None, False, 'Paid', issued_date=issued_date, expired_date=expired_date)

    test_util.test_logger('create zone and add the bs of the imagestore')
    node_uuid = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].uuid
    test_stub.create_zone()
    zone_uuid = res_ops.query_resource(res_ops.ZONE)[0].uuid

    bs_name = 'BS1'
    bs_hostname = os.environ.get('node1Ip')
    bs_username = os.environ.get('nodeUserName')
    bs_password = os.environ.get('nodePassword')
    bs_url = '/zstack_bs'
    bs_sshport = '22'
    test_stub.create_image_store_backup_storage(bs_name, bs_hostname, bs_username, bs_password, bs_url, bs_sshport)
    bs_uuid = res_ops.query_resource(res_ops.BACKUP_STORAGE)[0].uuid

    test_stub.reload_default_license()
    test_util.test_logger('Check default community license')
    #test_stub.check_license(None, None, 2147483647, False, 'Community')

    bs_ops.reconnect_backup_storage(bs_uuid)
    test_util.test_logger('reconnect the bs')

    test_util.test_logger('add image')
    bs_cond = res_ops.gen_query_conditions("status", '=', "Connected")
    bss = res_ops.query_resource_fields(res_ops.BACKUP_STORAGE, bs_cond, \
            None)
    if not bss:
        test_util.test_skip("not find available backup storage. Skip test")

    image_option = test_util.ImageOption()
    image_option.set_format('qcow2')
    image_option.set_name('test_file_url_image')
    image_option.set_system_tags('qemuga')
    image_option.set_mediaType('RootVolumeTemplate')
    image_option.set_url("file:///etc/issue")
    image_option.set_backup_storage_uuid_list([bss[0].uuid])
    image_option.set_timeout(600)

    new_image = zstack_image_header.ZstackTestImage()
    new_image.set_creation_option(image_option)

    new_image.add_root_volume_template()
    #new_image.delete()


    test_util.test_pass('Check License Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
