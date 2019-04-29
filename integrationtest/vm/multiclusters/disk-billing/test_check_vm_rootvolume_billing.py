# -*- coding: UTF-8 -*-
'''
New Test For rootvolume bill spending check
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
import time
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
vm = None
billing_resource = 'rootvolume'
offset_unit_dict=['sec','min','hou','day','week','month','year']
time_unit_dict=['s','m','h','d','w','mon']
resource_unit_dict={"M":1024 * float(1024), "G":1024**2 * float(1024), "T":1024**3 * float(1024)}
vm_max = 10
round_max = 10
round_sum = vm_max * round_max

#create instance_offering with systemtags
ps_uuid = res_ops.query_resource_fields(res_ops.CEPH_PRIMARY_STORAGE)[0].uuid
root_pool_name = 'test-pool-Root-1-' + ps_uuid
price_systemtags_json = {"priceUserConfig":{"priceKeyName":"highSpeedDisk"}}
price_system_tags = ['priceUserConfig::%s' % price_systemtags_json,]
instance_offering_opt = test_util.InstanceOfferingOption()
instance_offering_opt.set_cpuNum(2)
instance_offering_opt.set_memorySize(1073741824)
instance_offering_opt.set_name('high-speed-billing-test')
instance_offering_systemtags_json = {"allocate": {"primaryStorage": {"type": "ceph", "uuid": ps_uuid, "poolNames": [root_pool_name]}}, "priceUserConfig": {"rootVolume": {"priceKeyName": "highSpeedDisk"}}, "displayAttribute": {"rootVolume": {"云盘类型": "高速云盘"}}}
instance_offering_opt.set_system_tags(["instanceOfferingUserConfig::%s" % instance_offering_systemtags_json])
instance_offering_uuid = vm_ops.create_instance_offering(instance_offering_opt).uuid

def test():
	success_round = 0
	for i in range(0,vm_max):
		test_util.test_logger("clear data in RootVolumeUsageVO and PriceVO")
		test_lib.resource_price_clear(billing_resource)
		test_util.test_logger("=====SPENDING CHECK VM %s=====" % str(i+1)) 
		bill_rootvolume = test_lib.RootVolumeBilling()
		time_unit = random.choice(time_unit_dict)
		price = str(random.randint(0,9999))
		resource_unit = random.choice(resource_unit_dict.keys())
        	bill_rootvolume.set_timeUnit(time_unit)
		bill_rootvolume.set_price(price)
		bill_rootvolume.set_resourceUnit(resource_unit)
		bill_rootvolume.set_price_system_tags(price_system_tags)
		test_util.test_logger("create rootvolume price\n price=%s, timeUnit=%s, resourceUnit=%s \n systemTags=%s" % (price, time_unit, resource_unit, price_system_tags))
		price = bill_rootvolume.create_resource_type()
		if not price:
			test_util.test_fail("fail: create rootvolume price")
                else:
                        test_util.test_logger("success: create rootvolume price %s" % price.uuid)


		test_util.test_logger("create vm instance")        
		global vm
        	vm = test_lib.create_vm_billing("test_vmm", test_lib.set_vm_resource()[0], None,\
							instance_offering_uuid, test_lib.set_vm_resource()[2])

		rootVolumeSize = res_ops.query_resource(res_ops.VM_INSTANCE, \
					res_ops.gen_query_conditions('uuid', '=',\
					                        vm.get_vm().uuid))[0].allVolumes[0].size / resource_unit_dict[resource_unit]
		test_util.test_logger("@@@@debug %s %s" %(resource_unit, rootVolumeSize))

		test_util.test_logger("====check vm spending====")
		for r in range(0,round_max):
			test_util.test_logger("===spending check round %s-%s===" % (str(i+1), str(r+1)))
			if test_lib.billing_check(bill_rootvolume, billing_resource, random.choice(offset_unit_dict), random.randint(0,3), rootVolumeSize):
				success_round += 1
			else:
				test_util.test_fail("check rootvolume billing spending finished\n success: %s/%s" % (success_round, round_sum))
	test_util.test_pass("check root volume billing finished\n success: %s/%s" % (success_round,round_sum))

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
