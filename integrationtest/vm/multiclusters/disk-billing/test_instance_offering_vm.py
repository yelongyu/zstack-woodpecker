# -*- coding: UTF-8 -*-
'''
New Test For Instance Offering with SystemTags
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
import json
import time
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
vm = None
billing_resource = 'rootvolume'
offset_unit_dict=['sec','min','hou','day','week','month','year']
time_unit_dict=['s','m','h','d','w','mon']
resource_unit_dict={"M":1024 * float(1024), "G":1024**2 * float(1024), "T":1024**3 * float(1024)}

#create instance offering with systemTags
ps_uuid = res_ops.query_resource_fields(res_ops.CEPH_PRIMARY_STORAGE)[0].uuid
root_pool_name = 'test-pool-Root-1-' + ps_uuid
instance_offering_opt = test_util.InstanceOfferingOption()
instance_offering_opt.set_cpuNum(2)
instance_offering_opt.set_memorySize(1073741824)
instance_offering_opt.set_name('systemTags-test')
instance_offering_systemtags_json = json.dumps({"allocate": {"primaryStorage": {"type": "ceph", "uuid": ps_uuid, "poolNames": [root_pool_name]}}, "priceUserConfig": {"rootVolume": {"priceKeyName": "highSpeedDisk"}}, "displayAttribute": {"rootVolume": {"云盘类型": "普通云盘"}}})
instance_offering_opt.set_system_tags(["instanceOfferingUserConfig::%s" % instance_offering_systemtags_json,])
instance_offering_uuid = vm_ops.create_instance_offering(instance_offering_opt).uuid

def test():
        #1.test: create vm
	test_util.test_logger("1.create vm instance")        
	global vm1
	vm1 = test_lib.create_vm_billing("vm_create_test", test_lib.set_vm_resource()[0], None,\
						instance_offering_uuid, test_lib.set_vm_resource()[2])
	#check
	cond = res_ops.gen_query_conditions('uuid', '=', vm1.vm.uuid)
	vm1_query_result =  res_ops.query_resource_fields(res_ops.VM_INSTANCE, cond)
	if not vm1_query_result:
		test_util.test_fail("fail: create vm wtih instance offering %s" % instance_offering_uuid)

        #2.test: change vm instance offering
        test_util.test_logger("2.create vm instacne")
        global vm2
	vm2 = test_lib.create_vm_billing("vm_change_instanceoffering_test", test_lib.set_vm_resource()[0], None,\
                                                test_lib.set_vm_resource()[1], test_lib.set_vm_resource()[2])
	vm2.stop()
	vm2.change_instance_offering(instance_offering_uuid)
	#check
	if vm2.changed_instance_offering_uuid != instance_offering_uuid:
		test_util.test_fail("fail: change vm %s instance offering" % vm2.vm.uuid)
	test_util.test_pass("instance offering with systemTags test pass")

def error_cleanup():
	return
	global vm1
	if vm1:
		vm1.clean()
	global vm2
	if vm2:
		vm2.clean()

def env_recover():
	return
	global vm1
	if vm1:
		vm1.clean()
	global vm2
	if vm2:
		vm2.clean()
