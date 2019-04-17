# -*- coding: utf-8 -*-
'''
@author: Glody
'''
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.operations.iam2_operations as iam2_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.zstack_test.zstack_test_vid as test_vid
import os

case_flavor = dict(predefined_vm=    				               dict(target_role='vm'),
                   predefined_vm_operation_without_create_permission=          dict(target_role='vm_ops_without_creation'),
                   predefined_image=           				       dict(target_role='image'),
                   predefined_volume=                                          dict(target_role='volume'),
                   predefined_snapshot=					       dict(target_role='snapshot'),
                   predefined_affinity_group= 				       dict(target_role='affinity_group'),
                   predefined_networks=					       dict(target_role='networks'),
                   predefined_eip=					       dict(target_role='eip'),
                   predefined_security_group=				       dict(target_role='sg'),
                   predefined_load_balancer=				       dict(target_role='lb'),
                   predefined_port_forwarding=				       dict(target_role='pf'),
                   predefined_scheduler=				       dict(target_role='scheduler'),
                   predefined_pci_device= 				       dict(target_role='pci'),
                   predefined_zwatch=				       	       dict(target_role='zwatch'),
                   predefined_sns=				       	       dict(target_role='sns'),
                   )

project_uuid = None
virtual_id_uuid = None

def test():
    global project_uuid, virtual_id_uuid
    statements = []
    flavor = case_flavor[os.environ.get('CASE_FLAVOR')]
    zone_uuid = res_ops.query_resource(res_ops.ZONE)[0].uuid
    project_name = 'test_project_01'
    attributes = [{"name": "__ProjectRelatedZone__", "value": zone_uuid}]
    project_obj = iam2_ops.create_iam2_project(project_name, attributes=attributes)
    project_uuid = project_obj.uuid
    project_linked_account_uuid = project_obj.linkedAccountUuid
    password = 'b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86'
    '''name = 'username'
    name1 = 'username1'
    name2 = 'username2'
    password = 'b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86'

    vid = test_vid.ZstackTestVid()
    vid.create(name, password)
    attributes = [{"name": "__PlatformAdmin__"}]
    iam2_ops.add_attributes_to_iam2_virtual_id(vid.get_vid().uuid, attributes)
    vid.set_vid_attributes(attributes)
    vid.check()
    attributes = [{"name": "__ProjectAdmin__", "value": project_linked_account_uuid}]

    vid1 = test_vid.ZstackTestVid()
    vid1.create(name1, password)
    iam2_ops.add_iam2_virtual_ids_to_project([vid1.get_vid().uuid], project_uuid)
    attributes = [{"name": "__ProjectAdmin__", "value": project_uuid}]
    iam2_ops.add_attributes_to_iam2_virtual_id(vid1.get_vid().uuid, attributes)
    vid1.set_vid_attributes(attributes)
    vid1.check()

    vid2 = test_vid.ZstackTestVid()
    vid2.create(name2, password)
    iam2_ops.add_iam2_virtual_ids_to_project([vid2.get_vid().uuid], project_uuid)
    attributes = [{"name": "__ProjectOperator__", "value": project_uuid}]
    iam2_ops.add_attributes_to_iam2_virtual_id(vid2.get_vid().uuid, attributes)
    vid2.set_vid_attributes(attributes)
    vid2.check()
    '''


    policy_check_vid = test_vid.ZstackTestVid()
    policy_check_vid.create('policy_check', password)
    iam2_ops.add_iam2_virtual_ids_to_project([policy_check_vid.get_vid().uuid], project_uuid)
    virtual_id_uuid = policy_check_vid.get_vid().uuid    
    if flavor['target_role'] == 'vm':
        statements = [{"effect": "Allow", "actions": ["org.zstack.header.vm.**",
                            "org.zstack.ha.**"]}]
        cond = res_ops.gen_query_conditions('name', '=', "predefined: vm")
        cond = res_ops.gen_query_conditions('type', '=', "predefined", cond)

    if flavor['target_role'] == 'vm_ops_without_creation':
        statements = [{"effect": "Allow", "actions": ["org.zstack.header.vm.APIGetVmQgaMsg",
                            "org.zstack.header.vm.APIChangeVmImageMsg",
                            "org.zstack.header.vm.APISetVmSshKeyMsg",
                            "org.zstack.header.vm.APIStopVmInstanceMsg",
                            "org.zstack.header.vm.APISetVmStaticIpMsg",
                            "org.zstack.header.vm.APIRecoverVmInstanceMsg",
                            "org.zstack.header.vm.APIQueryVmNicMsg",
                            "org.zstack.header.vm.APIStartVmInstanceMsg",
                            "org.zstack.header.vm.APIDestroyVmInstanceMsg",
                            "org.zstack.header.vm.APIGetVmConsolePasswordMsg",
                            "org.zstack.header.vm.APIDeleteVmStaticIpMsg",
                            "org.zstack.header.vm.APISetNicQosMsg",
                            "org.zstack.header.vm.APIRebootVmInstanceMsg",
                            "org.zstack.header.vm.APIGetNicQosMsg",
                            "org.zstack.header.vm.APIGetVmBootOrderMsg",
                            "org.zstack.header.vm.APIChangeVmPasswordMsg",
                            "org.zstack.header.vm.APIGetCandidatePrimaryStoragesForCreatingVmMsg",
                            "org.zstack.header.vm.APISetVmRDPMsg",
                            "org.zstack.header.vm.APIMigrateVmMsg",
                            "org.zstack.header.vm.APIGetVmMigrationCandidateHostsMsg",
                            "org.zstack.header.vm.APIAttachL3NetworkToVmMsg",
                            "org.zstack.header.vm.APIExpungeVmInstanceMsg",
                            "org.zstack.header.vm.APIGetCandidateVmForAttachingIsoMsg",
                            "org.zstack.header.vm.APIAttachIsoToVmInstanceMsg",
                            "org.zstack.header.vm.APIGetVmAttachableL3NetworkMsg",
                            "org.zstack.header.vm.APIGetVmHostnameMsg",
                            "org.zstack.header.vm.APIDeleteVmSshKeyMsg",
                            "org.zstack.header.vm.APIGetVmMonitorNumberMsg",
                            "org.zstack.header.vm.APISetVmQgaMsg",
                            "org.zstack.header.vm.APIDetachL3NetworkFromVmMsg",
                            "org.zstack.header.vm.APISetVmConsolePasswordMsg",
                            "org.zstack.header.vm.APIGetCandidateZonesClustersHostsForCreatingVmMsg",
                            "org.zstack.header.vm.APIGetVmAttachableDataVolumeMsg",
                            "org.zstack.header.vm.APIGetInterdependentL3NetworksImagesMsg",
                            "org.zstack.header.vm.APIGetCandidateIsoForAttachingVmMsg",
                            "org.zstack.header.vm.APIDeleteNicQosMsg",
                            "org.zstack.header.vm.APISetVmUsbRedirectMsg",
                            "org.zstack.header.vm.APISetVmBootOrderMsg",
                            "org.zstack.header.vm.APIGetImageCandidatesForVmToChangeMsg",
                            "org.zstack.header.vm.APIGetVmConsoleAddressMsg",
                            "org.zstack.header.vm.APIChangeInstanceOfferingMsg",
                            "org.zstack.header.vm.APIDeleteVmHostnameMsg",
                            "org.zstack.header.vm.APIGetVmUsbRedirectMsg",
                            "org.zstack.header.vm.APIQueryVmInstanceMsg",
                            "org.zstack.header.vm.APISetVmMonitorNumberMsg",
                            "org.zstack.header.vm.APIReimageVmInstanceMsg",
                            "org.zstack.header.vm.APIResumeVmInstanceMsg",
                            "org.zstack.header.vm.APIUpdateVmNicMacMsg",
                            "org.zstack.header.vm.APIGetVmCapabilitiesMsg",
                            "org.zstack.header.vm.APIUpdateVmInstanceMsg",
                            "org.zstack.header.vm.APIGetVmSshKeyMsg",
                            "org.zstack.header.vm.APICloneVmInstanceMsg",
                            "org.zstack.header.vm.APIDeleteVmConsolePasswordMsg",
                            "org.zstack.header.vm.APISetVmHostnameMsg",
                            "org.zstack.header.vm.APIGetVmStartingCandidateClustersHostsMsg",
                            "org.zstack.header.vm.APIDetachIsoFromVmInstanceMsg",
                            "org.zstack.header.vm.APIGetVmRDPMsg",
                            "org.zstack.header.vm.APIPauseVmInstanceMsg"]}] 
        cond = res_ops.gen_query_conditions('name', '=', "predefined: vm-operation-without-create-permission")
        cond = res_ops.gen_query_conditions('type', '=', "predefined", cond)
    if flavor['target_role'] == 'image':
        statements = [{"effect": "Allow", "actions": ["org.zstack.header.image.**",
                            "org.zstack.storage.backup.imagestore.APIGetImagesFromImageStoreBackupStorageMsg"]}]
        cond = res_ops.gen_query_conditions('name', '=', "predefined: image")
        cond = res_ops.gen_query_conditions('type', '=', "predefined", cond)
    if flavor['target_role'] == 'snapshot':
        statements = [{"effect": "Allow", "actions": ["org.zstack.header.storage.snapshot.**",
                            "org.zstack.header.volume.APICreateVolumeSnapshotMsg"]}]
        cond = res_ops.gen_query_conditions('name', '=', "predefined: snapshot")
        cond = res_ops.gen_query_conditions('type', '=', "predefined", cond)
    if flavor['target_role'] == 'volume':
        statements = [{"effect": "Allow", "actions": ["org.zstack.header.volume.APICreateDataVolumeFromVolumeTemplateMsg",
                            "org.zstack.header.volume.APIGetVolumeQosMsg",
                            "org.zstack.header.volume.APISyncVolumeSizeMsg",
                            "org.zstack.header.volume.APICreateDataVolumeFromVolumeSnapshotMsg",
                            "org.zstack.header.volume.APIResizeDataVolumeMsg",
                            "org.zstack.header.volume.APIRecoverDataVolumeMsg",
                            "org.zstack.header.volume.APIExpungeDataVolumeMsg",
                            "org.zstack.mevoco.APIQueryShareableVolumeVmInstanceRefMsg",
                            "org.zstack.header.volume.APICreateDataVolumeMsg",
                            "org.zstack.header.volume.APIGetVolumeCapabilitiesMsg",
                            "org.zstack.header.volume.APIDetachDataVolumeFromVmMsg",
                            "org.zstack.header.volume.APIDeleteVolumeQosMsg",
                            "org.zstack.header.volume.APIGetVolumeFormatMsg",
                            "org.zstack.header.volume.APIGetDataVolumeAttachableVmMsg",
                            "org.zstack.header.volume.APIAttachDataVolumeToVmMsg",
                            "org.zstack.header.volume.APIResizeRootVolumeMsg",
                            "org.zstack.header.volume.APISetVolumeQosMsg",
                            "org.zstack.header.volume.APIDeleteDataVolumeMsg",
                            "org.zstack.header.volume.APIUpdateVolumeMsg",
                            "org.zstack.header.volume.APIChangeVolumeStateMsg",
                            "org.zstack.header.volume.APIQueryVolumeMsg"]}]
        cond = res_ops.gen_query_conditions('name', '=', "predefined: volume")
        cond = res_ops.gen_query_conditions('type', '=', "predefined", cond)
    if flavor['target_role'] == 'affinity_group':
        statements = [{"effect": "Allow", "actions": ["org.zstack.header.affinitygroup.**"]}]
        cond = res_ops.gen_query_conditions('name', '=', "predefined: affinity-group")
        cond = res_ops.gen_query_conditions('type', '=', "predefined", cond)
    if flavor['target_role'] == 'networks':
        statements = [{"effect": "Allow", "actions": ["org.zstack.header.network.l3.**",
                            "org.zstack.network.service.flat.**",
                            "org.zstack.header.network.l2.APIUpdateL2NetworkMsg",
                            "org.zstack.header.network.service.APIQueryNetworkServiceProviderMsg",
                            "org.zstack.header.network.service.APIAttachNetworkServiceToL3NetworkMsg",
                            "org.zstack.network.l2.vxlan.vxlanNetworkPool.APIQueryVniRangeMsg",
                            "org.zstack.network.l2.vxlan.vxlanNetwork.APIQueryL2VxlanNetworkMsg",
                            "org.zstack.network.l2.vxlan.vxlanNetwork.APICreateL2VxlanNetworkMsg",
                            "org.zstack.network.l2.vxlan.vxlanNetworkPool.APIQueryL2VxlanNetworkPoolMsg"]}]
        cond = res_ops.gen_query_conditions('name', '=', "predefined: networks")
        cond = res_ops.gen_query_conditions('type', '=', "predefined", cond)
    if flavor['target_role'] == 'eip':
        statements = [{"effect": "Allow", "actions": ["org.zstack.network.service.vip.**",
                            "org.zstack.network.service.eip.**",
                            "org.zstack.header.vipQos.**"]}]
        cond = res_ops.gen_query_conditions('name', '=', "predefined: eip")
        cond = res_ops.gen_query_conditions('type', '=', "predefined", cond)
    if flavor['target_role'] == 'sg':
        statements = [{"effect": "Allow", "actions": ["org.zstack.network.securitygroup.**"]}]
        cond = res_ops.gen_query_conditions('name', '=', "predefined: security-group")
        cond = res_ops.gen_query_conditions('type', '=', "predefined", cond)
    if flavor['target_role'] == 'lb':
        statements = [{"effect": "Allow", "actions": ["org.zstack.network.service.lb.**",
                            "org.zstack.network.service.vip.**",
                            "org.zstack.header.vipQos.**"]}]
        cond = res_ops.gen_query_conditions('name', '=', "predefined: load-balancer")
        cond = res_ops.gen_query_conditions('type', '=', "predefined", cond)
    if flavor['target_role'] == 'pf':
        statements = [{"effect": "Allow", "actions": ["org.zstack.network.service.portforwarding.**",
                            "org.zstack.network.service.vip.**",
                            "org.zstack.header.vipQos.**"]}]
        cond = res_ops.gen_query_conditions('name', '=', "predefined: port-forwarding")
        cond = res_ops.gen_query_conditions('type', '=', "predefined", cond)
    if flavor['target_role'] == 'scheduler':
        statements = [{"effect": "Allow", "actions": ["org.zstack.scheduler.**"]}]
        cond = res_ops.gen_query_conditions('name', '=', "predefined: scheduler")
        cond = res_ops.gen_query_conditions('type', '=', "predefined", cond)
    if flavor['target_role'] == 'pci':
        statements = [{"effect": "Allow", "actions": ["org.zstack.pciDevice.APIAttachPciDeviceToVmMsg",
                            "org.zstack.pciDevice.APIUpdateHostIommuStateMsg",
                            "org.zstack.pciDevice.APIGetPciDeviceCandidatesForNewCreateVmMsg",
                            "org.zstack.pciDevice.APIDetachPciDeviceFromVmMsg",
                            "org.zstack.pciDevice.APIQueryPciDeviceMsg",
                            "org.zstack.pciDevice.APIGetPciDeviceCandidatesForAttachingVmMsg"]}]
        cond = res_ops.gen_query_conditions('name', '=', "predefined: pci-device")
        cond = res_ops.gen_query_conditions('type', '=', "predefined", cond)
    if flavor['target_role'] == 'zwatch':
        statements = [{"effect": "Allow", "actions": ["org.zstack.zwatch.**",
                            "org.zstack.sns.**"]}]
        cond = res_ops.gen_query_conditions('name', '=', "predefined: zwatch")
        cond = res_ops.gen_query_conditions('type', '=', "predefined", cond)
    if flavor['target_role'] == 'sns':
        statements = [{"effect": "Allow", "actions": ["org.zstack.sns.**"]}]
        cond = res_ops.gen_query_conditions('name', '=', "predefined: sns")
        cond = res_ops.gen_query_conditions('type', '=', "predefined", cond)

    #role_uuid = iam2_ops.create_role('test_role', statements).uuid
    role_uuid = res_ops.query_resource(res_ops.ROLE, cond)[0].uuid

    #iam2_ops.add_policy_statements_to_role(role_uuid, statements)
    #statement_uuid = iam2_ops.get_policy_statement_uuid_of_role(role_uuid, action)
    #iam2_ops.remove_policy_statements_from_role(role_uuid, [statement_uuid])

    iam2_ops.add_roles_to_iam2_virtual_id([role_uuid], policy_check_vid.get_vid().uuid)
    policy_check_vid.set_vid_statements(statements)
    policy_check_vid.check()
    #iam2_ops.remove_roles_from_iam2_virtual_id([role_uuid], policy_check_vid.get_vid().uuid)
    #policy_check_vid.set_vid_statements([])
    #policy_check_vid.check()

    iam2_ops.delete_iam2_project(project_uuid)
    #vid.delete()
    #vid1.delete()
    #vid2.delete()
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
