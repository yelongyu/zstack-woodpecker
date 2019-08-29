'''

Test VM Live Migration with Host Management net dow via Longjob

@author: Legion
'''

import os
import time
import random
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops


test_stub = test_lib.lib_get_test_stub('virtualrouter')
longjob = test_stub.Longjob()


def test():
    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = os.getenv('zstackHaVip')
    longjob.create_vm()

    host_uuid = longjob.vm.get_vm().hostUuid
    cond_host = res_ops.gen_query_conditions('uuid', '=', host_uuid)
    host = res_ops.query_resource(res_ops.HOST, cond_host)[0]
    test_stub_mini = test_lib.lib_get_test_stub()

    test_stub_mini.down_host_network(host.managementIp, test_lib.all_scenario_config, "managment_net")
    time.sleep(90)

    longjob.live_migrate_vm()
    time.sleep(30)

    test_stub.up_host_network(host.managementIp, test_lib.all_scenario_config, "managment_net")

    for _ in range(100):
        if res_ops.query_resource(res_ops.HOST, cond_host)[0].status == 'Connected':
            break
        else:
            time.sleep(3)
    test_util.test_pass('VM Live Migration with Progress Checking Test Success')

def env_recover():
    try:
        longjob.vm.destroy()
    except:
        pass


#Will be called only if exception happens in test().
def error_cleanup():
    try:
        longjob.vm.destroy()
    except:
        pass
