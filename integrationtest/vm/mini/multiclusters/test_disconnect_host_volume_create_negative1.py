import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.test_util as test_util

volume = None
disconnect = False
host = None


def test():
    global disconnect, volume, host
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

    # create_volume on 2 clusters
    ps = res_ops.query_resource(res_ops.PRIMARY_STORAGE)[0]
    systemtags1 = ["volumeProvisioningStrategy::ThickProvisioning", "capability::virtio-scsi",
                   "miniStorage::clusterUuid::%s" % cluster1.uuid]
    volume_creation_option = test_util.VolumeOption()
    volume_creation_option.set_name("cluster1_volume")
    volume_creation_option.set_primary_storage_uuid(ps.uuid)
    volume_creation_option.set_system_tags(systemtags1)
    volume_creation_option.set_diskSize(2 * 1024 * 1024 * 1024)
    try:
        volume_inv = vol_ops.create_volume_from_diskSize(volume_creation_option)
    except Exception as e:
        host_ops.update_kvm_host(host.uuid, 'username', "root")
        host_ops.reconnect_host(host.uuid)
        print e.message.encode("utf-8")


def error_cleanup():
    global host, disconnect
    if disconnect:
        host_ops.update_kvm_host(host.uuid, 'username', "root")
        host_ops.reconnect_host(host.uuid)
        disconnect = False


def env_recover():
    global host, disconnect
    if disconnect:
        host_ops.update_kvm_host(host.uuid, 'username', "root")
        host_ops.reconnect_host(host.uuid)
        disconnect = False
