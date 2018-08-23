'''
Test baremetal instance operation

@author Glody
'''
import zstackwoodpecker.operations.baremetal_operations as baremetal_operations
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.cluster_operations as cluster_ops
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as zstack_vm_header
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import test_stub
import time
import os

vm = None
cluster_uuid = None
pxe_uuid = None
host_ip = None
def test():
    global vm, cluster_uuid, pxe_uuid, host_ip
    test_util.test_dsc('Create baremetal cluster and attach network')
    zone_uuid = res_ops.query_resource(res_ops.ZONE)[0].uuid
    cond = res_ops.gen_query_conditions('type', '=', 'baremetal')
    cluster = res_ops.query_resource(res_ops.CLUSTER, cond)
    if cluster == []:
        cluster_uuid = test_stub.create_cluster(zone_uuid).uuid
    else:
        cluster_uuid = cluster[0].uuid
        test_util.test_dsc('cluster uuis is %s '% cluster_uuid)
    cond = res_ops.gen_query_conditions('name', '=', os.environ.get('l3NoVlanNetworkName1'))
    l3_network = res_ops.query_resource(res_ops.L3_NETWORK, cond)[0]
    cidr = l3_network.ipRanges[0].networkCidr
    cond = res_ops.gen_query_conditions('l3Network.uuid', '=', l3_network.uuid)
    l2_uuid = res_ops.query_resource(res_ops.L2_NETWORK, cond)[0].uuid
    sys_tags = "l2NetworkUuid::%s::clusterUuid::%s::cidr::{%s}" %(l2_uuid, cluster_uuid, cidr)
    net_ops.attach_l2(l2_uuid, cluster_uuid, [sys_tags])

    test_util.test_dsc('Create pxe server')
    pxe_servers = res_ops.query_resource(res_ops.PXE_SERVER)
    if not pxe_servers:
        pxe_uuid = test_stub.create_pxe().uuid
 
    test_util.test_dsc('Create a vm to simulate baremetal host')
    mn_ip = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].hostName
    cond = res_ops.gen_query_conditions('managementIp', '=', mn_ip) 
    host = res_ops.query_resource(res_ops.HOST, cond)[0]
    host_uuid = host.uuid
    host_ip = host.managementIp
    cond = res_ops.gen_query_conditions('hypervisorType', '=', 'KVM')
    cluster_uuid = res_ops.query_resource(res_ops.CLUSTER, cond)[0].uuid
    vm = test_stub.create_vm(host_uuid = host_uuid, cluster_uuid = cluster_uuid)

    test_util.test_dsc('Create chassis')
    cond = res_ops.gen_query_conditions('hypervisorType', '=', 'baremetal')
    baremetal_cluster_uuid = res_ops.query_resource(res_ops.CLUSTER, cond)[0].uuid
    test_stub.create_vbmc(vm, host_ip, 623)
    chassis = test_stub.create_chassis(baremetal_cluster_uuid)
    chassis_uuid = chassis.uuid 
    #Hack inspect ks file to support vbmc, include ipmi device logic and ipmi addr to 127.0.0.1
    test_stub.hack_inspect_ks(host_ip)

    test_util.test_dsc('Inspect chassis, Because vbmc have bugs, \
	reset vm unable to enable boot options, power off/on then reset is worked')
    baremetal_operations.inspect_chassis(chassis_uuid)
    baremetal_operations.power_off_baremetal(chassis_uuid)
    time.sleep(3)
    baremetal_operations.power_on_baremetal(chassis_uuid)
    time.sleep(3)
    status = baremetal_operations.get_power_status(chassis_uuid).status
    baremetal_operations.inspect_chassis(chassis_uuid)
    hwinfo = test_stub.check_hwinfo(chassis_uuid)
    if not hwinfo:
        test_util.test_fail('Fail to get hardware info during the first inspection')

    test_util.test_dsc('Create baremetal instance')
    #Hack iso ks file to support unattended installation
<<<<<<< HEAD
    test_stub.hack_generic_ks(host_ip)
    test_stub.ca_pem_workaround(host_ip)
=======
    test_stub.hack_generic_ks(mn_ip)
    test_stub.ca_pem_workaround(mn_ip)
>>>>>>> upstream/master
    cond = res_ops.gen_query_conditions('name', '=', os.environ.get('imageName_iso')) 
    image_uuid = res_ops.query_resource(res_ops.IMAGE, cond)[0].uuid
    time.sleep(30)
    baremetal_ins = test_stub.create_baremetal_ins(image_uuid, chassis_uuid)
    baremetal_ins_uuid = baremetal_ins.uuid
    ins_status = test_stub.check_baremetal_ins(baremetal_ins_uuid, 'password', \
<<<<<<< HEAD
	baremetal_ins.managementIp, host_ip, chassis_uuid, os.environ.get('ipmiaddress'))
=======
	baremetal_ins.managementIp, mn_ip, chassis_uuid, os.environ.get('ipmiaddress'))
>>>>>>> upstream/master
    if not ins_status:
        test_util.test_fail('Baremetal instance installation failed')

    test_util.test_dsc('Check baremetal instance operations')
    cond = res_ops.gen_query_conditions('uuid', '=', baremetal_ins_uuid)
    new_name = 'New Baremetal Instance'
    baremetal_operations.update_baremetal_instance(baremetal_ins_uuid, name = new_name)
    udated_name = res_ops.query_resource(res_ops.BAREMETAL_INS, cond)[0].name
    if udated_name != new_name:
        test_util.test_fail('Update baremetal instance name failed, expected: %s, real: %s'%(new_name, udated_name))
    baremetal_operations.stop_baremetal_instance(baremetal_ins_uuid)
    state = res_ops.query_resource(res_ops.BAREMETAL_INS, cond)[0].state
    if state != 'Stopped':
        test_util.test_fail('Fail to stop baremetal instance, current status: %s'%state)
    baremetal_operations.start_baremetal_instance(baremetal_ins_uuid)
    time.sleep(60)
    state = res_ops.query_resource(res_ops.BAREMETAL_INS, cond)[0].state
    if state != 'Running':
        test_util.test_fail('Fail to start baremetal instance, current status: %s'%state)
    baremetal_operations.reboot_baremetal_instance(baremetal_ins_uuid)

    #test_util.test_dsc('Clear env')
    baremetal_operations.destory_baremetal_instance(baremetal_ins_uuid)
    baremetal_operations.expunge_baremetal_instanc(baremetal_ins_uuid)
    test_stub.delete_vbmc(vm, host_ip)
    baremetal_operations.delete_chassis(chassis_uuid)
    vm.destroy()
    baremetal_ops.delete_pxe(pxe_uuid)
    cluster_ops.delete_cluster(cluster_uuid)
    test_util.test_pass('Create chassis Test Success')

def error_cleanup():
    global vm, cluster_uuid, pex_uuid
    if vm:
        test_stub.delete_vbmc(vm = vm)
        chassis = os.environ.get('ipminame')
        chassis_uuid = test_lib.lib_get_chassis_by_name(chassis).uuid
        baremetal_operations.delete_chassis(chassis_uuid)
        vm.destroy()
        if host_ip:
            test_stub.delete_vbmc(vm, host_ip)
    if cluster_uuid:
        cluster_ops.delete_cluster(cluster_uuid)
    if pex_uuid:
        baremetal_ops.delete_pxe(pxe_uuid)
