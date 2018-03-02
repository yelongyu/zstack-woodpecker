'''
test basic function of alarm and dingtalk

# 1 create two dingtalkendpoint , one atAll, another atPerson
# 2 test update endpoint
# 3 create a sns topic and the both endpoint subscribe it
# 4 create a alarm and the sns topic subscribe it
# 5 update the alarm's name and period
# 6 change the alarm's state to 'disable'
# 7 test recover and delete

@author: rhZhou
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops

test_stub = test_lib.lib_get_test_stub()

endpoint_uuid_01 = None
endpoint_uuid_02 = None
sns_topic_uuid = None
alarm_uuid = None


def test():
	global endpoint_uuid_01, endpoint_uuid_02, sns_topic_uuid, alarm_uuid
	# create endpoint
	url_01 = 'https://oapi.dingtalk.com/robot/send?access_token=fed78d1384e0818fbd23d4eda0114315d9db84a7bbefbe0dcde724d7b0fe1484'
	url_02 = 'https://oapi.dingtalk.com/robot/send?access_token=fed78d1384e0818fbd23d4eda0114315d9db84a7bbefbe0dcde724d7b0fe1484'
	name_01 = 'dingtalkAtPerson'
	name_02 = 'dingtalkAtAll'
	phone_number = '18482223118'

	endpoint_uuid_01 = test_stub.create_sns_dingtalk_endpoint(url_01, name_01, at_all=False).uuid
	inventory = test_stub.add_sns_dingtalk_at_person(phone_number, endpoint_uuid_01)
	if inventory.phoneNumber != phone_number:
		test_util.test_fail('add sns dingtalk at person failed')
	endpoint_uuid_02 = test_stub.create_sns_dingtalk_endpoint(url_02, name_02, at_all=True).uuid

	# update endpoint
	endpoint_new_name = 'dingtalkAtpersonNew'
	description = 'this is a description for atperson'
	test_stub.update_sns_application_endpoint(endpoint_uuid_01, endpoint_new_name, description)
	cond = res_ops.gen_query_conditions('name', '=', endpoint_new_name)
	endpoint = res_ops.query_resource(res_ops.SNS_DING_TALK_ENDPOINT, cond)[0]
	if endpoint.description != description:
		test_util.test_fail('update sns application endpoint failed')

	# create sns topic
	sns_topic_uuid = test_stub.create_sns_topic('sns_topic_01').uuid
	test_stub.subscribe_sns_topic(sns_topic_uuid, endpoint_uuid_01)
	test_stub.subscribe_sns_topic(sns_topic_uuid, endpoint_uuid_02)

	# create alarm
	namespace = 'ZStack/Image'
	actions = [{"actionUuid": sns_topic_uuid, "actionType": "sns"}]
	period = 60
	comparisonOperator = 'GreaterThanOrEqualTo'
	threshold = 10
	metric_name = 'TotalImageCount'

	alarm = test_stub.create_alarm(comparisonOperator, period, threshold, namespace, metric_name, actions=actions)
	alarm_uuid = alarm.uuid

	cond = res_ops.gen_query_conditions('uuid', '=', alarm_uuid)
	inventories = res_ops.query_resource(res_ops.ALARM, cond)
	if not inventories:
		test_util.test_fail('create alarm Failed')

	# test update alarm
	new_name = 'total_image_count_alarm'
	test_stub.update_alarm(alarm_uuid, name=new_name, period=10)
	cond = res_ops.gen_query_conditions('uuid', '=', alarm_uuid)
	inventory = res_ops.query_resource(res_ops.ALARM, cond)[0]
	if inventory.period != 10 or inventory.name != new_name:
		test_util.test_fail('update alarm Failed')

	# test change state
	state_event = 'disable'
	test_stub.change_alarm_state(alarm_uuid, state_event)
	test_stub.change_sns_application_endpoint_state(endpoint_uuid_02, state_event)

	# test recover and delete
	test_stub.change_alarm_state(alarm_uuid, 'enable')
	test_stub.change_sns_application_endpoint_state(endpoint_uuid_02, 'enable')
	test_stub.delete_alarm(alarm_uuid)
	test_stub.unsubscribe_sns_topic(sns_topic_uuid, endpoint_uuid_01)
	test_stub.unsubscribe_sns_topic(sns_topic_uuid, endpoint_uuid_02)
	test_stub.delete_sns_topic(sns_topic_uuid, delete_mode='Delay')
	test_stub.remove_sns_dingtalk_at_person(phone_number, endpoint_uuid_01, delete_mode='Delay')
	test_stub.delete_sns_application_endpoint(endpoint_uuid_01)
	test_stub.delete_sns_application_endpoint(endpoint_uuid_02, delete_mode='Delay')  # delete_mode test

	test_util.test_pass('success test alarm with dingtalk endpoint basic option!')


# Will be called only if exception happens in test().
def error_cleanup():
	global endpoint_uuid_01, endpoint_uuid_02, sns_topic_uuid, alarm_uuid
	if alarm_uuid:
		test_stub.delete_alarm(alarm_uuid)
	if sns_topic_uuid:
		test_stub.delete_sns_topic(sns_topic_uuid)
	if endpoint_uuid_02:
		test_stub.delete_sns_application_endpoint(endpoint_uuid_02)
	if endpoint_uuid_01:
		test_stub.delete_sns_application_endpoint(endpoint_uuid_01)
