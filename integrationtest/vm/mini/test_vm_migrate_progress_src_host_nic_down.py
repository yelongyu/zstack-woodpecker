'''

Test VM Live Migration with 1 Host Management network down via Longjob

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
host = None

def wait_for_host_status_change(host_ip, status='Disconnected'):
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
    longjob.create_vm(l3_name=os.environ.get('l3PublicNetworkName'))

    host_uuid = longjob.vm.get_vm().hostUuid
    cond_host = res_ops.gen_query_conditions('uuid', '=', host_uuid)
    host = res_ops.query_resource(res_ops.HOST, cond_host)[0]

    conditions = res_ops.gen_query_conditions('clusterUuid', '=', host.clusterUuid)
    cond_other_host = res_ops.gen_query_conditions('uuid', '!=', host.uuid, conditions)

    other_host = res_ops.query_resource(res_ops.HOST, cond_other_host)[0]

    longjob.add_stress(networkio=False)

    test_stub_mini = test_lib.lib_get_test_stub()
    test_stub_mini.down_host_network(host.managementIp, test_lib.all_scenario_config, "managment_net")
    wait_for_host_status_change(host.managementIp)

    longjob.live_migrate_vm(host_uuid=other_host.uuid, allow_unknown=True)

    test_stub.up_host_network(host.managementIp, test_lib.all_scenario_config, "managment_net")

    wait_for_host_status_change(host.managementIp, 'Connecting')

    longjob.vm.update()
    longjob.vm.check()

    wait_for_host_status_change(host.managementIp, 'Connected')

    test_util.test_pass('VM Live Migration with Progress Checking Test Success')

def env_recover():
    global host
    test_stub.up_host_network(host.managementIp, test_lib.all_scenario_config, "managment_net")
    try:
        longjob.vm.destroy()
    except:
        pass


#Will be called only if exception happens in test().
def error_cleanup():
    global host
    test_stub.up_host_network(host.managementIp, test_lib.all_scenario_config, "managment_net")
    try:
        longjob.vm.destroy()
    except:
        pass
