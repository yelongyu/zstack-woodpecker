'''

New Perf Test for creating KHost Host with basic L3 network.
The created number will depend on the environment variable: ZSTACK_TEST_NUM

The difference with test_basic_l3_host_with_given_num.py is this case's max thread is 1000 

@author: Youyk
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.host_operations as host_ops
import os
import time 
from test_stub import *

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

class Delete_Host_Parall(Host_Operation_Parall):
    def operate_host_parall(self, host_uuid):
        try:
            host_ops.delete_host(host_uuid,self.session_uuid)
        except:
            self.exc_info.append(sys.exc_info())

    def check_operation_result(self):
        for i in range(0, self.i):
            v1 = test_lib.lib_get_host_by_uuid(self.hosts[i].uuid)
            if v1:
                test_util.test_fail('Fail to Delete Host %s.' % v1.uuid)

def test():
    get_host_con = res_ops.gen_query_conditions('hypervisorType', '=', "KVM")
    delete_hosts = Delete_Host_Parall(get_host_con, "KVM")
    delete_hosts.parall_test_run()
    delete_hosts.check_operation_result()

#Will be called only if exception happens in test().
def error_cleanup():
    if session_to:
        con_ops.change_global_config('identity', 'session.timeout', session_to, session_uuid)
    if session_mc:
        con_ops.change_global_config('identity', 'session.maxConcurrent', session_mc, session_uuid)
    if session_uuid:
        acc_ops.logout(session_uuid)
