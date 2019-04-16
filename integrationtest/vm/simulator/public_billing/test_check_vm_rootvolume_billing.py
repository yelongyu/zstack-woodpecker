'''
New Test For rootvolume bill spending check
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
billing_resource = 'rootvolume'
offset_unit_dict=['sec','min','hou','day','week','month','year']
time_unit_dict=['s','m','h','d','w','mon']
resource_unit_dict={"M":1024 * float(1024), "G":1024**2 * float(1024), "T":1024**3 * float(1024)}

def test():
	success_round = 0
	for i in range(0,10):
		test_util.test_logger("clear data in RootVolumeUsageVO and PriceVO")
		test_stub.resource_price_clear(billing_resource)
		test_util.test_logger("=====SPENDING CHECK VM %s=====" % str(i+1)) 
		bill_rootvolume = test_stub.RootVolumeBilling()
		time_unit = random.choice(time_unit_dict)
		price = str(random.randint(0,9999))
		resource_unit = random.choice(resource_unit_dict.keys())
        	bill_rootvolume.set_timeUnit(time_unit)
		bill_rootvolume.set_price(price)
		bill_rootvolume.set_resourceUnit(resource_unit)
		test_util.test_logger("create rootvolume billing\n price=%s, timeUnit=%s, resourceUnit=%s" % (price, time_unit, resource_unit))
		bill_rootvolume.create_resource_type()

		test_util.test_logger("create vm instance")        
		global vm
        	vm = test_stub.create_vm_billing("test_vmm", test_stub.set_vm_resource()[0], None,\
							test_stub.set_vm_resource()[1], test_stub.set_vm_resource()[2])

		rootVolumeSize = res_ops.query_resource(res_ops.VM_INSTANCE, \
					res_ops.gen_query_conditions('uuid', '=',\
					                        vm.get_vm().uuid))[0].allVolumes[0].size / resource_unit_dict[resource_unit]
		test_util.test_logger("@@@@debug %s %s" %(resource_unit, rootVolumeSize))

		test_util.test_logger("====check vm spending====")
		for r in range(0,10):
			test_util.test_logger("===spending check round %s-%s===" % (str(i+1), str(r+1)))
			if test_stub.check(bill_rootvolume, billing_resource, random.choice(offset_unit_dict), random.randint(0,3), rootVolumeSize):
				success_round += 1
	if success_round != 100:
		test_util.test_fail("check root volume billing finished\n success: %s/100" % success_round)
	else:
		test_util.test_pass("check root volume billing finished\n success: %s/100" % success_round)

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
