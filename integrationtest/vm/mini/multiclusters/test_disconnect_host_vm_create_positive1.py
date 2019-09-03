import os

import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header

vm = None
disconnect = False
host = None


def test():
    global disconnect, host
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

    # disconnect mn_host1
    host = cluster1_host[0]
    host_ops.update_kvm_host(host.uuid, 'username', "root1")
    disconnect = True

    # create_vm on cluster1
    vm_creation_option = test_util.VmOption()
    image_name = os.environ.get('imageName_s')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    l3_name = os.environ.get('l3VlanNetworkName1')

    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    vm_creation_option.set_l3_uuids([l3_net_uuid])
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_name('test_vm')

    vm_creation_option.set_cluster_uuid(cluster2.uuid)

    vm_creation_option.set_cpu_num(2)
    vm_creation_option.set_memory_size(2 * 1024 * 1024 * 1024)

    vm = test_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    try:
        vm.create()
    except Exception as e:
        print e.message.encode("utf-8")
        test_util.test_fail("This case need pass but fail")

    vm.check()
    vm.clean()

    host_ops.update_kvm_host(host.uuid, 'username', "root")
    host_ops.reconnect_host(host.uuid)


def error_cleanup():
    global host, disconnect, vm
    if disconnect:
        host_ops.update_kvm_host(host.uuid, 'username', "root")
        host_ops.reconnect_host(host.uuid)
        disconnect = False

    if vm:
        vm.clean()


def env_recover():
    global host, disconnect, vm
    if disconnect:
        host_ops.update_kvm_host(host.uuid, 'username', "root")
        host_ops.reconnect_host(host.uuid)
        disconnect = False

    if vm:
        vm.clean()
