'''
test basic function of event subscribetion,system-alarm topic,api alarm topic with email and http

------------------------------------------------------------------------------------------------------------
# 1 create email paltform and validate it                                                                  #
# 2 create twp endpoint,one email endpoint ,another http endpoint                                          #
# 3 create sns topic and query 'system-alarm' topic and 'api' topic ,subscribe them                        #
# 4 the sns topic subscribe an event                                                                       #
# 5 update both endpoint                                                                                   #
# 6 change all state                                                                                       #
# 7 test recover and delete                                                                                #
------------------------------------------------------------------------------------------------------------

@author: rhZhou
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.zwatch_operations as zwt_ops
import os

email_platform_uuid = None
email_endpoint_uuid = None
http_endpoint_uuid = None
sns_topic_uuid = None

def test():

    global email_platform_uuid, email_endpoint_uuid,http_endpoint_uuid, sns_topic_uuid

    # create platform
    smtp_server = os.environ.get('smtpServer')
    smtp_port = os.environ.get('smtpPort')
    email_platform_name = 'Alarm_email'
    email_username = os.environ.get('emailUsername')
    email_password = os.environ.get('emailPassword')
    email_platform = zwt_ops.create_sns_email_platform(smtp_server, smtp_port, email_platform_name, email_username, email_password)
    email_platform_uuid = email_platform.uuid
    cond=res_ops.gen_query_conditions('uuid','=',email_platform_uuid)
    inv = res_ops.query_resource(res_ops.SNS_EMAIL_PLATFORM,cond)
    if not inv:
        test_util.test_fail('create sns email platform failed')
    try:
        zwt_ops.validate_sns_email_platform(email_platform_uuid)
    except:
        test_util.test_fail('Validate SNS Email Platform Failed, Email Plarform: %s' % email_platform_uuid)

    # create endpoint
    email_receiver = os.environ.get('emailUsername')
    email_endpoint_name = os.environ.get('emailPassword')
    email_endpoint_uuid = zwt_ops.create_sns_email_endpoint(email_receiver, email_endpoint_name, email_platform_uuid).uuid
    cond=res_ops.gen_query_conditions('uuid','=',email_endpoint_uuid)
    inv=res_ops.query_resource(res_ops.SNS_EMAIL_ENDPOINT,cond)
    if not inv:
        test_util.test_fail('create sns email endpoint failed')
    http_endpoint_name='http'
    url = 'http://localhost:8080/webhook-url'
    http_username='url-username'
    http_password='url-password'
    http_endpoint=zwt_ops.create_sns_http_endpoint(url,http_endpoint_name,http_username,http_password)
    http_endpoint_uuid=http_endpoint.uuid
    cond=res_ops.gen_query_conditions('uuid','=',http_endpoint_uuid)
    inv=res_ops.query_resource(res_ops.SNS_HTTP_ENDPOINT,cond)
    if not inv:
        test_util.test_fail('create sns http endpoint failed')

    # create sns topic and query system-in topic
    sns_topic_uuid = zwt_ops.create_sns_topic('sns_topic_01').uuid
    zwt_ops.subscribe_sns_topic(sns_topic_uuid, email_endpoint_uuid)
    cond=res_ops.gen_query_conditions('endpoints.uuid','=',email_endpoint_uuid)
    inv=res_ops.query_resource(res_ops.SNS_TOPIC,cond)
    if not inv:
        test_util.test_fail('create and subscribe snstopic failed')
    cond = res_ops.gen_query_conditions('name', '=', 'system-alarm')
    system_alarm_topic = res_ops.query_resource(res_ops.SNS_TOPIC, cond)[0]
    system_alarm_topic_uuid=system_alarm_topic.uuid
    zwt_ops.subscribe_sns_topic(system_alarm_topic_uuid, email_endpoint_uuid)
    cond=res_ops.gen_query_conditions('endpoints.uuid','=',email_endpoint_uuid)
    inv=res_ops.query_resource(res_ops.SNS_TOPIC,cond)
    if not inv:
        test_util.test_fail('subscribe system-alarm topic failed')
    cond = res_ops.gen_query_conditions('name','=','api')
    api_topic= res_ops.query_resource(res_ops.SNS_TOPIC,cond)[0]
    api_topic_uuid=api_topic.uuid
    zwt_ops.subscribe_sns_topic(api_topic_uuid,http_endpoint_uuid)
    cond = res_ops.gen_query_conditions('endpointUuid','=',http_endpoint_uuid)
    cond = res_ops.gen_query_conditions('topicUuid','=',api_topic_uuid)
    inv=res_ops.query_resource(res_ops.SNS_TOPIC_SUBSCRIBER,cond)
    if not inv:
        test_util.test_fail('subscribe api topic failed')

    # subscribe event
    namespace = 'ZStack/VM'
    actions = [{"actionUuid": sns_topic_uuid, "actionType": "sns"}]
    labels = [{"key": "NewState", "op": "Equal", "value": "Disconnected"}]
    event_name = 'VMStateChangedOnHost'
    event_sub_uuid = zwt_ops.subscribe_event(namespace, event_name, actions, labels).uuid
    cond = res_ops.gen_query_conditions('uuid', '=', event_sub_uuid)
    event_subscription = res_ops.query_resource(res_ops.EVENT_SUBSCRIPTION, cond)
    if not event_subscription:
        test_util.test_fail('Subscribe event failed')

    #update endpoint
    new_name='endpointNewName'
    new_description='endpoint new description'
    zwt_ops.update_sns_application_endpoint(email_endpoint_uuid,new_name,new_description)
    cond= res_ops.gen_query_conditions('uuid','=',email_endpoint_uuid)
    inv =res_ops.query_resource(res_ops.SNS_APPLICATION_ENDPOINT,cond)[0]
    if inv.name!=new_name or inv.description!=new_description:
        test_util.test_fail('test update email endpoint failed')
    zwt_ops.update_sns_application_endpoint(http_endpoint_uuid,new_name,new_description)
    cond= res_ops.gen_query_conditions('uuid','=',http_endpoint_uuid)
    inv =res_ops.query_resource(res_ops.SNS_APPLICATION_ENDPOINT,cond)[0]
    if inv.name!=new_name or inv.description!=new_description:
        test_util.test_fail('test update http endpoint failed')
    new_name_platform='platformNewName'
    new_description_platform='platformNewName'
    zwt_ops.update_sns_application_platform(email_platform_uuid,new_name_platform,new_description_platform)
    cond= res_ops.gen_query_conditions('uuid','=',email_platform_uuid)
    inv =res_ops.query_resource(res_ops.SNS_APPLICATION_PLATFORM,cond)[0]
    if inv.name!=new_name_platform or inv.description!=new_description_platform:
        test_util.test_fail('test update email platform failed')

    #change state
    state_event = 'disable'
    state_result = 'Disabled'
    zwt_ops.change_sns_topic_state(system_alarm_topic_uuid,state_event)
    cond=res_ops.gen_query_conditions('uuid','=',system_alarm_topic_uuid)
    inv=res_ops.query_resource(res_ops.SNS_TOPIC,cond)[0]
    if inv.state!=state_result:
        test_util.test_fail('change system alarm topic state failed')
    zwt_ops.change_sns_topic_state(api_topic_uuid, state_event)
    cond = res_ops.gen_query_conditions('uuid', '=', api_topic_uuid)
    inv = res_ops.query_resource(res_ops.SNS_TOPIC, cond)[0]
    if inv.state != state_result:
        test_util.test_fail('change api topic state failed')
    zwt_ops.change_sns_application_endpoint_state(email_endpoint_uuid,state_event)
    cond = res_ops.gen_query_conditions('uuid', '=', email_endpoint_uuid)
    inv = res_ops.query_resource(res_ops.SNS_APPLICATION_ENDPOINT, cond)[0]
    if inv.state != state_result:
        test_util.test_fail('change email endpoint state failed')
    zwt_ops.change_sns_application_endpoint_state(http_endpoint_uuid,state_event)
    cond = res_ops.gen_query_conditions('uuid', '=', http_endpoint_uuid)
    inv = res_ops.query_resource(res_ops.SNS_APPLICATION_ENDPOINT, cond)[0]
    if inv.state != state_result:
        test_util.test_fail('change http endpoint state failed')
    zwt_ops.change_sns_application_platform_state(email_platform_uuid,state_event)
    cond = res_ops.gen_query_conditions('uuid', '=', email_platform_uuid)
    inv = res_ops.query_resource(res_ops.SNS_APPLICATION_PLATFORM, cond)[0]
    if inv.state != state_result:
        test_util.test_fail('change email platform state failed')

    # test recover and delete
    state_event='enable'
    state_result='Enabled'
    zwt_ops.change_sns_topic_state(system_alarm_topic_uuid,state_event)
    cond=res_ops.gen_query_conditions('uuid','=',system_alarm_topic_uuid)
    inv=res_ops.query_resource(res_ops.SNS_TOPIC,cond)[0]
    if inv.state!=state_result:
        test_util.test_fail('change system alarm topic state failed')
    zwt_ops.change_sns_topic_state(api_topic_uuid, state_event)
    cond = res_ops.gen_query_conditions('uuid', '=', api_topic_uuid)
    inv = res_ops.query_resource(res_ops.SNS_TOPIC, cond)[0]
    if inv.state != state_result:
        test_util.test_fail('change api topic state failed')
    zwt_ops.unsubscribe_event(event_sub_uuid)
    cond = res_ops.gen_query_conditions('uuid', '=', event_sub_uuid)
    event_subscription = res_ops.query_resource(res_ops.EVENT_SUBSCRIPTION, cond)
    if event_subscription:
        test_util.test_fail('unsubscribe event failed')
    zwt_ops.unsubscribe_sns_topic(sns_topic_uuid, email_endpoint_uuid)
    cond =res_ops.gen_query_conditions('endpointUuid','=',email_endpoint_uuid)
    cond=res_ops.gen_query_conditions('topicUuid','=',sns_topic_uuid,cond)
    inv = res_ops.query_resource(res_ops.SNS_TOPIC_SUBSCRIBER,cond)
    if inv:
        test_util.test_fail('unsubscribe sns topic failed')
    zwt_ops.unsubscribe_sns_topic(system_alarm_topic_uuid, email_endpoint_uuid)
    cond =res_ops.gen_query_conditions('endpointUuid','=',email_endpoint_uuid)
    cond=res_ops.gen_query_conditions('topicUuid','=',system_alarm_topic_uuid,cond)
    inv = res_ops.query_resource(res_ops.SNS_TOPIC_SUBSCRIBER,cond)
    if inv:
        test_util.test_fail('unsubscribe system alarm topic failed')
    zwt_ops.unsubscribe_sns_topic(api_topic_uuid, http_endpoint_uuid)
    cond =res_ops.gen_query_conditions('endpointUuid','=',http_endpoint_uuid)
    cond=res_ops.gen_query_conditions('topicUuid','=',api_topic_uuid,cond)
    inv = res_ops.query_resource(res_ops.SNS_TOPIC_SUBSCRIBER,cond)
    if inv:
        test_util.test_fail('unsubscribe api topic failed')
    zwt_ops.delete_sns_topic(sns_topic_uuid)
    cond=res_ops.gen_query_conditions('uuid','=',sns_topic_uuid)
    inv = res_ops.query_resource(res_ops.SNS_TOPIC, cond)
    if inv:
        test_util.test_fail('delete sns topic failed')
    zwt_ops.delete_sns_application_endpoint(http_endpoint_uuid)
    cond=res_ops.gen_query_conditions('uuid','=',http_endpoint_uuid)
    inv = res_ops.query_resource(res_ops.SNS_APPLICATION_ENDPOINT, cond)
    if inv:
        test_util.test_fail('delete http endpoint failed')
    zwt_ops.delete_sns_application_endpoint(email_endpoint_uuid)
    cond=res_ops.gen_query_conditions('uuid','=',email_endpoint_uuid)
    inv = res_ops.query_resource(res_ops.SNS_APPLICATION_ENDPOINT, cond)
    if inv:
        test_util.test_fail('delete email endpoint failed')
    zwt_ops.delete_sns_application_platform(email_platform_uuid)
    cond=res_ops.gen_query_conditions('uuid','=',email_platform_uuid)
    inv = res_ops.query_resource(res_ops.SNS_APPLICATION_PLATFORM, cond)
    if inv:
        test_util.test_fail('delete email platform failed')

    test_util.test_pass('success test event with email endpoint basic option!')

# Will be called only if exception happens in test().
def error_cleanup():
    global email_platform_uuid, email_endpoint_uuid, http_endpoint_uuid,sns_topic_uuid
    if sns_topic_uuid:
        zwt_ops.delete_sns_topic(sns_topic_uuid)
    if http_endpoint_uuid:
        zwt_ops.delete_sns_application_endpoint(http_endpoint_uuid)
    if email_endpoint_uuid:
        zwt_ops.delete_sns_application_endpoint(email_endpoint_uuid)
    if email_platform_uuid:
        zwt_ops.delete_sns_application_platform(email_platform_uuid)


