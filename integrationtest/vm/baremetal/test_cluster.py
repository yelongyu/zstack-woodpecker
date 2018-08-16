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
cluster_uuid = None
def test():
    global cluster_uuid
    zone = res_ops.query_resource(res_ops.ZONE)[0]
    l2_uuid = res_ops.query_resource(res_ops.L2_VXLAN_NETWORK)[0].uuid
    l2_pool = res_ops.query_resource(res_ops.L2_VXLAN_NETWORK_POOL)[0].uuid
    cluster_option = test_util.ClusterOption()
    cluster_option.set_name('baremetal_clusterI')
    cluster_option.set_hypervisor_type('baremetal')
    cluster_option.set_type('baremetal')
    cluster_option.set_zone_uuid(zone.uuid)
    cluster_uuid = cluster_ops.create_cluster(cluster_option).uuid
    cidr = "10.0.0.1/8"
    sys_tags = "l2NetworkUuid::%s::clusterUuid::%s::cidr::{%s}" %(l2_pool, cluster_uuid, cidr)
    net_ops.attach_l2_vxlan_pool(l2_pool, cluster_uuid, [sys_tags])
    cond = res_ops.gen_query_conditions('attachedClusterUuids', '=', cluster_uuid)
    attatch_networks = res_ops.query_resource(res_ops.L2_NETWORK)
    net_attached = False
    for net in attatch_networks:
        if net.uuid == l2_pool:
            net_attached = True
    if net_attached == False:
        test_util.test_fail('Attach L2 VxLAN Pool to Baremetal Cluster Failed')
    #net_ops.detach_l2(l2_pool, cluster_uuid)    
    cluster_ops.change_cluster_state(cluster_uuid, 'disable')
    cond = res_ops.gen_query_conditions('uuid', '=', cluster_uuid)
    if res_ops.query_resource(res_ops.CLUSTER, cond)[0].state!= 'Disabled':
        test_util.test_fail('Fail to disable Baremetal Cluster') 
    cluster_ops.change_cluster_state(cluster_uuid, 'enable')
    #cluster_ops.delete_cluster(cluster_uuid)
    test_util.test_pass('Test Baremetal Cluster Test Success')

def error_cleanup():
    global cluster_uuid
    if cluster_uuid:
        cluster_ops.delete_cluster(cluster_uuid)
