'''

@author: FangSun

'''


import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_util as test_util
import os
from zstackwoodpecker.operations import net_operations as net_ops
from zstackwoodpecker.operations import resource_operations as res_ops

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()


def test():

    with test_lib.expected_failure('create vm use system network', Exception):
        test_stub.create_vm_with_random_offering(vm_name='test_vm',
                                                 image_name='imageName_net',
                                                 l3_name='l3ManagementNetworkName')

    exist_vr_offering = res_ops.get_resource(res_ops.VR_OFFERING)[0]

    with test_lib.expected_failure('Create VR offering public network using system', Exception):
        net_ops.create_virtual_router_offering(name='test_vr_offering',
                                               cpuNum=exist_vr_offering.cpuNum,
                                               memorySize=exist_vr_offering.memorySize,
                                               imageUuid=exist_vr_offering.imageUuid,
                                               zoneUuid=exist_vr_offering.zoneUuid,
                                               managementNetworkUuid=exist_vr_offering.managementNetworkUuid,
                                               publicNetworkUuid=test_lib.lib_get_l3_by_name(os.environ.get('l3ManagementNetworkName')).uuid)


def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)


