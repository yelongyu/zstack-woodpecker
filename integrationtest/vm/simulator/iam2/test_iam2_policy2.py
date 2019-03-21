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
                   predefined_read_only_admin=		          dict(target_admin='readOnlyAdmin'),
                   )

project_uuid = None
virtual_id_uuid = None

def test():
    global project_uuid, virtual_id_uuid
    statements = []
    flavor = case_flavor[os.environ.get('CASE_FLAVOR')]

    policy_check_vid = test_vid.ZstackTestVid()
    policy_check_vid.create('policy_check', password)
    virtual_id_uuid = policy_check_vid.get_vid().uuid    

    if flavor['target_admin'] == 'noDeleteAdmin':
        username = 'noDeleteAdmin'
        password = 'b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86'
        platform_admin_uuid = iam2_ops.create_iam2_virtual_id(username, password).uuid
        attributes = [{"name": "__PlatformAdmin__"}]
        iam2_ops.add_attributes_to_iam2_virtual_id(platform_admin_uuid, attributes)
        platform_admin_session_uuid = iam2_ops.login_iam2_virtual_id(username, password)
        role_uuid = iam2_ops.create_role('noDeleteRole').uuid
        statements = [{"effect": "Deny", "actions": ["org.zstack.monitoring.media.APIDeleteMediaMsg",
                            "org.zstack.ticket.api.APIDeleteTicketMsg",
                            "org.zstack.vrouterRoute.APIDeleteVRouterRouteEntryMsg",
                            "org.zstack.header.hybrid.network.vpn.APIDeleteVpcVpnConnectionRemoteMsg",
                            "org.zstack.monitoring.APIDeleteMonitorTriggerMsg",
                            "org.zstack.zwatch.alarm.APIUnsubscribeEventMsg",
                            "org.zstack.header.aliyun.account.APIDeleteAliyunKeySecretMsg",
                            "org.zstack.header.aliyun.network.vrouter.APIDeleteAliyunRouteEntryRemoteMsg",
                            "org.zstack.header.baremetal.preconfiguration.APIDeletePreconfigurationTemplateMsg",
                            "org.zstack.header.aliyun.storage.disk.APIDeleteAliyunDiskFromRemoteMsg",
                            "org.zstack.header.aliyun.network.connection.APIDeleteAliyunRouterInterfaceRemoteMsg",
                            "org.zstack.header.daho.process.APIDeleteDahoCloudConnectionMsg",
                            "org.zstack.autoscaling.group.rule.APIDeleteAutoScalingRuleMsg",
                            "org.zstack.header.baremetal.instance.APIDestroyBaremetalInstanceMsg",
                            "org.zstack.iam2.api.APIDeleteIAM2VirtualIDMsg",
                            "org.zstack.header.cloudformation.APIDeleteResourceStackMsg",
                            "org.zstack.vrouterRoute.APIDeleteVRouterRouteTableMsg",
                            "org.zstack.header.core.webhooks.APIDeleteWebhookMsg",
                            "org.zstack.header.vm.APIDeleteVmBootModeMsg",
                            "org.zstack.sns.APIDeleteSNSApplicationPlatformMsg",
                            "org.zstack.header.identity.APIDeleteAccountMsg",
                            "org.zstack.network.service.portforwarding.APIDeletePortForwardingRuleMsg",
                            "org.zstack.header.affinitygroup.APIDeleteAffinityGroupMsg",
                            "org.zstack.network.service.vip.APIDeleteVipMsg",
                            "org.zstack.autoscaling.group.APIDeleteAutoScalingGroupMsg",
                            "org.zstack.header.hybrid.network.vpn.APIDeleteVpcIpSecConfigLocalMsg",
                            "org.zstack.header.network.l3.APIDeleteL3NetworkMsg",
                            "org.zstack.aliyun.nas.message.APIDeleteAliyunNasAccessGroupRuleMsg",
                            "org.zstack.storage.device.iscsi.APIDeleteIscsiServerMsg",
                            "org.zstack.header.identityzone.APIDeleteIdentityZoneInLocalMsg",
                            "org.zstack.aliyun.nas.message.APIDeleteAliyunNasAccessGroupMsg",
                            "org.zstack.header.hybrid.backup.APIDeleteBackupFileInPublicMsg",
                            "org.zstack.header.aliyun.ecs.APIDeleteAllEcsInstancesFromDataCenterMsg",
                            "org.zstack.accessKey.APIDeleteAccessKeyMsg",
                            "org.zstack.autoscaling.group.rule.trigger.APIDeleteAutoScalingRuleTriggerMsg",
                            "org.zstack.header.aliyun.oss.APIDeleteOssBucketNameLocalMsg",
                            "org.zstack.header.identity.APIDeletePolicyMsg",
                            "org.zstack.header.network.l2.APIDeleteL2NetworkMsg",
                            "org.zstack.sns.APIDeleteSNSTopicMsg",
                            "org.zstack.header.hybrid.network.eip.APIDeleteHybridEipFromLocalMsg",
                            "org.zstack.header.aliyun.oss.APIDeleteOssBucketFileRemoteMsg",
                            "org.zstack.pciDevice.APIDeletePciDeviceOfferingMsg",
                            "org.zstack.header.aliyun.network.vrouter.APIDeleteVirtualRouterLocalMsg",
                            "org.zstack.billing.APIDeleteResourcePriceMsg",
                            "org.zstack.header.identity.role.api.APIDeleteRoleMsg",
                            "org.zstack.header.datacenter.APIDeleteDataCenterInLocalMsg",
                            "org.zstack.scheduler.APIDeleteSchedulerJobMsg",
                            "org.zstack.header.cluster.APIDeleteClusterMsg",
                            "org.zstack.header.vm.APIDeleteVmHostnameMsg",
                            "org.zstack.header.cloudformation.APIDeleteStackTemplateMsg",
                            "org.zstack.header.aliyun.storage.snapshot.APIGCAliyunSnapshotRemoteMsg",
                            "org.zstack.aliyun.pangu.APIDeleteAliyunPanguPartitionMsg",
                            "org.zstack.header.aliyun.storage.snapshot.APIDeleteAliyunSnapshotFromRemoteMsg",
                            "org.zstack.ticket.iam2.api.APIDeleteIAM2TicketFlowMsg",
                            "org.zstack.header.aliyun.oss.APIDeleteOssBucketRemoteMsg",
                            "org.zstack.header.storage.volume.backup.APIDeleteVolumeBackupMsg",
                            "org.zstack.header.aliyun.network.connection.APIDeleteAliyunRouterInterfaceLocalMsg",
                            "org.zstack.header.hybrid.network.eip.APIDeleteHybridEipRemoteMsg",
                            "org.zstack.header.aliyun.network.connection.APIDeleteConnectionBetweenL3NetWorkAndAliyunVSwitchMsg",
                            "org.zstack.header.storage.backup.APIDeleteBackupStorageMsg",
                            "org.zstack.header.aliyun.network.vpc.APIDeleteEcsVpcRemoteMsg",
                            "org.zstack.zwatch.alarm.sns.APIDeleteSNSTextTemplateMsg",
                            "org.zstack.network.service.lb.APIDeleteCertificateMsg",
                            "org.zstack.scheduler.APIDeleteSchedulerTriggerMsg",
                            "org.zstack.header.volume.APIDeleteDataVolumeMsg",
                            "org.zstack.header.configuration.APIDeleteInstanceOfferingMsg",
                            "org.zstack.header.host.APIDeleteHostMsg",
                            "org.zstack.header.aliyun.network.group.APIDeleteEcsSecurityGroupInLocalMsg",
                            "org.zstack.header.aliyun.network.connection.APIDeleteConnectionAccessPointLocalMsg",
                            "org.zstack.header.vm.APIDestroyVmInstanceMsg",
                            "org.zstack.network.service.lb.APIDeleteLoadBalancerMsg",
                            "org.zstack.header.hybrid.network.vpn.APIDeleteVpcVpnGatewayLocalMsg",
                            "org.zstack.zwatch.alarm.APIDeleteAlarmMsg",
                            "org.zstack.pciDevice.APIDeletePciDeviceMsg",
                            "org.zstack.network.securitygroup.APIDeleteSecurityGroupMsg",
                            "org.zstack.header.aliyun.storage.snapshot.APIDeleteAliyunSnapshotFromLocalMsg",
                            "org.zstack.header.aliyun.image.APIDeleteEcsImageLocalMsg",
                            "org.zstack.header.identity.APIDeleteUserGroupMsg",
                            "org.zstack.header.aliyun.storage.disk.APIDeleteAliyunDiskFromLocalMsg",
                            "org.zstack.sns.APIDeleteSNSApplicationEndpointMsg",
                            "org.zstack.monitoring.actions.APIDeleteMonitorTriggerActionMsg",
                            "org.zstack.header.aliyun.network.vpc.APIDeleteEcsVSwitchInLocalMsg",
                            "org.zstack.nas.APIDeleteNasFileSystemMsg",
                            "org.zstack.header.aliyun.ecs.APIDeleteEcsInstanceLocalMsg",
                            "org.zstack.header.zone.APIDeleteZoneMsg",
                            "org.zstack.zwatch.alarm.APIRemoveLabelFromAlarmMsg",
                            "org.zstack.header.aliyun.image.APIDeleteEcsImageRemoteMsg",
                            "org.zstack.header.tag.APIDeleteTagMsg",
                            "org.zstack.header.aliyun.network.connection.APIDeleteVirtualBorderRouterLocalMsg",
                            "org.zstack.header.daho.process.APIDeleteDahoDataCenterConnectionMsg",
                            "org.zstack.header.hybrid.account.APIDeleteHybridKeySecretMsg",
                            "org.zstack.header.network.l3.APIDeleteIpRangeMsg",
                            "org.zstack.nas.APIDeleteNasMountTargetMsg",
                            "org.zstack.zwatch.alarm.APIRemoveActionFromAlarmMsg",
                            "org.zstack.header.identity.APIDeleteUserMsg",
                            "org.zstack.autoscaling.group.instance.APIDeleteAutoScalingGroupInstanceMsg",
                            "org.zstack.ldap.APIDeleteLdapServerMsg",
                            "org.zstack.network.l2.vxlan.vxlanNetworkPool.APIDeleteVniRangeMsg",
                            "org.zstack.header.hybrid.network.vpn.APIDeleteVpcVpnConnectionLocalMsg",
                            "org.zstack.header.baremetal.chassis.APIDeleteBaremetalChassisMsg",
                            "org.zstack.sns.platform.dingtalk.APIRemoveSNSDingTalkAtPersonMsg",
                            "org.zstack.header.storage.snapshot.APIDeleteVolumeSnapshotMsg",
                            "org.zstack.header.vm.APIDeleteVmStaticIpMsg",
                            "org.zstack.network.service.eip.APIDeleteEipMsg",
                            "org.zstack.header.configuration.APIDeleteDiskOfferingMsg",
                            "org.zstack.header.vm.cdrom.APIDeleteVmCdRomMsg",
                            "org.zstack.header.aliyun.network.vpc.APIDeleteEcsVSwitchRemoteMsg",
                            "org.zstack.header.identity.role.api.APIDetachRoleFromAccountMsg",
                            "org.zstack.v2v.APIDeleteV2VConversionHostMsg",
                            "org.zstack.vmware.APIDeleteVCenterMsg",
                            "org.zstack.header.hybrid.network.vpn.APIDeleteVpcIkeConfigLocalMsg",
                            "org.zstack.monitoring.APIDeleteAlertMsg",
                            "org.zstack.header.vm.APIDeleteVmNicMsg",
                            "org.zstack.autoscaling.template.APIDeleteAutoScalingTemplateMsg",
                            "org.zstack.header.aliyun.network.vpc.APIDeleteEcsVpcInLocalMsg",
                            "org.zstack.header.image.APIDeleteImageMsg",
                            "org.zstack.header.hybrid.network.vpn.APIDeleteVpcUserVpnGatewayRemoteMsg",
                            "org.zstack.header.baremetal.pxeserver.APIDeleteBaremetalPxeServerMsg",
                            "org.zstack.ticket.api.APIDeleteTicketFlowCollectionMsg",
                            "org.zstack.header.aliyun.network.group.APIDeleteEcsSecurityGroupRemoteMsg",
                            "org.zstack.header.daho.process.APIDeleteDahoVllMsg",
                            "org.zstack.ipsec.APIDeleteIPsecConnectionMsg",
                            "org.zstack.header.hybrid.network.vpn.APIDeleteVpcUserVpnGatewayLocalMsg",
                            "org.zstack.header.aliyun.ecs.APIDeleteEcsInstanceMsg",
                            "org.zstack.header.storage.volume.backup.APIDeleteVmBackupMsg",
                            "org.zstack.header.aliyun.network.group.APIDeleteEcsSecurityGroupRuleRemoteMsg",
                            "org.zstack.header.storage.primary.APIDeletePrimaryStorageMsg" ]}]
        policy_uuid = iam2_ops.create_policy('noDeletePolicy', statements).uuid
        iam2_ops.attach_policy_to_role(policy_uuid, role_uuid)
        iam2_ops.add_roles_to_iam2_virtual_id([role_uuid], policy_check_vid.get_vid().uuid)
        policy_check_vid.set_customized("noDeleteAdminPermission")
        policy_check_vid.check()
        iam2_ops.update_role(role_uuid, [])
        iam2_ops.add_policy_statements_to_role(role_uuid, statements)
        policy_check_vid.set_customized("noDeleteAdminPermission")
        policy_check_vid.check()

    if flavor['target_admin'] == 'readOnlyAdmin':
        username = 'readOnlyAdmin'
        password = 'b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86'
        vid_uuid = iam2_ops.create_iam2_virtual_id(username, password).uuid
        attributes = [{"name": "__AuditAdmin__"}]
        iam2_ops.add_attributes_to_iam2_virtual_id(vid_uuid, attributes)
        read_only_admin_session_uuid = iam2_ops.login_iam2_virtual_id(username, password)

        policy_check_vid.set_vid_statements(statements)
        policy_check_vid.check()


    policy_check_vid.delete()
    test_util.test_pass('success test iam2 policy!')


# Will be called only if exception happens in test().
def error_cleanup():
    global project_uuid, project_admin_uuid, virtual_id_uuid
    if virtual_id_uuid:
        iam2_ops.delete_iam2_virtual_id(virtual_id_uuid)
    if project_uuid:
        iam2_ops.delete_iam2_project(project_uuid)
        iam2_ops.expunge_iam2_project(project_uuid)
