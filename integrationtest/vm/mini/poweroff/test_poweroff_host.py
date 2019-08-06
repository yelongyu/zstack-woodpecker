'''
Integration test for testing power off mini hosts.
#1.power off hosts(not in mn cluster)
#2.start hosts
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
import time
import os
import random
import hashlib

MN_IP = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].hostName
admin_password = hashlib.sha512('password').hexdigest()
test_obj_dict = test_state.TestStateDict()
zstack_management_ip = os.environ.get('zstackManagementIp')

def recover_hosts(host_uuids, host_ips):
    for ip in host_ips:
        cond = res_ops.gen_query_conditions('vmNics.ip', '=', ip)
        vm_uuid = sce_ops.query_resource(zstack_management_ip, res_ops.VM_INSTANCE, cond).inventories[0].uuid
        sce_ops.start_vm(zstack_management_ip, vm_uuid)
    for uuid in host_uuids:
        host_ops.reconnect_host(uuid)

def test():
    global test_obj_dict
    test_util.test_logger("@@:mnip:{}".format(zstack_management_ip))
    cond = res_ops.gen_query_conditions('managementIp', '=', MN_IP)
    MN_HOST = res_ops.query_resource(res_ops.HOST, cond)[0]
    cond = res_ops.gen_query_conditions('uuid', '!=', MN_HOST.clusterUuid)
    cluster_uuid = res_ops.query_resource(res_ops.CLUSTER, cond)[0].uuid 
    host_uuids = []
    host_ips = []
    cond = res_ops.gen_query_conditions('cluster.uuid', '=', cluster_uuid)
    cluster_hosts = res_ops.query_resource(res_ops.HOST, cond)
    for host in cluster_hosts:
        host_uuids.append(host.uuid)
        host_ips.append(host.managementIp)
    shutdown_result = host_ops.poweroff_host(host_uuids, admin_password)
    test_util.test_logger("restart hosts")
    #vm sync per min
    time.sleep(150)
    recover_hosts(host_uuids, host_ips)
    test_util.test_pass("pass")

def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)

def env_recover():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
