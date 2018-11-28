'''

Perf Test for creating multiple vms and get the test used time..

@author: jiajun.xu
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.config_operations as con_ops
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import time
import os
import sys
import threading
import random
import string
from test_stub import *
import zstackwoodpecker.operations.zone_operations as zone_ops

case_flavor = dict(vm_100=              dict(vm_num=100),
                   vm_200=              dict(vm_num=200),
                   vm_500=              dict(vm_num=500),
                   vm_1000=             dict(vm_num=1000),
                   vm_10000=            dict(vm_num=10000),
                   )

session_uuid = None
session_to = None
session_mc = None

time_interval = 0

if os.environ.get('CASE_FLAVOR'):
    flavor = case_flavor[os.environ.get('CASE_FLAVOR')]
    num = flavor['vm_num']
else:
    num = 10000

if num == 100 or num == 200:
    time_interval = 200
elif num == 500:
    time_interval = 500
elif num == 1000:
    time_interval = 720
elif num == 10000:
    time_interval = 1800
else:
    time_interval = 300

os.environ['ZSTACK_THREAD_THRESHOLD']=str(num)
os.environ['ZSTACK_TEST_NUM']=str(num)

thread_threshold = os.environ.get('ZSTACK_THREAD_THRESHOLD')
if not thread_threshold:
    thread_threshold = 1000
else:
    thread_threshold = int(thread_threshold)

perf_loop = os.environ.get('ZSTACK_PERF_LOOP')
if not perf_loop:
    perf_loop = 3
else:
    perf_loop = int(perf_loop)

exc_info = []

def check_thread_exception():
    if exc_info:
        info1 = exc_info[0][1]
        info2 = exc_info[0][2]
        raise info1, None, info2

def get_random_name(length):
    letter = [random.choice(string.ascii_letters) for i in range(length)]
    return ''.join([i for i in letter])

class Destroy_VM_Parall(VM_Operation_Parall):
    def operate_vm_parall(self, vm_uuid):
        try:
            vm_ops.destroy_vm(vm_uuid, self.session_uuid)
        except:
            self.exc_info.append(sys.exc_info())

    def check_operation_result(self):
        for i in range(0, self.i):
            v1 = test_lib.lib_get_vm_by_uuid(self.vms[i].uuid)
            if v1.state != "Destroyed":
                test_util.test_fail('Fail to destroy VM %s.' % v1.uuid)

class Expunge_VM_Parall(VM_Operation_Parall):

    def operate_vm_parall(self, vm_uuid):
        try:
            vm_ops.expunge_vm(vm_uuid, self.session_uuid)
        except:
            self.exc_info.append(sys.exc_info())

    def check_operation_result(self):
        for i in range(0, self.i):
            v1 = test_lib.lib_get_vm_by_uuid(self.vms[i].uuid)
            if v1 is not None:
                test_util.test_fail('Fail to expunge VM %s.' % v1.uuid)

def wait_vm_condition(con):
    vm_num = os.environ.get('ZSTACK_TEST_NUM')
    if not vm_num:
        vm_num = 0
    else:
        vm_num = int(vm_num)
    vms = res_ops.query_resource(res_ops.VM_INSTANCE,con)
    print 'WAITING FOR ZSTACK_TEST_NUM'
    while vm_num >len(vms):
        vms = res_ops.query_resource(res_ops.VM_INSTANCE,con)
        time.sleep(120)

def create_vm(vm):
    try:
        vm.create()
    except:
        exc_info.append(sys.exc_info())

def Destroy_VM():
    get_vm_con = res_ops.gen_query_conditions('state', '!=', "Destroyed")
    get_vm_con = res_ops.gen_query_conditions('hypervisorType', '=', "KVM", get_vm_con)
    get_vm_con = res_ops.gen_query_conditions('type', '=', "UserVm", get_vm_con)
    wait_vm_condition(get_vm_con)
    destroyvms = Destroy_VM_Parall(get_vm_con, "Running")
    destroyvms.parall_test_run()
    destroyvms.check_operation_result()

def Expunge_VM():
    get_vm_con = res_ops.gen_query_conditions('state', '=', "Destroyed")
    get_vm_con = res_ops.gen_query_conditions('hypervisorType', '=', "KVM", get_vm_con)
    get_vm_con = res_ops.gen_query_conditions('type', '=', "UserVm", get_vm_con)
    wait_vm_condition(get_vm_con)
    expungevms = Expunge_VM_Parall(get_vm_con, "Running")
    expungevms.parall_test_run()
    expungevms.check_operation_result()

def time_convert(log_str):
    time_str = log_str.split()[0]+' '+log_str.split()[1]
    time_microscond = time_str.split(',')[1]
    time_str = time_str.split(',')[0]
    time_tuple = time.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    return int(time.mktime(time_tuple)*1000+int(time_microscond))

def get_begin_time(vm_name_prefix, operation):

    begin_time = 0
    start_line = 0
    mn_server_log = "/usr/local/zstacktest/apache-tomcat/logs/management-server.log"
    file_obj = open(mn_server_log)

    if operation == 'create':
        for line in file_obj.readlines():
            if line.find('APICreateVmInstanceMsg') != -1 and line.find(vm_name_prefix) != -1:
                begin_time = time_convert(line)
                break
    elif operation == 'destroy':
        for (num, line) in enumerate(file_obj):
            if line.find('APICreateVmInstanceMsg') != -1 and line.find(vm_name_prefix) != -1:
		start_line = num
                continue
            if line.find('APIDestroyVmInstanceMsg') != -1 and line.find('msg send') != -1:
		if num > start_line and start_line != 0:
                    begin_time = time_convert(line)
                    break
    elif operation == 'expunge':
        for (num, line) in enumerate(file_obj):
            if line.find('APICreateVmInstanceMsg') != -1 and line.find(vm_name_prefix) != -1:
		start_line = num
                continue
            if line.find('APIExpungeVmInstanceMsg') != -1 and line.find('msg send') != -1:
		if num > start_line and start_line != 0:
                    begin_time = time_convert(line)
                    break
    else:
        test_util.test_logger('Unknown option %s' % operation)

    file_obj.close()
    log_str = ''
    return begin_time

def get_end_time(vm_name_prefix, operation):
    
    end_time = 0
    start_line = 0
    mn_server_log = "/usr/local/zstacktest/apache-tomcat/logs/management-server.log"
    file_obj = open(mn_server_log)

    if operation == 'create':
        for line in file_obj.readlines():
            if line.find('event received') != -1 and line.find('APICreateVmInstanceEvent') != -1 and line.find(vm_name_prefix) != -1:
                end_time = time_convert(line)
    elif operation == 'destroy':
        for (num, line) in enumerate(file_obj):
            if line.find('event received') != -1 and line.find('APICreateVmInstanceEvent') != -1 and line.find(vm_name_prefix) != -1:
		start_line = num
                continue
            if line.find('event received') != -1 and line.find('APIDestroyVmInstanceEvent') != -1:
		if num > start_line and start_line != 0:
                    end_time = time_convert(line)
    elif operation == 'expunge':
        for (num, line) in enumerate(file_obj):
            if line.find('event received') != -1 and line.find('APICreateVmInstanceEvent') != -1 and line.find(vm_name_prefix) != -1:
		start_line = num
                continue
            if line.find('event received') != -1 and line.find('APIExpungeVmInstanceEvent') != -1:
		if num > start_line and start_line != 0:
                    end_time = time_convert(line)
    else:
        test_util.test_logger('Unknown option %s' % operation)


    file_obj.close()
    log_str = ''
    return end_time

def lib_set_provision_cpu_rate(rate):
    return con_ops.change_global_config('host', 'cpu.overProvisioning.ratio', rate)

def Create(vm_name_prefix):
    global session_uuid
    global session_to
    global session_mc

    session_uuid = None
    session_to = None
    session_mc = None

    vm_num = os.environ.get('ZSTACK_TEST_NUM')
    if not vm_num:
       vm_num = 1000
    else:
       vm_num = int(vm_num)

    test_util.test_logger('ZSTACK_THREAD_THRESHOLD is %d' % thread_threshold)
    test_util.test_logger('ZSTACK_TEST_NUM is %d' % vm_num)

    vm_creation_option = test_util.VmOption()
    image_name = os.environ.get('imageName_s')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid

    cond = res_ops.gen_query_conditions('category', '=', 'Private')
    l3net_uuid = res_ops.query_resource(res_ops.L3_NETWORK, cond, session_uuid)[0].uuid
    l3s = test_lib.lib_get_l3s()
    conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
    instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    #change account session timeout. 
    session_to = con_ops.change_global_config('identity', 'session.timeout', '720000', session_uuid)
    session_mc = con_ops.change_global_config('identity', 'session.maxConcurrent', '10000', session_uuid)

    session_uuid = acc_ops.login_as_admin()

    vm_creation_option.set_session_uuid(session_uuid)

    vm = test_vm_header.ZstackTestVm()
    vm_creation_option.set_l3_uuids([l3net_uuid])
          
    while vm_num > 0:
        check_thread_exception()
        vm_name = '%s_%s' % (vm_name_prefix, str(vm_num))
        vm_creation_option.set_name(vm_name)
        vm.set_creation_option(vm_creation_option)
        vm_num -= 1
        thread = threading.Thread(target=create_vm, args=(vm,))
        while threading.active_count() > thread_threshold:
            time.sleep(1)
        thread.start()

    while threading.active_count() > 1:
        time.sleep(0.05)

    cond = res_ops.gen_query_conditions('name', '=', vm_name)
    vms = res_ops.query_resource_count(res_ops.VM_INSTANCE, cond, session_uuid)
    con_ops.change_global_config('identity', 'session.timeout', session_to, session_uuid)
    con_ops.change_global_config('identity', 'session.maxConcurrent', session_mc, session_uuid)
    acc_ops.logout(session_uuid)

def test():

    total_create_vms_time = 0
    total_destroy_vms_time = 0
    total_expunge_vms_time = 0

    create_vms_time = []
    destroy_vms_time = []
    expunge_vms_time = []

    test_lib.lib_set_provision_memory_rate(20)
    test_lib.lib_set_provision_storage_rate(20)
    lib_set_provision_cpu_rate(20)

    for i in range(0, perf_loop):
        test_util.test_dsc("start the %d interation" % i)
        vm_name_prefix = 'multi_vms_%s' % str(get_random_name(4))
        Create(vm_name_prefix)
        time.sleep(time_interval)

        create_vm_begin_time = get_begin_time(vm_name_prefix, 'create')
        create_vm_end_time = get_end_time(vm_name_prefix, 'create')
        print ("vm creation begin time = %s") % create_vm_begin_time
        print ("vm creation end time = %s") % create_vm_end_time

        if create_vm_end_time != 0 and create_vm_begin_time != 0:
            create_vms_time.append(create_vm_end_time - create_vm_begin_time)
        test_util.test_dsc("create_vm_time is "+str(create_vms_time[i]))

        Destroy_VM()
        time.sleep(180)

        destroy_vm_begin_time = get_begin_time(vm_name_prefix, 'destroy')
        destroy_vm_end_time = get_end_time(vm_name_prefix, 'destroy')
        print ("vm destroy begin time = %s") % destroy_vm_begin_time
        print ("vm destroy end time = %s") % destroy_vm_end_time

        if destroy_vm_end_time != 0 and destroy_vm_begin_time != 0:
            destroy_vms_time.append(destroy_vm_end_time - destroy_vm_begin_time)
        test_util.test_dsc("destroy_vm_time is "+str(destroy_vms_time[i]))

        Expunge_VM()
        time.sleep(180)
        
        expunge_vm_begin_time = get_begin_time(vm_name_prefix, 'expunge')
        expunge_vm_end_time = get_end_time(vm_name_prefix, 'expunge')
        print ("vm expunge begin time = %s") % expunge_vm_begin_time
        print ("vm expunge end time = %s") % expunge_vm_end_time

        if expunge_vm_end_time != 0 and expunge_vm_begin_time != 0:
            expunge_vms_time.append(expunge_vm_end_time - expunge_vm_begin_time)
        test_util.test_dsc("expunge_vm_time is "+str(expunge_vms_time[i]))

    print ("totally %d iterations executed") % perf_loop
    print "\t\tCre\tDes\tExp"
    for i in range(0, perf_loop):
        print "Iteration%d\t%d\t%d\t%d" % (i, create_vms_time[i], destroy_vms_time[i], expunge_vms_time[i])
        total_create_vms_time = total_create_vms_time + create_vms_time[i]
        total_destroy_vms_time = total_destroy_vms_time + destroy_vms_time[i]
        total_expunge_vms_time = total_expunge_vms_time + expunge_vms_time[i]
    print "Average\t\t%d\t%d\t%d" % (int(total_create_vms_time/perf_loop), int(total_destroy_vms_time/perf_loop), int(total_expunge_vms_time/perf_loop))

    #zone_name = os.environ.get('zoneName')
    #zone = res_ops.get_resource(res_ops.ZONE, name = zone_name)[0]
    #zone_ops.delete_zone(zone.uuid)
    #test_util.test_pass('Create %d vms success,takes %s ms' % (num, create_vms_time))

def error_cleanup():
    if session_to:
        con_ops.change_global_config('identity', 'session.timeout', session_to, session_uuid)
    if session_mc:
        con_ops.change_global_config('identity', 'session.maxConcurrent', session_mc, session_uuid)
    if session_uuid:
        acc_ops.logout(session_uuid)

