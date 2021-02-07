# -*- coding: UTF-8 -*-
'''
New Test For datavolume bill spending check
@author Zhaohao
'''
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.billing_operations as bill_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm
import threading
import json
import random
import time
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
vm = None
billing_resource = 'datavolume'
offset_unit_dict=['sec','min','hou','day','week','month','year']
time_unit_dict=['s','m','h','d','w','mon']
resource_unit_dict={"M":1024 * float(1024), "G":1024**2 * float(1024), "T":1024**3 * float(1024)}
vm_max = 10
round_max = 10
round_sum = vm_max * round_max

#systemtags config
#cond = res_ops.gen_query_conditions('type', '=', 'ceph')
ps_uuid = res_ops.query_resource_fields(res_ops.CEPH_PRIMARY_STORAGE)[0].uuid
data_pool_name = 'test-pool-Data-1-' + ps_uuid
#price_systemtags_json = {"priceKeyName":"highSpeedDisk"}
price_systemtags_json = json.dumps({"priceUserConfig":{"priceKeyName":"highSpeedDisk"}})
price_system_tags = ["priceUserConfig::%s" % price_systemtags_json,]
#disk_offering_systemtags_json = {"allocate": {"primaryStorage": {"type": "ceph", "uuid": ps_uuid, "poolNames": [data_pool_name]}}, "priceUserConfig": {"volume": {"priceKeyName": "highSpeedDisk"}}, "displayAttribute": {"volume": {"云盘类型": "高速云盘"}}}
disk_offering_systemtags_json = json.dumps({"allocate": {"primaryStorage": {"type": "ceph", "uuid": ps_uuid, "poolNames": [data_pool_name]}}, "priceUserConfig": {"volume": {"priceKeyName": "highSpeedDisk"}}, "displayAttribute": {"volume": {"云盘类型": "高速云盘"}}})
disk_offering_system_tags = ["diskOfferingUserConfig::%s"  % disk_offering_systemtags_json,]

def test():
	success_round = 0
	for i in range(0,vm_max):
		test_util.test_logger("clear data in DataVolumeUsageVO and PriceVO")
		test_lib.resource_price_clear(billing_resource)
		test_util.test_logger("=====SENDING CHECK VM %s=====" % str(i+1))
		bill_datavolume = test_lib.DataVolumeBilling()
		time_unit = random.choice(time_unit_dict)
		price = str(random.randint(0,9999))
		resource_unit = random.choice(resource_unit_dict.keys())
		bill_datavolume.set_timeUnit(time_unit)
		bill_datavolume.set_price(price)
		bill_datavolume.set_resourceUnit(resource_unit)
                bill_datavolume.set_price_system_tags(price_system_tags)
		test_util.test_logger("create datavolume price\n price=%s, timeUnit=%s, resourceUnit=%s \n systemTags=%s" % (price, time_unit, resource_unit, price_system_tags))
		price = bill_datavolume.create_resource_type()
		if not price:
			test_util.test_fail("fail: create datavolume price")
		else:
			test_util.test_logger("success: create datavolume price %s" % price.uuid)
	
		test_util.test_logger("create vm instance")
		global vm
	        vm = test_lib.create_vm_billing("test_vmm", test_lib.set_vm_resource()[0], None,\
							test_lib.set_vm_resource()[1], test_lib.set_vm_resource()[2])
		
	        #vm = create_vm_billing("test_vmm", set_vm_resource()[0], None,\
		#					set_vm_resource()[1], set_vm_resource()[2])
		
		disk_offering_uuid = bill_datavolume.create_disk_offer(2147483648,"test_disk",disk_offering_system_tags).uuid #20G
		test_util.test_logger("create disk-offering \n size=%s, name=%s \n systemTags=%s" % (2147483648, "test_disk", disk_offering_system_tags))
		bill_datavolume.create_volume_and_attach_vmm(disk_offering_uuid,"test_volume",vm)
		test_util.test_logger("@@@@debug %s" %(bill_datavolume.disk.get_name()))
		dataVolumeSize = res_ops.query_resource(res_ops.DISK_OFFERING, \
						res_ops.gen_query_conditions('name', '=',\
				                        bill_datavolume.disk.get_name()))[0].diskSize / resource_unit_dict[resource_unit]
		test_util.test_logger("@@@@debug %s" %(dataVolumeSize))
	
		test_util.test_logger("====check datavolume spending====")
		for r in range(0,round_max):
			test_util.test_logger("===spending check round %s-%s===" % (str(i+1), str(r+1)))
			if test_lib.billing_check(bill_datavolume, billing_resource, random.choice(offset_unit_dict), random.randint(0,3), dataVolumeSize):
				success_round += 1
			else:
				test_util.test_fail("check datavolume billing spending finished\n success: %s/%s" % (success_round, round_sum))
	test_util.test_pass("check data volume billing finished\n success: %s/100" % success_round)

def error_cleanup():
	global vm
	if vm:
		vm.clean()

def env_recover():
	global vm
	if vm:
		vm.clean()
	resourcePrices = test_lib.query_resource_price()
	if resourcePrices:
		for resourceprice in resourcePrices:
			test_lib.delete_price(resourceprice.uuid)
