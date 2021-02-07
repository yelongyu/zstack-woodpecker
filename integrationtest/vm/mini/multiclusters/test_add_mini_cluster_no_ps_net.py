import os

import zstackwoodpecker.operations.cluster_operations as cluster_ops
import zstackwoodpecker.operations.deploy_operations as deploy_ops
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.operations.primarystorage_operations as ps_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header

ip1 = None
ip2 = None
cluster2 = None

tag = ["cluster::migrate::network::cidr::99.99.99.0/24"]


def change_zsn1(host_ip, up=False):
    if up:
        cmd = "ifup zsn1"
    else:
        cmd = "ifdown zsn1"
    test_lib.lib_execute_ssh_cmd(host_ip, "root", "password", cmd)

    return host_ip


def test():
    global ip1, ip2, cluster2
    ips = deploy_ops.get_vm_ip_from_scenariofile(test_lib.scenario_file)
    test_util.test_logger(ips)

    hosts = res_ops.query_resource(res_ops.HOST)
    hosts_ip = [i.managementIp for i in hosts]
    ips.remove(hosts_ip[0])
    ips.remove(hosts_ip[1])

    zone = res_ops.query_resource(res_ops.ZONE)[0]
    l2s = res_ops.query_resource(res_ops.L2_NETWORK)
    mini_ps = res_ops.query_resource(res_ops.PRIMARY_STORAGE)[0]

    ip1 = change_zsn1(ips[0], up=False)
    ip2 = change_zsn1(ips[1], up=False)

    mini_cluster_option = test_util.MiniClusterOption()
    mini_cluster_option.set_name("cluster2")
    mini_cluster_option.set_username("root")
    mini_cluster_option.set_password("password")
    mini_cluster_option.set_sshPort("22")
    mini_cluster_option.set_hypervisor_type("KVM")
    mini_cluster_option.set_zone_uuid(zone.uuid)
    mini_cluster_option.set_host_management_ips(ips[:2])

    cluster2 = cluster_ops.create_mini_cluster(mini_cluster_option)

    for l2 in l2s:
        net_ops.attach_l2(l2.uuid, cluster2.uuid)

    ps_ops.attach_primary_storage(mini_ps.uuid, cluster2.uuid)

    test_util.test_logger("Create Minicluster Passed")

    # create vm
    vm_creation_option = test_util.VmOption()
    image_name = os.environ.get('imageName_s')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    l3_name = "public network"

    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    vm_creation_option.set_l3_uuids([l3_net_uuid])
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_name('test_vm')
    vm_creation_option.set_cluster_uuid(cluster2.uuid)
    vm_creation_option.set_cpu_num(2)
    vm_creation_option.set_memory_size(2 * 1024 * 1024 * 1024)

    vm = test_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    vm.check()
    vm.clean()

    change_zsn1(ip1, up=True)
    change_zsn1(ip2, up=True)

    cluster_ops.delete_cluster(cluster2.uuid)
    test_util.test_logger("Create Minicluster check passed")

    cluster2 = None
    ip1 = None
    ip2 = None


def error_cleanup():
    global ip1, ip2, cluster2
    if ip1:
        change_zsn1(ip1, up=True)
    if ip2:
        change_zsn1(ip2, up=True)
    if cluster2:
        cluster_ops.delete_cluster(cluster2.uuid)


def env_recover():
    global ip1, ip2
    if ip1:
        change_zsn1(ip1, up=True)
    if ip2:
        change_zsn1(ip2, up=True)
    if cluster2:
        cluster_ops.delete_cluster(cluster2.uuid)
