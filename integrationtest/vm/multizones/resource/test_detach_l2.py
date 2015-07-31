'''

New Integration Test for testing detaching l2

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
l3_name1 = os.environ.get('l3VlanNetworkName1')
l3_name2 = os.environ.get('l3VlanNetwork2')
l2_name2 = None
cluster_uuid = None
l2_uuid = None

def check_detach_l2(pre_cluster_uuid, l2_uuid, vm, is_other_cluster):
    l2 = res_ops.get_resource(res_ops.L2_NETWORK, uuid = l2_uuid)[0]

    attached_clusters = l2.attachedClusterUuids

    if pre_cluster_uuid in attached_clusters:
        test_util.test_fail('[cluster:] %s is still in [l2:] %s attached list.'\
                % (pre_cluster_uuid, l2_uuid))

    test_util.test_dsc('start vm again. vm should be started in different cluster, if there has.')
    if attached_clusters :
        if not is_other_cluster:
            test_util.test_fail('There should not be available cluster for [l2:] %s. But catch some.' % l2_uuid)

        vm.start()
        new_cluster_uuid = vm.get_vm().clusterUuid
        if new_cluster_uuid == pre_cluster_uuid : 
            test_util.test_fail('\
            VM start on old [cluster]: %s, which is detached by [l2:] %s ' \
                    % (vm.get_vm().uuid, new_cluster_uuid, l2_uuid))
        vm.check()
    else:
        if is_other_cluster:
            test_util.test_fail('There should be available cluster for [l2:] %s. But did not catch.' % l2_uuid)
        #no cluster is attached with l2. vm will start failure.
        try:
            vm.start()
        except:
            test_util.test_logger('\
Expected: VM start failed, since there is not cluster is attached to [l2]: %s, \
after [cluster:] %s is detached' % (l2_uuid, pre_cluster_uuid))
        else:
            test_util.test_fail('[vm]: %s is Wrongly started up, since there is\
not cluster is attached with [l2]: %s, after previous detaching ops' % \
                (vm.get_vm().uuid, l2_uuid))

def test():
    global cluster_uuid
    global l2_uuid
    vm_creation_option = test_util.VmOption()
    image_name = os.environ.get('imageName_net')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    #pick up l3
    l3_1 = res_ops.get_resource(res_ops.L3_NETWORK, name = l3_name1)[0]
    l3_2 = res_ops.get_resource(res_ops.L3_NETWORK, name = l3_name2)[0]
    
    l2_2 = res_ops.get_resource(res_ops.L2_NETWORK, \
            uuid = l3_2.l2NetworkUuid)[0]

    l2_uuid = l2_2.uuid

    all_attached_clusters = l2_2.attachedClusterUuids
    l2_name2 = l2_2.name

    conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
    instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_name('multizones_basic_vm')
    vm_creation_option.set_l3_uuids([l3_1.uuid, l3_2.uuid])

    cluster1_name = os.environ.get('clusterName2')
    cluster1 = res_ops.get_resource(res_ops.CLUSTER, name = cluster1_name)[0]
    cluster_uuid = cluster1.uuid
    vm_creation_option.set_cluster_uuid(cluster_uuid)

    vm1 = test_lib.lib_create_vm(vm_creation_option)
    test_obj_dict.add_vm(vm1)

    net_ops.detach_l2(l2_uuid, cluster_uuid)
    test_obj_dict.mv_vm(vm1, vm_header.RUNNING, vm_header.STOPPED)
    vm1.update()
    vm1.set_state(vm_header.STOPPED)

    check_detach_l2(cluster_uuid, l2_uuid, vm1, True)
    #for num in range(len(all_attached_clusters)):
    #    curr_cluster_uuid = vm1.get_vm().clusterUuid
    #
    #    test_util.test_dsc('Detach l2_2')
    #    net_ops.detach_l2(l2_uuid, curr_cluster_uuid)
    #
    #    test_obj_dict.mv_vm(vm1, vm_header.RUNNING, vm_header.STOPPED)
    #    vm1.update()
    #    vm1.set_state(vm_header.STOPPED)
    #
    #    vm1.check()
    #
    #    if num != len(all_attached_clusters) - 1:
    #        check_detach_l2(curr_cluster_uuid, l2_uuid, vm1, True)
    #    else:
    #        check_detach_l2(curr_cluster_uuid, l2_uuid, vm1, False)

    #for cluster in all_attached_clusters:
    #    net_ops.attach_l2(l2_uuid, cluster)
    net_ops.attach_l2(l2_uuid, cluster_uuid)

    vm2 = test_lib.lib_create_vm(vm_creation_option)
    test_obj_dict.add_vm(vm2)

    #check vm1 vm2 status.
    vm2.check()

    vm1.destroy()
    vm2.destroy()
    test_util.test_pass('Detach L2 Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global cluster_uuid
    global l2_uuid
    test_lib.lib_error_cleanup(test_obj_dict)
    net_ops.attach_l2(l2_uuid, cluster_uuid)
