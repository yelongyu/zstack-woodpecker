'''

New Perf Test for creating data volume and do attach/detach operations.
The created number will depends on the environment variable: ZSTACK_TEST_NUM

The default max threads are 1000. It could be modified by env variable: 
ZSTACK_THREAD_THRESHOLD

@author: Youyk
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.config_operations as con_ops
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.zstack_test.zstack_test_volume as test_vol_header
import time
import os
import sys
import threading
import random

_config_ = {
    'timeout' : 10000,
    'noparallel' : True 
}

session_uuid = None
session_to = None
session_mc = None
exc_info = []

def create_volume(volume, vm_uuid):
    try:
        #create volume
        volume.create()
        #attach volume to vm
        vol_ops.attach_volume(volume.volume.uuid, vm_uuid, session_uuid)
        #detach volume from vm
        vol_ops.detach_volume(volume.volume.uuid, session_uuid)
    except:
        exc_info.append(sys.exc_info())

def check_thread_exception():
    if exc_info:
        info1 = exc_info[0][1]
        info2 = exc_info[0][2]
        raise info1, None, info2

def test():
    global session_uuid
    global session_to
    global session_mc
    thread_threshold = os.environ.get('ZSTACK_THREAD_THRESHOLD')
    if not thread_threshold:
        thread_threshold = 1000
    else:
        thread_threshold = int(thread_threshold)
    
    volume_num = os.environ.get('ZSTACK_TEST_NUM')
    if not volume_num:
        volume_num = 0
    else:
        volume_num = int(volume_num)

    #change account session timeout. 
    session_to = con_ops.change_global_config('identity', 'session.timeout', '720000', session_uuid)
    session_mc = con_ops.change_global_config('identity', 'session.maxConcurrent', '10000', session_uuid)
    session_uuid = acc_ops.login_as_admin()
    vm_num = res_ops.query_resource_count(res_ops.VM_INSTANCE, [], session_uuid)
    if vm_num < thread_threshold:
        test_util.test_fail('This test needs: %d VM instances for volume attaching and detaching operations. But there are only %d VMs instances. Please use this case: test_crt_basic_vm_with_max_threads.py to create required VMs.' % (thread_threshold, volume_num))

    vms = res_ops.query_resource_with_num(res_ops.VM_INSTANCE, [], \
            session_uuid, start = 0, limit = thread_threshold)

    test_util.test_logger('ZSTACK_THREAD_THRESHOLD is %d' % thread_threshold)
    test_util.test_logger('ZSTACK_TEST_NUM is %d' % volume_num)

    org_num = volume_num
    disk_offering_name = os.environ.get('smallDiskOfferingName')
    disk_offering_uuid = test_lib.lib_get_disk_offering_by_name(disk_offering_name).uuid
    volume_option = test_util.VolumeOption()
    volume_option.set_disk_offering_uuid(disk_offering_uuid)
    volume_option.set_session_uuid(session_uuid)

    random_name = random.random()
    volume_name = 'perf_volume_%s' % str(random_name)
    volume_option.set_name(volume_name)
    vm_num = 0
    while volume_num > 0:
        check_thread_exception()
        volume = test_vol_header.ZstackTestVolume()
        volume.set_creation_option(volume_option)
        volume_num -= 1
        if vm_num > (thread_threshold - 1):
            vm_num = 0
        thread = threading.Thread(target=create_volume, args = (volume, vms[vm_num].uuid, ))
        vm_num += 1
        while threading.active_count() > thread_threshold:
            time.sleep(0.)
        thread.start()

    while threading.active_count() > 1:
        time.sleep(0.01)

    cond = res_ops.gen_query_conditions('name', '=', volume_name)
    volumes_num = res_ops.query_resource_count(res_ops.VOLUME, cond, session_uuid)
    con_ops.change_global_config('identity', 'session.timeout', session_to, session_uuid)
    con_ops.change_global_config('identity', 'session.maxConcurrent', session_mc, session_uuid)
    acc_ops.logout(session_uuid)
    if volumes_num == org_num:
        test_util.test_pass('Create %d Volumes Test Success' % org_num)
    else:
        test_util.test_fail('Create %d Volumes Test Failed. Only find %d Volumes.' % (org_num, volumes_num))

#Will be called only if exception happens in test().
def error_cleanup():
    if session_to:
        con_ops.change_global_config('identity', 'session.timeout', session_to, session_uuid)
    if session_mc:
        con_ops.change_global_config('identity', 'session.maxConcurrent', session_mc, session_uuid)
    if session_uuid:
        acc_ops.logout(session_uuid)
