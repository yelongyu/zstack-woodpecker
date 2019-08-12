import os

import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import zstackwoodpecker.zstack_test.zstack_test_volume as zstack_vol_header

vm = None
volume1 = None
volume2 = None


def test():
    global vm, volume1, volume2
    # query&get clusters
    cond = res_ops.gen_query_conditions('name', '=', "cluster1")
    cluster1 = res_ops.query_resource(res_ops.CLUSTER, cond)[0]

    cond = res_ops.gen_query_conditions('name', '=', "cluster2")
    cluster2 = res_ops.query_resource(res_ops.CLUSTER, cond)[0]

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
    vm_creation_option.set_memory_size(2 * 1024 * 1024 * 1024)

    vm = test_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    vm.check()

    # create_volume on 2 clusters
    ps = res_ops.query_resource(res_ops.PRIMARY_STORAGE)[0]
    systemtags1 = ["volumeProvisioningStrategy::ThickProvisioning", "capability::virtio-scsi",
                   "miniStorage::clusterUuid::" + cluster1.uuid]
    volume_creation_option = test_util.VolumeOption()
    volume_creation_option.set_name("cluster1_volume")
    volume_creation_option.set_primary_storage_uuid(ps.uuid)
    volume_creation_option.set_system_tags(systemtags1)
    volume_creation_option.set_diskSize(2 * 1024 * 1024 * 1024)
    volume_inv = vol_ops.create_volume_from_diskSize(volume_creation_option)
    volume1 = zstack_vol_header.ZstackTestVolume()
    volume1.create_from(volume_inv.uuid)

    systemtags2 = ["volumeProvisioningStrategy::ThickProvisioning", "capability::virtio-scsi",
                   "miniStorage::clusterUuid::%s" + cluster2.uuid]
    volume_creation_option.set_name("cluster2_volume")
    volume_creation_option.set_system_tags(systemtags2)
    volume_inv = vol_ops.create_volume_from_diskSize(volume_creation_option)
    volume2 = zstack_vol_header.ZstackTestVolume()
    volume2.create_from(volume_inv.uuid)

    # attach cluster1_volume success
    volume1.attach(vm)
    # attach cluster1_volume failure
    try:
        volume2.attach(vm)
    except:
        test_util.test_logger("vm and volume2 is not in the same cluster")

    # check volume attachable volume
    vms = vol_ops.get_data_volume_attachable_vm(volume2.get_volume().uuid)
    assert len(vms) == 0

    # deatch volume
    volume1.detach()

    # get vm attachable vm
    volumes = vm_ops.get_vm_attachable_data_volume(vm.get_vm().uuid)
    assert len(volumes) == 1
    assert volume1.get_volume().uuid == volumes[0].uuid

    vm.clean()
    volume1.clean()
    volume2.clean()


def error_cleanup():
    global vm, volume1, volume2
    vm.clean()
    volume1.clean()
    volume2.clean()


def env_recover():
    global vm, volume1, volume2
    vm.clean()
    volume1.clean()
    volume2.clean()
