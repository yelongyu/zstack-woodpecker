'''

New Integration Test for testing deleting l3 when VM has 1 L3

@author: Youyk
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.header.vm as vm_header
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.export_operations as exp_ops
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import time
import os

_config_ = {
        'timeout' : 1200,
        'noparallel' : True
        }

test_obj_dict = test_state.TestStateDict()
host_config = test_util.HostOption()
l3_name1 = os.environ.get('l3VlanNetworkName1')
curr_deploy_conf = None

def test():
    global curr_deploy_conf
    curr_deploy_conf = exp_ops.export_zstack_deployment_config(test_lib.deploy_config)

    vm_creation_option = test_util.VmOption()
    image_name = os.environ.get('imageName_s')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    #pick up l3
    l3_1 = res_ops.get_resource(res_ops.L3_NETWORK, name = l3_name1)[0]

    conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
    instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_name('multizones_basic_vm')
    vm_creation_option.set_l3_uuids([l3_1.uuid])

    vm1 = test_lib.lib_create_vm(vm_creation_option)
    test_obj_dict.add_vm(vm1)

    vm2 = test_lib.lib_create_vm(vm_creation_option)
    test_obj_dict.add_vm(vm2)

    test_util.test_dsc('Delete l3_1')
    net_ops.delete_l3(l3_1.uuid)

    test_obj_dict.mv_vm(vm1, vm_header.RUNNING, vm_header.DESTROYED)
    test_obj_dict.mv_vm(vm2, vm_header.RUNNING, vm_header.DESTROYED)

    vm1.set_state(vm_header.DESTROYED)
    vm2.set_state(vm_header.DESTROYED)

    vm1.check()
    vm2.check()

    net_ops.add_l3_resource(curr_deploy_conf, l3_name = l3_1.name)

    test_lib.lib_robot_cleanup(test_obj_dict)
    test_util.test_pass('Delete L3 Test 2 Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global curr_deploy_conf
    test_lib.lib_error_cleanup(test_obj_dict)
    l3_1 = res_ops.get_resource(res_ops.L3_NETWORK, name = l3_name1)[0]
    if not l3_1:
        try:
            net_ops.add_l3_resource(curr_deploy_conf, l3_name = l3_1.name)
        except Exception as e:
            test_util.test_warn('Fail to recover [l3:] %s resource. It will impact later test case.' % l3_name1)
            raise e
