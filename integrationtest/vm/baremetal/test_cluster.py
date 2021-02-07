'''

Test baremetal cluster opreations

@author: Glody
'''

import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.cluster_operations as cluster_ops
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import test_stub
import os

cluster_uuid = None
def test():
    test_util.test_dsc('Create Baremetal Cluster')
    global cluster_uuid
    zone_uuid = res_ops.query_resource(res_ops.ZONE)[0].uuid
    cluster_uuid = test_stub.create_cluster(zone_uuid).uuid

    test_util.test_dsc('Attach l3 Network to Baremetal Cluster')
    cond = res_ops.gen_query_conditions('name', '=', os.environ.get('l3NoVlanNetworkName1'))
    l3_network = res_ops.query_resource(res_ops.L3_NETWORK, cond)[0]
    cidr = l3_network.ipRanges[0].networkCidr
    cond = res_ops.gen_query_conditions('l3Network.uuid', '=', l3_network.uuid)
    l2_uuid = res_ops.query_resource(res_ops.L2_NETWORK, cond)[0].uuid
    sys_tags = "l2NetworkUuid::%s::clusterUuid::%s::cidr::{%s}" %(l2_uuid, cluster_uuid, cidr)
    net_ops.attach_l2(l2_uuid, cluster_uuid, [sys_tags])
    cond = res_ops.gen_query_conditions('attachedClusterUuids', '=', cluster_uuid)
    attatched_networks = res_ops.query_resource(res_ops.L2_NETWORK, cond)

    test_util.test_dsc('Check if the L3 Network is attached on Baremetal Cluster')
    net_attached = False
    for net in attatched_networks:
        if net.uuid == l2_uuid:
            net_attached = True
    if net_attached == False:
        test_util.test_fail('Attach L2 to Baremetal Cluster Failed')

    net_ops.detach_l2(l2_uuid, cluster_uuid)    

    test_util.test_dsc('Check disable/enable Baremetal Cluster')
    cluster_ops.change_cluster_state(cluster_uuid, 'disable')
    cond = res_ops.gen_query_conditions('uuid', '=', cluster_uuid)
    if res_ops.query_resource(res_ops.CLUSTER, cond)[0].state != 'Disabled':
        test_util.test_fail('Fail to disable Baremetal Cluster') 
    cluster_ops.change_cluster_state(cluster_uuid, 'enable')
    if res_ops.query_resource(res_ops.CLUSTER, cond)[0].state != 'Enabled':
        test_util.test_fail('Fail to enable Baremetal Cluster')

    cluster_ops.delete_cluster(cluster_uuid)
    test_util.test_pass('Test Baremetal Cluster Test Success')

def error_cleanup():
    global cluster_uuid
    if cluster_uuid:
        cluster_ops.delete_cluster(cluster_uuid)
