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
import zstackwoodpecker.operations.zwatch_operations as zwt_ops
import os

test_stub = test_lib.lib_get_test_stub()
email_platform_uuid = None
email_endpoint_uuid = None
dingtalk_endpoint_uuid = None
http_endpoint_uuid = None
alarm_uuid = None
ps_event_sub_uuid =None
sns_topic_uuid = None
alarm_template_uuid = None

def test():
    global email_platform_uuid,email_endpoint_uuid,dingtalk_endpoint_uuid,http_endpoint_uuid,alarm_uuid,ps_event_sub_uuid,sns_topic_uuid,alarm_template_uuid
    iam2_ops.clean_iam2_enviroment()

    zone_uuid = res_ops.get_resource(res_ops.ZONE)[0].uuid
    # 3 create project
    project_name = 'test_project'
    password = \
        'b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86'
    project = iam2_ops.create_iam2_project(project_name)
    project_uuid = project.uuid
    linked_account_uuid = project.linkedAccountUuid
    attributes = [{"name": "__ProjectRelatedZone__", "value": zone_uuid}]
    iam2_ops.add_attributes_to_iam2_project(project_uuid, attributes)
    test_stub.share_admin_resource_include_vxlan_pool([linked_account_uuid])

    # 4 create projectAdmin  into project
    project_admin_name = 'projectadmin'
    project_admin_uuid = iam2_ops.create_iam2_virtual_id(project_admin_name, password).uuid
    iam2_ops.add_iam2_virtual_ids_to_project([project_admin_uuid], project_uuid)
    attributes = [{"name": "__ProjectAdmin__", "value": project_uuid}]
    iam2_ops.add_attributes_to_iam2_virtual_id(project_admin_uuid, attributes)
    project_admin_session_uuid = iam2_ops.login_iam2_virtual_id(project_admin_name,password)
    project_admin_session_uuid = iam2_ops.login_iam2_project(project_name,project_admin_session_uuid).uuid

    # 5 create zwatch resource
    smtp_server = os.environ.get('smtpServer')
    smtp_port = os.environ.get('smtpPort')
    email_platform_name = 'Alarm_email'
    email_username = os.environ.get('mailUsername')
    email_password = os.environ.get('mailPassword')
    email_platform_uuid = zwt_ops.create_sns_email_platform(smtp_server, smtp_port, email_platform_name, email_username, email_password,session_uuid=project_admin_session_uuid).uuid

    email_receiver = os.environ.get('mailUsername')
    email_endpoint_uuid = zwt_ops.create_sns_email_endpoint(email_receiver, 'test_email_endpoint', email_platform_uuid,session_uuid=project_admin_session_uuid).uuid

    url_01 = 'https://oapi.dingtalk.com/robot/send?access_token' \
             '=0be899d4bd0a7629961a5ccd3035dfba30d084b57944897838f1b601006dd153'
    name_01 = 'dingtalkAtPerson'
    dingtalk_endpoint_uuid = zwt_ops.create_sns_dingtalk_endpoint(url_01, name_01, at_all=False,session_uuid=project_admin_session_uuid).uuid
    http_endpoint_name = 'http'
    url = 'http://localhost:8080/webhook-url'
    http_username = 'url-username'
    http_password = 'url-password'
    http_endpoint_uuid = zwt_ops.create_sns_http_endpoint(url, http_endpoint_name, http_username, http_password,session_uuid=project_admin_session_uuid).uuid

    sns_topic_uuid = zwt_ops.create_sns_topic('sns_topic_01',session_uuid=project_admin_session_uuid).uuid
    zwt_ops.subscribe_sns_topic(sns_topic_uuid, dingtalk_endpoint_uuid,session_uuid=project_admin_session_uuid)
    zwt_ops.subscribe_sns_topic(sns_topic_uuid, email_endpoint_uuid,session_uuid=project_admin_session_uuid)
    zwt_ops.subscribe_sns_topic(sns_topic_uuid, http_endpoint_uuid,session_uuid=project_admin_session_uuid)

    namespace = 'ZStack/Volume'
    actions = [{"actionUuid": sns_topic_uuid, "actionType": "sns"}]
    comparisonOperator = 'GreaterThanOrEqualTo'
    repeat_interval = 20
    period = 10
    threshold = 5
    metric_name = 'TotalVolumeCount'
    alarm_uuid = zwt_ops.create_alarm(comparisonOperator, period, threshold, namespace, metric_name, actions=actions,repeat_interval=repeat_interval,session_uuid=project_admin_session_uuid).uuid

    ps_actions = [{"actionUuid": sns_topic_uuid, "actionType": "sns"}]
    ps_namespace = 'ZStack/PrimaryStorage'
    ps_disconnected = 'PrimaryStorageDisconnected'
    ps_event_sub_uuid = zwt_ops.subscribe_event(ps_namespace, ps_disconnected, ps_actions, session_uuid=project_admin_session_uuid).uuid

    application_platform_type = 'Email'
    alarm_template_name = 'my-alarm-template'
    alarm_template = '${ALARM_NAME} Change status to ${ALARM_CURRENT_STATUS}' \
                     'ALARM_UUID:${ALARM_UUID}' \
                     'keyword1:ThisWordIsKeyWord' \
                     'keyword2:TemplateForAlarmOn' \
                     '(Using for template changes email check)'
    alarm_template_uuid = zwt_ops.create_sns_text_template(alarm_template_name,
                                                             application_platform_type,
                                                             alarm_template,
                                                             default_template=False, session_uuid=project_admin_session_uuid).uuid

    acc_ops.logout(project_admin_session_uuid)

    # 6 delete project
    iam2_ops.delete_iam2_project(project_uuid)
    iam2_ops.expunge_iam2_project(project_uuid)

    # 7 cascade test
    try:
        test_stub.check_resource_not_exist(email_platform_uuid,res_ops.SNS_EMAIL_PLATFORM)
    except:
        test_util.test_logger("email platform should not be delete ,success")
    test_stub.check_resource_not_exist(email_endpoint_uuid,res_ops.SNS_APPLICATION_ENDPOINT)
    test_stub.check_resource_not_exist(dingtalk_endpoint_uuid,res_ops.SNS_APPLICATION_ENDPOINT)
    test_stub.check_resource_not_exist(http_endpoint_uuid,res_ops.SNS_APPLICATION_ENDPOINT)
    test_stub.check_resource_not_exist(alarm_uuid,res_ops.ALARM)
    test_stub.check_resource_not_exist(ps_event_sub_uuid,res_ops.EVENT_SUBSCRIPTION)
    test_stub.check_resource_not_exist(sns_topic_uuid,res_ops.SNS_TOPIC)
    test_stub.check_resource_not_exist(alarm_template_uuid,res_ops.SNS_TEXT_TEMPLATE)

    zwt_ops.delete_sns_application_platform(email_platform_uuid)

    iam2_ops.clean_iam2_enviroment()
    test_util.test_pass("success test project retired")


def error_cleanup():
    global email_platform_uuid,email_endpoint_uuid,dingtalk_endpoint_uuid,http_endpoint_uuid,alarm_uuid,ps_event_sub_uuid,sns_topic_uuid,alarm_template_uuid
    iam2_ops.clean_iam2_enviroment()
    if email_platform_uuid:
        zwt_ops.delete_sns_application_platform(email_platform_uuid)
    if email_endpoint_uuid:
        zwt_ops.delete_sns_application_endpoint(email_endpoint_uuid)
    if dingtalk_endpoint_uuid:
        zwt_ops.delete_sns_application_endpoint(dingtalk_endpoint_uuid)
    if http_endpoint_uuid:
        zwt_ops.delete_sns_application_endpoint(http_endpoint_uuid)
    if alarm_uuid:
        zwt_ops.delete_alarm(alarm_uuid)
    if ps_event_sub_uuid:
        zwt_ops.unsubscribe_event(ps_event_sub_uuid)
    if sns_topic_uuid:
        zwt_ops.delete_sns_topic(sns_topic_uuid)
    if alarm_template_uuid:
        zwt_ops.delete_sns_text_template(alarm_template_uuid)
