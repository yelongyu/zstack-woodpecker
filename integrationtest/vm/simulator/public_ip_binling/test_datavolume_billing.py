'''
New Test For data volume bill Operations
        1.create data volume billing operations
        2.deltet data volume billing operations
@author Antony WeiJiang
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
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
vm = None
count = 10

def test():
	test_util.test_logger("start data volume billing")
	test_util.test_logger("create many data volume  billing instantiation")
	bill_datavolume = test_stub.DataVolumeBilling()
	test_util.test_logger("loop 400 to create data volume billing")
	test_stub.create_option_billing(bill_datavolume, count)
	
	test_util.test_logger("verify data volume billing instantiation if is right,and then delete all")
	test_stub.verify_option_billing(count)
	
	test_util.test_logger("create data volume billing instantiation")
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
			                        bill_datavolume.disk.get_name())).diskSize / 1024 / float(1024)
#	test_util.test_logger("antony @@@@debug %s" %(dataVolumeSize))
#
#	time.sleep(1)
#	if bill_datavolume.get_price_total().total < dataVolumeSize * int(bill_datavolume.get_price()):
#		test_util.test_fail("calculate data volume cost fail,actual result is %s" %(bill_datavolume.get_price_total().total))
#	vm.clean()
#
#	bill_datavolume.delete_resource()
#	test_util.test_pass("check data volume billing pass")

#def error_cleanup():
#	global vm
#	if vm:
#		vm.clean()
#
#def env_recover():
#	global vm
#	if vm:
#		vm.clean()
#	resourcePrices = test_stub.query_resource_price()
#	if resourcePrices:
#		for resourceprice in resourcePrices:
#			test_stub.delete_price(resourceprice.uuid)

