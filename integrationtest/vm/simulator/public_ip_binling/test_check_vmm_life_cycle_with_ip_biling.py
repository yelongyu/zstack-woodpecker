'''
New Test For bill Operations
	1.test vm stop
	2.test vm destory
	3.test vm live migration
	4.test vm suspend
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

def test():
	test_util.test_logger("start check vm lifecycle")
	
	test_util.test_logger("create public ip billing")
	
	bill_ip = test_stub.PublicIpBilling()
	ipin = threading.Thread(target=bill_ip.create_resource_type(),\
				args=(bill_ip.set_resourceName("pubIpVmNicBandwidthIn")))
	bill_ip.set_resourceName("pubIpVmNicBandwidthOut")
	ipout = threading.Thread(target=bill_ip.create_resource_type(),\
				args=(bill_ip.get_resourceName()))
	ipin.start()
	ipout.start()
	
	test_util.test_logger("create vm instance")
    	imageUuid = res_ops.query_resource_fields(res_ops.IMAGE, \
				res_ops.gen_query_conditions('system', '=',  'false'))[0].uuid
	instanceOfferingUuid = res_ops.query_resource_fields(res_ops.INSTANCE_OFFERING, \
				res_ops.gen_query_conditions('type', '=',  'UserVm'))[0].uuid
	l3NetworkUuids = res_ops.query_resource_fields(res_ops.L3_NETWORK, \
				res_ops.gen_query_conditions('name', '=',  'public network'))[0].uuid
	vm = test_stub.create_vm_billing("test_vmm", imageUuid, None,instanceOfferingUuid, l3NetworkUuids)
	vm_nic = test_lib.lib_get_vm_nic_by_l3(vm.get_vm(), l3NetworkUuids)
	
	test_util.test_logger("set vm nic bandwidth")
	net_bandwidth = 10*1024*1024
	vm_ops.set_vm_nic_qos(vm_nic.uuid, outboundBandwidth = net_bandwidth, inboundBandwidth = net_bandwidth)
	
	test_util.test_logger("calculate ip cost")
	cond = res_ops.gen_query_conditions('name', '=',  'admin')
    	time.sleep(1)
    	admin_uuid = res_ops.query_resource_fields(res_ops.ACCOUNT, cond)[0].uuid
	prices = bill_ops.calculate_account_spending(admin_uuid)
	
	test_util.test_logger("verify calculate if right is")
	if prices.total < 100:
		test_util.test_fail("test billing fail, bill is %s ,less than 100" %(prices.total))
	
	test_util.test_logger("stop vm instance")
	vm.stop()
	compare(admin_uuid,"stop")

	test_util.test_logger("destory vm instance")
	vm.destory()
	compare(admin_uuid,"destory")

	test_util.test_logger("livemigration vm instance")
	cond = res_ops.gen_query_conditions('zoneUuid', '=', vm.get_vm().zoneUuid)
	Host = res_ops.query_resource(res_ops.HOST, cond)
	Host_uuid = get_resource_from_vmm("Host",vm.get_vm().zoneUuid,vm.get_vm().hostUuid)
 		
	PrimaryFlag = get_resource_from_vmm("LocalStorage",vm.get_vm().zoneUuid,vm.get_vm().hostUuid)
	if Host_uuid  and PrimaryFlag == 0:
		vm.migrate(Host_uuid)
		compare(admin_uuid,"migration")
	test_util.test_logger("clean vm instance")
	vm.clean()
	compare(admin_uuid,"clean")

