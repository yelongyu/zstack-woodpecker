'''
Test chassis operation

@author chenyuan.xu
'''
import zstackwoodpecker.operations.baremetal_operations as baremetal_operations
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.cluster_operations as cluster_ops
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as zstack_vm_header
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import test_stub
import threading
import zstacklib.utils.shell as shell
import time
import os

vm = None
baremetal_cluster_uuid = None
pxe_uuid = None
host_ip = None
exc_info = []

def inspect_chassis(chassis_uuid):
    try:
        baremetal_operations.inspect_chassis(chassis_uuid)
    except:
        exc_info.append(sys.exc_info())

def check_thread_exception():
    if exc_info:
        info1 = exc_info[0][1]
        info2 = exc_info[0][2]
        raise info1, None, info2

def test():
    global vm, baremetal_cluster_uuid, pxe_uuid, host_ip
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
    [pxe_ip, interface] = test_stub.get_pxe_info()
    if not pxe_servers:
        pxe_uuid = test_stub.create_pxe(dhcp_interface = interface, hostname = pxe_ip, zoneUuid = zone_uuid).uuid
        baremetal_operations.attach_pxe_to_cluster(pxe_uuid, baremetal_cluster_uuid)
 
    test_util.test_dsc('Create vms to simulate baremetal host')
    #mn_ip = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].hostName
    #cond = res_ops.gen_query_conditions('managementIp', '=', mn_ip) 
    #host = res_ops.query_resource(res_ops.HOST, cond)[0]
    host_list = []
    hosts = res_ops.query_resource(res_ops.HOST)
    num = len(hosts)
    for i in range (0, num):
        host_list.append(hosts[i])
    host_uuid = hosts[0].uuid
    host_ip = hosts[0].managementIp
    cond = res_ops.gen_query_conditions('hypervisorType', '=', 'KVM')
    cluster_uuid = res_ops.query_resource(res_ops.CLUSTER, cond)[0].uuid
    cond = res_ops.gen_query_conditions('name', '=', os.environ.get('scenl3VPCNetworkName1'))
    l3_network = res_ops.query_resource(res_ops.L3_NETWORK, cond)[0]
    l3_uuid_list = []
    l3_uuid_list.append(l3_network.uuid)
    cond = res_ops.gen_query_conditions('name', '=', os.environ.get('l3PublicNetworkName'))
    public_network = res_ops.query_resource(res_ops.L3_NETWORK, cond)[0]
    l3_uuid_list.append(public_network.uuid)
    vm_list = []
    for i in range (0, num):
        vm_name =  'baremetal_vm_%s' % str(i)
        vm = test_stub.create_vm_multi_l3(l3_uuid_list=l3_uuid_list, default_l3_uuid = l3_network.uuid, vm_name = vm_name, host_uuid = hosts[i].uuid, cluster_uuid = cluster_uuid)
        vm_list.append(vm)

    test_util.test_dsc('Create chassis')
    chassis_list = []
    for i in range (0, num):
        test_stub.create_vbmc(vm_list[i], hosts[i].managementIp, 623)
        chassis = test_stub.create_chassis(baremetal_cluster_uuid, address = hosts[i].managementIp)
        chassis_list.append(chassis)

    #Hack inspect ks file to support vbmc, include ipmi device logic and ipmi addr to 127.0.0.1
    node_ip = os.environ.get('node1Ip')
    ks = '/home/%s/zstack-woodpecker/integrationtest/vm/baremetal/inspector_ks.cfg' % node_ip
    path = '/var/lib/zstack/baremetal/ftp/ks/inspector_ks.cfg'
    session_uuid = acc_ops.login_as_admin()    
    cmd = "ip r | grep %s | awk '{print $NF}'" % interface
    pxe_server_ip = test_lib.lib_execute_ssh_cmd(pxe_ip, 'root', 'password', cmd, 180).strip()
    os.system("sed -i 's/session_uuid/%s/g' %s" %(session_uuid, ks))
    os.system("sed -i 's/pxe_server_ip/%s/g' %s" %(pxe_server_ip, ks))
    os.system("sed -i 's/pxe_server_uuid/%s/g' %s" %(pxe_uuid, ks))
    shell.call('scp %s %s:%s'  %(ks, pxe_ip, path))

    test_util.test_dsc('Inspect chassis, Because vbmc have bugs, \
	reset vm unable to enable boot options, power off/on then reset is worked')
 #   baremetal_operations.inspect_chassis(chassis_uuid)
    for i in range(0, num):
        baremetal_operations.inspect_chassis(chassis_list[i].uuid)
        baremetal_operations.power_off_baremetal(chassis_list[i].uuid)
        time.sleep(3)
        status = baremetal_operations.get_power_status(chassis_list[i].uuid).status
        if status != "Chassis Power is off":
            test_util.test_fail('Fail to power off chassis %s, current status is %s' %(chassis_list[i].uuid, status))
        baremetal_operations.power_on_baremetal(chassis_list[i].uuid)
        time.sleep(3)
        status = baremetal_operations.get_power_status(chassis_list[i].uuid).status
        if status != "Chassis Power is on":
            test_util.test_fail('Fail to power on chassis %s, current status is %s' %(chassis_list[i].uuid, status))
    n = 0
    while n < num:
        thread_threshold = 10
        check_thread_exception()
        thread = threading.Thread(target=inspect_chassis, args=(chassis_list[n].uuid,))
        n += 1
        while threading.active_count() > thread_threshold:
            time.sleep(1)
        thread.start()

    while threading.active_count() > 1:
        time.sleep(0.05)

    time.sleep(120)
    test_util.test_dsc('Check hardware info')
    for i in (0, num):
        hwinfo = test_stub.check_hwinfo(chassis_list[i].uuid)
        if not hwinfo:
            test_util.test_fail('Fail to get hardware info during the first inspection')

    test_util.test_dsc('Clear env')
    for i in range (0, num):
        test_stub.delete_vbmc(vm_list[i], hosts[i].managementIp)
        baremetal_operations.delete_chassis(chassis_list[i].uuid)
        vm_list[i].destroy()
    baremetal_operations.delete_pxe(pxe_uuid)
    cluster_ops.delete_cluster(baremetal_cluster_uuid)
    test_util.test_pass('Create chassis Test Success')

def error_cleanup():
    global vm, baremetal_cluster_uuid, pxe_uuid, host_ip
    for i in range (0, num):
        if vm_list[i]:
            test_stub.delete_vbmc(vm_list[i], hosts[i].managementIp)
            baremetal_operations.delete_chassis(chassis_list[i].uuid)
            vm_list[i].destroy()
            if hosts[i].managementIp:
                test_stub.delete_vbmc(vm_list[i], hosts.managementIp)
    if baremetal_cluster_uuid:
        cluster_ops.delete_cluster(baremetal_cluster_uuid)
    if pxe_uuid:
        baremetal_ops.delete_pxe(pxe_uuid)
