import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import time
import os
import random

vm = None

def test():
    global vm
    # query&get clusters
    cond = res_ops.gen_query_conditions('name', '=', "cluster1")
    cluster1 = res_ops.query_resource(res_ops.CLUSTER, cond)[0]

    cond = res_ops.gen_query_conditions('name', '=', "cluster2")
    cluster2 = res_ops.query_resource(res_ops.CLUSTER, cond)[0]

    # query&get hosts
    cond = res_ops.gen_query_conditions('clusterUuid', '=', cluster1.uuid)
    cluster1_host = res_ops.query_resource(res_ops.HOST, cond)

    cond = res_ops.gen_query_conditions('clusterUuid', '=', cluster2.uuid)
    cluster2_host = res_ops.query_resource(res_ops.HOST, cond)

    # create_vm on cluster1
    vm_creation_option = test_util.VmOption()
    image_name = os.environ.get('imageName_s')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    l3_name = os.environ.get('l3VlanNetworkName1')

    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    vm_creation_option.set_l3_uuids([l3_net_uuid])
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_name('test_vm')

    vm_creation_option.set_cluster_uuid(cluster1.uuid)

    vm_creation_option.set_cpu_num(2)
    vm_creation_option.set_memory_size(2*1024*1024*1024)

    vm = test_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    vm.check()

    # stop vm
    vm.stop()
    vm.check()

    # check vm_starting_candidate_clusters_hosts
    result = vm_ops.get_vm_starting_candidate_clusters_hosts(vm.get_vm().uuid)
    clusters = result.clusterInventories
    hosts = result.hostInventories

    assert len(clusters) == 1 and cluster1.uuid == clusters[0].uuid
    assert len(hosts) == 2
    for host in hosts:
        assert host.uuid in [i.uuid for i in cluster1_host]

    vm.clean()

def error_cleanup():
    global vm
    vm.clean()


def env_recover():
    global vm
    vm.clean()