'''
IAM2 Vid Attribute Checker.
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.header.checker as checker_header
import zstackwoodpecker.operations.iam2_operations as iam2_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.operations.image_operations as image_ops
import zstackwoodpecker.operations.volume_operations as volume_ops
import zstackwoodpecker.operations.affinitygroup_operations as ag_ops
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.operations.scheduler_operations as schd_ops
import zstackwoodpecker.operations.zwatch_operations as zwt_ops
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.test_lib as test_lib
import os

class zstack_vid_attr_checker(checker_header.TestChecker):
    def __init__(self):
        super(zstack_vid_attr_checker, self).__init__()

    def check_login(self, username, password):
        try:
            session_uuid = iam2_ops.login_iam2_virtual_id(username, password)
        except:
            test_util.test_logger('Check Result: [Virtual ID:] %s login failed' % username)
            return self.judge(False)

    def check_platform_admin_permission(self, username, password):
        session_uuid = iam2_ops.login_iam2_virtual_id(username, password)
        #Check if have permission to create project 
        try:
            project_uuid = iam2_ops.create_iam2_project(name='platform_admin_create_project_permission_check', session_uuid=session_uuid).uuid
            iam2_ops.delete_iam2_project(project_uuid, session_uuid=session_uuid)
        except:
            test_util.test_logger('Check Result: [Virtual ID:] %s is Platform Admin, but create project failed' % username)
            return self.judge(False)

    def check_project_admin_permission(self, username, password):
        session_uuid = iam2_ops.login_iam2_virtual_id(username, password)
        #Check if have permission to create project
        #try:
        #    project_uuid = iam2_ops.create_iam2_project(name='porject_admin_create_project_permission_check', session_uuid=session_uuid).uuid
        #    iam2_ops.delete_iam2_project(project_uuid, session_uuid=session_uuid)
        #    test_util.test_logger('Check Result: [Virtual ID:] %s is Porject Admin, but is able to create project' % username)
        #    return self.judge(False)
        #except KeyError as e:
        #    print e

        #Check if have permission to setup project operator
        try:
            project_operator_uuid = iam2_ops.create_iam2_virtual_id(name='project_admin_change_project_operator_permission_check', password='b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86').uuid
            project_uuid = ''
            for lst in self.test_obj.get_vid_attributes():
                if lst['name'] == '__ProjectAdmin__':
                    project_uuid = lst['value']
            if project_uuid != '':
                iam2_ops.add_iam2_virtual_ids_to_project([project_operator_uuid], project_uuid)
                attributes = [{"name": "__ProjectOperator__", "value": project_uuid}]
                conditions = res_ops.gen_query_conditions('uuid', '=', project_uuid)
                project_name = res_ops.query_resource(res_ops.IAM2_PROJECT, conditions)[0].name
                session_uuid = iam2_ops.login_iam2_project(project_name, session_uuid=session_uuid).uuid
                iam2_ops.add_attributes_to_iam2_virtual_id(project_operator_uuid, attributes, session_uuid=session_uuid)
            iam2_ops.delete_iam2_virtual_id(project_operator_uuid)
        except KeyError as e:
            test_util.test_logger('Check Result: [Virtual ID:] %s is Project Admin, but setup project operator failed' % username)
            return self.judge(False)
        return self.judge(True)

    def check_project_operator_permission(self, username, password):
        session_uuid = iam2_ops.login_iam2_virtual_id(username, password)
        #Check if have permission to setup project operator
        #try:
        #    project_operator_uuid = iam2_ops.create_iam2_virtual_id(name='project_admin_create_project_operator_permission_check', password='b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86', attributes=[{"name":"__ProjectOperator__"}], session_uuid=session_uuid).uuid
        #    test_util.test_logger('Check Result: [Virtual ID:] %s is Porject Operator, but is able to create other project operator' % username)
        #    iam2_ops.delete_iam2_virtual_id(project_operator_uuid, session_uuid=session_uuid)
        #    return self.judge(False)
        #except:
        #    pass

        #Check if have permission to add virtual id to project
        normal_user_uuid = iam2_ops.create_iam2_virtual_id(name='project_operator_add_virtual_add_to_project_permission_check', password='b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86').uuid
        try:
            project_uuid = ''
            for lst in self.test_obj.get_vid_attributes():
                if lst['name'] == '__ProjectOperator__':
                    project_uuid = lst['value']
            if project_uuid != '':
                conditions = res_ops.gen_query_conditions('uuid', '=', project_uuid)
                project_name = res_ops.query_resource(res_ops.IAM2_PROJECT, conditions)[0].name
                session_uuid = iam2_ops.login_iam2_project(project_name, session_uuid=session_uuid).uuid
                iam2_ops.add_iam2_virtual_ids_to_project([normal_user_uuid], project_uuid)

            iam2_ops.delete_iam2_virtual_id(normal_user_uuid)

        except KeyError as e:
            test_util.test_logger('Check Result: [Virtual ID:] %s is Project Operator, but add user to project failed' % username)
            return self.judge(False)
        return self.judge(True)

    def check(self):
        super(zstack_vid_attr_checker, self).check()
        password = 'b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86'
        virtual_id = self.test_obj.get_vid()
        self.check_login(virtual_id.name, password)
        for lst in self.test_obj.get_vid_attributes():
            if lst['name'] == '__PlatformAdmin__':
                self.check_platform_admin_permission(virtual_id.name, password)
            elif lst['name']  == '__ProjectAdmin__':
                self.check_project_admin_permission(virtual_id.name, password)
            elif lst['name']  == '__ProjectOperator__':
                self.check_project_operator_permission(virtual_id.name, password)
        return self.judge(True)

class zstack_vid_policy_checker(checker_header.TestChecker):
    def __init__(self):
        self.password = 'b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86'
        super(zstack_vid_policy_checker, self).__init__()

    def check_login(self, username, password):
        try:
            virtual_id = self.test_obj.get_vid()
            conditions = res_ops.gen_query_conditions('virtualIDs.uuid', '=', virtual_id.uuid)
            project_name = res_ops.query_resource(res_ops.IAM2_PROJECT, conditions)[0].name
            plain_user_session_uuid = iam2_ops.login_iam2_virtual_id(username, password)
            iam2_ops.login_iam2_project(project_name, plain_user_session_uuid)
        except:
            test_util.test_logger('Check Result: [Virtual ID:] %s login failed' % username)
            return self.judge(False)

    def check_vm_operation(self):
        virtual_id = self.test_obj.get_vid()
        plain_user_session_uuid = iam2_ops.login_iam2_virtual_id(virtual_id.name, self.password)
        conditions = res_ops.gen_query_conditions('virtualIDs.uuid', '=',virtual_id.uuid)
        project_ins = res_ops.query_resource(res_ops.IAM2_PROJECT, conditions)[0]
        project_login_session_uuid = iam2_ops.login_iam2_project(project_ins.name, plain_user_session_uuid).uuid
        project_linked_account_uuid = project_ins.linkedAccountUuid
        try:
            vm_creation_option = test_util.VmOption()
            l3_net_uuid = res_ops.query_resource(res_ops.L3_NETWORK)[0].uuid
            acc_ops.share_resources([project_linked_account_uuid], [l3_net_uuid])
            vm_creation_option.set_l3_uuids([l3_net_uuid])
            image_uuid = res_ops.query_resource(res_ops.IMAGE)[0].uuid
            vm_creation_option.set_image_uuid(image_uuid)
            acc_ops.share_resources([project_linked_account_uuid], [image_uuid])
            instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING)[0].uuid 
            vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
            acc_ops.share_resources([project_linked_account_uuid], [instance_offering_uuid])
            vm_creation_option.set_name('vm_policy_checker')
            vm_creation_option.set_session_uuid(project_login_session_uuid)
            vm = vm_ops.create_vm(vm_creation_option)
            vm_uuid = vm.uuid
            # VM related ops: Create, Delete, Expunge, Start, Stop, Suspend, Resume, Migrate
            vm_ops.stop_vm(vm_uuid, session_uuid=project_login_session_uuid)
            vm_ops.start_vm(vm_uuid, session_uuid=project_login_session_uuid)
            candidate_hosts = vm_ops.get_vm_migration_candidate_hosts(vm_uuid)
            if candidate_hosts != None and test_lib.lib_check_vm_live_migration_cap(vm):
                vm_ops.migrate_vm(vm_uuid, candidate_hosts.inventories[0].uuid, session_uuid=project_login_session_uuid)
            vm_ops.stop_vm(vm_uuid, force='cold', session_uuid=project_login_session_uuid)
            vm_ops.start_vm(vm_uuid, session_uuid=project_login_session_uuid)
            vm_ops.suspend_vm(vm_uuid, session_uuid=project_login_session_uuid)
            vm_ops.resume_vm(vm_uuid, session_uuid=project_login_session_uuid)
            vm_ops.destroy_vm(vm_uuid, session_uuid=project_login_session_uuid)
            vm_ops.expunge_vm(vm_uuid, session_uuid=project_login_session_uuid)
        except Exception as e:
            test_util.test_logger('Check Result: [Virtual ID:] %s has permission for vm but vm check failed' % virtual_id.name)    
            test_util.test_logger('Excepiton info: %s' %e)
            return self.judge(False)
        return self.judge(True)

    def check_vm_operation_without_create_permission(self):
        virtual_id = self.test_obj.get_vid()
        plain_user_session_uuid = iam2_ops.login_iam2_virtual_id(virtual_id.name, self.password)
        conditions = res_ops.gen_query_conditions('virtualIDs.uuid', '=',virtual_id.uuid)
        project_ins = res_ops.query_resource(res_ops.IAM2_PROJECT, conditions)[0]
        project_login_session_uuid = iam2_ops.login_iam2_project(project_ins.name, plain_user_session_uuid).uuid
        project_linked_account_uuid = project_ins.linkedAccountUuid
        try:
            vm_create_option = test_util.VmOption()
            vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
            vm_creation_option.set_image_uuid(image_uuid)
            vm_creation_option.set_l3_uuids([l3net_uuid])
            vm_creation_option.set_session_uuid(session_uuid)
            vm_uuid = vm_ops.create_vm(vm_creation_option).uuid
            vm_ops.destroy_vm(vm_uuid, session_uuid=session_uuid)
        except e:
            if e.find('permission') != -1:
                test_util.test_logger('Check Result: [Virtual ID:] %s has permission for vm except creation but vm check failed' % virtual_id.name)
                test_util.test_logger('Excepiton info: %s' %e)
                return self.judge(True)
            return self.judge(False)
        return self.judge(False)

    def check_image_operation(self):
        virtual_id = self.test_obj.get_vid()
        plain_user_session_uuid = iam2_ops.login_iam2_virtual_id(virtual_id.name, self.password)
        conditions = res_ops.gen_query_conditions('virtualIDs.uuid', '=',virtual_id.uuid)
        project_ins = res_ops.query_resource(res_ops.IAM2_PROJECT, conditions)[0]
        project_login_session_uuid = iam2_ops.login_iam2_project(project_ins.name, plain_user_session_uuid).uuid
        project_linked_account_uuid = project_ins.linkedAccountUuid

        try:
            bs = res_ops.query_resource(res_ops.BACKUP_STORAGE)[0]
            image_option = test_util.ImageOption()
            image_option.set_name('image_policy_checker')
            image_option.set_description('image for policy check')
            image_option.set_format('raw')
            image_option.set_mediaType('RootVolumeTemplate')
            image_option.set_backup_storage_uuid_list([bs.uuid])
            image_option.url = "http://fake_iamge/image.raw"
            image_option.set_session_uuid(project_login_session_uuid)
            image_uuid = img_ops.add_image(image_option).uuid
            img_ops.sync_image_size(image_uuid, session_uuid=project_login_session_uuid)
            img_ops.change_image_state(image_uuid, 'disable', session_uuid=project_login_session_uuid)
            img_ops.change_image_state(image_uuid, 'enable', session_uuid=project_login_session_uuid)
            if bs.type == 'ImageStoreBackupStorage':
                img_ops.export_image_from_backup_storage(image_uuid, bs.uuid, session_uuid=project_login_session_uuid)
                img_ops.delete_exported_image_from_backup_storage(image_uuid, bs.uuid, session_uuid=project_login_session_uuid)
            img_ops.set_image_qga_enable(image_uuid, session_uuid=project_login_session_uuid)
            img_ops.set_image_qga_disable(image_uuid, session_uuid=project_login_session_uuid)
            cond = res_ops.gen_query_conditions('name', '=', "image_policy_checker")
            image = res_ops.query_resource(res_ops.IMAGE, cond, session_uuid=project_login_session_uuid)
            if image == None:
                test_util.test_fail('fail to query image just added')
                return self.judge(False)
            img_ops.delete_image(image_uuid, session_uuid=project_login_session_uuid)
            img_ops.expunge_image(image_uuid, session_uuid=project_login_session_uuid)
        except Exception as e:
            test_util.test_logger('Check Result: [Virtual ID:] %s has permission for image but image check failed' % virtual_id.name)
            test_util.test_logger('Excepiton info: %s' %e)
            return self.judge(False)
        return self.judge(True)

    def check_snapshot(self):
        session_uuid = iam2_ops.login_iam2_virtual_id(username, password)
        iam2_ops.login_iam2_project(project_name, session_uuid=session_uuid)
        try:
            snapshot_option = test_util.SnapshotOption()
            snapshot_uuid = volume_ops.create_snapshot(snapshot_option).uuid
            volume_ops.delete_snapshot(snapshot_uuid, session_uuid=session_uuid)
        except e:
            if e.find('permission') != -1:
                test_util.test_logger('Check Result: [Virtual ID:] %s has permission to create snapshot but creation failed' % username)
                return self.judge(False)
        return self.judge(True)

    def check_volume_operation(self):
        session_uuid = iam2_ops.login_iam2_virtual_id(username, password)
        iam2_ops.login_iam2_project(project_name, session_uuid=session_uuid)
        try:
            volume_option = test_util.VolumeOption()
            volume_uuid = volume_ops.create_volume_from_offering(volume_option).uuid
            volume_ops.delete_volume(volume_uuid, session_uuid=session_uuid)
        except e:
            if e.find('permission') != -1:
                test_util.test_logger('Check Result: [Virtual ID:] %s has  permission to create volume but creation failed' % username)
                return self.judge(False)
        return self.judge(True)

    def check_affinity_group(self):
        session_uuid = iam2_ops.login_iam2_virtual_id(username, password)
        iam2_ops.login_iam2_project(project_name, session_uuid=session_uuid)
        try:
            ag_uuid = ag_ops.create_affinity_group('affinity_group_role_checker', 'soft', session_uuid=session_uuid).uuid
            ag_ops.delete_affinity_group(ag_uuid, session_uuid=session_uuid)
        except e:
            if e.find('permission') != -1:
                test_util.test_logger('Check Result: [Virtual ID:] %s has permission to create affinity group but creation failed' % username)
                return self.judge(False)
        return self.judge(True)

    def check_networks(self):
        session_uuid = iam2_ops.login_iam2_virtual_id(username, password)
        iam2_ops.login_iam2_project(project_name, session_uuid=session_uuid)
        try:
            l2_uuid = ''
            l3_uuid = net_ops.create_ls('l3_network_role_check', l2_uuid, session_uuid=session_uuid).uuid
            net_ops.delete_l3(l3_uuid, session_uuid=session_uuid)
        except e:
            if e.find('permission') != -1:
                test_util.test_logger('Check Result: [Virtual ID:] %s has permission to create l3 network but creation failed' % username)
                return self.judge(False)
        return self.judge(True)

    def check_eip(self):
        session_uuid = iam2_ops.login_iam2_virtual_id(username, password)
        iam2_ops.login_iam2_project(project_name, session_uuid=session_uuid)
        try:
            eip_creation_option = test_util.EipOption()
            eip_uuid = net_ops.create_eip(eip_creation_option).inventory.uuid
            net_ops.delete_eip(eip_uuid, session_uuid=session_uuid)
        except e:
            if e.find('permission') != -1:
                test_util.test_logger('Check Result: [Virtual ID:] %s has permission to create eip but creation failed' % username)
                return self.judge(False)
        return self.judge(True)

    def check_security_group(self):
        session_uuid = iam2_ops.login_iam2_virtual_id(username, password)
        iam2_ops.login_iam2_project(project_name, session_uuid=session_uuid)
        try:
            sg_creation_option = test_util.SecurityGroupOption()
            sg_uuid = net_ops.create_security_group(sg_creation_option).uuid
            net_ops.delete_security_group(sg_uuid, session_uuid=session_uuid)
        except e:
            if e.find('permission') != -1:
                test_util.test_logger('Check Result: [Virtual ID:] %s has permission to create security group but creation failed' % username)
                return self.judge(False)
        return self.judge(True)

    def check_load_balancer(self):
        session_uuid = iam2_ops.login_iam2_virtual_id(username, password)
        iam2_ops.login_iam2_project(project_name, session_uuid=session_uuid)
        try:
            vip_creation_option = test_util.LoadBalancerListenerOption()
            vip_uuid = net_ops.create_vip()
            lb_uuid = net_ops.create_load_balancer(vip_uuid, 'load_balancer_role_check').uuid
            net_ops.delete_load_balancer(lb_uuid, session_uuid=session_uuid)
        except e:
            if e.find('permission') != -1:
                test_util.test_logger('Check Result: [Virtual ID:] %s has permission to create load balancer but creation failed' % username)
                return self.judge(False)
        return self.judge(True)

    def check_port_forwarding(self):
        session_uuid = iam2_ops.login_iam2_virtual_id(username, password)
        iam2_ops.login_iam2_project(project_name, session_uuid=session_uuid)
        try:
            pf_rule_creation_option = test_util.PortForwardingRuleOption()
            pf_uuid = net_ops.create_port_forwarding(pf_rule_creation_option).uuid
            net_ops.delete_port_forwarding(pf_uuid, session_uuid=session_uuid)
        except e:
            if e.find('permission') != -1:
                test_util.test_logger('Check Result: [Virtual ID:] %s has permission to create port forwarding but creation failed' % username)
                return self.judge(False)
        return self.judge(True)

    def check_scheduler(self):
        session_uuid = iam2_ops.login_iam2_virtual_id(username, password)
        iam2_ops.login_iam2_project(project_name, session_uuid=session_uuid)
        try:
            description = 'scheduler_role_check'
            target_uuid = ''
            type = ''
            parameters = ''
            schd_uuid = schd_ops.create_scheduler_job('scheduler_role_check', description, target_uuid, type, parameters, session_uuid=session_uuid).uuid
            net_ops.del_scheduler_job(schd_uuid, session_uuid=session_uuid)
        except e:
            if e.find('permission') != -1:
                test_util.test_logger('Check Result: [Virtual ID:] %s has permission to create scheduler but creation failed' % username)
                return self.judge(False)
        return self.judge(True)
    def check_pci(self):
        pass

    def check_zwatch(self):
        session_uuid = iam2_ops.login_iam2_virtual_id(username, password)
        iam2_ops.login_iam2_project(project_name, session_uuid=session_uuid)
        try:
            comparison_operator = ''
            period = ''
            threshold = ''
            namespace = ''
            metric_name = ''
            alarm_uuid = zwt_ops.create_alarm(comparison_operator, period, threshold, namespace, metric_name, session_uuid=session_uuid)
            zwt_ops.delete_alarm(alarm_uuid, session_uuid=session_uuid)
        except e:
            if e.find('permission') != -1:
                test_util.test_logger('Check Result: [Virtual ID:] %s has permission to create alarm but creation failed' % username)
                return self.judge(False)
        return self.judge(True)

    def check_sns(self):
        session_uuid = iam2_ops.login_iam2_virtual_id(username, password)
        iam2_ops.login_iam2_project(project_name, session_uuid=session_uuid)
        try:
            endpoint_uuid = zwt_ops.create_sns_http_endpoint('http://test.checker', 'endpoint_role_check', session_uuid=session_uuid)
            zwt_ops.delete_sns_application_endpoint(endpoint_uuid, session_uuid=session_uuid)
        except e:
            if e.find('permission') != -1:
                test_util.test_logger('Check Result: [Virtual ID:] %s has permission to create endpoint but creation failed' % username)
                return self.judge(False)
        return self.judge(True)

    def check(self):
        super(zstack_vid_policy_checker, self).check()
        password = 'b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86'
        virtual_id = self.test_obj.get_vid()
        self.check_login(virtual_id.name, password)
        actions = self.test_obj.get_vid_statements()[0]['actions']
        if 'org.zstack.header.vm.**' in actions and 'org.zstack.ha.**' in actions:
            self.check_vm_operation()
        if 'org.zstack.header.image.**' in actions and 'org.zstack.storage.backup.imagestore.APIGetImagesFromImageStoreBackupStorageMsg' in actions:
            self.check_image_operation()
        if 'org.zstack.header.volume.APICreateDataVolumeFromVolumeTemplateMsg' in actions and 'org.zstack.header.volume.APIGetVolumeQosMsg' in actions and 'org.zstack.header.volume.APISyncVolumeSizeMsg' in actions and 'org.zstack.header.volume.APICreateDataVolumeFromVolumeSnapshotMsg' in actions:
            self.check_volume_operation()
        if 'org.zstack.header.vm.**' not in actions and 'org.zstack.header.vm.APIGetVmQgaMsg' in actions and 'org.zstack.header.vm.APIChangeVmImageMsg' in actions and 'org.zstack.header.vm.APISetVmSshKeyMsg' in actions and 'org.zstack.header.vm.APIStopVmInstanceMsg' in actions and 'org.zstack.header.vm.APISetVmStaticIpMsg' in actions:
            self.check_vm_operation_without_create_permission()
        if 'org.zstack.header.storage.snapshot.**' in actions and 'org.zstack.header.volume.APICreateVolumeSnapshotMsg' in actions:
            self.check_snapshot()
        if 'org.zstack.header.affinitygroup.**' in actions:
            self.check_affinity_group()
        if 'org.zstack.header.network.l3.**' in actions and 'org.zstack.network.service.flat.**' in actions and 'org.zstack.header.network.l2.APIUpdateL2NetworkMsg' in actions:
            self.check_networks()
        if 'org.zstack.network.service.vip.**' in actions and 'org.zstack.network.service.eip.**' in actions and 'org.zstack.header.vipQos.**' in actions:
            self.check_eip()
        if 'org.zstack.network.securitygroup.**' in actions:
            self.check_security_group()
        if 'org.zstack.network.service.lb.**' in actions and 'org.zstack.network.service.vip.**' in actions and 'org.zstack.header.vipQos.**' in actions:
            self,check_load_balancer()
        if 'org.zstack.network.service.portforwarding.**' in actions and 'org.zstack.network.service.vip.**' in actions and 'org.zstack.header.vipQos.**' in actions:
            self.check_port_forwarding()
        if 'org.zstack.scheduler.**' in actions:
            self.check_scheduler()
        if 'org.zstack.pciDevice.APIAttachPciDeviceToVmMsg' in actions and 'org.zstack.pciDevice.APIUpdateHostIommuStateMsg' in actions:
            self.check_pci()
        if 'org.zstack.zwatch.**' in actions and 'org.zstack.sns.**' in actions:
            self.check_zwatch()
        if 'org.zstack.sns.**' in actions:
            self.check_sns()  
        return self.judge(True)
'''
            if lst == 'org.zstack.header.vm.**':
                self.check_vm_operation():
            if lst == 'org.zstack.ipsec.**' and lst ==

            if lst == 'org.zstack.header.image.**' and lst == 'org.zstack.storage.backup.imagestore.APIGetImagesFromImageStoreBackupStorageMsg':
            if lst == 'org.zstack.header.network.l3.**'
            if lst == 'org.zstack.header.affinitygroup.**':
            if role.type == 'CreatedBySystem':
                if role.name == 'predefined: vm':
                    self.check_role_vm()
                elif role.name == 'predefined: vm-operation-without-create-permission':
                    self.check_role_vm_without_create()
                elif role.name == 'predefined: image':
                    self.check_role_image()
                elif role.name == 'predefined: snapshot':
                    self.check_role_snapshot()
                elif role.name == 'predefined: volume':
                    self.check_role_volume()
                elif role.name == 'predefined: affinity-group':
                    self.check_role_affinity_group()
                elif role.name == 'predefined: networks':
                    self.check_role_networks()
                elif role.name == 'predefined: eip':
                    self.check_role_eip()
                elif role.name == 'predefined: security-group':
                    self.check_role_sg()
                elif role.name == 'predefined: load-balancer':
                    self.check_role_lb()
                elif role.name == 'predefined: port-forwarding':
                    self.check_role_pf()
                elif role.name == 'predefined: scheduler':
                    self.check_scheduler()
                elif role.name == 'predefined: pci-device':
                    self.check_role_pci()
                elif role.name == 'predefined: zwatch':
                    self.check_role_zwatch()
                elif role.name == 'predefined: sns':
                    self.check_role_sns()
                else:
                    test_util.test_logger('The role is not predifined role, unable to check')
        return self.judge(True)
'''
