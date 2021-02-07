'''
test alarm with dingtalk.

@author: rhZhou
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.zwatch_operations as zwt_ops
import time


test_stub = test_lib.lib_get_test_stub()
test_dict = test_state.TestStateDict()
endpoint_uuid = None
sns_topic_uuid = None
alarm_uuid = None


def test():
    global endpoint_uuid, sns_topic_uuid, alarm_uuid, test_dict, test_stub
    url = 'https://oapi.dingtalk.com/robot/send?access_token' \
          '=0be899d4bd0a7629961a5ccd3035dfba30d084b57944897838f1b60100dddddd'
    name = 'dingtalkendpointTest'
    endpoint_uuid = zwt_ops.create_sns_dingtalk_endpoint(url, name, at_all=True).uuid

    # create sns topic
    sns_topic_uuid = zwt_ops.create_sns_topic('sns_topic_01').uuid
    zwt_ops.subscribe_sns_topic(sns_topic_uuid, endpoint_uuid)

    # create alarm
    namespace = 'ZStack/Volume'
    actions = [{"actionUuid": sns_topic_uuid, "actionType": "sns"}]
    comparisonOperator = 'GreaterThanOrEqualTo'
    repeat_interval = 20
    period = 10
    threshold = 5
    metric_name = 'TotalVolumeCount'
    alarm_uuid = zwt_ops.create_alarm(comparisonOperator, period, threshold, namespace, metric_name, actions=actions,
                                      repeat_interval=repeat_interval).uuid

    # Create volume
    for i in range(threshold+1):
        volume = test_stub.create_volume()
        test_dict.add_volume(volume)

    time.sleep(20)
    cond = res_ops.gen_query_conditions('uuid','=',alarm_uuid)
    alarm_inv = res_ops.query_resource(res_ops.ALARM,cond)[0]
    if alarm_inv.status != 'Alarm':
        test_util.test_fail("Alarm did't change status to alarm.Test fail")

    test_lib.lib_robot_cleanup(test_dict)
    zwt_ops.delete_alarm(alarm_uuid)
    zwt_ops.delete_sns_topic(sns_topic_uuid)
    zwt_ops.delete_sns_application_endpoint(endpoint_uuid)

    test_util.test_pass('success test alarm image account with dingtalk!')


# Will be called only if exception happens in test().
def error_cleanup():
    global endpoint_uuid, sns_topic_uuid, alarm_uuid, test_dict
    test_lib.lib_error_cleanup(test_dict)
    if alarm_uuid:
        zwt_ops.delete_alarm(alarm_uuid)
    if sns_topic_uuid:
        zwt_ops.delete_sns_topic(sns_topic_uuid)
    if endpoint_uuid:
        zwt_ops.delete_sns_application_endpoint(endpoint_uuid)
