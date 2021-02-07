'''

New Integration Test for vip qos.

@author: Legion
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.config_operations as conf_ops
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
qos = test_stub.VIPQOS()

def test():
    if os.getenv('zstackHaVip'):
        os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = os.getenv('zstackHaVip')
    conf_ops.change_global_config("networkService", "defaultDhcpMtu.l2VlanNetwork", '1450')
    qos.create_vm('l3VlanNetworkName5')
    qos.create_eip(flat=True)
    test_obj_dict.add_vm(qos.vm)
    test_obj_dict.add_vip(qos.vip)

    qos.set_vip_qos(27, 27)

    qos.check_outbound_bandwidth()
    qos.check_inbound_bandwidth()

    qos.vip.delete()
    test_obj_dict.rm_vm(qos.vm)
    test_util.test_pass('Flat Network VIP QoS 27M-In 27M-Out Test Success')

def env_recover():
    if qos.vm:
        qos.vm.destroy()
    if qos.vip:
        qos.vip.delete()
    qos.detach_eip_service()

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    qos.detach_eip_service()
    test_lib.lib_error_cleanup(test_obj_dict)
