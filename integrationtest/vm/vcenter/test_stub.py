'''

Create an unified test_stub to share test operations

@author: SyZhao
'''

import os
import subprocess
import time
import uuid

import zstacklib.utils.ssh as ssh
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.zstack_test.zstack_test_vm as zstack_vm_header
import zstackwoodpecker.zstack_test.zstack_test_volume as zstack_volume_header
import zstackwoodpecker.zstack_test.zstack_test_eip as zstack_eip_header
import zstackwoodpecker.zstack_test.zstack_test_vip as zstack_vip_header
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.operations.vcenter_operations as vc_ops
import zstackwoodpecker.operations.deploy_operations as dep_ops
import apibinding.api_actions as api_actions
import zstacklib.utils.xmlobject as xmlobject


original_root_password = "password"


def create_vm(vm_name='virt-vm', \
        image_name = None, \
        l3_name = None, \
        instance_offering_uuid = None, \
        host_uuid = None, \
        disk_offering_uuids=None, system_tags=None, \
        root_password=None, session_uuid = None):


    if not image_name:
        image_name = os.environ.get('imageName_net')
    elif os.environ.get(image_name):
        image_name = os.environ.get(image_name)

    if not l3_name:
        l3_name = os.environ.get('l3PublicNetworkName')

    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    if not instance_offering_uuid:
	instance_offering_name = os.environ.get('instanceOfferingName_m')
        instance_offering_uuid = test_lib.lib_get_instance_offering_by_name(instance_offering_name).uuid

    vm_creation_option = test_util.VmOption()
    vm_creation_option.set_l3_uuids([l3_net_uuid])
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_name(vm_name)
    vm_creation_option.set_system_tags(system_tags)
    vm_creation_option.set_data_disk_uuids(disk_offering_uuids)
    if root_password:
        vm_creation_option.set_root_password(root_password)
    if host_uuid:
        vm_creation_option.set_host_uuid(host_uuid)
    if session_uuid:
        vm_creation_option.set_session_uuid(session_uuid)

    vm = zstack_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    return vm 



def start_vm_with_host_uuid(vm_uuid, host_uuid, session_uuid=None, timeout=240000):
    action = api_actions.StartVmInstanceAction()
    action.uuid = vm_uuid
    action.hostUuid = host_uuid
    action.timeout = timeout
    test_util.action_logger('Start VM [uuid:] %s; Host [uuid:] %s' % (vm_uuid, host_uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory



def create_vm_in_vcenter(vm_name='vcenter-vm', \
        image_name = None, \
        l3_name = None, \
        instance_offering_uuid = None, \
        host_uuid = None, \
        disk_offering_uuids=None, system_tags=None, \
        root_password=None, session_uuid = None):


    if not image_name:
        image_name = os.environ.get('imageName_net')
    elif os.environ.get(image_name):
        image_name = os.environ.get(image_name)

    if not l3_name:
        l3_name = os.environ.get('l3PublicNetworkName')

    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    if not instance_offering_uuid:
	instance_offering_name = os.environ.get('instanceOfferingName_m')
        instance_offering_uuid = test_lib.lib_get_instance_offering_by_name(instance_offering_name).uuid

    vm_creation_option = test_util.VmOption()
    vm_creation_option.set_l3_uuids([l3_net_uuid])
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_name(vm_name)
    vm_creation_option.set_system_tags(system_tags)
    vm_creation_option.set_data_disk_uuids(disk_offering_uuids)
    if root_password:
        vm_creation_option.set_root_password(root_password)
    if host_uuid:
        vm_creation_option.set_host_uuid(host_uuid)
    if session_uuid:
        vm_creation_option.set_session_uuid(session_uuid)

    vm = zstack_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    return vm 


def create_user_in_vm(vm, username, password):
    """
    create non-root user with password setting
    """
    global original_root_password
    test_util.test_logger("create_user_in_vm: %s:%s" %(username, password))

    vm_ip = vm.vmNics[0].ip

    cmd = "adduser %s" % (username)
    ret, output, stderr = ssh.execute(cmd, vm_ip, "root", original_root_password, False, 22)
    if ret != 0:
        test_util.test_fail("User created failure, cmd[%s], output[%s], stderr[%s]" %(cmd, output, stderr))

    cmd = "echo -e \'%s\n%s\' | passwd %s" % (password, password, username)
    ret, output, stderr = ssh.execute(cmd, vm_ip, "root", original_root_password, False, 22)
    if ret != 0:
        test_util.test_fail("set non-root password failure, cmd[%s], output[%s], stderr[%s]" %(cmd, output, stderr))



def share_admin_resource(account_uuid_list):
    instance_offerings = res_ops.get_resource(res_ops.INSTANCE_OFFERING)
    for instance_offering in instance_offerings:
        acc_ops.share_resources(account_uuid_list, [instance_offering.uuid])
    cond = res_ops.gen_query_conditions('mediaType', '!=', 'ISO')
    images =  res_ops.query_resource(res_ops.IMAGE, cond)
    for image in images:
        acc_ops.share_resources(account_uuid_list, [image.uuid])

    root_disk_uuid = test_lib.lib_get_disk_offering_by_name(os.environ.get('rootDiskOfferingName')).uuid
    data_disk_uuid = test_lib.lib_get_disk_offering_by_name(os.environ.get('smallDiskOfferingName')).uuid

    share_list = [root_disk_uuid, data_disk_uuid]

    #l3net_uuids = res_ops.get_resource(res_ops.L3_NETWORK).uuid
    l3nets = res_ops.get_resource(res_ops.L3_NETWORK)
    for l3net in l3nets:
        l3net_uuid = l3net.uuid
        share_list.append(l3net_uuid)
    acc_ops.share_resources(account_uuid_list, share_list)

#To get common pgs amoung all the host with the same vswitch and the same pgs
#vsdic example
# vsdic = {'host3': {'switch2': ['pg5', 'pg6'], 'switch1': ['pg1', 'pg2', 'pg4'], 'switch3': ['pg9']}, 'host2': {'switch1': ['pg2', 'pg3'], 'switch2': ['pg5'], 'switch3': ['pg9']}, 'host1': {'switch1': ['pg1', 'pg2'], 'switch2': ['pg5', 'pg6']}}
def get_common_pgs(vsdic):
    res1 = []
    tmp_switches = None
    for host, v in vsdic.items():
        tmp_switches = (set(v.keys()) if not tmp_switches else tmp_switches & set(v.keys()))

    for switch in tmp_switches:
        tmp_pgs = None
        for host in vsdic:
            tmp_pgs = (set(vsdic[host][switch]) if not tmp_pgs else tmp_pgs & set(vsdic[host][switch]))
        if tmp_pgs:
            res1.extend(list(tmp_pgs))
    return map(lambda x: x.split('.')[0], res1), map(lambda x: x.split('.')[1], res1)

def check_deployed_vcenter(deploy_config, scenario_config = None, scenario_file = None):
    vc_name = os.environ.get('vcenter')
    vslist = {}

    if xmlobject.has_element(deploy_config, 'vcenter.datacenters.datacenter'):
        assert deploy_config.vcenter.name_ == vc_ops.lib_get_vcenter_by_name(vc_name).name

    for datacenter in xmlobject.safe_list(deploy_config.vcenter.datacenters.datacenter):
        if xmlobject.has_element(datacenter, 'dswitch'):
            for dswitch in xmlobject.safe_list(datacenter.dswitch):
                for dportgroup in xmlobject.safe_list(dswitch.dportgroups.dportgroup):
                    assert dportgroup.name_ == vc_ops.lib_get_vcenter_l2_by_name(dportgroup.name_).name
                    assert "L3-" + dportgroup.name_ == vc_ops.lib_get_vcenter_l3_by_name("L3-" + dportgroup.name_).name
        for cluster in xmlobject.safe_list(datacenter.clusters.cluster):
            assert cluster.name_ == vc_ops.lib_get_vcenter_cluster_by_name(cluster.name_).name
            for host in xmlobject.safe_list(cluster.hosts.host):
                vslist[host.name_] = {'vSwitch0':['VM Network.0']}
                managementIp = dep_ops.get_host_from_scenario_file(host.name_, scenario_config, scenario_file, deploy_config)
                assert managementIp == vc_ops.lib_get_vcenter_host_by_ip(managementIp).name
                assert vc_ops.lib_get_vcenter_host_by_ip(managementIp).hypervisorType == "ESX"
                if xmlobject.has_element(host, "iScsiStorage.vmfsdatastore"):
                    assert host.iScsiStorage.vmfsdatastore.name_ == vc_ops.lib_get_vcenter_primary_storage_by_name(host.iScsiStorage.vmfsdatastore.name_).name
                    assert vc_ops.lib_get_vcenter_primary_storage_by_name(host.iScsiStorage.vmfsdatastore.name_).type == "VCenter"
                    assert host.iScsiStorage.vmfsdatastore.name_ == vc_ops.lib_get_vcenter_backup_storage_by_name(host.iScsiStorage.vmfsdatastore.name_).name
                    assert vc_ops.lib_get_vcenter_backup_storage_by_name(host.iScsiStorage.vmfsdatastore.name_).type == "VCenter"
                if xmlobject.has_element(host, "vswitchs"):
                    for vswitch in xmlobject.safe_list(host.vswitchs.vswitch):
                        if vswitch.name_ == "vSwitch0":
                            for port_group in xmlobject.safe_list(vswitch.portgroup):
                                vslist[host.name_]['vSwitch0'].append(port_group.text_ + '.' + port_group.vlanId_)
                        else:
                            vslist[host.name_][vswitch.name_] = []
                            for port_group in xmlobject.safe_list(vswitch.portgroup):
                                vslist[host.name_][vswitch.name_].append(port_group.text_ + '.' + port_group.vlanId_)
                for vm in xmlobject.safe_list(host.vms.vm):
                    assert vm.name_ == vc_ops.lib_get_vm_by_name(vm.name_).name
                    assert vc_ops.lib_get_vm_by_name(vm.name_).hypervisorType == "ESX"
                    assert vc_ops.lib_get_vm_by_name(vm.name_).state == "Running"
        for template in xmlobject.safe_list(datacenter.templates.template):
            templ_name = template.path_
            tp_name = templ_name.split('/')[-1].split('.')[0]
            assert tp_name == vc_ops.lib_get_root_image_by_name(tp_name).name
        pg_list, vlan_list = get_common_pgs(vslist)
        for pg in pg_list:
            assert pg == vc_ops.lib_get_vcenter_l2_by_name(pg).name
            assert "L3-" + pg == vc_ops.lib_get_vcenter_l3_by_name("L3-" + pg).name
