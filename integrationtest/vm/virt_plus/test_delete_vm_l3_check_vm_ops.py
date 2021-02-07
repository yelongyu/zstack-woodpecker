'''
New Integration Test for deleting vm network and check vm ops.
@author: SyZhao
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import zstackwoodpecker.operations.export_operations as exp_ops
import zstackwoodpecker.header.vm as vm_header
import os


test_stub = test_lib.lib_get_specific_stub()
test_obj_dict = test_state.TestStateDict()
curr_deploy_conf = None
l3_name = None
l3 = None

def test():
    global curr_deploy_conf
    global test_obj_dict
    global l3_name
    global l3
    curr_deploy_conf = exp_ops.export_zstack_deployment_config(test_lib.deploy_config)
    delete_policy = test_lib.lib_set_delete_policy('vm', 'Delay')
    l3_name = os.environ.get('l3VlanNetworkName1')
    l3 = res_ops.get_resource(res_ops.L3_NETWORK, name = l3_name)[0]
    vm = test_stub.create_vlan_vm(l3_name)
    vm.check()
    test_obj_dict.add_vm(vm)
    net_ops.delete_l3(l3.uuid)
    if test_lib.lib_get_l3_by_uuid(l3.uuid):
        test_util.test_fail('l3 should not be found when associated L3 is deleted')
    #vm_nic_uuid = vm.vm.vmNics[0].uuid
    #net_ops.detach_l3(vm_nic_uuid)

    vm.destroy()
    vm.set_state(vm_header.DESTROYED)
    vm.check()

    vm.recover()
    vm.set_state(vm_header.STOPPED)
    vm.check()

    test_lib.lib_set_delete_policy('vm', delete_policy)

    try:
        vm.start()
    except Exception, e:
        #if "please attach a nic and try again" in str(e):
        test_util.test_pass('test detach l3 check vm passed.')

    test_util.test_fail("test delete l3 check vm status is not as expected, expected should be not started with error message have not nic.")


def env_recover():
    global curr_deploy_conf
    global test_obj_dict
    global l3_name
    test_lib.lib_error_cleanup(test_obj_dict)
    net_ops.add_l3_resource(curr_deploy_conf, l3_name)


#Will be called only if exception happens in test().
def error_cleanup():
    global curr_deploy_conf
    global l3_name
    test_lib.lib_error_cleanup(test_obj_dict)
    l3 = res_ops.get_resource(res_ops.L3_NETWORK, name = l3_name)
    if not l3:
        try:
            net_ops.add_l3_resource(curr_deploy_conf, l3_name)
        except Exception as e:
            test_util.test_warn('Fail to recover [l3:] %s resource. It will impact later test case.' % l3_name)
            raise e

