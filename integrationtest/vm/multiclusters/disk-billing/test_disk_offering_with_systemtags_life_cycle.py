# -*- coding: UTF-8 -*-
'''
New Test For Disk Offering with SystemTags Life Cycle
@author Zhaohao
'''
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.billing_operations as bill_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.operations.net_operations as net_ops
import threading
import random
import json
import time
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
vm = None

#create disk offering with systemTags
ps_uuid = res_ops.query_resource_fields(res_ops.CEPH_PRIMARY_STORAGE)[0].uuid
data_pool_name = 'test-pool-Data-1-' + ps_uuid
disk_offering_opt = test_util.DiskOfferingOption()
disk_offering_opt.set_diskSize(1073741824)
disk_offering_opt.set_name('systemTags-test')
disk_offering_systemtags_json = json.dumps({"allocate": {"primaryStorage": {"type": "ceph", "uuid": ps_uuid, "poolNames": [data_pool_name]}}, "priceUserConfig": {"volume": {"priceKeyName": "highSpeedDisk"}}, "displayAttribute": {"volume": {"云盘类型": "高速云盘"}}})
disk_offering_system_tags = ["diskOfferingUserConfig::%s"  % disk_offering_systemtags_json,]
disk_offering_opt.set_system_tags(disk_offering_system_tags)
#disk_offering_uuid = vol_ops.create_disk_offering(disk_offering_opt).uuid

def test():
        #1.test: create disk offering
	test_util.test_logger("1.create disk offering")        
	disk_offering_uuid = vol_ops.create_volume_offering(disk_offering_opt).uuid

	#2.test: query disk offering
	test_util.test_logger("2.query disk offering")
	cond = res_ops.gen_query_conditions('uuid', '=', disk_offering_uuid)
	offering_query_result =  res_ops.query_resource_fields(res_ops.DISK_OFFERING, cond)
	if not offering_query_result:
		test_util.test_fail("fail: query disk offering %s" % disk_offering_uuid)

        #3.test: delete disk offering
        test_util.test_logger("3.delete disk offering")
	vol_ops.delete_disk_offering(disk_offering_uuid)
	#check, because delete API always return 'success'
	cond = res_ops.gen_query_conditions('uuid', '=', disk_offering_uuid)
        offering_query_result =  res_ops.query_resource_fields(res_ops.DISK_OFFERING, cond)
	if offering_query_result:
		test_util.test_fail("fail: delete disk offering %s" % disk_offering_uuid)
	test_util.test_pass("test: disk offering with systemTags life cycle pass")

def error_cleanup():
	return

def env_recover():
	return
