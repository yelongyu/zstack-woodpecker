'''
New Test For vip bill spending check
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
billing_resource = 'vip_in'
offset_unit_dict=['sec','min','hou','day','week','month','year']
time_unit_dict=['s','m','h','d','w','mon']
resource_unit_dict={"K": float(1024), "M":1024 * float(1024), "G":1024**2 * float(1024)}
vip_max=10
round_max=10
round_sum=vip_max * round_max

def test():
	# test_stub.update_billing_symbol()
	success_round = 0
	for i in range(0,vip_max):	
	        test_util.test_logger("clear %s data" % billing_resource)
	        test_stub.resource_price_clear(billing_resource)
		test_util.test_logger("=====SPENDING CHECK VIP %s=====" % str(i+1))
		bill_vip_out = test_stub.PublicIpVipOutBilling()
		time_unit = random.choice(time_unit_dict)
		price = str(random.randint(0,9999))
		resource_unit = random.choice(resource_unit_dict.keys())
		bill_vip_out.set_timeUnit(time_unit)
		bill_vip_out.set_price(price)
		bill_vip_out.set_resourceUnit(resource_unit)
		test_util.test_logger("create vip out billing\n price=%s, timeUnit=%s" % (price, time_unit))
		bill_vip_out.create_resource_type()
		
		test_util.test_logger("create vip instance and set qos")
		global vip
		vip = test_stub.create_vip()
		qos_out = 1048576 #1M
		net_ops.set_vip_qos(vip.vip.uuid, outboundBandwidth = qos_out)	
		qos_size = qos_out/resource_unit_dict[resource_unit]	
	
	        test_util.test_logger("====check vip %s spending====" % vip.vip.uuid)
		for r in range(0,round_max):
			test_util.test_logger('===spending check round %s-%s===' % (str(i+1), str(r+1)))
			if test_stub.check(bill_vip_out, billing_resource, random.choice(offset_unit_dict), random.randint(0,3), qos_size):
				success_round += 1
			else:
				test_util.test_fail("check vip billing spending finished\n success: %s/%s" % (success_round, round_sum))	
				
	test_util.test_pass("check vip billing spending finished\n success: %s/%s" % (success_round, round_sum))

def error_cleanup():
	global vip
	if vip:
		vip.clean()

def env_recover():
	return
        global vip
        if vip:
                vip.clean()
        resourcePrices = test_stub.query_resource_price()
        if resourcePrices:
                for resourceprice in resourcePrices:
                        test_stub.delete_price(resourceprice.uuid)
