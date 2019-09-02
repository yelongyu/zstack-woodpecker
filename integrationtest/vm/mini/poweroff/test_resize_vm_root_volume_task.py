'''

New Integration Test for resizing root volume with GetHostTask

@author: Jiajun
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import zstackwoodpecker.operations.host_operations as host_ops
import time
import os
import random
import threading

vm = None

def test():
    global vm
    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = os.getenv('zstackHaVip')
    create_vm_option = test_util.VmOption()
    create_vm_option.set_name('test_resize_vm_root_volume')
    vm = test_lib.lib_create_vm(create_vm_option)
    vm.check()

    for i in range(1, 10):
        vol_size = test_lib.lib_get_root_volume(vm.get_vm()).size
        volume_uuid = test_lib.lib_get_root_volume(vm.get_vm()).uuid
        set_size = vol_size + 1024*1024*1024*10
        thread = threading.Thread(target=vol_ops.resize_volume, args=(volume_uuid, set_size))
        thread.start()

        hosts = test_lib.lib_find_hosts_by_status("Connected")
        for host in hosts:
            tasks = host_ops.get_host_task(host.uuid.split(' '))
            for k,v in tasks.items():
                if v['runningTask']:
                    for rtask in v['runningTask']:
                        if 'apiName' in rtask:
                            if rtask['apiName'] == 'org.zstack.header.volume.APIResizeRootVolumeMsg':
                                test_util.test_pass('%s is found running on host %s with Ip %s' % (rtask['apiName'], host.uuid, host.managementIp))
                            else:
                                test_util.test_logger('task %s found running on host %s with Ip %s, but it is not APIResizeRootVolumeMsg' % (rtask['apiName'], host.uuid, host.managementIp))

        test_util.test_logger('No task found at Iteration %s' % str(i))
        time.sleep(5)
        vm.update()

    vm.check()

    vm.destroy()
    vm.expunge()
    test_util.test_fail('No task found after 10 iterations for APIResizeRootVolume')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    if vm:
        try:
            vm.destroy()
            vm.expunge()
        except:
            pass
