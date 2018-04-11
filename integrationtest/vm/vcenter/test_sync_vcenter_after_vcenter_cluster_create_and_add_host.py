'''
Test sync vcenter after creating new vcenter cluster and add host to the cluster

@author:
'''
import apibinding.inventory as inventory
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.vcenter_operations as vct_ops
import zstackwoodpecker.operations.deploy_operations as deploy_operations
import test_stub

import os
import time


def test():
    global vc_cluster

    vcenter = os.environ.get('vcenter')
    SI = vct_ops.connect_vcenter(vcenter)
    content = SI.RetrieveContent()
    datacenter_name = os.environ.get('vcdatacenterName')
    datacenter = vct_ops.get_datacenter(content, datacenter_name)[0]
    #create vcenter cluster
    vc_cluster = vct_ops.create_cluster(datacenter)
    #create vcenter host
    host_name = os.environ.get('hostName3')
    managementIp = deploy_operations.get_host_from_scenario_file(host_name, test_lib.all_scenario_config, test_lib.scenario_file,test_lib.deploy_config)
    vc_host = vct_ops.add_host(vc_cluster, managementIp)

    #sync vcenter
    vcenter_uuid = vct_ops.lib_get_vcenter_by_name(vcenter).uuid
    vct_ops.sync_vcenter(vcenter_uuid)
    time.sleep(5)

    assert vc_cluster.name == vct_ops.lib_get_vcenter_cluster_by_name(vc_cluster.name).name

    assert managementIp == vct_ops.lib_get_vcenter_host_by_ip(managementIp).name
    assert vct_ops.lib_get_vcenter_host_by_ip(managementIp).hypervisorType == "ESX"

    vct_ops.remove_cluster(vc_cluster)
    test_util.test_pass('Sync vcenter after creating new vcenter cluster and add host to the cluster successfully')


def error_cleanup():
    global vc_cluster
    vct_ops.remove_cluster(vc_cluster)
