'''

New Integration Test for creating KVM VM.

@author: FangSun
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import random
import itertools

test_obj_dict = test_state.TestStateDict()
test_stub = test_lib.lib_get_test_stub()

BANDWIDTH = random.randint(1, 100) * 1024 * 1024
NET_OUT = random.randint(1, 10) * 1024 * 1024
NET_IN = random.randint(1, 10) * 1024 * 1024


@test_stub.skip_if_multi_ps
def test():

    for bandwidth, net_out, net_in in itertools.product((None, BANDWIDTH), (None, NET_OUT), (None, NET_IN)):
        instance_offering = test_lib.lib_create_instance_offering(name='test_offering',
                                                                  volume_bandwidth=bandwidth,
                                                                  net_outbound_bandwidth=net_out,
                                                                  net_inbound_bandwidth=net_in)
        test_obj_dict.add_instance_offering(instance_offering)
        volume_list = test_stub.create_multi_volumes(ps=random.choice(res_ops.get_resource(res_ops.PRIMARY_STORAGE)))
        for volume in volume_list:
            test_obj_dict.add_volume(volume)
        test_vm = test_stub.create_vm_with_random_offering(vm_name='test_vm', instance_offering_uuid=instance_offering.uuid,
                                                           l3_name='l3VlanNetwork2', image_name='imageName_net')
        test_obj_dict.add_vm(test_vm)
        for volume in volume_list:
            volume.attach(test_vm)
            volume.check()
        test_vm.check()

        for volume in volume_list:
            volume.detach()
            volume.check()
        test_vm.check()

        test_vm_with_datavol = test_stub.create_vm_with_random_offering(vm_name='test_vm_datavol', instance_offering_uuid=instance_offering.uuid,
                                                              disk_offering_uuids=[random.choice(res_ops.get_resource(res_ops.DISK_OFFERING)).uuid],
                                                              l3_name='l3VlanNetwork2', image_name='imageName_net')
        test_obj_dict.add_vm(test_vm_with_datavol)

    test_util.test_pass('Volume attach on QOS vm TEST PASS')


#Will be called only if exception happens in test().
def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)


