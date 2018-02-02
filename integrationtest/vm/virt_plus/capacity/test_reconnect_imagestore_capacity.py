'''

New Integration Test for imagestore capacity update when reconnect bs.

@author: quarkonics
'''

import os
import time
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.operations.backupstorage_operations as bs_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.zstack_test.zstack_test_image as zstack_image_header

_config_ = {
        'timeout' : 200,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
bs = None

def test():
    global bs

    cond = res_ops.gen_query_conditions('state', '=', 'Enabled')
    cond = res_ops.gen_query_conditions('status', '=', 'Connected', cond)
    cond = res_ops.gen_query_conditions('type', '=', 'ImageStoreBackupStorage', cond)
    bs = res_ops.query_resource_with_num(res_ops.BACKUP_STORAGE, cond, limit = 1)
    if not bs:
        test_util.test_skip('No Enabled/Connected bs was found, skip test.' )

    bs_ops.reconnect_backup_storage(bs[0].uuid)
    saved_bs = res_ops.query_resource_with_num(res_ops.BACKUP_STORAGE, cond, limit = 1)
    bs[0].managementIp = bs[0].hostname
    test_stub.setup_fake_fs(bs[0], '2G', saved_bs[0].url)
    bs_ops.reconnect_backup_storage(bs[0].uuid)

    bs = res_ops.query_resource_with_num(res_ops.BACKUP_STORAGE, cond, limit = 1)
    bs[0].managementIp = bs[0].hostname
    if bs[0].totalCapacity != 2*1024*1024*1024:
        test_util.test_fail('totalCapacity %s not updated after reconnect bs' % (bs[0].totalCapacity))
    if bs[0].availableCapacity != 2*1024*1024*1024:
        test_util.test_fail('availableCapacity %s not updated after reconnect bs' % (bs[0].availableCapacity))

    test_stub.remove_fake_fs(bs[0], saved_bs[0].url)
    bs_ops.reconnect_backup_storage(bs[0].uuid)
    
    bs = res_ops.query_resource_with_num(res_ops.BACKUP_STORAGE, cond, limit = 1)
    bs[0].managementIp = bs[0].hostname
    if bs[0].totalCapacity != saved_bs[0].totalCapacity:
        test_util.test_fail('totalCapacity %s not updated after reconnect bs' % (bs[0].totalCapacity))
    if bs[0].availableCapacity == 0:
        test_util.test_fail('availableCapacity %s not updated after reconnect bs' % (bs[0].availableCapacity))

    test_util.test_pass('Test backup storage capacity after reconnect bs pass.')

#Will be called only if exception happens in test().
def env_recover():
    global bs
    test_stub.remove_fake_fs(bs[0], saved_bs[0].url)
