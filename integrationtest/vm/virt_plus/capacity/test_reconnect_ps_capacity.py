'''

New Integration Test for capacity update when reconnect ps.

@author: quarkonics
'''

import os
import time
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.operations.primarystorage_operations as ps_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.zstack_test.zstack_test_image as zstack_image_header

_config_ = {
        'timeout' : 200,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
ps = None

DefaultFalseDict = test_lib.DefaultFalseDict
case_flavor = dict(reconnect_ceph=             DefaultFalseDict(ceph=True),
                   )


def test():
    global ps
    flavor = case_flavor[os.environ.get('CASE_FLAVOR')]

    cond = res_ops.gen_query_conditions('state', '=', 'Enabled')
    cond = res_ops.gen_query_conditions('status', '=', 'Connected', cond)
    if flavor['ceph']:
        cond = res_ops.gen_query_conditions('type', '=', 'Ceph', cond)

    ps = res_ops.query_resource_with_num(res_ops.PRIMARY_STORAGE, cond, limit = 1)
    if not ps:
        test_util.test_skip('No Enabled/Connected ps was found, skip test.' )

    ps_ops.reconnect_primary_storage(ps[0].uuid)
    saved_ps = res_ops.query_resource_with_num(res_ops.PRIMARY_STORAGE, cond, limit = 1)
    if flavor['ceph']:
        ps[0].managementIp = ps[0].mons[0].hostname
    else:
        ps[0].managementIp = ps[0].hostname
    if flavor['ceph']:
        test_stub.setup_fake_ceph(ps[0], 631242663936, 428968118272)
        fake_total = 631242663936
        fake_available = 428968118272
    else:
        test_stub.setup_fake_fs(ps[0], '2G', saved_ps[0].url)
        fake_total = 2*1024*1024*1024
        fake_available = 2*1024*1024*1024

    ps_ops.reconnect_primary_storage(ps[0].uuid)

    ps = res_ops.query_resource_with_num(res_ops.PRIMARY_STORAGE, cond, limit = 1)
    if flavor['ceph']:
        ps[0].managementIp = ps[0].mons[0].hostname
    else:
        ps[0].managementIp = ps[0].hostname

    if ps[0].totalCapacity != fake_total:
        test_util.test_fail('totalCapacity %s not updated after reconnect ps' % (ps[0].totalCapacity))
    if ps[0].availableCapacity != fake_available:
        test_util.test_fail('availableCapacity %s not updated after reconnect ps' % (ps[0].availableCapacity))

    if flavor['ceph']:
        test_stub.remove_fake_ceph(ps[0])
    else:
        test_stub.remove_fake_fs(ps[0], saved_ps[0].url)
    ps_ops.reconnect_primary_storage(ps[0].uuid)
    
    ps = res_ops.query_resource_with_num(res_ops.PRIMARY_STORAGE, cond, limit = 1)
    if flavor['ceph']:
        ps[0].managementIp = ps[0].mons[0].hostname
    else:
        ps[0].managementIp = ps[0].hostname

    if ps[0].totalCapacity != saved_ps[0].totalCapacity:
        test_util.test_fail('totalCapacity %s not updated after reconnect ps' % (ps[0].totalCapacity))
    if ps[0].availableCapacity == 0:
        test_util.test_fail('availableCapacity %s not updated after reconnect ps' % (ps[0].availableCapacity))

    test_util.test_pass('Test primary storage capacity after reconnect ps pass.')

#Will be called only if exception happens in test().
def env_recover():
    global ps
    flavor = case_flavor[os.environ.get('CASE_FLAVOR')]
    if flavor['ceph']:
        test_stub.remove_fake_ceph(ps[0])
    else:
        test_stub.remove_fake_fs(ps[0], saved_ps[0].url)
