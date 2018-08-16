'''
test host ,bs, ps disconnected event with email

@author: Ronghao.zhou
'''
import time as time

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.zwatch_operations as zwt_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.operations.primarystorage_operations as ps_ops
import zstackwoodpecker.operations.backupstorage_operations as bs_ops
import os

test_stub = test_lib.lib_get_test_stub()

email_platform_uuid=None
email_endpoint_uuid=None
my_sns_topic_uuid=None
host_sns_topic_uuid=None
ps_uuid=None
hostname=None
host_management_ip=None
host_uuid =None
host_status=None
bs_uuid=None
bs_type=None
bs_status=None
event_list=[]

def test():
    global email_endpoint_uuid,email_platform_uuid,my_sns_topic_uuid,host_sns_topic_uuid,ps_uuid,hostname,host_management_ip,host_uuid,host_status,bs_uuid,bs_type,bs_status
    bs_cond = res_ops.gen_query_conditions('status', '=', 'Connected')
    bs_list = res_ops.query_resource(res_ops.BACKUP_STORAGE, bs_cond)
    for bss in bs_list:
        if bss.type ==res_ops.SFTP_BACKUP_STORAGE:
            bs_uuid =bss.uuid
            bs_type =bss.type
            hostname = bss.hostname
            break
        elif bss.type == res_ops.IMAGE_STORE_BACKUP_STORAGE:
            bs_uuid=bss.uuid
            bs_type=bss.type
            hostname = bss.hostname
            break
        else:
            test_util.test_skip('No match backupStorage,test skip')

    smtp_server = os.environ.get('smtpServer')
    pop_server = os.environ.get('popServer')
    smtp_port = os.environ.get('smtpPort')
    username = os.environ.get('mailUsername')
    password = os.environ.get('mailPassword')
    email_platform_name='Alarm_email'
    email_platform = zwt_ops.create_sns_email_platform(smtp_server, smtp_port,email_platform_name , username, password)
    email_platform_uuid = email_platform.uuid
    try:
        zwt_ops.validate_sns_email_platform(email_platform_uuid)
    except:
        test_util.test_fail('Validate SNS Email Platform Failed, Email Plarform: %s' % email_platform_uuid)
    email_endpoint_uuid = zwt_ops.create_sns_email_endpoint(username, 'test_qa', email_platform_uuid).uuid

    my_sns_topic = zwt_ops.create_sns_topic('my_sns_topic')
    my_sns_topic_uuid = my_sns_topic.uuid
    zwt_ops.subscribe_sns_topic(my_sns_topic_uuid, email_endpoint_uuid)

    host_sns_topic = zwt_ops.create_sns_topic('host_topic')
    host_sns_topic_uuid = host_sns_topic.uuid
    zwt_ops.subscribe_sns_topic(host_sns_topic_uuid, email_endpoint_uuid)

    ps_actions = [{"actionUuid": my_sns_topic_uuid, "actionType": "sns"}]
    ps_namespace = 'ZStack/PrimaryStorage'
    ps_disconnected = 'PrimaryStorageDisconnected'
    ps_event_sub_uuid = zwt_ops.subscribe_event(ps_namespace, ps_disconnected, ps_actions).uuid
    event_list.append(ps_event_sub_uuid)

    bs_actions = [{"actionUuid": my_sns_topic_uuid, "actionType": "sns"}]
    bs_namespace = 'ZStack/BackupStorage'
    bs_disconnected = 'BackupStorageDisconnected'
    bs_event_sub_uuid = zwt_ops.subscribe_event(bs_namespace, bs_disconnected, bs_actions).uuid
    event_list.append(bs_event_sub_uuid)

    host_actions = [{"actionUuid": host_sns_topic_uuid, "actionType": "sns"}]
    host_namespace = 'ZStack/Host'
    host_status_changed = 'HostStatusChanged'
    host_status_labels = [{"key": "NewStatus", "op": "Equal", "value": "Disconnected"}]
    host_status_event_sub_uuid = zwt_ops.subscribe_event(host_namespace, host_status_changed, host_actions, host_status_labels).uuid
    event_list.append(host_status_event_sub_uuid)

    host_disconnected = 'HostDisconnected'
    host_disconnected_event_sub_uuid = zwt_ops.subscribe_event(host_namespace, host_disconnected, host_actions).uuid
    event_list.append(host_disconnected_event_sub_uuid)

    if zwt_ops.check_sns_email(pop_server, username, password, ps_disconnected, ps_event_sub_uuid):
        test_util.test_fail('email already exsist before test')
    if zwt_ops.check_sns_email(pop_server, username, password, bs_disconnected, bs_event_sub_uuid):
        test_util.test_fail('email already exsist before test')
    if zwt_ops.check_sns_email(pop_server, username, password, host_status_changed, host_status_event_sub_uuid):
        test_util.test_fail('email already exsist before test')
    if zwt_ops.check_sns_email(pop_server, username, password, host_disconnected, host_disconnected_event_sub_uuid):
        test_util.test_fail('email already exsist before test')

    # Disconnected ps ,bs and host
    zone_uuid = res_ops.query_resource(res_ops.ZONE)[0].uuid
    primary_storage_option = test_util.PrimaryStorageOption()
    primary_storage_option.set_type('nfs')
    primary_storage_option.set_zone_uuid(zone_uuid)
    primary_storage_option.set_name('test_nfs_ps')
    primary_storage_option.set_url('222.222.222.222/nfs/')
    try:
        ps_uuid = ps_ops.create_nfs_primary_storage(primary_storage_option).uuid
        ps_ops.reconnect_primary_storage(ps_uuid)
    except:
        pass

    if bs_type == res_ops.IMAGE_STORE_BACKUP_STORAGE:
        bs_ops.update_image_store_backup_storage_info(bs_uuid, 'hostname', '222.222.222.222')
        try:
            bs_ops.reconnect_backup_storage(bs_uuid)
        except:
            cond = res_ops.gen_query_conditions('uuid', '=', bs_uuid)
            bs_status = res_ops.query_resource(res_ops.IMAGE_STORE_BACKUP_STORAGE, cond)[0].status
    elif bs_type == res_ops.SFTP_BACKUP_STORAGE:
        bs_ops.update_sftp_backup_storage_info(bs_uuid,'hostname','222.222.222.222')
        try:
            bs_ops.reconnect_backup_storage(bs_uuid)
        except:
            cond=res_ops.gen_query_conditions('uuid','=',bs_uuid)
            bs_status=res_ops.query_resource(res_ops.SFTP_BACKUP_STORAGE,cond)[0].status

    host_cond = res_ops.gen_query_conditions('status', '=', 'Connected')
    host = res_ops.query_resource_with_num(res_ops.HOST, host_cond, start=0, limit=1)[0]
    host_uuid = host.uuid
    host_management_ip = host.managementIp
    host_ops.update_host(host_uuid, 'managementIp', '222.222.222.222')
    try:
        host_ops.reconnect_host(host_uuid)
    except:
        cond = res_ops.gen_query_conditions('uuid', '=', host_uuid)
        bs_status = res_ops.query_resource(res_ops.HOST, cond)[0].status

    # wait for send email
    time.sleep(120)

    ps_ops.delete_primary_storage(ps_uuid)
    if hostname:
        if bs_type == res_ops.IMAGE_STORE_BACKUP_STORAGE:
            bs_ops.update_image_store_backup_storage_info(bs_uuid, 'hostname', hostname)
            bs_ops.reconnect_backup_storage(bs_uuid)
        elif bs_type == res_ops.SFTP_BACKUP_STORAGE:
            bs_ops.update_sftp_backup_storage_info(bs_uuid, 'hostname', hostname)
            bs_ops.reconnect_backup_storage(bs_uuid)
    host_ops.update_host(host_uuid, 'managementIp', host_management_ip)
    host_ops.reconnect_host(host_uuid)
    zwt_ops.delete_sns_topic(host_sns_topic_uuid)
    zwt_ops.delete_sns_topic(my_sns_topic_uuid)
    for event_uuid in event_list:
        zwt_ops.unsubscribe_event(event_uuid)
    zwt_ops.delete_sns_application_endpoint(email_endpoint_uuid)
    zwt_ops.delete_sns_application_platform(email_platform_uuid)

    check_1 = zwt_ops.check_sns_email(pop_server, username, password, ps_disconnected, ps_event_sub_uuid)
    check_2 = zwt_ops.check_sns_email(pop_server, username, password, bs_disconnected, bs_event_sub_uuid)
    check_3 = zwt_ops.check_sns_email(pop_server, username, password, host_status_changed, host_status_event_sub_uuid)
    check_4 = zwt_ops.check_sns_email(pop_server, username, password, host_disconnected, host_disconnected_event_sub_uuid)

    if check_1 and check_2 and check_3 and check_4:
        test_util.test_pass('test host ,bs, ps disconnected event with email success!')
    else:
        test_util.test_fail('cannt receive all event mail')


# Will be called only if exception happens in test().
def error_cleanup():
    global email_endpoint_uuid,email_platform_uuid,my_sns_topic_uuid,host_sns_topic_uuid,ps_uuid,hostname,host_management_ip,host_status,bs_type,bs_status,event_list
    if host_status == 'Disconnected':
        host_ops.update_host(host_uuid, 'managementIp', host_management_ip)
        host_ops.reconnect_host(host_uuid)
    if bs_status == 'Disconnected':
        if bs_type == res_ops.IMAGE_STORE_BACKUP_STORAGE:
            bs_ops.update_image_store_backup_storage_info(bs_uuid, 'hostname', hostname)
            bs_ops.reconnect_backup_storage(bs_uuid)
        elif bs_type == res_ops.SFTP_BACKUP_STORAGE:
            bs_ops.update_sftp_backup_storage_info(bs_uuid, 'hostname', hostname)
            bs_ops.reconnect_backup_storage(bs_uuid)
    if ps_uuid:
        ps_ops.delete_primary_storage(ps_uuid)
    if host_sns_topic_uuid:
        zwt_ops.delete_sns_topic(host_sns_topic_uuid)
    if my_sns_topic_uuid:
        zwt_ops.delete_sns_topic(my_sns_topic_uuid)
    if event_list:
        for event_uuid in event_list:
            zwt_ops.unsubscribe_event(event_uuid)
    if email_endpoint_uuid:
        zwt_ops.delete_sns_application_endpoint(email_endpoint_uuid)
    if email_platform_uuid:
        zwt_ops.delete_sns_application_platform(email_platform_uuid)

