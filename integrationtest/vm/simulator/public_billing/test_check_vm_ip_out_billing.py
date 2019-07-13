'''
New Test For ip bill spending check
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
billing_resource = 'ip_in'
offset_unit_dict=['sec','min','hou','day','week','month','year']
time_unit_dict=['s','m','h','d','w','mon']
resource_unit_dict={"K": float(1024), "M":1024 * float(1024), "G":1024**2 * float(1024)}
vm_max=10
round_max=10
round_sum=vm_max * round_max

def test():
	# test_stub.update_billing_symbol()
	success_round = 0
	for i in range(0,vm_max):	
	        test_util.test_logger("clear %s data" % billing_resource)
	        test_stub.resource_price_clear(billing_resource)
		test_util.test_logger("=====SPENDING CHECK VIP %s=====" % str(i+1))
		bill_ip_out = test_stub.PublicIpNicOutBilling()
		time_unit = random.choice(time_unit_dict)
		price = str(random.randint(0,9999))
		resource_unit = random.choice(resource_unit_dict.keys())
		bill_ip_out.set_timeUnit(time_unit)
		bill_ip_out.set_price(price)
		bill_ip_out.set_resourceUnit(resource_unit)
		test_util.test_logger("create ip nic in billing\n price=%s, timeUnit=%s" % (price, time_unit))
		bill_ip_out.create_resource_type()
		
		test_util.test_logger("create ip nic instance and set qos")
		global vm
		vm = test_stub.create_vm_billing("test_vmm", test_stub.set_vm_resource()[0], None,\
                                                        test_stub.set_vm_resource()[1], test_stub.set_vm_resource()[2])
		qos_out = 1048576 #1M
		vm_nic_uuid = vm.vm.vmNics[0].uuid
		vm_ops.set_vm_nic_qos(vm_nic_uuid, outboundBandwidth = qos_out)	
		qos_size = qos_out/resource_unit_dict[resource_unit]	
		test_util.test_logger("@DEBUG@: qos_size=%s resource_unit=%s" % (qos_size, resource_unit))
	
	        test_util.test_logger("====check ip nic %s spending====" % vm_nic_uuid)
		for r in range(0,round_max):
			test_util.test_logger('===spending check round %s-%s===' % (str(i+1), str(r+1)))
			if test_stub.check(bill_ip_out, billing_resource, random.choice(offset_unit_dict), random.randint(0,3), qos_size):
				success_round += 1
			else:
				test_util.test_fail("check ip nic billing spending finished\n success: %s/%s" % (success_round, round_sum))	
				
	test_util.test_pass("check ip nic billing spending finished\n success: %s/%s" % (success_round, round_sum))

def error_cleanup():
	global vm
	if vm:
		vm.clean()

def env_recover():
	return
        global vm
        if vm:
                vm.clean()
        resourcePrices = test_stub.query_resource_price()
        if resourcePrices:
                for resourceprice in resourcePrices:
                        test_stub.delete_price(resourceprice.uuid)
