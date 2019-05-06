#-*- coding:UTF-8 -*-
'''
New Test For root volume bill Operations
	1.test vm stop
	2.test vm destroy
	3.test vm live migration
	4.test vm clean
'''
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.billing_operations as bill_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.net_operations as net_ops
import threading
import time
import json
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
vm = None

#systemtags config
ps_uuid = res_ops.query_resource_fields(res_ops.CEPH_PRIMARY_STORAGE)[0].uuid
root_pool_name = 'test-pool-Root-1-' + ps_uuid
price_systemtags_json = json.dumps({"priceUserConfig":{"priceKeyName":"highSpeedDisk"}})
price_system_tags = ["priceUserConfig::%s" % price_systemtags_json,]
instance_offering_opt = test_util.InstanceOfferingOption()
instance_offering_opt.set_cpuNum(2)
instance_offering_opt.set_memorySize(1073741824)
instance_offering_opt.set_name('systemTags-test')
instance_offering_systemtags_json = json.dumps({"allocate": {"primaryStorage": {"type": "ceph", "uuid": ps_uuid, "poolNames": [root_pool_name]}}, "priceUserConfig": {"rootVolume": {"priceKeyName": "highSpeedDisk"}}, "displayAttribute": {"rootVolume": {"云盘类型": "普通云盘"}}})
instance_offering_opt.set_system_tags(["instanceOfferingUserConfig::%s" % instance_offering_systemtags_json,])
instance_offering_uuid = vm_ops.create_instance_offering(instance_offering_opt).uuid


def test():
	test_util.test_logger("start check vm lifecycle")
	
	test_util.test_logger("create root volume billing")
	
	bill_rootvolume = test_lib.RootVolumeBilling()
	bill_rootvolume.set_timeUnit("s")
        bill_rootvolume.set_price("1")
        bill_rootvolume.set_resourceUnit("M")
	bill_rootvolume.set_price_system_tags(price_system_tags)
	bill_rootvolume.create_resource_type()
	
	test_util.test_logger("create vm instance")

	global vm
	vm = test_lib.create_vm_billing("test_vmm", test_lib.set_vm_resource()[0], None,\
                                                instance_offering_uuid, test_lib.set_vm_resource()[2])
    	
	rootVolumeSize = res_ops.query_resource(res_ops.VM_INSTANCE, \
				res_ops.gen_query_conditions('uuid', '=',\
					vm.get_vm().uuid))[0].allVolumes[0].size / 1024 / float(1024)
	time.sleep(1) 
	test_util.test_logger("verify calculate if right is")
	if bill_rootvolume.get_billing_price_total().total < rootVolumeSize * int(bill_rootvolume.get_price()):
		test_util.test_fail("test billing fail, bill is %s ,less than %s"\
					 %(bill_rootvolume.get_billing_price_total().total,cpuNum * bill_rootvolume.get_price()))
	
	test_util.test_logger("stop vm instance")
	vm.stop()
	bill_rootvolume.compare("stop")

	test_util.test_logger("destroy vm instance")
	vm.destroy()
	bill_rootvolume.compare("destroy")

	test_util.test_logger("recover vm instance")
	vm.recover()
	vm.start()
	bill_rootvolume.compare("recover")

	test_util.test_logger("get host total and primarystorge type")
	Host_uuid = test_stub.get_resource_from_vmm(res_ops.HOST,vm.get_vm().zoneUuid,vm.get_vm().hostUuid)
	PrimaryFlag = test_stub.get_resource_from_vmm(res_ops.PRIMARY_STORAGE,vm.get_vm().zoneUuid,\
										vm.get_vm().hostUuid)
	test_util.test_logger("@@@@debug %s" %(Host_uuid))
	test_util.test_logger("@@@@debug %s" %(PrimaryFlag))
	if Host_uuid  and PrimaryFlag == 0:
		test_util.test_logger("migration vm instance")
		prices = bill_rootvolume.get_price_total()
		vm.migrate(Host_uuid)
		prices1 = bill_rootvolume.get_price_total()
		if prices1.total >  prices.total:
			bill_rootvolume.compare("migration")
		else:
			test_util.test_fail("test bill fail, maybe can not calculate when vm live migration")

	test_util.test_logger("clean vm instance")
	vm.clean()
	bill_rootvolume.compare("clean")
	
	test_util.test_logger("delete root volume resource")
	resourcePrices = test_lib.query_resource_price()
	for resource_price in resourcePrices:
		test_lib.delete_price(resource_price.uuid)

	test_util.test_pass("check vm lifecycle with root volume billing pass")

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
