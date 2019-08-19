'''

New Integration test for ISO image creation for GetHostTask.

@author: Jiajun
'''

import os
import time
import random
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.host_operations as host_ops
import threading

test_stub = test_lib.lib_get_test_stub()
img_repl = test_stub.ImageReplication()

def test():
    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = os.getenv('zstackHaVip')
    bs_list = img_repl.get_bs_list()
    bs = random.choice(bs_list)


    test_util.test_logger('Start to check host task for APIAddImageMsg with at most 10 iterations')
    for i in range(1, 10):
        image_name = 'iso-image-hosttask-test-' + time.strftime('%y%m%d%H%M%S', time.localtime())
        thread = threading.Thread(target=img_repl.add_image, args=(image_name, bs.uuid, 'http://172.20.1.22/mirror/iso/iso_for_install_vm_test.iso' ,'iso'))
        #thread = threading.Thread(target=img_repl.add_image, args=(image_name, bs.uuid, 'http://172.20.1.22/mirror/diskimages/win10.qcow2' ))
        thread.start()
        #img_repl.add_image(image_name, bs_uuid=bs.uuid, img_format='iso')

        hosts = test_lib.lib_find_hosts_by_status("Connected")
        for host in hosts:
            tasks = host_ops.get_host_task(host.uuid.split(' '))
            for k,v in tasks.items():
                if v['runningTask']:
                    for rtask in v['runningTask']:
                        if 'apiName' in rtask:
                            if rtask['apiName'] == 'org.zstack.header.image.APIAddImageMsg':
                                test_util.test_fail('It is expected that APIAddImageMsg is not queried by GetHostTask but %s is found running on host %s with Ip %s' % (rtask['apiName'], host.uuid, host.managementIp))
                            else:
                                test_util.test_logger('task %s found running on host %s with Ip %s, but it is not APIAddImageMsg' % (rtask['apiName'], host.uuid, host.managementIp))

        test_util.test_logger('No task found at Iteration %s' % str(i))
        time.sleep(2)

    test_util.test_pass('APIAddImageMsg is passed as it is expected not queried by GetHostTask')
    img_repl.clean_on_expunge()

def env_recover():
    img_repl.delete_image()
    img_repl.expunge_image()
    img_repl.reclaim_space_from_bs()
    try:
        img_repl.vm.destroy()
    except:
        pass


#Will be called only if exception happens in test().
def error_cleanup():
    try:
        img_repl.delete_image()
        img_repl.expunge_image()
        img_repl.reclaim_space_from_bs()
        img_repl.vm.destroy()
    except:
        pass
