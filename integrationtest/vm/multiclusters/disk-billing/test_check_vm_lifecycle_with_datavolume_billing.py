#-*- coding: UTF-8 -*-
'''
New Test For data volume bill Operations
	1.test vm stop
	2.test vm destroy
	3.test vm live migration
	4.test vm clean
	5.test volume destroy
	6.test volume expunge
'''
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.billing_operations as bill_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import threading
import time
import json
import os

test_obj_dict = test_state.TestStateDict()
vm = None

#systemtags config
ps_uuid = res_ops.query_resource_fields(res_ops.CEPH_PRIMARY_STORAGE)[0].uuid
data_pool_name = 'test-pool-Data-1-' + ps_uuid
price_systemtags_json = json.dumps({"priceUserConfig":{"priceKeyName":"highSpeedDisk"}})
price_system_tags = ["priceUserConfig::%s" % price_systemtags_json,]
disk_offering_systemtags_json = json.dumps({"allocate": {"primaryStorage": {"type": "ceph", "uuid": ps_uuid, "poolNames": [data_pool_name]}}, "priceUserConfig": {"volume": {"priceKeyName": "highSpeedDisk"}}, "displayAttribute": {"volume": {"云盘类型": "高速云盘"}}})
disk_offering_system_tags = ["diskOfferingUserConfig::%s"  % disk_offering_systemtags_json,]


def test():
	test_util.test_logger("start check vm lifecycle")
	
	test_util.test_logger("create data volume billing")
	
	bill_datavolume = test_lib.DataVolumeBilling()
	bill_datavolume.set_timeUnit("s")
        bill_datavolume.set_price("1")
        bill_datavolume.set_resourceUnit("M")
	bill_datavolume.set_price_system_tags(price_system_tags)
	bill_datavolume.create_resource_type()
	
	test_util.test_logger("create vm instance")

	global vm
	vm = test_lib.create_vm_billing("test_vmm", test_lib.set_vm_resource()[0], None,\
                                                test_lib.set_vm_resource()[1], test_lib.set_vm_resource()[2])

	disk_offering_uuid = bill_datavolume.create_disk_offer(1048576,"test_disk",disk_offering_system_tags).uuid
	bill_datavolume.create_volume_and_attach_vmm(disk_offering_uuid,"test_volume",vm)
	test_util.test_logger("antony @@@@debug %s" %(bill_datavolume.disk.get_name()))
	dataVolumeSize = res_ops.query_resource(res_ops.DISK_OFFERING, \
				res_ops.gen_query_conditions('name', '=',\
					bill_datavolume.disk.get_name()))[0].diskSize / 1024 / float(1024)

	time.sleep(1)
	test_util.test_logger("verify calculate if right is")
	if bill_datavolume.get_billing_price_total().total < dataVolumeSize * int(bill_datavolume.get_price()):
		test_util.test_fail("calculate data volume cost fail,actual result is %s" \
							%(bill_datavolume.get_billing_price_total().total))
	
	test_util.test_logger("stop vm instance")
	vm.stop()
	bill_datavolume.compare("stop")

	test_util.test_logger("destroy vm instance")
	vm.destroy()
	bill_datavolume.compare("destroy")

	test_util.test_logger("recover vm instance")
	vm.recover()
	vm.start()
	bill_datavolume.compare("recover")

	test_util.test_logger("clean vm instance")
	vm.clean()
	bill_datavolume.compare("clean")
 	
	test_util.test_logger("destroy volume")
	bill_datavolume.volume.delete()
	bill_datavolume.compare("delete_volume")
	
	test_util.test_logger("expunge volume")
	bill_datavolume.volume.expunge()
	bill_datavolume.compare("volume_clean")	

	test_util.test_logger("delete disk offering")
	vol_ops.delete_disk_offering(disk_offering_uuid)

	test_util.test_logger("delete price resource")
	resourcePrices = test_lib.query_resource_price()
	for resource_price in resourcePrices:
		test_lib.delete_price(resource_price.uuid)

	test_util.test_pass("check vm lifecycle with data volume billing pass")

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
