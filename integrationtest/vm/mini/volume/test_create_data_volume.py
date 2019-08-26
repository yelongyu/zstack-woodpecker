'''

Integration test for testing create thick/thick data volume on mini.

@author: zhaohao.chen
'''

import apibinding.inventory as inventory
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_volume as test_volume_header
import zstackwoodpecker.operations.volume_operations as vol_ops
import time
import os
import random

PROVISION = ["volumeProvisioningStrategy::ThinProvisioning","volumeProvisioningStrategy::ThickProvisioning"]
round_num = 10
volume = None

test_obj_dict = test_state.TestStateDict()
def test():
    global round_num
    global volume
    global test_obj_dict
    volume_creation_option = test_util.VolumeOption()
    ps_uuid = res_ops.query_resource(res_ops.PRIMARY_STORAGE)[0].uuid
    volume_creation_option.set_primary_storage_uuid(ps_uuid)
    #create thin/thick data volume with random disksize and random provision type
    for i in range(round_num):
        volume_name = "volume_%s" % i
        volume_creation_option.set_name(volume_name)
        max_size = (res_ops.query_resource(res_ops.PRIMARY_STORAGE)[0].availableCapacity - 1048576)/(2*512)
        disk_size = random.randint(2048, max_size) * 512
        volume_creation_option.set_diskSize(disk_size)
        volume_creation_option.set_system_tags([random.choice(PROVISION)])
        volume = test_volume_header.ZstackTestVolume()
        volume.set_volume(vol_ops.create_volume_from_diskSize(volume_creation_option))
        test_obj_dict.add_volume(volume)
        volume.check() 
        volume.delete()
        volume.expunge()
    test_util.test_pass("Mini Create Volume Test Success")
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)

def env_recover():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)

