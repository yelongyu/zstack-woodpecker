'''
New Test For bill Operations
        1.create memory billing operations
        2.deltet memory billing operations
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
	test_util.test_logger("start memory billing")
	test_util.test_logger("create man memory billing instantiation")
	bill_memory = test_stub.MemoryBilling()

	test_util.test_logger("loop 400 to create memory billing")
	test_stub.create_option_billing(bill_memory, count)
	
	test_util.test_logger("verify memory billing instantiation if is right,and then delete all")
	test_stub.verify_option_billing(count)
	
	test_util.test_logger("create memory billing instantiation")
        bill_memory.set_timeUnit("s")
	bill_memory.set_price("5")
	bill_memory.create_resource_type()
	test_util.test_logger("create vm instance")
        
	global vm
        vm = test_stub.create_vm_billing("test_vmm", test_stub.set_vm_resource()[0], None,\
						test_stub.set_vm_resource()[1], test_stub.set_vm_resource()[2])
	vm_memory_size_ratio = res_ops.query_resource_fields(res_ops.INSTANCE_OFFERING, \
					res_ops.gen_query_conditions('uuid', '=',\
						test_stub.set_vm_resource()[1]))[0].memorySize / 1024 / 1024 / float(1024)
	time.sleep(1)
	if float(bill_memory.get_price()) * vm_memory_size_ratio > bill_memory.get_price_total().total:
		test_util.test_fail("calculate memory cost fail,actual result is %s" %(bill_memory.get_price_total().total))

	vm.clean()

	bill_memory.delete_resource()
	test_util.test_pass("check memory billing pass")

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
