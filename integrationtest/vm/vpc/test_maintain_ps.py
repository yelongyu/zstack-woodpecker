'''
@author: chenyuan.xu
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.primarystorage_operations as ps_ops
import zstackwoodpecker.operations.ha_operations as ha_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import time
import random


test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()


def test():

    test_util.test_dsc("create vpc vrouter")

    vr = test_stub.create_vpc_vrouter()

    test_util.test_dsc("attach vpc l3 to vpc vrouter")
    test_stub.attach_l3_to_vpc_vr(vr, test_stub.L3_SYSTEM_NAME_LIST)

    test_util.test_dsc("Create one neverstop vm in random L3")
    vm = test_stub.create_vm_with_random_offering(vm_name='vpc_vm1', l3_name=random.choice(test_stub.L3_SYSTEM_NAME_LIST))
    test_obj_dict.add_vm(vm)
    vm.check()

    ps_list = res_ops.query_resource(res_ops.PRIMARY_STORAGE)
    for ps in ps_list:
        ps_uuid = ps.uuid
        ps_ops.change_primary_storage_state(ps_uuid, 'maintain')
    
    time.sleep(10)
    cond = res_ops.gen_query_conditions('uuid', '=', vr.inv.uuid)
    vr = res_ops.query_resource(res_ops.VM_INSTANCE,cond)[0]
    vm.update()
    assert vr.state == 'Stopped'
    assert vm.vm.state == 'Stopped'
 
    for ps in ps_list:
        ps_ops.change_primary_storage_state(ps_uuid, 'enable')

    test_stub.ensure_hosts_connected(120)
    test_stub.ensure_pss_connected()
    vm.start()
    vr = res_ops.query_resource(res_ops.VM_INSTANCE,cond)[0]
    assert vr.state == 'Running'

    ha_ops.set_vm_instance_ha_level(vm.get_vm().uuid, "NeverStop")
    for ps in ps_list:
        ps_ops.change_primary_storage_state(ps_uuid, 'maintain')   
 
    time.sleep(20)
    vm.update()
    vr = res_ops.query_resource(res_ops.VM_INSTANCE,cond)[0]
    assert vr.state == 'Stopped'
    assert vm.vm.state == 'Stopped'

    for ps in ps_list:
        ps_ops.change_primary_storage_state(ps_uuid, 'enable')

    test_stub.ensure_pss_connected()
    
    for i in range(5):
        vm.update()
        print vm.vm.state
        if vm.vm.state == 'Running':
            break
        else:
           time.sleep(60)
    assert vm.vm.state == 'Running' 
    vr = res_ops.query_resource(res_ops.VM_INSTANCE,cond)[0]
    assert vr.state == 'Running'
    
    
    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_vrouter()


def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_vrouter()
    for ps in ps_list:
        if ps.state == 'maintain':
            ps_ops.change_primary_storage_state(ps.uuid, "enable")


