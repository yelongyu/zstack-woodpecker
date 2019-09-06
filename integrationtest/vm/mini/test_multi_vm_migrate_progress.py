'''

Test VM Live Migration with 1 Host Management network down via Longjob:
1. Live migrate 5 VMs;
2. All 5 VMs have CPU/Memory stress load

@author: Legion
'''

import os
import time
import random
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
from threading import Thread


test_stub = test_lib.lib_get_test_stub('virtualrouter')
longjob = test_stub.Longjob()
VMNUM = 3
vms = []
thread_list = []
host = None
vm_thrd_list = []

class CrtVMThread(Thread):
    def __init__(self, target=None, kwargs=None):
        self.vm = None
        self.__target = target
        self.__kwargs = kwargs
        super(CrtVMThread, self).__init__(target=target, kwargs=kwargs)

    def run(self):
        try:
            if self.__target:
                self.vm = self.__target(**self.__kwargs)
        finally:
            del self.__target, self.__kwargs

def wait_for_host_change(host_ip, status='Disconnected'):
    conditions = res_ops.gen_query_conditions('managementIp', '=', host_ip)
    host_status = res_ops.query_resource(res_ops.HOST, conditions)[0].status
    for _ in xrange(60):
        if host_status == status:
            return
        else:
            time.sleep(3)


def test():
    global host
    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = os.getenv('zstackHaVip')
    host_uuid = res_ops.query_resource(res_ops.HOST)[0].uuid

    for _ in range(VMNUM):
        vm_thrd_list.append(CrtVMThread(target=longjob.create_vm, kwargs={'l3_name': os.environ.get('l3PublicNetworkName'), 'host_uuid': host_uuid}))
        # vms.append(longjob.create_vm(l3_name=os.environ.get('l3PublicNetworkName'), host_uuid=host_uuid))


    for vmthrd in vm_thrd_list:
        vmthrd.start()

    for vmthrd in vm_thrd_list:
        vmthrd.join()
        vms.append(vmthrd.vm)

    for vm in vms:
        thread_list.append(Thread(target=longjob.live_migrate_vm, args=(vm, True)))
        longjob.add_stress(vm, networkio=False)

    cond_host = res_ops.gen_query_conditions('uuid', '=', host_uuid)
    host = res_ops.query_resource(res_ops.HOST, cond_host)[0]
    test_stub_mini = test_lib.lib_get_test_stub()

    test_stub_mini.down_host_network(host.managementIp, test_lib.all_scenario_config, "managment_net")

    wait_for_host_change(host.managementIp)

    for thrd in thread_list:
        thrd.start()

    for thrd in thread_list:
        thrd.join()

    for vm in vms:
        vm.check()
        longjob.check_data_integrity(vm)

    test_stub.up_host_network(host.managementIp, test_lib.all_scenario_config, "managment_net")

    wait_for_host_change(host.managementIp, 'Connected')

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
