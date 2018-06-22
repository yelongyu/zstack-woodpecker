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
import zstackwoodpecker.operations.affinitygroup_operations as ag_ops
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.operations.scheduler_operations as schd_ops
import zstackwoodpecker.operations.zwatch_operations as zwt_ops

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
        super(zstack_vid_policy_checker, self).__init__()

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
                test_util.test_logger('Check Result: [Virtual ID:] %s has permission to create vm but creation failed' % username)    
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
                test_util.test_logger('Check Result: [Virtual ID:] %s has permission to create vm but creation failed' % username)
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
                test_util.test_logger('Check Result: [Virtual ID:] %s has permission to add image but addition failed' % username)
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
                test_util.test_logger('Check Result: [Virtual ID:] %s has permission to create snapshot but creation failed' % username)
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
                test_util.test_logger('Check Result: [Virtual ID:] %s has  permission to create volume but creation failed' % username)
                return self.judge(False)
        return self.judge(True)

    def check_role_affinity_group(self):
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

    def check_role_networks(self):
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

    def check_role_eip(self):
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

    def check_role_sg(self):
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

    def check_role_lb(self):
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

    def check_role_pf(self):
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

    def check_role_scheduler(self):
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
    def check_role_pci(self):
        pass

    def check_role_zwatch(self):
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

    def check_role_sns(self):
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

        virtual_id = self.test_obj.vid
        self.check_login(virtual_id.username, virtual_id.password)
        for role in virtual_id.role:
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
