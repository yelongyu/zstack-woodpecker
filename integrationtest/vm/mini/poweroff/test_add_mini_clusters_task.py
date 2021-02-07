import zstackwoodpecker.operations.cluster_operations as cluster_ops
import zstackwoodpecker.operations.deploy_operations as deploy_ops
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.operations.primarystorage_operations as ps_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.host_operations as host_ops
import time
import os
import random
import threading
import Queue

clusters = []

def create_mini_cluster_parallel(mini_cluster_option, queue):
    cluster = cluster_ops.create_mini_cluster(mini_cluster_option)
    queue.put(cluster)

def test():
    global clusters
    threads = []
    q = Queue.Queue()
    ips = deploy_ops.get_vm_ip_from_scenariofile(test_lib.scenario_file)
    test_util.test_logger(ips)

    _hosts = res_ops.query_resource(res_ops.HOST)
    hosts_ip = [i.managementIp for i in _hosts]
    ips.remove(hosts_ip[0])
    ips.remove(hosts_ip[1])

    zone = res_ops.query_resource(res_ops.ZONE)[0]
    l2s = res_ops.query_resource(res_ops.L2_NETWORK)
    mini_ps = res_ops.query_resource(res_ops.PRIMARY_STORAGE)[0]

    mini_cluster_option_1 = test_util.MiniClusterOption()
    mini_cluster_option_1.set_name("cluster2")
    mini_cluster_option_1.set_username("root")
    mini_cluster_option_1.set_password("password")
    mini_cluster_option_1.set_sshPort("22")
    mini_cluster_option_1.set_hypervisor_type("KVM")
    mini_cluster_option_1.set_zone_uuid(zone.uuid)
    mini_cluster_option_1.set_host_management_ips(ips[:2])
    t1 = threading.Thread(target=create_mini_cluster_parallel, args=(mini_cluster_option_1, q))
    threads.append(t1)

    mini_cluster_option_2 = test_util.MiniClusterOption()
    mini_cluster_option_2.set_name("cluster3")
    mini_cluster_option_2.set_username("root")
    mini_cluster_option_2.set_password("password")
    mini_cluster_option_2.set_sshPort("22")
    mini_cluster_option_2.set_hypervisor_type("KVM")
    mini_cluster_option_2.set_zone_uuid(zone.uuid)
    mini_cluster_option_2.set_host_management_ips(ips[2:4])

    t2 = threading.Thread(target=create_mini_cluster_parallel, args=(mini_cluster_option_2, q))
    threads.append(t2)

    for i in range(2):
        threads[i].start()

    for i in range(1, 60):
        hosts = test_lib.lib_find_hosts_by_status("Connected")
        for host in hosts:
            tasks = host_ops.get_host_task(host.uuid.split(' '))
            for k,v in tasks.items():
                if v['runningTask']:
                    for rtask in v['runningTask']:
                        if 'apiName' in rtask:
                            if rtask['apiName'] == 'org.zstack.header.cluster.APICreateMiniClusterMsg':
                                test_util.test_fail('%s is found running on host %s with Ip %s, It is failed as it is not expected' % (rtask['apiName'], host.uuid, host.managementIp))
                            else:
                                test_util.test_logger('task %s found running on host %s with Ip %s, but it is not APICreateMiniClusterMsg' % (rtask['apiName'], host.uuid, host.managementIp))

        test_util.test_logger('No task found at Iteration %s' % str(i))
        time.sleep(1)

    for i in range(2):
        threads[i].join()

    while True:
        if q.empty():
            break
        else:
            clusters.append(q.get())

    for l2 in l2s:
        net_ops.attach_l2(l2.uuid, clusters[0].uuid)
        net_ops.attach_l2(l2.uuid, clusters[1].uuid)

    for cluster in clusters:
        ps_ops.attach_primary_storage(mini_ps.uuid, cluster.uuid)

    for cluster in clusters:
        thread = threading.Thread(target=cluster_ops.delete_cluster, args=(cluster.uuid,))
        thread.start()

    for i in range(1, 10):
        for host in _hosts:
            tasks = host_ops.get_host_task(host.uuid.split(' '))
            for k,v in tasks.items():
                if v['runningTask']:
                    for rtask in v['runningTask']:
                        if 'apiName' in rtask:
                            if rtask['apiName'] == 'org.zstack.header.cluster.APIDeleteClusterMsg':
                                test_util.test_fail('%s is found running on host %s with Ip %s, but it is expected not found on the host which is not the one being deleted' % (rtask['apiName'], host.uuid, host.managementIp))
                            else:
                                test_util.test_logger('task %s found running on host %s with Ip %s, but it is not APIDeleteClusterMsg' % (rtask['apiName'], host.uuid, host.managementIp))

        test_util.test_logger('No task found at Iteration %s' % str(i))
        time.sleep(1)

    test_util.test_pass('APICreateMiniClusterMsg and APIDeleteClusterMsg are passed with GetHostTask')

    clusters = []

def error_cleanup():
    global clusters
    if clusters:
        for cluster in clusters:
            cluster_ops.delete_cluster(cluster.uuid)
        clusters = []

def env_recover():
    global clusters
    if clusters:
        for cluster in clusters:
            cluster_ops.delete_cluster(cluster.uuid)
        clusters = []
