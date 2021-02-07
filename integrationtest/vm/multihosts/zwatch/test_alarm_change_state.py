'''
test change alarm state to see if it will send alarm email.

@author: Ronghao.zhou
'''
import time as time

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.zwatch_operations as zwt_ops
import os

test_stub = test_lib.lib_get_test_stub()

my_sns_topic_uuid = None
email_platform_uuid = None
email_endpoint_uuid = None
disk_all_write_bytes_alarm_uuid = None
vm = None


def test():
	global email_endpoint_uuid, email_platform_uuid, vm, disk_all_write_bytes_alarm_uuid, my_sns_topic_uuid
	smtp_server = os.environ.get('smtpServer')
	pop_server = os.environ.get('popServer')
	smtp_port = os.environ.get('smtpPort')
	username = os.environ.get('mailUsername')
	password = os.environ.get('mailPassword')
	email_platform_name = 'Alarm_email'
	email_platform_uuid = zwt_ops.create_sns_email_platform(smtp_server, smtp_port,
	                                                        email_platform_name, username, password).uuid
	zwt_ops.validate_sns_email_platform(email_platform_uuid)
	email_endpoint_uuid = zwt_ops.create_sns_email_endpoint(username, 'test_qa',
	                                                        email_platform_uuid).uuid
	my_sns_topic = zwt_ops.create_sns_topic('my_sns_topic')
	my_sns_topic_uuid = my_sns_topic.uuid
	zwt_ops.subscribe_sns_topic(my_sns_topic_uuid, email_endpoint_uuid)

	namespace = 'ZStack/VM'
	less_than = 'LessThan'
	actions = [{"actionUuid": my_sns_topic_uuid, "actionType": "sns"}]
	period = 10
	threshold_3 = 1024 * 1024 * 1024
	disk_all_write_bytes = 'DiskAllWriteBytes'
	disk_all_write_bytes_alarm_uuid = zwt_ops.create_alarm(less_than, period,
	                                                       threshold_3, namespace,
	                                                       disk_all_write_bytes,
	                                                       name='disk_all_write_bytes',
	                                                       repeat_interval=15,
	                                                       actions=actions).uuid
	image_name = os.environ.get('imageName_s')
	l3_name = os.environ.get('l3PublicNetworkName')
	vm = test_stub.create_vm('test_vm', image_name, l3_name)

	# wait for send email
	time.sleep(60)
	flag = zwt_ops.check_keywords_in_email(pop_server, username, password, disk_all_write_bytes,
	                                       disk_all_write_bytes_alarm_uuid)
	if not flag:
		test_util.test_fail('cant receive alarm email ')

	zwt_ops.change_alarm_state(disk_all_write_bytes_alarm_uuid, 'disable')

	time.sleep(10)
	time_stamp = zwt_ops.get_boundary_words()
	zwt_ops.send_boundary_email(time_stamp,smtp_server,username,password,username)

	time.sleep(30)
	flag = zwt_ops.check_keywords_in_email(pop_server, username, password, disk_all_write_bytes,
	                                       disk_all_write_bytes_alarm_uuid, time_stamp)
	if flag:
		test_util.test_fail(
			'the alarm had been changed state to Disabled,we should not receive the email,but we found flag is %s' %
			flag)

	time.sleep(10)
	zwt_ops.change_alarm_state(disk_all_write_bytes_alarm_uuid, 'enable')
	time.sleep(30)

	flag = zwt_ops.check_keywords_in_email(pop_server, username, password, disk_all_write_bytes,
	                                       disk_all_write_bytes_alarm_uuid, time_stamp)
	if not flag:
		test_util.test_fail('cant receive email when it change state to Enable.')

	vm.clean()
	zwt_ops.delete_alarm(disk_all_write_bytes_alarm_uuid)
	zwt_ops.delete_sns_topic(my_sns_topic_uuid)
	zwt_ops.delete_sns_application_endpoint(email_endpoint_uuid)
	zwt_ops.delete_sns_application_platform(email_platform_uuid)

	test_util.test_pass('success')


# Will be called only if exception happens in test().
def error_cleanup():
	global vm, my_sns_topic_uuid, email_endpoint_uuid, email_platform_uuid, disk_all_write_bytes_alarm_uuid
	if vm:
		vm.clean()
	if disk_all_write_bytes_alarm_uuid:
		zwt_ops.delete_alarm(disk_all_write_bytes_alarm_uuid)
	if my_sns_topic_uuid:
		zwt_ops.delete_sns_topic(my_sns_topic_uuid)
	if email_endpoint_uuid:
		zwt_ops.delete_sns_application_endpoint(email_endpoint_uuid)
	if email_platform_uuid:
		zwt_ops.delete_sns_application_platform(email_platform_uuid)
