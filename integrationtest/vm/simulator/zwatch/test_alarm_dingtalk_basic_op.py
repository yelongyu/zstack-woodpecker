'''
test basic function of alarm and dingtalk

# 1 create two dingtalkendpoint , one atAll, another atPerson,and then add atPerson and remove at Person
# 2 update endpoint
# 3 create a sns topic and the both endpoint subscribe it
# 4 update sns topic
# 5 create a alarm and the sns topic subscribe it
# 6 update alarm
# 7 add/remove action to/from alarm
# 8 add/remove label to/from alarm
# 9 change state of all
# 10 test recover and delete

@author: rhZhou
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.zwatch_operations as zwt_ops

endpoint_uuid_01 = None
endpoint_uuid_02 = None
sns_topic_uuid_01 = None
sns_topic_uuid_02 = None
alarm_uuid = None

def test():
	global endpoint_uuid_01, endpoint_uuid_02, sns_topic_uuid_01, sns_topic_uuid_02, alarm_uuid
	# create endpoint
	url_01 = 'https://oapi.dingtalk.com/robot/send?access_token=0be899d4bd0a7629961a5ccd3035dfba30d084b57944897838f1b601006dd153'
	url_02 = 'https://oapi.dingtalk.com/robot/send?access_token=0be899d4bd0a7629961a5ccd3035dfba30d084b57944897838f1b601006dd153'
	name_01 = 'dingtalkAtPerson'
	name_02 = 'dingtalkAtAll'
	phone_number = '+86-13999999999'
	endpoint_uuid_01 = zwt_ops.create_sns_dingtalk_endpoint(url_01, name_01, at_all=False).uuid
	cond = res_ops.gen_query_conditions('uuid', '=', endpoint_uuid_01)
	if not res_ops.query_resource(res_ops.SNS_DING_TALK_ENDPOINT, cond):
		test_util.test_fail('create sns dingtalk endpoint failed')
	zwt_ops.add_sns_dingtalk_at_person(phone_number, endpoint_uuid_01)
	cond = res_ops.gen_query_conditions('uuid', '=', endpoint_uuid_01)
	inv = res_ops.query_resource(res_ops.SNS_DING_TALK_ENDPOINT, cond)[0]
	if phone_number not in inv.atPersonPhoneNumbers:
		test_util.test_fail('add sns dingtalk at person failed')
	zwt_ops.remove_sns_dingtalk_at_person(phone_number, endpoint_uuid_01)
	cond = res_ops.gen_query_conditions('uuid', '=', endpoint_uuid_01)
	inv = res_ops.query_resource(res_ops.SNS_DING_TALK_ENDPOINT, cond)[0]
	if phone_number in inv.atPersonPhoneNumbers:
		test_util.test_fail('remove sns dingtalk at person failed')
	endpoint_uuid_02 = zwt_ops.create_sns_dingtalk_endpoint(url_02, name_02, at_all=True).uuid
	cond = res_ops.gen_query_conditions('uuid', '=', endpoint_uuid_02)
	if not res_ops.query_resource(res_ops.SNS_DING_TALK_ENDPOINT, cond):
		test_util.test_fail('create sns dingtalk endpoint failed')

	# update endpoint
	endpoint_new_name = 'dingtalkAtpersonNew'
	endpoint_description = 'this is a description for atperson'
	zwt_ops.update_sns_application_endpoint(endpoint_uuid_01, endpoint_new_name, endpoint_description)
	cond = res_ops.gen_query_conditions('name', '=', endpoint_new_name)
	endpoint = res_ops.query_resource(res_ops.SNS_DING_TALK_ENDPOINT, cond)[0]
	if endpoint.description != endpoint_description:
		test_util.test_fail('update sns application endpoint failed')

	# create sns topic
	sns_topic_uuid_01 = zwt_ops.create_sns_topic('sns_topic_01').uuid
	cond = res_ops.gen_query_conditions('uuid', '=', sns_topic_uuid_01)
	if not res_ops.query_resource(res_ops.SNS_TOPIC, cond):
		test_util.test_fail('create sns topic failed')
	sns_topic_uuid_02 = zwt_ops.create_sns_topic('sns_topic_02').uuid
	cond = res_ops.gen_query_conditions('uuid', '=', sns_topic_uuid_02)
	if not res_ops.query_resource(res_ops.SNS_TOPIC, cond):
		test_util.test_fail('create sns topic failed')

	# update sns topic
	topic_new_name = 'sns_topic_01_new'
	topic_description = 'this is a description for topic'
	zwt_ops.update_sns_topic(sns_topic_uuid_01, topic_new_name, topic_description)
	cond = res_ops.gen_query_conditions('uuid', '=', sns_topic_uuid_01)
	inv = res_ops.query_resource(res_ops.SNS_TOPIC, cond)[0]
	if inv.name != topic_new_name or inv.description != topic_description:
		test_util.test_fail('update sns topic failed')

	# subscribe sns topic
	zwt_ops.subscribe_sns_topic(sns_topic_uuid_01, endpoint_uuid_01)
	cond = res_ops.gen_query_conditions('endpoints.uuid', '=', endpoint_uuid_01)
	if not res_ops.query_resource(res_ops.SNS_TOPIC, cond):
		test_util.test_fail('subscribe sns topic failed')
	zwt_ops.subscribe_sns_topic(sns_topic_uuid_01, endpoint_uuid_02)
	cond = res_ops.gen_query_conditions('endpoints.uuid', '=', endpoint_uuid_02)
	if not res_ops.query_resource(res_ops.SNS_TOPIC, cond):
		test_util.test_fail('subscribe sns topic failed')
	zwt_ops.subscribe_sns_topic(sns_topic_uuid_02, endpoint_uuid_02)
	cond = res_ops.gen_query_conditions('endpoints.uuid', '=', endpoint_uuid_02)
	if len(res_ops.query_resource(res_ops.SNS_TOPIC, cond)) != 2:
		test_util.test_fail('subscribe sns topic failed')

	# create alarm
	namespace = 'ZStack/VM'
	actions = [{"actionUuid": sns_topic_uuid_01, "actionType": "sns"}]
	period = 60
	comparisonOperator = 'GreaterThanOrEqualTo'
	threshold = 10
	metric_name = 'CPUUsedUtilization'
	alarm = zwt_ops.create_alarm(comparisonOperator, period, threshold, namespace, metric_name, actions=actions)
	alarm_uuid = alarm.uuid
	cond = res_ops.gen_query_conditions('uuid', '=', alarm_uuid)
	inv = res_ops.query_resource(res_ops.ALARM, cond)
	if not inv:
		test_util.test_fail('create alarm Failed')

	# test update alarm
	new_name = 'total_image_count_alarm'
	zwt_ops.update_alarm(alarm_uuid, name=new_name, period=10)
	cond = res_ops.gen_query_conditions('uuid', '=', alarm_uuid)
	inv = res_ops.query_resource(res_ops.ALARM, cond)[0]
	if inv.period != 10 or inv.name != new_name:
		test_util.test_fail('update alarm Failed')

	# test add action to alarm
	action_type = 'sns'
	zwt_ops.add_action_to_alarm(alarm_uuid, sns_topic_uuid_02, action_type)
	cond = res_ops.gen_query_conditions('uuid', '=', alarm_uuid)
	inv = res_ops.query_resource(res_ops.ALARM, cond)[0]
	flag = False
	for action in inv.actions:
		if action.actionUuid == sns_topic_uuid_02:
			flag = True
	if not flag:
		test_util.test_fail('add action to alarm failed')

	# test remove action from alarm
	zwt_ops.remove_action_from_alarm(alarm_uuid, sns_topic_uuid_02)
	cond = res_ops.gen_query_conditions('uuid', '=', alarm_uuid)
	inv = res_ops.query_resource(res_ops.ALARM, cond)[0]
	flag = False
	for action in inv.actions:
		if action.actionUuid == sns_topic_uuid_02:
			flag = True
	if flag:
		test_util.test_fail('remove action from alarm failed')

	# test add label to alarm
	key = 'VMUuid'
	operator = 'Equal'
	value = '1a1d7395cf74474ca52deb80c41214a1'
	zwt_ops.add_label_to_alarm(alarm_uuid, key, value, operator)
	cond = res_ops.gen_query_conditions('uuid', '=', alarm_uuid)
	inv = res_ops.query_resource(res_ops.ALARM, cond)[0]
	if not inv.labels:
		test_util.test_fail('add label to alarm failed')
	label_uuid = inv.labels[0].uuid

	# test remove label from alarm
	zwt_ops.remove_label_from_alarm(label_uuid)
	cond = res_ops.gen_query_conditions('uuid', '=', alarm_uuid)
	inv = res_ops.query_resource(res_ops.ALARM, cond)[0]
	if inv.labels:
		test_util.test_fail('remove label from alarm failed')

	# test change state
	state_event = 'disable'
	state_result = 'Disabled'
	zwt_ops.change_alarm_state(alarm_uuid, state_event)
	cond = res_ops.gen_query_conditions('uuid', '=', alarm_uuid)
	inv = res_ops.query_resource(res_ops.ALARM, cond)[0]
	if inv.state != state_result:
		test_util.test_fail('change alarm state failed')
	zwt_ops.change_sns_application_endpoint_state(endpoint_uuid_02, state_event)
	cond = res_ops.gen_query_conditions('uuid', '=', endpoint_uuid_02)
	inv = res_ops.query_resource(res_ops.SNS_APPLICATION_ENDPOINT, cond)[0]
	if inv.state != state_result:
		test_util.test_fail('change sns application endpoint failed')
	zwt_ops.change_sns_topic_state(sns_topic_uuid_02, state_event)
	cond = res_ops.gen_query_conditions('uuid', '=', sns_topic_uuid_02)
	inv = res_ops.query_resource(res_ops.SNS_TOPIC, cond)[0]
	if inv.state != state_result:
		test_util.test_fail('change sns topic state failed')

	# test recover and delete
	state_event = 'enable'
	state_result = 'Enabled'
	zwt_ops.change_alarm_state(alarm_uuid, state_event)
	cond = res_ops.gen_query_conditions('uuid', '=', alarm_uuid)
	inv = res_ops.query_resource(res_ops.ALARM, cond)[0]
	if inv.state != state_result:
		test_util.test_fail('change alarm state failed')
	zwt_ops.change_sns_application_endpoint_state(endpoint_uuid_02, state_event)
	cond = res_ops.gen_query_conditions('uuid', '=', endpoint_uuid_02)
	inv = res_ops.query_resource(res_ops.SNS_APPLICATION_ENDPOINT, cond)[0]
	if inv.state != state_result:
		test_util.test_fail('change sns application endpoint failed')
	zwt_ops.change_sns_topic_state(sns_topic_uuid_02, state_event)
	cond = res_ops.gen_query_conditions('uuid', '=', sns_topic_uuid_02)
	inv = res_ops.query_resource(res_ops.SNS_TOPIC, cond)[0]
	if inv.state != state_result:
		test_util.test_fail('change sns topic state failed')
	zwt_ops.unsubscribe_sns_topic(sns_topic_uuid_01, endpoint_uuid_01)
	cond = res_ops.gen_query_conditions('endpoints.uuid', '=', endpoint_uuid_01)
	if res_ops.query_resource(res_ops.SNS_TOPIC, cond):
		test_util.test_fail('unsubscribe sns topic failed')
	zwt_ops.unsubscribe_sns_topic(sns_topic_uuid_01, endpoint_uuid_02)
	zwt_ops.unsubscribe_sns_topic(sns_topic_uuid_02, endpoint_uuid_02)
	cond = res_ops.gen_query_conditions('endpoints.uuid', '=', endpoint_uuid_02)
	if res_ops.query_resource(res_ops.SNS_TOPIC, cond):
		test_util.test_fail('unsubscribe sns topic failed')
	zwt_ops.delete_alarm(alarm_uuid)
	cond = res_ops.gen_query_conditions('uuid', '=', alarm_uuid)
	inv = res_ops.query_resource(res_ops.ALARM, cond)
	if inv:
		test_util.test_fail('delete alarm failed')
	zwt_ops.delete_sns_topic(sns_topic_uuid_01)
	cond = res_ops.gen_query_conditions('uuid', '=', sns_topic_uuid_01)
	inv = res_ops.query_resource(res_ops.SNS_TOPIC, cond)
	if inv:
		test_util.test_fail('delete sns topic failed')
	zwt_ops.delete_sns_topic(sns_topic_uuid_02)
	cond = res_ops.gen_query_conditions('uuid', '=', sns_topic_uuid_02)
	inv = res_ops.query_resource(res_ops.SNS_TOPIC, cond)
	if inv:
		test_util.test_fail('delete sns topic failed')
	zwt_ops.delete_sns_application_endpoint(endpoint_uuid_01)
	cond = res_ops.gen_query_conditions('uuid', '=', endpoint_uuid_01)
	inv = res_ops.query_resource(res_ops.SNS_APPLICATION_ENDPOINT, cond)
	if inv:
		test_util.test_fail('delete sns application endpoint  failed')
	zwt_ops.delete_sns_application_endpoint(endpoint_uuid_02)
	cond = res_ops.gen_query_conditions('uuid', '=', endpoint_uuid_02)
	inv = res_ops.query_resource(res_ops.SNS_APPLICATION_ENDPOINT, cond)
	if inv:
		test_util.test_fail('delete sns application endpoint  failed')

	test_util.test_pass('success test alarm with dingtalk endpoint basic option!')


# Will be called only if exception happens in test().
def error_cleanup():
	global endpoint_uuid_01, endpoint_uuid_02, sns_topic_uuid_01, sns_topic_uuid_02, alarm_uuid
	if alarm_uuid:
		zwt_ops.delete_alarm(alarm_uuid)
	if sns_topic_uuid_01:
		zwt_ops.delete_sns_topic(sns_topic_uuid_01)
	if sns_topic_uuid_02:
		zwt_ops.delete_sns_topic(sns_topic_uuid_02)
	if endpoint_uuid_02:
		zwt_ops.delete_sns_application_endpoint(endpoint_uuid_02)
	if endpoint_uuid_01:
		zwt_ops.delete_sns_application_endpoint(endpoint_uuid_01)
