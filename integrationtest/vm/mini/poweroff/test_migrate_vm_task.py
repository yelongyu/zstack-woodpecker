'''

New Integration test for testing vm migration with GetHostTask between hosts.

@author: Jiajun
'''

import os
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.host_operations as host_ops
import threading
import time

vm = None
test_stub = test_lib.lib_get_test_stub()

def test():
    global vm
    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = os.getenv('zstackHaVip')
    vm = test_lib.lib_create_vm()
    vm.check()

    for i in range(1, 20):
        thread = threading.Thread(target=test_stub.migrate_vm_to_random_host, args=(vm,))
        thread.start()

        hosts = test_lib.lib_find_hosts_by_status("Connected")
        for host in hosts:
            tasks = host_ops.get_host_task(host.uuid.split(' '))
            for k,v in tasks.items():
                if v['runningTask']:
                    for rtask in v['runningTask']:
                        if 'apiName' in rtask:
                            if rtask['apiName'] == 'org.zstack.header.vm.APIMigrateVmMsg':
                                test_util.test_pass('%s is found running on host %s with Ip %s' % (rtask['apiName'], host.uuid, host.managementIp))
                            else:
                                test_util.test_logger('task %s found running on host %s with Ip %s, but it is not APIMigrateVmMsg' % (rtask['apiName'], host.uuid, host.managementIp))

        test_util.test_logger('No task found at Iteration %s' % str(i))
        time.sleep(5)
        vm.update()

    vm.check()

    vm.destroy()
    vm.expunge()
    test_util.test_fail('No task found after 20 iterations for APIMigrateVmMsg')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    if vm:
        try:
            vm.destroy()
    	    vm.expunge()
        except:
            pass
