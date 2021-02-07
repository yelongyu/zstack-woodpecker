import zstackwoodpecker.operations.cluster_operations as cluster_ops
import zstackwoodpecker.operations.deploy_operations as deploy_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_util as test_util

ip = None

tag = ["cluster::migrate::network::cidr::99.99.99.0/24"]


def change_password(host_ip, old_password, new_password):
    cmd = "echo -e '%s\n%s' | passwd" % (new_password, new_password)
    test_lib.lib_execute_ssh_cmd(host_ip, "root", old_password, cmd)
    return host_ip


def test():
    global ip
    ips = deploy_ops.get_vm_ip_from_scenariofile(test_lib.scenario_file)
    test_util.test_logger(ips)

    hosts = res_ops.query_resource(res_ops.HOST)
    hosts_ip = [i.managementIp for i in hosts]
    ips.remove(hosts_ip[0])
    ips.remove(hosts_ip[1])

    zone = res_ops.query_resource(res_ops.ZONE)[0]
    l2s = res_ops.query_resource(res_ops.L2_NETWORK)
    mini_ps = res_ops.query_resource(res_ops.PRIMARY_STORAGE)[0]

    ip = change_password(ips[0], "password", "new_password")

    mini_cluster_option = test_util.MiniClusterOption()
    mini_cluster_option.set_name("cluster2")
    mini_cluster_option.set_username("root")
    mini_cluster_option.set_password("password")
    mini_cluster_option.set_sshPort("22")
    mini_cluster_option.set_hypervisor_type("KVM")
    mini_cluster_option.set_zone_uuid(zone.uuid)
    mini_cluster_option.set_host_management_ips(ips[:2])

    try:
        cluster2 = cluster_ops.create_mini_cluster(mini_cluster_option)
    except Exception as e:
        test_util.test_logger(e.message.encode("utf-8"))

    hosts = res_ops.query_resource(res_ops.HOST)
    assert len(hosts) == 2

    test_util.test_logger("Create Minicluster check passed")

    change_password(ip, "new_password", "password")
    ip = None


def error_cleanup():
    global ip
    if ip:
        change_password(ip, "new_password", "password")
    ip = None


def env_recover():
    global ip
    if ip:
        change_password(ip, "new_password", "password")
    ip = None
