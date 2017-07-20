'''

New Integration Test for hybrid.

@author: Legion
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.hybrid_operations as hyb_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.ipsec_operations as ipsec_ops
import time
import os
import commands

date_s = time.strftime('%m%d-%H%M%S', time.localtime())
test_obj_dict = test_state.TestStateDict()
ks_inv = None
datacenter_inv = None
test_stub = test_lib.lib_get_test_stub()
sg_inv = None
ecs_inv = None
ipsec_inv = None
bucket_inv = None
ecs_eip_inv = None
vswitch_inv = None
user_vpn_gw_inv = None
route_entry_inv = None
ipsec_vpn_inv_connection = None

def test():
    global ks_inv
    global datacenter_inv
    global sg_inv
    global ecs_inv
    global ecs_eip_inv
    global ipsec_inv
    global bucket_inv
    global vswitch_inv
    global user_vpn_gw_inv
    global route_entry_inv
    global ipsec_vpn_inv_connection
    public_ip_list = []
    cond_offering = res_ops.gen_query_conditions('name', '=', os.getenv('instanceOfferingName_m'))
    instance_offering = res_ops.query_resource(res_ops.INSTANCE_OFFERING, cond_offering)[0]
    # Create VM
    vm = test_stub.create_vlan_vm(os.environ.get('l3VlanNetworkName1'))
    test_obj_dict.add_vm(vm)
    vm.check()
    vm_ip = vm.vm.vmNics[0].ip
    pri_l3_uuid = vm.vm.vmNics[0].l3NetworkUuid
    vr = test_lib.lib_find_vr_by_l3_uuid(pri_l3_uuid)[0]
    l3_uuid = test_lib.lib_find_vr_pub_nic(vr).l3NetworkUuid
    vip_existed = res_ops.query_resource(res_ops.VIP)
    # Create Vip
    if vip_existed:
        vip = vip_existed[0]
    else:
        vip = test_stub.create_vip('ipsec_vip', l3_uuid).get_vip()
    cond = res_ops.gen_query_conditions('uuid', '=', pri_l3_uuid)
    zstack_cidrs = res_ops.query_resource(res_ops.L3_NETWORK, cond)[0].ipRanges[0].networkCidr
#     _vm_ip = zstack_cidrs.replace('1/', '254/')
#     cmd = 'ip a add dev br_eth0_1101 %s' % _vm_ip
#     commands.getoutput(cmd)
    datacenter_type = os.getenv('datacenterType')
    vpc_id = os.getenv('ecs_vpcId')
    vpc_vr_id = os.getenv('vpc_vrId')
    vpn_gateway_id = os.getenv('vpn_gatewayId')
    # Get Public IP for IPsec connection
    for i in ['ipRangeStartIp', 'ipRangeEndIp']:
        public_ip_list.append(os.environ.get(i))
    vr_nics = res_ops.query_resource(res_ops.VIRTUALROUTER_VM)[0].vmNics
    for nic in vr_nics:
        if nic.ip in public_ip_list:
            public_ip_list.remove(nic.ip)
    ks_existed = hyb_ops.query_aliyun_key_secret()
    # Add Aliyun key & secret
    if not ks_existed:
        ks_inv = hyb_ops.add_aliyun_key_secret('test_hybrid', 'test for hybrid', os.getenv('aliyunKey'), os.getenv('aliyunSecret'))
    datacenter_local = hyb_ops.query_datacenter_local()
    # Clear datacenter remained in local
    if datacenter_local:
        for d in datacenter_local:
            hyb_ops.del_datacenter_in_local(d.uuid)
    datacenter_list = hyb_ops.get_datacenter_from_remote(datacenter_type)
    regions = [ i.regionId for i in datacenter_list]
    for r in regions:
        if 'shanghai' in r:
            region_id = r
    datacenter_inv = hyb_ops.add_datacenter_from_remote(datacenter_type, region_id, 'datacenter for test')
    bucket_inv = hyb_ops.create_oss_bucket_remote(datacenter_inv.uuid, 'zstack-test-%s-%s' % (date_s, region_id), 'created-by-zstack-for-test')
    hyb_ops.attach_oss_bucket_to_ecs_datacenter(bucket_inv.uuid)
    iz_list = hyb_ops.get_identity_zone_from_remote(datacenter_type, region_id)
    zone_id = iz_list[-1].zoneId
    iz_inv = hyb_ops.add_identity_zone_from_remote(datacenter_type, datacenter_inv.uuid, zone_id)
    hyb_ops.sync_ecs_vpc_from_remote(datacenter_inv.uuid)
    vpc_local = hyb_ops.query_ecs_vpc_local()
    # Get Vpc which has available gateway
    for vl in vpc_local:
        if vl.ecsVpcId == vpc_id:
            vpc_inv = vl
    # Sync Aliyun image to local
    hyb_ops.sync_ecs_image_from_remote(datacenter_inv.uuid, image_type='system')
    ecs_image = hyb_ops.query_ecs_image_local()
    for i in ecs_image:
        if i.platform == 'CentOS':
            image = i
            break
    # Get Vpn gateway
    hyb_ops.sync_vpc_vpn_gateway_from_remote(datacenter_inv.uuid)
    vpc_vpn_gw_local = hyb_ops.query_vpc_vpn_gateway_local()
    for gw in vpc_vpn_gw_local:
        if gw.vpnGatewayId == vpn_gateway_id:
            vpn_gateway = gw
    # Create vSwitch
    hyb_ops.sync_ecs_vswitch_from_remote(datacenter_inv.uuid)
    vswitch_local = hyb_ops.query_ecs_vswitch_local()
    ecs_vswitch = [vs for vs in vswitch_local if vs.cidrBlock == '192.168.252.0/24']
    if ecs_vswitch:
        vswitch_inv = ecs_vswitch[0]
    else:
        vswitch_inv = hyb_ops.create_ecs_vswtich_remote(vpc_inv.uuid, iz_inv.uuid, 'zstack-test-vswitch', '192.168.252.0/24')
        time.sleep(5)
    # Create Vpc Security Group
    sg_inv = hyb_ops.create_ecs_security_group_remote('sg_for_test', vpc_inv.uuid)
    time.sleep(5)
    hyb_ops.create_ecs_security_group_rule_remote(sg_inv.uuid, 'ingress', 'ALL', '-1/-1', '0.0.0.0/0', 'accept', 'intranet', '10')
    hyb_ops.create_ecs_security_group_rule_remote(sg_inv.uuid, 'egress', 'ALL', '-1/-1', '0.0.0.0/0', 'accept', 'intranet', '10')
    time.sleep(5)
    # Create Vpc User Gateway
    user_vpn_gw_inv = hyb_ops.create_vpc_user_vpn_gateway(datacenter_inv.uuid, gw_ip=public_ip_list[0], gw_name="zstack-test-user-vpn-gateway")
    # Create Ecs
    ecs_inv = hyb_ops.create_ecs_instance_from_ecs_image('Password123', image.uuid, vswitch_inv.uuid, instance_offering.uuid, ecs_bandwidth=5,
                                                         ecs_security_group_uuid=sg_inv.uuid, allocate_public_ip='true', name='zstack-ecs-test')
    time.sleep(10)
    # Get Ecs Public IP
    ecs_instance_local = hyb_ops.query_ecs_instance_local()
    ecs_inv = [e for e in ecs_instance_local if e.name == 'zstack-ecs-test'][0]
    eip_local = hyb_ops.query_hybrid_eip_local()
    ecs_eip_inv = [e for e in eip_local if e.allocateResourceUuid == ecs_inv.uuid][0]
    time.sleep(10)
    # Get Aliyun virtual router
    hyb_ops.sync_aliyun_virtual_router_from_remote(vpc_inv.uuid)
    vr_local = hyb_ops.query_aliyun_virtual_router_local()
    for v in vr_local:
        if v.vrId == vpc_vr_id:
            vr = v
    # Create Hybrid IPsec Vpn connection
    vpn_ike_config = hyb_ops.create_vpn_ike_ipsec_config(name='zstack-test-vpn-ike-config', psk='zstack.hybrid.test123', local_ip=vpn_gateway.publicIp, remote_ip=user_vpn_gw_inv.ip)
    vpn_ipsec_config = hyb_ops.create_vpn_ipsec_config(name='zstack-test-vpn-ike-config')
    ipsec_vpn_inv_connection = hyb_ops.create_vpc_vpn_connection(user_vpn_gw_inv.uuid, vpn_gateway.uuid, 'zstack-test-ipsec-vpn-connection', '192.168.252.0/24',
                                      zstack_cidrs, vpn_ike_config.uuid, vpn_ipsec_config.uuid)
    # Create ZStack IPsec Vpn connection
    ipsec_conntion = hyb_ops.query_ipsec_connection()
    if ipsec_conntion:
        ipsec_inv = ipsec_conntion[0]
    else:
        ipsec_inv = ipsec_ops.create_ipsec_connection('ipsec', pri_l3_uuid, vpn_gateway.publicIp, 'zstack.hybrid.test123', vip.uuid, ['192.168.252.0/24'],
                                                      ike_dh_group=2, ike_encryption_algorithm='3des', policy_encryption_algorithm='3des')
    # Add route entry
    route_entry_inv = hyb_ops.create_aliyun_vpc_virtualrouter_entry_remote(zstack_cidrs.replace('1/', '0/'), vr.uuid, vrouter_type='vrouter', next_hop_type='Tunnel', next_hop_uuid=vpn_gateway.uuid)
    ping_ecs_cmd = "sshpass -p password ssh -o StrictHostKeyChecking=no root@%s 'ping %s -c 5 | grep time='" % (vm_ip, ecs_inv.privateIpAddress)
    # ZStack VM ping Ecs
    ping_ecs_cmd_status = commands.getstatusoutput(ping_ecs_cmd)[0]
    assert ping_ecs_cmd_status == 0
    ping_vm_cmd = "sshpass -p Password123 ssh -o StrictHostKeyChecking=no root@%s 'ping %s -c 5 | grep time='" % (ecs_eip_inv.eipAddress, vm_ip)
    # Ecs ping ZStack VM
    ping_vm_cmd_status = commands.getstatusoutput(ping_vm_cmd)[0]
    assert ping_vm_cmd_status == 0
    test_util.test_pass('Create hybrid IPsec Vpn Connection Test Success')

def env_recover():
    global ecs_inv
    global datacenter_inv
    if ecs_inv:
        time.sleep(10)
        hyb_ops.stop_ecs_instance(ecs_inv.uuid)
        for _ in xrange(600):
            hyb_ops.sync_ecs_instance_from_remote(datacenter_inv.uuid)
            ecs_inv = [e for e in hyb_ops.query_ecs_instance_local() if e.name == 'zstack-ecs-test'][0]
            if ecs_inv.ecsStatus.lower() == "stopped":
                break
            else:
                time.sleep(1)
        hyb_ops.del_ecs_instance(ecs_inv.uuid)

    global ecs_eip_inv
    if ecs_eip_inv:
        hyb_ops.del_hybrid_eip_remote(ecs_eip_inv.uuid)

    global ipsec_inv
    if ipsec_inv:
        ipsec_ops.delete_ipsec_connection(ipsec_inv.uuid)

    global ipsec_vpn_inv_connection
    if ipsec_vpn_inv_connection:
        hyb_ops.del_vpc_vpn_connection_remote(ipsec_vpn_inv_connection.uuid)

    vpc_ike_config_local = hyb_ops.query_vpc_vpn_ike_config_local()
    vpc_ipsec_config_local = hyb_ops.query_vpc_vpn_ipsec_config_local()
    if vpc_ike_config_local:
        for ike in vpc_ike_config_local:
            hyb_ops.del_vpc_ike_config_local(ike.uuid)
    if vpc_ipsec_config_local:
        for ipsec_config in vpc_ipsec_config_local:
            hyb_ops.del_vpc_ipsec_config_local(ipsec_config.uuid)

    global sg_inv
    if sg_inv:
        time.sleep(30)
        hyb_ops.del_ecs_security_group_remote(sg_inv.uuid)

    global route_entry_inv
    if route_entry_inv:
        hyb_ops.del_aliyun_route_entry_remote(route_entry_inv.uuid)

    global user_vpn_gw_inv
    if user_vpn_gw_inv:
        time.sleep(5)
        hyb_ops.del_vpc_user_vpn_gateway_remote(user_vpn_gw_inv.uuid)

    global vswitch_inv
    if vswitch_inv:
        time.sleep(10)
        hyb_ops.del_ecs_vswitch_remote(vswitch_inv.uuid)

    global iz_inv
    if iz_inv:
        hyb_ops.del_identity_zone_in_local(iz_inv.uuid)

    global bucket_inv
    if bucket_inv:
        bucket_file = hyb_ops.get_oss_bucket_file_from_remote(bucket_inv.uuid).files
        if bucket_file:
            for i in bucket_file:
                hyb_ops.del_oss_bucket_file_remote(bucket_inv.uuid, i)
        time.sleep(10)
        hyb_ops.del_oss_bucket_remote(bucket_inv.uuid)

    if datacenter_inv:
        hyb_ops.del_datacenter_in_local(datacenter_inv.uuid)
    global ks_inv
    if ks_inv:
        hyb_ops.del_aliyun_key_secret(ks_inv.uuid)

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
