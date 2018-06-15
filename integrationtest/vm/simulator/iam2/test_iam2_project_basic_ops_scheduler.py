'''
test iam2 login by platform admin

# 1 create project
# 2 create virtual id
# 3 create project admin
# 4 login in project by project admin
# 5 create virtual id group
# 6 create role
# 7 add virtual id into project and group
# 8 add/remove roles to/from virtual id (group)
# 9 create/delete project operator
# 10 remove virtual ids from group and project
# 11 delete

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

project_uuid = None
virtual_id_uuid = None
project_admin_uuid = None
test_stub = test_lib.lib_get_test_stub()


def test():
    global project_uuid, project_admin_uuid, virtual_id_uuid

    # 1 create project
    project_name = 'test_project'
    project = iam2_ops.create_iam2_project(project_name)
    project_uuid = project.uuid
    project_linked_account_uuid = project.linkedAccountUuid

    # 2 create virtual id
    project_admin_name = 'username'
    project_admin_password = 'password'
    project_admin_uuid = iam2_ops.create_iam2_virtual_id(project_admin_name, project_admin_password).uuid
    virtual_id_uuid = iam2_ops.create_iam2_virtual_id('usernametwo', 'password').uuid

    # 3 create project admin
    iam2_ops.add_iam2_virtual_ids_to_project([project_admin_uuid],project_uuid)
    attributes = [{"name": "__ProjectAdmin__", "value": project_uuid}]
    iam2_ops.add_attributes_to_iam2_virtual_id(project_admin_uuid, attributes)

    # 4 login in project by project admin
    project_admin_session_uuid = iam2_ops.login_iam2_virtual_id(project_admin_name, project_admin_password)
    project_login_uuid = iam2_ops.login_iam2_project(project_name, session_uuid=project_admin_session_uuid).uuid
    # iam2_ops.remove_attributes_from_iam2_virtual_id(virtual_id_uuid, attributes)

    vm_creation_option = test_util.VmOption()
    l3_net_uuid = test_lib.lib_get_l3_by_name(os.environ.get('l3VlanNetwork3')).uuid
    acc_ops.share_resources([project_linked_account_uuid], [l3_net_uuid])
    vm_creation_option.set_l3_uuids([l3_net_uuid])
    image_uuid = test_lib.lib_get_image_by_name("centos").uuid
    vm_creation_option.set_image_uuid(image_uuid)
    acc_ops.share_resources([project_linked_account_uuid], [image_uuid])
    instance_offering_uuid = test_lib.lib_get_instance_offering_by_name(os.environ.get('instanceOfferingName_s')).uuid
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    acc_ops.share_resources([project_linked_account_uuid], [instance_offering_uuid])
    vm_creation_option.set_name('vm_for_project_management')
    vm_creation_option.set_session_uuid(project_login_uuid)
    vm = test_stub.create_vm(image_uuid = image_uuid, session_uuid=project_login_uuid) 

    # scheduler ops:
    start_date = int(time.time())
    schd_job1 = schd_ops.create_scheduler_job('simple_start_vm_scheduler', 'simple_start_vm_scheduler', vm.get_vm().uuid, 'startVm', None, session_uuid=project_login_uuid)
    schd_trigger1 = schd_ops.create_scheduler_trigger('simple_start_vm_scheduler', start_date+5, None, 15, 'simple', session_uuid=project_login_uuid)
    schd_ops.add_scheduler_job_to_trigger(schd_trigger1.uuid, schd_job1.uuid, session_uuid=project_login_uuid)
    schd_ops.change_scheduler_state(schd_job1.uuid, 'disable', session_uuid=project_login_uuid)
    schd_ops.change_scheduler_state(schd_job1.uuid, 'enable', session_uuid=project_login_uuid)
    schd_ops.remove_scheduler_job_from_trigger(schd_trigger1.uuid, schd_job1.uuid, session_uuid=project_login_uuid)
    schd_ops.del_scheduler_job(schd_job1.uuid, session_uuid=project_login_uuid)
    schd_ops.del_scheduler_trigger(schd_trigger1.uuid, session_uuid=project_login_uuid)
    schd_ops.get_current_time()
    vm_ops.destroy_vm(vm.get_vm().uuid, session_uuid=project_login_uuid)
    vm_ops.expunge_vm(vm.get_vm().uuid, session_uuid=project_login_uuid)

    # certificate
    cert = net_ops.create_certificate('certificate_for_pm', 'fake certificate', session_uuid=project_login_uuid)
    net_ops.delete_certificate(cert.uuid, session_uuid=project_login_uuid)

    # 11 delete
    acc_ops.logout(project_login_uuid)
    iam2_ops.delete_iam2_virtual_id(virtual_id_uuid)
    iam2_ops.delete_iam2_virtual_id(project_admin_uuid)
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