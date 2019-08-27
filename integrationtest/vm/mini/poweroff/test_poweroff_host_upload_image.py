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
import zstackwoodpecker.operations.image_operations as img_ops
import time
import os
import random
import threading
import hashlib
import random

WINDOWS_URL = 'http://172.20.1.22/mirror/diskimages/windows-2012-cn-qcow2.qcow2'
UBUNTU_URL = 'http://172.20.1.22/mirror/diskimages/ubuntu14-test.qcow2'
CENTOS_URL = 'http://172.20.1.22/mirror/diskimages/centos7-test.qcow2.no-qemu-ga'
image_url_list = [WINDOWS_URL, UBUNTU_URL, CENTOS_URL]

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
    if operation_thread:
        operation_thread.start()
    shutdown_thread.start()
    shutdown_thread.join()
    time.sleep(180)
    recover_hosts(host_uuids, host_ips, wait_time)
    
def test():
    global test_obj_dict
    wait_time = 120
    round = 2 
    test_util.test_logger("@@:mnip:{}".format(zstack_management_ip))
    cond = res_ops.gen_query_conditions('managementIp', '=', MN_IP)
    MN_HOST = res_ops.query_resource(res_ops.HOST, cond)[0]
    cluster_list = res_ops.get_resource(res_ops.CLUSTER)
    #add images
    img_option = test_util.ImageOption()
    bs_uuid = res_ops.query_resource_fields(res_ops.BACKUP_STORAGE, [], None)[0].uuid
    img_option.set_backup_storage_uuid_list([bs_uuid])
    img_option.set_format('qcow2')
    for i in range(round): 
        host_uuids = []
        host_ips = []
        mn_flag = None # if candidate hosts including MN node
        #operations & power off random hosts
        test_util.test_logger("round {}".format(i))
        cluster_uuid = random.choice(cluster_list).uuid 
        cond = res_ops.gen_query_conditions('cluster.uuid', '=', cluster_uuid)
        cluster_hosts = res_ops.query_resource(res_ops.HOST, cond)
        for host in cluster_hosts:
            if host.uuid == MN_HOST.uuid:
                mn_flag = 1
                wait_time = 900 #wait mn up
            host_uuids.append(host.uuid)
            host_ips.append(host.managementIp)
        img_option.set_name('image%s' % i)
        img_option.set_url(image_url_list[i])
        upload_image_thread = threading.Thread(target=img_ops.add_image, args=(img_option,))
        power_off_thread = threading.Thread(target=host_ops.poweroff_host, args=(host_uuids, admin_password, mn_flag))
        operations_shutdown(power_off_thread, host_uuids, host_ips, wait_time, upload_image_thread) 
    test_util.test_pass("pass")

def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)

def env_recover():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
