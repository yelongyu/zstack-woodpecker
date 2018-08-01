'''
New Test For VM Operations

@author: Glody 
'''
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.account_operations as acc_ops
import apibinding.api_actions as api_actions
import apibinding.inventory as inventory
import threading
import time
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

case_flavor = dict(vm_100=             	dict(vm_num=100),
                   vm_1000=                    dict(vm_num=1000),
                   vm_10000=              	dict(vm_num=10000),
                   )
  
def create_vm(name, image_uuid, host_uuid, instance_offering_uuid, l3_uuid, session_uuid=None):
    vm_creation_option = test_util.VmOption()
    vm_creation_option.set_name(name)
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_l3_uuids([l3_uuid])
    vm_creation_option.set_host_uuid(host_uuid)
    if session_uuid:
        vm_creation_option.set_session_uuid(session_uuid)
    test_stub.create_vm(vm_creation_option)

def test():
    flavor = case_flavor[os.environ.get('CASE_FLAVOR')]
    num = flavor['vm_num']
    imageUuid = res_ops.query_resource_fields(res_ops.IMAGE)[0].uuid
    hostUuid = ''
    hostName = ''
    instanceOfferingUuid = res_ops.query_resource_fields(res_ops.INSTANCE_OFFERING)[0].uuid
    l3NetworkUuids = res_ops.query_resource_fields(res_ops.L3_NETWORK)[0].uuid
    hosts = res_ops.query_resource_fields(res_ops.HOST)
    counter = 0
    for i in range(0, 500):
        hostUuid = hosts[i].uuid
        hostName = hosts[i].name
        for j in range(0, 20):
            counter += 1
            if counter > num:
                test_util.test_pass("Create %s vms finished" %num)
            vm_name = 'vm-'+str(j)+'-on-host-'+hostName
            thread = threading.Thread(target=create_vm, args=(vm_name, imageUuid, hostUuid, instanceOfferingUuid, l3NetworkUuids))
            while threading.active_count() > 100:
                time.sleep(5)
            thread.start()
    test_util.test_fail("Fail to create vms")
def error_cleanup():
    pass
