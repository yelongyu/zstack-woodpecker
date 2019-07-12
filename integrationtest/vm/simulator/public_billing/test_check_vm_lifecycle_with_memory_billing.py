'''
New Test For memory bill Operations
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
import threading
import time
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
vm = None

def test():
	test_stub.update_billing_symbol()
	test_util.test_logger("start check vm lifecycle")
	
	test_util.test_logger("create memory  billing")
	
	bill_memory = test_stub.MemoryBilling()
	bill_memory.create_resource_type()
	
	test_util.test_logger("create vm instance")

	global vm
	vm = test_stub.create_vm_billing("test_vmm", test_stub.set_vm_resource()[0], None,\
                                                test_stub.set_vm_resource()[1], test_stub.set_vm_resource()[2])

    	time.sleep(1)
	test_util.test_logger("verify calculate if right is")
	vm_memory_size_ratio = res_ops.query_resource_fields(res_ops.INSTANCE_OFFERING, \
				res_ops.gen_query_conditions('uuid', '=',\
					test_stub.set_vm_resource()[1]))[0].memorySize / 1024 / 1024 / float(1024)
	if float(bill_memory.get_price()) * vm_memory_size_ratio > bill_memory.get_price_total().total:
		test_util.test_fail("test billing fail, bill is %s ,less than %s" \
				%(bill_memory.get_price().total,float(bill_memory.get_price()) * vm_memory_size_ratio))
	
	test_util.test_logger("stop vm instance")
	vm.stop()
	bill_memory.compare("stop")

	test_util.test_logger("destory vm instance")
	vm.destroy()
	bill_memory.compare("destory")

	test_util.test_logger("recover vm instance")
	vm.recover()
	vm.start()
	bill_memory.compare("recover")

	test_util.test_logger("get host total and primarystorge type")
	Host_uuid = test_stub.get_resource_from_vmm(res_ops.HOST,vm.get_vm().zoneUuid,vm.get_vm().hostUuid)
	PrimaryFlag = test_stub.get_resource_from_vmm(res_ops.PRIMARY_STORAGE,vm.get_vm().zoneUuid,\
										vm.get_vm().hostUuid)
	test_util.test_logger("antony %s" %(Host_uuid))
	test_util.test_logger("antony %s" %(PrimaryFlag))
	if Host_uuid  and PrimaryFlag == 0:
		test_util.test_logger("migration vm instance")
		prices = bill_memory.get_price_total()
		vm.migrate(Host_uuid)
		prices1 = bill_memory.get_price_total()
		if prices1.total >  prices.total:
			bill_memory.compare("migration")
		else:
			test_util.test_fail("test bill fail, maybe can not calculate when vm live migration")

	test_util.test_logger("clean vm instance")
	vm.clean()
	bill_memory.compare("clean")
	
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

