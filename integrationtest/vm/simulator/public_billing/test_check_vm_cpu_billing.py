'''
New Test For cpu bill spending check
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
billing_resource = 'vm'
offset_unit_dict=['sec','min','hou','day','week','month','year']
time_unit_dict=['s','m','h','d','w','mon']

def test():
	success_round = 0
	for i in range(0,10):	
	        test_util.test_logger("clear data in  VmUsageVO and PriceVO")
	        test_stub.resource_price_clear(billing_resource)
		test_util.test_logger("=====SPENDING CHECK VM %s=====" % str(i+1))
		bill_cpu = test_stub.CpuBilling()
		time_unit = random.choice(time_unit_dict)
		price = str(random.randint(0,9999))
		bill_cpu.set_timeUnit(time_unit)
		bill_cpu.set_price(price)
		test_util.test_logger("create cpu billing\n price=%s, timeUnit=%s" % (price, time_unit))
		bill_cpu.create_resource_type()
		
		test_util.test_logger("create vm instance")
		global vm
		vm = test_stub.create_vm_billing("test_vmm", test_stub.set_vm_resource()[0], None,\
	                                                test_stub.set_vm_resource()[1], test_stub.set_vm_resource()[2])
	        cpuNum = res_ops.query_resource_fields(res_ops.INSTANCE_OFFERING, \
	                        res_ops.gen_query_conditions('uuid', '=',\
	                                test_stub.set_vm_resource()[1]))[0].cpuNum
	
	        test_util.test_logger("====check vm spending====")
		for r in range(0,10):
			test_util.test_logger('===spending check round %s-%s===' % (str(i+1), str(r+1)))
			if test_stub.check(bill_cpu, billing_resource, random.choice(offset_unit_dict), random.randint(0,3), cpuNum):
				success_round += 1
	if success_round != 100:
		test_util.test_fail("check vm billing spending finished\n success: %s/100" % success_round)	
	else:
		test_util.test_pass("check vm billing spending finished\n success: %s/100" % success_round)


def error_cleanup():
	global vm
	if vm:
		vm.clean()

def env_recover():
	#return
        global vm
        if vm:
                vm.clean()
        resourcePrices = test_stub.query_resource_price()
        if resourcePrices:
                for resourceprice in resourcePrices:
                        test_stub.delete_price(resourceprice.uuid)

