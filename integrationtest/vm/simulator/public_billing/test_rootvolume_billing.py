'''
New Test For root volume bill Operations
        1.create root volume billing operations
        2.deltet root volume billing operations
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
count = 400

def test():
	test_stub.update_billing_symbol()
	test_util.test_logger("start root volume billing")
	test_util.test_logger("create many root volume  billing instantiation")
	bill_rootvolume = test_stub.RootVolumeBilling()
	test_util.test_logger("loop 400 to create root volume billing")
	test_stub.create_option_billing(bill_rootvolume, count)
	
	test_util.test_logger("verify root volume billing instantiation if is right,and then delete all")
	test_stub.verify_option_billing(count)
	
	test_util.test_logger("create root volume billing instantiation")
        bill_rootvolume.set_timeUnit("s")
	bill_rootvolume.set_price("1")
	bill_rootvolume.set_resourceUnit("M")
	bill_rootvolume.create_resource_type()
	test_util.test_logger("create vm instance")
        
	global vm
        vm = test_stub.create_vm_billing("test_vmm", test_stub.set_vm_resource()[0], None,\
						test_stub.set_vm_resource()[1], test_stub.set_vm_resource()[2])

	rootVolumeSize = res_ops.query_resource(res_ops.VM_INSTANCE, \
				res_ops.gen_query_conditions('uuid', '=',\
				                        vm.get_vm().uuid))[0].allVolumes[0].size / 1024 / float(1024)
	test_util.test_logger("antony @@@@debug %s" %(rootVolumeSize))

	time.sleep(1)
	if bill_rootvolume.get_price_total().total < rootVolumeSize * int(bill_rootvolume.get_price()):
		test_util.test_fail("calculate root volume cost fail,actual result is %s" %(bill_rootvolume.get_price_total().total))
	vm.clean()

	bill_rootvolume.delete_resource()
	test_util.test_pass("check root volume billing pass")

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
