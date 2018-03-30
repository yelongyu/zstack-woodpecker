'''

New Integration Test for resizing unattached data volume.

@author: czhou25
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import time
import os

vm = None
test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    global test_obj_dict
    volume_creation_option = test_util.VolumeOption()
    ps_uuid = res_ops.query_resource(res_ops.PRIMARY_STORAGE, [])[0].uuid
    test_util.test_dsc('Create volume and check')
    disk_offering = test_lib.lib_get_disk_offering_by_name(os.environ.get('smallDiskOfferingName'))
    volume_creation_option.set_disk_offering_uuid(disk_offering.uuid)
    volume_creation_option.set_primary_storage_uuid(ps_uuid)
    if res_ops.query_resource(res_ops.PRIMARY_STORAGE, [])[0].type == "LocalStorage":
        host = test_lib.lib_find_random_host()
        volume_creation_option.set_system_tags(["localStorage::hostUuid::%s" % host.uuid])
    volume = test_stub.create_volume(volume_creation_option)
    test_obj_dict.add_volume(volume)
    volume.check()
    volume_uuid = volume.volume.uuid
    vol_size = volume.volume.size

    set_size = 1024*1024*1024*5
    vol_ops.resize_data_volume(volume_uuid, set_size)
    cond = res_ops.gen_query_conditions('type', '=', "Data")
    cond = res_ops.gen_query_conditions('status', '=', "Ready", cond)
    vol_size_after  = res_ops.query_resource(res_ops.VOLUME, cond)[0].size
    if set_size != vol_size_after:
        test_util.test_fail('Resize Data Volume failed, size = %s' % vol_size_after)
    test_lib.lib_error_cleanup(test_obj_dict)
    test_util.test_pass('Resize Data Volume Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
