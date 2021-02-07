'''

New Integration Test for ps capacity update when reconnect host.

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
DefaultFalseDict = test_lib.DefaultFalseDict
case_flavor = dict(reconnect_local=             DefaultFalseDict(local=True, smp=False, nfs=False, ceph=False),
                   reconnect_smp=             DefaultFalseDict(local=False, smp=True, nfs=False, ceph=False),
                   reconnect_nfs=             DefaultFalseDict(local=False, smp=False, nfs=True, ceph=False),
                   reconnect_ceph=             DefaultFalseDict(local=False, smp=False, nfs=False, ceph=True),
                   )

def test():
    global host
    flavor = case_flavor[os.environ.get('CASE_FLAVOR')]
    cond = res_ops.gen_query_conditions('state', '=', 'Enabled')
    cond = res_ops.gen_query_conditions('status', '=', 'Connected', cond)
    host = res_ops.query_resource_with_num(res_ops.HOST, cond, limit = 1)
    if not host:
        test_util.test_skip('No Enabled/Connected host was found, skip test.' )

    cond = res_ops.gen_query_conditions('state', '=', 'Enabled')
    cond = res_ops.gen_query_conditions('status', '=', 'Connected', cond)
    if flavor['local']:
        cond = res_ops.gen_query_conditions('type', '=', 'LocalStorage', cond)
    elif flavor['smp']:
        cond = res_ops.gen_query_conditions('type', '=', 'SharedMountPoint', cond)
    elif flavor['nfs']:
        cond = res_ops.gen_query_conditions('type', '=', 'NFS', cond)
    elif flavor['ceph']:
        cond = res_ops.gen_query_conditions('type', '=', 'Ceph', cond)
    ps = res_ops.query_resource_with_num(res_ops.PRIMARY_STORAGE, cond, limit = 1)
    if not ps:
        test_util.test_skip('No Enabled/Connected local ps was found, skip test.' )

    host_ops.reconnect_host(host[0].uuid)
    if flavor['local']:
        saved_res = vol_ops.get_local_storage_capacity(host[0].uuid, ps[0].uuid)[0]
    elif flavor['smp']:
        saved_res = res_ops.query_resource_with_num(res_ops.PRIMARY_STORAGE, cond, limit = 1)[0]
    elif flavor['nfs']:
        saved_res = res_ops.query_resource_with_num(res_ops.PRIMARY_STORAGE, cond, limit = 1)[0]

    test_stub.setup_fake_df(host[0], '62403200', '22403200')
    host_ops.reconnect_host(host[0].uuid)

    if flavor['local']:
        res = vol_ops.get_local_storage_capacity(host[0].uuid, ps[0].uuid)[0]
    elif flavor['smp']:
        res = res_ops.query_resource_with_num(res_ops.PRIMARY_STORAGE, cond, limit = 1)[0]
    elif flavor['nfs']:
        res = res_ops.query_resource_with_num(res_ops.PRIMARY_STORAGE, cond, limit = 1)[0]

    if res.totalCapacity != 62403200*1024:
        test_util.test_fail('totalCapacity %s not updated after reconnect host' % (res.totalCapacity))
    if res.totalPhysicalCapacity != 62403200*1024:
        test_util.test_fail('totalPhysicalCapacity %s not updated after reconnect host' % (res.totalPhysicalCapacity))
    if res.availablePhysicalCapacity != 22403200*1024:
        test_util.test_fail('availablePhysicalCapacity %s not updated after reconnect host' % (res.availablePhysicalCapacity))
    if flavor['local']:
        if res.totalCapacity - saved_res.totalCapacity != res.availableCapacity - saved_res.availableCapacity:
            test_util.test_fail('availableCapacity %s not updated correctly' % (res.availableCapacity))

    test_stub.remove_fake_df(host[0])
    host_ops.reconnect_host(host[0].uuid)
    
    if flavor['local']:
        res = vol_ops.get_local_storage_capacity(host[0].uuid, ps[0].uuid)[0]
    elif flavor['smp']:
        res = res_ops.query_resource_with_num(res_ops.PRIMARY_STORAGE, cond, limit = 1)[0]
    elif flavor['nfs']:
        res = res_ops.query_resource_with_num(res_ops.PRIMARY_STORAGE, cond, limit = 1)[0]

    if res.totalCapacity != saved_res.totalCapacity:
        test_util.test_fail('totalCapacity %s not updated after reconnect host' % (res.totalCapacity))
    if res.totalPhysicalCapacity != saved_res.totalPhysicalCapacity:
        test_util.test_fail('totalPhysicalCapacity %s not updated after reconnect host' % (res.totalPhysicalCapacity))
    if flavor['local']:
        if res.availablePhysicalCapacity == saved_res.availablePhysicalCapacity:
            test_util.test_fail('availablePhysicalCapacity %s %s not updated after reconnect host' % (res.availablePhysicalCapacity, saved_res.availablePhysicalCapacity))
        if res.availableCapacity != saved_res.availableCapacity:
            test_util.test_fail('availableCapacity %s not updated after reconnect host' % (res.availableCapacity))

    test_util.test_pass('Test backup storage capacity for adding/deleting image pass.')

#Will be called only if exception happens in test().
def env_recover():
    global host
    test_stub.remove_fake_df(host[0])
