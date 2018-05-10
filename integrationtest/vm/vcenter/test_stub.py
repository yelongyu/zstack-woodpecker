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
	instance_offering_name = os.environ.get('instanceOfferingName_s')
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
        timeout = 1200000, \
        root_password=None, session_uuid = None):


    if not image_name:
        image_name = os.environ.get('imageName_net')
    elif os.environ.get(image_name):
        image_name = os.environ.get(image_name)

    if not l3_name:
        l3_name = os.environ.get('l3PublicNetworkName')

    image = test_lib.lib_get_image_by_name(image_name)
    image_uuid = image.uuid
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    datastore_type = vc_ops.get_datastore_type(os.environ['vcenter'])
    if datastore_type == 'local':
        cond = res_ops.gen_query_conditions('image.uuid', '=', image_uuid)
        vcbs = res_ops.query_resource(res_ops.VCENTER_BACKUP_STORAGE, cond)[0]
        vcps = vc_ops.lib_get_vcenter_primary_storage_by_name(vcbs.name)
        cond = res_ops.gen_query_conditions("name", '=', l3_name)
        l3_inv = res_ops.query_resource(res_ops.L3_NETWORK, cond)
        for l3_net in l3_inv:
            cond = res_ops.gen_query_conditions("uuid", '=', l3_net.l2NetworkUuid)
            l2 = res_ops.query_resource(res_ops.L2_NETWORK, cond)[0]
            if l2.attachedClusterUuids == vcps.attachedClusterUuids:
                l3_net_uuid = l3_net.uuid
                break   
    if not instance_offering_uuid:
	instance_offering_name = os.environ.get('instanceOfferingName_s')
        instance_offering_uuid = test_lib.lib_get_instance_offering_by_name(instance_offering_name).uuid

    vm_creation_option = test_util.VmOption()
    vm_creation_option.set_l3_uuids([l3_net_uuid])
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_name(vm_name)
    vm_creation_option.set_system_tags(system_tags)
    vm_creation_option.set_data_disk_uuids(disk_offering_uuids)
    vm_creation_option.set_timeout(timeout)
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
def get_pgs(vsdic):
    res1 = []
    res2 = []
    #tmp_switches get common vswitches
    tmp_switches = None
    for host, v in vsdic.items():
        tmp_switches = (set(v.keys()) if not tmp_switches else tmp_switches & set(v.keys()))

    for host, v in vsdic.items():
        non_common_switches = (tmp_switches ^ set(v.keys()))
        for non_common_switch in non_common_switches:
            if vsdic[host][non_common_switch]:
                res2.extend(vsdic[host][non_common_switch])

    for switch in tmp_switches:
        #tmp_pgs get common pgs
        tmp_pgs = None
        for host in vsdic:
            tmp_pgs = (set(vsdic[host][switch]) if not tmp_pgs else tmp_pgs & set(vsdic[host][switch]))
        if tmp_pgs:
            res1.extend(list(tmp_pgs))
        for host in vsdic:
            non_common_pgs = (set(vsdic[host][switch]) ^ tmp_pgs)
            if non_common_pgs:
                res2.extend(non_common_pgs)
    
    return res1, res2



def check_deployed_vcenter(deploy_config, scenario_config = None, scenario_file = None):
    vc_name = os.environ.get('vcenter')
    vslist = {}

    if xmlobject.has_element(deploy_config, 'vcenter.datacenters.datacenter'):
        assert deploy_config.vcenter.name_ == vc_ops.lib_get_vcenter_by_name(vc_name).name

    for datacenter in xmlobject.safe_list(deploy_config.vcenter.datacenters.datacenter):
        dportgroup_list = []
        if xmlobject.has_element(datacenter, 'dswitch'):
            for dswitch in xmlobject.safe_list(datacenter.dswitch):
                for dportgroup in xmlobject.safe_list(dswitch.dportgroups.dportgroup):
                    dportgroup_list.append(dportgroup.name_)
        for cluster in xmlobject.safe_list(datacenter.clusters.cluster):
            sign = None
            assert cluster.name_ == vc_ops.lib_get_vcenter_cluster_by_name(cluster.name_).name
            cluster_uuid = vc_ops.lib_get_vcenter_cluster_by_name(cluster.name_).uuid
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
                if xmlobject.has_element(host, "dswitchRef"):
                    sign = 1
                for vm in xmlobject.safe_list(host.vms.vm):
                    assert vm.name_ == vc_ops.lib_get_vm_by_name(vm.name_).name
                    assert vc_ops.lib_get_vm_by_name(vm.name_).hypervisorType == "ESX"
                    assert vc_ops.lib_get_vm_by_name(vm.name_).state == "Running"
            if xmlobject.has_element(cluster, "templates"):
                for template in xmlobject.safe_list(cluster.templates.template):
                    templ_name = template.path_
                    tp_name = templ_name.split('/')[-1].split('.')[0]
                    assert tp_name == vc_ops.lib_get_root_image_by_name(tp_name).name
            for dportgroup_name in dportgroup_list:
               if sign:
                    l2 = vc_ops.lib_get_vcenter_l2_by_name_and_cluster(dportgroup_name, cluster_uuid)
                    assert dportgroup_name == l2.name
                    assert "L3-" + dportgroup_name == vc_ops.lib_get_vcenter_l3_by_name_and_l2("L3-" + dportgroup_name, l2.uuid).name
            pg_vlan_list, non_pg_vlan_list = get_pgs(vslist)
            for pg_vlan in pg_vlan_list:
                pg = pg_vlan.split('.')[0]
                vlan = pg_vlan.split('.')[1]
                l2 = vc_ops.lib_get_vcenter_l2_by_name_and_cluster(pg, cluster_uuid)
                assert pg == l2.name
                if l2.vlan:                    
                    assert vlan == str(l2.vlan)
                assert "L3-" + pg == vc_ops.lib_get_vcenter_l3_by_name_and_l2("L3-" + pg, l2.uuid).name
            for non_pg_vlan in non_pg_vlan_list:
                non_pg = non_pg_vlan.split('.')[0]
                assert vc_ops.lib_get_vcenter_l2_by_name_and_cluster(non_pg, cluster_uuid) == None

                


def create_volume(volume_creation_option=None, session_uuid = None):
    if not volume_creation_option:
        disk_offering = test_lib.lib_get_disk_offering_by_name(os.environ.get('smallDiskOfferingName'))
        volume_creation_option = test_util.VolumeOption()
        volume_creation_option.set_disk_offering_uuid(disk_offering.uuid)
        volume_creation_option.set_name('test_vcenter_volume')

    volume_creation_option.set_session_uuid(session_uuid)
    volume = zstack_volume_header.ZstackTestVolume()
    volume.set_creation_option(volume_creation_option)
    volume.create()
    return volume

def set_httpd_in_vm(vm, ip):
    cmd = "systemctl start httpd; iptables -F; echo %s > /var/www/html/index.html" % ip
    test_lib.lib_execute_command_in_vm(vm, cmd)
