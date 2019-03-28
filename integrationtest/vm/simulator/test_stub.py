'''

Create an unified test_stub to share test operations

@author: Youyk
'''

import os

import apibinding.api_actions as api_actions
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.zone_operations as zone_ops
import zstackwoodpecker.operations.iam2_ticket_operations as ticket_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm
import zstackwoodpecker.zstack_test.zstack_test_volume as test_volume
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.operations.vpc_operations as vpc_ops
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.zstack_test.zstack_test_vip as zstack_vip_header
import zstackwoodpecker.zstack_test.zstack_test_eip as zstack_eip_header
import zstackwoodpecker.zstack_test.zstack_test_image as test_image
import zstackwoodpecker.header.vm as vm_header
from zstackwoodpecker.operations import vm_operations as vm_ops
import zstackwoodpecker.operations.longjob_operations as longjob_ops
import zstackwoodpecker.operations.billing_operations as bill_ops
import zstackwoodpecker.zstack_test.zstack_test_volume as zstack_volume_header 
import time
import re
import json
import random
import threading

def remove_all_vpc_vrouter():
    cond = res_ops.gen_query_conditions('applianceVmType', '=', 'vpcvrouter')
    vr_vm_list = res_ops.query_resource(res_ops.APPLIANCE_VM, cond)
    if vr_vm_list:
        for vr_vm in vr_vm_list:
            nic_uuid_list = [nic.uuid for nic in vr_vm.vmNics if nic.metaData == '4']
            for nic_uuid in nic_uuid_list:
                net_ops.detach_l3(nic_uuid)
            vm_ops.destroy_vm(vr_vm.uuid)

def create_system_admin(username, password, vid_tst_obj):
    #password = 'b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86'
    #username = "systemAdmin"
    #vid_tst_obj = test_vid.ZstackTestVid()
    attributes = [{"name": "__SystemAdmin__"}]
    vid_tst_obj.create(username, password, without_default_role="true")
    vid_uuid = vid_tst_obj.get_vid().uuid
    iam2_ops.add_attributes_to_iam2_virtual_id(vid_uuid, attributes)
    role_uuid = iam2_ops.create_role('systemAdminRole').uuid
    statements = [{"effect": "Allow", "actions": ["org.zstack.vpc.APIAddDnsToVpcRouterMsg",
                   "org.zstack.query.APIBatchQueryMsg",
                   "org.zstack.header.vm.cdrom.APICreateVmCdRomMsg",
                   "org.zstack.ha.APIDeleteVmInstanceHaLevelMsg",
                   "org.zstack.storage.fusionstor.primary.APIAddMonToFusionstorPrimaryStorageMsg",
                   "org.zstack.header.identity.APIGetAccountQuotaUsageMsg",
                   "org.zstack.header.baremetal.chassis.APIChangeBaremetalChassisStateMsg",
                   "org.zstack.header.datacenter.APIQueryDataCenterFromLocalMsg",
                   "org.zstack.aliyun.nas.message.APICreateAliyunNasAccessGroupMsg",
                   "org.zstack.iam2.api.APIDeleteIAM2OrganizationMsg",
                   "org.zstack.sns.APICreateSNSTopicMsg",
                   "org.zstack.pciDevice.APIUpdateHostIommuStateMsg",
                   "org.zstack.network.service.portforwarding.APIDetachPortForwardingRuleMsg",
                   "org.zstack.header.longjob.APIQueryLongJobMsg",
                   "org.zstack.autoscaling.group.instance.APIDeleteAutoScalingGroupInstanceMsg",
                   "org.zstack.ldap.APIDeleteLdapServerMsg",
                   "org.zstack.v2v.APIDeleteV2VConversionHostMsg",
                   "org.zstack.header.vm.APIGetVmAttachableDataVolumeMsg",
                   "org.zstack.header.aliyun.ecs.APISyncEcsInstanceFromRemoteMsg",
                   "org.zstack.aliyun.nas.storage.message.APIAddAliyunNasPrimaryStorageMsg",
                   "org.zstack.header.hybrid.network.eip.APIUpdateHybridEipMsg",
                   "org.zstack.monitoring.prometheus.APIPrometheusQueryMetadataMsg",
                   "org.zstack.header.hybrid.account.APIDeleteHybridKeySecretMsg",
                   "org.zstack.twoFactorAuthentication.APIGetTwoFactorAuthenticationStateMsg",
                   "org.zstack.header.vm.cdrom.APIUpdateVmCdRomMsg",
                   "org.zstack.header.vm.APIUpdateVmInstanceMsg",
                   "org.zstack.sns.platform.dingtalk.APIAddSNSDingTalkAtPersonMsg",
                   "org.zstack.storage.backup.imagestore.APIReclaimSpaceFromImageStoreMsg",
                   "org.zstack.header.baremetal.preconfiguration.APIAddPreconfigurationTemplateMsg",
                   "org.zstack.sns.platform.email.APIValidateSNSEmailPlatformMsg",
                   "org.zstack.network.service.lb.APIUpdateCertificateMsg",
                   "org.zstack.usbDevice.APIAttachUsbDeviceToVmMsg",
                   "org.zstack.iam2.api.APIUpdateIAM2ProjectMsg",
                   "org.zstack.iam2.api.APIUpdateIAM2VirtualIDAttributeMsg",
                   "org.zstack.monitoring.actions.APIUpdateEmailMonitorTriggerActionMsg",
                   "org.zstack.network.service.lb.APIChangeLoadBalancerListenerMsg",
                   "org.zstack.network.service.lb.APIDeleteCertificateMsg",
                   "org.zstack.header.vm.APIGetVmUsbRedirectMsg",
                   "org.zstack.header.storage.backup.APIReconnectBackupStorageMsg",
                   "org.zstack.header.core.webhooks.APICreateWebhookMsg",
                   "org.zstack.header.storage.primary.APIGetPrimaryStorageCapacityMsg",
                   "org.zstack.header.network.l3.APIGetL3NetworkRouterInterfaceIpMsg",
                   "org.zstack.core.errorcode.APIReloadElaborationMsg",
                   "org.zstack.zwatch.api.APIGetAuditDataMsg",
                   "org.zstack.storage.ceph.primary.APIDeleteCephPrimaryStoragePoolMsg",
                   "org.zstack.iam2.api.APIQueryIAM2ProjectMsg",
                   "org.zstack.scheduler.APIDeleteSchedulerJobMsg",
                   "org.zstack.header.aliyun.network.vpc.APIUpdateEcsVpcMsg",
                   "org.zstack.header.identity.APIDeleteUserMsg",
                   "org.zstack.header.volume.APICreateDataVolumeFromVolumeSnapshotMsg",
                   "org.zstack.header.configuration.APIChangeInstanceOfferingStateMsg",
                   "org.zstack.scheduler.APICreateSchedulerJobMsg",
                   "org.zstack.header.storage.database.backup.APICreateDatabaseBackupMsg",
                   "org.zstack.ticket.iam2.api.APIUpdateIAM2TicketFlowMsg",
                   "org.zstack.header.console.APIQueryConsoleProxyAgentMsg",
                   "org.zstack.v2v.APIUpdateV2VConversionHostMsg",
                   "org.zstack.header.core.webhooks.APIDeleteWebhookMsg",
                   "org.zstack.header.aliyun.network.connection.APIDeleteConnectionBetweenL3NetWorkAndAliyunVSwitchMsg",
                   "org.zstack.monitoring.APIGetMonitorItemMsg",
                   "org.zstack.aliyun.nas.message.APIAddAliyunNasAccessGroupMsg",
                   "org.zstack.vrouterRoute.APIQueryVRouterRouteTableMsg",
                   "org.zstack.header.storage.primary.APIDeletePrimaryStorageMsg",
                   "org.zstack.header.network.service.APIGetNetworkServiceTypesMsg",
                   "org.zstack.twoFactorAuthentication.APIGetTwoFactorAuthenticationSecretMsg",
                   "org.zstack.zwatch.alarm.sns.APIDeleteSNSTextTemplateMsg",
                   "org.zstack.header.baremetal.chassis.APIUpdateBaremetalChassisMsg",
                   "org.zstack.header.aliyun.network.vpc.APIDeleteEcsVSwitchRemoteMsg",
                   "org.zstack.header.volume.APIDetachDataVolumeFromVmMsg",
                   "org.zstack.zwatch.alarm.APIUnsubscribeEventMsg",
                   "org.zstack.header.tag.APIQuerySystemTagMsg",
                   "org.zstack.sns.APIDeleteSNSTopicMsg",
                   "org.zstack.storage.primary.nfs.APIAddNfsPrimaryStorageMsg",
                   "org.zstack.network.l2.vxlan.vxlanNetworkPool.APICreateL2VxlanNetworkPoolMsg",
                   "org.zstack.autoscaling.group.instance.APIQueryAutoScalingGroupInstanceMsg",
                   "org.zstack.iam2.api.APIRemoveAttributesFromIAM2ProjectMsg",
                   "org.zstack.header.vm.APISetVmBootModeMsg",
                   "org.zstack.iam2.api.APIUpdateIAM2OrganizationMsg",
                   "org.zstack.header.aliyun.oss.APIDeleteOssBucketNameLocalMsg",
                   "org.zstack.zwatch.alarm.sns.APIQuerySNSTextTemplateMsg",
                   "org.zstack.header.aliyun.ecs.APIDeleteEcsInstanceMsg",
                   "org.zstack.header.vm.APIGetVmCapabilitiesMsg",
                   "org.zstack.header.aliyun.network.vrouter.APIQueryAliyunVirtualRouterFromLocalMsg",
                   "org.zstack.iam2.api.APICreateIAM2ProjectTemplateFromProjectMsg",
                   "org.zstack.iam2.api.APIRecoverIAM2ProjectMsg",
                   "org.zstack.pciDevice.APIQueryPciDeviceOfferingMsg",
                   "org.zstack.header.network.l3.APIGetIpAddressCapacityMsg",
                   "org.zstack.network.securitygroup.APIDeleteVmNicFromSecurityGroupMsg",
                   "org.zstack.network.service.virtualrouter.APIReconnectVirtualRouterMsg",
                   "org.zstack.monitoring.media.APIChangeMediaStateMsg",
                   "org.zstack.header.aliyun.network.group.APICreateEcsSecurityGroupRuleRemoteMsg",
                   "org.zstack.vpc.APISetVpcVRouterNetworkServiceStateMsg",
                   "org.zstack.ipsec.APIDetachL3NetworksFromIPsecConnectionMsg",
                   "org.zstack.iam2.api.APIAddAttributesToIAM2OrganizationMsg",
                   "org.zstack.header.vm.APIQueryVmInstanceMsg",
                   "org.zstack.header.vm.APIGetVmConsolePasswordMsg",
                   "org.zstack.core.gc.APIDeleteGCJobMsg",
                   "org.zstack.header.aliyun.ecs.APIGetEcsInstanceTypeMsg",
                   "org.zstack.zwatch.alarm.APIRemoveLabelFromAlarmMsg",
                   "org.zstack.header.longjob.APIDeleteLongJobMsg",
                   "org.zstack.sns.platform.email.APIQuerySNSEmailPlatformMsg",
                   "org.zstack.ldap.APIQueryLdapBindingMsg",
                   "org.zstack.ticket.api.APICreateTicketMsg",
                   "org.zstack.header.affinitygroup.APIUpdateAffinityGroupMsg",
                   "org.zstack.autoscaling.group.rule.APIUpdateAutoScalingGroupAddingNewInstanceRuleMsg",
                   "org.zstack.header.aliyun.account.APIDeleteAliyunKeySecretMsg",
                   "org.zstack.storage.ceph.primary.APIQueryCephPrimaryStoragePoolMsg",
                   "org.zstack.network.securitygroup.APIDeleteSecurityGroupRuleMsg",
                   "org.zstack.header.identity.APIAttachPoliciesToUserMsg",
                   "org.zstack.header.network.l3.APIQueryIpAddressMsg",
                   "org.zstack.header.vm.APIGetVmMigrationCandidateHostsMsg",
                   "org.zstack.header.baremetal.chassis.APICreateBaremetalChassisMsg",
                   "org.zstack.aliyun.nas.message.APIAddAliyunNasFileSystemMsg",
                   "org.zstack.header.vipQos.APISetVipQosMsg",
                   "org.zstack.zwatch.api.APIUpdateEventDataMsg",
                   "org.zstack.network.securitygroup.APICreateSecurityGroupMsg",
                   "org.zstack.ticket.api.APIQueryTicketMsg",
                   "org.zstack.header.hybrid.network.vpn.APICreateVpnIpsecConfigMsg",
                   "org.zstack.header.vm.APIExpungeVmInstanceMsg",
                   "org.zstack.zwatch.alarm.APIUpdateAlarmLabelMsg",
                   "org.zstack.vrouterRoute.APIDeleteVRouterRouteTableMsg",
                   "org.zstack.header.vm.cdrom.APISetVmInstanceDefaultCdRomMsg",
                   "org.zstack.header.cluster.APICreateMiniClusterMsg",
                   "org.zstack.iam2.api.APIDeleteIAM2VirtualIDMsg",
                   "org.zstack.license.APIReloadLicenseMsg",
                   "org.zstack.header.identity.APIQueryAccountMsg",
                   "org.zstack.header.datacenter.APISyncDataCenterFromRemoteMsg",
                   "org.zstack.network.l2.vxlan.vxlanNetwork.APICreateL2VxlanNetworkMsg",
                   "org.zstack.autoscaling.group.rule.APIQueryAutoScalingRuleMsg",
                   "org.zstack.core.config.resourceconfig.APIGetResourceConfigMsg",
                   "org.zstack.header.vm.APIChangeVmImageMsg",
                   "org.zstack.network.service.virtualrouter.APIGetVipUsedPortsMsg",
                   "org.zstack.pciDevice.APIGetHostIommuStateMsg",
                   "org.zstack.header.aliyun.oss.APICreateOssBackupBucketRemoteMsg",
                   "org.zstack.iam2.api.APIUpdateIAM2VirtualIDGroupMsg",
                   "org.zstack.vmware.APIQueryVCenterBackupStorageMsg",
                   "org.zstack.header.baremetal.chassis.APIDeleteBaremetalChassisMsg",
                   "org.zstack.monitoring.prometheus.APIPrometheusQueryLabelValuesMsg",
                   "org.zstack.header.storage.database.backup.APIDeleteExportedDatabaseBackupFromBackupStorageMsg",
                   "org.zstack.zwatch.alarm.APIRemoveActionFromAlarmMsg",
                   "org.zstack.ldap.APICreateLdapBindingMsg",
                   "org.zstack.autoscaling.template.APICreateAutoScalingVmTemplateMsg",
                   "org.zstack.usbDevice.APIUpdateUsbDeviceMsg",
                   "org.zstack.header.allocator.APIGetCpuMemoryCapacityMsg",
                   "org.zstack.license.APIDeleteLicenseMsg",
                   "org.zstack.scheduler.APIRemoveSchedulerJobFromSchedulerTriggerMsg",
                   "org.zstack.header.hybrid.network.eip.APIQueryHybridEipFromLocalMsg",
                   "org.zstack.header.baremetal.instance.APIStopBaremetalInstanceMsg",
                   "org.zstack.aliyun.pangu.APIDeleteAliyunPanguPartitionMsg",
                   "org.zstack.header.vm.APISetVmConsolePasswordMsg",
                   "org.zstack.tag2.APIUpdateTagMsg",
                   "org.zstack.zwatch.alarm.APIAddLabelToEventSubscriptionMsg",
                   "org.zstack.header.affinitygroup.APIAddVmToAffinityGroupMsg",
                   "org.zstack.header.identity.APIUpdateUserMsg",
                   "org.zstack.header.identity.APIRenewSessionMsg",
                   "org.zstack.ticket.api.APIQueryTicketFlowCollectionMsg",
                   "org.zstack.header.configuration.APIQueryInstanceOfferingMsg",
                   "org.zstack.sns.platform.dingtalk.APIRemoveSNSDingTalkAtPersonMsg",
                   "org.zstack.header.vm.APISetVmQgaMsg",
                   "org.zstack.usbDevice.APIDetachUsbDeviceFromVmMsg",
                   "org.zstack.header.aliyun.image.APICreateEcsImageFromLocalImageMsg",
                   "org.zstack.header.vm.APICreateVmInstanceMsg",
                   "org.zstack.autoscaling.group.APIUpdateAutoScalingGroupMsg",
                   "org.zstack.header.network.l2.APIAttachL2NetworkToClusterMsg",
                   "org.zstack.header.aliyun.network.vrouter.APIDeleteVirtualRouterLocalMsg",
                   "org.zstack.header.storage.primary.APIUpdatePrimaryStorageMsg",
                   "org.zstack.header.affinitygroup.APIRemoveVmFromAffinityGroupMsg",
                   "org.zstack.header.identityzone.APISyncIdentityFromRemoteMsg",
                   "org.zstack.autoscaling.group.APIQueryAutoScalingGroupMsg",
                   "org.zstack.iam2.api.APIUpdateIAM2ProjectTemplateMsg",
                   "org.zstack.network.service.eip.APICreateEipMsg",
                   "org.zstack.header.identity.APILogOutMsg",
                   "org.zstack.header.aliyun.network.group.APIUpdateEcsSecurityGroupMsg",
                   "org.zstack.header.hybrid.network.vpn.APIQueryVpcUserVpnGatewayFromLocalMsg",
                   "org.zstack.iam2.api.APICreateIAM2OrganizationMsg",
                   "org.zstack.header.volume.APIResizeDataVolumeMsg",
                   "org.zstack.header.vm.APIStartVmInstanceMsg",
                   "org.zstack.monitoring.prometheus.APIPrometheusQueryVmMonitoringDataMsg",
                   "org.zstack.header.daho.process.APIUpdateDahoDataCenterConnectionMsg",
                   "org.zstack.vrouterRoute.APIUpdateVRouterRouteTableMsg",
                   "org.zstack.header.APIIsOpensourceVersionMsg",
                   "org.zstack.storage.backup.imagestore.APIAddDisasterImageStoreBackupStorageMsg",
                   "org.zstack.network.service.lb.APIUpdateLoadBalancerMsg",
                   "org.zstack.network.service.vip.APIQueryVipMsg",
                   "org.zstack.iam2.api.APIAddIAM2VirtualIDsToOrganizationMsg",
                   "org.zstack.header.storage.volume.backup.APISyncVmBackupFromImageStoreBackupStorageMsg",
                   "org.zstack.iam2.api.APIQueryIAM2ProjectAttributeMsg",
                   "org.zstack.ldap.APIAddLdapServerMsg",
                   "org.zstack.header.aliyun.network.vrouter.APICreateAliyunVpcVirtualRouterEntryRemoteMsg",
                   "org.zstack.header.aliyun.network.connection.APICreateAliyunRouterInterfaceRemoteMsg",
                   "org.zstack.sns.APIUpdateSNSApplicationEndpointMsg",
                   "org.zstack.network.service.eip.APIDeleteEipMsg",
                   "org.zstack.aliyun.nas.message.APICreateAliyunNasFileSystemMsg",
                   "org.zstack.header.identity.APIDetachPolicyFromUserMsg",
                   "org.zstack.header.storage.snapshot.APIRevertVolumeFromSnapshotMsg",
                   "org.zstack.aliyun.ebs.message.APIUpdateAliyunEbsBackupStorageMsg",
                   "org.zstack.header.aliyun.storage.disk.APIAttachAliyunDiskToEcsMsg",
                   "org.zstack.header.vm.APIMigrateVmMsg",
                   "org.zstack.header.hybrid.network.vpn.APIDeleteVpcUserVpnGatewayLocalMsg",
                   "org.zstack.zwatch.alarm.APIAddActionToEventSubscriptionMsg",
                   "org.zstack.autoscaling.group.APIChangeAutoScalingGroupStateMsg",
                   "org.zstack.core.gc.APITriggerGCJobMsg",
                   "org.zstack.header.aliyun.account.APIDetachAliyunKeyMsg",
                   "org.zstack.header.cloudformation.APIPreviewResourceStackMsg",
                   "org.zstack.header.volume.APIDeleteVolumeQosMsg",
                   "org.zstack.zwatch.alarm.APIAddLabelToAlarmMsg",
                   "org.zstack.header.vm.APIGetVmSshKeyMsg",
                   "org.zstack.aliyun.pangu.APIQueryAliyunPanguPartitionMsg",
                   "org.zstack.header.vm.APIDeleteNicQosMsg",
                   "org.zstack.zwatch.alarm.APIChangeAlarmStateMsg",
                   "org.zstack.network.service.virtualrouter.APIUpdateVirtualRouterOfferingMsg",
                   "org.zstack.header.storage.snapshot.APIQueryVolumeSnapshotMsg",
                   "org.zstack.header.longjob.APISubmitLongJobMsg",
                   "org.zstack.header.storage.backup.APIGetBackupStorageTypesMsg",
                   "org.zstack.header.vm.APIGetCandidateIsoForAttachingVmMsg",
                   "org.zstack.header.network.l3.APIAddIpRangeMsg",
                   "org.zstack.header.hybrid.network.vpn.APIQueryVpcVpnConnectionFromLocalMsg",
                   "org.zstack.header.storageDevice.APIDetachScsiLunFromVmInstanceMsg",
                   "org.zstack.header.hybrid.network.eip.APIDeleteHybridEipFromLocalMsg",
                   "org.zstack.usbDevice.APIGetUsbDeviceCandidatesForAttachingVmMsg",
                   "org.zstack.header.identity.APIGetResourceAccountMsg",
                   "org.zstack.scheduler.APICreateSchedulerTriggerMsg",
                   "org.zstack.header.hybrid.network.vpn.APIGetVpcVpnConfigurationFromRemoteMsg",
                   "org.zstack.header.configuration.APIQueryDiskOfferingMsg",
                   "org.zstack.header.host.APIChangeHostStateMsg",
                   "org.zstack.header.network.service.APIQueryNetworkServiceL3NetworkRefMsg",
                   "org.zstack.header.configuration.APIUpdateInstanceOfferingMsg",
                   "org.zstack.header.tag.APIQueryUserTagMsg",
                   "org.zstack.header.vm.APISetVmHostnameMsg",
                   "org.zstack.kvm.APIUpdateKVMHostMsg",
                   "org.zstack.header.aliyun.ecs.APIQueryEcsInstanceFromLocalMsg",
                   "org.zstack.pciDevice.APIQueryPciDeviceMsg",
                   "org.zstack.iam2.api.APIUpdateIAM2ProjectAttributeMsg",
                   "org.zstack.monitoring.APIAttachMonitorTriggerActionToTriggerMsg",
                   "org.zstack.header.storageDevice.APIGetScsiLunCandidatesForAttachingVmMsg",
                   "org.zstack.header.identity.APIAttachPolicyToUserMsg",
                   "org.zstack.header.vm.APIGetCandidateZonesClustersHostsForCreatingVmMsg",
                   "org.zstack.storage.migration.backup.APIGetBackupStorageCandidatesForImageMigrationMsg",
                   "org.zstack.autoscaling.template.APIQueryAutoScalingVmTemplateMsg",
                   "org.zstack.ipsec.APIUpdateIPsecConnectionMsg",
                   "org.zstack.aliyun.nas.message.APIGetAliyunNasFileSystemRemoteMsg",
                   "org.zstack.vpc.APISetVpcVRouterDistributedRoutingEnabledMsg",
                   "org.zstack.header.storage.backup.APIUpdateBackupStorageMsg",
                   "org.zstack.vrouterRoute.APIGetVRouterRouteTableMsg",
                   "org.zstack.nas.APIUpdateNasFileSystemMsg",
                   "org.zstack.header.aliyun.storage.snapshot.APIQueryAliyunSnapshotFromLocalMsg",
                   "org.zstack.zwatch.api.APIGetAllEventMetadataMsg",
                   "org.zstack.network.l2.vxlan.vxlanNetworkPool.APIQueryVniRangeMsg",
                   "org.zstack.query.APIZQLQueryMsg",
                   "org.zstack.header.storage.volume.backup.APICreateVmFromVmBackupMsg",
                   "org.zstack.network.service.lb.APIDeleteLoadBalancerListenerMsg",
                   "org.zstack.network.securitygroup.APIUpdateSecurityGroupMsg",
                   "org.zstack.scheduler.APIGetAvailableTriggersMsg",
                   "org.zstack.storage.backup.imagestore.APIGetImagesFromImageStoreBackupStorageMsg",
                   "org.zstack.billing.APICreateResourcePriceMsg",
                   "org.zstack.header.daho.process.APIDeleteDahoDataCenterConnectionMsg",
                   "org.zstack.tag2.APIQueryTagMsg",
                   "org.zstack.header.storage.volume.backup.APIRevertVolumeFromVolumeBackupMsg",
                   "org.zstack.header.baremetal.pxeserver.APIStopBaremetalPxeServerMsg",
                   "org.zstack.ipsec.APICreateIPsecConnectionMsg",
                   "org.zstack.loginControl.APIGetLoginCaptchaMsg",
                   "org.zstack.header.aliyun.network.vrouter.APIUpdateAliyunVirtualRouterMsg",
                   "org.zstack.header.cloudformation.APIQueryStackTemplateMsg",
                   "org.zstack.header.aliyun.network.vrouter.APISyncAliyunVirtualRouterFromRemoteMsg",
                   "org.zstack.header.vm.APIGetVmConsoleAddressMsg",
                   "org.zstack.header.network.service.APIAttachNetworkServiceToL3NetworkMsg",
                   "org.zstack.header.hybrid.network.vpn.APIUpdateVpcUserVpnGatewayMsg",
                   "org.zstack.vrouterRoute.APIQueryVRouterRouteEntryMsg",
                   "org.zstack.header.cloudformation.APIUpdateStackTemplateMsg",
                   "org.zstack.vpc.APIRemoveDnsFromVpcRouterMsg",
                   "org.zstack.storage.fusionstor.backup.APIRemoveMonFromFusionstorBackupStorageMsg",
                   "org.zstack.license.APIGetLicenseCapabilitiesMsg",
                   "org.zstack.header.storage.primary.APIQueryImageCacheMsg",
                   "org.zstack.header.image.APICreateRootVolumeTemplateFromRootVolumeMsg",
                   "org.zstack.header.aliyun.image.APIDeleteEcsImageLocalMsg",
                   "org.zstack.network.service.portforwarding.APIQueryPortForwardingRuleMsg",
                   "org.zstack.header.storage.volume.backup.APIRevertVmFromVmBackupMsg",
                   "org.zstack.vmware.APIQueryVCenterPrimaryStorageMsg",
                   "org.zstack.header.cluster.APICreateClusterMsg",
                   "org.zstack.header.image.APIGetCandidateBackupStorageForCreatingImageMsg",
                   "org.zstack.header.image.APIGetImageQgaMsg",
                   "org.zstack.network.service.lb.APIRefreshLoadBalancerMsg",
                   "org.zstack.storage.ceph.backup.APIRemoveMonFromCephBackupStorageMsg",
                   "org.zstack.header.baremetal.preconfiguration.APIQueryPreconfigurationTemplateMsg",
                   "org.zstack.header.volume.APIExpungeDataVolumeMsg",
                   "org.zstack.header.aliyun.network.group.APISyncEcsSecurityGroupRuleFromRemoteMsg",
                   "org.zstack.header.identity.APICreateUserMsg",
                   "org.zstack.header.hybrid.network.vpn.APISyncVpcVpnConnectionFromRemoteMsg",
                   "org.zstack.header.network.l2.APICreateL2VlanNetworkMsg",
                   "org.zstack.aliyun.nas.message.APIUpdateAliyunMountTargetMsg",
                   "org.zstack.tag2.APIDetachTagFromResourcesMsg",
                   "org.zstack.header.storage.primary.APICleanUpImageCacheOnPrimaryStorageMsg",
                   "org.zstack.header.aliyun.account.APIAttachAliyunKeyMsg",
                   "org.zstack.network.securitygroup.APIChangeSecurityGroupStateMsg",
                   "org.zstack.header.volume.APICreateDataVolumeMsg",
                   "org.zstack.pciDevice.APIDeletePciDeviceOfferingMsg",
                   "org.zstack.header.host.APIGetHypervisorTypesMsg",
                   "org.zstack.storage.migration.backup.APIBackupStorageMigrateImageMsg",
                   "org.zstack.header.identity.APIRemoveUserFromGroupMsg",
                   "org.zstack.iam2.api.APIGetIAM2ProjectsOfVirtualIDMsg",
                   "org.zstack.core.config.resourceconfig.APIUpdateResourceConfigMsg",
                   "org.zstack.ticket.api.APIChangeTicketStatusMsg",
                   "org.zstack.header.storage.volume.backup.APIRecoverBackupFromImageStoreBackupStorageMsg",
                   "org.zstack.core.config.APIUpdateGlobalConfigMsg",
                   "org.zstack.header.vm.APIAttachIsoToVmInstanceMsg",
                   "org.zstack.iam2.api.APICreateIAM2ProjectMsg",
                   "org.zstack.monitoring.APIDeleteAlertMsg",
                   "org.zstack.header.affinitygroup.APIDeleteAffinityGroupMsg",
                   "org.zstack.header.baremetal.pxeserver.APIDetachBaremetalPxeServerFromClusterMsg",
                   "org.zstack.usbDevice.APIQueryUsbDeviceMsg",
                   "org.zstack.header.vm.APICloneVmInstanceMsg",
                   "org.zstack.network.service.portforwarding.APIUpdatePortForwardingRuleMsg",
                   "org.zstack.storage.fusionstor.backup.APIUpdateFusionstorBackupStorageMonMsg",
                   "org.zstack.storage.fusionstor.primary.APIQueryFusionstorPrimaryStorageMsg",
                   "org.zstack.header.simulator.storage.primary.APIAddSimulatorPrimaryStorageMsg",
                   "org.zstack.zwatch.alarm.APIQueryEventSubscriptionMsg",
                   "org.zstack.header.vm.APIDeleteVmSshKeyMsg",
                   "org.zstack.header.storage.primary.APIGetPrimaryStorageTypesMsg",
                   "org.zstack.header.cluster.APIDeleteClusterMsg",
                   "org.zstack.header.aliyun.storage.disk.APICreateAliyunDiskFromRemoteMsg",
                   "org.zstack.storage.migration.primary.APIGetPrimaryStorageCandidatesForVolumeMigrationMsg",
                   "org.zstack.header.image.APIQueryImageMsg",
                   "org.zstack.header.identity.APIDetachPoliciesFromUserMsg",
                   "org.zstack.header.network.l3.APISetL3NetworkMtuMsg",
                   "org.zstack.header.cloudformation.APICheckStackTemplateParametersMsg",
                   "org.zstack.zwatch.api.APIGetMetricDataMsg",
                   "org.zstack.header.identity.APIValidateSessionMsg",
                   "org.zstack.header.hybrid.network.vpn.APISyncVpcUserVpnGatewayFromRemoteMsg",
                   "org.zstack.storage.device.iscsi.APIDeleteIscsiServerMsg",
                   "org.zstack.header.identity.APIUpdateQuotaMsg",
                   "org.zstack.vmware.APIQueryVCenterMsg",
                   "org.zstack.header.network.l2.APIDeleteL2NetworkMsg",
                   "org.zstack.network.securitygroup.APIDeleteSecurityGroupMsg",
                   "org.zstack.header.storage.backup.APIAttachBackupStorageToZoneMsg",
                   "org.zstack.header.aliyun.network.connection.APIUpdateConnectionBetweenL3NetWorkAndAliyunVSwitchMsg",
                   "org.zstack.header.vm.APISetVmUsbRedirectMsg",
                   "org.zstack.v2v.APICleanV2VConversionCacheMsg",
                   "org.zstack.header.volume.APIAttachDataVolumeToVmMsg",
                   "org.zstack.header.storage.database.backup.APISyncDatabaseBackupFromImageStoreBackupStorageMsg",
                   "org.zstack.header.console.APIUpdateConsoleProxyAgentMsg",
                   "org.zstack.header.aliyun.network.connection.APIGetConnectionBetweenL3NetworkAndAliyunVSwitchMsg",
                   "org.zstack.iam2.api.APIQueryIAM2ProjectTemplateMsg",
                   "org.zstack.header.image.APIUpdateImageMsg",
                   "org.zstack.zwatch.alarm.sns.APIUpdateSNSTextTemplateMsg",
                   "org.zstack.header.baremetal.pxeserver.APIAttachBaremetalPxeServerToClusterMsg",
                   "org.zstack.vrouterRoute.APIAttachVRouterRouteTableToVRouterMsg",
                   "org.zstack.header.aliyun.network.vpc.APISyncEcsVSwitchFromRemoteMsg",
                   "org.zstack.header.tag.APIUpdateSystemTagMsg",
                   "org.zstack.header.core.webhooks.APIUpdateWebhookMsg",
                   "org.zstack.header.hybrid.network.vpn.APIQueryVpcIkeConfigFromLocalMsg",
                   "org.zstack.header.cloudformation.APIQueryEventFromResourceStackMsg",
                   "org.zstack.header.aliyun.network.vpc.APIQueryEcsVpcFromLocalMsg",
                   "org.zstack.vmware.APIQueryVCenterClusterMsg",
                   "org.zstack.header.cloudformation.APIAddStackTemplateMsg",
                   "org.zstack.header.daho.process.APICreateDahoVllRemoteMsg",
                   "org.zstack.header.storage.primary.APIReconnectPrimaryStorageMsg",
                   "org.zstack.header.baremetal.pxeserver.APIQueryBaremetalPxeServerMsg",
                   "org.zstack.header.storage.primary.APIGetTrashOnPrimaryStorageMsg",
                   "org.zstack.header.storage.backup.APIDeleteBackupStorageMsg",
                   "org.zstack.header.baremetal.preconfiguration.APIChangePreconfigurationTemplateStateMsg",
                   "org.zstack.header.network.l2.APICreateL2NoVlanNetworkMsg",
                   "org.zstack.header.daho.process.APISyncDahoVllMsg",
                   "org.zstack.zwatch.api.APIGetMetricLabelValueMsg",
                   "org.zstack.header.storage.database.backup.APIRecoverDatabaseFromBackupMsg",
                   "org.zstack.header.baremetal.pxeserver.APIStartBaremetalPxeServerMsg",
                   "org.zstack.header.baremetal.chassis.APICheckBaremetalChassisConfigFileMsg",
                   "org.zstack.zwatch.alarm.sns.APICreateSNSTextTemplateMsg",
                   "org.zstack.network.service.lb.APIDeleteLoadBalancerMsg",
                   "org.zstack.monitoring.media.APIUpdateEmailMediaMsg",
                   "org.zstack.storage.primary.sharedblock.APIRefreshSharedblockDeviceCapacityMsg",
                   "org.zstack.iam2.api.APIRemoveIAM2VirtualIDsFromOrganizationMsg",
                   "org.zstack.header.vm.APISetVmBootOrderMsg",
                   "org.zstack.header.network.l2.APIDetachL2NetworkFromClusterMsg",
                   "org.zstack.header.vm.APIGetVmMonitorNumberMsg",
                   "org.zstack.header.aliyun.image.APICreateEcsImageFromEcsSnapshotMsg",
                   "org.zstack.header.baremetal.instance.APIExpungeBaremetalInstanceMsg",
                   "org.zstack.header.network.l3.APIRemoveDnsFromL3NetworkMsg",
                   "org.zstack.header.vm.APIGetVmStartingCandidateClustersHostsMsg",
                   "org.zstack.header.cloudformation.APIUpdateResourceStackMsg",
                   "org.zstack.header.hybrid.network.vpn.APICreateVpcUserVpnGatewayRemoteMsg",
                   "org.zstack.zwatch.api.APIDeleteMetricDataMsg",
                   "org.zstack.header.vm.APIChangeVmPasswordMsg",
                   "org.zstack.header.image.APIDeleteImageMsg",
                   "org.zstack.core.errorcode.APICheckElaborationContentMsg",
                   "org.zstack.iam2.api.APIExpungeIAM2ProjectMsg",
                   "org.zstack.ha.APISetVmInstanceHaLevelMsg",
                   "org.zstack.monitoring.APIDetachMonitorTriggerActionFromTriggerMsg",
                   "org.zstack.header.volume.APIDeleteDataVolumeMsg",
                   "org.zstack.header.aliyun.network.group.APIDeleteEcsSecurityGroupRuleRemoteMsg",
                   "org.zstack.header.aliyun.ecs.APIDeleteEcsInstanceLocalMsg",
                   "org.zstack.accessKey.APIDeleteAccessKeyMsg",
                   "org.zstack.sns.APISubscribeSNSTopicMsg",
                   "org.zstack.vrouterRoute.APICreateVRouterRouteTableMsg",
                   "org.zstack.storage.primary.local.APIGetLocalStorageHostDiskCapacityMsg",
                   "org.zstack.header.identity.APIShareResourceMsg",
                   "org.zstack.storage.ceph.primary.APIAddMonToCephPrimaryStorageMsg",
                   "org.zstack.network.service.portforwarding.APIChangePortForwardingRuleStateMsg",
                   "org.zstack.header.image.APICreateDataVolumeTemplateFromVolumeMsg",
                   "org.zstack.header.aliyun.storage.snapshot.APIGCAliyunSnapshotRemoteMsg",
                   "org.zstack.monitoring.APIQueryAlertMsg",
                   "org.zstack.header.affinitygroup.APIChangeAffinityGroupStateMsg",
                   "org.zstack.header.cloudformation.APIRestartResourceStackMsg",
                   "org.zstack.accessKey.APIChangeAccessKeyStateMsg",
                   "org.zstack.network.l2.vxlan.vxlanNetworkPool.APIUpdateVniRangeMsg",
                   "org.zstack.header.storage.primary.APIAttachPrimaryStorageToClusterMsg",
                   "org.zstack.header.aliyun.network.connection.APIDeleteVirtualBorderRouterLocalMsg",
                   "org.zstack.header.hybrid.account.APIUpdateHybridKeySecretMsg",
                   "org.zstack.header.aliyun.network.connection.APITerminateVirtualBorderRouterRemoteMsg",
                   "org.zstack.header.aliyun.ecs.APIGetEcsInstanceVncUrlMsg",
                   "org.zstack.sns.APIQuerySNSTopicMsg",
                   "org.zstack.storage.backup.imagestore.APIRecoveryImageFromImageStoreBackupStorageMsg",
                   "org.zstack.scheduler.APIUpdateSchedulerTriggerMsg",
                   "org.zstack.header.network.l2.APIQueryL2VlanNetworkMsg",
                   "org.zstack.header.aliyun.network.vpc.APIUpdateEcsVSwitchMsg",
                   "org.zstack.header.volume.APIQueryVolumeMsg",
                   "org.zstack.storage.primary.local.APILocalStorageGetVolumeMigratableHostsMsg",
                   "org.zstack.header.baremetal.pxeserver.APIDeleteBaremetalPxeServerMsg",
                   "org.zstack.header.vm.APISetVmRDPMsg",
                   "org.zstack.header.network.l3.APIQueryIpRangeMsg",
                   "org.zstack.header.aliyun.network.group.APISyncEcsSecurityGroupFromRemoteMsg",
                   "org.zstack.header.network.l3.APIGetL3NetworkMtuMsg",
                   "org.zstack.header.daho.process.APIQueryDahoVllMsg",
                   "org.zstack.header.configuration.APICreateInstanceOfferingMsg",
                   "org.zstack.kvm.APIKvmRunShellMsg",
                   "org.zstack.pciDevice.APICreatePciDeviceOfferingMsg",
                   "org.zstack.storage.backup.imagestore.APIUpdateImageStoreBackupStorageMsg",
                   "org.zstack.header.aliyun.network.group.APIDeleteEcsSecurityGroupInLocalMsg",
                   "org.zstack.zwatch.alarm.APISubscribeEventMsg",
                   "org.zstack.header.zone.APIDeleteZoneMsg",
                   "org.zstack.header.image.APIRecoverImageMsg",
                   "org.zstack.header.vm.APIPauseVmInstanceMsg",
                   "org.zstack.iam2.api.APIQueryIAM2OrganizationMsg",
                   "org.zstack.header.storage.database.backup.APIGetDatabaseBackupFromImageStoreMsg",
                   "org.zstack.header.storage.volume.backup.APIRecoverVmBackupFromImageStoreBackupStorageMsg",
                   "org.zstack.header.hybrid.network.eip.APISyncHybridEipFromRemoteMsg",
                   "org.zstack.autoscaling.template.APIAttachAutoScalingTemplateToGroupMsg",
                   "org.zstack.header.baremetal.instance.APIRecoverBaremetalInstanceMsg",
                   "org.zstack.header.host.APIAddKVMHostFromConfigFileMsg",
                   "org.zstack.header.baremetal.chassis.APIQueryBaremetalChassisMsg",
                   "org.zstack.sns.APIUpdateSNSApplicationPlatformMsg",
                   "org.zstack.storage.ceph.backup.APIUpdateCephBackupStorageMonMsg",
                   "org.zstack.header.hybrid.network.eip.APIDeleteHybridEipRemoteMsg",
                   "org.zstack.header.daho.process.APIQueryDahoDataCenterConnectionMsg",
                   "org.zstack.header.cloudformation.APIDeleteResourceStackMsg",
                   "org.zstack.storage.migration.primary.APIGetPrimaryStorageCandidatesForVmMigrationMsg",
                   "org.zstack.network.service.vip.APIDeleteVipMsg",
                   "org.zstack.header.vm.APISetVmCleanTrafficMsg",
                   "org.zstack.core.errorcode.APIGetElaborationsMsg",
                   "org.zstack.header.storage.backup.APIGetBackupStorageCapacityMsg",
                   "org.zstack.sns.platform.email.APICreateSNSEmailEndpointMsg",
                   "org.zstack.header.hybrid.network.vpn.APIQueryVpcIpSecConfigFromLocalMsg",
                   "org.zstack.zwatch.api.APIPutMetricDataMsg",
                   "org.zstack.header.daho.process.APIUpdateDahoCloudConnectionMsg",
                   "org.zstack.tag2.APIAttachTagToResourcesMsg",
                   "org.zstack.iam2.api.APIChangeIAM2OrganizationParentMsg",
                   "org.zstack.aliyunproxy.vpc.APICreateAliyunProxyVSwitchMsg",
                   "org.zstack.ticket.api.APIQueryArchiveTicketHistoryMsg",
                   "org.zstack.storage.fusionstor.backup.APIAddFusionstorBackupStorageMsg",
                   "org.zstack.network.service.flat.APIGetL3NetworkDhcpIpAddressMsg",
                   "org.zstack.vmware.APIUpdateVCenterMsg",
                   "org.zstack.header.identity.APICheckResourcePermissionMsg",
                   "org.zstack.twoFactorAuthentication.APIQueryTwoFactorAuthenticationMsg",
                   "org.zstack.zwatch.alarm.APIRemoveLabelFromEventSubscriptionMsg",
                   "org.zstack.core.debug.APIDebugSignalMsg",
                   "org.zstack.iam2.api.APIUpdateIAM2OrganizationAttributeMsg",
                   "org.zstack.iam2.api.APIRemoveIAM2VirtualIDsFromProjectMsg",
                   "org.zstack.header.baremetal.chassis.APIGetBaremetalChassisPowerStatusMsg",
                   "org.zstack.header.baremetal.pxeserver.APICreateBaremetalPxeServerMsg",
                   "org.zstack.billing.APIQueryResourcePriceMsg",
                   "org.zstack.sns.APIUnsubscribeSNSTopicMsg",
                   "org.zstack.header.aliyun.ecs.APIStopEcsInstanceMsg",
                   "org.zstack.header.storage.primary.APIDetachPrimaryStorageFromClusterMsg",
                   "org.zstack.header.volume.APISyncVolumeSizeMsg",
                   "org.zstack.storage.ceph.primary.APIQueryCephPrimaryStorageMsg",
                   "org.zstack.header.simulator.APIAddSimulatorHostMsg",
                   "org.zstack.header.identity.APIQueryAccountResourceRefMsg",
                   "org.zstack.header.cluster.APIUpdateClusterMsg",
                   "org.zstack.header.identityzone.APIQueryIdentityZoneFromLocalMsg",
                   "org.zstack.header.host.APIDeleteHostMsg",
                   "org.zstack.iam2.api.APIAddRolesToIAM2VirtualIDGroupMsg",
                   "org.zstack.header.aliyun.ecs.APICreateEcsInstanceFromEcsImageMsg",
                   "org.zstack.header.cloudformation.APIDeleteStackTemplateMsg",
                   "org.zstack.vpc.APIGetVpcVRouterNetworkServiceStateMsg",
                   "org.zstack.header.aliyun.storage.disk.APIDetachAliyunDiskFromEcsMsg",
                   "org.zstack.header.vm.cdrom.APIDeleteVmCdRomMsg",
                   "org.zstack.storage.ceph.primary.APIUpdateCephPrimaryStoragePoolMsg",
                   "org.zstack.ipsec.APIDeleteIPsecConnectionMsg",
                   "org.zstack.header.vm.APIDeleteVmConsolePasswordMsg",
                   "org.zstack.header.daho.process.APISyncDahoCloudConnectionMsg",
                   "org.zstack.header.managementnode.APIGetCurrentTimeMsg",
                   "org.zstack.iam2.api.APICreateIAM2ProjectTemplateMsg",
                   "org.zstack.network.service.eip.APIAttachEipMsg",
                   "org.zstack.header.vm.APIDeleteVmHostnameMsg",
                   "org.zstack.ticket.iam2.api.APICreateIAM2TickFlowCollectionMsg",
                   "org.zstack.header.zone.APIUpdateZoneMsg",
                   "org.zstack.header.baremetal.pxeserver.APIUpdateBaremetalPxeServerMsg",
                   "org.zstack.header.aliyun.ecs.APIStartEcsInstanceMsg",
                   "org.zstack.billing.APICalculateResourceSpendingMsg",
                   "org.zstack.storage.device.fibreChannel.APIQueryFiberChannelStorageMsg",
                   "org.zstack.iam2.api.APICreateIAM2VirtualIDMsg",
                   "org.zstack.header.hybrid.network.vpn.APIDeleteVpcVpnGatewayLocalMsg",
                   "org.zstack.header.daho.process.APIUpdateDahoVllMsg",
                   "org.zstack.v2v.APIConvertVmFromForeignHypervisorMsg",
                   "org.zstack.iam2.api.APIRemoveAttributesFromIAM2VirtualIDMsg",
                   "org.zstack.network.securitygroup.APIQuerySecurityGroupRuleMsg",
                   "org.zstack.aliyun.ebs.message.APIQueryAliyunEbsPrimaryStorageMsg",
                   "org.zstack.header.aliyun.image.APIDeleteEcsImageRemoteMsg",
                   "org.zstack.header.aliyun.ecs.APIUpdateEcsInstanceVncPasswordMsg",
                   "org.zstack.header.identity.APICheckApiPermissionMsg",
                   "org.zstack.v2v.APIChangeV2VConversionHostStateMsg",
                   "org.zstack.billing.APIDeleteResourcePriceMsg",
                   "org.zstack.storage.primary.local.APIAddLocalPrimaryStorageMsg",
                   "org.zstack.autoscaling.group.rule.APIUpdateAutoScalingGroupRemovalInstanceRuleMsg",
                   "org.zstack.iam2.api.APIAddAttributesToIAM2ProjectMsg",
                   "org.zstack.header.aliyun.storage.snapshot.APISyncAliyunSnapshotRemoteMsg",
                   "org.zstack.header.aliyun.network.vpc.APISyncEcsVpcFromRemoteMsg",
                   "org.zstack.ipsec.APIAddRemoteCidrsToIPsecConnectionMsg",
                   "org.zstack.header.storage.volume.backup.APIDeleteVolumeBackupMsg",
                   "org.zstack.header.image.APIAddImageMsg",
                   "org.zstack.header.hybrid.backup.APIDownloadBackupFileFromPublicCloudMsg",
                   "org.zstack.header.aliyun.network.group.APIQueryEcsSecurityGroupFromLocalMsg",
                   "org.zstack.header.vm.APIAttachVmNicToVmMsg",
                   "org.zstack.network.l2.vxlan.vtep.APIQueryVtepMsg",
                   "org.zstack.ldap.APICleanInvalidLdapBindingMsg",
                   "org.zstack.network.service.virtualrouter.APICreateVirtualRouterOfferingMsg",
                   "org.zstack.autoscaling.group.rule.trigger.APICreateAutoScalingRuleAlarmTriggerMsg",
                   "org.zstack.header.hybrid.account.APIAttachHybridKeyMsg",
                   "org.zstack.nas.APIQueryNasMountTargetMsg",
                   "org.zstack.header.hybrid.network.vpn.APISyncVpcVpnGatewayFromRemoteMsg",
                   "org.zstack.header.baremetal.chassis.APIPowerOffBaremetalChassisMsg",
                   "org.zstack.ticket.iam2.api.APIUpdateIAM2TicketFlowCollectionMsg",
                   "org.zstack.header.vm.APIDeleteVmBootModeMsg",
                   "org.zstack.network.l2.vxlan.vxlanNetworkPool.APIQueryL2VxlanNetworkPoolMsg",
                   "org.zstack.header.storageDevice.APIUpdateScsiLunMsg",
                   "org.zstack.vmware.APISyncVCenterMsg",
                   "org.zstack.header.identity.APIChangeResourceOwnerMsg",
                   "org.zstack.iam2.api.APIQueryIAM2VirtualIDGroupAttributeMsg",
                   "org.zstack.header.aliyun.network.vpc.APICreateEcsVpcRemoteMsg",
                   "org.zstack.monitoring.actions.APIQueryMonitorTriggerActionMsg",
                   "org.zstack.network.service.portforwarding.APIDeletePortForwardingRuleMsg",
                   "org.zstack.core.errorcode.APIGetMissedElaborationMsg",
                   "org.zstack.aliyunproxy.vpc.APIQueryAliyunProxyVSwitchMsg",
                   "org.zstack.header.vm.APIDestroyVmInstanceMsg",
                   "org.zstack.header.zone.APIChangeZoneStateMsg",
                   "org.zstack.header.baremetal.preconfiguration.APIUpdatePreconfigurationTemplateMsg",
                   "org.zstack.header.aliyun.network.vrouter.APISyncAliyunRouteEntryFromRemoteMsg",
                   "org.zstack.header.hybrid.network.vpn.APIDeleteVpcIpSecConfigLocalMsg",
                   "org.zstack.header.longjob.APICancelLongJobMsg",
                   "org.zstack.header.aliyun.oss.APIGetOssBucketNameFromRemoteMsg",
                   "org.zstack.network.service.eip.APIGetEipAttachableVmNicsMsg",
                   "org.zstack.header.storage.snapshot.APIDeleteVolumeSnapshotMsg",
                   "org.zstack.sns.platform.http.APICreateSNSHttpEndpointMsg",
                   "org.zstack.header.network.l3.APICheckIpAvailabilityMsg",
                   "org.zstack.iam2.api.APIRemoveAttributesFromIAM2OrganizationMsg",
                   "org.zstack.storage.backup.sftp.APIReconnectSftpBackupStorageMsg",
                   "org.zstack.network.service.lb.APICreateCertificateMsg",
                   "org.zstack.header.volume.APIGetVolumeQosMsg",
                   "org.zstack.iam2.api.APIAddAttributesToIAM2VirtualIDGroupMsg",
                   "org.zstack.iam2.api.APIGetIAM2VirtualIDAPIPermissionMsg",
                   "org.zstack.zwatch.alarm.APIQueryAlarmMsg",
                   "org.zstack.iam2.api.APIAddIAM2VirtualIDsToGroupMsg",
                   "org.zstack.autoscaling.group.rule.APIUpdateAutoScalingRuleMsg",
                   "org.zstack.nas.APIQueryNasFileSystemMsg",
                   "org.zstack.header.aliyun.storage.disk.APIQueryAliyunDiskFromLocalMsg",
                   "org.zstack.header.baremetal.instance.APIStartBaremetalInstanceMsg",
                   "org.zstack.header.baremetal.instance.APIDestroyBaremetalInstanceMsg",
                   "org.zstack.storage.device.iscsi.APIUpdateIscsiServerMsg",
                   "org.zstack.header.affinitygroup.APIQueryAffinityGroupMsg",
                   "org.zstack.monitoring.actions.APIChangeMonitorTriggerActionStateMsg",
                   "org.zstack.iam2.api.APIDeleteIAM2ProjectMsg",
                   "org.zstack.header.aliyun.network.vpc.APIDeleteEcsVSwitchInLocalMsg",
                   "org.zstack.iam2.api.APIAddIAM2VirtualIDsToProjectMsg",
                   "org.zstack.header.cloudformation.APIGetSupportedCloudFormationResourcesMsg",
                   "org.zstack.iam2.api.APIRemoveAttributesFromIAM2VirtualIDGroupMsg",
                   "org.zstack.iam2.api.APICreateIAM2ProjectFromTemplateMsg",
                   "org.zstack.header.identity.APIQuerySharedResourceMsg",
                   "org.zstack.iam2.api.APIChangeIAM2OrganizationStateMsg",
                   "org.zstack.header.daho.process.APIDeleteDahoCloudConnectionMsg",
                   "org.zstack.header.storage.backup.APIGetTrashOnBackupStorageMsg",
                   "org.zstack.network.l2.vxlan.vtep.APICreateVxlanVtepMsg",
                   "org.zstack.ipsec.APIQueryIPSecConnectionMsg",
                   "org.zstack.header.aliyun.network.connection.APICreateConnectionBetweenL3NetworkAndAliyunVSwitchMsg",
                   "org.zstack.iam2.api.APIQueryIAM2VirtualIDMsg",
                   "org.zstack.storage.device.iscsi.APIDetachIscsiServerFromClusterMsg",
                   "org.zstack.vpc.APICreateVpcVRouterMsg",
                   "org.zstack.aliyun.nas.message.APIDeleteAliyunNasAccessGroupMsg",
                   "org.zstack.header.storage.snapshot.APIUpdateVolumeSnapshotMsg",
                   "org.zstack.vrouterRoute.APIDetachVRouterRouteTableFromVRouterMsg",
                   "org.zstack.header.vo.APIGetResourceNamesMsg",
                   "org.zstack.header.image.APISetImageQgaMsg",
                   "org.zstack.header.storage.primary.APIGetPrimaryStorageAllocatorStrategiesMsg",
                   "org.zstack.header.managementnode.APIGetVersionMsg",
                   "org.zstack.header.datacenter.APIGetDataCenterFromRemoteMsg",
                   "org.zstack.header.aliyun.network.vpc.APIDeleteEcsVpcInLocalMsg",
                   "org.zstack.header.network.l3.APIQueryL3NetworkMsg",
                   "org.zstack.header.aliyun.network.vpc.APIDeleteEcsVpcRemoteMsg",
                   "org.zstack.header.aliyun.image.APIGetCreateEcsImageProgressMsg",
                   "org.zstack.storage.backup.imagestore.APISyncImageFromImageStoreBackupStorageMsg",
                   "org.zstack.header.image.APICreateDataVolumeTemplateFromVolumeSnapshotMsg",
                   "org.zstack.network.service.eip.APIDetachEipMsg",
                   "org.zstack.header.network.l2.APIUpdateL2NetworkMsg",
                   "org.zstack.storage.backup.imagestore.APIQueryImageStoreBackupStorageMsg",
                   "org.zstack.pciDevice.APIDetachPciDeviceFromVmMsg",
                   "org.zstack.header.core.webhooks.APIQueryWebhookMsg",
                   "org.zstack.aliyun.nas.message.APIGetAliyunNasAccessGroupRemoteMsg",
                   "org.zstack.scheduler.APIQuerySchedulerJobMsg",
                   "org.zstack.ticket.api.APIChangeTicketFlowCollectionStateMsg",
                   "org.zstack.iam2.api.APIGetIAM2SystemAttributesMsg",
                   "org.zstack.header.storage.primary.APISyncPrimaryStorageCapacityMsg",
                   "org.zstack.header.core.progress.APIGetTaskProgressMsg",
                   "org.zstack.nas.APIUpdateNasMountTargetMsg",
                   "org.zstack.header.storage.backup.APIDetachBackupStorageFromZoneMsg",
                   "org.zstack.header.zone.APIQueryZoneMsg",
                   "org.zstack.header.configuration.APICreateDiskOfferingMsg",
                   "org.zstack.header.hybrid.network.vpn.APIDeleteVpcIkeConfigLocalMsg",
                   "org.zstack.vpc.APIQueryVpcRouterMsg",
                   "org.zstack.header.storage.snapshot.APICreateVolumesSnapshotMsg",
                   "org.zstack.header.aliyun.oss.APIUpdateOssBucketMsg",
                   "org.zstack.header.hybrid.network.vpn.APIQueryVpcVpnGatewayFromLocalMsg",
                   "org.zstack.header.aliyun.oss.APIDeleteOssBucketFileRemoteMsg",
                   "org.zstack.billing.APICalculateAccountSpendingMsg",
                   "org.zstack.network.service.portforwarding.APIAttachPortForwardingRuleMsg",
                   "org.zstack.header.vm.APIRebootVmInstanceMsg",
                   "org.zstack.header.network.l3.APIChangeL3NetworkStateMsg",
                   "org.zstack.header.network.l2.APIQueryL2NetworkMsg",
                   "org.zstack.header.network.l3.APIGetL3NetworkTypesMsg",
                   "org.zstack.header.configuration.APIUpdateDiskOfferingMsg",
                   "org.zstack.sns.platform.http.APIQuerySNSHttpEndpointMsg",
                   "org.zstack.sns.APIChangeSNSApplicationPlatformStateMsg",
                   "org.zstack.header.aliyun.network.connection.APIUpdateAliyunRouteInterfaceRemoteMsg",
                   "org.zstack.header.affinitygroup.APICreateAffinityGroupMsg",
                   "org.zstack.monitoring.media.APIDeleteMediaMsg",
                   "org.zstack.header.storage.backup.APIChangeBackupStorageStateMsg",
                   "org.zstack.header.aliyun.image.APISyncEcsImageFromRemoteMsg",
                   "org.zstack.header.simulator.storage.backup.APIAddSimulatorBackupStorageMsg",
                   "org.zstack.network.service.lb.APIQueryLoadBalancerMsg",
                   "org.zstack.header.longjob.APIRerunLongJobMsg",
                   "org.zstack.header.storage.database.backup.APISyncDatabaseBackupMsg",
                   "org.zstack.header.aliyun.storage.disk.APIDeleteAliyunDiskFromRemoteMsg",
                   "org.zstack.header.aliyun.storage.disk.APISyncDiskFromAliyunFromRemoteMsg",
                   "org.zstack.zwatch.alarm.APIRemoveActionFromEventSubscriptionMsg",
                   "org.zstack.zwatch.api.APIUpdateAlarmDataMsg",
                   "org.zstack.header.aliyun.network.connection.APIQueryVirtualBorderRouterFromLocalMsg",
                   "org.zstack.header.vipQos.APIDeleteVipQosMsg",
                   "org.zstack.ldap.APIGetCandidateLdapEntryForBindingMsg",
                   "org.zstack.header.volume.APIChangeVolumeStateMsg",
                   "org.zstack.zwatch.api.APIGetEventDataMsg",
                   "org.zstack.sns.APIDeleteSNSApplicationEndpointMsg",
                   "org.zstack.header.network.l3.APIGetFreeIpMsg",
                   "org.zstack.header.aliyun.storage.disk.APIUpdateAliyunDiskMsg",
                   "org.zstack.aliyun.nas.message.APIAddAliyunNasMountTargetMsg",
                   "org.zstack.header.datacenter.APIAddDataCenterFromRemoteMsg",
                   "org.zstack.header.volume.APICreateVolumeSnapshotMsg",
                   "org.zstack.header.network.l3.APICreateL3NetworkMsg",
                   "org.zstack.header.aliyun.network.connection.APIDeleteAliyunRouterInterfaceLocalMsg",
                   "org.zstack.header.datacenter.APIDeleteDataCenterInLocalMsg",
                   "org.zstack.sns.APIQuerySNSApplicationEndpointMsg",
                   "org.zstack.ldap.APIUpdateLdapServerMsg",
                   "org.zstack.header.aliyun.oss.APIDetachOssBucketFromEcsDataCenterMsg",
                   "org.zstack.ha.APIGetVmInstanceHaLevelMsg",
                   "org.zstack.zwatch.alarm.APIUpdateAlarmMsg",
                   "org.zstack.header.image.APIChangeImageStateMsg",
                   "org.zstack.header.network.service.APIDetachNetworkServiceFromL3NetworkMsg",
                   "org.zstack.monitoring.media.APIQueryMediaMsg",
                   "org.zstack.vmware.APIQueryVCenterDatacenterMsg",
                   "org.zstack.storage.primary.sharedblock.APIAddSharedBlockToSharedBlockGroupMsg",
                   "org.zstack.iam2.api.APIUpdateIAM2VirtualIDMsg",
                   "org.zstack.header.volume.APISetVolumeQosMsg",
                   "org.zstack.storage.backup.sftp.APIUpdateSftpBackupStorageMsg",
                   "org.zstack.network.service.lb.APICreateLoadBalancerMsg",
                   "org.zstack.header.aliyun.network.group.APIQueryEcsSecurityGroupRuleFromLocalMsg",
                   "org.zstack.storage.ceph.primary.APIRemoveMonFromCephPrimaryStorageMsg",
                   "org.zstack.scheduler.APIQuerySchedulerTriggerMsg",
                   "org.zstack.storage.migration.primary.APIPrimaryStorageMigrateVolumeMsg",
                   "org.zstack.header.aliyun.oss.APIQueryOssBucketFileNameMsg",
                   "org.zstack.pciDevice.APIUpdatePciDeviceMsg",
                   "org.zstack.header.storage.backup.APIDeleteExportedImageFromBackupStorageMsg",
                   "org.zstack.network.service.lb.APIRemoveCertificateFromLoadBalancerListenerMsg",
                   "org.zstack.header.volume.APIGetVolumeCapabilitiesMsg",
                   "org.zstack.header.storage.primary.APICleanUpTrashOnPrimaryStorageMsg",
                   "org.zstack.network.service.lb.APIAddVmNicToLoadBalancerMsg",
                   "org.zstack.header.vm.APISetVmSshKeyMsg",
                   "org.zstack.header.aliyun.oss.APIGetOssBackupBucketFromRemoteMsg",
                   "org.zstack.network.service.lb.APIQueryLoadBalancerListenerMsg",
                   "org.zstack.header.aliyun.account.APIAddAliyunKeySecretMsg",
                   "org.zstack.storage.backup.imagestore.APIAddImageStoreBackupStorageMsg",
                   "org.zstack.autoscaling.group.rule.APICreateAutoScalingGroupAddingNewInstanceRuleMsg",
                   "org.zstack.header.aliyun.network.connection.APISyncVirtualBorderRouterFromRemoteMsg",
                   "org.zstack.storage.primary.sharedblock.APIQuerySharedBlockGroupPrimaryStorageHostRefMsg",
                   "org.zstack.header.storage.backup.APIExportImageFromBackupStorageMsg",
                   "org.zstack.header.vm.APIQueryVmNicMsg",
                   "org.zstack.sns.platform.dingtalk.APIQuerySNSDingTalkEndpointMsg",
                   "org.zstack.header.hybrid.network.vpn.APICreateVpcVpnConnectionRemoteMsg",
                   "org.zstack.network.securitygroup.APIQuerySecurityGroupMsg",
                   "org.zstack.ldap.APIDeleteLdapBindingMsg",
                   "org.zstack.iam2.api.APIQueryIAM2VirtualIDGroupMsg",
                   "org.zstack.header.network.l3.APISetL3NetworkRouterInterfaceIpMsg",
                   "org.zstack.header.storage.volume.backup.APICreateDataVolumeTemplateFromVolumeBackupMsg",
                   "org.zstack.ticket.api.APIQueryTicketFlowMsg",
                   "org.zstack.appliancevm.APIQueryApplianceVmMsg",
                   "org.zstack.header.storageDevice.APIQueryScsiLunMsg",
                   "org.zstack.storage.device.iscsi.APIAttachIscsiServerToClusterMsg",
                   "org.zstack.header.volume.APICreateDataVolumeFromVolumeTemplateMsg",
                   "org.zstack.network.service.lb.APIAddCertificateToLoadBalancerListenerMsg",
                   "org.zstack.header.baremetal.instance.APICreateBaremetalInstanceMsg",
                   "org.zstack.header.vm.APIUpdateVmNicMacMsg",
                   "org.zstack.header.baremetal.pxeserver.APIReconnectBaremetalPxeServerMsg",
                   "org.zstack.header.vm.APIDeleteVmNicMsg",
                   "org.zstack.scheduler.APIDeleteSchedulerTriggerMsg",
                   "org.zstack.header.daho.process.APIDeleteDahoVllMsg",
                   "org.zstack.header.vm.APIGetVmAttachableL3NetworkMsg",
                   "org.zstack.aliyun.pangu.APIUpdateAliyunPanguPartitionMsg",
                   "org.zstack.network.service.lb.APICreateLoadBalancerListenerMsg",
                   "org.zstack.vmware.APIAddVCenterMsg",
                   "org.zstack.network.service.virtualrouter.APIQueryVirtualRouterOfferingMsg",
                   "org.zstack.network.service.vip.APIChangeVipStateMsg",
                   "org.zstack.sns.APIQuerySNSTopicSubscriberMsg",
                   "org.zstack.scheduler.APIUpdateSchedulerJobMsg",
                   "org.zstack.header.hybrid.network.vpn.APICreateVpnIkeConfigMsg",
                   "org.zstack.header.console.APIReconnectConsoleProxyAgentMsg",
                   "org.zstack.network.service.eip.APIChangeEipStateMsg",
                   "org.zstack.storage.ceph.backup.APIAddCephBackupStorageMsg",
                   "org.zstack.header.vm.APIGetVmBootOrderMsg",
                   "org.zstack.header.baremetal.network.APIQueryBaremetalBondingMsg",
                   "org.zstack.storage.device.fibreChannel.APIQueryFiberChannelLunMsg",
                   "org.zstack.storage.ceph.primary.APIUpdateCephPrimaryStorageMonMsg",
                   "org.zstack.nas.APIDeleteNasMountTargetMsg",
                   "org.zstack.header.baremetal.network.APICreateBaremetalBondingMsg",
                   "org.zstack.aliyun.ebs.message.APIQueryAliyunEbsBackupStorageMsg",
                   "org.zstack.header.aliyun.network.group.APICreateEcsSecurityGroupRemoteMsg",
                   "org.zstack.monitoring.actions.APIDeleteMonitorTriggerActionMsg",
                   "org.zstack.header.allocator.APIGetHostAllocatorStrategiesMsg",
                   "org.zstack.header.hybrid.account.APIQueryHybridKeySecretMsg",
                   "org.zstack.iam2.api.APIQueryIAM2OrganizationAttributeMsg",
                   "org.zstack.header.aliyun.network.connection.APIUpdateVirtualBorderRouterRemoteMsg",
                   "org.zstack.header.aliyun.network.connection.APIDeleteConnectionAccessPointLocalMsg",
                   "org.zstack.zwatch.api.APIGetAllMetricMetadataMsg",
                   "org.zstack.header.identity.APIDeletePolicyMsg",
                   "org.zstack.network.l2.vxlan.vxlanNetworkPool.APICreateVniRangeMsg",
                   "org.zstack.header.volume.APIRecoverDataVolumeMsg",
                   "org.zstack.header.identity.APILogInByAccountMsg",
                   "org.zstack.iam2.api.APIChangeIAM2VirtualIDStateMsg",
                   "org.zstack.v2v.APIQueryV2VConversionHostMsg",
                   "org.zstack.header.aliyun.network.vpc.APIQueryEcsVSwitchFromLocalMsg",
                   "org.zstack.header.aliyun.oss.APIAttachOssBucketToEcsDataCenterMsg",
                   "org.zstack.storage.fusionstor.backup.APIQueryFusionstorBackupStorageMsg",
                   "org.zstack.header.storage.volume.backup.APICreateVmBackupMsg",
                   "org.zstack.monitoring.APIDeleteMonitorTriggerMsg",
                   "org.zstack.sns.APIChangeSNSTopicStateMsg",
                   "org.zstack.iam2.api.APIChangeIAM2VirtualIDGroupStateMsg",
                   "org.zstack.header.aliyun.oss.APICreateOssBucketRemoteMsg",
                   "org.zstack.ticket.api.APIQueryArchiveTicketMsg",
                   "org.zstack.storage.backup.imagestore.APIReconnectImageStoreBackupStorageMsg",
                   "org.zstack.core.gc.APIQueryGCJobMsg",
                   "org.zstack.storage.ceph.backup.APIAddMonToCephBackupStorageMsg",
                   "org.zstack.header.vipQos.APIGetVipQosMsg",
                   "org.zstack.network.service.virtualrouter.APIQueryVirtualRouterVmMsg",
                   "org.zstack.header.hybrid.network.vpn.APIUpdateVpcVpnGatewayMsg",
                   "org.zstack.header.storage.snapshot.APIBatchDeleteVolumeSnapshotMsg",
                   "org.zstack.vrouterRoute.APIAddVRouterRouteEntryMsg",
                   "org.zstack.header.network.l3.APIUpdateL3NetworkMsg",
                   "org.zstack.storage.backup.sftp.APIQuerySftpBackupStorageMsg",
                   "org.zstack.ipsec.APIRemoveRemoteCidrsFromIPsecConnectionMsg",
                   "org.zstack.header.identity.APIDeleteUserGroupMsg",
                   "org.zstack.monitoring.media.APIQueryEmailMediaMsg",
                   "org.zstack.aliyunproxy.vpc.APICreateAliyunProxyVpcMsg",
                   "org.zstack.core.captcha.APIRefreshCaptchaMsg",
                   "org.zstack.ticket.iam2.api.APIAddIAM2TicketFlowMsg",
                   "org.zstack.monitoring.actions.APICreateEmailMonitorTriggerActionMsg",
                   "org.zstack.zwatch.alarm.APICreateAlarmMsg",
                   "org.zstack.header.hybrid.network.vpn.APIDeleteVpcUserVpnGatewayRemoteMsg",
                   "org.zstack.header.vm.APIDetachIsoFromVmInstanceMsg",
                   "org.zstack.storage.primary.smp.APIAddSharedMountPointPrimaryStorageMsg",
                   "org.zstack.header.host.APIReconnectHostMsg",
                   "org.zstack.network.service.eip.APIUpdateEipMsg",
                   "org.zstack.header.identity.APILogInByUserMsg",
                   "org.zstack.header.image.APICreateRootVolumeTemplateFromVolumeSnapshotMsg",
                   "org.zstack.monitoring.APIChangeMonitorTriggerStateMsg",
                   "org.zstack.ticket.iam2.api.APIDeleteIAM2TicketFlowMsg",
                   "org.zstack.autoscaling.group.rule.APICreateAutoScalingGroupRemovalInstanceRuleMsg",
                   "org.zstack.header.network.l3.APIDeleteL3NetworkMsg",
                   "org.zstack.aliyun.nas.message.APIQueryAliyunNasAccessGroupMsg",
                   "org.zstack.vpc.APIGetAttachableVpcL3NetworkMsg",
                   "org.zstack.header.aliyun.account.APIUpdateAliyunKeySecretMsg",
                   "org.zstack.header.cluster.APIUpdateClusterOSMsg",
                   "org.zstack.zwatch.api.APIGetAlarmDataMsg",
                   "org.zstack.header.identity.APIRevokeResourceSharingMsg",
                   "org.zstack.header.storageDevice.APIAttachScsiLunToVmInstanceMsg",
                   "org.zstack.header.aliyun.network.connection.APISyncAliyunRouterInterfaceFromRemoteMsg",
                   "org.zstack.ticket.api.APIDeleteTicketFlowCollectionMsg",
                   "org.zstack.network.service.portforwarding.APIGetPortForwardingAttachableVmNicsMsg",
                   "org.zstack.iam2.api.APIChangeIAM2ProjectStateMsg",
                   "org.zstack.header.storage.backup.APIQueryBackupStorageMsg",
                   "org.zstack.aliyun.nas.message.APIUpdateAliyunNasAccessGroupMsg",
                   "org.zstack.pciDevice.APIQueryPciDevicePciDeviceOfferingMsg",
                   "org.zstack.storage.primary.local.APILocalStorageMigrateVolumeMsg",
                   "org.zstack.header.storage.primary.APIChangePrimaryStorageStateMsg",
                   "org.zstack.ipsec.APIChangeIPSecConnectionStateMsg",
                   "org.zstack.header.vm.APIDeleteVmStaticIpMsg",
                   "org.zstack.storage.fusionstor.primary.APIRemoveMonFromFusionstorPrimaryStorageMsg",
                   "org.zstack.header.aliyun.network.vpc.APICreateEcsVSwitchRemoteMsg",
                   "org.zstack.header.configuration.APIDeleteInstanceOfferingMsg",
                   "org.zstack.header.volume.APIGetDataVolumeAttachableVmMsg",
                   "org.zstack.header.storage.database.backup.APIDeleteDatabaseBackupMsg",
                   "org.zstack.sns.platform.dingtalk.APICreateSNSDingTalkEndpointMsg",
                   "org.zstack.header.hybrid.network.vpn.APIUpdateVpcVpnConnectionRemoteMsg",
                   "org.zstack.aliyun.ebs.message.APIAddAliyunEbsBackupStorageMsg",
                   "org.zstack.header.cloudformation.APIQueryResourceStackMsg",
                   "org.zstack.header.volume.APIGetVolumeFormatMsg",
                   "org.zstack.header.aliyun.storage.snapshot.APIUpdateAliyunSnapshotMsg",
                   "org.zstack.storage.device.iscsi.APIRefreshIscsiServerMsg",
                   "org.zstack.header.network.l3.APIAddDnsToL3NetworkMsg",
                   "org.zstack.header.vm.cdrom.APIQueryVmCdRomMsg",
                   "org.zstack.iam2.api.APIDeleteIAM2ProjectTemplateMsg",
                   "org.zstack.ticket.api.APIUpdateTicketRequestMsg",
                   "org.zstack.core.config.resourceconfig.APIGetResourceBindableConfigMsg",
                   "org.zstack.header.console.APIRequestConsoleAccessMsg",
                   "org.zstack.monitoring.prometheus.APIPrometheusQueryPassThroughMsg",
                   "org.zstack.header.network.l3.APIAddHostRouteToL3NetworkMsg",
                   "org.zstack.sns.APIDeleteSNSApplicationPlatformMsg",
                   "org.zstack.vrouterRoute.APIQueryVirtualRouterVRouterRouteTableRefMsg",
                   "org.zstack.header.identity.APIQueryUserGroupMsg",
                   "org.zstack.header.hybrid.network.vpn.APIDeleteVpcVpnConnectionRemoteMsg",
                   "org.zstack.header.storage.volume.backup.APISyncBackupFromImageStoreBackupStorageMsg",
                   "org.zstack.sns.APIChangeSNSApplicationEndpointStateMsg",
                   "org.zstack.tag2.APICreateTagMsg",
                   "org.zstack.pciDevice.APIGetPciDeviceCandidatesForNewCreateVmMsg",
                   "org.zstack.header.hybrid.account.APIDetachHybridKeyMsg",
                   "org.zstack.ticket.api.APIQueryTicketHistoryMsg",
                   "org.zstack.header.vm.APISetVmStaticIpMsg",
                   "org.zstack.header.vm.APIStopVmInstanceMsg",
                   "org.zstack.header.image.APIExpungeImageMsg",
                   "org.zstack.aliyun.pangu.APIAddAliyunPanguPartitionMsg",
                   "org.zstack.header.aliyun.storage.snapshot.APIDeleteAliyunSnapshotFromLocalMsg",
                   "org.zstack.scheduler.APIChangeSchedulerStateMsg",
                   "org.zstack.header.identity.APIUpdateUserGroupMsg",
                   "org.zstack.header.aliyun.storage.snapshot.APIDeleteAliyunSnapshotFromRemoteMsg",
                   "org.zstack.storage.device.iscsi.APIQueryIscsiServerMsg",
                   "org.zstack.header.aliyun.network.connection.APIAddConnectionAccessPointFromRemoteMsg",
                   "org.zstack.header.network.l3.APIAddIpv6RangeByNetworkCidrMsg",
                   "org.zstack.core.errorcode.APIGetElaborationCategoriesMsg",
                   "org.zstack.header.identityzone.APIAddIdentityZoneFromRemoteMsg",
                   "org.zstack.network.securitygroup.APIGetCandidateVmNicForSecurityGroupMsg",
                   "org.zstack.header.storage.volume.backup.APIQueryVolumeBackupMsg",
                   "org.zstack.monitoring.APICreateMonitorTriggerMsg",
                   "org.zstack.header.image.APISyncImageSizeMsg",
                   "org.zstack.network.service.vip.APIUpdateVipMsg",
                   "org.zstack.header.tag.APIDeleteTagMsg",
                   "org.zstack.header.hybrid.network.vpn.APIDeleteVpcVpnConnectionLocalMsg",
                   "org.zstack.header.storage.volume.backup.APICreateVolumeBackupMsg",
                   "org.zstack.header.aliyun.storage.disk.APIDeleteAliyunDiskFromLocalMsg",
                   "org.zstack.header.aliyun.ecs.APIRebootEcsInstanceMsg",
                   "org.zstack.header.hybrid.backup.APIDeleteBackupFileInPublicMsg",
                   "org.zstack.header.storage.snapshot.APIQueryVolumeSnapshotTreeMsg",
                   "org.zstack.header.aliyun.network.connection.APIQueryConnectionAccessPointFromLocalMsg",
                   "org.zstack.pciDevice.APIAttachPciDeviceToVmMsg",
                   "org.zstack.header.identity.APICreateAccountMsg",
                   "org.zstack.iam2.api.APICreateIAM2VirtualIDGroupMsg",
                   "org.zstack.storage.fusionstor.primary.APIAddFusionstorPrimaryStorageMsg",
                   "org.zstack.scheduler.APIAddSchedulerJobToSchedulerTriggerMsg",
                   "org.zstack.storage.ceph.backup.APIQueryCephBackupStorageMsg",
                   "org.zstack.autoscaling.template.APIDetachAutoScalingTemplateFromGroupMsg",
                   "org.zstack.sns.APIUpdateSNSTopicMsg",
                   "org.zstack.zwatch.alarm.APIDeleteAlarmMsg",
                   "org.zstack.network.securitygroup.APIAttachSecurityGroupToL3NetworkMsg",
                   "org.zstack.autoscaling.group.APICreateAutoScalingGroupMsg",
                   "org.zstack.aliyun.nas.message.APIDeleteAliyunNasAccessGroupRuleMsg",
                   "org.zstack.network.l2.vxlan.vxlanNetwork.APIQueryL2VxlanNetworkMsg",
                   "org.zstack.header.baremetal.chassis.APIPowerResetBaremetalChassisMsg",
                   "org.zstack.header.aliyun.network.vrouter.APIDeleteAliyunRouteEntryRemoteMsg",
                   "org.zstack.header.daho.process.APIQueryDahoVllVbrRefMsg",
                   "org.zstack.header.volume.APIResizeRootVolumeMsg",
                   "org.zstack.storage.primary.sharedblock.APIQuerySharedBlockGroupPrimaryStorageMsg",
                   "org.zstack.header.identity.APIQueryQuotaMsg",
                   "org.zstack.header.baremetal.instance.APIRebootBaremetalInstanceMsg",
                   "org.zstack.header.hybrid.backup.APIBackupDatabaseToPublicCloudMsg",
                   "org.zstack.header.vm.APIGetInterdependentL3NetworksImagesMsg",
                   "org.zstack.header.vm.APICreateVmNicMsg",
                   "org.zstack.core.config.resourceconfig.APIDeleteResourceConfigMsg",
                   "org.zstack.header.apimediator.APIIsReadyToGoMsg",
                   "org.zstack.accessKey.APIQueryAccessKeyMsg",
                   "org.zstack.header.storage.database.backup.APIQueryDatabaseBackupMsg",
                   "org.zstack.header.hybrid.network.eip.APICreateHybridEipMsg",
                   "org.zstack.header.tag.APICreateUserTagMsg",
                   "org.zstack.core.config.APIResetGlobalConfigMsg",
                   "org.zstack.header.aliyun.network.connection.APIStartConnectionBetweenAliyunRouterInterfaceMsg",
                   "org.zstack.ldap.APILogInByLdapMsg",
                   "org.zstack.header.vm.APIGetVmRDPMsg",
                   "org.zstack.storage.ceph.primary.APIAddCephPrimaryStoragePoolMsg",
                   "org.zstack.monitoring.APIQueryMonitorTriggerMsg",
                   "org.zstack.header.aliyun.storage.snapshot.APICreateAliyunSnapshotRemoteMsg",
                   "org.zstack.monitoring.APIUpdateMonitorTriggerMsg",
                   "org.zstack.header.aliyun.image.APIQueryEcsImageFromLocalMsg",
                   "org.zstack.header.daho.process.APIQueryDahoCloudConnectionMsg",
                   "org.zstack.storage.device.iscsi.APIQueryIscsiLunMsg",
                   "org.zstack.header.baremetal.chassis.APIPowerOnBaremetalChassisMsg",
                   "org.zstack.license.APIUpdateLicenseMsg",
                   "org.zstack.storage.device.iscsi.APIAddIscsiServerMsg",
                   "org.zstack.vmware.APIDeleteVCenterMsg",
                   "org.zstack.header.network.l3.APIAddIpRangeByNetworkCidrMsg",
                   "org.zstack.monitoring.media.APICreateEmailMediaMsg",
                   "org.zstack.pciDevice.APIGetPciDeviceCandidatesForAttachingVmMsg",
                   "org.zstack.header.vm.APIResumeVmInstanceMsg",
                   "org.zstack.sns.platform.email.APICreateSNSEmailPlatformMsg",
                   "org.zstack.scheduler.APIGetNoTriggerSchedulerJobsMsg",
                   "org.zstack.header.network.l3.APIRemoveHostRouteFromL3NetworkMsg",
                   "org.zstack.header.vm.APIGetVmQgaMsg",
                   "org.zstack.header.host.APIUpdateHostMsg",
                   "org.zstack.header.vm.APIGetCandidatePrimaryStoragesForCreatingVmMsg",
                   "org.zstack.sns.APIQuerySNSApplicationPlatformMsg",
                   "org.zstack.network.service.lb.APIRemoveVmNicFromLoadBalancerMsg",
                   "org.zstack.header.cluster.APIQueryClusterMsg",
                   "org.zstack.kvm.APIAddKVMHostMsg",
                   "org.zstack.header.storage.backup.APICleanUpTrashOnBackupStorageMsg",
                   "org.zstack.ticket.api.APIDeleteTicketMsg",
                   "org.zstack.header.managementnode.APIQueryManagementNodeMsg",
                   "org.zstack.header.network.l2.APIGetL2NetworkTypesMsg",
                   "org.zstack.autoscaling.group.activity.APIQueryAutoScalingGroupActivityMsg",
                   "org.zstack.header.aliyun.image.APIUpdateEcsImageMsg",
                   "org.zstack.aliyun.nas.message.APIGetAliyunNasMountTargetRemoteMsg",
                   "org.zstack.zwatch.alarm.APIAddActionToAlarmMsg",
                   "org.zstack.header.vm.APIGetImageCandidatesForVmToChangeMsg",
                   "org.zstack.nas.APIDeleteNasFileSystemMsg",
                   "org.zstack.header.aliyun.network.group.APIDeleteEcsSecurityGroupRemoteMsg",
                   "org.zstack.autoscaling.group.rule.APIDeleteAutoScalingRuleMsg",
                   "org.zstack.header.cloudformation.APICreateResourceStackMsg",
                   "org.zstack.vrouterRoute.APIDeleteVRouterRouteEntryMsg",
                   "org.zstack.header.aliyun.network.connection.APIQueryAliyunRouterInterfaceFromLocalMsg",
                   "org.zstack.mevoco.APIQueryShareableVolumeVmInstanceRefMsg",
                   "org.zstack.storage.primary.local.APIQueryLocalStorageResourceRefMsg",
                   "org.zstack.header.vm.APIChangeInstanceOfferingMsg",
                   "org.zstack.core.config.APIQueryGlobalConfigMsg",
                   "org.zstack.iam2.api.APIAddAttributesToIAM2VirtualIDMsg",
                   "org.zstack.network.securitygroup.APIDetachSecurityGroupFromL3NetworkMsg",
                   "org.zstack.storage.primary.sharedblock.APIQuerySharedBlockMsg",
                   "org.zstack.v2v.APIAddV2VConversionHostMsg",
                   "org.zstack.storage.migration.primary.APIPrimaryStorageMigrateVmMsg",
                   "org.zstack.header.storage.volume.backup.APICreateRootVolumeTemplateFromVolumeBackupMsg",
                   "org.zstack.header.baremetal.instance.APIQueryBaremetalInstanceMsg",
                   "org.zstack.header.identity.APIDeleteAccountMsg",
                   "org.zstack.iam2.api.APILoginIAM2ProjectMsg",
                   "org.zstack.network.service.lb.APIGetCandidateVmNicsForLoadBalancerMsg",
                   "org.zstack.ldap.APIQueryLdapServerMsg",
                   "org.zstack.storage.primary.zses.APIAddZsesPrimaryStorageMsg",
                   "org.zstack.header.storage.primary.APIQueryPrimaryStorageMsg",
                   "org.zstack.header.hybrid.network.eip.APIDetachHybridEipFromEcsMsg",
                   "org.zstack.pciDevice.APIGetHostIommuStatusMsg",
                   "org.zstack.header.network.l3.APIUpdateIpRangeMsg",
                   "org.zstack.accessKey.APICreateAccessKeyMsg",
                   "org.zstack.header.network.service.APIQueryNetworkServiceProviderMsg",
                   "org.zstack.header.vm.APIReimageVmInstanceMsg",
                   "org.zstack.header.aliyun.oss.APIGetOssBucketFileFromRemoteMsg",
                   "org.zstack.header.zone.APICreateZoneMsg",
                   "org.zstack.ipsec.APIAttachL3NetworksToIPsecConnectionMsg",
                   "org.zstack.storage.primary.sharedblock.APIGetSharedBlockCandidateMsg",
                   "org.zstack.header.network.l3.APIDeleteIpRangeMsg",
                   "org.zstack.autoscaling.group.APIDeleteAutoScalingGroupMsg",
                   "org.zstack.header.aliyun.network.connection.APIDeleteAliyunRouterInterfaceRemoteMsg",
                   "org.zstack.core.config.resourceconfig.APIQueryResourceConfigMsg",
                   "org.zstack.sns.platform.email.APIQuerySNSEmailEndpointMsg",
                   "org.zstack.header.baremetal.instance.APIUpdateBaremetalInstanceMsg",
                   "org.zstack.iam2.api.APIQueryIAM2VirtualIDAttributeMsg",
                   "org.zstack.iam2.api.APILoginIAM2VirtualIDMsg",
                   "org.zstack.header.configuration.APIChangeDiskOfferingStateMsg",
                   "org.zstack.storage.primary.sharedblock.APIAddSharedBlockGroupPrimaryStorageMsg",
                   "org.zstack.vpc.APIGetVpcVRouterDistributedRoutingConnectionsMsg",
                   "org.zstack.header.vm.APIAttachL3NetworkToVmNicMsg",
                   "org.zstack.header.identity.APIAddUserToGroupMsg",
                   "org.zstack.autoscaling.template.APIDeleteAutoScalingTemplateMsg",
                   "org.zstack.network.service.vip.APICreateVipMsg",
                   "org.zstack.network.securitygroup.APIAddVmNicToSecurityGroupMsg",
                   "org.zstack.header.baremetal.chassis.APICleanUpBaremetalChassisBondingMsg",
                   "org.zstack.header.vm.APIGetVmHostnameMsg",
                   "org.zstack.header.cluster.APIChangeClusterStateMsg",
                   "org.zstack.header.daho.process.APISyncDahoDataCenterConnectionMsg",
                   "org.zstack.vmware.APIQueryVCenterResourcePoolMsg",
                   "org.zstack.aliyunproxy.vpc.APIQueryAliyunProxyVpcMsg",
                   "org.zstack.autoscaling.group.rule.trigger.APIQueryAutoScalingRuleTriggerMsg",
                   "org.zstack.storage.backup.sftp.APIAddSftpBackupStorageMsg",
                   "org.zstack.header.aliyun.network.connection.APISyncConnectionAccessPointFromRemoteMsg",
                   "org.zstack.storage.device.fibreChannel.APIRefreshFiberChannelStorageMsg",
                   "org.zstack.header.hybrid.network.eip.APIAttachHybridEipToEcsMsg",
                   "org.zstack.header.vm.APIDetachL3NetworkFromVmMsg",
                   "org.zstack.header.network.l3.APIAddIpv6RangeMsg",
                   "org.zstack.vpc.APIGetVpcVRouterDistributedRoutingEnabledMsg",
                   "org.zstack.iam2.api.APIRemoveIAM2VirtualIDsFromGroupMsg",
                   "org.zstack.header.identity.APICreateUserGroupMsg",
                   "org.zstack.monitoring.actions.APIQueryEmailTriggerActionMsg",
                   "org.zstack.header.vm.APIGetCandidateVmForAttachingIsoMsg",
                   "org.zstack.aliyun.ebs.message.APIAddAliyunEbsPrimaryStorageMsg",
                   "org.zstack.iam2.api.APIStopAllResourcesInIAM2ProjectMsg",
                   "org.zstack.autoscaling.group.rule.trigger.APIDeleteAutoScalingRuleTriggerMsg",
                   "org.zstack.header.aliyun.network.vrouter.APIQueryAliyunRouteEntryFromLocalMsg",
                   "org.zstack.header.vm.APISetNicQosMsg",
                   "org.zstack.network.securitygroup.APIAddSecurityGroupRuleMsg",
                   "org.zstack.header.vm.APIRecoverVmInstanceMsg",
                   "org.zstack.header.aliyun.oss.APIAddOssBucketFromRemoteMsg",
                   "org.zstack.license.APIGetLicenseInfoMsg",
                   "org.zstack.header.configuration.APIDeleteDiskOfferingMsg",
                   "org.zstack.header.baremetal.chassis.APIBatchCreateBaremetalChassisMsg",
                   "org.zstack.header.aliyun.ecs.APIDeleteAllEcsInstancesFromDataCenterMsg",
                   "org.zstack.network.securitygroup.APIQueryVmNicInSecurityGroupMsg",
                   "org.zstack.header.storage.volume.backup.APIDeleteVmBackupMsg",
                   "org.zstack.header.storageDevice.APICheckScsiLunClusterStatusMsg",
                   "org.zstack.header.zone.APIGetZoneMsg",
                   "org.zstack.network.l2.vxlan.vxlanNetworkPool.APIDeleteVniRangeMsg",
                   "org.zstack.header.vm.APISetVmMonitorNumberMsg",
                   "org.zstack.aliyun.ebs.message.APIUpdateAliyunEbsPrimaryStorageMsg",
                   "org.zstack.network.service.lb.APIUpdateLoadBalancerListenerMsg",
                   "org.zstack.iam2.api.APIDeleteIAM2VirtualIDGroupMsg",
                   "org.zstack.aliyun.nas.message.APICreateAliyunNasMountTargetMsg",
                   "org.zstack.ldap.APIGetLdapEntryMsg",
                   "org.zstack.header.aliyun.ecs.APIUpdateEcsInstanceMsg",
                   "org.zstack.header.cloudformation.APIDecodeStackTemplateMsg",
                   "org.zstack.header.host.APIQueryHostMsg",
                   "org.zstack.header.storage.database.backup.APIExportDatabaseBackupFromBackupStorageMsg",
                   "org.zstack.pciDevice.APIDeletePciDeviceMsg",
                   "org.zstack.header.aliyun.network.connection.APIRecoveryVirtualBorderRouterRemoteMsg",
                   "org.zstack.storage.ceph.primary.APIAddCephPrimaryStorageMsg",
                   "org.zstack.network.service.eip.APIQueryEipMsg",
                   "org.zstack.header.identityzone.APIGetIdentityZoneFromRemoteMsg",
                   "org.zstack.header.identityzone.APIDeleteIdentityZoneInLocalMsg",
                   "org.zstack.license.APIGetLicenseAddOnsMsg",
                   "org.zstack.iam2.api.APIUpdateIAM2VirtualIDGroupAttributeMsg",
                   "org.zstack.header.cloudformation.APIGetResourceFromResourceStackMsg",
                   "org.zstack.header.aliyun.network.connection.APIQueryConnectionBetweenL3NetworkAndAliyunVSwitchMsg",
                   "org.zstack.network.service.portforwarding.APICreatePortForwardingRuleMsg",
                   "org.zstack.header.vm.APIAttachL3NetworkToVmMsg",
                   "org.zstack.header.hybrid.account.APIAddHybridKeySecretMsg",
                   "org.zstack.header.host.APICheckKVMHostConfigFileMsg",
                   "org.zstack.header.vm.APIGetNicQosMsg",
                   "org.zstack.header.identity.APIUpdateAccountMsg",
                   "org.zstack.aliyun.nas.message.APICreateAliyunNasAccessGroupRuleMsg",
                   "org.zstack.storage.fusionstor.backup.APIAddMonToFusionstorBackupStorageMsg",
                   "org.zstack.header.identity.APIQueryUserMsg",
                   "org.zstack.storage.fusionstor.primary.APIUpdateFusionstorPrimaryStorageMonMsg",
                   "org.zstack.header.volume.APIUpdateVolumeMsg",
                   "org.zstack.header.baremetal.chassis.APIInspectBaremetalChassisMsg",
                   "org.zstack.network.service.virtualrouter.APIGetAttachablePublicL3ForVRouterMsg",
                   "org.zstack.header.tag.APICreateSystemTagMsg",
                   "org.zstack.iam2.api.APIRemoveRolesFromIAM2VirtualIDGroupMsg",
                   "org.zstack.header.baremetal.preconfiguration.APIDeletePreconfigurationTemplateMsg",
                   "org.zstack.header.aliyun.network.connection.APIGetConnectionAccessPointFromRemoteMsg",
                   "org.zstack.network.service.lb.APIQueryCertificateMsg",
                   "org.zstack.header.aliyun.oss.APIDeleteOssBucketRemoteMsg"]

    iam2_ops.add_policy_statements_to_role(role_uuid, statements)
    iam2_ops.add_roles_to_iam2_virtual_id([role_uuid], vid_test_obj.get_vid().uuid)


def share_admin_resource_include_vxlan_pool(account_uuid_list, session_uuid=None):
    instance_offerings = res_ops.get_resource(res_ops.INSTANCE_OFFERING)
    for instance_offering in instance_offerings:
        acc_ops.share_resources(account_uuid_list, [instance_offering.uuid], session_uuid)
    cond1 = res_ops.gen_query_conditions('mediaType', '!=', 'ISO')
    images = res_ops.query_resource(res_ops.IMAGE, cond1)
    for image in images:
        acc_ops.share_resources(account_uuid_list, [image.uuid], session_uuid)

    l3nets = res_ops.get_resource(res_ops.L3_NETWORK)
    for l3net in l3nets:
        acc_ops.share_resources(account_uuid_list, [l3net.uuid], session_uuid)

    l2vxlan_pools = res_ops.get_resource(res_ops.L2_VXLAN_NETWORK_POOL)
    for l2vxlan_pool in l2vxlan_pools:
        acc_ops.share_resources(account_uuid_list, [l2vxlan_pool.uuid], session_uuid)

    virtual_router_offerings = res_ops.get_resource(res_ops.VR_OFFERING)
    for virtual_router_offering in virtual_router_offerings:
        acc_ops.share_resources(account_uuid_list, [virtual_router_offering.uuid], session_uuid)
    volume_offerings = res_ops.get_resource(res_ops.DISK_OFFERING)
    for volume_offering in volume_offerings:
        acc_ops.share_resources(account_uuid_list, [volume_offering.uuid], session_uuid)


def revoke_admin_resource(account_uuid_list, session_uuid=None):
    instance_offerings = res_ops.get_resource(res_ops.INSTANCE_OFFERING)
    for instance_offering in instance_offerings:
        acc_ops.revoke_resources(account_uuid_list, [instance_offering.uuid], session_uuid)
    cond2 = res_ops.gen_query_conditions('mediaType', '!=', 'ISO')
    images = res_ops.query_resource(res_ops.IMAGE, cond2)
    for image in images:
        acc_ops.revoke_resources(account_uuid_list, [image.uuid], session_uuid)
    l3nets = res_ops.get_resource(res_ops.L3_NETWORK)
    for l3net in l3nets:
        acc_ops.revoke_resources(account_uuid_list, [l3net.uuid], session_uuid)

    l2vxlan_pool_uuid = res_ops.get_resource(res_ops.L2_VXLAN_NETWORK_POOL)[0].uuid
    acc_ops.revoke_resources(account_uuid_list, [l2vxlan_pool_uuid], session_uuid)

    virtual_router_offerings = res_ops.get_resource(res_ops.VR_OFFERING)
    for virtual_router_offering in virtual_router_offerings:
        acc_ops.revoke_resources(account_uuid_list, [virtual_router_offering.uuid], session_uuid)
    volume_offerings = res_ops.get_resource(res_ops.DISK_OFFERING)
    for volume_offering in volume_offerings:
        acc_ops.revoke_resources(account_uuid_list, [volume_offering.uuid], session_uuid)

def get_image_by_bs(bs_uuid):
    cond = res_ops.gen_query_conditions('mediaType', '!=', 'ISO')
    cond = res_ops.gen_query_conditions('platform', '=', 'Linux', cond)
    cond = res_ops.gen_query_conditions('system','=','false', cond)
    images = res_ops.query_resource(res_ops.IMAGE, cond)
    for image in images:
        for bs_ref in image.backupStorageRefs:
            if bs_ref.backupStorageUuid == bs_uuid:
                return image.uuid

def create_vm(vm_creation_option=None, volume_uuids=None, root_disk_uuid=None,
              image_uuid=None, ps_uuid=None, session_uuid=None):
    if not vm_creation_option:
        instance_offering_uuid = test_lib.lib_get_instance_offering_by_name(
            os.environ.get('instanceOfferingName_s')).uuid
        cond = res_ops.gen_query_conditions('mediaType', '!=', 'ISO')
        cond = res_ops.gen_query_conditions('platform', '=', 'Linux', cond)
        cond = res_ops.gen_query_conditions('system','=','false',cond)
        l3net_uuid = test_lib.lib_get_l3_by_name(
            os.environ.get('l3VlanNetworkName3')).uuid
	if image_uuid:
	    image_uuid = image_uuid
	else:
            image_uuid = res_ops.query_resource(
            res_ops.IMAGE, cond, session_uuid)[0].uuid
        vm_creation_option = test_util.VmOption()
        vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
        vm_creation_option.set_image_uuid(image_uuid)
        vm_creation_option.set_l3_uuids([l3net_uuid])
        vm_creation_option.set_timeout(864000000)

    if volume_uuids:
        if isinstance(volume_uuids, list):
            vm_creation_option.set_data_disk_uuids(volume_uuids)
        else:
            test_util.test_fail(
                'volume_uuids type: %s is not "list".' % type(volume_uuids))

    if root_disk_uuid:
        vm_creation_option.set_root_disk_uuid(root_disk_uuid)

    if image_uuid:
        vm_creation_option.set_image_uuid(image_uuid)

    if ps_uuid:
        vm_creation_option.set_ps_uuid(ps_uuid)

    if session_uuid:
        vm_creation_option.set_session_uuid(session_uuid)

    vm = test_vm.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    return vm

def create_vr_vm(test_obj_dict,l3_uuid, session_uuid = None):
    '''
    '''
    vrs = test_lib.lib_find_vr_by_l3_uuid(l3_uuid)
    if not vrs:
        #create temp_vm1 for getting vlan1's vr for test pf_vm portforwarding
        instance_offering_uuid = test_lib.lib_get_instance_offering_by_name(
            os.environ.get('instanceOfferingName_s')).uuid
        cond = res_ops.gen_query_conditions('mediaType', '!=', 'ISO')
        cond = res_ops.gen_query_conditions('platform', '=', 'Linux', cond)
        cond = res_ops.gen_query_conditions('system','=','false',cond)
        image_uuid = res_ops.query_resource(res_ops.IMAGE, cond, session_uuid=session_uuid)[0].uuid

        vm_creation_option = test_util.VmOption()
        vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
        vm_creation_option.set_image_uuid(image_uuid)
        vm_creation_option.set_l3_uuids([l3_uuid])
        temp_vm = create_vm(vm_creation_option,session_uuid=session_uuid)
        test_obj_dict.add_vm(temp_vm)
        vr = test_lib.lib_find_vr_by_vm(temp_vm.vm)[0]
        temp_vm.destroy(session_uuid)
        test_obj_dict.rm_vm(temp_vm)
    else:
        vr = vrs[0]
        if not test_lib.lib_is_vm_running(vr):
            test_lib.lib_robot_cleanup(test_obj_dict)
            test_util.test_skip('vr: %s is not running. Will skip test.' % vr.uuid)
    return vr

def create_windows_vm(vm_creation_option=None, volume_uuids=None, root_disk_uuid=None, image_uuid=None, session_uuid=None):
    if not vm_creation_option:
        instance_offering_uuid = test_lib.lib_get_instance_offering_by_name(
            os.environ.get('instanceOfferingName_win')).uuid
        cond = res_ops.gen_query_conditions('mediaType', '!=', 'ISO')
        cond = res_ops.gen_query_conditions('platform', '=', 'Windows', cond)
        image_uuid = res_ops.query_resource(
            res_ops.IMAGE, cond, session_uuid)[0].uuid
        l3net_uuid = test_lib.lib_get_l3_by_name(
            os.environ.get('l3VlanNetworkName3')).uuid
        vm_creation_option = test_util.VmOption()
        vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
        vm_creation_option.set_image_uuid(image_uuid)
        vm_creation_option.set_l3_uuids([l3net_uuid])
    return create_vm(vm_creation_option, volume_uuids, root_disk_uuid, image_uuid, session_uuid)

def create_volume(volume_creation_option=None, session_uuid=None):
    if not volume_creation_option:
        disk_offering = test_lib.lib_get_disk_offering_by_name(
            os.environ.get('smallDiskOfferingName'))
        volume_creation_option = test_util.VolumeOption()
        volume_creation_option.set_disk_offering_uuid(disk_offering.uuid)
        volume_creation_option.set_name('test_volume')

    if session_uuid:
        volume_creation_option.set_session_uuid(session_uuid)

    volume = zstack_volume_header.ZstackTestVolume()
    volume.set_creation_option(volume_creation_option)
    volume.create()
    return volume


def create_vm_with_volume(vm_creation_option=None, data_volume_uuids=None,
                          session_uuid=None):
    if not data_volume_uuids:
        disk_offering = test_lib.lib_get_disk_offering_by_name(
            os.environ.get('smallDiskOfferingName'), session_uuid)
        data_volume_uuids = [disk_offering.uuid]
    return create_vm(vm_creation_option, data_volume_uuids,
                     session_uuid=session_uuid)


def create_vm_with_iso(vm_creation_option=None, session_uuid=None):
    img_option = test_util.ImageOption()
    img_option.set_name('iso')
    root_disk_uuid = test_lib.lib_get_disk_offering_by_name(
        os.environ.get('rootDiskOfferingName')).uuid
    bs_uuid = res_ops.query_resource_fields(res_ops.BACKUP_STORAGE, [],
                                            session_uuid)[0].uuid
    img_option.set_backup_storage_uuid_list([bs_uuid])
    if os.path.exists("%s/apache-tomcat/webapps/zstack/static/zstack-repo/" % (os.environ.get('zstackInstallPath'))):
        os.system("genisoimage -o %s/apache-tomcat/webapps/zstack/static/zstack-repo/7/x86_64/os/test.iso /tmp/" % (os.environ.get('zstackInstallPath')))
        img_option.set_url('http://%s:8080/zstack/static/zstack-repo/7/x86_64/os/test.iso' % (os.environ.get('node1Ip')))
    else:
        os.system("genisoimage -o %s/apache-tomcat/webapps/zstack/static/test.iso /tmp/" % (os.environ.get('zstackInstallPath')))
        img_option.set_url('http://%s:8080/zstack/static/test.iso' % (os.environ.get('node1Ip')))

    image_uuid = img_ops.add_iso_template(img_option).uuid

    return create_vm(vm_creation_option, None, root_disk_uuid, image_uuid,
                     session_uuid=session_uuid)


def create_vm_with_previous_iso(vm_creation_option=None, session_uuid=None):
    cond = res_ops.gen_query_conditions('name', '=', 'iso')
    image_uuid = res_ops.query_resource(res_ops.IMAGE, cond)[0].uuid
    root_disk_uuid = test_lib.lib_get_disk_offering_by_name(
        os.environ.get('rootDiskOfferingName')).uuid
    return create_vm(vm_creation_option, None, root_disk_uuid, image_uuid,
                     session_uuid=session_uuid)

def create_zone(name=None,description=None,session_uuid=None):
    zone_create_option = test_util.ZoneOption()
    zone_create_option.set_name('new_test_zone')
    zone_create_option.set_description('a new zone for deleted test')
    if name:
        zone_create_option.set_name(name)
    if description:
        zone_create_option.set_description(description)
    zone_inv = zone_ops.create_zone(zone_create_option,session_uuid)
    return zone_inv

def create_vm_ticket(virtual_id_uuid , project_uuid , session_uuid , name=None , request_name=None ,execute_times=None,instance_offering_uuid=None , image_uuid = None, l3_network_uuid=None ):
    if not instance_offering_uuid:
        conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
        instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid
    if not image_uuid:
        image_name = os.environ.get('imageName_s')
        image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    if not l3_network_uuid:
        l3_name = os.environ.get('l3VlanNetworkName1')
        l3_network_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    api_body = {"name": "vm", "instanceOfferingUuid": instance_offering_uuid, "imageUuid": image_uuid,
                "l3NetworkUuids": [l3_network_uuid]}
    api_name = 'org.zstack.header.vm.APICreateVmInstanceMsg'
    if not execute_times:
        execute_times = 1
    if not name:
        name = 'ticket_for_test'
    if not request_name:
        request_name = 'create-vm-ticket'
    account_system_type = 'iam2'
    ticket = ticket_ops.create_ticket(name, request_name, api_body, api_name, execute_times, account_system_type,virtual_id_uuid, project_uuid, session_uuid=session_uuid)
    return ticket

def share_admin_resource(account_uuid_list):
    instance_offerings = res_ops.get_resource(res_ops.INSTANCE_OFFERING)
    for instance_offering in instance_offerings:
        acc_ops.share_resources(account_uuid_list, [instance_offering.uuid])
    cond = res_ops.gen_query_conditions('mediaType', '!=', 'ISO')
    images = res_ops.query_resource(res_ops.IMAGE, cond)
    for image in images:
        acc_ops.share_resources(account_uuid_list, [image.uuid])
    l3net_uuid = res_ops.get_resource(res_ops.L3_NETWORK)[0].uuid
    root_disk_uuid = test_lib.lib_get_disk_offering_by_name(
        os.environ.get('rootDiskOfferingName')).uuid
    data_disk_uuid = test_lib.lib_get_disk_offering_by_name(
        os.environ.get('smallDiskOfferingName')).uuid
    acc_ops.share_resources(
        account_uuid_list, [l3net_uuid, root_disk_uuid, data_disk_uuid])

def check_resource_not_exist(uuid,resource_type):
    conditions = res_ops.gen_query_conditions('uuid', '=', uuid)
    resource_inv = res_ops.query_resource(resource_type,conditions)
    if resource_inv:
        test_util.test_fail("resource [%s] is still exist,uuid [%s]"%(resource_type,uuid))


def check_libvirt_host_uuid():
    libvirt_dir = "/etc/libvirt/libvirtd.conf"
    p = re.compile(r'^host_uuid')
    with open(libvirt_dir, 'r') as a:
        lines = a.readlines()
        for line in lines:
            if re.match(p, line):
                return True
    return False

def create_spice_vm(vm_creation_option=None, volume_uuids=None, root_disk_uuid=None,
              image_uuid=None,system_tag="vmConsoleMode::spice", session_uuid=None):
    if not vm_creation_option:
        instance_offering_uuid = test_lib.lib_get_instance_offering_by_name(
            os.environ.get('instanceOfferingName_s')).uuid
        cond = res_ops.gen_query_conditions('mediaType', '!=', 'ISO')
        cond = res_ops.gen_query_conditions('platform', '=', 'Linux', cond)
        image_uuid = res_ops.query_resource(
            res_ops.IMAGE, cond, session_uuid)[0].uuid
        l3net_uuid = res_ops.get_resource(
            res_ops.L3_NETWORK, session_uuid)[0].uuid
        vm_creation_option = test_util.VmOption()
        vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
        vm_creation_option.set_image_uuid(image_uuid)
        vm_creation_option.set_l3_uuids([l3net_uuid])
        vm_creation_option.set_system_tags([system_tag])

    if volume_uuids:
        if isinstance(volume_uuids, list):
            vm_creation_option.set_data_disk_uuids(volume_uuids)
        else:
            test_util.test_fail(
                'volume_uuids type: %s is not "list".' % type(volume_uuids))

    if root_disk_uuid:
        vm_creation_option.set_root_disk_uuid(root_disk_uuid)

    if image_uuid:
        vm_creation_option.set_image_uuid(image_uuid)

    if session_uuid:
        vm_creation_option.set_session_uuid(session_uuid)

    vm = test_vm.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    return vm

def get_vm_console_protocol(uuid, session_uuid=None):
    action = api_actions.GetVmConsoleAddressAction()
    action.timeout = 30000
    action.uuid = uuid
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    test_util.action_logger('Get VM Console protocol:  %s ' % evt.protocol)
    return evt

def create_vnc_vm(vm_creation_option=None, volume_uuids=None, root_disk_uuid=None,
              image_uuid=None,system_tag="vmConsoleMode::vnc", session_uuid=None):
    if not vm_creation_option:
        instance_offering_uuid = test_lib.lib_get_instance_offering_by_name(
            os.environ.get('instanceOfferingName_s')).uuid
        cond = res_ops.gen_query_conditions('mediaType', '!=', 'ISO')
        cond = res_ops.gen_query_conditions('platform', '=', 'Linux', cond)
        image_uuid = res_ops.query_resource(
            res_ops.IMAGE, cond, session_uuid)[0].uuid
        l3net_uuid = res_ops.get_resource(
            res_ops.L3_NETWORK, session_uuid)[0].uuid
        vm_creation_option = test_util.VmOption()
        vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
        vm_creation_option.set_image_uuid(image_uuid)
        vm_creation_option.set_l3_uuids([l3net_uuid])
        vm_creation_option.set_system_tags([system_tag])

    if volume_uuids:
        if isinstance(volume_uuids, list):
            vm_creation_option.set_data_disk_uuids(volume_uuids)
        else:
            test_util.test_fail(
                'volume_uuids type: %s is not "list".' % type(volume_uuids))

    if root_disk_uuid:
        vm_creation_option.set_root_disk_uuid(root_disk_uuid)

    if image_uuid:
        vm_creation_option.set_image_uuid(image_uuid)

    if session_uuid:
        vm_creation_option.set_session_uuid(session_uuid)

    vm = test_vm.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    return vm

def create_ag_vm(vm_creation_option=None, volume_uuids=None, root_disk_uuid=None,
              image_uuid=None, affinitygroup_uuid=None, host_uuid=None, session_uuid=None):
    if not vm_creation_option:
        instance_offering_uuid = test_lib.lib_get_instance_offering_by_name(
            os.environ.get('instanceOfferingName_s')).uuid
        cond = res_ops.gen_query_conditions('mediaType', '!=', 'ISO')
        cond = res_ops.gen_query_conditions('platform', '=', 'Linux', cond)
        cond = res_ops.gen_query_conditions('system', '=', 'false', cond)
        image_uuid = res_ops.query_resource(
            res_ops.IMAGE, cond, session_uuid)[0].uuid
        cond = res_ops.gen_query_conditions('category', '!=', 'System')
        l3net_uuid = res_ops.query_resource(
            res_ops.L3_NETWORK, cond, session_uuid)[0].uuid
        vm_creation_option = test_util.VmOption()
        vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
        vm_creation_option.set_image_uuid(image_uuid)
        vm_creation_option.set_l3_uuids([l3net_uuid])
        vm_creation_option.set_host_uuid(host_uuid)

    if affinitygroup_uuid:
        vm_creation_option.set_system_tags(["affinityGroupUuid::%s" % affinitygroup_uuid])

    if volume_uuids:
        if isinstance(volume_uuids, list):
            vm_creation_option.set_data_disk_uuids(volume_uuids)
        else:
            test_util.test_fail(
                'volume_uuids type: %s is not "list".' % type(volume_uuids))

    if root_disk_uuid:
        vm_creation_option.set_root_disk_uuid(root_disk_uuid)

    if image_uuid:
        vm_creation_option.set_image_uuid(image_uuid)

    if session_uuid:
        vm_creation_option.set_session_uuid(session_uuid)

    vm = test_vm.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    return vm


def create_data_volume_template_from_volume(volume_uuid, backup_storage_uuid_list, name = None, session_uuid = None ):
    volume_temp = vol_ops.create_volume_template(volume_uuid, backup_storage_uuid_list, name, session_uuid)
    return volume_temp

def create_data_volume_from_template(image_uuid, ps_uuid, name = None, host_uuid = None ):
    vol = vol_ops.create_volume_from_template(image_uuid, ps_uuid, name, host_uuid)
    return vol

def export_image_from_backup_storage(image_uuid, bs_uuid, session_uuid = None):
    imageurl = img_ops.export_image_from_backup_storage(image_uuid, bs_uuid, session_uuid)
    return imageurl

def delete_volume_image(image_uuid):
    img_ops.delete_image(image_uuid)

def get_local_storage_volume_migratable_hosts(volume_uuid):
    hosts = vol_ops.get_volume_migratable_host(volume_uuid)
    return hosts

def migrate_local_storage_volume(volume_uuid, host_uuid):
    vol_ops.migrate_volume(volume_uuid, host_uuid)

def delete_volume(volume_uuid):
    evt = vol_ops.delete_volume(volume_uuid)
    return evt

def expunge_volume(volume_uuid):
    evt = vol_ops.expunge_volume(volume_uuid)
    return evt

def recover_volume(volume_uuid):
    evt = vol_ops.recover_volume(volume_uuid)
    return evt

def expunge_image(image_uuid):
    evt = img_ops.expunge_image(image_uuid)
    return evt

def create_vip(vip_name=None, l3_uuid=None, session_uuid = None, required_ip=None):
    if not vip_name:
        vip_name = 'test vip'
    if not l3_uuid:
        l3_name = os.environ.get('l3PublicNetworkName')
        l3_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid

    vip_creation_option = test_util.VipOption()
    vip_creation_option.set_name(vip_name)
    vip_creation_option.set_l3_uuid(l3_uuid)
    vip_creation_option.set_session_uuid(session_uuid)
    vip_creation_option.set_requiredIp(required_ip)

    vip = zstack_vip_header.ZstackTestVip()
    vip.set_creation_option(vip_creation_option)
    vip.create()
    return vip

def create_eip(vip_uuid,eip_name=None,vnic_uuid=None, vm_obj=None, \
        session_uuid = None):

    eip_option = test_util.EipOption()
    eip_option.set_name(eip_name)
    eip_option.set_vip_uuid(vip_uuid)
    eip_option.set_vm_nic_uuid(vnic_uuid)
    eip_option.set_session_uuid(session_uuid)
    eip = zstack_eip_header.ZstackTestEip()
    eip.set_creation_option(eip_option)
    if vnic_uuid and not vm_obj:
        test_util.test_fail('vm_obj can not be None in create_eip() API, when setting vm_nic_uuid.')
    eip.create(vm_obj)
    return eip


def delete_vip(vip_uuid, session_uuid = None):
    action = api_actions.DeleteVipAction()
    action.timeout = 30000
    action.uuid = vip_uuid
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    test_util.action_logger('Delete Vip:  %s ' % vip_uuid)
    return evt 

def create_vpc_vrouter(vr_name='test_vpc'):
    conf = res_ops.gen_query_conditions('name', '=', 'test_vpc')
    vr_list = res_ops.query_resource(res_ops.APPLIANCE_VM, conf)
    if vr_list:
        return ZstackTestVR(vr_list[0])
    vr_offering = res_ops.get_resource(res_ops.VR_OFFERING)[0]
    vr_inv =  vpc_ops.create_vpc_vrouter(name=vr_name, virtualrouter_offering_uuid=vr_offering.uuid)
    return ZstackTestVR(vr_inv)

def query_vpc_vrouter(vr_name):
    conf = res_ops.gen_query_conditions('name', '=', vr_name)
    vr_list = res_ops.query_resource(res_ops.APPLIANCE_VM, conf)
    if vr_list:
        return ZstackTestVR(vr_list[0])

def attach_l3_to_vpc_vr(vpc_vr, l3_list):
    for l3 in l3_list:
        vpc_vr.add_nic(l3.uuid)

def attach_l3_to_vpc_vr_by_uuid(vpc_vr, l3_uuid):
    vpc_vr.add_nic(l3_uuid)

class ZstackTestVR(vm_header.TestVm):
    def __init__(self, vr_inv):
        super(ZstackTestVR, self).__init__()
        self._inv = vr_inv

    def __hash__(self):
        return hash(self.inv.uuid)

    def __eq__(self, other):
        return self.inv.uuid == other.inv.uuid

    @property
    def inv(self):
        return self._inv

    @inv.setter
    def inv(self, value):
        self._inv = value

    def destroy(self, session_uuid = None):
        vm_ops.destroy_vm(self.inv.uuid, session_uuid)
        super(ZstackTestVR, self).destroy()

    def reboot(self, session_uuid = None):
        self.inv = vm_ops.reboot_vm(self.inv.uuid, session_uuid)
        super(ZstackTestVR, self).reboot()

    def reconnect(self, session_uuid = None):
        self.inv = vm_ops.reconnect_vr(self.inv.uuid, session_uuid)

    def migrate(self, host_uuid, timeout = None, session_uuid = None):
        self.inv = vm_ops.migrate_vm(self.inv.uuid, host_uuid, timeout, session_uuid)
        super(ZstackTestVR, self).migrate(host_uuid)

    def migrate_to_random_host(self, timeout = None, session_uuid = None):
        host_uuid = random.choice([host.uuid for host in res_ops.get_resource(res_ops.HOST)
                                                      if host.uuid != test_lib.lib_find_host_by_vm(self.inv).uuid])
        self.inv = vm_ops.migrate_vm(self.inv.uuid, host_uuid, timeout, session_uuid)
        super(ZstackTestVR, self).migrate(host_uuid)

    def update(self):
        '''
        If vm's status was changed by none vm operations, it needs to call
        vm.update() to update vm's infromation.

        The none vm operations: host.maintain() host.delete(), zone.delete()
        cluster.delete()
        '''
        super(ZstackTestVR, self).update()
        if self.get_state != vm_header.EXPUNGED:
            update_inv = test_lib.lib_get_vm_by_uuid(self.inv.uuid)
            if update_inv:
                self.inv = update_inv
                #vm state need to chenage to stopped, if host is deleted
                host = test_lib.lib_find_host_by_vm(update_inv)
                if not host and self.inv.state != vm_header.STOPPED:
                    self.set_state(vm_header.STOPPED)
            else:
                self.set_state(vm_header.EXPUNGED)
            return self.inv

    def add_nic(self, l3_uuid):
        '''
        Add a new NIC device to VM. The NIC device will connect with l3_uuid.
        '''
        self.inv = net_ops.attach_l3(l3_uuid, self.inv.uuid)

    def remove_nic(self, nic_uuid):
        '''
        Detach a NIC from VM.
        '''
        self.inv = net_ops.detach_l3(nic_uuid)


def sleep_util(timestamp):
   while True:
      if time.time() >= timestamp:
         break
      time.sleep(0.5)


class MulISO(object):
    def __init__(self):
        self.vm1 = None
        self.vm2 = None
        self.iso_uuids = None
        self.iso = [{'name': 'iso1', 'url': 'http://zstack.yyk.net/iso/iso1.iso'},
                    {'name': 'iso2', 'url': 'http://zstack.yyk.net/iso/iso2.iso'},
                    {'name': 'iso3', 'url': 'http://zstack.yyk.net/iso/iso3.iso'}]

    def add_iso_image(self):
        bs_uuid = res_ops.query_resource(res_ops.BACKUP_STORAGE)[0].uuid
        images = res_ops.query_resource(res_ops.IMAGE)
        image_names = [i.name for i in  images]
        if self.iso[-1]['name'] not in image_names:
            for iso in self.iso:
                img_option = test_util.ImageOption()
                img_option.set_name(iso['name'])
                img_option.set_backup_storage_uuid_list([bs_uuid])
                testIsoUrl = iso['url']
                img_option.set_url(testIsoUrl)
                image_inv = img_ops.add_iso_template(img_option)
                image = test_image.ZstackTestImage()
                image.set_image(image_inv)
                image.set_creation_option(img_option)

    def get_all_iso_uuids(self):
        cond = res_ops.gen_query_conditions('mediaType', '=', 'ISO')
        iso_images = res_ops.query_resource(res_ops.IMAGE, cond)
        self.iso_uuids = [i.uuid for i in iso_images]
        self.iso_names = [i.name for i in iso_images]

    def check_iso_candidate(self, iso_name, vm_uuid=None, is_candidate=False):
        if not vm_uuid:
            vm_uuid = self.vm1.vm.uuid
        iso_cand = vm_ops.get_candidate_iso_for_attaching(vm_uuid)
        cand_name_list = [i.name for i in iso_cand]
        if is_candidate:
            assert iso_name in cand_name_list
        else:
            assert iso_name not in cand_name_list

    def create_vm(self, vm2=False):
        self.vm1 = create_vm()
        if vm2:
            self.vm2 = create_vm()

    def attach_iso(self, iso_uuid, vm_uuid=None):
        if not vm_uuid:
            vm_uuid = self.vm1.vm.uuid
        img_ops.attach_iso(iso_uuid, vm_uuid)
        self.check_vm_systag(iso_uuid, vm_uuid)

    def detach_iso(self, iso_uuid, vm_uuid=None):
        if not vm_uuid:
            vm_uuid = self.vm1.vm.uuid
        img_ops.detach_iso(vm_uuid, iso_uuid)
        self.check_vm_systag(iso_uuid, vm_uuid, tach='detach')

    def set_iso_first(self, iso_uuid, vm_uuid=None):
        if not vm_uuid:
            vm_uuid = self.vm1.vm.uuid
        system_tags = ['iso::%s::0' % iso_uuid]
        vm_ops.update_vm(vm_uuid, system_tags=system_tags)

    def check_vm_systag(self, iso_uuid, vm_uuid=None, tach='attach', order=None):
        if not vm_uuid:
            vm_uuid = self.vm1.vm.uuid
        cond = res_ops.gen_query_conditions('resourceUuid', '=', vm_uuid)
        systags = res_ops.query_resource(res_ops.SYSTEM_TAG, cond)
        iso_orders = {t.tag.split('::')[-2]: t.tag.split('::')[-1] for t in systags if 'iso' in t.tag}
        if tach == 'attach':
            assert iso_uuid in iso_orders
        else:
            assert iso_uuid not in iso_orders
        if order:
            assert iso_orders[iso_uuid] == order

class Longjob(object):
    def __init__(self):
        self.vm = None
        self.image_name_net = os.getenv('imageName_net')
        self.url = os.getenv('imageUrl_net')
        self.add_image_job_name = 'APIAddImageMsg'
        self.crt_vm_image_job_name = 'APICreateRootVolumeTemplateFromRootVolumeMsg'
        self.crt_vol_image_job_name = 'APICreateDataVolumeTemplateFromVolumeMsg'
        self.vm_create_image_name = 'test-vm-crt-image'
        self.vol_create_image_name = 'test-vol-crt-image'
        self.image_add_name = 'test-image-longjob'
        self.cond_name = "res_ops.gen_query_conditions('name', '=', 'name_to_replace')"

    def create_vm(self):
        self.vm = create_vm()

    def create_data_volume(self):
        disk_offering = test_lib.lib_get_disk_offering_by_name(os.getenv('rootDiskOfferingName'))
        ps_uuid = self.vm.vm.allVolumes[0].primaryStorageUuid
        volume_option = test_util.VolumeOption()
        volume_option.set_disk_offering_uuid(disk_offering.uuid)
        volume_option.set_name('data-volume-for-crt-image-test')
#         volume_option.set_primary_storage_uuid(ps_uuid)
        self.data_volume = create_volume(volume_option)
        self.set_ceph_mon_env(ps_uuid)
        self.data_volume.attach(self.vm)
        self.data_volume.check()

    def set_ceph_mon_env(self, ps_uuid):
        cond_vol = res_ops.gen_query_conditions('uuid', '=', ps_uuid)
        ps = res_ops.query_resource(res_ops.PRIMARY_STORAGE, cond_vol)[0]
        if ps.type.lower() == 'ceph':
            ps_mon_ip = ps.mons[0].monAddr
            os.environ['cephBackupStorageMonUrls'] = 'root:password@%s' % ps_mon_ip

    def submit_longjob(self, job_data, name, job_type=None):
        if job_type == 'image':
            _job_name = self.add_image_job_name
        elif job_type == 'crt_vm_image':
            _job_name = self.crt_vm_image_job_name
        elif job_type == 'crt_vol_image':
            _job_name = self.crt_vol_image_job_name
        long_job = longjob_ops.submit_longjob(_job_name, job_data, name)
        assert long_job.state == "Running"
        time.sleep(5)
        cond_longjob = res_ops.gen_query_conditions('apiId', '=', long_job.apiId)
        longjob = res_ops.query_resource(res_ops.LONGJOB, cond_longjob)[0]
        assert longjob.state == "Succeeded"
        assert longjob.jobResult == "Succeeded"
        job_data_name = job_data.split('"')[3]
        image_inv = res_ops.query_resource(res_ops.IMAGE, eval(self.cond_name.replace('name_to_replace', job_data_name)))
        assert image_inv
        assert image_inv[0].status == 'Ready'
        if job_type == 'crt_vol_image':
            assert image_inv[0].mediaType == 'DataVolumeTemplate'
        else:
            assert image_inv[0].mediaType == 'RootVolumeTemplate'

    def add_image(self):
        name = "longjob_image"
        bs = res_ops.query_resource(res_ops.BACKUP_STORAGE)
        self.target_bs = bs[random.randint(0, len(bs) - 1)]
        job_data = '{"name":"%s", "url":"%s", "mediaType"="RootVolumeTemplate", "format"="qcow2", "platform"="Linux", \
        "backupStorageUuids"=["%s"]}' % (self.image_add_name, self.url, self.target_bs.uuid)
        self.submit_longjob(job_data, name, job_type='image')

    def delete_image(self):
        cond_image = res_ops.gen_query_conditions('name', '=', 'test-image-longjob')
        longjob_image = res_ops.query_resource(res_ops.IMAGE, cond_image)[0]
        try:
            img_ops.delete_image(longjob_image.uuid, backup_storage_uuid_list=[self.target_bs.uuid])
        except:
            pass

    def crt_vm_image(self):
        name = 'longjob_crt_vol_image'
        job_data = '{"name"="%s", "guestOsType":"Linux","system"="false","platform"="Linux","backupStorageUuids"=["%s"], \
        "rootVolumeUuid"="%s"}' % (self.vm_create_image_name, res_ops.query_resource(res_ops.BACKUP_STORAGE)[-1].uuid, self.vm.vm.rootVolumeUuid)
        self.submit_longjob(job_data, name, job_type='crt_vm_image')

    def crt_vol_image(self):
        name = 'longjob_crt_vol_image'
        job_data = '{"name"="%s", "guestOsType":"Linux","system"="false","platform"="Linux","backupStorageUuids"=["%s"], \
        "volumeUuid"="%s"}' %(self.vol_create_image_name, res_ops.query_resource(res_ops.BACKUP_STORAGE)[0].uuid, self.data_volume.get_volume().uuid)
        self.submit_longjob(job_data, name, job_type='crt_vol_image')


class Billing(object):
	def __init__(self):
		self.resourceName = None
		self.timeUnit = "s"
		self.price = 5
	
	def set_resourceName(self,resourceName):
		self.resourceName = resourceName

	def get_resourceName(self):
		return self.resourceName

	def set_price(self,price):
		self.price = price

	def get_price(self):
		return self.price

	def set_timeUnit(self,timeUnit):
		self.timeUnit = timeUnit

	def get_timeUnit(self):
		return self.timeUnit

	def get_price_total(self):
		cond = res_ops.gen_query_conditions('name', '=',  'admin')
		admin_uuid = res_ops.query_resource_fields(res_ops.ACCOUNT, cond)[0].uuid
		prices = bill_ops.calculate_account_spending(admin_uuid)
		return 	prices

class CpuBilling(Billing):
	def __init__(self):
		super(CpuBilling, self).__init__()
		self.resourceName = "cpu"
		self.uuid = None

	def get_uuid(self):
		return self.uuid
	
        def create_resource_type(self):
                evt = bill_ops.create_resource_price(self.resourceName,self.timeUnit,self.price)
                self.uuid = evt.uuid
                return evt

	def delete_resource(self):
		return bill_ops.delete_resource_price(self.uuid)
	
	def compare(self,status):
		prices = super(CpuBilling, self).get_price_total()
		time.sleep(1)
		prices1 = super(CpuBilling, self).get_price_total()
		if status == "migration" or status == "recover":
			if prices1.total <= prices.total:
				test_util.test_fail("test billing fail,maybe can not calculate when vm %s"\
						 %(status))
		else:
			if prices1.total != prices.total:
				test_util.test_fail("test billing fail,maybe can not calculate when vm %s"\
						%(status))

class MemoryBilling(Billing):
	def __init__(self):
		super(MemoryBilling, self).__init__()
		self.resourceName = "memory"
		self.resourceUnit = "G"
		self.uuid = None
	
	def set_resourceUnit(self,resourceUnit):
		self.resourceUnit = resourceUnit

	def get_resourceUnit(self):
		return self.resourceUnit
	
	def get_uuid(self):
		return self.uuid

	def create_resource_type(self):
		evt = bill_ops.create_resource_price(self.resourceName,self.timeUnit,self.price,self.resourceUnit)
		self.uuid = evt.uuid
		return evt
	
	def delete_resource(self):
		return bill_ops.delete_resource_price(self.uuid)

        def compare(self,status):
		prices = super(MemoryBilling, self).get_price_total()
		time.sleep(1)
		prices1 = super(MemoryBilling, self).get_price_total()
		if status == "migration" or status == "recover":
			if prices1.total <= prices.total:
				test_util.test_fail("test billing fail,maybe can not calculate when vm %s"\
					%(status))
		else:
			if prices1.total != prices.total:
				test_util.test_fail("test billing fail,maybe can not calculate when vm %s"\
					%(status))

class RootVolumeBilling(Billing):
	def __init__(self):
		super(RootVolumeBilling, self).__init__()
		self.resourceName = "rootVolume"
		self.resourceUnit = "G"
		self.uuid = None
	
        def set_resourceUnit(self,resourceUnit):
                self.resourceUnit = resourceUnit

        def get_resourceUnit(self):
                return self.resourceUnit

	def create_resource_type(self):
		return bill_ops.create_resource_price(self.resourceName,self.timeUnit,self.price,self.resourceUnit)

        def get_uuid(self):
                return self.uuid

        def create_resource_type(self):
                evt = bill_ops.create_resource_price(self.resourceName,self.timeUnit,self.price,self.resourceUnit)
                self.uuid = evt.uuid
                return evt

	def delete_resource(self):
		return bill_ops.delete_resource_price(self.uuid)

	def compare(self,status):
		prices = super(RootVolumeBilling, self).get_price_total()
		time.sleep(1)
		prices1 = super(RootVolumeBilling, self).get_price_total()
		if status == "clean":
			if prices1.total != prices.total:
				test_util.test_fail("test billing fail,maybe can not calculate when vm %s" \
					%(status))
		else:
			if prices1.total <= prices.total:
				test_util.test_fail("test billing fail,maybe can not calculate when vm %s"\
					%(status))

class DataVolumeBilling(Billing):
        def __init__(self):
                super(DataVolumeBilling, self).__init__()
                self.resourceName = "dataVolume"
                self.resourceUnit = "G"
		self.uuid = None
		self.volume = None
		self.disk = None

        def set_resourceUnit(self,resourceUnit):
                self.resourceUnit = resourceUnit

        def get_resourceUnit(self):
                return self.resourceUnit

	def create_resource_type(self):
		evt = bill_ops.create_resource_price(self.resourceName,self.timeUnit,self.price,self.resourceUnit)
		self.uuid = evt.uuid
		return evt

	def delete_resource(self):
		return bill_ops.delete_resource_price(self.uuid)

	def compare(self,status):
		prices = super(DataVolumeBilling, self).get_price_total()
                time.sleep(1)
                prices1 = super(DataVolumeBilling, self).get_price_total()
                if status == "volume_clean":
                        if prices1.total != prices.total:
                                test_util.test_fail("test billing fail,maybe can not calculate when vm %s" \
                                        %(status))
                else:
                        if prices1.total <= prices.total:
                                test_util.test_fail("test billing fail,maybe can not calculate when vm %s"\
                                        %(status))
	
	def create_volume_and_attach_vmm(self,disk_offering_uuid,volume_name,vm_instance):
		volume = test_volume.ZstackTestVolume()
		volume.volume_creation_option.set_disk_offering_uuid(disk_offering_uuid)
		volume.volume_creation_option.set_name(volume_name)
		volume.create()
		time.sleep(1)
		volume.attach(vm_instance)
		self.volume = volume
		return volume.volume
	
	def create_disk_offer(self,diskSize,disk_name):
		disk_offer = test_util.DiskOfferingOption()
		disk_offer.set_diskSize(diskSize)
		disk_offer.set_name(disk_name)
		self.disk = disk_offer		
		return vol_ops.create_volume_offering(disk_offer)
		
class PublicIpBilling(Billing):
	def __init__(self):
		super(PublicIpBilling, self).__init__()
		self.resourceName = "pubIpVmNicBandwidthIn"
		self.resourceUnit = "M"
		self.uuid = None
	
	def set_resourceUnit(self,resourceUnit):
		self.resourceUnit = resourceUnit

	def get_resourceUnit(self):
		return self.resourceUnit

        def create_resource_type(self):
		evt = bill_ops.create_resource_price(self.resourceName,self.timeUnit,self.price,self.resourceUnit)
		self.uuid = evt.uuid
		return evt

	def get_uuid(self):
                return self.uuid

	def delete_resource(self):
		return bill_ops.delete_resource_price(self.uuid)
	
	def compare(self,status):
		prices = super(PublicIpBilling, self).get_price_total()
		time.sleep(1)
		prices1 = super(PublicIpBilling, self).get_price_total()
		if status == "clean" or status == "destory":
			if prices1.total != prices.total:
				test_util.test_fail("test billing fail,maybe can not calculate when vm %s" \
							%(status))
		else:
			if prices1.total <= prices.total:
				test_util.test_fail("test billing fail,maybe can not calculate when vm %s" \
							%(status))

'''
to be define
'''
class GPUBilling(Billing):
        def __init__(self):
                super(GPUBilling, self).__init__()

def set_vm_resource():
	imageUuid = res_ops.query_resource_fields(res_ops.IMAGE, \
				res_ops.gen_query_conditions('system', '=',  'false'))[0].uuid
	instanceOfferingUuid = res_ops.query_resource_fields(res_ops.INSTANCE_OFFERING, \
				res_ops.gen_query_conditions('type', '=',  'UserVm'))[0].uuid
	l3NetworkUuids = res_ops.query_resource_fields(res_ops.L3_NETWORK, \
				res_ops.gen_query_conditions('name', '=',  'public network'))[0].uuid
	return (imageUuid,instanceOfferingUuid,l3NetworkUuids)

def create_vm_billing(name, image_uuid, host_uuid, instance_offering_uuid, l3_uuid, session_uuid=None):
	vm_creation_option = test_util.VmOption()
	vm_creation_option.set_name(name)
	vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
	vm_creation_option.set_image_uuid(image_uuid)
	vm_creation_option.set_l3_uuids([l3_uuid])
	if host_uuid:
		vm_creation_option.set_host_uuid(host_uuid)
	if session_uuid:
		vm_creation_option.set_session_uuid(session_uuid)
	vm = test_vm.ZstackTestVm()
	vm.set_creation_option(vm_creation_option)
	vm.create()
	return vm

def get_resource_from_vmm(resource_type,zone_uuid = None,host_uuid_from_vmm = None):
	if zone_uuid:
		cond = res_ops.gen_query_conditions('zoneUuid', '=', zone_uuid)
	else:
		cond = res_ops.gen_query_conditions('name', '!=', 'NULL')
        resource_list = res_ops.query_resource(resource_type, cond)
	if resource_type == "PrimaryStorage":
		return judge_PrimaryStorage(resource_list)
	if resource_type == "Host":
		return judge_HostResource(resource_list,host_uuid_from_vmm)
	if resource_type == "BackupStorage":
		return judge_BackStorage(resource_list)

def judge_PrimaryStorage(PrimaryStorageSource):
	flag = 0
        for childStorge in PrimaryStorageSource:
                test_util.test_logger("type is %s" %(childStorge.type))
                if childStorge.type == "LocalStorage":
                        flag = 1
                        break
	return flag

def judge_HostResource(HostSource,host_uuid):
	for host in HostSource:
		test_util.test_logger("host uuid is %s" %(host.uuid))
		if host.uuid != host_uuid:
			return host.uuid
		else:
			return None

def judge_BackStorage(BackStorageSource):
	flag = 0
	for backstorage in BackStorageSource:
		test_util.test_logger("backstorage uuid is %s" %(backstorage))
		if backstorage.type == "ImageStoreBackupStorage" or backstorage.type == "CephBackupStorage":
			flag = 1
	return flag

'''
create many billing instantiation
'''
def create_option_billing(billing_option,count):
        length_step = count/2
        for i in range(0, count):
                billing_option.set_price(i)
                if i >= count/2:
                        billing_option.set_timeUnit("m")
                threading.Thread(target=billing_option.create_resource_type()).start()
                if threading.active_count() > length_step:
                        time.sleep(3)
                        length_step += count/4
'''
query many billing and delete these
'''
def verify_option_billing(billing_count):
	for i in range(0,5):
		resourcePrices = query_resource_price()
		if len(resourcePrices) == billing_count:
                        break
                if  i == 4 and len(resourcePrices) != billing_count:
                        test_util.test_fail("create %s  billing fail ,actual create is %s" %(billing_count,len(resourcePrices)))
                time.sleep(3)
	for resourceprice in resourcePrices:
		delete_price(resourceprice.uuid)
	
def query_resource_price(uuid = None, price = None, resource_name = None, time_unit = None, resource_unit = None):
	cond = []
	if uuid:
		cond = res_ops.gen_query_conditions('uuid', "=", uuid, cond)
	if price:
		cond = res_ops.gen_query_conditions('price', "=", price, cond)
	if resource_name:
		cond = res_ops.gen_query_conditions('resourceName', "=", resource_name, cond)
	if time_unit:
		cond = res_ops.gen_query_conditions('timeUnit', "=", time_unit, cond)
	if resource_unit:
		cond = res_ops.gen_query_conditions('resourceUnit', "=", resource_unit, cond)
	result = bill_ops.query_resource_price(cond)
	return result

def delete_price(price_uuid, delete_mode = None):
	test_util.test_logger('Delete resource price')
	result = bill_ops.delete_resource_price(price_uuid, delete_mode)
	return result

def generate_collectd_conf(host, collectdPath, list_port, host_disks = None,
                           host_nics = None, vm_disks = None, vm_nics = None):

    hostUuid = ''
    hostInstance = ''
    hostCpu = ''
    hostDisks = []
    hostMem = ''
    hostNics = []

    vmUuid = ''
    vmCpu = ''
    vmDisks = []
    vmMem = ''
    vmNics = []

    collectdFile = ''
    collectdModule = ''

    hostInstance = host.managementIp.replace('.','-')
    hostUuid = host.uuid
    hostCpu = host.cpuNum
    hostMem = int(int(host.totalMemoryCapacity) / 1024 / 1024)
    hostDisks = ' '.join(host_disks)
    hostNics = ' '.join(host_nics)
 
    cond = res_ops.gen_query_conditions('hostUuid', '=', hostUuid)
    vminstances = res_ops.query_resource_fields(res_ops.VM_INSTANCE, cond)
 
    collectdFile = os.path.join(collectdPath, hostInstance + '.conf')
    collectdModule = os.path.join(collectdPath, 'modules')
    test_util.test_logger('generate collectd file %s for %s with cpu %s mem %s'\
                          % (collectdFile, hostInstance, hostCpu, hostMem))
 
    fd = open(collectdFile, 'w+')
    fd.write('Interval 10\nFQDNLookup false\nLoadPlugin python\nLoadPlugin network\n')
    fd.write('<Plugin network>\n')
    fd.write('Server \"localhost\" \"' + str(list_port) + '\"\n')
    fd.write('</Plugin>\n')
    fd.write('<Plugin python>\n')
    fd.write('ModulePath \"' + collectdModule + '\"\n')
    fd.write('LogTraces true\n')
    fd.write('Import \"cpu\"\n')
    fd.write('Import \"disk\"\n')
    fd.write('Import \"interface\"\n')
    fd.write('Import \"memory\"\n')
    fd.write('Import \"virt\"\n')
 
    fd.write('<Module cpu>\n')
    fd.write('Instance \"' + hostInstance + '\"\n')
    fd.write('Cpu_Num \"' + str(hostCpu) + '\"\n')
    fd.write('</Module>\n')
 
    fd.write('<Module disk>\n')
    fd.write('Instance \"' + hostInstance + '\"\n')
    fd.write('Disk_Instances \"' + hostDisks + '\"\n')
    fd.write('</Module>\n')
 
    fd.write('<Module interface>\n')
    fd.write('Instance \"' + hostInstance + '\"\n')
    fd.write('Net_Interfaces \"' + hostNics + '\"\n')
    fd.write('</Module>\n')
 
    fd.write('<Module memory>\n')
    fd.write('Instance \"' + hostInstance + '\"\n')
    fd.write('Memory \"' + str(hostMem) + '\"\n')
    fd.write('</Module>\n')
 
    if vminstances:
        fd.write('<Module virt>\n')
        for j in range(0, len(vminstances)):
            vmUuid = vminstances[j].uuid
            vmCpu = vminstances[j].cpuNum
            vmDisks = ' '.join(vm_disks)
            vmMem = int(int(vminstances[j].memorySize ) / 1025 / 1024)
            vmNics = ' '.join(vm_nics) 
 
            fd.write('VM_Instance' + str(j) + '_Name \"' + vmUuid + '\"\n')
            fd.write('VM_Instance' + str(j) + '_Cpu_Num \"' + str(vmCpu) + '\"\n')
            fd.write('VM_Instance' + str(j) + '_Memory \"' + str(vmMem) + '\"\n')
            fd.write('VM_Instance' + str(j) + '_Disks \"' + vmDisks + '\"\n')
            fd.write('VM_Instance' + str(j) + '_Net_Interfaces \"' + vmNics + '\"\n')
 
        fd.write('</Module>\n')
 
    fd.write('</Plugin>\n')
    fd.close()

    return collectdFile

def collectd_trigger(collectdFile):

    cmd = 'collectd -C ' + collectdFile + ' -f'
    try:
        #shell.call(cmd)
        os.system(cmd)
        test_util.test_logger('successfully trigger collectd for conf %s' % collectdFile)
    except:
        test_util.test_logger('fail to execute command %s' % cmd)
        return False

    return True

def collectdmon_trigger(collectdFile):

    cmd = 'collectdmon -- -C ' + collectdFile
    try:
        #shell.call(cmd)
        os.system(cmd)
        test_util.test_logger('successfully trigger collectdmon for conf %s' % collectdFile)
    except:
        test_util.test_logger('fail to execute command %s' % cmd)
        return False

    return True

def collectd_exporter_trigger(list_port, web_port):
    cmd = ''

    if os.path.exists('/var/lib/zstack/kvm/collectd_exporter'):
        cmd = '/var/lib/zstack/kvm/collectd_exporter -collectd.listen-address :' + str(list_port) + ' -web.listen-address :' + str(web_port)
        try:
            os.system(cmd)
            #shell.call(cmd)
            test_util.test_logger('successfully trigger collectd_exporter with listen port %s and web port %s' % (list_port, web_port))
        except:
            test_util.test_logger('fail to execute command %s' % cmd)
            return False
    else:
        test_util.test_logger('no collectd_exporter found under /var/lib/zstack/kvm/')
        return False

    return True

def prometheus_conf_generate(host, web_port, address = None):
    hostInstance = ''
    hostUuid = ''
    dict_prometheus = {}

    prometheus_dir = '/usr/local/zstacktest/prometheus/discovery/hosts/'

    if address:
        ip_addr = address
    else:
        ip_addr = '127.0.0.1'

    hostInstance = host.managementIp.replace('.','-')
    hostUuid = host.uuid

    dict_prometheus['labels'] = {'hostUuid':hostUuid}
    dict_prometheus['targets'] = [str(ip_addr) + ':9100', str(ip_addr) + ':' + str(web_port), str(ip_addr) + ':7069']

    file_path = os.path.join(prometheus_dir, hostUuid + '-' + hostInstance + '.json')

    with open(file_path, 'w+') as fd:
        fd.write('[' + json.dumps(dict_prometheus) + ']')

    test_util.test_logger('successfully deploy host %s with port %s for prometheus' % (hostInstance, web_port))

    return True
