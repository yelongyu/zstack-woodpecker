'''
test iam2 delete zone cascading operations

@author: rhZhou
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.iam2_operations as iam2_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.operations.iam2_ticket_operations as ticket_ops
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.zone_operations as zone_ops

#import simulator.test_stub as test_stub

test_stub = test_lib.lib_get_test_stub()

new_zone_uuid = None

def test():
    global new_zone_uuid
    iam2_ops.clean_iam2_enviroment()

    # 1 create new zone
    new_zone_uuid = test_stub.create_zone().uuid

    # 2 create platform admin related new zone
    platform_admin_name = 'platformadmin'
    password = \
        'b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86'

    platform_admin_uuid = iam2_ops.create_iam2_virtual_id(platform_admin_name, password).uuid
    attributes = [{"name": "__PlatformAdmin__"}, {"name": "__PlatformAdminRelatedZone__", "value": new_zone_uuid}]
    iam2_ops.add_attributes_to_iam2_virtual_id(platform_admin_uuid, attributes)

    # 3 create project
    project_name = 'test_project'
    project = iam2_ops.create_iam2_project(project_name)
    project_uuid = project.uuid
    linked_account_uuid = project.linkedAccountUuid
    attributes = [{"name": "__ProjectRelatedZone__", "value": new_zone_uuid}]
    iam2_ops.add_attributes_to_iam2_project(project_uuid, attributes)

    # 4 create projectAdmin and virtual id into project
    project_admin_name = 'projectadmin'
    project_admin_uuid = iam2_ops.create_iam2_virtual_id(project_admin_name, password).uuid
    iam2_ops.add_iam2_virtual_ids_to_project([project_admin_uuid], project_uuid)
    attributes = [{"name": "__ProjectAdmin__", "value": project_uuid}]
    iam2_ops.add_attributes_to_iam2_virtual_id(project_admin_uuid, attributes)

    username = 'username'
    virtual_id_uuid = iam2_ops.create_iam2_virtual_id(username, password).uuid
    iam2_ops.add_iam2_virtual_ids_to_project([virtual_id_uuid], project_uuid)
    action = "org.zstack.ticket.**"
    statements = [{"effect": "Allow", "actions": [action]}]
    role_uuid = iam2_ops.create_role('test_role', statements).uuid
    iam2_ops.add_policy_statements_to_role(role_uuid, statements)
    statement_uuid = iam2_ops.get_policy_statement_uuid_of_role(role_uuid, action)
    iam2_ops.add_roles_to_iam2_virtual_id([role_uuid], virtual_id_uuid)
    virtual_id_session = iam2_ops.login_iam2_virtual_id(username, password)
    virtual_id_session = iam2_ops.login_iam2_project(project_name, virtual_id_session).uuid


    # 5 create ticket
    ticket = test_stub.create_vm_ticket(virtual_id_uuid, project_uuid, virtual_id_session)
    ticket_02 = test_stub.create_vm_ticket(virtual_id_uuid, project_uuid, virtual_id_session, name='new ticket',
                                           request_name='ticket-vm-2')
    acc_ops.logout(virtual_id_session)

    ticket_ops.change_ticket_status(ticket.uuid, 'reject')

    # 6 delete Zone
    zone_ops.delete_zone(new_zone_uuid)

    # 7 cascade test
    # test for platformAdmin
    cond = res_ops.gen_query_conditions('virtualIDUuid', '=', platform_admin_uuid)
    cond_02 = res_ops.gen_query_conditions('name', '=', "__PlatformAdminRelatedZone__", cond)
    attributes = res_ops.query_resource(res_ops.IAM2_VIRTUAL_ID_ATTRIBUTE, cond_02)
    if attributes:
        test_util.test_fail('the attributes:uuid[%s] name[%s] is still exist after delete the new zone[%s]' % (
        attributes[0].uuid, attributes[0].name, new_zone_uuid))

    # test for project
    cond = res_ops.gen_query_conditions('uuid', '=', project_uuid)
    project_inv = res_ops.query_resource(res_ops.IAM2_PROJECT, cond)
    if project_inv:
        test_util.test_fail(
            'the project[%s] is still exist after delete the new zone[%s]' % (project_inv[0].uuid, new_zone_uuid))

    cond = res_ops.gen_query_conditions('virtualIDUuid', '=', project_admin_uuid)
    cond_02 = res_ops.gen_query_conditions('name', '=', "__ProjectAdmin__", cond)
    attributes = res_ops.query_resource(res_ops.IAM2_VIRTUAL_ID_ATTRIBUTE, cond_02)
    if attributes:
        test_util.test_fail('the attributes:uuid[%s] name[%s] is still exist after delete the new zone[%s]' % (
            attributes[0].uuid, attributes[0].name, new_zone_uuid))

    platform_admin_session = iam2_ops.login_iam2_virtual_id(platform_admin_name, password)
    project_admin_session = iam2_ops.login_iam2_virtual_id(project_admin_name, password)
    virtual_id_session = iam2_ops.login_iam2_virtual_id(username, password)

    try:
        iam2_ops.login_iam2_project(project_name, project_admin_session)
        test_util.test_fail("can't login deleted project ,fail!")
    except:
        test_util.test_logger("can't login deleted project ,success!")

    try:
        iam2_ops.login_iam2_project(project_name, virtual_id_session)
        test_util.test_fail("can't login deleted project ,fail!")
    except:
        test_util.test_logger("can't login deleted project ,success!")

    # test for ticket

    cond = res_ops.gen_query_conditions('uuid', '=', ticket.uuid)
    ticket_inv = res_ops.query_resource(res_ops.TICKET, cond)
    if ticket_inv:
        test_util.test_fail(
            "Ticket [%s] is still exist after delete the zone[%s]" % (ticket_inv[0].uuid, new_zone_uuid))

    cond = res_ops.gen_query_conditions('uuid', '=', ticket_02.uuid)
    ticket_02_inv = res_ops.query_resource(res_ops.TICKET, cond)
    if ticket_02_inv:
        test_util.test_fail(
            "Ticket [%s] is still exist after delete the zone[%s]" % (ticket_02_inv[0].uuid, new_zone_uuid))

    iam2_ops.clean_iam2_enviroment()
    test_util.test_pass("success test project retired")

def error_cleanup():
    global new_zone_uuid
    if new_zone_uuid:
        zone_ops.delete_zone(new_zone_uuid)
    iam2_ops.clean_iam2_enviroment()
