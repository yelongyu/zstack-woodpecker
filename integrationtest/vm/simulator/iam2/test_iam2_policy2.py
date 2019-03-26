'''
@author: SyZhao
'''
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.operations.iam2_operations as iam2_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.zstack_test.zstack_test_vid as test_vid
import os

case_flavor = dict(predefined_no_delete_admin=		          dict(target_admin='noDeleteAdmin'),
                   #predefined_read_only_admin=		          dict(target_admin='readOnlyAdmin'),
                   )

vid_uuid = None

def test():
    global vid_uuid
    statements = []
    flavor = case_flavor[os.environ.get('CASE_FLAVOR')]

    vid_test_obj = test_vid.ZstackTestVid()

    if flavor['target_admin'] == 'noDeleteAdmin':
        username = 'noDeleteAdmin'
        password = 'b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86'
        vid_test_obj.create(username, password)
        vid_uuid = vid_test_obj.get_vid().uuid    
        #platform_admin_uuid = iam2_ops.create_iam2_virtual_id(username, password).uuid
        attributes = [{"name": "__PlatformAdmin__"}, {"name":"__PlatformAdminRelatedZone__", "value": "ALL_ZONES"}]
        iam2_ops.add_attributes_to_iam2_virtual_id(vid_uuid, attributes)
        #platform_admin_session_uuid = iam2_ops.login_iam2_virtual_id(username, password)
        role_uuid = iam2_ops.create_role('noDeleteRole').uuid
        statements = [{"effect": "Deny", "actions": ["org.zstack.iam2.api.APIDeleteIAM2OrganizationMsg",
                       "org.zstack.network.service.portforwarding.APIDetachPortForwardingRuleMsg",
                       "org.zstack.autoscaling.group.instance.APIDeleteAutoScalingGroupInstanceMsg",
                       "org.zstack.ldap.APIDeleteLdapServerMsg",
                       "org.zstack.v2v.APIDeleteV2VConversionHostMsg",
                       "org.zstack.header.hybrid.account.APIDeleteHybridKeySecretMsg",
                       "org.zstack.network.service.lb.APIDeleteCertificateMsg",
                       "org.zstack.storage.ceph.primary.APIDeleteCephPrimaryStoragePoolMsg",
                       "org.zstack.scheduler.APIDeleteSchedulerJobMsg",
                       "org.zstack.header.identity.APIDeleteUserMsg",
                       "org.zstack.header.core.webhooks.APIDeleteWebhookMsg",
                       "org.zstack.header.aliyun.network.connection.APIDeleteConnectionBetweenL3NetWorkAndAliyunVSwitchMsg",
                       "org.zstack.header.storage.primary.APIDeletePrimaryStorageMsg",
                       "org.zstack.zwatch.alarm.sns.APIDeleteSNSTextTemplateMsg",
                       "org.zstack.header.aliyun.network.vpc.APIDeleteEcsVSwitchRemoteMsg",
                       "org.zstack.header.volume.APIDetachDataVolumeFromVmMsg",
                       "org.zstack.zwatch.alarm.APIUnsubscribeEventMsg",
                       "org.zstack.sns.APIDeleteSNSTopicMsg",
                       "org.zstack.iam2.api.APIRemoveAttributesFromIAM2ProjectMsg",
                       "org.zstack.header.aliyun.oss.APIDeleteOssBucketNameLocalMsg",
                       "org.zstack.header.aliyun.ecs.APIDeleteEcsInstanceMsg",
                       "org.zstack.network.securitygroup.APIDeleteVmNicFromSecurityGroupMsg",
                       "org.zstack.ipsec.APIDetachL3NetworksFromIPsecConnectionMsg",
                       "org.zstack.core.gc.APIDeleteGCJobMsg",
                       "org.zstack.zwatch.alarm.APIRemoveLabelFromAlarmMsg",
                       "org.zstack.header.longjob.APIDeleteLongJobMsg",
                       "org.zstack.header.aliyun.account.APIDeleteAliyunKeySecretMsg",
                       "org.zstack.network.securitygroup.APIDeleteSecurityGroupRuleMsg",
                       "org.zstack.header.identity.role.api.APIRemovePolicyStatementsFromRoleMsg",
                       "org.zstack.header.identity.role.api.APIDeleteRoleMsg",
                       "org.zstack.header.identity.APIDetachPolicyFromUserGroupMsg",
                       "org.zstack.vrouterRoute.APIDeleteVRouterRouteTableMsg",
                       "org.zstack.iam2.api.APIDeleteIAM2VirtualIDMsg",
                       "org.zstack.header.baremetal.chassis.APIDeleteBaremetalChassisMsg",
                       "org.zstack.header.storage.database.backup.APIDeleteExportedDatabaseBackupFromBackupStorageMsg",
                       "org.zstack.zwatch.alarm.APIRemoveActionFromAlarmMsg",
                       "org.zstack.license.APIDeleteLicenseMsg",
                       "org.zstack.scheduler.APIRemoveSchedulerJobFromSchedulerTriggerMsg",
                       "org.zstack.aliyun.pangu.APIDeleteAliyunPanguPartitionMsg",
                       "org.zstack.sns.platform.dingtalk.APIRemoveSNSDingTalkAtPersonMsg",
                       "org.zstack.header.aliyun.network.vrouter.APIDeleteVirtualRouterLocalMsg",
                       "org.zstack.header.affinitygroup.APIRemoveVmFromAffinityGroupMsg",
                       "org.zstack.header.identity.APILogOutMsg",
                       "org.zstack.network.service.eip.APIDeleteEipMsg",
                       "org.zstack.header.identity.APIDetachPolicyFromUserMsg",
                       "org.zstack.header.hybrid.network.vpn.APIDeleteVpcUserVpnGatewayLocalMsg",
                       "org.zstack.header.volume.APIDeleteVolumeQosMsg",
                       "org.zstack.header.vm.APIDeleteNicQosMsg",
                       "org.zstack.header.storageDevice.APIDetachScsiLunFromVmInstanceMsg",
                       "org.zstack.header.hybrid.network.eip.APIDeleteHybridEipFromLocalMsg",
                       "org.zstack.network.service.lb.APIDeleteLoadBalancerListenerMsg",
                       "org.zstack.header.daho.process.APIDeleteDahoDataCenterConnectionMsg",
                       "org.zstack.vpc.APIRemoveDnsFromVpcRouterMsg",
                       "org.zstack.storage.fusionstor.backup.APIRemoveMonFromFusionstorBackupStorageMsg",
                       "org.zstack.header.aliyun.image.APIDeleteEcsImageLocalMsg",
                       "org.zstack.storage.ceph.backup.APIRemoveMonFromCephBackupStorageMsg",
                       "org.zstack.tag2.APIDetachTagFromResourcesMsg",
                       "org.zstack.pciDevice.APIDeletePciDeviceOfferingMsg",
                       "org.zstack.header.identity.APIRemoveUserFromGroupMsg",
                       "org.zstack.monitoring.APIDeleteAlertMsg",
                       "org.zstack.header.affinitygroup.APIDeleteAffinityGroupMsg",
                       "org.zstack.header.baremetal.pxeserver.APIDetachBaremetalPxeServerFromClusterMsg",
                       "org.zstack.header.vm.APIDeleteVmSshKeyMsg",
                       "org.zstack.header.cluster.APIDeleteClusterMsg",
                       "org.zstack.header.identity.APIDetachPoliciesFromUserMsg",
                       "org.zstack.storage.device.iscsi.APIDeleteIscsiServerMsg",
                       "org.zstack.header.network.l2.APIDeleteL2NetworkMsg",
                       "org.zstack.network.securitygroup.APIDeleteSecurityGroupMsg",
                       "org.zstack.header.storage.backup.APIDeleteBackupStorageMsg",
                       "org.zstack.network.service.lb.APIDeleteLoadBalancerMsg",
                       "org.zstack.iam2.api.APIRemoveIAM2VirtualIDsFromOrganizationMsg",
                       "org.zstack.header.network.l2.APIDetachL2NetworkFromClusterMsg",
                       "org.zstack.header.network.l3.APIRemoveDnsFromL3NetworkMsg",
                       "org.zstack.zwatch.api.APIDeleteMetricDataMsg",
                       "org.zstack.header.image.APIDeleteImageMsg",
                       "org.zstack.monitoring.APIDetachMonitorTriggerActionFromTriggerMsg",
                       "org.zstack.header.volume.APIDeleteDataVolumeMsg",
                       "org.zstack.header.aliyun.network.group.APIDeleteEcsSecurityGroupRuleRemoteMsg",
                       "org.zstack.header.aliyun.ecs.APIDeleteEcsInstanceLocalMsg",
                       "org.zstack.accessKey.APIDeleteAccessKeyMsg",
                       "org.zstack.header.aliyun.network.connection.APIDeleteVirtualBorderRouterLocalMsg",
                       "org.zstack.header.baremetal.pxeserver.APIDeleteBaremetalPxeServerMsg",
                       "org.zstack.header.aliyun.network.group.APIDeleteEcsSecurityGroupInLocalMsg",
                       "org.zstack.header.zone.APIDeleteZoneMsg",
                       "org.zstack.header.hybrid.network.eip.APIDeleteHybridEipRemoteMsg",
                       "org.zstack.header.cloudformation.APIDeleteResourceStackMsg",
                       "org.zstack.network.service.vip.APIDeleteVipMsg",
                       "org.zstack.zwatch.alarm.APIRemoveLabelFromEventSubscriptionMsg",
                       "org.zstack.iam2.api.APIRemoveIAM2VirtualIDsFromProjectMsg",
                       "org.zstack.sns.APIUnsubscribeSNSTopicMsg",
                       "org.zstack.header.storage.primary.APIDetachPrimaryStorageFromClusterMsg",
                       "org.zstack.header.host.APIDeleteHostMsg",
                       "org.zstack.header.cloudformation.APIDeleteStackTemplateMsg",
                       "org.zstack.header.vm.cdrom.APIDeleteVmCdRomMsg",
                       "org.zstack.ipsec.APIDeleteIPsecConnectionMsg",
                       "org.zstack.header.vm.APIDeleteVmConsolePasswordMsg",
                       "org.zstack.header.vm.APIDeleteVmHostnameMsg",
                       "org.zstack.header.hybrid.network.vpn.APIDeleteVpcVpnGatewayLocalMsg",
                       "org.zstack.iam2.api.APIRemoveAttributesFromIAM2VirtualIDMsg",
                       "org.zstack.header.identity.role.api.APIDetachRoleFromAccountMsg",
                       "org.zstack.header.aliyun.image.APIDeleteEcsImageRemoteMsg",
                       "org.zstack.billing.APIDeleteResourcePriceMsg",
                       "org.zstack.header.storage.volume.backup.APIDeleteVolumeBackupMsg",
                       "org.zstack.header.vm.APIDeleteVmBootModeMsg",
                       "org.zstack.network.service.portforwarding.APIDeletePortForwardingRuleMsg",
                       "org.zstack.header.vm.APIDestroyVmInstanceMsg",
                       "org.zstack.header.hybrid.network.vpn.APIDeleteVpcIpSecConfigLocalMsg",
                       "org.zstack.header.storage.snapshot.APIDeleteVolumeSnapshotMsg",
                       "org.zstack.iam2.api.APIRemoveAttributesFromIAM2OrganizationMsg",
                       "org.zstack.header.baremetal.instance.APIDestroyBaremetalInstanceMsg",
                       "org.zstack.iam2.api.APIDeleteIAM2ProjectMsg",
                       "org.zstack.header.aliyun.network.vpc.APIDeleteEcsVSwitchInLocalMsg",
                       "org.zstack.iam2.api.APIRemoveAttributesFromIAM2VirtualIDGroupMsg",
                       "org.zstack.header.daho.process.APIDeleteDahoCloudConnectionMsg",
                       "org.zstack.storage.device.iscsi.APIDetachIscsiServerFromClusterMsg",
                       "org.zstack.aliyun.nas.message.APIDeleteAliyunNasAccessGroupMsg",
                       "org.zstack.vrouterRoute.APIDetachVRouterRouteTableFromVRouterMsg",
                       "org.zstack.header.aliyun.network.vpc.APIDeleteEcsVpcInLocalMsg",
                       "org.zstack.header.aliyun.network.vpc.APIDeleteEcsVpcRemoteMsg",
                       "org.zstack.network.service.eip.APIDetachEipMsg",
                       "org.zstack.header.storage.backup.APIDetachBackupStorageFromZoneMsg",
                       "org.zstack.header.hybrid.network.vpn.APIDeleteVpcIkeConfigLocalMsg",
                       "org.zstack.header.aliyun.oss.APIDeleteOssBucketFileRemoteMsg",
                       "org.zstack.monitoring.media.APIDeleteMediaMsg",
                       "org.zstack.header.aliyun.storage.disk.APIDeleteAliyunDiskFromRemoteMsg",
                       "org.zstack.zwatch.alarm.APIRemoveActionFromEventSubscriptionMsg",
                       "org.zstack.header.vipQos.APIDeleteVipQosMsg",
                       "org.zstack.sns.APIDeleteSNSApplicationEndpointMsg",
                       "org.zstack.header.aliyun.network.connection.APIDeleteAliyunRouterInterfaceLocalMsg",
                       "org.zstack.header.datacenter.APIDeleteDataCenterInLocalMsg",
                       "org.zstack.header.network.service.APIDetachNetworkServiceFromL3NetworkMsg",
                       "org.zstack.storage.ceph.primary.APIRemoveMonFromCephPrimaryStorageMsg",
                       "org.zstack.header.storage.backup.APIDeleteExportedImageFromBackupStorageMsg",
                       "org.zstack.network.service.lb.APIRemoveCertificateFromLoadBalancerListenerMsg",
                       "org.zstack.ldap.APIDeleteLdapBindingMsg",
                       "org.zstack.header.vm.APIDeleteVmNicMsg",
                       "org.zstack.scheduler.APIDeleteSchedulerTriggerMsg",
                       "org.zstack.header.daho.process.APIDeleteDahoVllMsg",
                       "org.zstack.nas.APIDeleteNasMountTargetMsg",
                       "org.zstack.monitoring.actions.APIDeleteMonitorTriggerActionMsg",
                       "org.zstack.header.aliyun.network.connection.APIDeleteConnectionAccessPointLocalMsg",
                       "org.zstack.header.identity.APIDeletePolicyMsg",
                       "org.zstack.monitoring.APIDeleteMonitorTriggerMsg",
                       "org.zstack.ipsec.APIRemoveRemoteCidrsFromIPsecConnectionMsg",
                       "org.zstack.header.identity.APIDeleteUserGroupMsg",
                       "org.zstack.header.hybrid.network.vpn.APIDeleteVpcUserVpnGatewayRemoteMsg",
                       "org.zstack.header.vm.APIDetachIsoFromVmInstanceMsg",
                       "org.zstack.ticket.iam2.api.APIDeleteIAM2TicketFlowMsg",
                       "org.zstack.header.network.l3.APIDeleteL3NetworkMsg",
                       "org.zstack.ticket.api.APIDeleteTicketFlowCollectionMsg",
                       "org.zstack.header.vm.APIDeleteVmStaticIpMsg",
                       "org.zstack.storage.fusionstor.primary.APIRemoveMonFromFusionstorPrimaryStorageMsg",
                       "org.zstack.header.configuration.APIDeleteInstanceOfferingMsg",
                       "org.zstack.header.storage.database.backup.APIDeleteDatabaseBackupMsg",
                       "org.zstack.iam2.api.APIDeleteIAM2ProjectTemplateMsg",
                       "org.zstack.sns.APIDeleteSNSApplicationPlatformMsg",
                       "org.zstack.header.hybrid.network.vpn.APIDeleteVpcVpnConnectionRemoteMsg",
                       "org.zstack.header.aliyun.storage.snapshot.APIDeleteAliyunSnapshotFromLocalMsg",
                       "org.zstack.header.aliyun.storage.snapshot.APIDeleteAliyunSnapshotFromRemoteMsg",
                       "org.zstack.header.tag.APIDeleteTagMsg",
                       "org.zstack.header.identity.role.api.APIDetachPolicyFromRoleMsg",
                       "org.zstack.header.hybrid.network.vpn.APIDeleteVpcVpnConnectionLocalMsg",
                       "org.zstack.header.aliyun.storage.disk.APIDeleteAliyunDiskFromLocalMsg",
                       "org.zstack.header.hybrid.backup.APIDeleteBackupFileInPublicMsg",
                       "org.zstack.autoscaling.template.APIDetachAutoScalingTemplateFromGroupMsg",
                       "org.zstack.zwatch.alarm.APIDeleteAlarmMsg",
                       "org.zstack.aliyun.nas.message.APIDeleteAliyunNasAccessGroupRuleMsg",
                       "org.zstack.header.aliyun.network.vrouter.APIDeleteAliyunRouteEntryRemoteMsg",
                       "org.zstack.core.config.resourceconfig.APIDeleteResourceConfigMsg",
                       "org.zstack.vmware.APIDeleteVCenterMsg",
                       "org.zstack.header.network.l3.APIRemoveHostRouteFromL3NetworkMsg",
                       "org.zstack.network.service.lb.APIRemoveVmNicFromLoadBalancerMsg",
                       "org.zstack.ticket.api.APIDeleteTicketMsg",
                       "org.zstack.nas.APIDeleteNasFileSystemMsg",
                       "org.zstack.header.aliyun.network.group.APIDeleteEcsSecurityGroupRemoteMsg",
                       "org.zstack.autoscaling.group.rule.APIDeleteAutoScalingRuleMsg",
                       "org.zstack.vrouterRoute.APIDeleteVRouterRouteEntryMsg",
                       "org.zstack.network.securitygroup.APIDetachSecurityGroupFromL3NetworkMsg",
                       "org.zstack.header.identity.APIDeleteAccountMsg",
                       "org.zstack.header.network.l3.APIDeleteIpRangeMsg",
                       "org.zstack.autoscaling.group.APIDeleteAutoScalingGroupMsg",
                       "org.zstack.header.aliyun.network.connection.APIDeleteAliyunRouterInterfaceRemoteMsg",
                       "org.zstack.autoscaling.template.APIDeleteAutoScalingTemplateMsg",
                       "org.zstack.header.vm.APIDetachL3NetworkFromVmMsg",
                       "org.zstack.iam2.api.APIRemoveIAM2VirtualIDsFromGroupMsg",
                       "org.zstack.iam2.api.APIRemoveRolesFromIAM2VirtualIDMsg",
                       "org.zstack.autoscaling.group.rule.trigger.APIDeleteAutoScalingRuleTriggerMsg",
                       "org.zstack.header.configuration.APIDeleteDiskOfferingMsg",
                       "org.zstack.header.aliyun.ecs.APIDeleteAllEcsInstancesFromDataCenterMsg",
                       "org.zstack.header.storage.volume.backup.APIDeleteVmBackupMsg",
                       "org.zstack.network.l2.vxlan.vxlanNetworkPool.APIDeleteVniRangeMsg",
                       "org.zstack.iam2.api.APIDeleteIAM2VirtualIDGroupMsg",
                       "org.zstack.pciDevice.APIDeletePciDeviceMsg",
                       "org.zstack.header.identityzone.APIDeleteIdentityZoneInLocalMsg",
                       "org.zstack.iam2.api.APIRemoveRolesFromIAM2VirtualIDGroupMsg",
                       "org.zstack.header.baremetal.preconfiguration.APIDeletePreconfigurationTemplateMsg",
                       "org.zstack.header.aliyun.oss.APIDeleteOssBucketRemoteMsg",
                       "org.zstack.iam2.api.APIExpungeIAM2ProjectMsg",
                       "org.zstack.header.volume.APIExpungeDataVolumeMsg",
                       "org.zstack.header.image.APIExpungeImageMsg",
                       "org.zstack.header.vm.APIExpungeVmInstanceMsg"]}]

        policy_uuid = iam2_ops.create_policy('noDeletePolicy', statements).uuid
        iam2_ops.attach_policy_to_role(policy_uuid, role_uuid)
        iam2_ops.add_roles_to_iam2_virtual_id([role_uuid], vid_test_obj.get_vid().uuid)
        vid_test_obj.set_customized("noDeleteAdminPermission")
        vid_test_obj.set_vid_statements(statements)
        vid_test_obj.check()
        iam2_ops.update_role(role_uuid, [])
        iam2_ops.add_policy_statements_to_role(role_uuid, statements)
        vid_test_obj.set_customized("noDeleteAdminPermission")
        vid_test_obj.set_vid_statements(statements)
        vid_test_obj.check()

    #if flavor['target_admin'] == 'readOnlyAdmin':
    #    username = 'readOnlyAdmin'
    #    password = 'b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86'
    #    vid_uuid = iam2_ops.create_iam2_virtual_id(username, password).uuid
    #    attributes = [{"name": "__AuditAdmin__"}]
    #    iam2_ops.add_attributes_to_iam2_virtual_id(vid_uuid, attributes)
    #    read_only_admin_session_uuid = iam2_ops.login_iam2_virtual_id(username, password)

    #    vid_test_obj.set_vid_statements(statements)
    #    vid_test_obj.check()


    vid_test_obj.delete()
    test_util.test_pass('success test iam2 policy!')


# Will be called only if exception happens in test().
def error_cleanup():
    global vid_uuid
    if vid_uuid:
        iam2_ops.delete_iam2_virtual_id(vid_uuid)
