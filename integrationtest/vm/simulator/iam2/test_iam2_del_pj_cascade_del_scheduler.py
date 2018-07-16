'''

Test for iam2 delete project cascade delete scheduler.

@author: ronghao.zhou
'''

import os
import time
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.scheduler_operations as schd_ops
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
#import simulator.test_stub as test_stub
import zstackwoodpecker.operations.iam2_operations as iam2_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.account_operations as acc_ops

test_stub = test_lib.lib_get_test_stub()
vm = None
schd_job1 = None
schd_trigger1 = None
schd_job2 = None
schd_trigger2 = None


def test():
    global vm
    global schd_job1
    global schd_job2
    global schd_trigger1
    global schd_trigger2
    iam2_ops.clean_iam2_enviroment()

    zone_uuid = res_ops.get_resource(res_ops.ZONE)[0].uuid
    # 1 create project
    project_name = 'test_project'
    password = \
        'b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86'
    project = iam2_ops.create_iam2_project(project_name)
    project_uuid = project.uuid
    linked_account_uuid = project.linkedAccountUuid
    attributes = [{"name": "__ProjectRelatedZone__", "value": zone_uuid}]
    iam2_ops.add_attributes_to_iam2_project(project_uuid, attributes)
    test_stub.share_admin_resource_include_vxlan_pool([linked_account_uuid])

    # 2 create projectAdmin  into project
    project_admin_name = 'projectadmin'
    project_admin_uuid = iam2_ops.create_iam2_virtual_id(project_admin_name, password).uuid
    iam2_ops.add_iam2_virtual_ids_to_project([project_admin_uuid], project_uuid)
    attributes = [{"name": "__ProjectAdmin__", "value": project_uuid}]
    iam2_ops.add_attributes_to_iam2_virtual_id(project_admin_uuid, attributes)
    project_admin_session_uuid = iam2_ops.login_iam2_virtual_id(project_admin_name,password)
    project_admin_session_uuid = iam2_ops.login_iam2_project(project_name,project_admin_session_uuid).uuid

    # 3 create scheduler job and trigger
    vm = test_stub.create_vm(session_uuid=project_admin_session_uuid)
    start_date = int(time.time())
    schd_job1 = schd_ops.create_scheduler_job('simple_stop_vm_scheduler', 'simple_stop_vm_scheduler', vm.get_vm().uuid, 'stopVm', None,session_uuid=project_admin_session_uuid)
    schd_trigger1 = schd_ops.create_scheduler_trigger('simple_stop_vm_scheduler', start_date+60, None, 120, 'simple',session_uuid=project_admin_session_uuid)
    schd_ops.add_scheduler_job_to_trigger(schd_trigger1.uuid, schd_job1.uuid,session_uuid=project_admin_session_uuid)

    schd_job2 = schd_ops.create_scheduler_job('simple_start_vm_scheduler', 'simple_start_vm_scheduler', vm.get_vm().uuid, 'startVm', None,session_uuid=project_admin_session_uuid)
    schd_trigger2 = schd_ops.create_scheduler_trigger('simple_start_vm_scheduler', start_date+120, None, 120, 'simple',session_uuid=project_admin_session_uuid)
    schd_ops.add_scheduler_job_to_trigger(schd_trigger2.uuid, schd_job2.uuid,session_uuid=project_admin_session_uuid)

    acc_ops.logout(project_admin_session_uuid)

    # 4 delete project
    iam2_ops.delete_iam2_project(project_uuid)
    iam2_ops.expunge_iam2_project(project_uuid)

    # 5 check for cascade delete
    test_stub.check_resource_not_exist(schd_job1.uuid,res_ops.SCHEDULERJOB)
    test_stub.check_resource_not_exist(schd_job2.uuid,res_ops.SCHEDULERJOB)
    test_stub.check_resource_not_exist(schd_trigger1.uuid,res_ops.SCHEDULERTRIGGER)
    test_stub.check_resource_not_exist(schd_trigger2.uuid,res_ops.SCHEDULERTRIGGER)

    vm.clean()
    iam2_ops.clean_iam2_enviroment()
    test_util.test_pass('Create Simple VM Stop Start Scheduler Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    global schd_job1
    global schd_job2
    global schd_trigger1
    global schd_trigger2
    iam2_ops.clean_iam2_enviroment()
    if vm:
        vm.clean()
    if schd_job1:
        schd_ops.del_scheduler_job(schd_job1.uuid)
    if schd_trigger1:
        schd_ops.del_scheduler_trigger(schd_trigger1.uuid)
    if schd_job2:
        schd_ops.del_scheduler_job(schd_job2.uuid)
    if schd_trigger2:
        schd_ops.del_scheduler_trigger(schd_trigger2.uuid)
