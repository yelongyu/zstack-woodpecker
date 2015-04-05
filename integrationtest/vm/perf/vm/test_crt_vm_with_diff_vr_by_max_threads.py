'''

New Perf Test for creating KVM VM with SG L3 network.
The created number will depends on the environment variable: ZSTACK_TEST_NUM
Each VM will use different VR. The max number is based on simulation environment

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
import sys
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

exc_info = []
def check_thread_exception():
    if exc_info:
        info1 = exc_info[0][1]
        info2 = exc_info[0][2]
        raise info1, None, info2

def create_vm(vm):
    try:
        vm.create()
    except:
        exc_info.append(sys.exc_info())

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
    conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
    instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid
    l3_name = os.environ.get('l3PublicNetworkName')
    conditions = res_ops.gen_query_conditions('name', '!=', l3_name)
    l3s = res_ops.query_resource_fields(res_ops.L3_NETWORK, conditions, \
            session_uuid, ['uuid'], start = 0, limit = org_num)
    session_uuid = acc_ops.login_as_admin()
    #change account session timeout. 
    session_to = con_ops.change_global_config('identity', 'session.timeout', '720000', session_uuid)
    session_mc = con_ops.change_global_config('identity', 'session.maxConcurrent', '10000', session_uuid)

    random_name = random.random()
    vm_name = 'multihost_basic_vm_%s' % str(random_name)
    for vm_n in range(org_num):
        vm_creation_option = test_util.VmOption()
        image_name = os.environ.get('imageName_s')
        image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
        vm_creation_option.set_l3_uuids([l3s[vm_n].uuid])
        vm_creation_option.set_image_uuid(image_uuid)
        vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
        vm_creation_option.set_session_uuid(session_uuid)

        vm = test_vm_header.ZstackTestVm()
        vm_creation_option.set_name(vm_name)

        check_thread_exception()
        vm.set_creation_option(vm_creation_option)
        thread = threading.Thread(target=create_vm, args=(vm,))
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
