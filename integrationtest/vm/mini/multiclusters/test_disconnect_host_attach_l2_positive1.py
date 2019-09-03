import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_util as test_util

l2 = None
disconnect = False
host = None


def test():
    global disconnect, host
    global l2
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

    # create l2
    name = 'mini_network_test'
    test_util.test_dsc('create L2_vlan network mini_l2_network_test')
    zone_uuid = res_ops.query_resource(res_ops.ZONE)[0].uuid
    cluster_uuid = res_ops.query_resource(res_ops.CLUSTER)[0].uuid
    l2 = net_ops.create_l2_vlan('l2_vlan', 'zsn0', zone_uuid, '1998').inventory
    l2_uuid = l2.uuid

    # attach l2 to cluster1
    try:
        net_ops.attach_l2(l2_uuid, cluster2.uuid)
    except Exception as e:
        print e.message.encode("utf-8")
        test_util.test_fail("this action must success but faild")

    cond = res_ops.gen_query_conditions("uuid", "=", l2_uuid)
    l2 = res_ops.query_resource(res_ops.L2_NETWORK, cond)[0]

    assert len(l2.attachedClusterUuids) == 1

    net_ops.delete_l2(l2_uuid)
    l2 = None

    host_ops.update_kvm_host(host.uuid, 'username', "root")
    host_ops.reconnect_host(host.uuid)


def env_recover():
    global host, disconnect, l2
    if disconnect:
        host_ops.update_kvm_host(host.uuid, 'username', "root")
        host_ops.reconnect_host(host.uuid)
        disconnect = False

    if l2:
        net_ops.delete_l2(l2.uuid)



def error_cleanup():
    global host, disconnect, l2
    if disconnect:
        host_ops.update_kvm_host(host.uuid, 'username', "root")
        host_ops.reconnect_host(host.uuid)
        disconnect = False

    if l2:
        net_ops.delete_l2(l2.uuid)