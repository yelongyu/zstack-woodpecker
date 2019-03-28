'''
test iam2 zwatch operations by platform admin/operator/member

# 1 create project
# 2 create virtual id (project admin/operator/member)
# 3 operations on zwatch with virtual id
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
        virtual_id_uuid = vid_tst_obj.get_vid().uuid
        test_stub.create_system_admin(username, password, vid_tst_obj)
        project_login_uuid = acc_ops.login_by_account(username, password)


    # Image related ops: Add, Delete, Expunge, sync image size, Update QGA, delete, expunge
    if flavor['target_role'] == 'project_member':
        statements = [{"effect": "Allow", "actions": ["org.zstack.sns.**"]}, {"effect": "Allow", "actions": ["org.zstack.zwatch.**"]}]
        role_uuid = iam2_ops.create_role('test_role', statements).uuid
        iam2_ops.add_roles_to_iam2_virtual_id([role_uuid], plain_user_uuid)

    # create platform
    smtp_server = os.environ.get('smtpServer')
    smtp_port = os.environ.get('smtpPort')
    email_platform_name = 'Alarm_email'
    email_username = os.environ.get('mailUsername')
    email_password = os.environ.get('mailPassword')
    email_platform = zwt_ops.create_sns_email_platform(smtp_server, smtp_port, email_platform_name, email_username, email_password, session_uuid=project_login_uuid)
    email_platform_uuid = email_platform.uuid
    cond=res_ops.gen_query_conditions('uuid','=',email_platform_uuid)
    inv = res_ops.query_resource(res_ops.SNS_EMAIL_PLATFORM,cond, session_uuid=project_login_uuid)
    if not inv:
        test_util.test_fail('create sns email platform failed')
    try:
        zwt_ops.validate_sns_email_platform(email_platform_uuid)
    except:
        test_util.test_fail('Validate SNS Email Platform Failed, Email Plarform: %s' % email_platform_uuid)

    # create endpoint
    email_receiver = os.environ.get('mailUsername')
    email_endpoint_name = os.environ.get('mailPassword')
    email_endpoint_uuid = zwt_ops.create_sns_email_endpoint(email_receiver, email_endpoint_name, email_platform_uuid, session_uuid=project_login_uuid).uuid
    cond=res_ops.gen_query_conditions('uuid','=',email_endpoint_uuid)
    inv=res_ops.query_resource(res_ops.SNS_EMAIL_ENDPOINT,cond, session_uuid=project_login_uuid)
    if not inv:
        test_util.test_fail('create sns email endpoint failed')
    http_endpoint_name='http'
    url = 'http://localhost:8080/webhook-url'
    http_username='url-username'
    http_password='url-password'
    http_endpoint=zwt_ops.create_sns_http_endpoint(url,http_endpoint_name,http_username,http_password, session_uuid=project_login_uuid)
    http_endpoint_uuid=http_endpoint.uuid
    cond=res_ops.gen_query_conditions('uuid','=',http_endpoint_uuid)
    inv=res_ops.query_resource(res_ops.SNS_HTTP_ENDPOINT,cond, session_uuid=project_login_uuid)
    if not inv:
        test_util.test_fail('create sns http endpoint failed')

    # create sns topic and query system-in topic
    sns_topic_uuid = zwt_ops.create_sns_topic('sns_topic_01', session_uuid=project_login_uuid).uuid
    zwt_ops.subscribe_sns_topic(sns_topic_uuid, email_endpoint_uuid, session_uuid=project_login_uuid)
    cond=res_ops.gen_query_conditions('endpoints.uuid','=',email_endpoint_uuid)
    inv=res_ops.query_resource(res_ops.SNS_TOPIC,cond, session_uuid=project_login_uuid)
    if not inv:
        test_util.test_fail('create and subscribe snstopic failed')
    cond = res_ops.gen_query_conditions('name', '=', 'system-alarm')
    system_alarm_topic = res_ops.query_resource(res_ops.SNS_TOPIC, cond)[0]
    system_alarm_topic_uuid=system_alarm_topic.uuid
    acc_ops.share_resources([project_linked_account_uuid], [system_alarm_topic_uuid])
    cond = res_ops.gen_query_conditions('name', '=', 'system-alarm')
    system_alarm_topic = res_ops.query_resource(res_ops.SNS_TOPIC, cond)[0]
    system_alarm_topic_uuid=system_alarm_topic.uuid
    zwt_ops.subscribe_sns_topic(system_alarm_topic_uuid, email_endpoint_uuid, session_uuid=project_login_uuid)
    cond=res_ops.gen_query_conditions('endpoints.uuid','=',email_endpoint_uuid)
    inv=res_ops.query_resource(res_ops.SNS_TOPIC,cond, session_uuid=project_login_uuid)
    if not inv:
        test_util.test_fail('subscribe system-alarm topic failed')
    cond = res_ops.gen_query_conditions('name','=','api')
    api_topic= res_ops.query_resource(res_ops.SNS_TOPIC,cond)[0]
    api_topic_uuid=api_topic.uuid
    acc_ops.share_resources([project_linked_account_uuid], [api_topic_uuid])
    cond = res_ops.gen_query_conditions('name','=','api')
    api_topic= res_ops.query_resource(res_ops.SNS_TOPIC,cond, session_uuid=project_login_uuid)[0]
    api_topic_uuid=api_topic.uuid
    zwt_ops.subscribe_sns_topic(api_topic_uuid,http_endpoint_uuid, session_uuid=project_login_uuid)
    cond = res_ops.gen_query_conditions('endpointUuid','=',http_endpoint_uuid)
    cond = res_ops.gen_query_conditions('topicUuid','=',api_topic_uuid)
    inv=res_ops.query_resource(res_ops.SNS_TOPIC_SUBSCRIBER,cond, session_uuid=project_login_uuid)
    if not inv:
        test_util.test_fail('subscribe api topic failed')

    # subscribe event
    namespace = 'ZStack/VM'
    actions = [{"actionUuid": sns_topic_uuid, "actionType": "sns"}]
    labels = [{"key": "NewState", "op": "Equal", "value": "Disconnected"}]
    event_name = 'VMStateChangedOnHost'
    event_sub_uuid = zwt_ops.subscribe_event(namespace, event_name, actions, labels, session_uuid=project_login_uuid).uuid
    cond = res_ops.gen_query_conditions('uuid', '=', event_sub_uuid)
    event_subscription = res_ops.query_resource(res_ops.EVENT_SUBSCRIPTION, cond, session_uuid=project_login_uuid)
    if not event_subscription:
        test_util.test_fail('Subscribe event failed')

    #update endpoint
    new_name='endpointNewName'
    new_description='endpoint new description'
    zwt_ops.update_sns_application_endpoint(email_endpoint_uuid,new_name,new_description, session_uuid=project_login_uuid)
    cond= res_ops.gen_query_conditions('uuid','=',email_endpoint_uuid)
    inv =res_ops.query_resource(res_ops.SNS_APPLICATION_ENDPOINT,cond, session_uuid=project_login_uuid)[0]
    if inv.name!=new_name or inv.description!=new_description:
        test_util.test_fail('test update email endpoint failed')
    zwt_ops.update_sns_application_endpoint(http_endpoint_uuid,new_name,new_description, session_uuid=project_login_uuid)
    cond= res_ops.gen_query_conditions('uuid','=',http_endpoint_uuid)
    inv =res_ops.query_resource(res_ops.SNS_APPLICATION_ENDPOINT,cond, session_uuid=project_login_uuid)[0]
    if inv.name!=new_name or inv.description!=new_description:
        test_util.test_fail('test update http endpoint failed')
    new_name_platform='platformNewName'
    new_description_platform='platformNewName'
    zwt_ops.update_sns_application_platform(email_platform_uuid,new_name_platform,new_description_platform, session_uuid=project_login_uuid)
    cond= res_ops.gen_query_conditions('uuid','=',email_platform_uuid)
    inv =res_ops.query_resource(res_ops.SNS_APPLICATION_PLATFORM,cond, session_uuid=project_login_uuid)[0]
    if inv.name!=new_name_platform or inv.description!=new_description_platform:
        test_util.test_fail('test update email platform failed')

    #change state
    state_event = 'disable'
    state_result = 'Disabled'
    zwt_ops.change_sns_topic_state(system_alarm_topic_uuid,state_event, session_uuid=project_login_uuid)
    cond=res_ops.gen_query_conditions('uuid','=',system_alarm_topic_uuid)
    inv=res_ops.query_resource(res_ops.SNS_TOPIC,cond, session_uuid=project_login_uuid)[0]
    if inv.state!=state_result:
        test_util.test_fail('change system alarm topic state failed')
    zwt_ops.change_sns_topic_state(api_topic_uuid, state_event, session_uuid=project_login_uuid)
    cond = res_ops.gen_query_conditions('uuid', '=', api_topic_uuid)
    inv = res_ops.query_resource(res_ops.SNS_TOPIC, cond, session_uuid=project_login_uuid)[0]
    if inv.state != state_result:
        test_util.test_fail('change api topic state failed')
    zwt_ops.change_sns_application_endpoint_state(email_endpoint_uuid,state_event, session_uuid=project_login_uuid)
    cond = res_ops.gen_query_conditions('uuid', '=', email_endpoint_uuid)
    inv = res_ops.query_resource(res_ops.SNS_APPLICATION_ENDPOINT, cond, session_uuid=project_login_uuid)[0]
    if inv.state != state_result:
        test_util.test_fail('change email endpoint state failed')
    zwt_ops.change_sns_application_endpoint_state(http_endpoint_uuid,state_event, session_uuid=project_login_uuid)
    cond = res_ops.gen_query_conditions('uuid', '=', http_endpoint_uuid)
    inv = res_ops.query_resource(res_ops.SNS_APPLICATION_ENDPOINT, cond, session_uuid=project_login_uuid)[0]
    if inv.state != state_result:
        test_util.test_fail('change http endpoint state failed')
    zwt_ops.change_sns_application_platform_state(email_platform_uuid,state_event, session_uuid=project_login_uuid)
    cond = res_ops.gen_query_conditions('uuid', '=', email_platform_uuid)
    inv = res_ops.query_resource(res_ops.SNS_APPLICATION_PLATFORM, cond, session_uuid=project_login_uuid)[0]
    if inv.state != state_result:
        test_util.test_fail('change email platform state failed')

    # test recover and delete
    state_event='enable'
    state_result='Enabled'
    zwt_ops.change_sns_topic_state(system_alarm_topic_uuid,state_event, session_uuid=project_login_uuid)
    cond=res_ops.gen_query_conditions('uuid','=',system_alarm_topic_uuid)
    inv=res_ops.query_resource(res_ops.SNS_TOPIC,cond, session_uuid=project_login_uuid)[0]
    if inv.state!=state_result:
        test_util.test_fail('change system alarm topic state failed')
    zwt_ops.change_sns_topic_state(api_topic_uuid, state_event, session_uuid=project_login_uuid)
    cond = res_ops.gen_query_conditions('uuid', '=', api_topic_uuid)
    inv = res_ops.query_resource(res_ops.SNS_TOPIC, cond, session_uuid=project_login_uuid)[0]
    if inv.state != state_result:
        test_util.test_fail('change api topic state failed')
    zwt_ops.unsubscribe_event(event_sub_uuid, session_uuid=project_login_uuid)
    cond = res_ops.gen_query_conditions('uuid', '=', event_sub_uuid)
    event_subscription = res_ops.query_resource(res_ops.EVENT_SUBSCRIPTION, cond, session_uuid=project_login_uuid)
    if event_subscription:
        test_util.test_fail('unsubscribe event failed')
    zwt_ops.unsubscribe_sns_topic(sns_topic_uuid, email_endpoint_uuid)
    cond =res_ops.gen_query_conditions('endpointUuid','=',email_endpoint_uuid)
    cond=res_ops.gen_query_conditions('topicUuid','=',sns_topic_uuid,cond)
    inv = res_ops.query_resource(res_ops.SNS_TOPIC_SUBSCRIBER,cond, session_uuid=project_login_uuid)
    if inv:
        test_util.test_fail('unsubscribe sns topic failed')
    zwt_ops.unsubscribe_sns_topic(system_alarm_topic_uuid, email_endpoint_uuid, session_uuid=project_login_uuid)
    cond =res_ops.gen_query_conditions('endpointUuid','=',email_endpoint_uuid)
    cond=res_ops.gen_query_conditions('topicUuid','=',system_alarm_topic_uuid,cond)
    inv = res_ops.query_resource(res_ops.SNS_TOPIC_SUBSCRIBER,cond, session_uuid=project_login_uuid)
    if inv:
        test_util.test_fail('unsubscribe system alarm topic failed')
    zwt_ops.unsubscribe_sns_topic(api_topic_uuid, http_endpoint_uuid, session_uuid=project_login_uuid)
    cond =res_ops.gen_query_conditions('endpointUuid','=',http_endpoint_uuid)
    cond=res_ops.gen_query_conditions('topicUuid','=',api_topic_uuid,cond)
    inv = res_ops.query_resource(res_ops.SNS_TOPIC_SUBSCRIBER,cond, session_uuid=project_login_uuid)
    if inv:
        test_util.test_fail('unsubscribe api topic failed')
    zwt_ops.delete_sns_topic(sns_topic_uuid, session_uuid=project_login_uuid)
    cond=res_ops.gen_query_conditions('uuid','=',sns_topic_uuid)
    inv = res_ops.query_resource(res_ops.SNS_TOPIC, cond, session_uuid=project_login_uuid)
    if inv:
        test_util.test_fail('delete sns topic failed')
    zwt_ops.delete_sns_application_endpoint(http_endpoint_uuid, session_uuid=project_login_uuid)
    cond=res_ops.gen_query_conditions('uuid','=',http_endpoint_uuid)
    inv = res_ops.query_resource(res_ops.SNS_APPLICATION_ENDPOINT, cond, session_uuid=project_login_uuid)
    if inv:
        test_util.test_fail('delete http endpoint failed')
    zwt_ops.delete_sns_application_endpoint(email_endpoint_uuid, session_uuid=project_login_uuid)
    cond=res_ops.gen_query_conditions('uuid','=',email_endpoint_uuid)
    inv = res_ops.query_resource(res_ops.SNS_APPLICATION_ENDPOINT, cond, session_uuid=project_login_uuid)
    if inv:
        test_util.test_fail('delete email endpoint failed')
    zwt_ops.delete_sns_application_platform(email_platform_uuid, session_uuid=project_login_uuid)
    cond=res_ops.gen_query_conditions('uuid','=',email_platform_uuid)
    inv = res_ops.query_resource(res_ops.SNS_APPLICATION_PLATFORM, cond, session_uuid=project_login_uuid)
    if inv:
        test_util.test_fail('delete email platform failed')

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

