import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.operations.tag_operations as tag_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.cluster_operations as cls_ops
import zstackwoodpecker.operations.primarystorage_operations as ps_ops
import apibinding.api_actions as api_actions
import time
import os
import test_stub


def test():
    host = dict()
    host['Broadwell'] = []
    host['Haswell-noTSX'] = []
    _hosts = res_ops.query_resource(res_ops.HOST)
    if len(_hosts) < 4:
        test_util.test_fail("this case need at least 4 hosts")

    for i in _hosts[:2]:
        test_stub.set_host_cpu_model(i.managementIp, model='Broadwell')
        host['Broadwell'].append(i)

    for i in _hosts[2:]:
        test_stub.set_host_cpu_model(i.managementIp, model='Haswell-noTSX')
        host['Haswell-noTSX'].append(i)

    hosts = host['Broadwell'] + host['Haswell-noTSX']
    clusters = res_ops.query_resource(res_ops.CLUSTER)
    for i in clusters:
        cls_ops.delete_cluster(i.uuid)
    clusters = []
    zone = res_ops.query_resource(res_ops.ZONE)[0]
    cluster_option = test_util.ClusterOption()
    cluster_option.set_hypervisor_type('KVM')
    cluster_option.set_zone_uuid(zone.uuid)

    cluster_option.set_name('Broadwell_1')
    cluster1 = cls_ops.create_cluster(cluster_option)
    tag_ops.create_system_tag('ClusterVO',cluster1.uuid,tag="clusterKVMCpuModel::Broadwell")
    clusters.append(cluster1)

    cluster_option.set_name('Broadwell_2')
    cluster2 = cls_ops.create_cluster(cluster_option)
    tag_ops.create_system_tag('ClusterVO',cluster2.uuid,tag="clusterKVMCpuModel::Broadwell")
    clusters.append(cluster2)

    cluster_option.set_name('Haswell-noTSX_1')
    cluster3 = cls_ops.create_cluster(cluster_option)
    tag_ops.create_system_tag('ClusterVO',cluster3.uuid,tag="clusterKVMCpuModel::Haswell-noTSX")
    clusters.append(cluster3)

    conditions = res_ops.gen_query_conditions('name', '=', 'vlan-test9')
    l2 = res_ops.query_resource(res_ops.L2_VLAN_NETWORK, conditions)[0]

    conditions = res_ops.gen_query_conditions('name', '=', 'l2-public')
    l2_public = res_ops.query_resource(res_ops.L2_NETWORK, conditions)[0]

    ps = res_ops.query_resource(res_ops.PRIMARY_STORAGE)


    _hosts = []
    for i in range(len(clusters)):
        net_ops.attach_l2(l2.uuid, clusters[i].uuid)
        net_ops.attach_l2(l2_public.uuid, clusters[i].uuid)
        for j in ps:
            ps_ops.attach_primary_storage(j.uuid, clusters[i].uuid)
        host_option = test_util.HostOption()
        host_option.set_cluster_uuid(clusters[i].uuid)
        host_option.set_username('root')
        host_option.set_password('password')
        host_option.set_name(hosts[i].managementIp)
        host_option.set_management_ip(hosts[i].managementIp)
        _hosts.append(host_ops.add_kvm_host(host_option))

    # test
    host_option = test_util.HostOption()
    host_option.set_cluster_uuid(clusters[0].uuid)
    host_option.set_username('root')
    host_option.set_password('password')
    host_option.set_name(hosts[3].managementIp)
    host_option.set_management_ip(hosts[3].managementIp)
    try:
        _hosts.append(host_ops.add_kvm_host(host_option))
    except Exception as e:
        test_util.test_logger(e)

    host_option.set_cluster_uuid(clusters[2].uuid)
    try:
        _hosts.append(host_ops.add_kvm_host(host_option))
    except Exception as e:
        test_util.test_fail("test cluster cpu model faild")

    # migrate vm
    conditions = res_ops.gen_query_conditions('name', '=', 'ttylinux')
    img = res_ops.query_resource(res_ops.IMAGE, conditions)[0]
    ins = res_ops.query_resource(res_ops.INSTANCE_OFFERING)[0]
    conditions = res_ops.gen_query_conditions('name', '=', 'public network')
    l3 = res_ops.query_resource(res_ops.L3_NETWORK, conditions)[0]


    vms = []
    for i in [0,2]:
        vm_option = test_util.VmOption()
        vm_option.set_name("vm")
        vm_option.set_image_uuid(img.uuid)
        vm_option.set_cluster_uuid(clusters[i].uuid)
        vm_option.set_host_uuid(_hosts[i].uuid)
        vm_option.set_instance_offering_uuid(ins.uuid)
        vm_option.set_l3_uuids([l3.uuid])
        vm_option.set_default_l3_uuid(l3.uuid)
        vms.append(vm_ops.create_vm(vm_option))

    time.sleep(20)
    try:
        vm_ops.migrate_vm(vms[0].uuid, _hosts[1].uuid)
    except Exception as e:
        test_util.test_fail(e)

    try:
        vm_ops.migrate_vm(vms[1].uuid, _hosts[1].uuid)
    except Exception as e:
        test_util.test_logger(e)

    test_util.test_pass("test cluster cpu model pass")

def error_cleanup():
    pass
