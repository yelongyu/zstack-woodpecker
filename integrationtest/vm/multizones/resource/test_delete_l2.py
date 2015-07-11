'''

New Integration Test for testing deleting l2

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
l3_name2 = os.environ.get('l3VlanNetwork2')
l2_name2 = None
curr_deploy_conf = None

def test():
    global curr_deploy_conf
    global l2_name2
    curr_deploy_conf = exp_ops.export_zstack_deployment_config(test_lib.deploy_config)

    vm_creation_option = test_util.VmOption()
    image_name = os.environ.get('imageName_s')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    #pick up l3
    l3_1 = res_ops.get_resource(res_ops.L3_NETWORK, name = l3_name1)[0]
    l3_2 = res_ops.get_resource(res_ops.L3_NETWORK, name = l3_name2)[0]
    
    l2_2 = res_ops.get_resource(res_ops.L2_NETWORK, \
            uuid = l3_2.l2NetworkUuid)[0]
    l2_name2 = l2_2.name

    conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
    instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_name('multizones_basic_vm')
    vm_creation_option.set_l3_uuids([l3_1.uuid, l3_2.uuid])
    cluster1_name = os.environ.get('clusterName2')
    cluster1 = res_ops.get_resource(res_ops.CLUSTER, name = cluster1_name)[0]
    vm_creation_option.set_cluster_uuid(cluster1.uuid)

    vm1 = test_lib.lib_create_vm(vm_creation_option)
    test_obj_dict.add_vm(vm1)

    test_util.test_dsc('Delete l2_2')
    net_ops.delete_l2(l2_2.uuid)

    test_obj_dict.mv_vm(vm1, vm_header.RUNNING, vm_header.STOPPED)
    vm1.update()
    vm1.set_state(vm_header.STOPPED)

    vm1.check()

    test_util.test_dsc('start vm again. vm should remove the deleted l2')
    vm1.start()

    #add l2 resource will also add l3 resource
    net_ops.add_l2_resource(curr_deploy_conf, l2_name = l2_name2)

    #update l3_2, since it is readded.
    l3_2 = res_ops.get_resource(res_ops.L3_NETWORK, name = l3_name2)[0]
    vm_creation_option.set_l3_uuids([l3_1.uuid, l3_2.uuid])

    vm2 = test_lib.lib_create_vm(vm_creation_option)
    test_obj_dict.add_vm(vm2)

    #check vm1 vm2 status.
    vm1.check()

    if not len(vm1.get_vm().vmNics) == 1:
        test_util.test_fail('vm1 vmNics still have L3: %s, even if it is deleted' % l3_2.uuid)

    vm2.check()

    test_lib.lib_robot_cleanup(test_obj_dict)
    test_util.test_pass('Delete L2 Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global curr_deploy_conf
    global l2_name2
    test_lib.lib_error_cleanup(test_obj_dict)
    l3s = res_ops.get_resource(res_ops.L3_NETWORK, name = l3_name2)
    if not l3s:
        try:
            net_ops.add_l2_resource(curr_deploy_conf, l2_name = l2_name2)
        except Exception as e:
            test_util.test_warn('Fail to recover [l2:] %s resource. It will impact later test case.' % l2_name2)
            raise e
