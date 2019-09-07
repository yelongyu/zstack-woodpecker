'''

Test VM Live Migration with 1 Host Management network down via Longjob:
1. Live migrate multiple VMs;
2. All VMs have CPU/Memory stress load

@author: Legion
'''

import os
import sys
import time
import random
import traceback
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
from threading import Thread


test_stub = test_lib.lib_get_test_stub('virtualrouter')
longjob = test_stub.Longjob()
num_list = range(5)
vms = []
migration_thread_list = []
host = None
vm_thrd_list = []
migtation_failed_list = []
stress_thread_list = []

class CrtVMThread(Thread):
    def __init__(self, host_uuid):
        super(CrtVMThread, self).__init__()
        self.exitcode = 0
        self.exception = None
        self.exc_traceback = ''
        self.vm = None
        self.host_uuid = host_uuid

    def run(self):
        try:
            self.vm = longjob.create_vm(l3_name=os.environ.get('l3PublicNetworkName'),
                                        host_uuid=self.host_uuid, check=False)
        except Exception as e:
            self.exitcode = 1
            self.exception = e
            self.exc_traceback = ''.join(traceback.format_exception(*sys.exc_info()))

    def join(self):
        super(CrtVMThread, self).join()
        return self.vm

class LongjobThread(Thread):
    def __init__(self, vm, host_uuid):
        super(LongjobThread, self).__init__()
        self.exitcode = 0
        self.exception = None
        self.exc_traceback = ''
        self.vm = vm
        self.host_uuid = host_uuid

    def run(self):
        try:
            longjob.live_migrate_vm(self.vm, self.host_uuid, True)
        except Exception as e:
            self.exitcode = 1
            self.exception = e
            self.exc_traceback = ''.join(traceback.format_exception(*sys.exc_info()))

class StressVMThread(Thread):
    def __init__(self, vm):
        super(StressVMThread, self).__init__()
        self.exitcode = 0
        self.exception = None
        self.exc_traceback = ''
        self.vm = vm

    def run(self):
        try:
            self.vm.check()
            longjob.add_stress(self.vm, networkio=False)
        except Exception as e:
            self.exitcode = 1
            self.exception = e
            self.exc_traceback = ''.join(traceback.format_exception(*sys.exc_info()))



def wait_for_host_status_change(host_ip, status='Disconnected'):
    conditions = res_ops.gen_query_conditions('managementIp', '=', host_ip)
    host_status = res_ops.query_resource(res_ops.HOST, conditions)[0].status
    for _ in xrange(60):
        if host_status == status:
            time.sleep(1)
            return
        else:
            time.sleep(3)


def test():
    global host
    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = os.getenv('zstackHaVip')
    host_uuid = res_ops.query_resource(res_ops.HOST)[0].uuid

    for _ in num_list:
        vm_thrd_list.append(CrtVMThread(host_uuid))
        # vms.append(longjob.create_vm(l3_name=os.environ.get('l3PublicNetworkName'), host_uuid=host_uuid))

    cond_host = res_ops.gen_query_conditions('uuid', '=', host_uuid)
    host = res_ops.query_resource(res_ops.HOST, cond_host)[0]

    conditions = res_ops.gen_query_conditions('clusterUuid', '=', host.clusterUuid)
    cond_other_host = res_ops.gen_query_conditions('uuid', '!=', host.uuid, conditions)

    other_host = res_ops.query_resource(res_ops.HOST, cond_other_host)[0]

    for i in num_list:
        vm_thrd_list[i].start()

    for n in num_list:
        vms.append(vm_thrd_list[n].join())

    for vm in vms:
        stress_thread_list.append(StressVMThread(vm))
        migration_thread_list.append(LongjobThread(vm, other_host.uuid))
    
    for sthrd in stress_thread_list:
        sthrd.start()
    
    for sthrd in stress_thread_list:
        sthrd.join()
        if sthrd.exitcode != 0:
            print('----------------------Exception Reason------------------------')
            print(sthrd.exc_traceback)
            print('-------------------------Reason End---------------------------\n')
            test_util.test_fail('Error happened while stressing vm: [%s]' % sthrd.vm.get_vm().name)

    test_stub_mini = test_lib.lib_get_test_stub()
    test_stub_mini.down_host_network(host.managementIp, test_lib.all_scenario_config, "managment_net")

    wait_for_host_status_change(host.managementIp)

    for thrd in migration_thread_list:
        thrd.start()
    # MINI-1408
    # for thrd in migration_thread_list:
        thrd.join()
        if thrd.exitcode != 0:
            print('----------------------Exception Reason------------------------')
            print(thrd.exc_traceback)
            print('-------------------------Reason End---------------------------\n')
            test_util.test_fail('Error happened while migrating vm: [%s]' % thrd.vm.get_vm().name)

    for vm in vms:
        vm.update()
        vm.check()

    test_stub.up_host_network(host.managementIp, test_lib.all_scenario_config, "managment_net")

    wait_for_host_status_change(host.managementIp, 'Connected')

    test_util.test_pass('VM Live Migration with Progress Checking Test Success')

def env_recover():
    global host
    test_stub.up_host_network(host.managementIp, test_lib.all_scenario_config, "managment_net")
    try:
        for vm in vms:
            vm.destroy()
    except:
        pass


#Will be called only if exception happens in test().
def error_cleanup():
    global host
    test_stub.up_host_network(host.managementIp, test_lib.all_scenario_config, "managment_net")
    try:
        for vm in vms:
            vm.destroy()
    except:
        pass
