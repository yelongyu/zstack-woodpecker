import os

import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import zstackwoodpecker.zstack_test.zstack_test_volume as zstack_vol_header

disconnect, volume1, volume2, vm1, vm2, host = (False, None, None, None, None, None)


def test():
    global disconnect, volume1, volume2, vm1, vm2, host
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

    # create vm on 2 cluster
    vm_creation_option = test_util.VmOption()
    image_name = os.environ.get('imageName_s')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    l3_name = os.environ.get('l3VlanNetworkName1')

    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    vm_creation_option.set_l3_uuids([l3_net_uuid])
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_name('test_vm1')
    vm_creation_option.set_cluster_uuid(cluster1.uuid)
    vm_creation_option.set_cpu_num(2)
    vm_creation_option.set_memory_size(2 * 1024 * 1024 * 1024)

    vm1 = test_vm_header.ZstackTestVm()
    vm1.set_creation_option(vm_creation_option)
    vm1.create()

    vm_creation_option.set_name('test_vm2')
    vm_creation_option.set_cluster_uuid(cluster2.uuid)

    vm2 = test_vm_header.ZstackTestVm()
    vm2.set_creation_option(vm_creation_option)
    vm2.create()

    # create_volume on 2 cluster
    ps = res_ops.query_resource(res_ops.PRIMARY_STORAGE)[0]
    systemtags1 = ["volumeProvisioningStrategy::ThickProvisioning", "capability::virtio-scsi",
                   "miniStorage::clusterUuid::%s" % cluster1.uuid]
    volume_creation_option = test_util.VolumeOption()
    volume_creation_option.set_name("cluster1_volume")
    volume_creation_option.set_primary_storage_uuid(ps.uuid)
    volume_creation_option.set_system_tags(systemtags1)
    volume_creation_option.set_diskSize(2 * 1024 * 1024 * 1024)
    volume_inv = vol_ops.create_volume_from_diskSize(volume_creation_option)
    volume1 = zstack_vol_header.ZstackTestVolume()
    volume1.create_from(volume_inv.uuid)

    systemtags1 = ["volumeProvisioningStrategy::ThickProvisioning", "capability::virtio-scsi",
                   "miniStorage::clusterUuid::%s" % cluster2.uuid]
    volume_creation_option.set_name("cluster2_volume")
    volume_creation_option.set_primary_storage_uuid(ps.uuid)
    volume_creation_option.set_system_tags(systemtags1)

    volume_inv = vol_ops.create_volume_from_diskSize(volume_creation_option)
    volume2 = zstack_vol_header.ZstackTestVolume()
    volume2.create_from(volume_inv.uuid)

    # attach vm
    volume1.attach(vm1)
    volume2.attach(vm2)

    # disconnect mn_host1
    host = cluster2_host[0]
    host_ops.update_kvm_host(host.uuid, 'username', "root1")
    try:
        host_ops.reconnect_host(host.uuid)
    except:
        test_util.test_logger("host: [%s] is disconnected" % host.uuid)
    disconnect = True

    if vm2.get_vm().hostUuid == host.uuid:
        test_util.test_logger("VM state is unknow must migrate vm")
        vm2.migrate(cluster2_host[1].uuid, allowUnknown=True, migrateFromDestination=True)

    volume2.detach()
    volume2.delete()
    volume2.recover()

    delta = 1 * 1024 * 1024 * 1024
    current_size = volume2.get_volume().size
    current_size = current_size + int(delta)
    try:
        vol_ops.resize_data_volume(volume2.get_volume().uuid, current_size)
    except Exception:
        test_util.test_logger("Resize root volume is valid")

    volume2.update()
    volume2.update_volume()

    volume2.attach(vm2)
    current_size = current_size + int(delta)
    try:
        vol_ops.resize_data_volume(volume2.get_volume().uuid, current_size)
    except Exception:
        test_util.test_logger("Resize volume is valid")
    volume2.update()
    volume2.update_volume()

    volume2.delete()
    try:
        volume2.expunge()
    except Exception:
        test_util.test_logger("expunge volume faild is valid")

    volume1.detach()
    volume1.delete()
    volume1.recover()

    current_size = volume1.get_volume().size
    current_size = current_size + int(delta)
    vol_ops.resize_data_volume(volume1.get_volume().uuid, current_size)
    volume1.update()
    volume1.update_volume()

    volume1.attach(vm1)
    current_size = current_size + int(delta)
    vol_ops.resize_data_volume(volume1.get_volume().uuid, current_size)
    volume1.update()
    volume1.update_volume()

    volume1.delete()
    volume1.expunge()

    vm1.clean()

    host_ops.update_kvm_host(host.uuid, 'username', "root")
    host_ops.reconnect_host(host.uuid)

    volume2.expunge()
    vm2.clean()

    disconnect, volume1, volume2, vm1, vm2, host = (True, None, None, None, None, None)


def error_cleanup():
    global disconnect, volume1, volume2, vm1, vm2, host
    if disconnect:
        host_ops.update_kvm_host(host.uuid, 'username', "root")
        host_ops.reconnect_host(host.uuid)
        disconnect = False

    if volume1:
        volume1.clean()
    if volume2:
        volume2.clean()
    if vm1:
        vm1.clean()
    if vm2:
        vm2.clean()
    disconnect, volume1, volume2, vm1, vm2, host = (False, None, None, None, None, None)


def env_recover():
    global disconnect, volume1, volume2, vm1, vm2, host
    if disconnect:
        host_ops.update_kvm_host(host.uuid, 'username', "root")
        host_ops.reconnect_host(host.uuid)
        disconnect = False

    if volume1:
        volume1.clean()
    if volume2:
        volume2.clean()
    if vm1:
        vm1.clean()
    if vm2:
        vm2.clean()
    disconnect, volume1, volume2, vm1, vm2, host = (False, None, None, None, None, None)
