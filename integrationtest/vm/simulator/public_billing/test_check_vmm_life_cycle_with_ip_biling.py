'''
New Test For ip bill Operations
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
	# test_stub.update_billing_symbol()
	test_util.test_logger("start check vm lifecycle")
	
	test_util.test_logger("create public ip billing")
	
	bill_ip = test_stub.PublicIpBilling()
	ipin = threading.Thread(target=bill_ip.create_resource_type(),\
				args=(bill_ip.get_resourceName()))
	bill_ip.set_resourceName("pubIpVmNicBandwidthOut")
	ipout = threading.Thread(target=bill_ip.create_resource_type(),\
				args=(bill_ip.get_resourceName()))
	ipin.start()
	ipout.start()
	
	test_util.test_logger("create vm instance")

	global vm
	vm = test_stub.create_vm_billing("test_vmm", test_stub.set_vm_resource()[0], None,\
                                                test_stub.set_vm_resource()[1], test_stub.set_vm_resource()[2])

	vm_nic = test_lib.lib_get_vm_nic_by_l3(vm.get_vm(), test_stub.set_vm_resource()[2])
	
	test_util.test_logger("set vm nic bandwidth")
	net_bandwidth = 10*1024*1024
	vm_ops.set_vm_nic_qos(vm_nic.uuid, outboundBandwidth = net_bandwidth, inboundBandwidth = net_bandwidth)
	
    	time.sleep(1)
	test_util.test_logger("verify calculate if right is")
	if bill_ip.get_price_total().total < 100:
		test_util.test_fail("test billing fail, bill is %s ,less than 100" %(bill_ip.get_price_total().total))
	
	test_util.test_logger("stop vm instance")
	vm.stop()
	bill_ip.compare("stop")

	test_util.test_logger("destory vm instance")
	vm.destroy()
	bill_ip.compare("destory")

	test_util.test_logger("recover vm instance")
	vm.recover()
	vm.start()
	bill_ip.compare("recover")

	test_util.test_logger("get host total and primarystorge type")
	Host_uuid = test_stub.get_resource_from_vmm(res_ops.HOST,vm.get_vm().zoneUuid,vm.get_vm().hostUuid)
	PrimaryFlag = test_stub.get_resource_from_vmm(res_ops.PRIMARY_STORAGE,vm.get_vm().zoneUuid)
	if Host_uuid  and PrimaryFlag == 0:
		test_util.test_logger("migration vm instance")
		prices = bill_ip.get_price_total()
		vm.migrate(Host_uuid)
		prices1 = bill_ip.get_price_total()
		if prices1.total >  prices.total:
			bill_ip.compare("migration")
		else:
			test_util.test_fail("test bill fail, maybe can not calculate when vm live migration")
	BackStorageFlag = test_stub.get_resource_from_vmm(res_ops.BACKUP_STORAGE)
	if BackStorageFlag == 1:
		clone = vm.clone(["clone-1"])
		vm.clean()
		bill_ip.compare("clone")
		clone[0].clean()
	else:	
		test_util.test_logger("clean vm instance")
		vm.clean()
		bill_ip.compare("clean")
	
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

