'''

New Integration Test for vip qos.

@author: Legion
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state

Port = test_state.Port

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
test_obj_dict2 = test_state.TestStateDict()
qos = test_stub.VIPQOS()

def test():
    qos.create_vm('l3VlanNetworkName6')
    qos.create_vm2('l3VlanNetworkName6')
    qos.create_vip(flat=False)
    test_obj_dict.add_vm(qos.vm)
    test_obj_dict2.add_vm(qos.vm2)
    test_obj_dict.add_vip(qos.vip)
    
    startPort, endPort = Port.get_start_end_ports(Port.rule2_ports)
    port = test_stub.gen_random_port(startPort, endPort)

    qos.set_vip_qos(86, 86)

    qos.create_pf()
    qos.create_lb(port)

    startPort3, endPort3 = Port.get_start_end_ports(Port.rule3_ports)

    loop = True
    n = 0

    while loop:
        try:
            qos.iperf_port = test_stub.gen_random_port(startPort3, endPort3)
            qos.check_outbound_bandwidth()
            qos.check_inbound_bandwidth()
        except IndexError:
            n += 1
            if n == 3:
                loop = False
        else:
            loop = False 

    qos.check_outbound_bandwidth(qos.vm_ip2)
    qos.check_inbound_bandwidth(qos.vm_ip2)

    test_obj_dict.rm_vm(qos.vm)
    test_obj_dict2.rm_vm(qos.vm2)
    test_util.test_pass('Test VIP QoS for PF and LB Success')

def env_recover():
    if qos.vm:
        qos.vm.destroy()

    if qos.vm2:
        qos.vm2.destroy()

    if qos.vip:
        qos.vip.delete()

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
