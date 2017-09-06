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

date_s = time.strftime('%m%d-%H%M%S', time.localtime())
test_obj_dict = test_state.TestStateDict()
ks_inv = None
datacenter_inv = None
test_stub = test_lib.lib_get_test_stub()
sg_inv = None
iz_inv = None
vm_inv = None
ecs_inv = None
ipsec_inv = None
bucket_inv = None
ecs_eip_inv = None
vswitch_inv = None
user_vpn_gw_inv = None
route_entry_inv = None
ipsec_vpn_inv_connection = None

def create_vpn_connection(vpn_gateway, vswitch_cidr, zstack_cidrs, auth_alg_1='sha1', auth_alg_2='sha1'):
    vpn_ike_config = hyb_ops.create_vpn_ike_ipsec_config(name='zstack-test-vpn-ike-config', psk='ZStack.Hybrid.Test123789', local_ip=vpn_gateway.publicIp, remote_ip=user_vpn_gw_inv.ip, auth_alg=auth_alg_1)
    vpn_ipsec_config = hyb_ops.create_vpn_ipsec_config(name='zstack-test-vpn-ike-config', auth_alg=auth_alg_2)
    vpn_connection = hyb_ops.create_vpc_vpn_connection(user_vpn_gw_inv.uuid, vpn_gateway.uuid, 'zstack-test-ipsec-vpn-connection', vswitch_cidr,
                                              zstack_cidrs, vpn_ike_config.uuid, vpn_ipsec_config.uuid)
    return vpn_connection

def test():
    global ks_inv
    global datacenter_inv
    global sg_inv
    global vm_inv
    global iz_inv
    global ecs_inv
    global ecs_eip_inv
    global ipsec_inv
    global bucket_inv
    global vswitch_inv
    global user_vpn_gw_inv
    global route_entry_inv
    global ipsec_vpn_inv_connection
    vm_inv = test_stub.create_vlan_vm(os.environ.get('l3VlanNetworkName1'))
#     test_obj_dict.add_vm(vm_inv)
    vm_inv.check()
    pri_l3_uuid = vm_inv.vm.vmNics[0].l3NetworkUuid
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
    datacenter_type = os.getenv('datacenterType')
    ks_existed = hyb_ops.query_aliyun_key_secret()
    # Add Aliyun key & secret
    if not ks_existed:
        ks_inv = hyb_ops.add_aliyun_key_secret('test_hybrid', 'test for hybrid', os.getenv('aliyunKey'), os.getenv('aliyunSecret'))
    # Clear datacenter remained in local
    datacenter_local = hyb_ops.query_datacenter_local()
    if datacenter_local:
        for d in datacenter_local:
            hyb_ops.del_datacenter_in_local(d.uuid)
    datacenter_list = hyb_ops.get_datacenter_from_remote(datacenter_type)
    regions = [ i.regionId for i in datacenter_list]
    for r in regions:
        datacenter_inv = hyb_ops.add_datacenter_from_remote(datacenter_type, r, 'datacenter for test')
        # Add Identity Zone
        iz_list = hyb_ops.get_identity_zone_from_remote(datacenter_type, r)
        vpn_gateway_list = []
        for iz in iz_list:
            if not iz.availableInstanceTypes:
                continue
            iz_inv = hyb_ops.add_identity_zone_from_remote(datacenter_type, datacenter_inv.uuid, iz.zoneId)
            vpn_gateway_list = hyb_ops.sync_vpc_vpn_gateway_from_remote(datacenter_inv.uuid)
            if vpn_gateway_list:
                vpn_gateway = vpn_gateway_list[0]
                break
            else:
                hyb_ops.del_identity_zone_in_local(iz_inv.uuid)
        if vpn_gateway_list:
            break
        else:
            hyb_ops.del_datacenter_in_local(datacenter_inv.uuid)
    if not vpn_gateway_list:
        test_util.test_fail("VpnGate for ipsec vpn connection was not found in all available dataCenter")
    hyb_ops.sync_ecs_vpc_from_remote(datacenter_inv.uuid)
    hyb_ops.sync_ecs_vswitch_from_remote(datacenter_inv.uuid)
    vswitch_local = hyb_ops.query_ecs_vswitch_local()
    vpc_local = hyb_ops.query_ecs_vpc_local()
    # Get VPC which has available gateway
    vpc_uuid = [vs.ecsVpcUuid for vs in vswitch_local if vs.uuid == vpn_gateway.vSwitchUuid][0]
    vpc_inv = [vpc for vpc in vpc_local if vpc.uuid == vpc_uuid][0]
    # Create vSwitch
    vpc_cidr_list = vpc_inv.cidrBlock.split('.')
    vpc_cidr_list[2] = '252'
    vpc_cidr_list[3] = '0/24'
    vswitch_cidr = '.'.join(vpc_cidr_list)
    ecs_vswitch = [vs for vs in vswitch_local if vs.cidrBlock == vswitch_cidr]
    if ecs_vswitch:
        vswitch_inv = ecs_vswitch[0]
    else:
        vswitch_inv = hyb_ops.create_ecs_vswtich_remote(vpc_inv.uuid, iz_inv.uuid, 'zstack-test-vswitch', vswitch_cidr)
        time.sleep(5)
    # Create Vpc User Gateway
    hyb_ops.sync_vpc_user_vpn_gateway_from_remote(datacenter_inv.uuid)
    user_vpn_gw_local = hyb_ops.query_vpc_user_vpn_gateway_local()
    user_vpn_gw = [gw for gw in user_vpn_gw_local if gw.ip == vip.ip]
    if user_vpn_gw:
        user_vpn_gw_inv = user_vpn_gw[0]
    else:
        user_vpn_gw_inv = hyb_ops.create_vpc_user_vpn_gateway(datacenter_inv.uuid, gw_ip=vip.ip, gw_name="zstack-test-user-vpn-gateway")
    # Delete existed IPsec
    ipsec_conntion = hyb_ops.query_ipsec_connection()
    time.sleep(5)
    if ipsec_conntion:
        ipsec_ops.delete_ipsec_connection(ipsec_conntion[0].uuid)
    # Create VPC VPN connection
    ipsec_vpn_inv_connection = create_vpn_connection(vpn_gateway, vswitch_cidr, zstack_cidrs)
    # Create ZStack IPsec VPN connection
    ipsec_inv = ipsec_ops.create_ipsec_connection('ipsec', pri_l3_uuid, vpn_gateway.publicIp, 'ZStack.Hybrid.Test123789', vip.uuid, [vswitch_cidr],
                                                          ike_dh_group=2, ike_encryption_algorithm='3des', policy_encryption_algorithm='3des', pfs='dh-group2')
    time.sleep(10)
    vpc_vpn_auto_synced = hyb_ops.query_vpc_vpn_connection_local()
    if vpc_vpn_auto_synced:
        for vpn in vpc_vpn_auto_synced:
            hyb_ops.del_vpc_vpn_connection_local(vpn.uuid)
    assert not hyb_ops.query_vpc_vpn_connection_local()
    hyb_ops.sync_vpc_vpn_connection_from_remote(datacenter_inv.uuid)
    assert hyb_ops.query_vpc_vpn_connection_local()
    vpc_vpn_conn_local = hyb_ops.query_vpc_vpn_connection_local()
    for conn in vpc_vpn_conn_local:
        if conn.connectionId == ipsec_vpn_inv_connection.connectionId:
            ipsec_vpn_inv_connection = conn
    test_util.test_pass('Sync Delete Vpc Vpn Connection Local Test Success')

def env_recover():
    global vm_inv
    if vm_inv:
        hyb_ops.destroy_vm_instance(vm_inv.vm.uuid)

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

    global user_vpn_gw_inv
    if user_vpn_gw_inv:
        time.sleep(10)
        hyb_ops.del_vpc_user_vpn_gateway_remote(user_vpn_gw_inv.uuid)

    global vswitch_inv
    if vswitch_inv:
        time.sleep(10)
        hyb_ops.del_ecs_vswitch_remote(vswitch_inv.uuid)

    global route_entry_inv
    if route_entry_inv:
        time.sleep(30)
        hyb_ops.del_aliyun_route_entry_remote(route_entry_inv.uuid)

    global iz_inv
    if iz_inv:
        hyb_ops.del_identity_zone_in_local(iz_inv.uuid)

    if datacenter_inv:
        hyb_ops.del_datacenter_in_local(datacenter_inv.uuid)

    global ks_inv
    if ks_inv:
        hyb_ops.del_aliyun_key_secret(ks_inv.uuid)

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
