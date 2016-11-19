'''
This case can not execute parallelly
@author: MengLai 
'''
import os
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.account_operations as account_operations
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.deploy_operations as dep_ops
import zstackwoodpecker.operations.export_operations as exp_ops
import zstackwoodpecker.operations.account_operations as acc_ops

_config_ = {
        'timeout' : 1000,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    global deploy_conf
    global vm_inv
    global vm

    test_util.test_dsc('Test Delete VR Offering and Teboot Normal VM')

    vm = test_stub.create_basic_vm()
    test_obj_dict.add_vm(vm)

    vm_inv = vm.get_vm()
    vm_ip = vm_inv.vmNics[0].ip
  
    vm.check()
    
    test_util.test_dsc('Record current virtual router offering information')
    deploy_conf = exp_ops.export_zstack_deployment_config(test_lib.deploy_config)
    cond = res_ops.gen_query_conditions('zone.vmInstance.uuid', '=', vm_inv.uuid)
    vr_offering_uuid = res_ops.query_resource(res_ops.VR_OFFERING, cond)[0].uuid

    test_util.test_dsc('Delete VR-RM and VR-Offering')
    cond = res_ops.gen_query_conditions('zone.vmInstance.uuid', '=', vm_inv.uuid)
    vr_vm_uuid = res_ops.query_resource(res_ops.VIRTUALROUTER_VM, cond)[0].uuid

    vm_ops.destroy_vm(vr_vm_uuid)
    vm_ops.delete_instance_offering(vr_offering_uuid)

    test_util.test_dsc('Create new VR-Offering, same as the former one, stop and start VM')
    session_uuid = acc_ops.login_as_admin()
    dep_ops.add_virtual_router(deploy_conf, session_uuid) 
    vm.reboot()

    vm.destroy()
    test_obj_dict.rm_vm(vm)

    test_util.test_pass('Delete VR Offering and reboot normal VM: SUCCESS')

#Will be called only if exception happens in test().
def error_cleanup():
    global deploy_conf
    global vm_inv
    global vm

    cond = res_ops.gen_query_conditions('zone.vmInstance.uuid', '=', vm_inv.uuid)
    if len(res_ops.query_resource(res_ops.VR_OFFERING, cond)) == 0:
        session_uuid = acc_ops.login_as_admin()
        dep_ops.add_virtual_router(deploy_conf, session_uuid)
        vm.reboot()

    test_lib.lib_error_cleanup(test_obj_dict)
