'''

New Perf Test for creating sim VM with basic L3 network and extra data volume
The created number will depends on the environment variable: ZSTACK_TEST_NUM

The difference with test_basic_l3_vm_with_given_num.py is this case's max thread
is 1000, which could be modified by env variable: ZSTACK_THREAD_THRESHOLD

@author: Youyk
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
import threading
import random

session_uuid = None
session_to = None
session_mc = None
thread_threshold = os.environ.get('ZSTACK_THREAD_THRESHOLD')
if not thread_threshold:
    thread_threshold = 1000
else:
    thread_threshold = int(thread_threshold)

def test():
    global session_uuid
    global session_to
    global session_mc
    vm_num = os.environ.get('ZSTACK_TEST_NUM')
    if not vm_num:
        vm_num = 0
    else:
        vm_num = int(vm_num)

    test_util.test_logger('ZSTACK_THREAD_THRESHOLD is %d' % thread_threshold)
    test_util.test_logger('ZSTACK_TEST_NUM is %d' % vm_num)

    org_num = vm_num
    vm_creation_option = test_util.VmOption()
    image_name = os.environ.get('imageName_s')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    l3_name = os.environ.get('l3PublicNetworkName')

    disk_offering_name = os.environ.get('smallDiskOfferingName')
    disk_offering_uuid = test_lib.lib_get_disk_offering_by_name(disk_offering_name).uuid

    l3s = test_lib.lib_get_l3s()
    conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
    instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_data_disk_uuids([disk_offering_uuid])
    session_uuid = acc_ops.login_as_admin()

    #change account session timeout. 
    session_to = con_ops.change_global_config('identity', 'session.timeout', '720000', session_uuid)
    session_mc = con_ops.change_global_config('identity', 'session.maxConcurrent', '10000', session_uuid)

    vm_creation_option.set_session_uuid(session_uuid)

    vm = test_vm_header.ZstackTestVm()
    random_name = random.random()
    vm_name = 'multihost_basic_vm_%s' % str(random_name)
    vm_creation_option.set_name(vm_name)

    while vm_num > 0:
        vm_creation_option.set_l3_uuids([random.choice(l3s).uuid])
        vm.set_creation_option(vm_creation_option)
        vm_num -= 1
        thread = threading.Thread(target=vm.create)
        while threading.active_count() > thread_threshold:
            time.sleep(1)
        thread.start()

    while threading.active_count() > 1:
        time.sleep(0.01)

    cond = res_ops.gen_query_conditions('name', '=', vm_name)
    vms = res_ops.query_resource_count(res_ops.VM_INSTANCE, cond, session_uuid)
    con_ops.change_global_config('identity', 'session.timeout', session_to, session_uuid)
    con_ops.change_global_config('identity', 'session.maxConcurrent', session_mc, session_uuid)
    acc_ops.logout(session_uuid)
    if vms == org_num:
        test_util.test_pass('Create %d VMs Test Success' % org_num)
    else:
        test_util.test_fail('Create %d VMs Test Failed. Only find %d VMs.' % (org_num, vms))

#Will be called only if exception happens in test().
def error_cleanup():
    if session_to:
        con_ops.change_global_config('identity', 'session.timeout', session_to, session_uuid)
    if session_mc:
        con_ops.change_global_config('identity', 'session.maxConcurrent', session_mc, session_uuid)
    if session_uuid:
        acc_ops.logout(session_uuid)
