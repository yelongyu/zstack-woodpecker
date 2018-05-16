'''
test alarm Image and custom sns text template with email

@author: Ronghao.zhou
'''
import time as time

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.zwatch_operations as zwt_ops
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_image as  zstack_image_header
import os

test_stub = test_lib.lib_get_test_stub()
test_dict = test_state.TestStateDict()

email_platform_uuid = None
email_endpoint_uuid = None
my_sns_topic_uuid = None
event_template_uuid = None
alarm_template_uuid = None

alarm_uuid_list = []


def test():
    global my_sns_topic_uuid, email_endpoint_uuid, email_platform_uuid, event_template_uuid, \
        alarm_template_uuid, alarm_uuid_list, test_dict

    smtp_server = os.environ.get('smtpServer')
    pop_server = os.environ.get('popServer')
    smtp_port = os.environ.get('smtpPort')
    username = os.environ.get('mailUsername')
    password = os.environ.get('mailPassword')
    email_platform_name = 'Alarm_email'
    email_platform = zwt_ops.create_sns_email_platform(smtp_server, smtp_port,
                                                         email_platform_name, username, password)
    email_platform_uuid = email_platform.uuid
    try:
        zwt_ops.validate_sns_email_platform(email_platform_uuid)
    except:
        test_util.test_fail(
            'Validate SNS Email Platform Failed, Email Plarform: %s' % email_platform_uuid)
    email_endpoint_uuid = zwt_ops.create_sns_email_endpoint(username, 'test_qa',
                                                              email_platform_uuid).uuid

    my_sns_topic = zwt_ops.create_sns_topic('my_sns_topic')
    my_sns_topic_uuid = my_sns_topic.uuid
    zwt_ops.subscribe_sns_topic(my_sns_topic_uuid, email_endpoint_uuid)

    # create alarm
    namespace = 'ZStack/Image'
    greater_than_or_equal_to = 'GreaterThanOrEqualTo'
    greater_than = 'GreaterThan'
    actions = [{"actionUuid": my_sns_topic_uuid, "actionType": "sns"}]

    period = 10

    threshold_1 = 1
    threshold_3 = 3
    threshold_10 = 10
    threshold_50 = 50

    total_image_count = 'TotalImageCount'
    total_image_count_alarm_uuid = zwt_ops.create_alarm(greater_than_or_equal_to, period,
                                                          threshold_3, namespace,
                                                          total_image_count,
                                                          name='total-count-image',
                                                          repeat_interval=600,
                                                          actions=actions).uuid
    alarm_uuid_list.append(total_image_count_alarm_uuid)

    ready_image_count = 'ReadyImageCount'
    ready_image_count_alarm_uuid = zwt_ops.create_alarm(greater_than_or_equal_to, period,
                                                          threshold_3, namespace,
                                                          ready_image_count,
                                                          name='ready_image_count',
                                                          repeat_interval=600,
                                                          actions=actions).uuid
    alarm_uuid_list.append(ready_image_count_alarm_uuid)

    ready_image_in_percent = 'ReadyImageInPercent'
    ready_image_in_percent_alarm_uuid = zwt_ops.create_alarm(greater_than_or_equal_to, period,
                                                               threshold_1, namespace,
                                                               ready_image_in_percent,
                                                               name='ready_image_in_percent',
                                                               repeat_interval=600,
                                                               actions=actions).uuid
    alarm_uuid_list.append(ready_image_in_percent_alarm_uuid)

    root_volume_template_count = 'RootVolumeTemplateCount'
    root_volume_template_count_alarm_uuid = zwt_ops.create_alarm(greater_than_or_equal_to,
                                                                   period,
                                                                   threshold_3, namespace,
                                                                   root_volume_template_count,
                                                                   name='root_volume_template_count',
                                                                   repeat_interval=600,
                                                                   actions=actions, ).uuid
    alarm_uuid_list.append(root_volume_template_count_alarm_uuid)

    root_volume_template_in_percent = 'RootVolumeTemplateInPercent'
    root_volume_template_in_percent_alarm_uuid = zwt_ops.create_alarm(greater_than, period,
                                                                        threshold_1, namespace,
                                                                        root_volume_template_in_percent,
                                                                        name='root_volume_template_in_percent',
                                                                        repeat_interval=600,
                                                                        actions=actions).uuid
    alarm_uuid_list.append(root_volume_template_in_percent_alarm_uuid)

    data_volume_template_count = 'DataVolumeTemplateCount'
    data_volume_template_count_alarm_uuid = zwt_ops.create_alarm(greater_than_or_equal_to,
                                                                   period,
                                                                   threshold_3, namespace,
                                                                   data_volume_template_count,
                                                                   name='data_volume_template_count',
                                                                   repeat_interval=600,
                                                                   actions=actions).uuid
    alarm_uuid_list.append(data_volume_template_count_alarm_uuid)

    data_volume_template_in_percent = 'DataVolumeTemplateInPercent'
    data_volume_template_in_percent_alarm_uuid = zwt_ops.create_alarm(greater_than, period,
                                                                        threshold_1, namespace,
                                                                        data_volume_template_in_percent,
                                                                        name='data_volume_template_in_percent',
                                                                        repeat_interval=600,
                                                                        actions=actions).uuid
    alarm_uuid_list.append(data_volume_template_in_percent_alarm_uuid)

    iso_count = 'ISOCount'
    iso_count_alarm_uuid = zwt_ops.create_alarm(greater_than_or_equal_to, period, threshold_3,
                                                  namespace, iso_count, name='iso_count',
                                                  repeat_interval=600, actions=actions).uuid
    alarm_uuid_list.append(iso_count_alarm_uuid)

    iso_in_percent = 'ISOInPercent'
    iso_in_percent_alarm_uuid = zwt_ops.create_alarm(greater_than, period, threshold_1,
                                                       namespace,
                                                       iso_in_percent, name='iso_in_percent',
                                                       repeat_interval=600, actions=actions).uuid
    alarm_uuid_list.append(iso_in_percent_alarm_uuid)

    # create Image
    image_name = os.environ.get('imageName_s')
    l3_name = os.environ.get('l3VlanNetworkName1')
    vm_name='multihost_basic_vm'
    vm = test_stub.create_vm(vm_name,image_name,l3_name)
    test_dict.add_vm(vm)
    volume = test_stub.create_volume()
    test_dict.add_volume(volume)
    volume.attach(vm)
    zone_uuid = vm.get_vm().zoneUuid
    root_volume_uuid = test_lib.lib_get_root_volume_uuid(vm.get_vm())
    bs_uuid_list = test_lib.lib_get_backup_storage_uuid_list_by_zone(zone_uuid)

    image_option = test_util.ImageOption()
    image_option.set_root_volume_uuid(root_volume_uuid)
    image_option.set_format('qcow2')
    image_option.set_backup_storage_uuid_list(bs_uuid_list)
    # image_option.set_mediaType('ISO')

    for i in range(threshold_3):
        image_option.set_name('root_volume_template_for_test_' + str(i))
        root_volume_template = zstack_image_header.ZstackTestImage()
        root_volume_template.set_creation_option(image_option)
        root_volume_template.create()
        test_dict.add_image(root_volume_template)
        iso=test_stub.add_test_minimal_iso("iso_for_test_"+str(i))
        test_dict.add_image(iso)
    time.sleep(30)
    # before change template
    flag = zwt_ops.check_sns_email(pop_server, username, password, total_image_count,
                                     total_image_count_alarm_uuid)
    if flag != 1:
        test_util.test_fail('No send event email')
    flag = zwt_ops.check_sns_email(pop_server, username, password, ready_image_count,
                                     ready_image_count_alarm_uuid)
    if flag != 1:
        test_util.test_fail('No send event email')
    flag = zwt_ops.check_sns_email(pop_server, username, password, ready_image_in_percent,
                                     ready_image_in_percent_alarm_uuid)
    if flag != 1:
        test_util.test_fail('No send event email')
    flag = zwt_ops.check_sns_email(pop_server, username, password, root_volume_template_count,
                                     root_volume_template_count_alarm_uuid)
    if flag != 1:
        test_util.test_fail('No send event email')
    flag = zwt_ops.check_sns_email(pop_server, username, password,
                                     root_volume_template_in_percent,
                                     root_volume_template_in_percent_alarm_uuid)
    if flag != 1:
        test_util.test_fail('No send event email')
    flag = zwt_ops.check_sns_email(pop_server, username, password, iso_count,
                                     iso_count_alarm_uuid)
    if flag != 1:
        test_util.test_fail('No send event email')
    flag = zwt_ops.check_sns_email(pop_server, username, password, iso_in_percent,
                                     iso_in_percent_alarm_uuid)
    if flag != 1:
        test_util.test_fail('No send event email')

    alarm_keywords = 'TemplateForAlarmOn'

    if zwt_ops.check_keywords_in_email(pop_server, username, password, alarm_keywords,
                                         total_image_count_alarm_uuid):
        test_util.test_fail('email already exsist before test')
    if zwt_ops.check_keywords_in_email(pop_server, username, password, alarm_keywords,
                                         ready_image_count_alarm_uuid):
        test_util.test_fail('email already exsist before test')
    if zwt_ops.check_keywords_in_email(pop_server, username, password, alarm_keywords,
                                         ready_image_in_percent_alarm_uuid):
        test_util.test_fail('email already exsist before test')
    if zwt_ops.check_keywords_in_email(pop_server, username, password, alarm_keywords,
                                         root_volume_template_count_alarm_uuid):
        test_util.test_fail('email already exsist before test')
    if zwt_ops.check_keywords_in_email(pop_server, username, password, alarm_keywords,
                                         root_volume_template_in_percent_alarm_uuid):
        test_util.test_fail('email already exsist before test')
    if zwt_ops.check_keywords_in_email(pop_server, username, password, alarm_keywords,
                                         data_volume_template_count_alarm_uuid):
        test_util.test_fail('email already exsist before test')
    if zwt_ops.check_keywords_in_email(pop_server, username, password, alarm_keywords,
                                         data_volume_template_in_percent_alarm_uuid):
        test_util.test_fail('email already exsist before test')
    if zwt_ops.check_keywords_in_email(pop_server, username, password, alarm_keywords,
                                         iso_count_alarm_uuid):
        test_util.test_fail('email already exsist before test')
    if zwt_ops.check_keywords_in_email(pop_server, username, password, alarm_keywords,
                                         iso_in_percent_alarm_uuid):
        test_util.test_fail('email already exsist before test')

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
                                                             default_template=False).uuid

    event_template_name = 'my-event-template'
    event_keywords = 'TemplateForEventHappened'
    event_template = '${EVENT_NAME} IN ${EVENT_NAMESPACE}' \
                     'keyword1:ThisWordIsKeyWord' \
                     'keyword2:TemplateForEventHappened' \
                     'keyword3{PARAM_EVENT_SUBSCRIPTION_UUID}' \
                     '(Using for template changes email check)'
    event_template_uuid = zwt_ops.create_sns_text_template(event_template_name,
                                                             application_platform_type,
                                                             event_template,
                                                             default_template=True).uuid

    # test update text template
    zwt_ops.update_sns_text_template(alarm_template_uuid, description='this is a new description',
                                       default_template=True)

    cond = res_ops.gen_query_conditions('uuid', '=', alarm_template_uuid)
    inv = res_ops.query_resource(res_ops.SNS_TEXT_TEMPLATE, cond)[0]
    if inv.defaultTemplate == False or inv.description != 'this is a new description':
        test_util.test_fail('change template fail')

    for i in range(threshold_3):
        data_volume_template = volume.create_template(bs_uuid_list,
                                                      name="vol_temp_for_volume_test_" + str(i))
        test_dict.add_image(data_volume_template)

    # wait for reboot and send email
    time.sleep(30)
    test_lib.lib_robot_cleanup(test_dict)
    zwt_ops.delete_sns_text_template(alarm_template_uuid)
    zwt_ops.delete_sns_text_template(event_template_uuid)
    for alarm_uuid in alarm_uuid_list:
        zwt_ops.delete_alarm(alarm_uuid)
    zwt_ops.delete_sns_topic(my_sns_topic_uuid)
    zwt_ops.delete_sns_application_endpoint(email_endpoint_uuid)
    zwt_ops.delete_sns_application_platform(email_platform_uuid)

    if zwt_ops.check_keywords_in_email(pop_server, username, password, alarm_keywords,
                                         data_volume_template_count_alarm_uuid) and zwt_ops.check_keywords_in_email(
        pop_server, username, password, alarm_keywords,
        data_volume_template_in_percent_alarm_uuid):
        test_util.test_pass('success check all keywords in the email')
    else:
        test_util.test_fail('cannt check all mail')


# Will be called only if exception happens in test().
def error_cleanup():
    global test_dict, my_sns_topic_uuid, email_endpoint_uuid, email_platform_uuid, event_template_uuid, \
        alarm_template_uuid, alarm_uuid_list
    test_lib.lib_error_cleanup(test_dict)
    if alarm_uuid_list:
        for alarm_uuid in alarm_uuid_list:
            zwt_ops.delete_alarm(alarm_uuid)
    if event_template_uuid:
        zwt_ops.delete_sns_text_template(event_template_uuid)
    if alarm_template_uuid:
        zwt_ops.delete_sns_text_template(alarm_template_uuid)
    if my_sns_topic_uuid:
        zwt_ops.delete_sns_topic(my_sns_topic_uuid)
    if email_endpoint_uuid:
        zwt_ops.delete_sns_application_endpoint(email_endpoint_uuid)
    if email_platform_uuid:
        zwt_ops.delete_sns_application_platform(email_platform_uuid)
    if event_template_uuid:
        zwt_ops.delete_sns_text_template(event_template_uuid)
