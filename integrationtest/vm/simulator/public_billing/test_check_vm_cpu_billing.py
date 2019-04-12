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

def test():
        test_util.test_logger("clear data in  VmUsageVO and PriceVO")
        test_stub.resource_price_clear(billing_resource)
	
	test_util.test_logger("create cpu billing")
	bill_cpu = test_stub.CpuBilling()
	bill_cpu.create_resource_type()
	
	test_util.test_logger("create vm instance")
	global vm
	vm = test_stub.create_vm_billing("test_vmm", test_stub.set_vm_resource()[0], None,\
                                                test_stub.set_vm_resource()[1], test_stub.set_vm_resource()[2])
        cpuNum = res_ops.query_resource_fields(res_ops.INSTANCE_OFFERING, \
                        res_ops.gen_query_conditions('uuid', '=',\
                                test_stub.set_vm_resource()[1]))[0].cpuNum

        test_util.test_logger("====check vm spending====")
	for i in range(1,10):
		test_util.test_logger('==spending check round %s===\n' % i)
		test_stub.check(bill_cpu, billing_resource, random.choice(offset_unit_dict), random.randint(0,30), cpuNum)
	test_util.test_pass("check vm billing spending pass")


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

