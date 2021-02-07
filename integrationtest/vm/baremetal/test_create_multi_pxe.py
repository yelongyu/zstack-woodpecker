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
    test_util.test_dsc('Create baremetal cluster and attach network')
    zone_uuid = res_ops.query_resource(res_ops.ZONE)[0].uuid
    cond = res_ops.gen_query_conditions('name', '=', os.environ.get('l3NoVlanNetworkName1'))
    l3_network = res_ops.query_resource(res_ops.L3_NETWORK, cond)[0]
    cidr = l3_network.ipRanges[0].networkCidr
    cond = res_ops.gen_query_conditions('l3Network.uuid', '=', l3_network.uuid)
    l2_uuid = res_ops.query_resource(res_ops.L2_NETWORK, cond)[0].uuid
    baremetal_cluster1_uuid = test_stub.create_cluster(zone_uuid).uuid
    sys_tags = "l2NetworkUuid::%s::clusterUuid::%s::cidr::{%s}" %(l2_uuid, baremetal_cluster1_uuid, cidr)
    net_ops.attach_l2(l2_uuid, baremetal_cluster1_uuid, [sys_tags])
    baremetal_cluster2_uuid = test_stub.create_cluster(zone_uuid).uuid
    sys_tags = "l2NetworkUuid::%s::clusterUuid::%s::cidr::{%s}" %(l2_uuid, baremetal_cluster2_uuid, cidr)
    net_ops.attach_l2(l2_uuid, baremetal_cluster2_uuid, [sys_tags])

    test_util.test_dsc('Create pxe server')
    mn_ip = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].hostName
    cond = res_ops.gen_query_conditions('managementIp', '=', mn_ip) 
    mn_host_uuid = res_ops.query_resource(res_ops.HOST, cond)[0].uuid
    host_list = res_ops.query_resource(res_ops.HOST, [], None)
    flag = 0
    for host in host_list:
        if host.managementIp_ != mn_ip:
            host_ip = host.managementIp_
            flag = 1
        if (flag ==1 ):
            break
    pxe1_uuid = test_stub.create_pxe(hostname = host_ip, zoneUuid = zone_uuid).uuid
    baremetal_operations.attach_pxe_to_cluster(pxe1_uuid, baremetal_cluster1_uuid)
    cmd = "ps aux | grep dnsmasq | awk 'NR==1 {print $2}' | xargs kill -9"
    rsp = test_lib.lib_execute_ssh_cmd(host_ip, host.username, host.password, cmd, 180)
    pxe2_uuid = test_stub.create_pxe(zoneUuid = zone_uuid).uuid
    baremetal_operations.attach_pxe_to_cluster(pxe2_uuid, baremetal_cluster2_uuid)

    test_util.test_dsc('Create a vm to simulate baremetal host')
    cond = res_ops.gen_query_conditions('hypervisorType', '=', 'KVM')
    cluster_uuid = res_ops.query_resource(res_ops.CLUSTER, cond)[0].uuid
    vm = test_stub.create_vm(host_uuid = mn_host_uuid, cluster_uuid = cluster_uuid)

    test_util.test_dsc('Create chassis')
    test_stub.create_vbmc(vm, mn_ip, 623)
    chassis = test_stub.create_chassis(baremetal_cluster2_uuid)
    chassis_uuid = chassis.uuid
    #Hack inspect ks file to support vbmc, include ipmi device logic and ipmi addr to 127.0.0.1
    test_stub.hack_inspect_ks(mn_ip)

    test_util.test_dsc('Inspect chassis, Because vbmc have bugs, \
	reset vm unable to enable boot options, power off/on then reset is worked')
    baremetal_operations.inspect_chassis(chassis_uuid)
    baremetal_operations.power_off_baremetal(chassis_uuid)
    time.sleep(3)
    status = baremetal_operations.get_power_status(chassis_uuid).status
    if status != "Chassis Power is off":
        test_util.test_fail('Fail to power off chassis %s, current status is %s' %(chassis_uuid, status))
    baremetal_operations.power_on_baremetal(chassis_uuid)
    time.sleep(3)
    status = baremetal_operations.get_power_status(chassis_uuid).status
    if status != "Chassis Power is on":
        test_util.test_fail('Fail to power on chassis %s, current status is %s' %(chassis_uuid, status))

    test_util.test_dsc('Disable/Enable chassis and check')
    cond = res_ops.gen_query_conditions('uuid','=', chassis_uuid)
    baremetal_operations.change_baremetal_chassis_state(chassis_uuid, 'disable')
    state = res_ops.query_resource(res_ops.CHASSIS, cond)[0].state
    if state != 'Disabled':
        test_util.test_fail('Disable chassis %s failed, current state is %s' %(chassis_uuid, state))
    baremetal_operations.change_baremetal_chassis_state(chassis_uuid, 'enable')
    state = res_ops.query_resource(res_ops.CHASSIS, cond)[0].state
    if state != 'Enabled':
        test_util.test_fail('Enable chassis %s failed, current state is %s' %(chassis_uuid, state))

    test_util.test_dsc('Inspect chassis and check hardware info')
    baremetal_operations.inspect_chassis(chassis_uuid)
    hwinfo = test_stub.check_hwinfo(chassis_uuid)
    if not hwinfo:
        test_util.test_fail('Fail to get hardware info during the first inspection')

    baremetal_operations.power_reset_baremetal(chassis_uuid)
    time.sleep(30)

    test_util.test_dsc('Clear env')
    test_stub.delete_vbmc(vm, mn_ip)
    baremetal_operations.delete_chassis(chassis_uuid)
    vm.destroy()
    baremetal_operations.delete_pxe(pxe1_uuid)
    baremetal_operations.delete_pxe(pxe2_uuid)
    cluster_ops.delete_cluster(baremetal_cluster1_uuid)
    cluster_ops.delete_cluster(baremetal_cluster2_uuid)
    test_util.test_pass('Create chassis Test Success')

def error_cleanup():
    global vm, baremetal_cluster1_uuid,baremetal_cluster2_uuid, pxe1_uuid, pxe2_uuid, mn_ip
    if vm:
        test_stub.delete_vbmc(vm, mn_ip)
        chassis = os.environ.get('ipminame')
        chassis_uuid = test_lib.lib_get_chassis_by_name(chassis).uuid
        baremetal_operations.delete_chassis(chassis_uuid)
        vm.destroy()
        if mn_ip:
            test_stub.delete_vbmc(vm, mn_ip)
    if baremetal_cluster1_uuid:
        cluster_ops.delete_cluster(baremetal_cluster1_uuid)
    if baremetal_cluster2_uuid:
        cluster_ops.delete_cluster(baremetal_cluster2_uuid)
    if pxe1_uuid:
        baremetal_ops.delete_pxe(pxe1_uuid)
    if pxe2_uuid:
        baremetal_ops.delete_pxe(pxe2_uuid)    

