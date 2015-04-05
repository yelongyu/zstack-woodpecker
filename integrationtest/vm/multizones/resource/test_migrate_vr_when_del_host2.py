'''

When deleting host, if VR is that host. The VR VM should be migrated to other host, if there is any host has the same L2. 

In this case, the VR will be created on the cluster, which only have 1 host. 
The cluster will share the same l2 with another cluster. So the case will check
if the VR will be migrated to the 2nd cluster.

@author: Youyk
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.header.vm as vm_header
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.export_operations as exp_ops
import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import time
import os

_config_ = {
        'timeout' : 1200,
        'noparallel' : True
        }

test_obj_dict = test_state.TestStateDict()
host_config = test_util.HostOption()

def test():
    global host_config
    curr_deploy_conf = exp_ops.export_zstack_deployment_config(test_lib.deploy_config)

    vm_creation_option = test_util.VmOption()
    image_name = os.environ.get('imageName_net')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    #pick up host1
    host1_name = os.environ.get('hostName')
    host1 = res_ops.get_resource(res_ops.HOST, name = host1_name)[0]
    host3_name = os.environ.get('hostName3')
    host3 = res_ops.get_resource(res_ops.HOST, name = host3_name)[0]

    cond = res_ops.gen_query_conditions('clusterUuid', '=', host1.clusterUuid)
    cluster_hosts = res_ops.query_resource(res_ops.HOST, cond)
    if not len(cluster_hosts) > 1:
        test_util.test_skip('Skip test, since [cluster:] %s did not include more than 1 host' % host1.clusterUuid)

    for host in cluster_hosts:
        if host.uuid != host1.uuid:
            host2 = host

    conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
    instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_name('multizones_basic_vm')
    vm_creation_option.set_host_uuid(host1.uuid)

    l3_name = os.environ.get('l3VlanNetworkName1')
    l3 = res_ops.get_resource(res_ops.L3_NETWORK, name = l3_name)[0]
    vm_creation_option.set_l3_uuids([l3.uuid])

    vm1 = test_lib.lib_create_vm(vm_creation_option)
    test_obj_dict.add_vm(vm1)

    vr_vm_inv = test_lib.lib_find_vr_by_vm(vm1.get_vm())[0]
    vr_host_uuid = vr_vm_inv.hostUuid

    #migrate vr to host3.
    if vr_host_uuid != host3.uuid:
        vm_ops.migrate_vm(vr_vm_inv.uuid, host3.uuid)


    host_config.set_cluster_uuid(host3.clusterUuid)
    host_config.set_username(os.environ.get('hostUsername'))
    host_config.set_password(os.environ.get('hostPassword'))
    host_config.set_name(host3_name)
    host_config.set_management_ip(host3.managementIp)
    target_host_uuid = host3.uuid

    test_util.test_dsc("Delete VR VM's host. VR should be migrated to Cluster1")
    host_ops.delete_host(target_host_uuid)

    vm1.check()

    #using the same L3 to create VM2 to check if VR is working well.
    vm_creation_option.set_host_uuid(None)
    vm2 = test_lib.lib_create_vm(vm_creation_option)
    test_obj_dict.add_vm(vm2)
    vm2.check()

    host_ops.add_kvm_host(host_config)

    test_lib.lib_robot_cleanup(test_obj_dict)
    test_util.test_pass('Test VR migration when deleting Host is Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global host_config
    test_lib.lib_error_cleanup(test_obj_dict)
    if not host1:
        try:
            host_ops.add_kvm_host(host_config)
        except Exception as e:
            test_util.test_warn('Fail to recover all [host:] %s resource. It will impact later test case.' % host1_name)
            raise e
