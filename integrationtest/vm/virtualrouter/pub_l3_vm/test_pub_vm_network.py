'''

@author: FangSun
'''


import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.net_operations as net_ops
import os
import time


test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()


@test_stub.skip_if_no_service_in_l3('Eip', os.environ.get('l3NoVlanNetworkName2'))
@test_stub.skip_if_no_service_in_l3('Eip', os.environ.get('l3NoVlanNetworkName1'))
def test():

    pub_l3_vm, flat_l3_vm, vr_l3_vm = test_stub.generate_pub_test_vm(tbj=test_obj_dict)

    ip_status_before = net_ops.get_ip_capacity_by_l3s(l3_network_list=[pub_l3_vm.get_vm().vmNics[0].l3NetworkUuid])

    flat_vip = test_stub.create_vip('create_flat_vip')
    test_obj_dict.add_vip(flat_vip)
    vr_vip = test_stub.create_vip('create_vr_vip')
    test_obj_dict.add_vip(vr_vip)

    ip_status_after = net_ops.get_ip_capacity_by_l3s(l3_network_list=[pub_l3_vm.get_vm().vmNics[0].l3NetworkUuid])

    assert ip_status_before.availableCapacity == ip_status_after.availableCapacity + 2

    test.flat_eip = test_stub.create_eip('create flat eip', vip_uuid=flat_vip.get_vip().uuid,
                                    vnic_uuid=flat_l3_vm.get_vm().vmNics[0].uuid, vm_obj=flat_l3_vm)

    test.vr_eip = test_stub.create_eip('create vr eip', vip_uuid=vr_vip.get_vip().uuid,
                                    vnic_uuid=vr_l3_vm.get_vm().vmNics[0].uuid, vm_obj=vr_l3_vm)

    flat_vip.attach_eip(test.flat_eip)
    vr_vip.attach_eip(test.vr_eip)

    for vm in (flat_l3_vm, vr_l3_vm):
        vm.check()
    
    time.sleep(30)
    l3 = test_lib.lib_get_l3_by_name(os.environ.get('l3PublicNetworkName'))
    if 'DHCP' in [service.networkServiceType for service in l3.networkServices]:
        ip_list = [pub_l3_vm.get_vm().vmNics[0].ip, flat_vip.get_vip().ip, vr_vip.get_vip().ip]
        for ip in ip_list:
            if not test_lib.lib_check_directly_ping(ip):
                test_util.test_fail('expected to be able to ping vip while it fail')

    test_lib.lib_error_cleanup(test_obj_dict)
    ip_status_final = net_ops.get_ip_capacity_by_l3s(l3_network_list=[pub_l3_vm.get_vm().vmNics[0].l3NetworkUuid])
    assert ip_status_final.availableCapacity == ip_status_after.availableCapacity + 3

    test_util.test_pass('pub vm volume network test pass')


def env_recover():
    with test_lib.ignored(AttributeError):
        test.flat_eip.delete()

    with test_lib.ignored(AttributeError):
        test.vr_eip.delete()

    test_lib.lib_error_cleanup(test_obj_dict)
