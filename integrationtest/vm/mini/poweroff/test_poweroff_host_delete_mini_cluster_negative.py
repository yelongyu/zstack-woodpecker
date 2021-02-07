'''
Integration test for testing power off mini hosts.
#1.operations & power off random hosts
#2.start hosts
#3.duplicated operation
@author: zhaohao.chen
'''
import apibinding.inventory as inventory
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import zstackwoodpecker.zstack_test.zstack_test_volume as test_volume_header
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.operations.scenario_operations as sce_ops
import zstackwoodpecker.operations.cluster_operations as cluster_ops
import zstackwoodpecker.operations.deploy_operations as deploy_ops
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.operations.primarystorage_operations as ps_ops
import time
import os
import random
import threading
import hashlib
import random

clusters = []
MN_IP = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].hostName
admin_password = hashlib.sha512('password').hexdigest()
zstack_management_ip = os.environ.get('zstackManagementIp')
test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def recover_hosts(host_uuids, host_ips, wait_time):
    for ip in host_ips:
        cond = res_ops.gen_query_conditions('vmNics.ip', '=', ip)
        vm = sce_ops.query_resource(zstack_management_ip, res_ops.VM_INSTANCE, cond).inventories[0]
        if vm.state != 'Stopped':
            test_util.test_fail("Fail to power off host:{}".format(vm.uuid))
        sce_ops.start_vm(zstack_management_ip, vm.uuid)
    time.sleep(wait_time)#wait MN
    for uuid in host_uuids:
        host_ops.reconnect_host(uuid)

def operations_shutdown(shutdown_thread, host_uuids, host_ips, wait_time, operation_thread=None):
    shutdown_thread.start()
    time.sleep(120)
    if operation_thread:
        fail_flag = 1
        timeout = 180
        operation_thread.start()
        while timeout:
            if operation_thread.exitcode:
                test_util.test_logger('@@Operation failed because:\n %s' % operation_thread.exc_traceback)
                fail_flag = 0
                break
            else:
                time.sleep(1)
                timeout -= 1
        if fail_flag:
            test_util.test_fail("@@Operation successed@@")
            shutdown_thread.join(0.1)
    shutdown_thread.join()
    time.sleep(180)
    recover_hosts(host_uuids, host_ips, wait_time) 
    
def test():
    global test_obj_dict
    global clusters
    wait_time = 120
    round = 2 
    test_util.test_logger("@@:mnip:{}".format(zstack_management_ip))
    cond = res_ops.gen_query_conditions('managementIp', '=', MN_IP)
    MN_HOST = res_ops.query_resource(res_ops.HOST, cond)[0]
    cluster_uuid = MN_HOST.clusterUuid
    #add mini clusters
    ips = deploy_ops.get_vm_ip_from_scenariofile(test_lib.scenario_file)
    test_util.test_logger(ips)
    _hosts = res_ops.query_resource(res_ops.HOST)
    hosts_ip = [i.managementIp for i in _hosts]
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
    cluster = cluster_ops.create_mini_cluster(mini_cluster_option)
    for i in range(round): 
        host_uuids = []
        host_ips = []
        mn_flag = None # if candidate hosts including MN node
        cluster_cond = res_ops.gen_query_conditions('uuid', '=', cluster.uuid)
        if not res_ops.query_resource(res_ops.CLUSTER, cluster_cond):
            cluster = cluster_ops.create_mini_cluster(mini_cluster_option)
        #operations & power off random hosts
        test_util.test_logger("round {}".format(i))
        cond = res_ops.gen_query_conditions('cluster.uuid', '=', cluster_uuid)
        cluster_hosts = res_ops.query_resource(res_ops.HOST, cond)
        for host in cluster_hosts:
            if host.uuid == MN_HOST.uuid:
                mn_flag = 1
                wait_time = 900 #wait mn up
            host_uuids.append(host.uuid)
            host_ips.append(host.managementIp)
        delete_cluster_thread = test_stub.ExcThread(target=cluster_ops.delete_cluster, args=(cluster.uuid,)) 
        power_off_thread = test_stub.ExcThread(target=host_ops.poweroff_host, args=(host_uuids, admin_password, mn_flag))
        operations_shutdown(power_off_thread, host_uuids, host_ips, wait_time, delete_cluster_thread) 
    test_util.test_pass("pass")

def error_cleanup():
    global test_obj_dict
    global clusters
    test_lib.lib_error_cleanup(test_obj_dict)
    if clusters:
        for cluster in clusters:
            cluster_ops.delete_cluster(cluster.uuid)
        clusters = []

def env_recover():
    global test_obj_dict
    global clusters
    test_lib.lib_error_cleanup(test_obj_dict)
    if clusters:
        for cluster in clusters:
            cluster_ops.delete_cluster(cluster.uuid)
        clusters = []
