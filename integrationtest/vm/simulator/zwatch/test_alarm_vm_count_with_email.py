'''
test alarm if the total vm count is GreaterThanOrEqualTo 10 with email

@author: Glody
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import test_stub

test_dict = test_state.TestStateDict()
    
def test():
    smtp_server = 'smtp.zstack.io'
    pop_server = 'pop3.zstack.io'
    smtp_port = 25
    username = 'test.qa@zstack.io'
    password = 'Test1234'
    email_platform = test_stub.create_sns_email_platform(smtp_server, smtp_port, 'Alarm_email', username, password)
    email_platform_uuid = email_platform.uuid

    try:
        test_stub.validate_sns_email_platform(email_platform_uuid)
    except:
        test_util.test_fail('Validate SNS Email Platform Failed, Email Plarform: %s' %email_platform_uuid)

    email_endpoint_uuid = test_stub.create_sns_email_endpoint(username, 'test_qa', email_platform_uuid).uuid

    sns_topic = test_stub.create_sns_topic('sns_topic_01')
    
    test_stub.subscribe_sns_topic(sns_topic.uuid, email_endpoint_uuid)

    namespace = 'ZStack/VM'
    actions = sns_topic.uuid
    period = 100
    comparisonOperator = 'GreaterThanOrEqualTo'
    threshold = 10
    metric_name = 'TotalVMCount'
    alarm = test_stub.create_alarm(comparisonOperator, period, threshold, namespace, metric_name)

    #Create volume to spend ps
    for i in range(threshold):
       vm_name = 'vm'+str(i)
       test_stub.create_vm(vm_name)

    keywords = ''
    trigger = ''
    target_uuid = ''

    if test_util.check_sns_email(pop_server, username, password, keywords, trigger, target_uuid):
        test_util.test_pass('Email Alarm Triggered Success')
    else:
        test_util.test_Fail('Email Alarm Didnt Triggered When The VM Count Equal To Threshold')

#Will be called only if exception happens in test().
def error_cleanup():
    pass
