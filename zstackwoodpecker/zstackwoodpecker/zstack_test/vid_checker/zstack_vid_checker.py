'''
IAM2 Vid Attribute Checker.
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.header.checker as checker_header
import zstackwoodpecker.operations.iam2_operations as iam2_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.image_operations as image_ops
import zstackwoodpecker.operations.volume_operations as volume_ops

class zstack_vid_attr_checker(checker_header.TestChecker):
    def __init__(self):
        super(VidChecker, self).__init__()

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
            create_iam2_project(name='platform_admin_create_project_permission_check', session_uuid=session_uuid)
        except:
            test_util.test_logger('Check Result: [Virtual ID:] %s is Platform Admin, but create project failed' % username)
            return self.judge(False)

    def check_project_admin_permission(self, username, password):
        session_uuid = iam2_ops.login_iam2_virtual_id(username, password)
        #Check if have permission to create project
        try:
            create_iam2_project(name='porject_admin_create_project_permission_check', session_uuid=session_uuid)
            test_util.test_logger('Check Result: [Virtual ID:] %s is Porject Admin, but is able to create project' % username)
            return self.judge(False)
        except:
            pass 

        #Check if have permission to setup project operator
        try:
            project_operator_uuid = iam2_ops.create_iam2_virtual_id(name='project_admin_create_project_operator_permission_check', password=''b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86, attributes=[{"name":"__ProjectOperator__"}], session_uuid=session_uuid).uuid
        except:
            test_util.test_logger('Check Result: [Virtual ID:] %s is Project Admin, but setup project operator failed' % username)
            return self.judge(False)
        iam2_ops.delete_iam2_virtual_id(project_operator_uuid, session_uuid=session_uuid)

    def check_project_operator_permisson(self, username, password):
        session_uuid = iam2_ops.login_iam2_virtual_id(username, password)
        #Check if have permission to setup project operator
        try:
            project_operator_uuid = iam2_ops.create_iam2_virtual_id(name='project_admin_create_project_operator_permission_check', password=''b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86, attributes=[{"name":"__ProjectOperator__"}], session_uuid=session_uuid).uuid
            test_util.test_logger('Check Result: [Virtual ID:] %s is Porject Operator, but is able to create other project operator' % username)
            iam2_ops.delete_iam2_virtual_id(project_operator_uuid, session_uuid=session_uuid)
            return self.judge(False)
        except:
            pass

        #Check if have permission to disable project
        conditions = res_ops.gen_query_conditions('attributes.name', '=', '__ProjectOperator__')
        project_uuid = res_ops.res_ops.query_resource(res_ops.IAM2_VIRTUAL_ID, conditions)[0].value
        try:
            conditions = res_ops.gen_query_conditions('uuid', '=', project_uuid)
            origin_state = res_ops.res_ops.query_resource(res_ops.IAM2_PROJECT, conditions)[0].state 
            if origin_state != 'Disabled':
                try:
                    new_state = iam2_ops.change_iam2_project_state(uuid, 'Disabled', session_uuid=session_uuid).state
                    iam2_ops.change_iam2_project_state(uuid, origin_state, session_uuid=session_uuid)
                except:
                    test_util.test_logger('Check Result: [Virtual ID:] %s is Porject Operator, but change project state failed' % username)
                    return self.judge(False)
            else:
                try:
                    new_state = iam2_ops.change_iam2_project_state(uuid, 'Enabled', session_uuid=session_uuid).state
                    iam2_ops.change_iam2_project_state(uuid, origin_state, session_uuid=session_uuid)
                except:
                    test_util.test_logger('Check Result: [Virtual ID:] %s is Porject Operator, but change project state failed' % username)
                    return self.judge(False)

    def check(self):
        super(zstack_vid_attr_checker, self).check()

        virtual_id = self.test_obj.virtual_id
        self.check_login(virtual_id.username, virtual_id.password)
        for attr in virtual_id.attributes.name:
            if attr = '__PlatformAdmin__':
                self.check_platform_admin_permission(virtual_id.username, virtual_id.password)
            elif attr = '__ProjectAdmin__':
                self.check_porject_admin_permission(virtual_id.username, virtual_id.password)
            elif attr = '__ProjectOperator__':
                self.check_porject_operator_permission(virtual_id.username, virtual_id.password)
        return self.judge(True)

class zstack_vid_policy_checker(checker_header.TestChecker):
    def __init__(self):
        super(VidChecker, self).__init__()

    def check_login(self, username, password):
        try:
            session_uuid = iam2_ops.login_iam2_virtual_id(username, password)
            iam2_ops.login_iam2_project(project_name, session_uuid=session_uuid)
        except:
            test_util.test_logger('Check Result: [Virtual ID:] %s login failed' % username)
            return self.judge(False)
    def check_role_vm(self):
        session_uuid = iam2_ops.login_iam2_virtual_id(username, password)
        iam2_ops.login_iam2_project(project_name, session_uuid=session_uuid)
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
                test_util.test_logger('Check Result: [Virtual ID:] %s has not permission to create vm' % username)    
                return self.judge(False)
        return self.judge(True)
    def check_role_vm_without_create(self):
        session_uuid = iam2_ops.login_iam2_virtual_id(username, password)
        iam2_ops.login_iam2_project(project_name, session_uuid=session_uuid)
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
                test_util.test_logger('Check Result: [Virtual ID:] %s has not permission to create vm' % username)
                return self.judge(True)
            return self.judge(False)
        return self.judge(False)
    def check_role_image(self):
        session_uuid = iam2_ops.login_iam2_virtual_id(username, password)
        iam2_ops.login_iam2_project(project_name, session_uuid=session_uuid)
        try:
            image_option = test_util.ImageOption()
            image_uuid = image_ops.add_image(image_option).uuid
            image_ops.delete_image(image_uuid, session_uuid=session_uuid)
            image_ops.expunge_image(image_uuid, session_uuid=session_uuid)
        except e:
            if e.find('permission') != -1:
                test_util.test_logger('Check Result: [Virtual ID:] %s has not permission to add image' % username)
                return self.judge(False)
        return self.judge(True)
    def check_role_snapshot(self):
        session_uuid = iam2_ops.login_iam2_virtual_id(username, password)
        iam2_ops.login_iam2_project(project_name, session_uuid=session_uuid)
        try:
            snapshot_option = test_util.SnapshotOption()
            snapshot_uuid = volume_ops.create_snapshot(snapshot_option).uuid
            volume_ops.delete_snapshot(snapshot_uuid, session_uuid=session_uuid)
        except e:
            if e.find('permission') != -1:
                test_util.test_logger('Check Result: [Virtual ID:] %s has not permission to create snapshot' % username)
                return self.judge(False)
        return self.judge(True)
    def check_role_volume(self):
        session_uuid = iam2_ops.login_iam2_virtual_id(username, password)
        iam2_ops.login_iam2_project(project_name, session_uuid=session_uuid)
        try:
            volume_option = test_util.VolumeOption()
            volume_uuid = volume_ops.create_volume_from_offering(volume_option).uuid
            volume_ops.delete_volume(volume_uuid, session_uuid=session_uuid)
        except e:
            if e.find('permission') != -1:
                test_util.test_logger('Check Result: [Virtual ID:] %s has not permission to create volume' % username)
                return self.judge(False)
        return self.judge(True)
    def check_role_affinity_group(self):
        pass
    def check_role_networks(self):
        pass
    def check_role_eip(self):
        pass
    def check_role_sg(self):
        pass
    def check_role_lb(self):
        pass
    def check_role_pf(self):
        pass
    def check_scheduler(self):
        pass
    def check_role_pci(self):
        pass
    def check_role_zwatch(self):
        session_uuid = iam2_ops.login_iam2_virtual_id(username, password)
        iam2_ops.login_iam2_project(project_name, session_uuid=session_uuid)

    def check_role_sns(self):
        session_uuid = iam2_ops.login_iam2_virtual_id(username, password)
        iam2_ops.login_iam2_project(project_name, session_uuid=session_uuid)

    def check(self):
        super(zstack_vid_policy_checker, self).check()

        virtual_id = self.test_obj.virtual_id

        self.check_login(virtual_id.username, virtual_id.password)
        
        for role in virtual_id.role:
            if role.type = 'CreatedBySystem':
                if role.name = 'predefined: vm':
                    self.check_role_vm()
                elif role.name = 'predefined: vm-operation-without-create-permission':
                    self.check_role_vm_without_create()
                elif role.name = 'predefined: image':
                    self.check_role_image()
                elif role.name = 'predefined: snapshot':
                    self.check_role_snapshot()
                elif role.name = 'predefined: volume':
                    self.check_role_volume()
                elif role.name = 'predefined: affinity-group':
                    self.check_role_affinity_group()
                elif role.name = 'predefined: networks':
                    self.check_role_networks()
                elif role.name = 'predefined: eip':
                    self.check_role_eip()
                elif role.name = 'predefined: security-group':
                    self.check_role_sg()
                elif role.name = 'predefined: load-balancer':
                    self.check_role_lb()
                elif role.name = 'predefined: port-forwarding':
                    self.check_role_pf()
                elif role.name = 'predefined: scheduler':
                    self.check_scheduler()
                elif role.name = 'predefined: pci-device':
                    self.check_role_pci()
                elif role.name = 'predefined: zwatch':
                    self.check_role_zwatch()
                elif role.name = 'predefined: sns':
                    self.check_role_sns()
                else:
                    test_util.test_logger('The role is not predifined role, unable to check')
        return self.judge(True)

