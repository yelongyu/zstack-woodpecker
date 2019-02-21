'''

All zwatch operations for test.

@author: ronghaoZhou
'''

import apibinding.api_actions as api_actions
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.account_operations as acc_ops
import poplib
from email.parser import Parser
import base64
import quopri
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib
import os



def create_alarm(comparison_operator, period, threshold, namespace, metric_name, name=None, repeat_interval=None, labels=None, actions=None, resource_uuid=None, session_uuid=None):
    action = api_actions.CreateAlarmAction()
    action.timeout = 30000
    if name:
        action.name = name
    if not name:
        action.name = 'alarm_01'
    action.comparisonOperator=comparison_operator
    action.period=period
    action.threshold=threshold
    action.namespace=namespace
    action.metricName=metric_name
    if actions:
        action.actions=actions
    if repeat_interval:
        action.repeatInterval=repeat_interval
    if labels:
        action.labels=labels
    if resource_uuid:
        action.resourceUuid=resource_uuid
    test_util.action_logger('Create Alarm: %s ' % name)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def update_alarm(uuid, comparison_operator=None, period=None, threshold=None, name=None, repeat_interval=None, resource_uuid=None, session_uuid=None):
    action = api_actions.UpdateAlarmAction()
    action.timeout = 30000
    action.uuid = uuid
    if comparison_operator:
        action.comparisonOperator = comparison_operator
    if period:
        action.period = period
    if threshold:
        action.threshold = threshold
    if name:
        action.name = name
    test_util.action_logger('Update Alarm: %s ' % uuid)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def change_alarm_state(uuid, state_event, session_uuid=None):
    action = api_actions.ChangeAlarmStateAction()
    action.timeout = 30000
    action.uuid = uuid
    action.stateEvent = state_event
    test_util.action_logger('Change Alarm: %s State to %s' % (uuid, state_event))
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def delete_alarm(uuid, delete_mode=None, session_uuid=None):
    action = api_actions.DeleteAlarmAction()
    action.timeout = 30000
    action.uuid = uuid
    if delete_mode:
        action.deleteMode=delete_mode
    test_util.action_logger('Delete Alarm: %s ' % uuid)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def add_action_to_alarm(alarm_uuid, action_uuid, action_type, session_uuid=None):
    action = api_actions.AddActionToAlarmAction()
    action.timeout = 30000
    action.alarmUuid = alarm_uuid
    action.actionUuid = action_uuid
    action.actionType = action_type
    test_util.action_logger('Add Action: %s to Alarm: %s ' % (action_uuid, alarm_uuid))
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def remove_action_from_alarm(alarm_uuid, action_uuid, delete_mode=None, session_uuid=None):
    action = api_actions.RemoveActionFromAlarmAction()
    action.timeout = 30000
    action.alarmUuid = alarm_uuid
    action.actionUuid = action_uuid
    if delete_mode:
        action.deleteMode = delete_mode
    test_util.action_logger('Remove Action: %s From Alarm: %s ' % (action_uuid, alarm_uuid))
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def add_label_to_alarm(alarm_uuid, key, value, operator, session_uuid=None):
    action = api_actions.AddLabelToAlarmAction()
    action.timeout = 30000
    action.alarmUuid = alarm_uuid
    action.key = key
    action.value = value
    action.operator = operator
    test_util.action_logger('Add Label to Alarm: %s ' %alarm_uuid)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def remove_label_from_alarm(uuid, delete_mode=None, session_uuid=None):
    action = api_actions.RemoveLabelFromAlarmAction()
    action.timeout = 30000
    action.uuid = uuid
    if delete_mode:
        action.deleteMode = delete_mode
    test_util.action_logger('Remove Label From Alarm: %s ' %uuid)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def subscribe_event(namespace, event_name, actions, labels=None, session_uuid=None):
    action = api_actions.SubscribeEventAction()
    action.timeout = 30000
    action.namespace = namespace
    action.eventName = event_name
    action.actions = actions
    if labels:
        action.labels = labels
    test_util.action_logger('Subscribe Event: %s ' %event_name)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def unsubscribe_event(uuid, delete_mode=None, session_uuid=None):
    action = api_actions.UnsubscribeEventAction()
    action.timeout = 30000
    action.uuid = uuid
    if delete_mode:
        action.deleteMode = delete_mode
    test_util.action_logger('Unsubscribe Event: %s ' %uuid)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def create_sns_email_endpoint(email, name, platform_uuid=None, session_uuid=None):
    action = api_actions.CreateSNSEmailEndpointAction()
    action.timeout = 30000
    action.email = email
    action.name = name
    if platform_uuid:
        action.platformUuid = platform_uuid
    test_util.action_logger('Create SNS Email Endpoint: %s ' %name)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def create_sns_email_platform(smtp_server, smtp_port, name, username=None, password=None, session_uuid=None):
    action = api_actions.CreateSNSEmailPlatformAction()
    action.timeout = 30000
    action.smtpServer = smtp_server
    action.smtpPort = smtp_port
    action.name = name
    if username:
        action.username = username
    if password:
        action.password = password
    test_util.action_logger('Create SNS Email Platform: %s ' %name)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def validate_sns_email_platform(uuid, session_uuid=None):
    action = api_actions.ValidateSNSEmailPlatformAction()
    action.timeout = 30000
    action.uuid = uuid
    test_util.action_logger('Validate SNS Email Platform: %s ' %uuid)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def create_sns_http_endpoint(url, name, username=None, password=None, session_uuid=None):
    action = api_actions.CreateSNSHttpEndpointAction()
    action.timeout = 30000
    action.url = url
    action.name = name
    if username:
        action.username = username
    if password:
        action.password = password
    test_util.action_logger('Create SNS Http Endpoint: %s ' %name)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def create_sns_dingtalk_endpoint(url, name, at_all=None, at_person_phone_numbers=None, session_uuid=None):
    action = api_actions.CreateSNSDingTalkEndpointAction()
    action.timeout = 30000
    action.url = url
    action.name = name
    if at_all:
        action.atAll = at_all
    if at_person_phone_numbers:
        action.atPersonPhoneNumbers = at_person_phone_numbers
    test_util.action_logger('Create SNS DingTalk Endpoint: %s ' %name)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def add_sns_dingtalk_at_person(phone_number, endpoint_uuid, session_uuid=None):
    action = api_actions.AddSNSDingTalkAtPersonAction()
    action.timeout = 30000
    action.phoneNumber = phone_number
    action.endpointUuid = endpoint_uuid
    test_util.action_logger('Add SNS DingTalk At Person: %s ' %phone_number)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def remove_sns_dingtalk_at_person(phone_number, endpoint_uuid, delete_mode=None, session_uuid=None):
    action = api_actions.RemoveSNSDingTalkAtPersonAction()
    action.timeout = 30000
    action.phoneNumber = phone_number
    action.endpointUuid = endpoint_uuid
    if delete_mode:
        action.deleteMode = delete_mode
    test_util.action_logger('Remove SNS DingTalk At Person: %s ' % endpoint_uuid)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def update_sns_application_endpoint(uuid, name, description, session_uuid=None):
    action = api_actions.UpdateSNSApplicationEndpointAction()
    action.timeout = 30000
    action.uuid = uuid
    action.name = name
    action.description = description
    test_util.action_logger('Update SNS Application Endpoint: %s ' %uuid)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def delete_sns_application_endpoint(uuid, delete_mode=None, session_uuid=None):
    action = api_actions.DeleteSNSApplicationEndpointAction()
    action.timeout = 30000
    action.uuid = uuid
    if delete_mode:
        action.deleteMode = delete_mode
    test_util.action_logger('Delete SNS Application Endpoint: %s ' %uuid)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def change_sns_application_endpoint_state(uuid, state_event, session_uuid=None):
    action = api_actions.ChangeSNSApplicationEndpointStateAction()
    action.timeout = 30000
    action.uuid = uuid
    action.stateEvent = state_event
    test_util.action_logger('Change SNS Application Endpoint State To: %s ' %state_event)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def update_sns_application_platform(uuid, name, description, session_uuid=None):
    action = api_actions.UpdateSNSApplicationPlatformAction()
    action.timeout = 30000
    action.uuid = uuid
    action.name = name
    action.description = description
    test_util.action_logger('Update SNS Application Platform: %s ' %uuid)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def delete_sns_application_platform(uuid, delete_mode=None, session_uuid=None):
    action = api_actions.DeleteSNSApplicationPlatformAction()
    action.timeout = 30000
    action.uuid = uuid
    if delete_mode:
        action.deleteMode = delete_mode
    test_util.action_logger('Delete SNS Application Platform: %s ' %uuid)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def change_sns_application_platform_state(uuid, state_event, session_uuid=None):
    action = api_actions.ChangeSNSApplicationPlatformStateAction()
    action.timeout = 30000
    action.uuid = uuid
    action.stateEvent = state_event
    test_util.action_logger('Change SNS Application Platform State To: %s ' %state_event)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def create_sns_topic(name, session_uuid=None):
    action = api_actions.CreateSNSTopicAction()
    action.timeout = 30000
    action.name = name
    test_util.action_logger('Create SNS Topic: %s ' %name)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def update_sns_topic(uuid, name, description, session_uuid=None):
    action = api_actions.UpdateSNSTopicAction()
    action.timeout = 30000
    action.uuid = uuid
    action.name = name
    action.description = description
    test_util.action_logger('Update SNS Topic: %s ' %uuid)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def delete_sns_topic(uuid, delete_mode=None, session_uuid=None):
    action = api_actions.DeleteSNSTopicAction()
    action.timeout = 30000
    action.uuid = uuid
    if delete_mode:
        action.deleteMode = delete_mode
    test_util.action_logger('Delete SNS Topic: %s ' %uuid)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def change_sns_topic_state(uuid, state_event, session_uuid=None):
    action = api_actions.ChangeSNSTopicStateAction()
    action.timeout = 30000
    action.uuid = uuid
    action.stateEvent = state_event
    test_util.action_logger('Change SNS Topic State To: %s ' %state_event)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def subscribe_sns_topic(topic_uuid, endpoint_uuid, session_uuid=None):
    action = api_actions.SubscribeSNSTopicAction()
    action.timeout = 30000
    action.topicUuid = topic_uuid
    action.endpointUuid = endpoint_uuid
    test_util.action_logger('Subscribe SNS Topic: %s ' %topic_uuid)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def unsubscribe_sns_topic(topic_uuid, endpoint_uuid, session_uuid=None):
    action = api_actions.UnsubscribeSNSTopicAction()
    action.timeout = 30000
    action.topicUuid = topic_uuid
    action.endpointUuid = endpoint_uuid
    test_util.action_logger('Unsubscribe SNS Topic: %s ' %topic_uuid)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def get_all_metric_metadata(session_uuid=None):
    action = api_actions.GetAllMetricMetadataAction()
    action.timeout = 30000
    test_util.action_logger('Get All Metric Metadata:')
    evt = acc_ops.execute_action_with_session(action,session_uuid)
    return evt.metrics

def get_all_event_metadata(session_uuid=None):
    action = api_actions.GetAllEventMetadataAction()
    action.timeout = 30000
    test_util.action_logger('Get All Event Metadata:')
    evt = acc_ops.execute_action_with_session(action,session_uuid)
    return evt.events

def get_audit_data(start_time=None,end_time=None,limit=None,conditions=None,session_uuid=None):
    action = api_actions.GetAuditDataAction()
    action.timeout = 30000
    if start_time:
        action.startTime=start_time
    if end_time:
        action.endTime=end_time
    if limit:
        action.limit=limit
    if conditions:
        action.conditions=conditions
    test_util.action_logger('Get Audit Data:')
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.audits

def get_metric_label_value(namespace,metric_name,label_names,filter_labels=None,session_uuid=None):
    action = api_actions.GetMetricLabelValueAction()
    action.timeout = 30000
    action.namespace = namespace
    action.metricName = metric_name
    action.labelNames = label_names
    if filter_labels:
        action.filterLabels = filter_labels
    test_util.action_logger('Get Metric Label value:[namespace]:%s [metricName]:%s [labelNames]:%s'% (namespace,metric_name,label_names))
    evt=acc_ops.execute_action_with_session(action,session_uuid)
    return evt.labels

def get_metric_data(namespace,metric_name,start_time=None,end_time=None,period=None,labels=None,session_uuid=None):
    action = api_actions.GetMetricDataAction()
    action.timeout = 30000
    action.namespace = namespace
    action.metricName = metric_name
    if start_time:
        action.startTime = start_time
    if end_time:
        action.endTime = end_time
    if period:
        action.period = period
    if labels:
        action.labels = labels
    test_util.action_logger('Get Metric Data:[namespace]:%s [metricName]:%s' % (namespace, metric_name,))
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.data

def get_event_data(start_time=None,end_time=None,labels=None,conditions=None,session_uuid=None):
    action = api_actions.GetEventDataAction()
    action.timeout = 30000
    if start_time:
        action.startTime = start_time
    if end_time:
        action.endTime = end_time
    if conditions:
        action.conditions= conditions
    if labels:
        action.labels = labels
    test_util.action_logger('Get Event Data:')
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.events

def get_alarm_data(start_time=None,end_time=None,labels=None,session_uuid=None):
    action = api_actions.GetAlarmDataAction()
    action.timeout = 30000
    if start_time:
        action.startTime = start_time
    if end_time:
        action.endTime = end_time
    if labels:
        action.labels = labels
    test_util.action_logger('Get Alarm Data:')
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.histories

def put_metric_data(namespace,data,session_uuid=None):
    action = api_actions.PutMetricDataAction()
    action.timeout = 30000
    action.namespace = namespace
    action.data = data
    test_util.action_logger('Put Metric Data:[namespace]:%s [data]:%s'%(namespace,data))
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def create_sns_text_template(name,application_platform_type,template,default_template=None,description=None,session_uuid=None):
    action = api_actions.CreateSNSTextTemplateAction()
    action.timeout = 30000
    action.name = name
    action.applicationPlatformType = application_platform_type
    action.template = template
    if default_template:
        action.defaultTemplate = default_template
    if description:
        action.description = description
    test_util.action_logger('Create SNS Text Template:%s '% name)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def delete_sns_text_template(uuid,delete_mode=None,session_uuid=None):
    action = api_actions.DeleteSNSTextTemplateAction()
    action.timeout = 30000
    action.uuid = uuid
    if delete_mode:
        action.deleteMode = delete_mode
    test_util.action_logger('Delete SNS Text Template:%s ' % uuid)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def update_sns_text_template(uuid,name=None,description=None,template=None,default_template=None,session_uuid=None):
    action = api_actions.UpdateSNSTextTemplateAction()
    action.timeout = 30000
    action.uuid = uuid
    if name:
        action.name = name
    if description:
        action.description = description
    if template:
        action.template = template
    if default_template:
        action.defaultTemplate = default_template
    test_util.action_logger('Update SNS Text Template:%s ' % uuid)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def get_mail_list(pop_server, username, password):
    test_util.action_logger('Get Mail List From [pop server]:%s [user]:%s '%(pop_server,username))
    pop3 = poplib.POP3(pop_server)
    pop3.set_debuglevel(1)
    pop3.user(username)
    pop3.pass_(password)
    ret = pop3.stat()
    mail_list = []
    for i in range(ret[0] - 20, ret[0]+1):
        resp, msg, octets = pop3.retr(i)
        mail_list.append(msg)
    mail_list.reverse()
    pop3.quit()
    return mail_list

def check_sns_email(pop_server, username, password, name, uuid):
    '''
    This function is using for checking default SNS Text Template

    :param name: metric_name or event_name
    :param uuid: For Alarm email,this is alarm_uuid;For Event email,this is subscription_uuid or resource_uuid
    :return: 1 for found or 0 for not found
    '''
    mail_list = get_mail_list(pop_server, username, password)
    flag = 0      #check result
    test_util.action_logger('Check SNS Email:[name]:%s [uuid]:%s'% (name,uuid))
    for mail in mail_list:
        if flag == 1:
            break
        #msg_content = b'\r\n'.join(mail).decode('utf-8') #python3.x
        if 'Content-Transfer-Encoding: base64' in mail: 
            line1 = mail[-6:]
       	    line2 = mail[:-7]
	    for i in range(0, 6):
	        if (len(line1[i]) % 3 == 1):
                    line1[i] += "=="
	        elif(len(line1[i]) % 3 == 2):
       	            line1[i] += "="
            msg_content1 = '\r\n'.join(line1)  #python2.x
            msg1 = base64.b64decode(msg_content1)
            msg_content2 = '\r\n'.join(line2)  #python2.x
            msg2 = Parser().parsestr(msg_content2)
            msg = str(msg2) + msg1
            test_util.test_logger('find boundary_words,Search words is terminated .')
        elif 'Content-Transfer-Encoding: quoted-printable' in mail:        
            msg_content = '\r\n'.join(mail)  #python2.x
            msg1 = quopri.decodestring(msg_content)
            msg = Parser().parsestr(msg1)
        content=str(msg)
        if (username in content) and (name in content) and (uuid in content):
            flag = 1
            test_util.test_logger('Mail sent addr is %s' % username)
            test_util.test_logger('Got keywords uuid : %s in Mail' % uuid)
            test_util.test_logger('Got keywords name: %s in Mail' % name)

    test_util.test_logger('flag value is %s' % flag)
    return flag

def check_keywords_in_email(pop_server, username, password, first_keyword, second_keyword='',boundary_words=None):
    '''
    This function is used for checking different SNS Text Template

    :param first_keyword: keyword search in mail
    :param second_keyword: keyword search in mail(optional)
    :param boundary_words: when find boundary_words,serch will be terminated.You may send an email has this
                           boundary_words earlly to make a difference between old email and new email
    :return: 1 for found or 0 for not found
    '''
    mail_list = get_mail_list(pop_server, username, password)
    if boundary_words:
        for m in mail_list:
            for i in m:
                if boundary_words in i:
                    index_id = mail_list.index(m)
                    mail_list = mail_list[:index_id]
    test_util.action_logger('Check Keywords In Email:[keyword]:%s [keyword]:%s'% (first_keyword,second_keyword))
    for mail in mail_list:
        #msg_content = b'\r\n'.join(mail).decode('utf-8') #python3.x
        #msg_content1 = '\r\n'.join(mail[-6:])  #python2.x
        if 'Content-Transfer-Encoding: base64' in mail:
	    line1 = mail[-6:]
	    line2 = mail[:-7]
	    for i in range(0, 6):
	        if (len(line1[i]) % 3 == 1):
	            line1[i] += "=="
	        elif(len(line1[i]) % 3 == 2):
		    line1[i] += "="
            msg_content1 = '\r\n'.join(line1)  #python2.x
            msg1 = base64.b64decode(msg_content1)
            msg_content2 = '\r\n'.join(line2)  #python2.x
            msg2 = Parser().parsestr(msg_content2)
            msg = str(msg2) + msg1
            test_util.test_logger('find boundary_words,Search words is terminated .')
        elif 'Content-Transfer-Encoding: quoted-printable' in mail:
            msg_content = '\n'.join(mail)  #python2.x
            msg1 = quopri.decodestring(msg_content)
            msg = Parser().parsestr(msg1)
        content=str(msg)
        #test_util.test_logger(msg)
        if boundary_words:
            if boundary_words in content:
                test_util.test_logger('find boundary_words,Search words is terminated .')
                return 0
        if (username in content) and (first_keyword in content) and (second_keyword in content):
            test_util.test_logger('Mail sent addr is %s' % username)
            test_util.test_logger('Got first_keyword :[ %s ]in Mail' % first_keyword)
            test_util.test_logger('Got second_keyword :[ %s ]in Mail' % second_keyword)
            return 1
    test_util.test_logger('cant find boundary_words or keywords in latest 20 emails')
    return 0



def send_boundary_email(boundary_words,smtp_server,from_addr,password,to_addr):
    '''
    this function is used to send a boundary email to make a distinction between old and new email
    :param boundary_words:(may be a timestamp or uuid)
    :return: no return
    '''

    msg = MIMEText(boundary_words, 'plain')
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Subject'] = Header('boundary_email')

    test_util.action_logger('Send Mail List From :%s  to :%s '%(from_addr,to_addr))
    server = smtplib.SMTP(smtp_server, 25)
    server.set_debuglevel(1)
    server.login(from_addr, password)
    server.sendmail(from_addr, [to_addr], msg.as_string())
    server.quit()

def get_boundary_words():
    import time,random
    time_stamp=str(int(time.time()))
    boundary_words_list = []
    boundary_words='this is a boundary message,with time stamp:%s'%time_stamp
    boundary_words_02='this message is used to make a distinction between new email and old email,with time stamp %s'%time_stamp
    boundary_words_list.append(boundary_words)
    boundary_words_list.append(boundary_words_02)
    return random.choice(boundary_words_list)
