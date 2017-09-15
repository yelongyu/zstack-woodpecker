'''

@author: FangSun
'''


import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_util as test_util


test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()


def test():

    pub_l3_vm, flat_l3_vm, vr_l3_vm = test_stub.generate_pub_test_vm(tbj=test_obj_dict)

    flat_vip = test_stub.create_vip('create_flat_vip')
    test_obj_dict.add_vip(flat_vip)
    vr_vip = test_stub.create_vip('create_vr_vip')
    test_obj_dict.add_vip(vr_vip)

    test.flat_eip = test_stub.create_eip('create flat eip', vip_uuid=flat_vip.get_vip().uuid,
                                    vnic_uuid=flat_l3_vm.get_vm().vmNics[0].uuid, vm_obj=flat_l3_vm)

    test.vr_eip = test_stub.create_eip('create vr eip', vip_uuid=vr_vip.get_vip().uuid,
                                    vnic_uuid=vr_l3_vm.get_vm().vmNics[0].uuid, vm_obj=vr_l3_vm)

    flat_vip.attach_eip(test.flat_eip)
    vr_vip.attach_eip(test.vr_eip)

    for vm in (flat_l3_vm, vr_l3_vm):
        vm.check()

    for ip in [pub_l3_vm.get_vm().vmNics[0].ip, flat_vip.get_vip().ip, vr_vip.get_vip().ip]:
        if not test_lib.lib_check_directly_ping(ip):
            test_util.test_fail('expected to be able to ping vip while it fail')

    test_util.test_pass('pub vm volume network test pass')


def env_recover():
    with test_lib.ignored(AttributeError):
        test.flat_eip.delete()

    with test_lib.ignored(AttributeError):
        test.vr_eip.delete()

    test_lib.lib_error_cleanup(test_obj_dict)
