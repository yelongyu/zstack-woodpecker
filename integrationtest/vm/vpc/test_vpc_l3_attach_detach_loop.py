'''
@author: FangSun
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.net_operations as net_ops
import time
import random
import os



test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()


all_vpc_l3_list = ['l3VlanNetworkName1'] + ["l3VlanNetwork{}".format(i) for i in xrange(2,11)] + \
                  ["l3VxlanNetwork{}".format(i) for i in xrange(11,21)]

case_flavor = dict(one_vpc=   dict(vpc_num=1),
                   two_vpc=   dict(vpc_num=2),
                   )

vr_inv_list = []


@test_lib.pre_execution_action(test_stub.remove_all_vpc_vrouter)
def test():
    flavor = case_flavor[os.environ.get('CASE_FLAVOR')]
    test_util.test_dsc("create vpc vrouter and attach vpc l3 to vpc")
    vr_inv_list.append(test_stub.create_vpc_vrouter('vpc1'))
    if flavor['vpc_num'] == 2:
        vr_inv_list.append(test_stub.create_vpc_vrouter('vpc2'))

    for _ in xrange(3):
        for vr_inv in vr_inv_list:
            test_stub.attach_all_l3_to_vpc_vr(vr_inv, all_vpc_l3_list)
            conf = res_ops.gen_query_conditions('uuid', '=', vr_inv.uuid)
            vr_inv = res_ops.query_resource(res_ops.APPLIANCE_VM, conf)[0]
            nic_uuid_list = [nic.uuid for nic in vr_inv.vmNics if nic.metaData == '4']
            assert len(nic_uuid_list) == len(all_vpc_l3_list)
            for nic_uuid in nic_uuid_list:
                net_ops.detach_l3(nic_uuid)
            time.sleep(10)

    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_vrouter()

def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_vrouter()

