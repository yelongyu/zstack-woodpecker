'''
Create an unified test_stub to share test operations
@author: Youyk
@author: Liu Lei
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.config_operations as con_ops
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import time
import os
import sys
import threading
import random

class VM_Operation_Parall:
    def __init__(self, get_vm_con, justify_con = None):
        self.exc_info = []
        self.vms = []
        self.i = 0
        self.session_uuid = None
        self.session_to = None
        self.session_mc = None
        self.vm_num = os.environ.get('ZSTACK_TEST_NUM')
        self.thread_threshold = os.environ.get('ZSTACK_THREAD_THRESHOLD')
        self.get_vm_con = get_vm_con
        self.justify_con = justify_con
        if not self.vm_num:
            self.vm_num = 0
        else:
            self.vm_num = int(self.vm_num)

        if not self.thread_threshold:
            self.thread_threshold = 1000
        else:
            self.thread_threshold = int(self.thread_threshold)

        self.vms = res_ops.query_resource(res_ops.VM_INSTANCE, self.get_vm_con)
        if self.vm_num > len(self.vms):
            self.vm_num = len(self.vms)
            test_util.test_warn('ZSTACK_TEST_NUM is forcibly set as %d\n' % len(self.vms))

        self.session_to = con_ops.change_global_config('identity', 'session.timeout',\
                                                  '720000', self.session_uuid)

        self.session_mc = con_ops.change_global_config('identity', 'session.maxConcurrent',\
                                                  '10000', self.session_uuid)
        self.session_uuid = acc_ops.login_as_admin()

    def check_thread_exception(self):
        if self.exc_info:
            info1 = self.exc_info[0][1]
            info2 = self.exc_info[0][2]
            raise info1, None, info2

    def operate_vm_parall(self, vm_uuid):
        try:
            #should be defined by case
            vm_ops.stop_vm(vm_uuid, None, self.session_uuid)
        except:
            self.exc_info.append(sys.exc_info())

    def check_operation_result(self):
        #should be defined by case
        for i in range(0, self.i):
            v1 = test_lib.lib_get_vm_by_uuid(self.vms[i].uuid)
            if v1.state == self.justify_con:
                test_util.test_fail('Fail to operate VM %s.' % v1.uuid)

    def parall_test_run(self):
        test_util.test_logger('ZSTACK_THREAD_THRESHOLD is %d' % self.thread_threshold)
        test_util.test_logger('ZSTACK_TEST_NUM is %d' % self.vm_num)

        while self.vm_num > 0:
            self.check_thread_exception()
            self.vm_num -= 1
            thread = threading.Thread(target=self.operate_vm_parall, args=(self.vms[self.i].uuid,))
            self.i += 1
            while threading.active_count() > self.thread_threshold:
                time.sleep(1)
            thread.start()

        while threading.active_count() > 1:
            time.sleep(0.01)

        con_ops.change_global_config('identity', 'session.timeout', self.session_to, self.session_uuid)
        con_ops.change_global_config('identity', 'session.maxConcurrent', self.session_mc, self.session_uuid)
        acc_ops.logout(self.session_uuid)

    #Will be called only if exception happens in test().
    def error_cleanup():
        if self.session_to:
            con_ops.change_global_config('identity', 'session.timeout', self.session_to, self.session_uuid)
        if self.session_mc:
            con_ops.change_global_config('identity', 'session.maxConcurrent', self.session_mc, self.session_uuid)
        if self.session_uuid:
            acc_ops.logout(self.session_uuid)

