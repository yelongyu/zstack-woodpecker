'''

New Integration Test for vip qos.

@author: Legion
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
qos = test_stub.VIPQOS()
port = test_stub.gen_random_port()

def test():
    qos.create_vm('l3VlanNetworkName1')
    qos.create_eip()
    test_obj_dict.add_vm(qos.vm)
    test_obj_dict.add_vip(qos.vip)

    qos.set_vip_qos(21, 19, port, port)

    qos.check_outbound_bandwidth()
    qos.check_inbound_bandwidth()

    qos.vip.delete()
    test_util.test_pass('Create VIP Qos for EIP Success')

def env_recover():
    if qos.vm:
        qos.vm.destroy()
    if qos.vip:
        qos.vip.delete()

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
