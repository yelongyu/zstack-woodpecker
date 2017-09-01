'''

This test is about eamil server.

@author:haoChen

'''
import os
import test_stub
import random
import time
import zstacklib.utils.ssh as ssh
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.monitor_operations as mon_ops

def test():
    global trigger
    global media
    global trigger_action

    test_item = "create.email.server"
    hosts = res_ops.get_resource(res_ops.HOST)
    host = hosts[0]
    duration = 60
    expression = "host.cpu.util{cpu=-1,type=\"used\"}>200"
    monitor_trigger = mon_ops.create_monitor_trigger(host.uuid, duration, expression)

    send_email = test_stub.create_email_media()
    media = send_email.uuid
    trigger_action_name = "trigger"+ ''.join(map(lambda xx:(hex(ord(xx))[2:]),os.urandom(8)))
    trigger = monitor_trigger.uuid
    receive_email = os.environ.get('receive_email')
    monitor_trigger_action = mon_ops.create_email_monitor_trigger_action(trigger_action_name, send_email.uuid, trigger.split(), receive_email)
    trigger_action = monitor_trigger_action.uuid
    
    time.sleep(100)
    mail_list = test_stub.receive_email()
    keywords = "ZStack-Monitor"
    result = 'success'
    mail_flag = test_stub.check_email(mail_list, keywords, trigger_action, result)
    if mail_flag == 0:
        test_util.test_fail('Failed to Get Target: %s for: %s Trigger Mail' % (host.uuid, test_item))

    mon_ops.delete_monitor_trigger_action(trigger_action)
    mon_ops.delete_monitor_trigger(trigger)
    mon_ops.delete_email_media(media)

def error_cleanup():
    global trigger
    global media
    global trigger_action
    mon_ops.delete_monitor_trigger_action(trigger_action)
    mon_ops.delete_monitor_trigger(trigger)
    mon_ops.delete_email_media(media)
