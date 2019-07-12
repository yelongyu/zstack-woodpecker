'''
New Test For cpu bill Operations
        1.create cpu billing operations
        2.deltet cpu billing operations
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
	test_util.test_logger("start cpu billing")
	test_util.test_logger("create man cpu billing instantiation")
	bill_cpu = test_stub.CpuBilling()

	test_util.test_logger("loop 400 to create cpu billing")
	test_stub.create_option_billing(bill_cpu, count)
	
	test_util.test_logger("verify cpu billing instantiation if is right,and then delete all")
	test_stub.verify_option_billing(count)
	
	test_util.test_logger("create cpu billing instantiation")
        bill_cpu.set_timeUnit("s")
	bill_cpu.set_price("5")
	bill_cpu.create_resource_type()
	test_util.test_logger("create vm instance")
        
	global vm
        vm = test_stub.create_vm_billing("test_vmm", test_stub.set_vm_resource()[0], None,\
						test_stub.set_vm_resource()[1], test_stub.set_vm_resource()[2])
	
	cpuNum = res_ops.query_resource_fields(res_ops.INSTANCE_OFFERING, \
			res_ops.gen_query_conditions('uuid', '=',\
				test_stub.set_vm_resource()[1]))[0].cpuNum
	time.sleep(1)
	if bill_cpu.get_price_total().total < cpuNum * int(bill_cpu.get_price()):
		test_util.test_fail("calculate cpu cost fail,actual result is %s" %(bill_cpu.get_price_total().total))
	vm.clean()

	bill_cpu.delete_resource()
	test_util.test_pass("check cpu billing pass")

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
			
