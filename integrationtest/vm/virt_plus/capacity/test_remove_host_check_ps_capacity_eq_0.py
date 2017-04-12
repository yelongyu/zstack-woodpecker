'''
New Integration Test for SMP ps remove host and check ps capacity equal 0.
@author: SyZhao
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.operations.host_operations as host_ops
import time
import os

_config_ = {
        'timeout' : 200,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    test_util.test_dsc('SMP ps remove host and check ps is 0')
    pss = res_ops.get_resource(res_ops.PRIMARY_STORAGE)
    #if pss[0].type != "SharedMountPoint":
    #    test_util.test_skip("ps is not smp as expected, therefore, skip!")
    
    cond = res_ops.gen_query_conditions('state', '=', 'Enabled')
    cond = res_ops.gen_query_conditions('status', '=', 'Connected', cond)
    host = res_ops.query_resource_with_num(res_ops.HOST, cond, limit = 1)
    if not host:
        test_util.test_skip('No Enabled/Connected host was found, skip test.' )
        return True

    ps = res_ops.query_resource_with_num(res_ops.PRIMARY_STORAGE, cond, limit = 1)
    if not ps:
        test_util.test_skip('No Enabled/Connected primary storage was found, skip test.' )
        return True

    host = host[0]
    ps = ps[0]

    vm = test_stub.create_vm(vm_name = 'basic-test-vm', host_uuid = host.uuid)
    vm.check()

    host_ops.delete_host(host.uuid)

    ps_capacity = test_lib.lib_get_storage_capacity(ps_uuids=[ps.uuid])
    avail_cap = ps_capacity.availableCapacity
    avail_phy_cap = ps_capacity.availablePhysicalCapacity
    avail_total_cap = ps_capacity.totalCapacity
    avail_total_phy_cap = ps_capacity.totalPhysicalCapacity
    if avail_cap != 0:
        test_util.test_fail("avail_cap:%d is not 0 as expected" %(avail_cap))
    if avail_phy_cap != 0:
        test_util.test_fail("avail_phy_cap:%d is not 0 as expected" %(avail_phy_cap))
    if avail_total_cap != 0:
        test_util.test_fail("avail_total_cap:%d is not 0 as expected" %(avail_total_cap))
    if avail_total_phy_cap != 0:
        test_util.test_fail("avail_total_phy_cap:%d is not 0 as expected" %(avail_total_phy_cap))

    test_util.test_pass('SMP remove host check ps capacity equal 0 test success')


#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
