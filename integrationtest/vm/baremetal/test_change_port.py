'''
Test change 8080 port

@author chenyuan.xu
'''
import zstackwoodpecker.operations.baremetal_operations as baremetal_operations
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.cluster_operations as cluster_ops
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as zstack_vm_header
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import test_stub
from vncdotool import api
import time
import os

vm = None
baremetal_cluster_uuid = None
pxe_uuid = None
host_ip = None
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

    cond = res_ops.gen_query_conditions('uuid','=', pxe_uuid)
    pxe_server = res_ops.query_resource(res_ops.PXE_SERVER,cond)[0]
    assert pxe_server.status == 'Connected'

    hosts = res_ops.query_resource(res_ops.HOST, [], None)    
    properties_path = '/usr/local/zstacktest/apache-tomcat/webapps/zstack/WEB-INF/classes/zstack.properties'
    tomcat_path = '/usr/local/zstacktest/apache-tomcat-8.5.35/conf/server.xml'
    cmd = 'echo CloudBus.httpPort=8989 >> %s' % properties_path
    mn_ip = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].hostName
    test_lib.lib_execute_ssh_cmd(mn_ip, 'root', 'password', cmd,180)
    cmd = 'echo RESTFacade.port=8989 >> %s' % properties_path
    test_lib.lib_execute_ssh_cmd(mn_ip, 'root', 'password', cmd,180)
    cmd = "sed -i 's/8080/8989/g' %s" % tomcat_path
    test_lib.lib_execute_ssh_cmd(mn_ip, 'root', 'password', cmd,180)

    cmd = 'zstack-ctl stop_node;zstack-ctl start_node'
    test_lib.lib_execute_ssh_cmd(mn_ip, 'root', 'password', cmd,180)

    time.sleep(60)
    for host in hosts:
        cmd = "zstack-cli --port 8989 LogInByAccount accountName=admin password=password;\
               zstack-cli --port 8989 ReconnectHost uuid=%s" % host.uuid
        result=test_lib.lib_execute_ssh_cmd(mn_ip, 'root', 'password', cmd,900)
        if result == False:
            test_util.test_fail('Fail to reconnect host:%s' % host.uuid)
    
    cmd =  "zstack-cli --port 8989 LogInByAccount accountName=admin password=password;\
               zstack-cli --port 8989 ReconnectBaremetalPxeServer uuid=%s" % pxe_uuid
    result=test_lib.lib_execute_ssh_cmd(mn_ip, 'root', 'password', cmd,600)
    if result == False:
        test_util.test_fail('Fail to reconnect pxe server:%s' % pxe_uuid)   

#######Recover environment######
    cmd = "sed -i 's/8989/8080/g' %s" % tomcat_path
    test_lib.lib_execute_ssh_cmd(mn_ip, 'root', 'password', cmd,180)
    cmd = "sed -i 's/RESTFacade.port=8989/RESTFacade.port=8080/g' %s" % properties_path
    test_lib.lib_execute_ssh_cmd(mn_ip, 'root', 'password', cmd,180)
    cmd = "sed -i 's/CloudBus.httpPort=8989/CloudBus.httpPort=8080/g' %s" % properties_path
    test_lib.lib_execute_ssh_cmd(mn_ip, 'root', 'password', cmd,180)
    cmd = 'zstack-ctl stop_node;zstack-ctl start_node'
    test_lib.lib_execute_ssh_cmd(mn_ip, 'root', 'password', cmd,180)

    if baremetal_cluster_uuid:
        cluster_ops.delete_cluster(baremetal_cluster_uuid)
    if pxe_uuid:
        baremetal_operations.delete_pxe(pxe_uuid)

    test_util.test_pass('Test Change Port Test Success')

def error_cleanup():
    global baremetal_cluster_uuid
    cmd = "sed -i 's/8989/8080/g' %s" % tomcat_path
    test_lib.lib_execute_ssh_cmd(mn_ip, 'root', 'password', cmd,180)
    cmd = "sed -i 's/RESTFacade.port=8989/RESTFacade.port=8080/g' %s" % properties_path
    test_lib.lib_execute_ssh_cmd(mn_ip, 'root', 'password', cmd,180)
    cmd = "sed -i 's/CloudBus.httpPort=8989/CloudBus.httpPort=8080/g' %s" % properties_path
    test_lib.lib_execute_ssh_cmd(mn_ip, 'root', 'password', cmd,180)
    cmd = 'zstack-ctl stop_node;zstack-ctl start_node'
    test_lib.lib_execute_ssh_cmd(mn_ip, 'root', 'password', cmd,180)
    
    if baremetal_cluster_uuid:
        cluster_ops.delete_cluster(baremetal_cluster_uuid)
    if pxe_uuid:
        baremetal_operations.delete_pxe(pxe_uuid)
