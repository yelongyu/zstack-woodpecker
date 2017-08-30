'''

Create an unified test_stub to share test operations

@author: Songtao
'''

import os
import subprocess
import time
import threading
import uuid

import zstacklib.utils.ssh as ssh
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.zstack_test.zstack_test_vm as zstack_vm_header
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.operations.monitor_operations as mon_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import os, sys, string
import poplib


def create_vm():
    global vm
    vm_creation_option = test_util.VmOption()
    image_name = os.environ.get('imageName_s')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    l3_name = os.environ.get('l3PublicNetworkName')

    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
    instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid
    vm_creation_option.set_l3_uuids([l3_net_uuid])
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_name('vm_'+ ''.join(map(lambda xx:(hex(ord(xx))[2:]),os.urandom(8))))
    vm = test_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    return  vm

def get_monitor_item(resourceType):
    monitor_item_name = []
    vm_db = "VmInstanceVO"
    host_db = "HostVO"
    if resourceType == vm_db:
        monitor_item = mon_ops.get_monitor_item(vm_db)
    elif resourceType == host_db:
         monitor_item = mon_ops.get_monitor_item(host_db)
    for item in monitor_item:
        monitor_item_name.append(item.name)
    return monitor_item_name

def query_monitor_trigger(monitor_trigger_uuid):
    cond = res_ops.gen_query_conditions('uuid', '=', monitor_trigger_uuid)
    return res_ops.query_resource(res_ops.MONITOR_TRIGGER, cond)

def query_monitor_trigger_action(monitor_trigger_action_uuid):
    cond = res_ops.gen_query_conditions('uuid', '=', monitor_trigger_action_uuid)
    return res_ops.query_resource(res_ops.MONITOR_TRIGGER_ACTION, cond)

def query_vmnic(ip):
    cond = res_ops.gen_query_conditions('ip','=',ip)
    return res_ops.query_resource(res_ops.VM_NIC, cond)

def query_trigger_in_loop(trigger,retry_times1):
    retry_times=retry_times1
    Problem = 0
    OK = 0
    while retry_times >0 and Problem == 0:
        time.sleep(10)
        retry_times -= 1
        tirgger_Q = query_monitor_trigger(trigger)
        trigger_status = tirgger_Q[0].status
        if trigger_status == "Problem":
            Problem = 1
            retry_times -= 1
            while retry_times > 0 and Problem == 1:
                time.sleep(10)
                retry_times -= 1
                tirgger_Q = query_monitor_trigger(trigger)
                trigger_status = tirgger_Q[0].status
                if trigger_status == "OK":
                    OK = 1
                    break
            break
    return Problem, OK

def query_trigger_is_problem(trigger,monitor_trigger):
    retry_times = 50
    Problem = 0
    while retry_times >0 and Problem == 0:
        time.sleep(10)
        retry_times -= 1
        tirgger_Q = query_monitor_trigger(trigger)
        trigger_status = tirgger_Q[0].status
        if trigger_status == "Problem":
            Problem = 1
            retry_times -= 1
            stateevent = "disable"
            monitor_trigger =mon_ops.change_monitor_trigger_state(trigger,stateevent)
            break
    return Problem

def create_email_media():
    media_name = "email" + ''.join(map(lambda xx: (hex(ord(xx))[2:]), os.urandom(8)))
    port = os.environ.get('media_smtpport')
    server = os.environ.get('media_smtpserver')
    mail_name = os.environ.get('media_username')
    mail_password = os.environ.get('media_password')
    return mon_ops.create_email_media(media_name, port, server, mail_name, mail_password)


def receive_email():
    server = os.environ.get('receive_pop3server')
    email = os.environ.get('receive_email')
    password = os.environ.get('receive_password')
    pop3 = poplib.POP3(server)
    pop3.set_debuglevel(1)
    pop3.user(email)
    pop3.pass_(password)
    ret = pop3.stat()
    test_util.action_logger('Messages: %s. Size: %s' % pop3.stat())
    mail_list = []
    for i in range(ret[0] - 20, ret[0]):
        resp, msg, octets = pop3.retr(i)
        mail_list.append(msg)
    return mail_list



def check_email(list, keywords, trigger, target_uuid):
    mail = os.environ.get('media_username')
    flag = 0
    print mail
    for i in list:
        '''check mail list form the mail sender'''
        if 'MF='+ mail in i[0]:
            test_util.action_logger('Mail sent addr is %s' % mail)
            if (trigger in i[13].lower()) and (target_uuid in i[13]) and keywords in i[8]:
                flag = 1
                test_util.action_logger('Got Target: %s for: %s Trigger Mail' % (target_uuid, trigger))
                test_util.action_logger('Mail detail info is %s' % i)
                break
            #test_util.action_logger('Mail sent date is %s' % i[3].split(',')[1].lstrip())
            #mail_date = i[3].split(',')[1].lstrip()[:-6]
            #mail_time = time.mktime(time.strptime(mail_date, "%d %b %Y %H:%M:%S"))
            #if operate_time > mail_time:
            #    print "Got an old email"
    test_util.action_logger('flag value is %s' % flag)
    return flag

def execute_shell_in_process(cmd, timeout=10, logfd=None):
    if not logfd:
        process = subprocess.Popen(cmd, executable='/bin/sh', shell=True, universal_newlines=True)
    else:
        process = subprocess.Popen(cmd, executable='/bin/sh', shell=True, stdout=logfd, stderr=logfd, universal_newlines=True)

    start_time = time.time()
    while process.poll() is None:
        curr_time = time.time()
        TEST_TIME = curr_time - start_time
        if TEST_TIME > timeout:
            process.kill()
            test_util.test_logger('[shell:] %s timeout ' % cmd)
            return False
        time.sleep(1)

    test_util.test_logger('[shell:] %s is finished.' % cmd)
    return process.returncode

def ssh_cmd_line(ip_addr, username, password, port):
    ssh_cmd = '/usr/bin/sshpass -p %s ssh  %s@%s -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null  -p %s' \
              % (password, username, ip_addr, port)
    return ssh_cmd

def yum_install_stress_tool(ssh_cmd_line):
    timeout = 330
    cmd = '%s "yum install -y fio stress iperf enablerepo=ali* --nogpgcheck"' % (ssh_cmd_line)
    if execute_shell_in_process(cmd, timeout) != 0:
        test_util.test_fail('fail to install stress')

def run_cpu_load(ssh_cmd_line, cpu_core, threads):
    timeout = 100
    cmd = '%s "taskset -c %s stress --timeout 90 --cpu %s"' % (ssh_cmd_line, cpu_core,threads)
    if execute_shell_in_process(cmd, timeout) != 0:
        test_util.test_fail('cpu load fail to run')

def run_all_cpus_load(ssh_cmd_line):
    timeout= 100
    cmd ='%s "stress --timeout 90 --cpu $(cat /proc/cpuinfo|grep \"processor\"|wc -l)"' %ssh_cmd_line
    if execute_shell_in_process(cmd, timeout) != 0:
        test_util.test_fail('cpu load fail to run')

def run_mem_load(ssh_cmd_line,runtime):
    timeout = 100
    cmd = '%s "stress --vm-bytes $(awk \'/MemFree/{printf \"%%d\\n\", $2 * 0.95;}\' < /proc/meminfo)k --vm-keep -m 1 -t %d"' % (ssh_cmd_line,runtime)
    if execute_shell_in_process(cmd, timeout) != 0:
        test_util.test_fail('mem load fail to run')

def run_disk_load(ssh_cmd_line, rw):
    timeout = 100
    cmd = '%s "fio -filename=/tmp/test -direct=1 -iodepth 1 -thread -rw=%s -ioengine=psync -bs=16k -size=4G -numjobs=10 -runtime=80 -group_reporting -name=mytest"' \
          % (ssh_cmd_line, rw)
    if execute_shell_in_process(cmd, timeout) != 0:
        test_util.test_fail('disk io load fail to run')

def run_iperf_server(ssh_cmd_line):
    timeout = 100
    cmd = '%s "iptables -F;nohup netperf -s  >/root/tmp.log & "' % ssh_cmd_line

def run_iperf_client(ssh_cmd_line, server_ip, runtime):
    timeout = 100
    cmd = '%s "netperf -d -c %s -t %d >/root/test.log &"' % (ssh_cmd_line, server_ip,runtime)
    if execute_shell_in_process(cmd, timeout) != 0:
        test_util.test_fail('network io load fail to run')

def run_disk_load1(ssh_cmd_line,rw):
    if rw == 'write':
        os.system('%s "dd if=/dev/zero of=test.dbf bs=8k count=300000 oflag=direct,nonblock"'% ssh_cmd_line)
    else:
        os.system('%s "dd if=/dev/vda of=/dev/null bs=8k iflag=direct,nonblock"' % ssh_cmd_line)

def run_network_load(ssh_cmd_line):
   os.system('%s "wget http://192.168.200.100/mirror/diskimages/win7.qcow2"' % ssh_cmd_line) 

def kill(ssh_cmd_line):
    os.system('%s "ps -A|grep -w dd|awk \'{print $1}\'|xargs kill -9"' % ssh_cmd_line)
    os.system('%s "ps -A|grep wget|awk \'{print $1}\'|xargs kill -9"' % ssh_cmd_line)
    os.system('%s "rm -rf win7.qcow2"' % ssh_cmd_line)
