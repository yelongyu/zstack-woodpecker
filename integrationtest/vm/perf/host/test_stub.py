'''
Create an unified test_stub to share test operations
@author: Carl
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.config_operations as con_ops
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.operations.host_operations as host_ops
import time
import os
import sys
import threading
import random


class Host_Operation_Parall:
    def __init__(self, get_host_con = None, justify_con = None):
        self.exc_info = []
        self.hosts = []
        self.i = 0
        self.session_uuid = None
        self.session_to = None
        self.session_mc = None
        self.host_num = os.environ.get('ZSTACK_TEST_NUM')
        self.thread_threshold = os.environ.get('ZSTACK_THREAD_THRESHOLD')
        self.get_host_con = get_host_con
        self.justify_con = justify_con
        if not self.host_num:
            self.host_num = 0
        else:
            self.host_num = int(self.host_num)

        if not self.thread_threshold:
            self.thread_threshold = 1000
        else:
            self.thread_threshold = int(self.thread_threshold)

        self.hosts = res_ops.query_resource(res_ops.HOST, self.get_host_con)
        if self.host_num > len(self.hosts):
            self.host_num = len(self.hosts)
            test_util.test_warn('ZSTACK_TEST_NUM is forcibly set as %d\n' % len(self.hosts))

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

    def operate_host_parall(self, host_uuid):
        try:
            #should be defined by case
            host_ops.change_host_state(host_uuid, None, self.session_uuid)
        except:
            self.exc_info.append(sys.exc_info())

    def check_operation_result(self):
        #should be defined by case
        for i in range(0, self.i):
            v1 = test_lib.lib_get_host_by_uuid(self.hosts[i].uuid)
            if v1.state == self.justify_con:
                test_util.test_fail('Fail to operate Host %s.' % v1.uuid)

    def parall_test_run(self):
        test_util.test_logger('ZSTACK_THREAD_THRESHOLD is %d' % self.thread_threshold)
        test_util.test_logger('ZSTACK_TEST_NUM is %d' % self.host_num)
        tmp_host_num = self.host_num

        while tmp_host_num > 0:
            self.check_thread_exception()
            tmp_host_num -= 1
            thread = threading.Thread(target=self.operate_host_parall, args=(self.hosts[self.i].uuid,))
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
