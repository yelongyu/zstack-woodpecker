'''

New Integration Test for local ps capacity update when reconnect host.

@author: quarkonics
'''

import os
import time
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.operations.primarystorage_operations as ps_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.zstack_test.zstack_test_image as zstack_image_header

_config_ = {
        'timeout' : 200,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
host = None

def test():
    global host
    cond = res_ops.gen_query_conditions('state', '=', 'Enabled')
    cond = res_ops.gen_query_conditions('status', '=', 'Connected', cond)
    host = res_ops.query_resource_with_num(res_ops.HOST, cond, limit = 1)
    if not host:
        test_util.test_skip('No Enabled/Connected host was found, skip test.' )

    cond = res_ops.gen_query_conditions('state', '=', 'Enabled')
    cond = res_ops.gen_query_conditions('status', '=', 'Connected', cond)
    cond = res_ops.gen_query_conditions('type', '=', 'LocalStorage', cond)
    ps = res_ops.query_resource_with_num(res_ops.PRIMARY_STORAGE, cond, limit = 1)
    if not ps:
        test_util.test_skip('No Enabled/Connected local ps was found, skip test.' )

    host_ops.reconnect_host(host[0].uuid)
    saved_host_res = vol_ops.get_local_storage_capacity(host[0].uuid, ps[0].uuid)[0]
    test_stub.setup_fake_df(host[0], '62403200', '22403200')
    host_ops.reconnect_host(host[0].uuid)

    host_res = vol_ops.get_local_storage_capacity(host[0].uuid, ps[0].uuid)[0]
    if host_res.totalCapacity != 62403200*1024:
        test_util.test_fail('totalCapacity %s not updated after reconnect host' % (host_res.totalCapacity))
    if host_res.totalPhysicalCapacity != 62403200*1024:
        test_util.test_fail('totalPhysicalCapacity %s not updated after reconnect host' % (host_res.totalPhysicalCapacity))
    if host_res.availablePhysicalCapacity != 22403200*1024:
        test_util.test_fail('availablePhysicalCapacity %s not updated after reconnect host' % (host_res.availablePhysicalCapacity))
    if host_res.totalCapacity - saved_host_res.totalCapacity != host_res.availableCapacity - saved_host_res.availableCapacity:
        test_util.test_fail('availableCapacity %s not updated correctly' % (host_res.availableCapacity))

    test_stub.remove_fake_df(host[0])
    host_ops.reconnect_host(host[0].uuid)
    
    host_res = vol_ops.get_local_storage_capacity(host[0].uuid, ps[0].uuid)[0]
    if host_res.totalCapacity != saved_host_res.totalCapacity:
        test_util.test_fail('totalCapacity %s not updated after reconnect host' % (host_res.totalCapacity))
    if host_res.totalPhysicalCapacity != saved_host_res.totalPhysicalCapacity:
        test_util.test_fail('totalPhysicalCapacity %s not updated after reconnect host' % (host_res.totalPhysicalCapacity))
    if host_res.availablePhysicalCapacity == saved_host_res.availablePhysicalCapacity:
        test_util.test_fail('availablePhysicalCapacity %s %s not updated after reconnect host' % (host_res.availablePhysicalCapacity, saved_host_res.availablePhysicalCapacity))
    if host_res.availableCapacity != saved_host_res.availableCapacity:
        test_util.test_fail('availableCapacity %s not updated after reconnect host' % (host_res.availableCapacity))

    test_util.test_pass('Test backup storage capacity for adding/deleting image pass.')

#Will be called only if exception happens in test().
def env_recover():
    global host
    test_stub.remove_fake_df(host[0])
