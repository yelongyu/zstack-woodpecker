'''

New Integration Test for creating KVM VM.

@author: quarkonics
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import time
import os
_config_ = {
        'timeout' : 600,
        'noparallel' : False
        }

vm = None
l2_net_uuid = None
cluster_uuid = None

def test():
    global l2_net_uuid
    global cluster_uuid
    global vm
    cluster1 = res_ops.get_resource(res_ops.CLUSTER)[0]
    cluster2 = res_ops.get_resource(res_ops.CLUSTER)[1]
    vm_creation_option = test_util.VmOption()
    image_name = os.environ.get('imageName_s')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    l3_name = os.environ.get('l3VlanNetworkName1')

    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    l2_net_uuid = test_lib.lib_get_l3_by_name(l3_name).l2NetworkUuid
    l2_net_type = res_ops.get_resource(res_ops.L2_NETWORK, uuid=l2_net_uuid)[0].type

    test_util.test_logger("l2_network.type@@:%s" %(l2_net_type))
    if l2_net_type == "VxlanNetwork":
        test_util.test_skip("Vxlan network not support detach l2 network, therefore, skip the test")

    conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
    instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid
    vm_creation_option.set_l3_uuids([l3_net_uuid])
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_cluster_uuid(cluster1.uuid)
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_name('multicluster_basic_vm')
    vm = test_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()

    vm2 = test_vm_header.ZstackTestVm()
    vm_creation_option.set_cluster_uuid(cluster2.uuid)
    vm2.set_creation_option(vm_creation_option)
    vm2.create()
    vrs = test_lib.lib_find_vr_by_l3_uuid(l3_net_uuid)
    if len(vrs) == 0:
        test_util.test_skip("skip the test for non vr")
    vr = vrs[0]
    cluster_uuid = vr.clusterUuid
    net_ops.detach_l2(l2_net_uuid, cluster_uuid)
    vr = test_lib.lib_find_vr_by_l3_uuid(l3_net_uuid)[0]
    if vr.clusterUuid == cluster_uuid:
        test_util.test_logger('vr is expected to migrate to another cluster')
    vm.destroy()
    vm2.destroy()
    net_ops.attach_l2(l2_net_uuid, cluster_uuid)
    test_util.test_pass('Create detach l2 from clsuter vr migrate Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global l2_net_uuid
    global cluster_uuid

    try:
        net_ops.attach_l2(l2_net_uuid, cluster_uuid)
    except:
        pass
    #time.sleep(5)
    global vm
    if vm:
        try:
            vm.destroy()
        except:
            pass
    global vm2
    if vm2:
        try:
            vm2.destroy()
        except:
            pass
