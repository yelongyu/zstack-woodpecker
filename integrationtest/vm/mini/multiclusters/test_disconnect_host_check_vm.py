import os

import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header

disconnect, vm1, vm2, host = (False, None, None, None)


def test():
    global disconnect, vm1, vm2, host
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

    # disconnect mn_host1
    host = cluster2_host[0]
    host_ops.update_kvm_host(host.uuid, 'username', "root1")
    try:
        host_ops.reconnect_host(host.uuid)
    except:
        test_util.test_logger("host: [%s] is disconnected" % host.uuid)
    disconnect = True

    delta = 1 * 1024 * 1024 * 1024

    # vm action
    # vm1 action
    vm1.stop()
    vm1.start()
    vm1.destroy()
    vm1.recover()

    root_volume_uuid = test_lib.lib_get_root_volume(vm1.get_vm()).uuid
    current_size = test_lib.lib_get_root_volume(vm1.get_vm()).size
    current_size = current_size + int(delta)
    vol_ops.resize_volume(root_volume_uuid, current_size)
    vm1.start()

    current_size = current_size + int(delta)
    vol_ops.resize_volume(root_volume_uuid, current_size)
    vm1.reboot()

    target_hosts = vm_ops.get_vm_migration_candidate_hosts(vm1.vm.uuid)
    vm1.migrate(target_hosts[0].uuid)
    vm1.reboot()

    vm1.destroy()
    vm1.expunge()

    # vm2 action
    if vm2.get_vm().hostUuid == host.uuid:
        test_util.test_logger("VM state is unknow must migrate vm")
        vm2.migrate(cluster2_host[1].uuid, allowUnknown=True, migrateFromDestination=True)

    vm2.stop()
    vm2.start()
    vm2.destroy()
    vm2.recover()

    root_volume_uuid = test_lib.lib_get_root_volume(vm2.get_vm()).uuid
    current_size = test_lib.lib_get_root_volume(vm2.get_vm()).size
    current_size = current_size + int(delta)
    try:
        vol_ops.resize_volume(root_volume_uuid, current_size)
    except Exception:
        test_util.test_logger("Resize root volume is valid")
    vm2.start()

    current_size = current_size + int(delta)
    try:
        vol_ops.resize_volume(root_volume_uuid, current_size)
    except Exception:
        test_util.test_logger("Resize root volume faild is valid")
    vm2.reboot()

    target_hosts = vm_ops.get_vm_migration_candidate_hosts(vm2.vm.uuid)
    assert len(target_hosts) == 0

    vm2.destroy()
    try:
        vm2.expunge()
    except Exception:
        test_util.test_logger("expunge vm faild is valid")

    host_ops.update_kvm_host(host.uuid, 'username', "root")
    host_ops.reconnect_host(host.uuid)

    vm2.expunge()

    disconnect, vm1, vm2, host = (False, None, None, None)


def error_cleanup():
    global disconnect, vm1, vm2, host
    if disconnect:
        host_ops.update_kvm_host(host.uuid, 'username', "root")
        host_ops.reconnect_host(host.uuid)
        disconnect = False
    if vm1:
        vm1.clean()
    if vm2:
        vm2.clean()

    disconnect, vm1, vm2, host = (False, None, None, None)


def env_recover():
    global disconnect, vm1, vm2, host
    if disconnect:
        host_ops.update_kvm_host(host.uuid, 'username', "root")
        host_ops.reconnect_host(host.uuid)
        disconnect = False
    if vm1:
        vm1.clean()
    if vm2:
        vm2.clean()

    disconnect, vm1, vm2, host = (False, None, None, None)
