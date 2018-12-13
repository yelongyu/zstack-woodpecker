'''
Test chassis operation

@author chenyuan.xu
'''
import zstackwoodpecker.operations.baremetal_operations as baremetal_operations
import zstackwoodpecker.operations.config_operations as conf_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.cluster_operations as cluster_ops
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as zstack_vm_header
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import test_stub
import time
import os
import base64

vm = None
baremetal_cluster_uuid = None
pxe_uuid = None
host_ip = None
def test():
    global vm, baremetal_cluster_uuid, pxe_uuid, host_ip
    conf_ops.change_global_config('mevoco', 'overProvisioning.memory', '5')
    test_util.test_dsc('Create baremetal cluster and attach network')
    zone_uuid = res_ops.query_resource(res_ops.ZONE)[0].uuid
    cond = res_ops.gen_query_conditions('type', '=', 'baremetal')
    cluster = res_ops.query_resource(res_ops.CLUSTER, cond)
    if not cluster:
        baremetal_cluster_uuid = test_stub.create_cluster(zone_uuid).uuid
    else:
        baremetal_cluster_uuid = cluster[0].uuid
    cond = res_ops.gen_query_conditions('name', '=', os.environ.get('l3NoVlanNetworkName1'))
    l3_network = res_ops.query_resource(res_ops.L3_NETWORK, cond)[0]
    cidr = l3_network.ipRanges[0].networkCidr
    cond = res_ops.gen_query_conditions('l3Network.uuid', '=', l3_network.uuid)
    l2_uuid = res_ops.query_resource(res_ops.L2_NETWORK, cond)[0].uuid
    sys_tags = "l2NetworkUuid::%s::clusterUuid::%s::cidr::{%s}" %(l2_uuid, baremetal_cluster_uuid, cidr)
    net_ops.attach_l2(l2_uuid, baremetal_cluster_uuid, [sys_tags])

    test_util.test_dsc('Create pxe server')
    pxe_servers = res_ops.query_resource(res_ops.PXE_SERVER)
    if not pxe_servers:
        pxe_uuid = test_stub.create_pxe(zoneUuid = zone_uuid).uuid
        baremetal_operations.attach_pxe_to_cluster(pxe_uuid, baremetal_cluster_uuid)
    else:
        pxe_uuid = pxe_servers[0].uuid

    test_util.test_dsc('Create a vm to simulate baremetal host')
    mn_ip = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].hostName
    cond = res_ops.gen_query_conditions('managementIp', '=', mn_ip)
    host = res_ops.query_resource(res_ops.HOST, cond)[0]
    host_uuid = host.uuid
    host_ip = host.managementIp
    cond = res_ops.gen_query_conditions('hypervisorType', '=', 'KVM')
    cluster_uuid = res_ops.query_resource(res_ops.CLUSTER, cond)[0].uuid
    vm_list = test_stub.create_multi_vms(name_prefix='test-vm', count=5, host_uuid=host_uuid)

    test_util.test_dsc('Create chassis')
    for i in range (0, 5):
        test_stub.create_vbmc(vm_list[i], host_ip, 6230+i)
    os.system("sed -i 's/cluster_uuid/%s/g' /home/baremetal_chassis_info.txt" % baremetal_cluster_uuid)
    file_path = '/home/baremetal_chassis_info.txt'
    with open(file_path.strip('\n'), 'r') as chassis_info2:
        chassis_info1 = chassis_info2.read()
        chassis_info = base64.b64encode('%s' % chassis_info1)
    baremetal_operations.batch_create_chassis(chassis_info)
    time.sleep(5)
    chassis_number = len(res_ops.query_resource(res_ops.CHASSIS, [], None))
    if chassis_number != 5:
        test_util.test_fail('Successfully create %s chassis,but there are %s chassis faild.' % (chassis_number, 5-chassis_number)

    test_util.test_dsc('Clear env')
    for i in range (0, 5):
        test_stub.delete_vbmc(vm_list[i], host_ip)
        vm_list[i].destroy()
    baremetal_operations.delete_pxe(pxe_uuid)
    cluster_ops.delete_cluster(baremetal_cluster_uuid)
    conf_ops.change_global_config('mevoco', 'overProvisioning.memory', '1')
    test_util.test_pass('Batch create chassis Test Success')

def error_cleanup():
    global vm, baremetal_cluster_uuid, pxe_uuid, host_ip
    if vm:
        test_stub.delete_vbmc(vm, host_ip)
        chassis = os.environ.get('ipminame')
        chassis_uuid = test_lib.lib_get_chassis_by_name(chassis).uuid
        baremetal_operations.delete_chassis(chassis_uuid)
        vm.destroy()
        if host_ip:
            test_stub.delete_vbmc(vm, host_ip)
    if baremetal_cluster_uuid:
        cluster_ops.delete_cluster(baremetal_cluster_uuid)
    if pxe_uuid:
        baremetal_ops.delete_pxe(pxe_uuid)
