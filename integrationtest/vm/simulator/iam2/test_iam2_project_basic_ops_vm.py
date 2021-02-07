'''
test iam2 vm operations by platform admin/operator/member

# 1 create project
# 2 create virtual id (project admin/operator/member)
# 3 operations on vm with virtual id
# 4 delete

@author: quarkonics
'''
import os
import time
import zstackwoodpecker.test_util as test_util
import apibinding.inventory as inventory
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.operations.iam2_operations as iam2_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.operations.account_operations as acc_ops
from zstackwoodpecker.operations import vm_operations as vm_ops
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.operations.scheduler_operations as schd_ops
import zstackwoodpecker.operations.zwatch_operations as zwt_ops
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.zstack_test.zstack_test_vid as test_vid

project_uuid = None
virtual_id_uuid = None
project_admin_uuid = None
project_operator_uuid = None
plain_user_uuid = None
test_stub = test_lib.lib_get_test_stub()

case_flavor = dict(project_admin=                   dict(target_role='project_admin'),
                   project_operator=                dict(target_role='project_operator'),
                   project_member=                  dict(target_role='project_member'),
                   system_admin=                    dict(target_role='system_admin'),
                   )

def test():
    global project_uuid, project_admin_uuid, virtual_id_uuid, project_operator_uuid, plain_user_uuid

    flavor = case_flavor[os.environ.get('CASE_FLAVOR')]
    # 1 create project
    if flavor['target_role'] != 'system_admin':
        project_name = 'test_project'
        project = iam2_ops.create_iam2_project(project_name)
        project_uuid = project.uuid
        project_linked_account_uuid = project.linkedAccountUuid

    if flavor['target_role'] == 'project_admin':
        # 2 create virtual id
        project_admin_name = 'username'
        project_admin_password = 'password'
        project_admin_uuid = iam2_ops.create_iam2_virtual_id(project_admin_name, project_admin_password).uuid
        virtual_id_uuid = iam2_ops.create_iam2_virtual_id('usernametwo', 'password').uuid
    
        # 3 create project admin
        iam2_ops.add_iam2_virtual_ids_to_project([project_admin_uuid],project_uuid)
        attributes = [{"name": "__ProjectAdmin__", "value": project_uuid}]
        iam2_ops.add_attributes_to_iam2_virtual_id(project_admin_uuid, attributes)

        # 4 add the project admin role
        projectadminrole_uuid='55553cefbbfb42468873897c95408a43'
        iam2_ops.add_roles_to_iam2_virtual_id([projectadminrole_uuid], virtual_id_uuid)

        # login in project by project admin
        project_admin_session_uuid = iam2_ops.login_iam2_virtual_id(project_admin_name, project_admin_password)
        project_login_uuid = iam2_ops.login_iam2_project(project_name, session_uuid=project_admin_session_uuid).uuid
        # iam2_ops.remove_attributes_from_iam2_virtual_id(virtual_id_uuid, attributes)
    elif flavor['target_role'] == 'project_operator':
        project_operator_name = 'username2'
        project_operator_password = 'password'
        attributes = [{"name": "__ProjectOperator__", "value": project_uuid}]
        project_operator_uuid = iam2_ops.create_iam2_virtual_id(project_operator_name,project_operator_password,attributes=attributes).uuid
        virtual_id_uuid = iam2_ops.create_iam2_virtual_id('usernamethree','password').uuid

        # login in project by project operator
        iam2_ops.add_iam2_virtual_ids_to_project([project_operator_uuid],project_uuid)
        project_operator_session_uuid = iam2_ops.login_iam2_virtual_id(project_operator_name,project_operator_password)
        project_login_uuid = iam2_ops.login_iam2_project(project_name,session_uuid=project_operator_session_uuid).uuid
    elif flavor['target_role'] == 'project_member':
	plain_user_name = 'username'
	plain_user_password = 'password'
	plain_user_uuid = iam2_ops.create_iam2_virtual_id(plain_user_name, plain_user_password,
	                                                  project_uuid=project_uuid).uuid
	# 3 add virtual id to project
	iam2_ops.add_iam2_virtual_ids_to_project([plain_user_uuid],project_uuid)

	# 4 login in project by plain user
	plain_user_session_uuid = iam2_ops.login_iam2_virtual_id(plain_user_name, plain_user_password)

	# 4 login in project
	#project_inv=iam2_ops.get_iam2_projects_of_virtual_id(plain_user_session_uuid)
	project_login_uuid = iam2_ops.login_iam2_project(project_name, plain_user_session_uuid).uuid
    elif flavor['target_role'] == 'system_admin':
        username = "systemAdmin"
        password = 'b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86'
        vid_tst_obj = test_vid.ZstackTestVid()
        test_stub.create_system_admin(username, password, vid_tst_obj)
        virtual_id_uuid = vid_tst_obj.get_vid().uuid

        # add the system admin role
        systemadminrole_uuid='2069fe8ff0fb49efac0d4db3650a8076'
        iam2_ops.add_roles_to_iam2_virtual_id([systemadminrole_uuid], virtual_id_uuid)

        project_login_uuid = acc_ops.login_by_account(username, password)


    # Image related ops: Add, Delete, Expunge, sync image size, Update QGA, delete, expunge
    if flavor['target_role'] == 'project_member':
        statements = [{"effect": "Allow", "actions": ["org.zstack.header.vm.**"]}]
        role_uuid = iam2_ops.create_role('test_role', statements).uuid
        iam2_ops.add_roles_to_iam2_virtual_id([role_uuid], plain_user_uuid)

    vm_creation_option = test_util.VmOption()
    l3_net_uuid = test_lib.lib_get_l3_by_name(os.environ.get('l3VlanNetwork3')).uuid
    if flavor['target_role'] != 'system_admin':
        acc_ops.share_resources([project_linked_account_uuid], [l3_net_uuid])
    vm_creation_option.set_l3_uuids([l3_net_uuid])
    image_uuid = test_lib.lib_get_image_by_name("centos").uuid
    vm_creation_option.set_image_uuid(image_uuid)
    if flavor['target_role'] != 'system_admin':
        acc_ops.share_resources([project_linked_account_uuid], [image_uuid])
    instance_offering_uuid = test_lib.lib_get_instance_offering_by_name(os.environ.get('instanceOfferingName_s')).uuid
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    if flavor['target_role'] != 'system_admin':
        acc_ops.share_resources([project_linked_account_uuid], [instance_offering_uuid])
    vm_creation_option.set_name('vm_for_project_management')
    vm_creation_option.set_session_uuid(project_login_uuid)
    vm = test_stub.create_vm(image_uuid = image_uuid, session_uuid=project_login_uuid) 
    vm_uuid = vm.get_vm().uuid

    # VM related ops: Create, Delete, Expunge, Start, Stop, Suspend, Resume, Migrate
    vm_ops.stop_vm(vm_uuid, session_uuid=project_login_uuid)
    vm_ops.start_vm(vm_uuid, session_uuid=project_login_uuid)
    candidate_hosts = vm_ops.get_vm_migration_candidate_hosts(vm_uuid)
    if candidate_hosts != None and test_lib.lib_check_vm_live_migration_cap(vm.get_vm()):
        try:
            vm_ops.migrate_vm(vm_uuid, candidate_hosts.inventories[0].uuid, session_uuid=project_login_uuid)
        except:
            vm_ops.migrate_vm(vm_uuid, candidate_hosts[0].uuid, session_uuid=project_login_uuid)
    vm_ops.stop_vm(vm_uuid, force='cold', session_uuid=project_login_uuid)
    vm_ops.start_vm(vm_uuid, session_uuid=project_login_uuid)
    vm_ops.suspend_vm(vm_uuid, session_uuid=project_login_uuid)
    vm_ops.resume_vm(vm_uuid, session_uuid=project_login_uuid)
    vm_ops.destroy_vm(vm_uuid, session_uuid=project_login_uuid)
    vm_ops.expunge_vm(vm_uuid, session_uuid=project_login_uuid)

    # 11 delete
    acc_ops.logout(project_login_uuid)
    if virtual_id_uuid != None:
        iam2_ops.delete_iam2_virtual_id(virtual_id_uuid)
    if project_admin_uuid != None:
        iam2_ops.delete_iam2_virtual_id(project_admin_uuid)
    if project_operator_uuid != None:
        iam2_ops.delete_iam2_virtual_id(project_operator_uuid)
    if plain_user_uuid != None:
        iam2_ops.delete_iam2_virtual_id(plain_user_uuid)

    if flavor['target_role'] != 'system_admin':
        iam2_ops.delete_iam2_project(project_uuid)
        iam2_ops.expunge_iam2_project(project_uuid)

    test_util.test_pass('success test iam2 login in by project admin!')


def error_cleanup():
    global project_uuid, project_admin_uuid, virtual_id_uuid
    if virtual_id_uuid:
        iam2_ops.delete_iam2_virtual_id(virtual_id_uuid)
    if project_admin_uuid:
        iam2_ops.delete_iam2_virtual_id(project_admin_uuid)
    if project_uuid:
        iam2_ops.delete_iam2_project(project_uuid)
        iam2_ops.expunge_iam2_project(project_uuid)
    if plain_user_uuid != None:
        iam2_ops.delete_iam2_virtual_id(plain_user_uuid)

