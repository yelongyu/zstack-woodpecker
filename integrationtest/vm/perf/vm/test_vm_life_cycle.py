'''
For KVM VM life  cycle.
The created number will depend on the environment variable: ZSTACK_TEST_NUM
This case's max thread is 1000 

@author: wjy
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.config_operations as con_ops
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.operations.scheduler_operations as schd_ops
import zstackwoodpecker.operations.ha_operations as ha_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import time
import os
import sys
import threading
import random
from test_stub import *

global start_date
global vm_stat_flag
global snapshot_date
global reboot_date


session_uuid = None
session_to = None
session_mc = None
thread_threshold = os.environ.get('ZSTACK_THREAD_THRESHOLD')
if not thread_threshold:
    thread_threshold = 1000
else:
    thread_threshold = int(thread_threshold)

exc_info = []

def check_thread_exception():
    if exc_info:
        info1 = exc_info[0][1]
        info2 = exc_info[0][2]
        raise info1, None, info2

class Start_VM_Parall(VM_Operation_Parall):

    def operate_vm_parall(self, vm_uuid):
        try:
            vm_ops.start_vm(vm_uuid, self.session_uuid)
        except:
            self.exc_info.append(sys.exc_info())

    def check_operation_result(self):
        for i in range(0, self.i):
            v1 = test_lib.lib_get_vm_by_uuid(self.vms[i].uuid)
            if v1.state != "Running":
                test_util.test_fail('Fail to start VM %s.' % v1.uuid)

class Reboot_VM_Parall(VM_Operation_Parall):

    def operate_vm_parall(self, vm_uuid):
        try:
            vm_ops.reboot_vm(vm_uuid, self.session_uuid)
            v1 = test_lib.lib_get_vm_by_uuid(vm_uuid)
            if v1.state == "Rebooting":
                test_util.test_fail('Fail to reboot VM %s.' % v1.uuid)

        except:
            self.exc_info.append(sys.exc_info())

class HA_Neverstop_VM_Parall(VM_Operation_Parall):

    def operate_vm_parall(self, vm_uuid):
        try:
            ha_ops.set_vm_instance_ha_level(vm_uuid, "NeverStop")
        except:
            self.exc_info.append(sys.exc_info())
 
    def check_operation_result(self):
        for i in range(0, self.i):
            vi = test_lib.lib_get_vm_by_uuid(self.vms[i].uuid)
            if v1.state == "Stopped":
                test_util.test_fail('Fail to start VM %s.' % v1.uuid)

class Stop_VM_Simple_Scheduler_Parall(VM_Operation_Parall):

    def operate_vm_parall(self, vm_uuid):
        start_date = int(time.time())
        try:
            vm_ops.stop_vm_scheduler(vm_uuid, 'simple', 'simple_stop_vm_scheduler', 0, 1, 1)
        except:
            self.exc_info.append(sys.exc_info())

    def check_operation_result(self):
        for x in range(30):
            start_msg_mismatch=1
            time.sleep(10)
            for i in range(0, self.i):
                vm_stat_flag=0
                v1 = test_lib.lib_get_vm_by_uuid(self.vms[i].uuid)
                if v1.state != "Stopped":
                    start_msg_mismatch += 1
                    vm_stat_flag=1
            if vm_stat_flag == 0:
                break
            if start_msg_mismatch > 30: 
                test_util.test_fail('StopVmInstance scheduler doesn\'t work as expected')

class Cancel_HA_VM_Parall(VM_Operation_Parall):

    def operate_vm_parall(self, vm_uuid):
        try:
            ha_ops.del_vm_instance_ha_level(vm_uuid)
        except:
            self.exc_info.append(sys.exc_info())

class Start_VM_Simple_Scheduler_Parall(VM_Operation_Parall):

    date=int(time.time())

    def operate_vm_parall(self, vm_uuid):
        try:
            vm_ops.start_vm_scheduler(vm_uuid, 'simple', 'simple_start_vm_scheduler', 0, 1, 1)        
	except:
            self.exc_info.append(sys.exc_info())

    def check_operation_result(self):
        for x in range(30): 
            start_msg_mismatch=1
            time.sleep(10)
            for i in range(0, self.i):
                vm_stat_flag=0
                v1 = test_lib.lib_get_vm_by_uuid(self.vms[i].uuid)
                if v1.state != "Running":
                    start_msg_mismatch += 1
                    vm_stat_flag=1
            if vm_stat_flag == 0:
                break
            if start_msg_mismatch > 30:
                test_util.test_fail('StartVmInstance scheduler doesn\'t work as expected')

class Snapshot_VM_Simple_Scheduler_Parall(VM_Operation_Parall):

    date=int(time.time())

    def operate_vm_parall(self, vm_uuid):
        try:
            #test_lib.lib_get_root_volume_uuid(rebootvms.vms[0])
            vm=test_lib.lib_get_vm_by_uuid(vm_uuid)
            root_volume_uuid=test_lib.lib_get_root_volume_uuid(vm)
            sp_option = test_util.SnapshotOption()
            sp_option.set_name('simple_schduler_snapshot')
            sp_option.set_volume_uuid(root_volume_uuid)
            schd = vol_ops.create_snapshot_scheduler(sp_option, 'simple', 'simple_create_snapshot_scheduler',  0, 1, 1)
        except:
            self.exc_info.append(sys.exc_info())

    def query_snapshot_number(snapshot_name):
        cond = res_ops.gen_query_conditions('name', '=', snapshot_name)
        return res_ops.query_resource_count(res_ops.VOLUME_SNAPSHOT, cond)

    def check_operation_result(self):
        time.sleep(30)
        start_msg_mismatch = 1 
        for k in range(0, 1000):
            for i in range(0, self.i):
                vm_stat_flag=0
                vm=test_lib.lib_get_vm_by_uuid(self.vms[i].uuid)
                root_volume_uuid=test_lib.lib_get_root_volume_uuid(vm)
                if not test_lib.lib_find_in_local_management_server_log(self.date+k, '[msg send]: {"org.zstack.header.volume.CreateVolumeSnapshotMsg', self.vms[i].uuid):
                    test_util.test_warn('CreateVolumeSnapshotMsg is expected to execute at %s' % (self.date+k))
                    vm_stat_flag=1
                start_msg_mismatch += 1
            if vm_stat_flag == 0:
                break
        if start_msg_mismatch > 1000:
            test_util.test_fail('%s of 1000 CreateVolumeSnapshotMsg not executed at expected timestamp' % (start_msg_mismatch))

class Reboot_VM_Simple_Scheduler_Parall(VM_Operation_Parall):

    date=int(time.time())
    def operate_vm_parall(self, vm_uuid):
        try:
            vm_ops.reboot_vm_scheduler(vm_uuid, 'simple', 'simple_reboot_vm_scheduler', 0, 1, 1)        
	except:
            self.exc_info.append(sys.exc_info())

    def check_operation_result(self):
        time.sleep(30)
        start_msg_mismatch = 1
        for k in range(0, 100):
            for i in range(0, self.i):
                vm_stat_flag=0
                if not test_lib.lib_find_in_local_management_server_log(self.date+k, '[msg send]: {"org.zstack.header.vm.RebootVmInstanceMsg', self.vms[i].uuid):                     
		    test_util.test_warn('RebootVmInstanceMsg is expected to execute at %s' % (self.date+k))                                 
		    vm_stat_flag=1
                start_msg_mismatch += 1
            if vm_stat_flag == 0:
                break
        if start_msg_mismatch > 1000:
            test_util.test_fail('%s of 1000 RebootVmInstanceMsg not executed at expected timestamp' % (start_msg_mismatch))

class Force_Stop_VM_Parall(VM_Operation_Parall):

    def operate_vm_parall(self, vm_uuid):
        try:
            vm_ops.stop_vm(vm_uuid, force='cold')
        except:
            self.exc_info.append(sys.exc_info())

    def check_operation_result(self):
        for i in range(0, self.i):
            v1 = test_lib.lib_get_vm_by_uuid(self.vms[i].uuid)
            if v1.state != "Stopped":
                test_util.test_fail('Fail to force stop VM %s.' % v1.uuid)

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

class Recover_VM_Parall(VM_Operation_Parall):
    def operate_vm_parall(self, vm_uuid):
        try:
            vm_ops.recover_vm(vm_uuid, self.session_uuid)
        except:
            self.exc_info.append(sys.exc_info())

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

def Create():
    global session_uuid
    global session_to
    global session_mc
    vm_num = os.environ.get('ZSTACK_TEST_NUM')
    if not vm_num:
       vm_num = 1000
    else:
       vm_num = int(vm_num)

    test_util.test_logger('ZSTACK_THREAD_THRESHOLD is %d' % thread_threshold)
    test_util.test_logger('ZSTACK_TEST_NUM is %d' % vm_num)

    org_num = vm_num
    vm_creation_option = test_util.VmOption()
    image_name = os.environ.get('imageName_s')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    l3_name = os.environ.get('l3PublicNetworkName')

    l3 = test_lib.lib_get_l3_by_name(l3_name)
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
    vm_creation_option.set_l3_uuids([l3.uuid])

    while vm_num > 0:
        check_thread_exception()
        vm_name = 'multihost_basic_vm_%s' % str(vm_num)
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
   # if vms == org_num:
    #    print 'Create %d VMs Test Success.' % (org_num)
   # else:
    #    test_util.test_fail('Create %d VMs Test Failed. Only find %d VMs.' % (org_num, vms))

def Stop_VM():
    get_vm_con = res_ops.gen_query_conditions('state', '=', "Running")
    wait_vm_condition(get_vm_con)
    stopvms = VM_Operation_Parall(get_vm_con, "Running")
    stopvms.parall_test_run()
    stopvms.check_operation_result()

def Start_VM():
    get_vm_con = res_ops.gen_query_conditions('state', '=', "Stopped")
    wait_vm_condition(get_vm_con)
    startvms = Start_VM_Parall(get_vm_con, "Running")
    startvms.parall_test_run()
    startvms.check_operation_result()

def Reboot_VM():
    get_vm_con = res_ops.gen_query_conditions('state', '=', "Running")
    wait_vm_condition(get_vm_con)
    rebootvms = Reboot_VM_Parall(get_vm_con, "Running")
    rebootvms.parall_test_run()

def Ha_NeverStop_VM():
    get_vm_con = res_ops.gen_query_conditions('state', '=', 'Running')
    wait_vm_condition(get_vm_con)
    neverstop_vms = HA_Neverstop_VM_Parall(get_vm_con, "Running")
    neverstop_vms.parall_test_run()
    neverstop_vms.check_operation_result()

def Stop_VM_Simple_Scheduler():
    get_vm_con = res_ops.gen_query_conditions('state', '=', "Running")
    wait_vm_condition(get_vm_con)
    startvms = Stop_VM_Simple_Scheduler_Parall(get_vm_con, "Running")
    startvms.parall_test_run()
    startvms.check_operation_result()

def Cancel_Ha_VM():
    get_vm_con = res_ops.gen_query_conditions('state', '!=', "Destroyed")
    wait_vm_condition(get_vm_con)
    cancel_ha_vms = Cancel_HA_VM_Parall(get_vm_con, "Running")
    cancel_ha_vms.parall_test_run()

def Start_VM_Simple_Scheduler():
    get_vm_con = res_ops.gen_query_conditions('state', '=', "Stopped")
    wait_vm_condition(get_vm_con)
    startvms = Start_VM_Simple_Scheduler_Parall(get_vm_con, "Stopped")
    start_date=int(time.time())
    startvms.parall_test_run()
    startvms.check_operation_result()

def Snapshot_VM_Simple_Scheduler():
    get_vm_con = res_ops.gen_query_conditions('type', '=', "UserVm")
    wait_vm_condition(get_vm_con)
    snapshotvms = Snapshot_VM_Simple_Scheduler_Parall(get_vm_con, "UserVm")
    snapshotvms.parall_test_run()
    snapshotvms.check_operation_result()

def Reboot_VM_Simple_Scheduler():
    get_vm_con = res_ops.gen_query_conditions('state', '=', "Running")
    wait_vm_condition(get_vm_con)
    rebootvms = Reboot_VM_Simple_Scheduler_Parall(get_vm_con, "Running")
    rebootvms.parall_test_run()
    rebootvms.check_operation_result()

def Force_Stop_VM():
    get_vm_con = res_ops.gen_query_conditions('state', '=', "Running")
    wait_vm_condition(get_vm_con)
    stopvms = Force_Stop_VM_Parall(get_vm_con, "Running")
    stopvms.parall_test_run()
    stopvms.check_operation_result()

def Destroy_VM():
    get_vm_con = res_ops.gen_query_conditions('state', '!=', "Destroyed")
    wait_vm_condition(get_vm_con)
    destroyvms = Destroy_VM_Parall(get_vm_con, "Running")
    destroyvms.parall_test_run()
    destroyvms.check_operation_result()

def Recover_VM():
    get_vm_con = res_ops.gen_query_conditions('state', '=', "Destroyed")
    wait_vm_condition(get_vm_con)
    recovervms = Recover_VM_Parall(get_vm_con, "Destroyed")
    recovervms.parall_test_run()
    recovervms.check_operation_result()

def Expunge_VM():
    get_vm_con = res_ops.gen_query_conditions('state', '=', "Destroyed")
    wait_vm_condition(get_vm_con)
    expungevms = Expunge_VM_Parall(get_vm_con, "Running")
    expungevms.parall_test_run()
    expungevms.check_operation_result()

def lib_set_provision_cpu_rate(rate):
    return con_ops.change_global_config('host', 'cpu.overProvisioning.ratio', rate)


def test():
    os.environ['ZSTACK_THREAD_THRESHOLD']='1000'
    os.environ['ZSTACK_TEST_NUM']='1000'
    test_lib.lib_set_provision_memory_rate(20)
    test_lib.lib_set_provision_storage_rate(20)
    lib_set_provision_cpu_rate(20)
    while True:
	Create()
        time.sleep(180)
        Stop_VM()
        time.sleep(180)
        Start_VM()
        time.sleep(180)
        Reboot_VM()
        time.sleep(360)
        Ha_NeverStop_VM()
        time.sleep(30)
        Stop_VM_Simple_Scheduler()
        time.sleep(180)
        Cancel_Ha_VM()
        time.sleep(30)
        Stop_VM_Simple_Scheduler()
        time.sleep(180)
        Start_VM_Simple_Scheduler()    
        time.sleep(180)
        Reboot_VM_Simple_Scheduler()
        time.sleep(180)
        Snapshot_VM_Simple_Scheduler()
        time.sleep(30)
        Force_Stop_VM()
        time.sleep(180)
        Destroy_VM()
        time.sleep(180)
        Recover_VM()
        time.sleep(180)
        Start_VM()
        time.sleep(180)
        Destroy_VM()
        time.sleep(180)
        Expunge_VM()
        time.sleep(180)
    while True:
        time.sleep(3600)
    
#Will be called only if exception happens in test().
def error_cleanup():
    if session_to:
        con_ops.change_global_config('identity', 'session.timeout', session_to, session_uuid)
    if session_mc:
        con_ops.change_global_config('identity', 'session.maxConcurrent', session_mc, session_uuid)
    if session_uuid:
        acc_ops.logout(session_uuid)

