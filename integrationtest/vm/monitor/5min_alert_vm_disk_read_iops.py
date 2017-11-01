'''

Test about monitor trigger on vm disk reading iops in five minutes

@author: Songtao,Haochen

'''

import os
import test_stub
import random
import zstacklib.utils.ssh as ssh
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.monitor_operations as mon_ops

def test():
    global vm
    global trigger
    global media
    global trigger_action

    vm = test_stub.create_vm()
    vm.check()
    vm_ip = vm.get_vm().vmNics[0].ip
    vm_uuid = vm.get_vm().uuid
    vm_username = os.environ.get('Vm_Username')
    vm_password = os.environ.get('Vm_Password')
    vm_port = os.environ.get('Vm_Sshport')

    test_item = "vm.disk.io"
    resource_type = "VmInstanceVO"
    vm_monitor_item = test_stub.get_monitor_item(resource_type)
    if test_item not in vm_monitor_item:
        test_util.test_fail('%s is not available for monitor' % test_item)

    duration = 300
    #expression = "vm.disk.io{type=\"iops\", direction=\"read\"} > 250.0"
    expression = "vm.disk.io{type=\"iops\", direction=\"read\"} > 50.0"
    monitor_trigger = mon_ops.create_monitor_trigger(vm_uuid, duration, expression)

    send_email = test_stub.create_email_media()
    media = send_email.uuid
    trigger_action_name = "trigger"+ ''.join(map(lambda xx:(hex(ord(xx))[2:]),os.urandom(8)))
    trigger = monitor_trigger.uuid
    receive_email = os.environ.get('receive_email')
    monitor_trigger_action = mon_ops.create_email_monitor_trigger_action(trigger_action_name, send_email.uuid, trigger.split(), receive_email)
    trigger_action = monitor_trigger_action.uuid

    ssh_cmd = test_stub.ssh_cmd_line(vm_ip, vm_username, vm_password, vm_port)
    test_stub.yum_install_stress_tool(ssh_cmd)
    rw = 'read'
    for i in range(5):test_stub.run_disk_load(ssh_cmd, rw)

    #status_problem, status_ok = test_stub.query_trigger_in_loop(trigger,80)
    status_problem, status_ok = test_stub.query_trigger_in_loop(trigger,50)
    test_util.action_logger('Trigger old status: %s triggered. Trigger new status: %s recovered' % (status_problem, status_ok ))
    if status_problem != 1 or status_ok != 1:
        test_util.test_fail('%s Monitor Test failed, expected Problem or OK status not triggered' % test_item)

    mail_list = test_stub.receive_email()
    keywords = "fired"
    mail_flag = test_stub.check_email(mail_list, keywords, trigger, vm_uuid)
    if mail_flag == 0:
        test_util.test_fail('Failed to Get Target: %s for: %s Trigger Mail' % (vm_uuid, test_item))

    mon_ops.delete_monitor_trigger_action(trigger_action)
    mon_ops.delete_monitor_trigger(trigger)
    mon_ops.delete_email_media(media)
    vm.destroy()

def error_cleanup():
    global trigger
    global media
    global trigger_action
    global vm
    mon_ops.delete_monitor_trigger_action(trigger_action)
    mon_ops.delete_monitor_trigger(trigger)
    mon_ops.delete_email_media(media)
    vm.destroy()
