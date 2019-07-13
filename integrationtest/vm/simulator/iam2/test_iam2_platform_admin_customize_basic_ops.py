'''
test iam2 platform admin basic operations
@author: zhaohao.chen
'''
import os
import zstackwoodpecker.test_util as test_util
import apibinding.inventory as inventory
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.operations.iam2_operations as iam2_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.operations.scheduler_operations as schd_ops
import zstackwoodpecker.operations.vxlan_operations as vxlan_ops
import zstackwoodpecker.test_lib as test_lib
import time
virtual_id_uuid = None
test_stub = test_lib.lib_get_test_stub()

cond = res_ops.gen_query_conditions('name', '=', 'Platform admin role')
pltadm_statement = res_ops.query_resource(res_ops.ROLE, cond)[0].statements[0].statement


def basic_ops(session_uuid, prj_linked_account_uuid=None):
    #Image related ops: Add, Delete, Expunge, sync image size, Update QGA, delete, expunge
    bs = res_ops.query_resource(res_ops.BACKUP_STORAGE)[0]
    image_option = test_util.ImageOption()
    image_option.set_name('fake_image')
    image_option.set_description('fake image')
    image_option.set_format('raw')
    image_option.set_mediaType('RootVolumeTemplate')
    image_option.set_backup_storage_uuid_list([bs.uuid])
    image_option.url = "http://fake/fake.raw"
    image_option.set_session_uuid(session_uuid)
    image_uuid = img_ops.add_image(image_option).uuid
    img_ops.sync_image_size(image_uuid, session_uuid=session_uuid)
    img_ops.change_image_state(image_uuid, 'disable', session_uuid=session_uuid)
    img_ops.change_image_state(image_uuid, 'enable', session_uuid=session_uuid)
    if bs.type == inventory.IMAGE_STORE_BACKUP_STORAGE_TYPE:
        img_ops.export_image_from_backup_storage(image_uuid, bs.uuid, session_uuid=session_uuid)
        img_ops.delete_exported_image_from_backup_storage(image_uuid, bs.uuid, session_uuid=session_uuid)
    img_ops.set_image_qga_enable(image_uuid, session_uuid=session_uuid)
    img_ops.set_image_qga_disable(image_uuid, session_uuid=session_uuid)
    img_ops.delete_image(image_uuid, session_uuid=session_uuid)
    img_ops.expunge_image(image_uuid, session_uuid=session_uuid)

    # Volume related ops: Create, Delete, Expunge, Attach, Dettach, Enable, Disable
    disk_offering_uuid = res_ops.query_resource(res_ops.DISK_OFFERING)[0].uuid
    volume_option = test_util.VolumeOption()
    volume_option.set_disk_offering_uuid(disk_offering_uuid)
    volume_option.set_name('data_volume_iam2_pf_adm')
    volume_option.set_session_uuid(session_uuid)
    data_volume = vol_ops.create_volume_from_offering(volume_option)
    vol_ops.stop_volume(data_volume.uuid, session_uuid=session_uuid)
    vol_ops.start_volume(data_volume.uuid, session_uuid=session_uuid)
    vm_creation_option = test_util.VmOption()
    l3_net_uuid = test_lib.lib_get_l3_by_name(os.environ.get('l3VlanNetwork3')).uuid
    vm_creation_option.set_l3_uuids([l3_net_uuid])
    image_uuid = test_lib.lib_get_image_by_name("centos").uuid
    vm_creation_option.set_image_uuid(image_uuid)
    instance_offering_uuid = test_lib.lib_get_instance_offering_by_name(os.environ.get('instanceOfferingName_s')).uuid
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_name('vm_iam2_pf_adm')
    vm_creation_option.set_session_uuid(session_uuid)
    vm = test_stub.create_vm(image_uuid = image_uuid, session_uuid=session_uuid) 
    vm_uuid = vm.get_vm().uuid
    vol_ops.attach_volume(data_volume.uuid, vm_uuid, session_uuid=session_uuid)
    vol_ops.detach_volume(data_volume.uuid, vm_uuid, session_uuid=session_uuid)
    vol_ops.delete_volume(data_volume.uuid, session_uuid=session_uuid)
    vol_ops.expunge_volume(data_volume.uuid, session_uuid=session_uuid)

    # L2 related ops: create, delete, attach
    vxlan_pool_uuid = None
    if prj_linked_account_uuid:
        zone_uuid = res_ops.get_resource(res_ops.ZONE)[0].uuid
        cluster_uuid = res_ops.get_resource(res_ops.CLUSTER)[0].uuid
        vxlan_pool_name = 'vxlan_pool_name'
        vxlan_pool_uuid = vxlan_ops.create_l2_vxlan_network_pool(vxlan_pool_name,zone_uuid).uuid
        vxlan_ops.create_vni_range('vni_range',20,40,vxlan_pool_uuid)
        acc_ops.share_resources([prj_linked_account_uuid], [vxlan_pool_uuid])
        systemTags = ["l2NetworkUuid::%s::clusterUuid::%s::cidr::{192.168.0.1/16}"%(vxlan_pool_uuid,cluster_uuid)]
        net_ops.attach_l2_vxlan_pool(vxlan_pool_uuid,cluster_uuid,systemTags)
        l2_uuid = vxlan_ops.create_l2_vxlan_network('l2_vxlan',vxlan_pool_uuid,zone_uuid,session_uuid=session_uuid).uuid
    else:
        zone_uuid = res_ops.get_resource(res_ops.ZONE)[0].uuid
        l2 = net_ops.create_l2_vlan('l2_iam2_pf_adm', 'eth0', zone_uuid, 1234, session_uuid=session_uuid)
        l2_uuid = l2.inventory.uuid
        cluster_uuid = res_ops.query_resource(res_ops.CLUSTER)[0].uuid 
        net_ops.attach_l2(l2_uuid, cluster_uuid)

    #L3 related ops:create, attach, detach, delete
    ip_range_option = test_util.IpRangeOption()
    l3_name = 'l3_test'
    category = 'Private'
    type = 'L3BasicNetwork'
    l3_uuid = net_ops.create_l3(l3_name, l2_uuid, category=category, Type=type, session_uuid=session_uuid).uuid
    cond = res_ops.gen_query_conditions('type','=','VirtualRouter')
    service_uuid = res_ops.query_resource(res_ops.NETWORK_SERVICE_PROVIDER, cond)[0].uuid
    net_ops.attach_pf_service_to_l3network(l3_uuid, service_uuid, snat=True)
    net_ops.attach_lb_service_to_l3network(l3_uuid, service_uuid)
    ip_range_option.set_name('iprange_test')
    ip_range_option.set_l3_uuid(l3_uuid)
    ip_range_option.set_startIp('192.168.0.10')
    ip_range_option.set_endIp('192.168.0.15')
    ip_range_option.set_gateway('192.168.0.1')
    ip_range_option.set_netmask('255.255.255.0')
    net_ops.add_ip_range(ip_range_option, session_uuid=session_uuid)
    nics = net_ops.attach_l3(l3_uuid, vm_uuid, session_uuid=session_uuid).vmNics
    for nic in nics:
        if nic.l3NetworkUuid == l3_uuid:
            nic_uuid = nic.uuid
            break

    # network service ops:sg, vip, eip, port forwarding, lb, lb listener, IPsec tunnel
    # sg
    cond = res_ops.gen_query_conditions('type','=','SecurityGroup')
    network_provider_uuid = res_ops.query_resource(res_ops.NETWORK_SERVICE_PROVIDER, cond)[0].uuid
    net_ops.attach_sg_service_to_l3network(l3_uuid, network_provider_uuid, session_uuid=session_uuid)
    sg_name = 'sg_test'
    sg_creation_option = test_util.SecurityGroupOption()
    sg_creation_option.set_name(sg_name)
    sg_creation_option.set_ipVersion(4)
    sg_creation_option.set_session_uuid(session_uuid)
    sg_uuid = net_ops.create_security_group(sg_creation_option).uuid
    rule_test = {"allowedCidr": "0.0.0.0/0",
                 "endPort": 9528,
                 "ipVersion": 4,
                 "protocol": "TCP",
                 "securityGroupUuid": sg_uuid,
                 "startPort": 9527,
                 "state": "Enabled",
                 "type": "Ingress"}
    rules = net_ops.add_rules_to_security_group(sg_uuid, [rule_test], session_uuid=session_uuid).rules
    net_ops.attach_security_group_to_l3(sg_uuid, l3_uuid, session_uuid=session_uuid)
    net_ops.detach_security_group_from_l3(sg_uuid, l3_uuid, session_uuid=session_uuid)
    net_ops.delete_security_group(sg_uuid, session_uuid=session_uuid)

    #vip
    l3_name_new = 'l3_test_new'
    l3_uuid_new = net_ops.create_l3(l3_name_new, l2_uuid, category=category, Type=type, session_uuid=session_uuid).uuid
    ip_range_option.set_name('iprange_test_new')
    ip_range_option.set_l3_uuid(l3_uuid_new)
    ip_range_option.set_startIp('192.168.1.20')
    ip_range_option.set_endIp('192.168.1.25')
    ip_range_option.set_gateway('192.168.1.1')
    ip_range_option.set_netmask('255.255.255.0')
    net_ops.add_ip_range(ip_range_option, session_uuid=session_uuid)
    vip_name = 'vip_test'
    vip_creation_option = test_util.VipOption()
    vip_creation_option.set_l3_uuid(l3_uuid_new)
    vip_creation_option.set_name(vip_name)
    vip_creation_option.set_session_uuid(session_uuid)
    vip_uuid = net_ops.create_vip(vip_creation_option).uuid
    net_ops.set_vip_qos(vip_uuid, inboundBandwidth=2, outboundBandwidth=2, session_uuid=session_uuid)
    net_ops.get_vip_qos(vip_uuid, session_uuid=session_uuid)
    net_ops.delete_vip_qos(vip_uuid, session_uuid=session_uuid)

    #eip
    cond = res_ops.gen_query_conditions('type', '=', 'Flat')
    network_provider_uuid = res_ops.query_resource(res_ops.NETWORK_SERVICE_PROVIDER, cond)[0].uuid
    net_ops.attach_eip_service_to_l3network(l3_uuid, network_provider_uuid, session_uuid=session_uuid)
    net_ops.attach_eip_service_to_l3network(l3_uuid_new, network_provider_uuid, session_uuid=session_uuid)
    eip_name = 'eip_test'
    eip_creation_option = test_util.EipOption()
    eip_creation_option.set_session_uuid(session_uuid)
    eip_creation_option.set_name(eip_name)
    eip_creation_option.set_vip_uuid(vip_uuid)
    eip_creation_option.set_vm_nic_uuid(nic_uuid)
    eip_uuid = net_ops.create_eip(eip_creation_option).uuid
    net_ops.detach_eip(eip_uuid, session_uuid=session_uuid)
    net_ops.attach_eip(eip_uuid, nic_uuid, session_uuid=session_uuid)

    #port forwarding
    cond = res_ops.gen_query_conditions('category','=','Public')
    l3_pub_uuid = res_ops.query_resource(res_ops.L3_NETWORK, cond)[0].uuid
    vip_pf_name = 'vip_pf'
    vip_creation_option.set_l3_uuid(l3_pub_uuid)
    vip_creation_option.set_name(vip_pf_name)
    vip_pf_uuid = net_ops.create_vip(vip_creation_option).uuid
    pf_name = 'pf_test'
    pf_creation_option = test_util.PortForwardingRuleOption()
    pf_creation_option.set_name(pf_name)
    pf_creation_option.set_session_uuid(session_uuid)
    pf_creation_option.set_vip_ports(9527,9528)
    pf_creation_option.set_private_ports(9527,9528)
    pf_creation_option.set_protocol('TCP')
    pf_creation_option.set_allowedCidr('192.168.5.1/24')
    pf_creation_option.set_vip_uuid(vip_pf_uuid)
    pf_uuid = net_ops.create_port_forwarding(pf_creation_option).uuid
    net_ops.attach_port_forwarding(pf_uuid, nic_uuid, session_uuid=session_uuid)
    net_ops.detach_port_forwarding(pf_uuid, session_uuid=session_uuid)

    #LB
    vip_lb_name = 'vip_lb'
    vip_creation_option.set_name(vip_lb_name)
    vip_lb_uuid = net_ops.create_vip(vip_creation_option).uuid
    lb_uuid = net_ops.create_load_balancer(vip_lb_uuid, vip_lb_name, session_uuid=session_uuid).uuid
    
    #LB Listener
    lbl_name = 'lbl_test'
    lbl_creation_option = test_util.LoadBalancerListenerOption()
    lbl_creation_option.set_session_uuid(session_uuid)
    lbl_creation_option.set_name(lbl_name)
    lbl_creation_option.set_protocol('tcp')
    lbl_creation_option.set_load_balancer_uuid(lb_uuid)
    lbl_creation_option.set_load_balancer_port(9527)
    lbl_uuid = net_ops.create_load_balancer_listener(lbl_creation_option).uuid
    net_ops.add_nic_to_load_balancer(lbl_uuid, [nic_uuid], session_uuid=session_uuid)
    net_ops.remove_nic_from_load_balancer(lbl_uuid, [nic_uuid], session_uuid=session_uuid)
    # zwatch ops:

    #scheduler ops:
    start_date = int(time.time())
    schd_job1 = schd_ops.create_scheduler_job('simple_start_vm_scheduler', 'simple_start_vm_scheduler', vm_uuid, 'startVm', None, session_uuid=session_uuid)
    schd_trigger1 = schd_ops.create_scheduler_trigger('simple_start_vm_scheduler', start_date+5, None, 15, 'simple', session_uuid=session_uuid)
    schd_ops.add_scheduler_job_to_trigger(schd_trigger1.uuid, schd_job1.uuid, session_uuid=session_uuid)
    schd_ops.change_scheduler_state(schd_job1.uuid, 'disable', session_uuid=session_uuid)
    schd_ops.change_scheduler_state(schd_job1.uuid, 'enable', session_uuid=session_uuid)
    schd_ops.remove_scheduler_job_from_trigger(schd_trigger1.uuid, schd_job1.uuid, session_uuid=session_uuid)
    schd_ops.del_scheduler_job(schd_job1.uuid, session_uuid=session_uuid)
    schd_ops.del_scheduler_trigger(schd_trigger1.uuid, session_uuid=session_uuid)
    schd_ops.get_current_time()
    #certificate
    cert = net_ops.create_certificate('certificate_for_pm', 'fake certificate', session_uuid=session_uuid)
    net_ops.delete_certificate(cert.uuid, session_uuid=session_uuid)

    # delete:l2,l3,network services
    net_ops.delete_load_balancer_listener(lbl_uuid, session_uuid=session_uuid)
    net_ops.delete_load_balancer(lb_uuid, session_uuid=session_uuid)
    net_ops.delete_port_forwarding(pf_uuid, session_uuid=session_uuid)
    net_ops.delete_eip(eip_uuid, session_uuid=session_uuid)
    net_ops.delete_vip(vip_lb_uuid, session_uuid=session_uuid)
    net_ops.delete_vip(vip_pf_uuid, session_uuid=session_uuid)
    net_ops.delete_vip(vip_uuid, session_uuid=session_uuid)
    net_ops.detach_l3(nic_uuid, session_uuid=session_uuid)
    net_ops.delete_l3(l3_uuid_new, session_uuid=session_uuid)
    net_ops.delete_l3(l3_uuid, session_uuid=session_uuid)
    if not prj_linked_account_uuid:
        net_ops.detach_l2(l2_uuid, cluster_uuid, session_uuid=session_uuid)
    net_ops.delete_l2(l2_uuid, session_uuid=session_uuid)
    if vxlan_pool_uuid:
        net_ops.delete_l2(vxlan_pool_uuid)
    # VM related ops: Create, Delete, Expunge, Start, Stop, Suspend, Resume, Migrate
    vm_ops.stop_vm(vm_uuid, session_uuid=session_uuid)
    vm_ops.start_vm(vm_uuid, session_uuid=session_uuid)
    candidate_hosts = vm_ops.get_vm_migration_candidate_hosts(vm_uuid)
    if candidate_hosts != None and test_lib.lib_check_vm_live_migration_cap(vm.get_vm()):
        vm_ops.migrate_vm(vm_uuid, candidate_hosts.inventories[0].uuid, session_uuid=session_uuid)
    vm_ops.stop_vm(vm_uuid, force='cold', session_uuid=session_uuid)
    vm_ops.start_vm(vm_uuid, session_uuid=session_uuid)
    vm_ops.suspend_vm(vm_uuid, session_uuid=session_uuid)
    vm_ops.resume_vm(vm_uuid, session_uuid=session_uuid)
    vm_ops.destroy_vm(vm_uuid, session_uuid=session_uuid)
    vm_ops.expunge_vm(vm_uuid, session_uuid=session_uuid)
    

def test():
    global virtual_id_uuid
    iam2_ops.clean_iam2_enviroment()
    #create vid
    username = "platform admin test"
    password = 'b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86'
    virtual_id_uuid = iam2_ops.create_iam2_virtual_id(username, password).uuid
    #add role to vid
    role_name = 'platform_admin_customize'
    role_uuid = iam2_ops.create_role(role_name, statements=[pltadm_statement]).uuid
    iam2_ops.add_roles_to_iam2_virtual_id([role_uuid], virtual_id_uuid)
    session_uuid = iam2_ops.login_iam2_virtual_id(username, password)
    basic_ops(session_uuid)
    #delete
    acc_ops.logout(session_uuid)
    iam2_ops.delete_iam2_virtual_id(virtual_id_uuid)
    test_util.test_pass('success test iam2 platform admin basic operations!')

def error_cleanup():
    global virtual_id_uuid
    if virtual_id_uuid:
        iam2_ops.delete_iam2_virtual_id(virtual_id_uuid)
