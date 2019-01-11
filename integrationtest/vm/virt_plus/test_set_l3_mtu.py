'''

@author: Quarkonics
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.net_operations as net_ops
import os
import tempfile

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
default_l3_mtu = None
_config_ = {
        'timeout' : 1800,
        'noparallel' : True
        }


def test():
    global default_l3_mtu
    test_util.test_dsc('Create test vm and check. VR has DNS SNAT EIP PF and DHCP services')
    l3_name = os.environ.get('l3PublicNetworkName')
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    default_l3_mtu = net_ops.get_l3_mtu(l3_net_uuid)
    net_ops.set_l3_mtu(l3_net_uuid, 1200)
    
    vm = test_stub.create_vlan_vm(l3_name)
    test_obj_dict.add_vm(vm)
    vm.check()
    script_file = tempfile.NamedTemporaryFile(delete=False)
    script_file.write('tracepath -n yyk.net | tail -1 | grep "pmtu 1200"')
    script_file.close()
    if not test_lib.lib_execute_shell_script_in_vm(vm.get_vm(), script_file.name):
        test_util.test_fail("fail to check mtu in [vm:] %s" % (vm.get_vm().uuid))
    os.unlink(script_file.name)

    vm.destroy()
    test_util.test_pass('Create VirtualRouter VM DNS DHCP SANT EIP PF Test Success')

def env_recover():
    global default_l3_mtu
    if default_l3_mtu:
        l3_name = os.environ.get('l3PublicNetworkName')
        l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
        net_ops.set_l3_mtu(l3_net_uuid, default_l3_mtu)

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
