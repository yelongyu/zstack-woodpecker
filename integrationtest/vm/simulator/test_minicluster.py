'''
New Test For mini cluster creation and roll back when creation failed

@author: Glody
'''
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.operations.cluster_operations as cluster_ops
import apibinding.api_actions as api_actions
import apibinding.inventory as inventory
import threading
import time
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    zone_uuid =  res_ops.query_resource_fields(res_ops.ZONE)[0].uuid
    cluster_uuid = res_ops.query_resource_fields(res_ops.CLUSTER)[0].uuid
    cond = res_ops.gen_query_conditions('clusterUuid', '=',  cluster_uuid)
    hosts = res_ops.query_resource_fields(res_ops.HOST, cond)

    minicluster_name = 'minicluster'
    username = hosts[0].username
    password = 'password'
    ssh_port = hosts[0].sshPort
    hypervisor_type= 'KVM'
    host1_ip = hosts[0].managementIp
    host1_uuid = hosts[0].uuid
    host2_ip = hosts[1].managementIp
    host2_uuid = hosts[1].uuid

    #Delete cluster then add minicluster
    cluster_ops.delete_cluster(cluster_uuid) 

    mini_cluster_option = test_util.MiniClusterOption()
    mini_cluster_option.set_name(minicluster_name)
    mini_cluster_option.set_username(username)
    mini_cluster_option.set_password(password)
    mini_cluster_option.set_sshPort(ssh_port)
    mini_cluster_option.set_hypervisor_type(hypervisor_type)
    mini_cluster_option.set_zone_uuid(zone_uuid)
    mini_cluster_option.set_host_management_ips([host1_ip, host2_ip])
    cluster_ops.create_mini_cluster(mini_cluster_option)
    test_util.test_logger("Create Minicluster Passed")

    #Check roll back when create mini cluster failed
    cluster_uuid = res_ops.query_resource_fields(res_ops.CLUSTER)[0].uuid
    cond = res_ops.gen_query_conditions('clusterUuid', '=',  cluster_uuid)
    hosts = res_ops.query_resource_fields(res_ops.HOST, cond)
    host_ip = hosts[0].managementIp
    #Delete cluster then add minicluster
    cluster_ops.delete_cluster(cluster_uuid)
    mini_cluster_option.set_host_management_ips([host_ip, '127.127.127.127'])

    try:
        cluster_ops.create_mini_cluster(mini_cluster_option)
    except:
        pass

    cond = res_ops.gen_query_conditions('managementIp', '=',  host_ip)
    try:
        hosts = res_ops.query_resource_fields(res_ops.HOST, cond)
    except:
        test_util.test_pass("[Host:] %s is removed when create mini cluster failed" %host_ip)

    if hosts != []:
        test_util.test_fail("Fail to roll back when create mini cluster failed")

    test_util.test_pass("Mini cluster test passed")

def error_cleanup():
    pass

