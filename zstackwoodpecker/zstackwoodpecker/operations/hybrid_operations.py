'''

All hybrid operations for test.

@author: quarkonics
'''

from apibinding.api import ApiError
import apibinding.inventory as inventory
import apibinding.api_actions as api_actions
import zstackwoodpecker.test_util as test_util
import zstacklib.utils.xmlobject as xmlobject
import account_operations
import config_operations

import os
import inspect

def add_hybrid_key_secret(name, description, key, secret, ks_type='aliyun', sync='true', session_uuid=None):
    action = api_actions.AddHybridKeySecretAction()
    action.name = name
    action.description = description
    action.key = key
    action.secret = secret
    action.type = ks_type
    action.sync = sync
    test_util.action_logger('Add [aliyun key secret:] %s' % key)
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[aliyun key secret:] %s is added.' % key)
    return evt.inventory

def del_hybrid_key_secret(uuid, session_uuid=None):
    action = api_actions.DeleteHybridKeySecretAction()
    action.uuid = uuid
    test_util.action_logger('Delete [aliyun key secret:] %s' % uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[aliyun key secret:] %s is deleted.' % uuid)
    return evt

def update_aliyun_key_secret(uuid, name=None, description=None, session_uuid=None):
    action = api_actions.UpdateAliyunKeySecretAction()
    action.uuid = uuid
    action.name = name
    action.description = description
    test_util.action_logger('Update [aliyun key secret:] %s' % uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[aliyun key secret:] %s is updated.' % uuid)
    return evt

def attach_hybrid_key(uuid, session_uuid=None):
    action = api_actions.AttachHybridKeyAction()
    action.uuid = uuid
    test_util.action_logger('Attach [aliyun key:] %s' % uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[aliyun key:] %s is attached.' % uuid)
    return evt

def detach_hybrid_key(uuid, session_uuid=None):
    action = api_actions.DetachHybridKeyAction()
    action.uuid = uuid
    test_util.action_logger('Detach [aliyun key:] %s' % uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[aliyun key:] %s is detached.' % uuid)
    return evt

def get_oss_bucket_name_from_remote(data_center_uuid, session_uuid=None):
    action = api_actions.GetOssBucketNameFromRemoteAction()
    action.dataCenterUuid = data_center_uuid
    test_util.action_logger('get Oss Bucket Name from Remote')
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    return evt.inventories

def add_oss_bucket_from_remote(data_center_uuid, oss_bucket_name, oss_domain=None, oss_key=None, oss_secret=None, session_uuid=None):
    action = api_actions.AddOssBucketFromRemoteAction()
    action.dataCenterUuid = data_center_uuid
    action.bucketName = oss_bucket_name
    action.ossDomain = oss_domain
    action.ossKey = oss_key
    action.ossSecret = oss_secret
    test_util.action_logger('Add [Oss Bucket From Remote:] %s %s' % (data_center_uuid, oss_bucket_name))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[Oss Bucket:] %s %s is added.' % (data_center_uuid, oss_bucket_name))
    return evt.inventory

def del_oss_bucket_name_in_local(uuid, session_uuid=None):
    action = api_actions.DeleteOssBucketNameLocalAction()
    action.uuid = uuid
    test_util.action_logger('Delete [Oss File Bucket Name in local:] %s' % (uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[Oss File Bucket Name in local:] %s is deleted.' % (uuid))
    return evt

def create_oss_bucket_remote(data_center_uuid, bucket_name, description, session_uuid=None):
    action = api_actions.CreateOssBucketRemoteAction()
    action.dataCenterUuid = data_center_uuid
    action.bucketName = bucket_name
    action.description = description
    test_util.action_logger('Create [Oss Bucket Name Remote:] %s %s' % (data_center_uuid, bucket_name))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[Oss Bucket Name Remote:] %s %s is created.' % (data_center_uuid, bucket_name))
    return evt.inventory

def del_oss_bucket_remote(uuid, session_uuid=None):
    action = api_actions.DeleteOssBucketRemoteAction()
    action.uuid = uuid
    test_util.action_logger('Delete [Oss Bucket Name Remote:] %s' % uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[Oss Bucket Name Remote:] %s is deleted.' % uuid)
    return evt

def del_oss_bucket_file_remote(bucket_uuid, file_name, session_uuid=None):
    action = api_actions.DeleteOssBucketFileRemoteAction()
    action.uuid = bucket_uuid
    action.fileName = file_name
    test_util.action_logger('Delete [Oss Bucket File Remote:] %s %s' % (bucket_uuid, file_name))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[Oss Bucket File Remote:] %s %s is deleted.' % (bucket_uuid, file_name))
    return evt

def get_oss_bucket_file_from_remote(bucket_uuid, session_uuid=None):
    action = api_actions.GetOssBucketFileFromRemoteAction()
    action.uuid = bucket_uuid
    test_util.action_logger('Get [Oss Bucket File From Remote:] %s' % bucket_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    return evt

def get_datacenter_from_remote(datacenter_type, session_uuid=None):
    action = api_actions.GetDataCenterFromRemoteAction()
    action.type = datacenter_type
    test_util.action_logger('Get [Datacenter From Remote:] %s' % datacenter_type)
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    return evt.inventories

def get_ecs_instance_type_from_remote(iz_uuid, session_uuid=None):
    action = api_actions.GetEcsInstanceTypeAction()
    action.identityZoneUuid = iz_uuid
    test_util.action_logger('Get [Ecs Instance Type From Remote:] %s' % iz_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    return evt.types

def add_datacenter_from_remote(datacenter_type, region_id, description, session_uuid=None):
    action = api_actions.AddDataCenterFromRemoteAction()
    action.type = datacenter_type
    action.regionId = region_id
    action.description = description
    test_util.action_logger('Add [datacenter from remote:] %s %s' % (datacenter_type, region_id))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[datacenter from remote:] %s %s is added.' % (datacenter_type, region_id))
    return evt.inventory

def del_datacenter_in_local(uuid, session_uuid=None):
    action = api_actions.DeleteDataCenterInLocalAction()
    action.uuid = uuid
    test_util.action_logger('Delete [datacenter in local:] %s' % (uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[datacenter in local:] %s is deleted.' % uuid)
    return evt

def attach_oss_bucket_to_ecs_datacenter(oss_bucket_uuid, session_uuid=None):
    action = api_actions.AttachOssBucketToEcsDataCenterAction()
    action.ossBucketUuid = oss_bucket_uuid
#     action.dataCenterUuid = datacenter_uuid 
    test_util.action_logger('Attach [Oss bucket:] %s to Datacenter' % oss_bucket_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[Oss bucket:] %s is attached to Datacenter.' % oss_bucket_uuid)
    return evt

def detach_oss_bucket_from_ecs_datacenter(oss_bucket_uuid, session_uuid=None):
    action = api_actions.DetachOssBucketFromEcsDataCenterAction()
    action.ossBucketUuid = oss_bucket_uuid
#     action.dataCenterUuid = datacenter_uuid 
    test_util.action_logger('Detach [Oss bucket:] %s from Datacenter' % oss_bucket_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[Oss bucket:] %s is detached from Datacenter.' % oss_bucket_uuid)
    return evt

def get_identity_zone_from_remote(datacenter_type, region_id=None, dc_uuid=None, session_uuid=None):
    action = api_actions.GetIdentityZoneFromRemoteAction()
    action.type = datacenter_type
    action.regionId = region_id
    action.dataCenterUuid = dc_uuid
    test_util.action_logger('Get [Identity zone From Remote:] %s %s' % (datacenter_type, region_id))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    return evt.inventories

def add_identity_zone_from_remote(iz_type, datacenter_uuid, zone_id, session_uuid=None):
    action = api_actions.AddIdentityZoneFromRemoteAction()
    action.type = iz_type
    action.dataCenterUuid = datacenter_uuid
    action.zoneId = zone_id
    test_util.action_logger('Add [identity zone from remote:] %s %s' % (datacenter_uuid, zone_id))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[identity zone from remote:] %s %s is added.' % (datacenter_uuid, zone_id))
    return evt.inventory

def del_identity_zone_in_local(uuid, session_uuid=None):
    action = api_actions.DeleteIdentityZoneInLocalAction()
    action.uuid = uuid
    test_util.action_logger('Delete [identity zone in local:] %s' % (uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[identity zone in local:] %s is deleted.' % uuid)
    return evt

def create_ecs_vpc_remote(datacenter_uuid, name, vrouter_name, cidr_block, session_uuid=None):
    action = api_actions.CreateEcsVpcRemoteAction()
    action.dataCenterUuid = datacenter_uuid
    action.name = name
    action.vRouterName = vrouter_name
    action.cidrBlock = cidr_block
    test_util.action_logger('Create [Ecs VPC Remote:] %s %s %s %s' % (datacenter_uuid, name, vrouter_name, cidr_block))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[Ecs VPC Remote:] %s %s %s %s is created.' % (datacenter_uuid, name, vrouter_name, cidr_block))
    return evt.inventory

def sync_ecs_vpc_from_remote(datacenter_uuid, session_uuid=None):
    action = api_actions.SyncEcsVpcFromRemoteAction()
    action.dataCenterUuid = datacenter_uuid
    test_util.action_logger('Sync [Ecs VPC From Remote:] %s' % (datacenter_uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    return evt.inventories

def sync_virtual_border_router_from_remote(datacenter_uuid, session_uuid=None):
    action = api_actions.SyncVirtualBorderRouterFromRemoteAction()
    action.dataCenterUuid = datacenter_uuid
    test_util.action_logger('Sync [Virtual Border Router From Remote:] %s' % (datacenter_uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    return evt.inventories

def del_ecs_vpc_local(uuid, session_uuid=None):
    action = api_actions.DeleteEcsVpcInLocalAction()
    action.uuid = uuid
    test_util.action_logger('Delete [Ecs VPC Local:] %s ' % (uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[Ecs VPC Local:] %s is deleted.' % (uuid))
    return evt

def del_ecs_vpc_remote(uuid, session_uuid=None):
    action = api_actions.DeleteEcsVpcRemoteAction()
    action.uuid = uuid
    test_util.action_logger('Delete [Ecs VPC Remote:] %s ' % (uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[Ecs VPC Remote:] %s is deleted.' % (uuid))
    return evt

def create_ecs_vswtich_remote(vpc_uuid, identity_zone_uuid, name, cidr_block, session_uuid=None):
    action = api_actions.CreateEcsVSwitchRemoteAction()
    action.vpcUuid = vpc_uuid
    action.identityZoneUuid = identity_zone_uuid
    action.name = name
    action.cidrBlock = cidr_block
    test_util.action_logger('Create [Ecs VSwitch Remote:] %s %s %s %s' % (vpc_uuid, identity_zone_uuid, name, cidr_block))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[Ecs VSwitch Remote:] %s %s %s %s is created.' % (vpc_uuid, identity_zone_uuid, name, cidr_block))
    return evt.inventory

def create_hybrid_eip(data_center_uuid, name, band_width, charge_type='PayByTraffic', eip_type='aliyun', session_uuid=None):
    action = api_actions.CreateHybridEipAction()
    action.dataCenterUuid = data_center_uuid
    action.name = name
    action.bandWidthMb = band_width
    action.chargeType = charge_type
    action.type = eip_type
    test_util.action_logger('Create [Hybrid Eip:] %s %s %s %s' % (data_center_uuid, name, charge_type, eip_type))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[Hybrid Eip:] %s %s %s %s is created.' % (data_center_uuid, name, charge_type, eip_type))
    return evt.inventory

def del_hybrid_eip_remote(uuid, eip_type='aliyun', session_uuid=None):
    action = api_actions.DeleteHybridEipRemoteAction()
    action.uuid = uuid
    action.type = eip_type
    test_util.action_logger('Delete [Hybrid Eip Remote:] %s' % (uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[Hybrid Eip Remote:] %s is deleted.' % uuid)
    return evt

def attach_hybrid_eip_to_ecs(eip_uuid, ecs_uuid, eip_type='aliyun', session_uuid=None):
    action = api_actions.AttachHybridEipToEcsAction()
    action.eipUuid = eip_uuid
    action.ecsUuid = ecs_uuid
    action.type = eip_type
    test_util.action_logger('Attach [Hybrid Eip :] %s to ECS %s' % (eip_uuid, ecs_uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[Hybrid Eip :] %s is attached to Ecs %s.' % (eip_uuid, ecs_uuid))
    return evt

def detach_hybrid_eip_from_ecs(eip_uuid, eip_type='aliyun', session_uuid=None):
    action = api_actions.DetachHybridEipFromEcsAction()
    action.eipUuid = eip_uuid
    action.type = eip_type
    test_util.action_logger('Detach [Hybrid Eip :] %s from ECS' % eip_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[Hybrid Eip :] %s is detached from Ecs.' % eip_uuid)
    return evt

def sync_hybrid_eip_from_remote(data_center_uuid, eip_type='aliyun', session_uuid=None):
    action = api_actions.SyncHybridEipFromRemoteAction()
    action.dataCenterUuid = data_center_uuid
    action.type = eip_type
    test_util.action_logger('Sync [Hybrid Eip From Remote:] %s' % (data_center_uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    return evt.inventories

def sync_ecs_vswitch_from_remote(data_center_uuid, session_uuid=None):
    action = api_actions.SyncEcsVSwitchFromRemoteAction()
    action.dataCenterUuid = data_center_uuid
    test_util.action_logger('Sync [Ecs VSwitch From Remote:] %s' % (data_center_uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    return evt.inventories

def del_ecs_vswitch_in_local(uuid, session_uuid=None):
    action = api_actions.DeleteEcsVSwitchInLocalAction()
    action.uuid = uuid
    test_util.action_logger('Delete [Ecs VSwitch: %s] in Local' % (uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[Ecs VSwitch: %s] in Local is deleted.' % uuid)
    return evt

def del_ecs_vswitch_remote(uuid, session_uuid=None):
    action = api_actions.DeleteEcsVSwitchRemoteAction()
    action.uuid = uuid
    test_util.action_logger('Delete [Ecs VSwitch Remote:] %s ' % (uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[Ecs VSwitch Remote:] %s is deleted.' % (uuid))
    return evt

def del_ecs_instance_local(uuid, session_uuid=None):
    action = api_actions.DeleteEcsInstanceLocalAction()
    action.uuid = uuid
    test_util.action_logger('Delete [Ecs Instance in Local:] %s ' % (uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[Ecs Instance in Local:] %s is deleted.' % (uuid))
    return evt

def sync_aliyun_virtual_router_from_remote(vpc_uuid, session_uuid=None):
    action = api_actions.SyncAliyunVirtualRouterFromRemoteAction()
    action.vpcUuid = vpc_uuid
    test_util.action_logger('Sync [Aliyun VirtualRouter From Remote:] %s' % (vpc_uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    return evt.inventories

def sync_route_entry_from_remote(vrouter_uuid, vrouter_type, session_uuid=None):
    action = api_actions.SyncAliyunRouteEntryFromRemoteAction()
    action.vRouterUuid = vrouter_uuid
    action.vRouterType = vrouter_type
    test_util.action_logger('Sync [Route Entry From Remote:] %s' % (vrouter_uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    return evt.inventories

def create_aliyun_vpc_virtualrouter_entry_remote(dst_cidr_block, vrouter_uuid, vrouter_type, next_hop_type, next_hop_uuid, session_uuid=None):
    action = api_actions.CreateAliyunVpcVirtualRouterEntryRemoteAction()
    action.dstCidrBlock = dst_cidr_block
    action.vRouterUuid = vrouter_uuid
    action.vRouterType = vrouter_type
    action.nextHopType = next_hop_type
    action.nextHopUuid = next_hop_uuid
    test_util.action_logger('Create [VPC VirtualRouter Entry Remote:] %s %s %s %s %s' % (dst_cidr_block, vrouter_uuid, vrouter_type, next_hop_type, next_hop_uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[VPC VirtualRouter Entry Remote:] %s %s %s %s %s is created.' % (dst_cidr_block, vrouter_uuid, vrouter_type, next_hop_type, next_hop_uuid))
    return evt.inventory

def create_vpn_ipsec_config(name, pfs='group2', enc_alg='3des', auth_alg='sha1', session_uuid=None):
    action = api_actions.CreateVpnIpsecConfigAction()
    action.name = name
    action.pfs = pfs
    action.encAlg = enc_alg
    action.authAlg = auth_alg
    test_util.action_logger('Create [VPN IPsec Config:] %s %s %s %s' % (name, pfs, enc_alg, auth_alg))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[VPN IPsec Config:] %s %s %s %s is created.' % (name, pfs, enc_alg, auth_alg))
    return evt.inventory

def create_vpn_ike_ipsec_config(name, psk, local_ip, remote_ip, pfs='group2', enc_alg='3des', auth_alg='sha1', version='ikev1', mode='main', session_uuid=None):
    action = api_actions.CreateVpnIkeConfigAction()
    action.psk = psk
    action.pfs = pfs
    action.localIp = local_ip
    action.remoteIp = remote_ip
    action.encAlg = enc_alg
    action.authAlg = auth_alg
    action.version = version
    action.mode = mode
    action.name = name
    test_util.action_logger('Create [VPN Ike Config:] %s %s %s %s %s %s %s %s %s' % (name, local_ip, remote_ip, psk, pfs, enc_alg, auth_alg, version, mode))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[VPN Ike Config:] %s %s %s %s %s %s %s %s %s is created.' % (name, local_ip, remote_ip, psk, pfs, enc_alg, auth_alg, version, mode))
    return evt.inventory

def create_vpc_vpn_connection(user_gatway_uuid, vpn_gateway_uuid, name, local_cidr, remote_cidr, ike_config_uuid, ipsec_config_uuid, active='true', session_uuid=None):
    action = api_actions.CreateVpcVpnConnectionRemoteAction()
    action.userGatewayUuid = user_gatway_uuid
    action.vpnGatewayUuid = vpn_gateway_uuid
    action.name = name
    action.localCidr = local_cidr
    action.remoteCidr = remote_cidr
    action.ikeConfUuid = ike_config_uuid
    action.ipsecConfUuid = ipsec_config_uuid
    action.active = active
    test_util.action_logger('Create [VPC VPN Connection:] %s %s' % (vpn_gateway_uuid, user_gatway_uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[VPC VPN Connection:] %s %s is created.' % (vpn_gateway_uuid, user_gatway_uuid))
    return evt.inventory

def create_vpc_user_vpn_gateway(data_center_uuid, gw_ip, gw_name, session_uuid=None):
    action = api_actions.CreateVpcUserVpnGatewayRemoteAction()
    action.dataCenterUuid = data_center_uuid
    action.ip = gw_ip
    action.name = gw_name
    test_util.action_logger('Create [VPC User VPN Gateway:] %s %s' % (data_center_uuid, gw_ip))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[VPC User VPN Gateway:] %s %s is created.' % (data_center_uuid, gw_ip))
    return evt.inventory

def del_vpc_user_vpn_gateway_remote(uuid, session_uuid=None):
    action = api_actions.DeleteVpcUserVpnGatewayRemoteAction()
    action.uuid = uuid
    test_util.action_logger('Delete [Vpc User Vpn Gateway Remote:] %s ' % (uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[Vpc User Vpn Gateway Remote:] %s is deleted.' % (uuid))
    return evt

def del_vpc_vpn_connection_remote(uuid, session_uuid=None):
    action = api_actions.DeleteVpcVpnConnectionRemoteAction()
    action.uuid = uuid
    test_util.action_logger('Delete [Vpc Vpn Connection Remote:] %s ' % (uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[Vpc Vpn Connection Remote:] %s is deleted.' % (uuid))
    return evt

def del_aliyun_route_entry_remote(uuid, session_uuid=None):
    action = api_actions.DeleteAliyunRouteEntryRemoteAction()
    action.uuid = uuid
    test_util.action_logger('Delete [Aliyun Route Entry Remote:] %s ' % (uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[Aliyun Route Entry Remote:] %s is deleted.' % (uuid))
    return evt

def del_vpc_vpn_gateway_local(uuid, session_uuid=None):
    action = api_actions.DeleteVpcVpnGatewayLocalAction()
    action.uuid = uuid
    test_util.action_logger('Delete [Vpc Vpn Gateway in local:] %s ' % (uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[Vpc Vpn Gateway in local:] %s is deleted.' % (uuid))
    return evt

def del_vpc_vpn_connection_local(uuid, session_uuid=None):
    action = api_actions.DeleteVpcVpnConnectionLocalAction()
    action.uuid = uuid
    test_util.action_logger('Delete [Vpc Vpn Gateway Local:] %s ' % (uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[Router Entry Remote:] %s is deleted.' % (uuid))
    return evt

def del_vpc_ike_config_local(uuid, session_uuid=None):
    action = api_actions.DeleteVpcIkeConfigLocalAction()
    action.uuid = uuid
    test_util.action_logger('Delete [Vpc Ike Config in Local:] %s ' % (uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[Vpc Ike Config in Local:] %s is deleted.' % (uuid))
    return evt

def del_vpc_ipsec_config_local(uuid, session_uuid=None):
    action = api_actions.DeleteVpcIpSecConfigLocalAction()
    action.uuid = uuid
    test_util.action_logger('Delete [Vpc IPsec Config in Local:] %s ' % (uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[Vpc IPsec Config in Local:] %s is deleted.' % (uuid))
    return evt

def del_vpc_user_vpn_gateway_local(uuid, session_uuid=None):
    action = api_actions.DeleteVpcUserVpnGatewayLocalAction()
    action.uuid = uuid
    test_util.action_logger('Delete [Router Entry Remote:] %s ' % (uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[Router Entry Remote:] %s is deleted.' % (uuid))
    return evt

def destroy_vm_instance(uuid, session_uuid=None):
    action = api_actions.DestroyVmInstanceAction()
    action.uuid = uuid
    test_util.action_logger('Destroy [VM Instance:] %s ' % (uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[VM Instance:] %s is destroyed.' % (uuid))
    return evt

def create_ecs_security_group_remote(name, vpc_uuid, session_uuid=None):
    action = api_actions.CreateEcsSecurityGroupRemoteAction()
    action.name = name
    action.vpcUuid = vpc_uuid
    test_util.action_logger('Create [Ecs Security Group Remote:] %s %s' % (name, vpc_uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('Ecs Security Group Remote:] %s %s is created.' % (name, vpc_uuid))
    return evt.inventory

def create_ecs_security_group_rule_remote(group_uuid, direction, protocol, port_range, cidr, policy, nic_type, priority, description=None, session_uuid=None):
    action = api_actions.CreateEcsSecurityGroupRuleRemoteAction()
    action.groupUuid = group_uuid
    action.direction = direction
    action.protocol = protocol
    action.portRange = port_range
    action.cidr = cidr
    action.policy = policy
    action.nictype = nic_type
    action.priority = priority
    action.description = description
    test_util.action_logger('Create [Ecs Security Group Rule Remote:] %s %s %s %s %s %s %s %s' % (group_uuid, direction, protocol, port_range, cidr, policy, nic_type, priority))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[Ecs Security Group Rule Remote:] %s %s %s %s %s %s %s %s is created.' % (group_uuid, direction, protocol, port_range, cidr, policy, nic_type, priority))
    return evt.inventory

def sync_ecs_security_group_from_remote(ecs_vpc_uuid, session_uuid=None):
    action = api_actions.SyncEcsSecurityGroupFromRemoteAction()
    action.ecsVpcUuid = ecs_vpc_uuid
    test_util.action_logger('Sync [Security Group From Remote:] %s' % (ecs_vpc_uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    return evt.inventories

def sync_ecs_security_group_rule_from_remote(sg_uuid, session_uuid=None):
    action = api_actions.SyncEcsSecurityGroupRuleFromRemoteAction()
    action.uuid = sg_uuid
    test_util.action_logger('Sync [Security Group From Remote:] %s' % (sg_uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    return evt.inventories

def sync_vpc_vpn_gateway_from_remote(data_center_uuid, session_uuid=None):
    action = api_actions.SyncVpcVpnGatewayFromRemoteAction()
    action.dataCenterUuid = data_center_uuid
    test_util.action_logger('Sync [Vpc Vpn Gateway From Remote:] %s' % (data_center_uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    return evt.inventories

def sync_vpc_user_vpn_gateway_from_remote(data_center_uuid, session_uuid=None):
    action = api_actions.SyncVpcUserVpnGatewayFromRemoteAction()
    action.dataCenterUuid = data_center_uuid
    test_util.action_logger('Sync [Vpc User Vpn Gateway From Remote:] %s' % (data_center_uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    return evt.inventories

def sync_vpc_vpn_connection_from_remote(data_center_uuid, session_uuid=None):
    action = api_actions.SyncVpcVpnConnectionFromRemoteAction()
    action.dataCenterUuid = data_center_uuid
    test_util.action_logger('Sync [Vpc Vpn Connection From Remote:] %s' % (data_center_uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    return evt.inventories

def del_ecs_security_group_in_local(uuid, session_uuid=None):
    action = api_actions.DeleteEcsSecurityGroupInLocalAction()
    action.uuid = uuid
    test_util.action_logger('Delete [ecs security group in local:] %s' % (uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[ecs security group in local:] %s is deleted.' % uuid)
    return evt

def del_ecs_security_group_rule_remote(uuid, session_uuid=None):
    action = api_actions.DeleteEcsSecurityGroupRuleRemoteAction()
    action.uuid = uuid
    test_util.action_logger('Delete [Ecs Security Group Rule Remote:] %s ' % (uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[Ecs Security Group Rule Remote:] %s is deleted.' % (uuid))
    return evt

def del_ecs_security_group_remote(uuid, session_uuid=None):
    action = api_actions.DeleteEcsSecurityGroupRemoteAction()
    action.uuid = uuid
    test_util.action_logger('Delete [Ecs Security Group Remote:] %s ' % (uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[Ecs Security Group Remote:] %s is deleted.' % (uuid))
    return evt

def create_ecs_image_from_local_image(bs_uuid, datacenter_uuid, image_uuid, name, session_uuid=None):
    action = api_actions.CreateEcsImageFromLocalImageAction()
    action.backupStorageUuid = bs_uuid
    action.dataCenterUuid = datacenter_uuid
    action.imageUuid = image_uuid
    action.name = name
    test_util.action_logger('Create Ecs Image from [Local image:] %s %s %s' % (bs_uuid, datacenter_uuid, image_uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('Ecs Image is created from [Local image:] %s %s %s.' % (bs_uuid, datacenter_uuid, image_uuid))
    return evt.inventory

def del_ecs_image_remote(uuid, session_uuid=None):
    action = api_actions.DeleteEcsImageRemoteAction()
    action.uuid = uuid
    test_util.action_logger('Delete [ecs image remote:] %s' % (uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[ecs image remote:] %s is deleted.' % uuid)
    return evt

def del_ecs_image_in_local(uuid, session_uuid=None):
    action = api_actions.DeleteEcsImageLocalAction()
    action.uuid = uuid
    test_util.action_logger('Delete [ecs image in local:] %s' % (uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[ecs image in local:] %s is deleted.' % uuid)
    return evt

def del_hybrid_eip_local(uuid, eip_type='aliyun', session_uuid=None):
    action = api_actions.DeleteHybridEipFromLocalAction()
    action.type = eip_type
    action.uuid = uuid
    test_util.action_logger('Delete [Hybrid Eip in local:] %s' % (uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[Hybrid Eip in local:] %s is deleted.' % uuid)
    return evt

def sync_ecs_image_from_remote(datacenter_uuid, image_type='self', session_uuid=None):
    action = api_actions.SyncEcsImageFromRemoteAction()
    action.dataCenterUuid = datacenter_uuid
    action.type = image_type
    test_util.action_logger('Sync [Ecs Image From Remote:] %s' % (datacenter_uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    return evt.inventories

def create_ecs_instance_from_ecs_image(ecs_root_password, image_uuid, ecs_vswitch_uuid, ecs_bandwidth, ecs_security_group_uuid, instance_offering_uuid=None, instance_type=None, private_ip_address=None, allocate_public_ip='false', name=None, ecs_console_password=None, session_uuid=None):
    action = api_actions.CreateEcsInstanceFromEcsImageAction()
    action.ecsRootPassword = ecs_root_password
    action.ecsImageUuid = image_uuid
    action.ecsVSwitchUuid = ecs_vswitch_uuid
    action.instanceOfferingUuid = instance_offering_uuid
    action.instanceType = instance_type
    action.ecsBandWidth = ecs_bandwidth
    action.ecsSecurityGroupUuid = ecs_security_group_uuid
    action.privateIpAddress = private_ip_address
    action.allocatePublicIp = allocate_public_ip
    action.name = name
    action.ecsConsolePassword = ecs_console_password
    test_util.action_logger('Create Ecs Instance from [Ecs Image:] %s' %  image_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('Ecs Instance is created from [Ecs Image:] %s.' %  image_uuid)
    return evt.inventory

def del_ecs_instance(uuid, session_uuid=None):
    action = api_actions.DeleteEcsInstanceAction()
    action.uuid = uuid
    test_util.action_logger('Delete [ecs instance:] %s' % (uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[ecs instance:] %s is deleted.' % uuid)
    return evt

def sync_ecs_instance_from_remote(datacenter_uuid, only_zstack=None, session_uuid=None):
    action = api_actions.SyncEcsInstanceFromRemoteAction()
    action.dataCenterUuid = datacenter_uuid
    action.onlyZstack = only_zstack
    test_util.action_logger('Sync [Ecs Instance From Remote:] %s' % (datacenter_uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    return evt.inventories

def update_ecs_instance(uuid, name=None, description=None, password=None, session_uuid=None):
    action = api_actions.UpdateEcsInstanceAction()
    action.uuid = uuid
    action.name = name
    action.description = description
    action.password = password
    test_util.action_logger('Update [Ecs Instance: %s]' % (uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    return evt

def stop_ecs_instance(uuid, session_uuid=None):
    action = api_actions.StopEcsInstanceAction()
    action.uuid = uuid
    test_util.action_logger('Stop [ecs instance:] %s' % (uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[ecs instance:] %s is stopped.' % uuid)
    return evt

def start_ecs_instance(uuid, session_uuid=None):
    action = api_actions.StartEcsInstanceAction()
    action.uuid = uuid
    test_util.action_logger('Start [ecs instance:] %s' % (uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[ecs instance:] %s is started.' % uuid)
    return evt

def reboot_ecs_instance(uuid, session_uuid=None):
    action = api_actions.RebootEcsInstanceAction()
    action.uuid = uuid
    test_util.action_logger('Reboot [ecs instance:] %s' % (uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[ecs instance:] %s is rebooted.' % uuid)
    return evt

def update_ecs_instance_vnc_password(uuid, password, session_uuid=None):
    action = api_actions.UpdateEcsInstanceVncPasswordAction()
    action.uuid = uuid
    action.password = password
    test_util.action_logger('Update [ecs instance:] vnc password %s' % (uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[ecs instance:] %s vnc password is updated.' % uuid)
    return evt

def update_image_guestOsType(uuid, guest_os_type, session_uuid=None):
    action = api_actions.UpdateImageAction()
    action.uuid = uuid
    action.guestOsType = guest_os_type
    test_util.action_logger('Update [image %s] guestOsType' % (uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.action_logger('[image %s] guestOsType is updated to [%s]' % (uuid, guest_os_type))
    return evt

def update_ecs_image(uuid, name=None, description=None, session_uuid=None):
    action = api_actions.UpdateEcsImageAction()
    action.uuid = uuid
    action.name = name
    action.description = description
    test_util.action_logger('Update [ECS Image:] %s' % (uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.action_logger('[ECS Image:] %s is updated' % uuid)
    return evt

def update_ecs_security_group(uuid, name=None, description=None, session_uuid=None):
    action = api_actions.UpdateEcsSecurityGroupAction()
    action.uuid = uuid
    action.name = name
    action.description = description
    test_util.action_logger('Update [ECS Security Group:] %s' % (uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.action_logger('[ECS Security Group:] %s is updated' % uuid)
    return evt

def update_ecs_vpc(uuid, name=None, description=None, session_uuid=None):
    action = api_actions.UpdateEcsVpcAction()
    action.uuid = uuid
    action.name = name
    action.description = description
    test_util.action_logger('Update [ECS VPC:] %s' % (uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.action_logger('[ECS VPC:] %s is updated' % uuid)
    return evt

def update_ecs_vswitch(uuid, name=None, description=None, session_uuid=None):
    action = api_actions.UpdateEcsVSwitchAction()
    action.uuid = uuid
    action.name = name
    action.description = description
    test_util.action_logger('Update [ECS vSwitch:] %s' % (uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.action_logger('[ECS vSwitch:] %s is updated' % uuid)
    return evt

def update_vbr(uuid, name=None, description=None, session_uuid=None):
    action = api_actions.UpdateVirtualBorderRouterRemoteAction()
    action.uuid = uuid
    action.name = name
    action.description = description
    test_util.action_logger('Update [ECS Virtual Border Router:] %s' % (uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.action_logger('[ECS Virtual Border Router:] %s is updated' % uuid)
    return evt

def update_aliyun_vr(uuid, name=None, description=None, session_uuid=None):
    action = api_actions.UpdateAliyunVirtualRouterAction()
    action.uuid = uuid
    action.name = name
    action.description = description
    test_util.action_logger('Update [Aliyun Virtual Router:] %s' % (uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.action_logger('[Aliyun Virtual Router:] %s is updated' % uuid)
    return evt

def update_oss_bucket(uuid, name=None, description=None, session_uuid=None):
    action = api_actions.UpdateOssBucketAction()
    action.uuid = uuid
    action.name = name
    action.description = description
    test_util.action_logger('Update [OSS Bucket:] %s' % (uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.action_logger('[OSS Bucket:] %s is updated' % uuid)
    return evt.inventory

def update_aliyun_snapshot(uuid, name=None, description=None, session_uuid=None):
    action = api_actions.UpdateAliyunSnapshotAction()
    action.uuid = uuid
    action.name = name
    action.description = description
    test_util.action_logger('Update [Aliyun Snapshot:] %s' % (uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.action_logger('[Aliyun Snapshot:] %s is updated' % uuid)
    return evt

def update_hybrid_eip(uuid, name=None, description=None, eip_type='aliyun', session_uuid=None):
    action = api_actions.UpdateHybridEipAction()
    action.uuid = uuid
    action.name = name
    action.type = eip_type
    action.description = description
    test_util.action_logger('Update [Hybrid EIP:] %s' % (uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.action_logger('[Hybrid EIP:] %s is updated' % uuid)
    return evt

def update_vpc_user_vpn_gateway(uuid, name=None, description=None, session_uuid=None):
    action = api_actions.UpdateVpcUserVpnGatewayAction()
    action.uuid = uuid
    action.name = name
    action.description = description
    test_util.action_logger('Update [VPC User VPN Gateway:] %s' % (uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.action_logger('[VPC User VPN Gateway:] %s is updated' % uuid)
    return evt

def update_vpc_vpn_connection(uuid, name=None, description=None, session_uuid=None):
    action = api_actions.UpdateVpcVpnConnectionRemoteAction()
    action.uuid = uuid
    action.name = name
    action.description = description
    test_util.action_logger('Update [VPC VPN Connection:] %s' % (uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.action_logger('[VPC VPN Connection:] %s is updated' % uuid)
    return evt

def update_vpc_vpn_gateway(uuid, name=None, description=None, session_uuid=None):
    action = api_actions.UpdateVpcVpnGatewayAction()
    action.uuid = uuid
    action.name = name
    action.description = description
    test_util.action_logger('Update [VPC VPN Gateway:] %s' % (uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.action_logger('[VPC VPN Gateway:] %s is updated' % uuid)
    return evt

def query_ecs_image_local(condition=[], session_uuid=None):
    action = api_actions.QueryEcsImageFromLocalAction()
    action.conditions = condition
    test_util.action_logger('Query Ecs image from local')
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def query_ecs_vpc_local(condition=[], session_uuid=None):
    action = api_actions.QueryEcsVpcFromLocalAction()
    action.conditions = condition
    test_util.action_logger('Query Ecs Vpc from local')
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def query_ecs_vswitch_local(condition=[], session_uuid=None):
    action = api_actions.QueryEcsVSwitchFromLocalAction()
    action.conditions = condition
    test_util.action_logger('Query Ecs vSwitch from local')
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def query_ecs_instance_local(condition=[], session_uuid=None):
    action = api_actions.QueryEcsInstanceFromLocalAction()
    action.conditions = condition
    test_util.action_logger('Query Ecs Instance from local')
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def query_hybrid_key_secret(condition=[], session_uuid=None):
    action = api_actions.QueryHybridKeySecretAction()
    action.conditions = condition
    test_util.action_logger('Query Aliyun Key Secret')
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def query_datacenter_local(condition=[], session_uuid=None):
    action = api_actions.QueryDataCenterFromLocalAction()
    action.conditions = condition
    test_util.action_logger('Query DataCenter from local')
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def query_iz_local(condition=[], session_uuid=None):
    action = api_actions.QueryIdentityZoneFromLocalAction()
    action.conditions = condition
    test_util.action_logger('Query IdentityZone from local')
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def query_ecs_security_group_local(condition=[], session_uuid=None):
    action = api_actions.QueryEcsSecurityGroupFromLocalAction()
    action.conditions = condition
    test_util.action_logger('Query Ecs Security Group from local')
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def query_ecs_security_group_rule_local(condition=[], session_uuid=None):
    action = api_actions.QueryEcsSecurityGroupRuleFromLocalAction()
    action.conditions = condition
    test_util.action_logger('Query Ecs Security Group from local')
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def query_hybrid_eip_local(condition=[], session_uuid=None):
    action = api_actions.QueryHybridEipFromLocalAction()
    action.conditions = condition
    test_util.action_logger('Query Hybrid Eip from local')
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def query_vpc_vpn_gateway_local(condition=[], session_uuid=None):
    action = api_actions.QueryVpcVpnGatewayFromLocalAction()
    action.conditions = condition
    test_util.action_logger('Query Vpc Vpn Gateway from local')
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def query_vpc_vpn_ike_config_local(condition=[], session_uuid=None):
    action = api_actions.QueryVpcIkeConfigFromLocalAction()
    action.conditions = condition
    test_util.action_logger('Query Vpc Vpn Ike Config from local')
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def query_vpc_vpn_ipsec_config_local(condition=[], session_uuid=None):
    action = api_actions.QueryVpcIpSecConfigFromLocalAction()
    action.conditions = condition
    test_util.action_logger('Query Vpc Vpn IPsec Config from local')
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def query_vpc_user_vpn_gateway_local(condition=[], session_uuid=None):
    action = api_actions.QueryVpcUserVpnGatewayFromLocalAction()
    action.conditions = condition
    test_util.action_logger('Query Vpc User Vpn Gate from local')
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def query_vpc_vpn_connection_local(condition=[], session_uuid=None):
    action = api_actions.QueryVpcVpnConnectionFromLocalAction()
    action.conditions = condition
    test_util.action_logger('Query Vpc Vpn Connection from local')
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def query_aliyun_virtual_router_local(condition=[], session_uuid=None):
    action = api_actions.QueryAliyunVirtualRouterFromLocalAction()
    action.conditions = condition
    test_util.action_logger('Query Aliyun Virtual Router from local')
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def query_aliyun_route_entry_local(condition=[], session_uuid=None):
    action = api_actions.QueryAliyunRouteEntryFromLocalAction()
    action.conditions = condition
    test_util.action_logger('Query Aliyun Route Entry from local')
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def query_oss_bucket_file_name(condition=[], session_uuid=None):
    action = api_actions.QueryOssBucketFileNameAction()
    action.conditions = condition
    test_util.action_logger('Query Oss Bucket File Name')
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def query_ipsec_connection(condition=[], session_uuid=None):
    action = api_actions.QueryIPSecConnectionAction()
    action.conditions = condition
    test_util.action_logger('Query IPsec Connection')
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def get_ecs_instance_vnc_url(uuid, session_uuid=None):
    action = api_actions.GetEcsInstanceVncUrlAction()
    action.uuid = uuid
    test_util.action_logger('Get Ecs Instance Vpc Url')
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def get_create_ecs_image_progress(data_center_uuid, image_uuid, session_uuid=None):
    action = api_actions.GetCreateEcsImageProgressAction()
    action.dataCenterUuid = data_center_uuid
    action.imageUuid = image_uuid
    test_util.action_logger('Get Create ECS Image Progress')
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def create_aliyun_disk_remote(name, identity_uuid, size_gb, disk_category=None, description=None, snapshot_uuid=None, session_uuid=None):
    action = api_actions.CreateAliyunDiskFromRemoteAction()
    action.identityUuid = identity_uuid
    action.name = name
    action.sizeWithGB = size_gb
    action.diskCategory = disk_category
    action.description = description
    action.snapshotUuid = snapshot_uuid
    test_util.action_logger('Create [Aliyun Disk Remote:] %s %s %s' % (identity_uuid, name, size_gb))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[Aliyun Disk Remote:] %s %s %s is created.' % (identity_uuid, name, size_gb))
    return evt.inventory

def del_aliyun_disk_remote(uuid, session_uuid=None):
    action = api_actions.DeleteAliyunDiskFromRemoteAction()
    action.uuid = uuid
    test_util.action_logger('Delete [Aliyun Disk Remote:] %s' % uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[Aliyun Disk Remote:] %s is deleted.' % uuid)
    return evt

def del_aliyun_disk_in_local(uuid, session_uuid=None):
    action = api_actions.DeleteAliyunDiskFromLocalAction()
    action.uuid = uuid
    test_util.action_logger('Delete [Aliyun Disk in Local:] %s' % uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[Aliyun Disk in Local:] %s is deleted.' % uuid)
    return evt

def attach_aliyun_disk_to_ecs(ecs_uuid, disk_uuid, session_uuid=None):
    action = api_actions.AttachAliyunDiskToEcsAction()
    action.ecsUuid = ecs_uuid
    action.diskUuid = disk_uuid
    test_util.action_logger('Attach Aliyun Disk to ECS: %s %s' % (disk_uuid, ecs_uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[Aliyun Disk:] %s is attached to ECS:  %s' % (disk_uuid, ecs_uuid))
    return evt

def detach_aliyun_disk_from_ecs(uuid, session_uuid=None):
    action = api_actions.DetachAliyunDiskFromEcsAction()
    action.uuid = uuid
    test_util.action_logger('Detach [Aliyun Disk:] %s from ECS' % uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[Aliyun Disk:] %s is detached from ECS.' % uuid)
    return evt

def sync_aliyun_disk_from_remote(identity_uuid, session_uuid=None):
    action = api_actions.SyncDiskFromAliyunFromRemoteAction()
    action.identityUuid = identity_uuid
    test_util.action_logger('Sync Aliyun Disk from Remote %s' % identity_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('Aliyun Disk is synced from Remote %s.' % identity_uuid)
    return evt.inventories

def query_aliyun_disk_local(condition=[], session_uuid=None):
    action = api_actions.QueryAliyunDiskFromLocalAction()
    action.conditions = condition
    test_util.action_logger('Query Aliyun Disk From Local')
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def update_aliyun_disk(uuid, name=None, description=None, delete_with_instance=None, delete_autosnapshot=None, enable_autosnapshot=None,session_uuid=None):
    action = api_actions.UpdateAliyunDiskAction()
    action.uuid = uuid
    action.name = name
    action.description = description
    action.deleteWithInstance = delete_with_instance
    action.deleteAutoSnapshot = delete_autosnapshot
    action.enableAutoSnapshot = enable_autosnapshot
    test_util.action_logger('Update [Aliyun Disk:] %s' % uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[Aliyun Disk:] %s is updated.' % uuid)
    return evt

def creaet_aliyun_snapshot_remote(uuid, name, description=None, resource_uuid=None, session_uuid=None):
    action = api_actions.CreateAliyunSnapshotRemoteAction()
    action.diskUuid = uuid
    action.name = name
    action.resourceUuid = resource_uuid
    test_util.action_logger('Create Aliyun Snapshot Remote %s %s' % (uuid, name))
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('Aliyun Snapshot Remote %s %s is Created' % (uuid, name))
    return evt.inventory

def del_aliyun_snapshot_remote(uuid, session_uuid=None):
    action = api_actions.DeleteAliyunSnapshotFromRemoteAction()
    action.uuid = uuid
    test_util.action_logger('Delete [Aliyun Snapshot Remote:] %s' % uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[Aliyun Snapshot Remote:] %s is deleted.' % uuid)
    return evt

def del_aliyun_snapshot_in_local(uuid, session_uuid=None):
    action = api_actions.DeleteAliyunSnapshotFromLocalAction()
    action.uuid = uuid
    test_util.action_logger('Delete [Aliyun Snapshot in Local:] %s' % uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('[Aliyun Snapshot in Local:] %s is deleted.' % uuid)
    return evt

def query_aliyun_snapshot_local(condition=[], session_uuid=None):
    action = api_actions.QueryAliyunSnapshotFromLocalAction()
    action.conditions = condition
    test_util.action_logger('Query Aliyun Snapshot From Local')
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def sync_aliyun_snapshot_from_remote(datacenter_uuid, snapshot_id=None, session_uuid=None):
    action = api_actions.SyncAliyunSnapshotRemoteAction()
    action.dataCenterUuid = datacenter_uuid
    action.snapshotId = snapshot_id
    test_util.action_logger('Sync Aliyun Snapshot from Remote %s' % datacenter_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid) 
    test_util.test_logger('Aliyun Snapshot is synced from Remote %s.' % datacenter_uuid)
    return evt.inventories
