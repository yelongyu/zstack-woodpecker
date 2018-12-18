'''
New Test For data volume bill Operations
	1.test vm stop
	2.test vm destory
	3.test vm live migration
	4.test vm clean
@author Antony WeiJiang
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
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
vm = None

def test():
	test_util.test_logger("start check vm lifecycle")
	
	test_util.test_logger("create data volume billing")
	
	bill_datavolume = test_stub.DataVolumeBilling()
	bill_datavolume.set_timeUnit("s")
        bill_datavolume.set_price("1")
        bill_datavolume.set_resourceUnit("M")
	bill_datavolume.create_resource_type()
	
	test_util.test_logger("create vm instance")

	global vm
	vm = test_stub.create_vm_billing("test_vmm", test_stub.set_vm_resource()[0], None,\
                                                test_stub.set_vm_resource()[1], test_stub.set_vm_resource()[2])

	disk_offering_uuid = bill_datavolume.create_disk_offer(1048576,"test_disk").uuid
	bill_datavolume.create_volume_and_attach_vmm(disk_offering_uuid,"test_volume",vm)
	test_util.test_logger("antony @@@@debug %s" %(bill_datavolume.disk.get_name()))
	dataVolumeSize = res_ops.query_resource(res_ops.DISK_OFFERING, \
				res_ops.gen_query_conditions('name', '=',\
					bill_datavolume.disk.get_name()))[0].diskSize / 1024 / float(1024)

	time.sleep(1)
	test_util.test_logger("verify calculate if right is")
	if bill_datavolume.get_price_total().total < dataVolumeSize * int(bill_datavolume.get_price()):
		test_util.test_fail("calculate data volume cost fail,actual result is %s" \
							%(bill_datavolume.get_price_total().total))
	
	test_util.test_logger("stop vm instance")
	vm.stop()
	bill_datavolume.compare("stop")

	test_util.test_logger("destory vm instance")
	vm.destroy()
	bill_datavolume.compare("destory")

	test_util.test_logger("recover vm instance")
	vm.recover()
	vm.start()
	bill_datavolume.compare("recover")

	test_util.test_logger("clean vm instance")
	vm.clean()
	bill_datavolume.compare("clean")
 	
	test_util.test_logger("destory volume")
	bill_datavolume.volume.delete()
	bill_datavolume.compare("delete_volume")
	
	test_util.test_logger("expunge volume")
	bill_datavolume.volume.expunge()
	bill_datavolume.compare("volume_clean")	

	test_util.test_logger("delete disk offering")
	vol_ops.delete_disk_offering(disk_offering_uuid)

	test_util.test_logger("delete  public ip resource")
	resourcePrices = test_stub.query_resource_price()
	for resource_price in resourcePrices:
		test_stub.delete_price(resource_price.uuid)

	test_util.test_pass("check vm lifecycle with public ip billing pass")

def error_cleanup():
	global vm
	if vm:
		vm.clean()

def env_recover():
	global vm
	if vm:
		vm.clean()
	resourcePrices = test_stub.query_resource_price()
	if resourcePrices:
		for resourceprice in resourcePrices:
			test_stub.delete_price(resourceprice.uuid)
