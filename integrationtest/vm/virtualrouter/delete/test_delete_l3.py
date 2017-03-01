'''

@author: quarkonics
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.export_operations as exp_ops
import zstackwoodpecker.operations.net_operations as net_ops
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

curr_deploy_conf = None
l3_name = None
l3 = None
def test():
    global curr_deploy_conf
    global l3_name
    global l3
    curr_deploy_conf = exp_ops.export_zstack_deployment_config(test_lib.deploy_config)
    test_util.test_dsc('Create test vm and delete l3.')
    l3_name = os.environ.get('l3VlanNetworkName1')
    l3 = res_ops.get_resource(res_ops.L3_NETWORK, name = l3_name)[0]
    vm = test_stub.create_vlan_vm(l3_name)
    test_obj_dict.add_vm(vm)
    vm.check()
    net_ops.delete_l3(l3.uuid)
    if len(test_lib.lib_find_vr_by_l3_uuid(l3.uuid)) != 0:
        test_util.test_fail('VR VM should be delete when associated L3 is deleted')

    vm.destroy()
    net_ops.add_l3_resource(curr_deploy_conf, l3_name)

    test_util.test_pass('Create VirtualRouter VM delete l3 Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global curr_deploy_conf
    global l3_name
    global l3
    test_lib.lib_error_cleanup(test_obj_dict)
    l3 = res_ops.get_resource(res_ops.L3_NETWORK, name = l3_name)
    if not l3s:
        try:
            net_ops.add_l3_resource(curr_deploy_conf, l3_name)
        except Exception as e:
            test_util.test_warn('Fail to recover [l3:] %s resource. It will impact later test case.' % l3_name)
            raise e
