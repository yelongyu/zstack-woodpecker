'''

New Integration test for testing host reconnect for mini with GetHostTask

@author: Jiajun
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.header.host as host_header
import time
import os
import random
import threading


vm = None
test_stub = test_lib.lib_get_test_stub()


def test():
    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = os.getenv('zstackHaVip')
    iter_ = len(test_lib.lib_find_hosts_by_status("Connected"))

    for i in range(0, iter_):
        hosts = test_lib.lib_find_hosts_by_status("Connected")
        host = random.choice(hosts)
        thread = threading.Thread(target=host_ops.reconnect_host, args=(host.uuid,))
        thread.start()

        #hosts = test_lib.lib_find_hosts_by_status("Connected")
        for host in hosts:
            tasks = host_ops.get_host_task(host.uuid.split(' '))
            for k,v in tasks.items():
                if v['runningTask']:
                    for rtask in v['runningTask']:
                        if 'apiName' in rtask:
                            if rtask['apiName'] == 'org.zstack.header.host.APIReconnectHostMsg':
                                test_util.test_fail('It is expected that APIReconnectHostMsg is not queried by GetHostTask but %s is found running on host %s with Ip %s' % (rtask['apiName'], host.uuid, host.managementIp))
                            else:
                                test_util.test_logger('task %s found running on host %s with Ip %s, but it is not APIReconnectHostMsg' % (rtask['apiName'], host.uuid, host.managementIp))

        test_util.test_logger('No task found at Iteration %s' % str(i))
        time.sleep(5)
  
    test_util.test_pass('APIReconnectHostMsg is passed as it is expected not queried by GetHostTask')

#Will be called only if exception happens in test().
def error_cleanup():
    pass
