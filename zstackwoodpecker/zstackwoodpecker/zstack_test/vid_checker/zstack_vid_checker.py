'''
IAM2 Vid Attribute Checker.
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.header.checker as checker_header
import zstackwoodpecker.operations.iam2_operations as iam2_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.operations.affinitygroup_operations as ag_ops
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.operations.vxlan_operations as vxlan_ops
import zstackwoodpecker.operations.scheduler_operations as schd_ops
import zstackwoodpecker.operations.zwatch_operations as zwt_ops
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.test_lib as test_lib
import time
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
            conditions = res_ops.gen_query_conditions('system', '=', 'false')
            conditions = res_ops.gen_query_conditions('category', '=', 'Private', conditions)
            l3_net_uuid = res_ops.query_resource(res_ops.L3_NETWORK, conditions)[0].uuid
            acc_ops.share_resources([project_linked_account_uuid], [l3_net_uuid])
            vm_creation_option.set_l3_uuids([l3_net_uuid])
            conditions = res_ops.gen_query_conditions('platform', '=', 'Linux')
            conditions = res_ops.gen_query_conditions('system', '=', 'false', conditions)
            image_uuid = res_ops.query_resource(res_ops.IMAGE, conditions)[0].uuid
            vm_creation_option.set_image_uuid(image_uuid)
            acc_ops.share_resources([project_linked_account_uuid], [image_uuid])
            conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
            instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid
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
            vm_creation_option = test_util.VmOption()
            conditions = res_ops.gen_query_conditions('system', '=', 'false')
            conditions = res_ops.gen_query_conditions('category', '=', 'Private', conditions)
            l3_net_uuid = res_ops.query_resource(res_ops.L3_NETWORK, conditions)[0].uuid
            acc_ops.share_resources([project_linked_account_uuid], [l3_net_uuid])
            vm_creation_option.set_l3_uuids([l3_net_uuid])
            conditions = res_ops.gen_query_conditions('platform', '=', 'Linux')
            conditions = res_ops.gen_query_conditions('system', '=', 'false', conditions)
            image_uuid = res_ops.query_resource(res_ops.IMAGE, conditions)[0].uuid
            vm_creation_option.set_image_uuid(image_uuid)
            acc_ops.share_resources([project_linked_account_uuid], [image_uuid])
            conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
            instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid
            vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
            acc_ops.share_resources([project_linked_account_uuid], [instance_offering_uuid])
            vm_creation_option.set_name('vm_without_create_policy_checker')
            vm = vm_ops.create_vm(vm_creation_option)
            vm_uuid = vm.uuid
            res_ops.change_recource_owner(project_linked_account_uuid, vm_uuid)
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
            test_util.test_logger('Check Result: [Virtual ID:] %s has permission for vm except creation but vm check failed' % virtual_id.name)
            test_util.test_logger('Excepiton info: %s' %e)
            return self.judge(False)
        return self.judge(True)

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
        virtual_id = self.test_obj.get_vid()
        plain_user_session_uuid = iam2_ops.login_iam2_virtual_id(virtual_id.name, self.password)
        conditions = res_ops.gen_query_conditions('virtualIDs.uuid', '=',virtual_id.uuid)
        project_ins = res_ops.query_resource(res_ops.IAM2_PROJECT, conditions)[0]
        project_login_session_uuid = iam2_ops.login_iam2_project(project_ins.name, plain_user_session_uuid).uuid
        project_linked_account_uuid = project_ins.linkedAccountUuid

        try:
            bs = res_ops.query_resource(res_ops.BACKUP_STORAGE)[0]
            disk_offering_uuid = res_ops.query_resource(res_ops.DISK_OFFERING)[0].uuid
            acc_ops.share_resources([project_linked_account_uuid], [disk_offering_uuid])
            volume_option = test_util.VolumeOption()
            volume_option.set_disk_offering_uuid(disk_offering_uuid)
            volume_option.set_name('data_volume_for_snapshot_policy_checker')
            data_volume = vol_ops.create_volume_from_offering(volume_option)
            res_ops.change_recource_owner(project_linked_account_uuid, data_volume.uuid)

            vm_creation_option = test_util.VmOption()
            conditions = res_ops.gen_query_conditions('system', '=', 'false')
            conditions = res_ops.gen_query_conditions('category', '=', 'Private', conditions)
            l3_net_uuid = res_ops.query_resource(res_ops.L3_NETWORK, conditions)[0].uuid
            acc_ops.share_resources([project_linked_account_uuid], [l3_net_uuid])
            vm_creation_option.set_l3_uuids([l3_net_uuid])
            conditions = res_ops.gen_query_conditions('platform', '=', 'Linux')
            conditions = res_ops.gen_query_conditions('system', '=', 'false', conditions)
            image_uuid = res_ops.query_resource(res_ops.IMAGE, conditions)[0].uuid
            vm_creation_option.set_image_uuid(image_uuid)
            acc_ops.share_resources([project_linked_account_uuid], [image_uuid])
            conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
            instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid
            vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
            acc_ops.share_resources([project_linked_account_uuid], [instance_offering_uuid])
            vm_creation_option.set_name('vm_without_create_policy_checker')
            vm = vm_ops.create_vm(vm_creation_option)
            vm_uuid = vm.uuid
            vol_ops.attach_volume(data_volume.uuid, vm_uuid)

            snapshot_option = test_util.SnapshotOption()
            snapshot_option.set_volume_uuid(data_volume.uuid)
            snapshot_option.set_name('snapshot_policy_checker')
            snapshot_option.set_description('snapshot for policy check')
            snapshot_option.set_session_uuid(project_login_session_uuid)
            snapshot_uuid = vol_ops.create_snapshot(snapshot_option).uuid
            vm_ops.stop_vm(vm_uuid, force='cold')
            vol_ops.use_snapshot(snapshot_uuid, project_login_session_uuid)
            #vol_ops.backup_snapshot(snapshot_uuid, bs.uuid, project_login_session_uuid)
            #new_volume = vol_ops.create_volume_from_snapshot(snapshot_uuid)
            #vol_ops.delete_snapshot_from_backupstorage(snapshot_uuid, [bs.uuid], session_uuid=project_login_session_uuid)
            vol_ops.delete_snapshot(snapshot_uuid, project_login_session_uuid)
            vol_ops.delete_volume(data_volume.uuid)
            vol_ops.expunge_volume(data_volume.uuid)
            vm_ops.destroy_vm(vm_uuid)
            vm_ops.expunge_vm(vm_uuid)

        except Exception as e:
            test_util.test_logger('Check Result: [Virtual ID:] %s has permission for snapshot but snapshot check failed' % virtual_id.name)
            test_util.test_logger('Excepiton info: %s' %e)
            return self.judge(False)
        return self.judge(True)

    def check_volume_operation(self):
        virtual_id = self.test_obj.get_vid()
        plain_user_session_uuid = iam2_ops.login_iam2_virtual_id(virtual_id.name, self.password)
        conditions = res_ops.gen_query_conditions('virtualIDs.uuid', '=',virtual_id.uuid)
        project_ins = res_ops.query_resource(res_ops.IAM2_PROJECT, conditions)[0]
        project_login_session_uuid = iam2_ops.login_iam2_project(project_ins.name, plain_user_session_uuid).uuid
        project_linked_account_uuid = project_ins.linkedAccountUuid

        try:
            # Volume related ops: Create, Delete, Expunge, Attach, Dettach, Enable, Disable
            disk_offering_uuid = res_ops.query_resource(res_ops.DISK_OFFERING)[0].uuid
            acc_ops.share_resources([project_linked_account_uuid], [disk_offering_uuid])
            volume_option = test_util.VolumeOption()
            volume_option.set_disk_offering_uuid(disk_offering_uuid)
            volume_option.set_name('data_volume_policy_checker')
            volume_option.set_session_uuid(project_login_session_uuid)
            data_volume = vol_ops.create_volume_from_offering(volume_option)
            vol_ops.stop_volume(data_volume.uuid, session_uuid=project_login_session_uuid)
            vol_ops.start_volume(data_volume.uuid, session_uuid=project_login_session_uuid)
            vm_creation_option = test_util.VmOption()
            conditions = res_ops.gen_query_conditions('system', '=', 'false')
            conditions = res_ops.gen_query_conditions('category', '=', 'Private', conditions)
            l3_net_uuid = res_ops.query_resource(res_ops.L3_NETWORK, conditions)[0].uuid
            acc_ops.share_resources([project_linked_account_uuid], [l3_net_uuid])
            vm_creation_option.set_l3_uuids([l3_net_uuid])
            conditions = res_ops.gen_query_conditions('platform', '=', 'Linux')
            conditions = res_ops.gen_query_conditions('system', '=', 'false', conditions)
            image_uuid = res_ops.query_resource(res_ops.IMAGE, conditions)[0].uuid
            vm_creation_option.set_image_uuid(image_uuid)
            acc_ops.share_resources([project_linked_account_uuid], [image_uuid])
            conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
            instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid
            vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
            acc_ops.share_resources([project_linked_account_uuid], [instance_offering_uuid])
            vm_creation_option.set_name('vm_for_vol_policy_checker')
            #vm_creation_option.set_session_uuid(project_login_session_uuid)
            vm = vm_ops.create_vm(vm_creation_option)
            vm_uuid = vm.uuid
            res_ops.change_recource_owner(project_linked_account_uuid, vm_uuid)
            vol_ops.attach_volume(data_volume.uuid, vm_uuid, session_uuid=project_login_session_uuid)
            vol_ops.detach_volume(data_volume.uuid, vm_uuid, session_uuid=project_login_session_uuid)
            vol_ops.delete_volume(data_volume.uuid, session_uuid=project_login_session_uuid)
            vol_ops.expunge_volume(data_volume.uuid, session_uuid=project_login_session_uuid)
            vm_ops.destroy_vm(vm_uuid)
            vm_ops.expunge_vm(vm_uuid)
            
        except Exception as e:
            test_util.test_logger('Check Result: [Virtual ID:] %s has permission for volume but volume check failed' % virtual_id.name)
            test_util.test_logger('Excepiton info: %s' %e)
            return self.judge(False)
        return self.judge(True)

    def check_affinity_group(self):
        virtual_id = self.test_obj.get_vid()
        plain_user_session_uuid = iam2_ops.login_iam2_virtual_id(virtual_id.name, self.password)
        conditions = res_ops.gen_query_conditions('virtualIDs.uuid', '=',virtual_id.uuid)
        project_ins = res_ops.query_resource(res_ops.IAM2_PROJECT, conditions)[0]
        project_login_session_uuid = iam2_ops.login_iam2_project(project_ins.name, plain_user_session_uuid).uuid
        project_linked_account_uuid = project_ins.linkedAccountUuid
        try:
            vm_creation_option = test_util.VmOption()
            conditions = res_ops.gen_query_conditions('system', '=', 'false')
            conditions = res_ops.gen_query_conditions('category', '=', 'Private', conditions)
            l3_net_uuid = res_ops.query_resource(res_ops.L3_NETWORK, conditions)[0].uuid
            acc_ops.share_resources([project_linked_account_uuid], [l3_net_uuid])
            vm_creation_option.set_l3_uuids([l3_net_uuid])
            conditions = res_ops.gen_query_conditions('platform', '=', 'Linux')
            conditions = res_ops.gen_query_conditions('system', '=', 'false', conditions)
            image_uuid = res_ops.query_resource(res_ops.IMAGE, conditions)[0].uuid
            vm_creation_option.set_image_uuid(image_uuid)
            acc_ops.share_resources([project_linked_account_uuid], [image_uuid])
            conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
            instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid
            vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
            acc_ops.share_resources([project_linked_account_uuid], [instance_offering_uuid])
            vm_creation_option.set_name('vm_for_affinity_group_policy_checker')
            vm = vm_ops.create_vm(vm_creation_option)
            vm_uuid = vm.uuid
            res_ops.change_recource_owner(project_linked_account_uuid, vm_uuid)
            ag_uuid = ag_ops.create_affinity_group('affinity_group_policy_checker', 'antiHard', session_uuid=project_login_session_uuid).uuid
            ag_ops.add_vm_to_affinity_group(ag_uuid, vm_uuid, session_uuid=project_login_session_uuid)
            ag_ops.remove_vm_from_affinity_group(ag_uuid, vm_uuid, session_uuid=project_login_session_uuid)
            ag_ops.delete_affinity_group(ag_uuid, session_uuid=project_login_session_uuid)
            vm_ops.destroy_vm(vm_uuid)
            vm_ops.expunge_vm(vm_uuid)
        except Exception as e:
            test_util.test_logger('Check Result: [Virtual ID:] %s has permission for affinity group but affinity group check failed' % virtual_id.name)
            test_util.test_logger('Excepiton info: %s' %e)
            return self.judge(False)
        return self.judge(True)

    def check_networks(self):
        virtual_id = self.test_obj.get_vid()
        plain_user_session_uuid = iam2_ops.login_iam2_virtual_id(virtual_id.name, self.password)
        conditions = res_ops.gen_query_conditions('virtualIDs.uuid', '=',virtual_id.uuid)
        project_ins = res_ops.query_resource(res_ops.IAM2_PROJECT, conditions)[0]
        project_login_session_uuid = iam2_ops.login_iam2_project(project_ins.name, plain_user_session_uuid).uuid
        project_linked_account_uuid = project_ins.linkedAccountUuid
        try:
            zone_uuid = res_ops.query_resource(res_ops.ZONE)[0].uuid
            vxlan_pool = res_ops.get_resource(res_ops.L2_VXLAN_NETWORK_POOL)
            clear_vxlan_pool = False
            if vxlan_pool == None or len(vxlan_pool) == 0:
                vxlan_pool_uuid = vxlan_ops.create_l2_vxlan_network_pool('vxlan_poll_for networks_polocy_checker', zone_uuid).uuid
                vni_uuid = vxlan_ops.create_vni_range('vni_range_for_networks_policy_checker', '10000', '20000', vxlan_pool_uuid).uuid
                clear_vxlan_pool = True
            else:
                vxlan_pool_uuid = vxlan_pool[0].uuid
            acc_ops.share_resources([project_linked_account_uuid], [vxlan_pool_uuid])
            vxlan_pool_uuid = res_ops.get_resource(res_ops.L2_VXLAN_NETWORK_POOL, session_uuid=project_login_session_uuid)[0].uuid
            vxlan_l2_uuid = vxlan_ops.create_l2_vxlan_network('vxlan_for_policy_checker', vxlan_pool_uuid, zone_uuid, session_uuid=project_login_session_uuid).uuid
            conditions = res_ops.gen_query_conditions('name', '=', 'vrouter')
            service_providor_uuid = res_ops.query_resource(res_ops.NETWORK_SERVICE_PROVIDER, conditions, session_uuid=project_login_session_uuid)[0].uuid
            l3_uuid = net_ops.create_l3('l3_network_for_policy_checker', vxlan_l2_uuid, session_uuid=project_login_session_uuid).uuid
            net_ops.attach_network_service_to_l3network(l3_uuid, service_providor_uuid, session_uuid=project_login_session_uuid)
            #net_ops.detach_network_service_from_l3network(l3_uuid, service_providor_uuid, session_uuid=project_login_session_uuid)
            net_ops.delete_l3(l3_uuid, session_uuid=project_login_session_uuid)
            if clear_vxlan_pool:
                vxlan_ops.delete_vni_range(vni_uuid, session_uuid=project_login_session_uuid)
            net_ops.delete_l2(vxlan_l2_uuid, session_uuid=project_login_session_uuid)
        except Exception as e:
            test_util.test_logger('Check Result: [Virtual ID:] %s has permission for networks but networks check failed' % virtual_id.name)
            test_util.test_logger('Excepiton info: %s' %e)
            return self.judge(False)
        return self.judge(True)

    def check_eip(self):
        virtual_id = self.test_obj.get_vid()
        plain_user_session_uuid = iam2_ops.login_iam2_virtual_id(virtual_id.name, self.password)
        conditions = res_ops.gen_query_conditions('virtualIDs.uuid', '=',virtual_id.uuid)
        project_ins = res_ops.query_resource(res_ops.IAM2_PROJECT, conditions)[0]
        project_login_session_uuid = iam2_ops.login_iam2_project(project_ins.name, plain_user_session_uuid).uuid
        project_linked_account_uuid = project_ins.linkedAccountUuid
        try:
            vm_creation_option = test_util.VmOption()
            conditions = res_ops.gen_query_conditions('category', '=', 'Public')
            l3_pub_uuid = res_ops.query_resource(res_ops.L3_NETWORK, conditions)[0].uuid
            conditions = res_ops.gen_query_conditions('system', '=', 'false')
            conditions = res_ops.gen_query_conditions('category', '=', 'Private', conditions)
            l3_net_uuid = res_ops.query_resource(res_ops.L3_NETWORK, conditions)[0].uuid
            acc_ops.share_resources([project_linked_account_uuid], [l3_pub_uuid, l3_net_uuid])
            vm_creation_option.set_l3_uuids([l3_net_uuid])
            conditions = res_ops.gen_query_conditions('platform', '=', 'Linux')
            conditions = res_ops.gen_query_conditions('system', '=', 'false', conditions)
            image_uuid = res_ops.query_resource(res_ops.IMAGE, conditions)[0].uuid
            vm_creation_option.set_image_uuid(image_uuid)
            acc_ops.share_resources([project_linked_account_uuid], [image_uuid])
            conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
            instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid
            vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
            acc_ops.share_resources([project_linked_account_uuid], [instance_offering_uuid])
            vm_creation_option.set_name('vm_for_eip_policy_checker')
            vm = vm_ops.create_vm(vm_creation_option)
            vm_uuid = vm.uuid
            res_ops.change_recource_owner(project_linked_account_uuid, vm_uuid)
            vip_option = test_util.VipOption()
            vip_option.set_name("vip_for_eip_policy_checker")
            vip_option.set_session_uuid(project_login_session_uuid)
            vip_option.set_l3_uuid(l3_pub_uuid)
            vip = net_ops.create_vip(vip_option) 
            conditions = res_ops.gen_query_conditions('vmInstance.uuid', '=', vm_uuid)
            vm_nic_uuid = res_ops.query_resource(res_ops.VM_NIC, conditions)[0].uuid
            test_util.test_logger('vip creation finished, vm nic uuid is %s' %vm_nic_uuid)
            eip_option = test_util.EipOption()
            eip_option.set_name('eip_policy_checker')
            eip_option.set_session_uuid(project_login_session_uuid)
            eip_option.set_vip_uuid(vip.uuid)
            eip_option.set_vm_nic_uuid(vm_nic_uuid)
            eip = net_ops.create_eip(eip_option)
            net_ops.detach_eip(eip.uuid, session_uuid=project_login_session_uuid)
            net_ops.attach_eip(eip.uuid, vm_nic_uuid, session_uuid=project_login_session_uuid)
            net_ops.delete_eip(eip.uuid)
            net_ops.delete_vip(vip.uuid)
            vm_ops.destroy_vm(vm_uuid)
            vm_ops.expunge_vm(vm_uuid)
            acc_ops.revoke_resources([project_linked_account_uuid], [l3_pub_uuid, l3_net_uuid, image_uuid, instance_offering_uuid])
        except Exception as e:
            test_util.test_logger('Check Result: [Virtual ID:] %s has permission for eip but eip check failed' % virtual_id.name)
            test_util.test_logger('Excepiton info: %s' %e)
            return self.judge(False)
        return self.judge(True)

    def check_security_group(self):
        virtual_id = self.test_obj.get_vid()
        plain_user_session_uuid = iam2_ops.login_iam2_virtual_id(virtual_id.name, self.password)
        conditions = res_ops.gen_query_conditions('virtualIDs.uuid', '=',virtual_id.uuid)
        project_ins = res_ops.query_resource(res_ops.IAM2_PROJECT, conditions)[0]
        project_login_session_uuid = iam2_ops.login_iam2_project(project_ins.name, plain_user_session_uuid).uuid
        project_linked_account_uuid = project_ins.linkedAccountUuid
        try:
            vm_creation_option = test_util.VmOption()
            conditions = res_ops.gen_query_conditions('system', '=', 'false')
            conditions = res_ops.gen_query_conditions('category', '=', 'Private', conditions)
            l3_net_uuid = res_ops.query_resource(res_ops.L3_NETWORK, conditions)[0].uuid
            conditions = res_ops.gen_query_conditions('name', '=', 'SecurityGroup')
            sg_service_providor_uuid = res_ops.query_resource(res_ops.NETWORK_SERVICE_PROVIDER, conditions)[0].uuid
            acc_ops.share_resources([project_linked_account_uuid], [l3_net_uuid])
            conditions = res_ops.gen_query_conditions('l3Network.uuid', '=', l3_net_uuid)
            network_service_list = res_ops.query_resource(res_ops.NETWORK_SERVICE_PROVIDER_L3_REF, conditions)
            sg_service_need_attach = True
            sg_service_need_detach = False
            for service in network_service_list:
                if service.networkServiceType == 'SecurityGroup':
                    sg_service_need_attach = False
            if sg_service_need_attach:
                net_ops.attach_sg_service_to_l3network(l3_net_uuid, sg_service_providor_uuid, session_uuid=project_login_session_uuid)
                sg_service_need_detach = True
            vm_creation_option = test_util.VmOption()
            conditions = res_ops.gen_query_conditions('system', '=', 'false')
            conditions = res_ops.gen_query_conditions('category', '=', 'Private', conditions)
            l3_net_uuid = res_ops.query_resource(res_ops.L3_NETWORK, conditions)[0].uuid
            acc_ops.share_resources([project_linked_account_uuid], [l3_net_uuid])
            vm_creation_option.set_l3_uuids([l3_net_uuid])
            conditions = res_ops.gen_query_conditions('platform', '=', 'Linux')
            conditions = res_ops.gen_query_conditions('system', '=', 'false', conditions)
            image_uuid = res_ops.query_resource(res_ops.IMAGE, conditions)[0].uuid
            vm_creation_option.set_image_uuid(image_uuid)
            acc_ops.share_resources([project_linked_account_uuid], [image_uuid])
            conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
            instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid
            vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
            acc_ops.share_resources([project_linked_account_uuid], [instance_offering_uuid])
            vm_creation_option.set_name('vm_for_security_group_policy_checker')
            vm = vm_ops.create_vm(vm_creation_option)
            vm_uuid = vm.uuid
            res_ops.change_recource_owner(project_linked_account_uuid, vm_uuid)
            sg_creation_option = test_util.SecurityGroupOption()
            sg_creation_option.set_name('security_group_policy_checker')
            sg_creation_option.set_session_uuid(session_uuid=project_login_session_uuid)
            sg_uuid = net_ops.create_security_group(sg_creation_option).uuid
            net_ops.attach_security_group_to_l3(sg_uuid, l3_net_uuid, session_uuid=project_login_session_uuid)
            conditions = res_ops.gen_query_conditions('vmInstance.uuid', '=', vm_uuid)
            vm_nic_uuid = res_ops.query_resource(res_ops.VM_NIC, conditions)[0].uuid
            net_ops.add_nic_to_security_group(sg_uuid, [vm_nic_uuid], session_uuid=project_login_session_uuid)
            net_ops.remove_nic_from_security_group(sg_uuid, [vm_nic_uuid], session_uuid=project_login_session_uuid)
            net_ops.detach_security_group_from_l3(sg_uuid, l3_net_uuid, session_uuid=project_login_session_uuid)
            net_ops.delete_security_group(sg_uuid, session_uuid=project_login_session_uuid)
            vm_ops.destroy_vm(vm_uuid)
            vm_ops.expunge_vm(vm_uuid)
            if sg_service_need_detach:
                net_ops.detach_sg_service_from_l3network(l3_net_uuid, sg_service_providor_uuid, session_uuid=project_login_session_uuid)
            acc_ops.revoke_resources([project_linked_account_uuid], [l3_net_uuid, image_uuid, instance_offering_uuid])

        except Exception as e:
            test_util.test_logger('Check Result: [Virtual ID:] %s has permission for security group but security group check failed' % virtual_id.name)
            test_util.test_logger('Excepiton info: %s' %e)
            return self.judge(False)
        return self.judge(True)

    def check_load_balancer(self):
        virtual_id = self.test_obj.get_vid()
        plain_user_session_uuid = iam2_ops.login_iam2_virtual_id(virtual_id.name, self.password)
        conditions = res_ops.gen_query_conditions('virtualIDs.uuid', '=',virtual_id.uuid)
        project_ins = res_ops.query_resource(res_ops.IAM2_PROJECT, conditions)[0]
        project_login_session_uuid = iam2_ops.login_iam2_project(project_ins.name, plain_user_session_uuid).uuid
        project_linked_account_uuid = project_ins.linkedAccountUuid
        try:
            conditions = res_ops.gen_query_conditions('category', '=', 'Public')
            l3_pub_uuid = res_ops.query_resource(res_ops.L3_NETWORK, conditions)[0].uuid
            vm_creation_option = test_util.VmOption()
            conditions = res_ops.gen_query_conditions('system', '=', 'false')
            conditions = res_ops.gen_query_conditions('category', '=', 'Private', conditions)
            l3_net_uuid = res_ops.query_resource(res_ops.L3_NETWORK, conditions)[0].uuid
            conditions = res_ops.gen_query_conditions('name', '=', 'vrouter')
            service_providor_uuid = res_ops.query_resource(res_ops.NETWORK_SERVICE_PROVIDER, conditions)[0].uuid
            acc_ops.share_resources([project_linked_account_uuid], [l3_pub_uuid, l3_net_uuid])
            conditions = res_ops.gen_query_conditions('l3Network.uuid', '=', l3_net_uuid)
            network_service_list = res_ops.query_resource(res_ops.NETWORK_SERVICE_PROVIDER_L3_REF, conditions)
            lb_service_need_attach = True
            lb_service_need_detach = False
            for service in network_service_list:
                if service.networkServiceType == 'LoadBalancer':
                    lb_service_need_attach = False
            if lb_service_need_attach:
                net_ops.attach_lb_service_to_l3network(l3_net_uuid, service_providor_uuid, session_uuid=project_login_session_uuid)
                lb_service_need_detach = True
            vm_creation_option.set_l3_uuids([l3_net_uuid])
            conditions = res_ops.gen_query_conditions('platform', '=', 'Linux')
            conditions = res_ops.gen_query_conditions('system', '=', 'false', conditions)
            image_uuid = res_ops.query_resource(res_ops.IMAGE, conditions)[0].uuid
            vm_creation_option.set_image_uuid(image_uuid)
            acc_ops.share_resources([project_linked_account_uuid], [image_uuid])
            conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
            instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid
            vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
            acc_ops.share_resources([project_linked_account_uuid], [instance_offering_uuid])
            vm_creation_option.set_name('vm_for_load_balancer_policy_checker')
            vm = vm_ops.create_vm(vm_creation_option)
            vm_uuid = vm.uuid
            res_ops.change_recource_owner(project_linked_account_uuid, vm_uuid)
            vip_option = test_util.VipOption()
            vip_option.set_name("vip_for_load_balancer_policy_checker")
            vip_option.set_session_uuid(project_login_session_uuid)
            vip_option.set_l3_uuid(l3_pub_uuid)
            vip = net_ops.create_vip(vip_option)
            lb_uuid = net_ops.create_load_balancer(vip.uuid, 'load_balancer_policy_checker', session_uuid=project_login_session_uuid).uuid
            lb_listener_option = test_util.LoadBalancerListenerOption()
            lb_listener_option.set_name('load_balancer_listener_policy_checker')
            lb_listener_option.set_load_balancer_uuid(lb_uuid)
            lb_listener_option.set_load_balancer_port('2222')
            lb_listener_option.set_instance_port('80')
            lb_listener_option.set_protocol('http')
            lb_listener_option.set_session_uuid(session_uuid=project_login_session_uuid)
            lbl_uuid = net_ops.create_load_balancer_listener(lb_listener_option).uuid
            conditions = res_ops.gen_query_conditions('vmInstance.uuid', '=', vm_uuid)
            vm_nic_uuid = res_ops.query_resource(res_ops.VM_NIC, conditions)[0].uuid
            net_ops.add_nic_to_load_balancer(lbl_uuid, [vm_nic_uuid], session_uuid=project_login_session_uuid)
            net_ops.remove_nic_from_load_balancer(lbl_uuid, [vm_nic_uuid], session_uuid=project_login_session_uuid)
            net_ops.refresh_load_balancer(lb_uuid, session_uuid=project_login_session_uuid) 
            net_ops.delete_load_balancer_listener(lbl_uuid, session_uuid=project_login_session_uuid)
            net_ops.delete_load_balancer(lb_uuid, session_uuid=project_login_session_uuid)
            net_ops.delete_vip(vip.uuid)
            vm_ops.destroy_vm(vm_uuid)
            vm_ops.expunge_vm(vm_uuid)
            if lb_service_need_detach:
                net_ops.detach_lb_service_from_l3network(l3_net_uuid, service_providor_uuid, session_uuid=project_login_session_uuid)
            acc_ops.revoke_resources([project_linked_account_uuid], [l3_pub_uuid, l3_net_uuid, image_uuid, instance_offering_uuid])
        except Exception as e:
            test_util.test_logger('Check Result: [Virtual ID:] %s has permission for load balancer but load balancer check failed' % virtual_id.name)
            test_util.test_logger('Excepiton info: %s' %e)
            return self.judge(False)
        return self.judge(True)

    def check_port_forwarding(self):
        virtual_id = self.test_obj.get_vid()
        plain_user_session_uuid = iam2_ops.login_iam2_virtual_id(virtual_id.name, self.password)
        conditions = res_ops.gen_query_conditions('virtualIDs.uuid', '=',virtual_id.uuid)
        project_ins = res_ops.query_resource(res_ops.IAM2_PROJECT, conditions)[0]
        project_login_session_uuid = iam2_ops.login_iam2_project(project_ins.name, plain_user_session_uuid).uuid
        project_linked_account_uuid = project_ins.linkedAccountUuid
        
        try:
            conditions = res_ops.gen_query_conditions('category', '=', 'Public')
            l3_pub_uuid = res_ops.query_resource(res_ops.L3_NETWORK, conditions)[0].uuid
            vm_creation_option = test_util.VmOption()
            conditions = res_ops.gen_query_conditions('system', '=', 'false')
            conditions = res_ops.gen_query_conditions('category', '=', 'Private', conditions)
            l3_net_uuid = res_ops.query_resource(res_ops.L3_NETWORK, conditions)[0].uuid
            conditions = res_ops.gen_query_conditions('name', '=', 'vrouter')
            pf_service_providor_uuid = res_ops.query_resource(res_ops.NETWORK_SERVICE_PROVIDER, conditions)[0].uuid 
            acc_ops.share_resources([project_linked_account_uuid], [l3_pub_uuid, l3_net_uuid])
            conditions = res_ops.gen_query_conditions('l3Network.uuid', '=', l3_net_uuid)
            network_service_list = res_ops.query_resource(res_ops.NETWORK_SERVICE_PROVIDER_L3_REF, conditions)
            pf_service_need_attach = True
            pf_service_need_detach = False
            for service in network_service_list:
                if service.networkServiceType == 'PortForwarding':
                    pf_service_need_attach = False
            if pf_service_need_attach:
                net_ops.attach_pf_service_to_l3network(l3_net_uuid, pf_service_providor_uuid, session_uuid=project_login_session_uuid)
                pf_service_need_detach = True   
            vm_creation_option.set_l3_uuids([l3_net_uuid])
            conditions = res_ops.gen_query_conditions('platform', '=', 'Linux')
            conditions = res_ops.gen_query_conditions('system', '=', 'false', conditions)
            image_uuid = res_ops.query_resource(res_ops.IMAGE, conditions)[0].uuid
            vm_creation_option.set_image_uuid(image_uuid)
            acc_ops.share_resources([project_linked_account_uuid], [image_uuid])
            conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
            instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid
            vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
            acc_ops.share_resources([project_linked_account_uuid], [instance_offering_uuid])
            vm_creation_option.set_name('vm_for_port_forwarding_policy_checker')
            vm = vm_ops.create_vm(vm_creation_option)
            vm_uuid = vm.uuid
            res_ops.change_recource_owner(project_linked_account_uuid, vm_uuid)
            conditions = res_ops.gen_query_conditions('vmInstance.uuid', '=', vm_uuid)
            vm_nic_uuid = res_ops.query_resource(res_ops.VM_NIC, conditions)[0].uuid
            vip_option = test_util.VipOption()
            vip_option.set_name("vip_for_port_forwarding_policy_checker")
            vip_option.set_session_uuid(project_login_session_uuid)
            vip_option.set_l3_uuid(l3_pub_uuid)
            vip = net_ops.create_vip(vip_option)
            pf_rule_creation_option = test_util.PortForwardingRuleOption()
            pf_rule_creation_option.set_vip_uuid(vip.uuid)
            pf_rule_creation_option.set_protocol('TCP')
            pf_rule_creation_option.set_vip_ports('8080', '8088')
            pf_rule_creation_option.set_private_ports('8080', '8088')
            pf_rule_creation_option.set_name('port_forwarding_rule_policy_checker')
            pf_rule_creation_option.set_session_uuid(session_uuid=project_login_session_uuid)
            pf_rule_uuid = net_ops.create_port_forwarding(pf_rule_creation_option).uuid
            net_ops.attach_port_forwarding(pf_rule_uuid, vm_nic_uuid, session_uuid=project_login_session_uuid)
            net_ops.detach_port_forwarding(pf_rule_uuid, session_uuid=project_login_session_uuid)
            net_ops.delete_port_forwarding(pf_rule_uuid, session_uuid=project_login_session_uuid)
            net_ops.delete_vip(vip.uuid)
            vm_ops.destroy_vm(vm_uuid)
            vm_ops.expunge_vm(vm_uuid)
            if pf_service_need_detach:
                net_ops.detach_pf_service_from_l3network(l3_net_uuid, pf_service_providor_uuid, session_uuid=project_login_session_uuid)
            acc_ops.revoke_resources([project_linked_account_uuid], [l3_pub_uuid, l3_net_uuid, image_uuid, instance_offering_uuid])
        except Exception as e:
            test_util.test_logger('Check Result: [Virtual ID:] %s has permission for port forwarding but port forwarding check failed' % virtual_id.name)
            test_util.test_logger('Excepiton info: %s' %e)
            return self.judge(False)
        return self.judge(True)

    def check_scheduler(self):
        virtual_id = self.test_obj.get_vid()
        plain_user_session_uuid = iam2_ops.login_iam2_virtual_id(virtual_id.name, self.password)
        conditions = res_ops.gen_query_conditions('virtualIDs.uuid', '=',virtual_id.uuid)
        project_ins = res_ops.query_resource(res_ops.IAM2_PROJECT, conditions)[0]
        project_login_session_uuid = iam2_ops.login_iam2_project(project_ins.name, plain_user_session_uuid).uuid
        project_linked_account_uuid = project_ins.linkedAccountUuid

        try:
            vm_creation_option = test_util.VmOption()
            conditions = res_ops.gen_query_conditions('system', '=', 'false')
            l3_net_uuid = res_ops.query_resource(res_ops.L3_NETWORK, conditions)[0].uuid
            acc_ops.share_resources([project_linked_account_uuid], [l3_net_uuid])
            vm_creation_option.set_l3_uuids([l3_net_uuid])
            conditions = res_ops.gen_query_conditions('platform', '=', 'Linux')
            conditions = res_ops.gen_query_conditions('system', '=', 'false', conditions)
            image_uuid = res_ops.query_resource(res_ops.IMAGE, conditions)[0].uuid
            vm_creation_option.set_image_uuid(image_uuid)
            acc_ops.share_resources([project_linked_account_uuid], [image_uuid])
            conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
            instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid
            vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
            acc_ops.share_resources([project_linked_account_uuid], [instance_offering_uuid])
            vm_creation_option.set_name('vm_for_scheduler_policy_checker')
            vm = vm_ops.create_vm(vm_creation_option)
            vm_uuid = vm.uuid
            res_ops.change_recource_owner(project_linked_account_uuid, vm_uuid)

            start_date = int(time.time())
            schd_job = schd_ops.create_scheduler_job('start_vm_scheduler_policy_checker', 'start vm scheduler policy checker', vm_uuid, 'startVm', None, session_uuid=project_login_session_uuid)
            schd_trigger = schd_ops.create_scheduler_trigger('start_vm_scheduler_policy_checker', start_date+5, None, 15, 'simple', session_uuid=project_login_session_uuid)
            schd_ops.add_scheduler_job_to_trigger(schd_trigger.uuid, schd_job.uuid, session_uuid=project_login_session_uuid)
            schd_ops.change_scheduler_state(schd_job.uuid, 'disable', session_uuid=project_login_session_uuid)
            schd_ops.change_scheduler_state(schd_job.uuid, 'enable', session_uuid=project_login_session_uuid)
            schd_ops.remove_scheduler_job_from_trigger(schd_trigger.uuid, schd_job.uuid, session_uuid=project_login_session_uuid)
            schd_ops.del_scheduler_job(schd_job.uuid, session_uuid=project_login_session_uuid)
            schd_ops.del_scheduler_trigger(schd_trigger.uuid, session_uuid=project_login_session_uuid)
            schd_ops.get_current_time()
            vm_ops.destroy_vm(vm_uuid)
            vm_ops.expunge_vm(vm_uuid)
        except Exception as e:
            test_util.test_logger('Check Result: [Virtual ID:] %s has permission for scheduler but scheduler check failed' % virtual_id.name)
            test_util.test_logger('Excepiton info: %s' %e)
            return self.judge(False)
        return self.judge(True)

    def check_pci(self):
        #Haven't simulator pci device, skip to check 
        pass

    def check_zwatch(self):
        virtual_id = self.test_obj.get_vid()
        plain_user_session_uuid = iam2_ops.login_iam2_virtual_id(virtual_id.name, self.password)
        conditions = res_ops.gen_query_conditions('virtualIDs.uuid', '=',virtual_id.uuid)
        project_ins = res_ops.query_resource(res_ops.IAM2_PROJECT, conditions)[0]
        project_login_session_uuid = iam2_ops.login_iam2_project(project_ins.name, plain_user_session_uuid).uuid
        project_linked_account_uuid = project_ins.linkedAccountUuid
        try:
            http_endpoint_name='http_endpoint_for zwatch_policy_checker'
            url = 'http://localhost:8080/webhook-url'
            http_endpoint=zwt_ops.create_sns_http_endpoint(url, http_endpoint_name, session_uuid=project_login_session_uuid)
            http_endpoint_uuid=http_endpoint.uuid
            sns_topic_uuid = zwt_ops.create_sns_topic('sns_topic_for zwatch_policy_checker', session_uuid=project_login_session_uuid).uuid        
            sns_topic_uuid1 = zwt_ops.create_sns_topic('sns_topic_for zwatch_policy_checker_01', session_uuid=project_login_session_uuid).uuid        
            zwt_ops.subscribe_sns_topic(sns_topic_uuid, http_endpoint_uuid, session_uuid=project_login_session_uuid)
            namespace = 'ZStack/VM'
            actions = [{"actionUuid": sns_topic_uuid, "actionType": "sns"}]
            period = 60
            comparison_operator = 'GreaterThanOrEqualTo'
            threshold = 10
            metric_name = 'CPUUsedUtilization'
            labels = [{"key": "NewState", "op": "Equal", "value": "Disconnected"}]
            event_name = 'VMStateChangedOnHost'
            alarm_uuid = zwt_ops.create_alarm(comparison_operator, period, threshold, namespace, metric_name, session_uuid=project_login_session_uuid).uuid
            event_sub_uuid = zwt_ops.subscribe_event(namespace, event_name, actions, labels, session_uuid=project_login_session_uuid).uuid
            zwt_ops.update_alarm(alarm_uuid, comparison_operator='GreaterThan', session_uuid=project_login_session_uuid)
            zwt_ops.update_sns_application_endpoint(http_endpoint_uuid, 'new_endpoint_name', 'new description', session_uuid=project_login_session_uuid)
            zwt_ops.add_action_to_alarm(alarm_uuid, sns_topic_uuid1, 'sns', session_uuid=project_login_session_uuid) 
            zwt_ops.remove_action_from_alarm(alarm_uuid, sns_topic_uuid, session_uuid=project_login_session_uuid)
            zwt_ops.change_alarm_state(alarm_uuid, 'disable', session_uuid=project_login_session_uuid)
            zwt_ops.change_sns_topic_state(sns_topic_uuid, 'disable', session_uuid=project_login_session_uuid)
            zwt_ops.change_sns_application_endpoint_state(http_endpoint_uuid, 'disable', session_uuid=project_login_session_uuid)
            zwt_ops.delete_alarm(alarm_uuid, session_uuid=project_login_session_uuid) 
            zwt_ops.unsubscribe_event(event_sub_uuid, session_uuid=project_login_session_uuid)
            zwt_ops.unsubscribe_sns_topic(sns_topic_uuid, http_endpoint_uuid, session_uuid=project_login_session_uuid)
            zwt_ops.delete_sns_topic(sns_topic_uuid, session_uuid=project_login_session_uuid)
            zwt_ops.delete_sns_topic(sns_topic_uuid1, session_uuid=project_login_session_uuid)
            zwt_ops.delete_sns_application_endpoint(http_endpoint_uuid, session_uuid=project_login_session_uuid)

        except Exception as e:
            test_util.test_logger('Check Result: [Virtual ID:] %s has permission for zwatch but zwatch check failed' % virtual_id.name)
            test_util.test_logger('Excepiton info: %s' %e)
            return self.judge(False)
        return self.judge(True)

    def check_sns(self):
        virtual_id = self.test_obj.get_vid()
        plain_user_session_uuid = iam2_ops.login_iam2_virtual_id(virtual_id.name, self.password)
        conditions = res_ops.gen_query_conditions('virtualIDs.uuid', '=',virtual_id.uuid)
        project_ins = res_ops.query_resource(res_ops.IAM2_PROJECT, conditions)[0]
        project_login_session_uuid = iam2_ops.login_iam2_project(project_ins.name, plain_user_session_uuid).uuid
        project_linked_account_uuid = project_ins.linkedAccountUuid
        try:
            http_endpoint_name='http_endpoint_for zwatch_policy_checker'
            url = 'http://localhost:8080/webhook-url'
            http_endpoint=zwt_ops.create_sns_http_endpoint(url, http_endpoint_name)
            http_endpoint_uuid=http_endpoint.uuid
            sns_topic_uuid = zwt_ops.create_sns_topic('sns_topic_for zwatch_policy_checker', session_uuid=project_login_session_uuid).uuid
            sns_topic_uuid1 = zwt_ops.create_sns_topic('sns_topic_for zwatch_policy_checker_01', session_uuid=project_login_session_uuid).uuid
            zwt_ops.subscribe_sns_topic(sns_topic_uuid, http_endpoint_uuid, session_uuid=project_login_session_uuid)
            namespace = 'ZStack/VM'
            actions = [{"actionUuid": sns_topic_uuid, "actionType": "sns"}]
            period = 60
            comparison_operator = 'GreaterThanOrEqualTo'
            threshold = 10
            metric_name = 'CPUUsedUtilization'
            alarm_uuid = zwt_ops.create_alarm(comparison_operator, period, threshold, namespace, metric_name).uuid
            labels = [{"key": "NewState", "op": "Equal", "value": "Disconnected"}]
            event_name = 'VMStateChangedOnHost'
            event_sub_uuid = zwt_ops.subscribe_event(namespace, event_name, actions, labels).uuid
            zwt_ops.update_sns_application_endpoint(http_endpoint_uuid, 'new_endpoint_name', 'new description', session_uuid=project_login_session_uuid)
            zwt_ops.add_action_to_alarm(alarm_uuid, sns_topic_uuid1, 'sns')
            zwt_ops.remove_action_from_alarm(alarm_uuid, sns_topic_uuid)
            zwt_ops.change_sns_topic_state(sns_topic_uuid, 'disable', session_uuid=project_login_session_uuid)
            zwt_ops.change_sns_application_endpoint_state(http_endpoint_uuid, 'disable', session_uuid=project_login_session_uuid)
            zwt_ops.delete_alarm(alarm_uuid)
            zwt_ops.unsubscribe_event(event_sub_uuid)
            zwt_ops.unsubscribe_sns_topic(sns_topic_uuid, http_endpoint_uuid, session_uuid=project_login_session_uuid)
            zwt_ops.delete_sns_topic(sns_topic_uuid, session_uuid=project_login_session_uuid)
            zwt_ops.delete_sns_topic(sns_topic_uuid1, session_uuid=project_login_session_uuid)
            zwt_ops.delete_sns_application_endpoint(http_endpoint_uuid, session_uuid=project_login_session_uuid)

        except Exception as e:
            test_util.test_logger('Check Result: [Virtual ID:] %s has permission for sns but sns check failed' % virtual_id.name)
            test_util.test_logger('Excepiton info: %s' %e)
            return self.judge(False)
        return self.judge(True)

    def check(self):
        super(zstack_vid_policy_checker, self).check()
        password = 'b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86'
        virtual_id = self.test_obj.get_vid()
        self.check_login(virtual_id.name, password)
        actions = self.test_obj.get_vid_statements()[0]['actions']
        if 'org.zstack.header.vm.**' in actions and \
                'org.zstack.ha.**' in actions:
            self.check_vm_operation()
        if 'org.zstack.header.image.**' in actions and \
                'org.zstack.storage.backup.imagestore.APIGetImagesFromImageStoreBackupStorageMsg' in actions:
            self.check_image_operation()
        if 'org.zstack.header.volume.APICreateDataVolumeFromVolumeTemplateMsg' in actions and \
                'org.zstack.header.volume.APIGetVolumeQosMsg' in actions and \
                'org.zstack.header.volume.APISyncVolumeSizeMsg' in actions and \
                'org.zstack.header.volume.APICreateDataVolumeFromVolumeSnapshotMsg' in actions and \
                'org.zstack.header.volume.APIResizeDataVolumeMsg' in actions and \
                'org.zstack.header.volume.APIRecoverDataVolumeMsg' in actions and \
                'org.zstack.header.volume.APIExpungeDataVolumeMsg' in actions and \
                'org.zstack.mevoco.APIQueryShareableVolumeVmInstanceRefMsg' in actions and \
                'org.zstack.header.volume.APICreateDataVolumeMsg' in actions and \
                'org.zstack.header.volume.APIGetVolumeCapabilitiesMsg' in actions and \
                'org.zstack.header.volume.APIDetachDataVolumeFromVmMsg' in actions and \
                'org.zstack.header.volume.APIDeleteVolumeQosMsg' in actions and \
                'org.zstack.header.volume.APIGetVolumeFormatMsg' in actions and \
                'org.zstack.header.volume.APIGetDataVolumeAttachableVmMsg' in actions and \
                'org.zstack.header.volume.APIAttachDataVolumeToVmMsg' in actions and \
                'org.zstack.header.volume.APIResizeRootVolumeMsg' in actions and \
                'org.zstack.header.volume.APISetVolumeQosMsg' in actions and \
                'org.zstack.header.volume.APIDeleteDataVolumeMsg' in actions and \
                'org.zstack.header.volume.APIUpdateVolumeMsg' in actions and \
                'org.zstack.header.volume.APIChangeVolumeStateMsg' in actions and \
                'org.zstack.header.volume.APIQueryVolumeMsg' in actions: 
            self.check_volume_operation()
        if 'org.zstack.header.vm.**' not in actions and \
                'org.zstack.header.vm.APIGetVmQgaMsg' in actions and \
                'org.zstack.header.vm.APIChangeVmImageMsg' in actions and \
                'org.zstack.header.vm.APISetVmSshKeyMsg' in actions and \
                'org.zstack.header.vm.APIStopVmInstanceMsg' in actions and \
                'org.zstack.header.vm.APISetVmStaticIpMsg' in actions and \
                'org.zstack.header.vm.APIRecoverVmInstanceMsg' in actions and \
                'org.zstack.header.vm.APIQueryVmNicMsg' in actions and \
                'org.zstack.header.vm.APIStartVmInstanceMsg' in actions and \
                'org.zstack.header.vm.APIDestroyVmInstanceMsg' in actions and \
                'org.zstack.header.vm.APIGetVmConsolePasswordMsg' in actions and \
                'org.zstack.header.vm.APIDeleteVmStaticIpMsg' in actions and \
                'org.zstack.header.vm.APISetNicQosMsg' in actions and \
                'org.zstack.header.vm.APIRebootVmInstanceMsg' in actions and \
                'org.zstack.header.vm.APIGetNicQosMsg' in actions and \
                'org.zstack.header.vm.APIGetVmBootOrderMsg' in actions and \
                'org.zstack.header.vm.APIChangeVmPasswordMsg' in actions and \
                'org.zstack.header.vm.APIGetCandidatePrimaryStoragesForCreatingVmMsg' in actions and \
                'org.zstack.header.vm.APISetVmRDPMsg' in actions and \
                'org.zstack.header.vm.APIMigrateVmMsg' in actions and \
                'org.zstack.header.vm.APIGetVmMigrationCandidateHostsMsg' in actions and \
                'org.zstack.header.vm.APIAttachL3NetworkToVmMsg' in actions and \
                'org.zstack.header.vm.APIExpungeVmInstanceMsg' in actions and \
                'org.zstack.header.vm.APIGetCandidateVmForAttachingIsoMsg' in actions and \
                'org.zstack.header.vm.APIAttachIsoToVmInstanceMsg' in actions and \
                'org.zstack.header.vm.APIGetVmAttachableL3NetworkMsg' in actions and \
                'org.zstack.header.vm.APIGetVmHostnameMsg' in actions and \
                'org.zstack.header.vm.APIDeleteVmSshKeyMsg' in actions and \
                'org.zstack.header.vm.APIGetVmMonitorNumberMsg' in actions and \
                'org.zstack.header.vm.APISetVmQgaMsg' in actions and \
                'org.zstack.header.vm.APIDetachL3NetworkFromVmMsg' in actions and \
                'org.zstack.header.vm.APISetVmConsolePasswordMsg' in actions and \
                'org.zstack.header.vm.APIGetCandidateZonesClustersHostsForCreatingVmMsg' in actions and \
                'org.zstack.header.vm.APIGetVmAttachableDataVolumeMsg' in actions and \
                'org.zstack.header.vm.APIGetInterdependentL3NetworksImagesMsg' in actions and \
                'org.zstack.header.vm.APIGetCandidateIsoForAttachingVmMsg' in actions and \
                'org.zstack.header.vm.APIDeleteNicQosMsg' in actions and \
                'org.zstack.header.vm.APISetVmUsbRedirectMsg' in actions and \
                'org.zstack.header.vm.APISetVmBootOrderMsg' in actions and \
                'org.zstack.header.vm.APIGetImageCandidatesForVmToChangeMsg' in actions and \
                'org.zstack.header.vm.APIGetVmConsoleAddressMsg' in actions and \
                'org.zstack.header.vm.APIChangeInstanceOfferingMsg' in actions and \
                'org.zstack.header.vm.APIDeleteVmHostnameMsg' in actions and \
                'org.zstack.header.vm.APIGetVmUsbRedirectMsg' in actions and \
                'org.zstack.header.vm.APIQueryVmInstanceMsg' in actions and \
                'org.zstack.header.vm.APISetVmMonitorNumberMsg' in actions and \
                'org.zstack.header.vm.APIReimageVmInstanceMsg' in actions and \
                'org.zstack.header.vm.APIResumeVmInstanceMsg' in actions and \
                'org.zstack.header.vm.APIUpdateVmNicMacMsg' in actions and \
                'org.zstack.header.vm.APIGetVmCapabilitiesMsg' in actions and \
                'org.zstack.header.vm.APIUpdateVmInstanceMsg' in actions and \
                'org.zstack.header.vm.APIGetVmSshKeyMsg' in actions and \
                'org.zstack.header.vm.APICloneVmInstanceMsg' in actions and \
                'org.zstack.header.vm.APIDeleteVmConsolePasswordMsg' in actions and \
                'org.zstack.header.vm.APISetVmHostnameMsg' in actions and \
                'org.zstack.header.vm.APIGetVmStartingCandidateClustersHostsMsg' in actions and \
                'org.zstack.header.vm.APIDetachIsoFromVmInstanceMsg' in actions and \
                'org.zstack.header.vm.APIGetVmRDPMsg' in actions and \
                'org.zstack.header.vm.APIPauseVmInstanceMsg' in actions:
            self.check_vm_operation_without_create_permission()
        if 'org.zstack.header.storage.snapshot.**' in actions and \
                'org.zstack.header.volume.APICreateVolumeSnapshotMsg' in actions:
            self.check_snapshot()
        if 'org.zstack.header.affinitygroup.**' in actions:
            self.check_affinity_group()
        if 'org.zstack.header.network.l3.**' in actions and \
                'org.zstack.network.service.flat.**' in actions and \
                'org.zstack.header.network.l2.APIUpdateL2NetworkMsg' in actions and \
                'org.zstack.header.network.service.APIQueryNetworkServiceProviderMsg' in actions and \
                'org.zstack.header.network.service.APIAttachNetworkServiceToL3NetworkMsg' in actions and \
                'org.zstack.network.l2.vxlan.vxlanNetworkPool.APIQueryVniRangeMsg' in actions and \
                'org.zstack.network.l2.vxlan.vxlanNetwork.APIQueryL2VxlanNetworkMsg' in actions and \
                'org.zstack.network.l2.vxlan.vxlanNetwork.APICreateL2VxlanNetworkMsg' in actions and \
                'org.zstack.network.l2.vxlan.vxlanNetworkPool.APIQueryL2VxlanNetworkPoolMsg' in actions:
            self.check_networks()
        if 'org.zstack.network.service.vip.**' in actions and \
                'org.zstack.network.service.eip.**' in actions and \
                'org.zstack.header.vipQos.**' in actions:
            self.check_eip()
        if 'org.zstack.network.securitygroup.**' in actions:
            self.check_security_group()
        if 'org.zstack.network.service.lb.**' in actions and \
                'org.zstack.network.service.vip.**' in actions and \
                'org.zstack.header.vipQos.**' in actions:
            self.check_load_balancer()
        if 'org.zstack.network.service.portforwarding.**' in actions and \
                'org.zstack.network.service.vip.**' in actions and \
                'org.zstack.header.vipQos.**' in actions:
            self.check_port_forwarding()
        if 'org.zstack.scheduler.**' in actions:
            self.check_scheduler()
        if 'org.zstack.pciDevice.APIAttachPciDeviceToVmMsg' in actions and \
                'org.zstack.pciDevice.APIUpdateHostIommuStateMsg' in actions and \
                'org.zstack.pciDevice.APIGetPciDeviceCandidatesForNewCreateVmMsg' in actions and \
                'org.zstack.pciDevice.APIDetachPciDeviceFromVmMsg' in actions and \
                'org.zstack.pciDevice.APIQueryPciDeviceMsg' in actions and \
                'org.zstack.pciDevice.APIGetPciDeviceCandidatesForAttachingVmMsg' in actions:
            self.check_pci()
        if 'org.zstack.zwatch.**' in actions and \
                'org.zstack.sns.**' in actions:
            self.check_zwatch()
        if 'org.zstack.sns.**' in actions:
            self.check_sns()  
        return self.judge(True)
