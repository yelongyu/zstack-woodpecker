# -*- coding: UTF-8 -*-
'''
New Test For Instance Offering with SystemTags Life Cycle
@author Zhaohao
'''
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.billing_operations as bill_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.net_operations as net_ops
import threading
import random
import json
import time
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
vm = None

#create instance offering with systemTags
ps_uuid = res_ops.query_resource_fields(res_ops.CEPH_PRIMARY_STORAGE)[0].uuid
root_pool_name = 'test-pool-Root-1-' + ps_uuid
instance_offering_opt = test_util.InstanceOfferingOption()
instance_offering_opt.set_cpuNum(2)
instance_offering_opt.set_memorySize(1073741824)
instance_offering_opt.set_name('systemTags-test')
instance_offering_systemtags_json = json.dumps({"allocate": {"primaryStorage": {"type": "ceph", "uuid": ps_uuid, "poolNames": [root_pool_name]}}, "priceUserConfig": {"rootVolume": {"priceKeyName": "highSpeedDisk"}}, "displayAttribute": {"rootVolume": {"云盘类型": "普通云盘"}}})
instance_offering_opt.set_system_tags(["instanceOfferingUserConfig::%s" % instance_offering_systemtags_json,])
instance_offering_uuid = vm_ops.create_instance_offering(instance_offering_opt).uuid

def test():
        #1.test: create instance offering
	test_util.test_logger("1.create instance offering")        
	instance_offering_uuid = vm_ops.create_instance_offering(instance_offering_opt).uuid

	#2.test: query instance offering
	test_util.test_logger("2.query instance offering")
	cond = res_ops.gen_query_conditions('uuid', '=', instance_offering_uuid)
	offering_query_result =  res_ops.query_resource_fields(res_ops.INSTANCE_OFFERING, cond)
	if not offering_query_result:
		test_util.test_fail("fail: query instance offering %s" % instance_offering_uuid)

        #3.test: delete instance offering
        test_util.test_logger("3.delete instacne offering")
	vm_ops.delete_instance_offering(instance_offering_uuid)
	#check, because delete API always return 'success'
	cond = res_ops.gen_query_conditions('uuid', '=', instance_offering_uuid)
        offering_query_result =  res_ops.query_resource_fields(res_ops.INSTANCE_OFFERING, cond)
	if offering_query_result:
		test_util.test_fail("fail: delete instance offering %s" % instance_offering_uuid)
	test_util.test_pass("test: instance offering with systemTags life cycle pass")

def error_cleanup():
	return

def env_recover():
	return
