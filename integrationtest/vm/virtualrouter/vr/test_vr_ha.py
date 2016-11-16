'''
1. Create 1 Test VMs with VR. 
2. After 1 VM created, Check VR Appliance VM ha status. 


@author: Quarkonics
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.ha_operations as ha_ops

_config_ = {
        'timeout' : 600,
        'noparallel' : False
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    test_util.test_dsc('Create test vm1 and check')
    if test_lib.lib_get_ha_enable() != 'true':
        test_util.test_skip("vm ha not enabled. Skip test")

    vm1 = test_stub.create_vlan_vm()
    test_obj_dict.add_vm(vm1)

    vm1.check()

    vrs = test_lib.lib_find_vr_by_vm(vm1.vm)
    for vr in vrs:
        if ha_ops.get_vm_instance_ha_level(vr.uuid) != "NeverStop":
            test_util.test_fail('vr: %s is not set to HA mode NeverStop.' % vr.uuid)
    vm1.destroy()
    test_util.test_pass('Check VR HA mode Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)

