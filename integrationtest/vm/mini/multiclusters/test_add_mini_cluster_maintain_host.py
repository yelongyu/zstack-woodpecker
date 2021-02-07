import zstackwoodpecker.operations.cluster_operations as cluster_ops
import zstackwoodpecker.operations.deploy_operations as deploy_ops
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.operations.primarystorage_operations as ps_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_util as test_util
import threading
import time

cluster2 = None

tag = ["cluster::migrate::network::cidr::99.99.99.0/24"]


def maintain_host(host_uuid):
    host_ops.change_host_state(host_uuid, state="maintain")


def test():
    global ip1, ip2, cluster2
    ips = deploy_ops.get_vm_ip_from_scenariofile(test_lib.scenario_file)
    test_util.test_logger(ips)

    old_hosts = res_ops.query_resource(res_ops.HOST)
    hosts_ip = [i.managementIp for i in old_hosts]
    ips.remove(hosts_ip[0])
    ips.remove(hosts_ip[1])

    zone = res_ops.query_resource(res_ops.ZONE)[0]
    l2s = res_ops.query_resource(res_ops.L2_NETWORK)
    mini_ps = res_ops.query_resource(res_ops.PRIMARY_STORAGE)[0]

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

    # reconnect hosts
    hosts = res_ops.query_resource(res_ops.HOST)

    thread_list = []
    for host in hosts:
        t = threading.Thread(target=maintain_host, args=(host.uuid,))
        thread_list.append(t)
        t.start()

    for t in thread_list:
        t.join()

    cluster_ops.delete_cluster(cluster2.uuid)
    test_util.test_logger("Create Minicluster check passed")

    for host in old_hosts:
        host_ops.change_host_state(host.uuid, state="enable")
        wait_hosts_connected(host.uuid)

    cluster2 = None


def error_cleanup():
    global cluster2
    if cluster2:
        cluster_ops.delete_cluster(cluster2.uuid)


def env_recover():
    global cluster2
    if cluster2:
        cluster_ops.delete_cluster(cluster2.uuid)


def wait_hosts_connected(host_uuid):
    while True:
        time.sleep(5)
        cond = res_ops.gen_query_conditions("uuid", "=", host_uuid)
        host = res_ops.query_resource(res_ops.HOST, cond)[0]
        if host.status == "Connected":
            break
        time.sleep(5)