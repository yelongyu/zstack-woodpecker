'''

New Integration Test for capacity update when reconnect bs.

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

DefaultFalseDict = test_lib.DefaultFalseDict
case_flavor = dict(reconnect_sftp=             DefaultFalseDict(sftp=True, imagestore=False, ceph=False),
                   reconnect_imagestore=             DefaultFalseDict(sftp=False, imagestore=True, ceph=False),
                   reconnect_ceph=             DefaultFalseDict(sftp=False, imagestore=False, ceph=True),
                   )


def test():
    global bs
    flavor = case_flavor[os.environ.get('CASE_FLAVOR')]

    cond = res_ops.gen_query_conditions('state', '=', 'Enabled')
    cond = res_ops.gen_query_conditions('status', '=', 'Connected', cond)
    if flavor['sftp']:
        cond = res_ops.gen_query_conditions('type', '=', 'SftpBackupStorage', cond)
    elif flavor['imagestore']:
        cond = res_ops.gen_query_conditions('type', '=', 'ImageStoreBackupStorage', cond)
    elif flavor['ceph']:
        cond = res_ops.gen_query_conditions('type', '=', 'Ceph', cond)

    bs = res_ops.query_resource_with_num(res_ops.BACKUP_STORAGE, cond, limit = 1)
    if not bs:
        test_util.test_skip('No Enabled/Connected bs was found, skip test.' )

    bs_ops.reconnect_backup_storage(bs[0].uuid)
    saved_bs = res_ops.query_resource_with_num(res_ops.BACKUP_STORAGE, cond, limit = 1)
    if flavor['ceph']:
        bs[0].managementIp = bs[0].mons[0].hostname
    else:
        bs[0].managementIp = bs[0].hostname
    if flavor['ceph']:
        test_stub.setup_fake_ceph(bs[0], 631242663936, 428968118272)
        fake_total = 631242663936
        fake_available = 428968118272
    else:
        test_stub.setup_fake_fs(bs[0], '2G', saved_bs[0].url)
        fake_total = 2*1024*1024*1024
        fake_available = 2*1024*1024*1024

    bs_ops.reconnect_backup_storage(bs[0].uuid)

    bs = res_ops.query_resource_with_num(res_ops.BACKUP_STORAGE, cond, limit = 1)
    if flavor['ceph']:
        bs[0].managementIp = bs[0].mons[0].hostname
    else:
        bs[0].managementIp = bs[0].hostname

    if bs[0].totalCapacity != fake_total:
        test_util.test_fail('totalCapacity %s not updated after reconnect bs' % (bs[0].totalCapacity))
    if bs[0].availableCapacity != fake_available:
        test_util.test_fail('availableCapacity %s not updated after reconnect bs' % (bs[0].availableCapacity))

    if flavor['ceph']:
        test_stub.remove_fake_ceph(bs[0])
    else:
        test_stub.remove_fake_fs(bs[0], saved_bs[0].url)
    bs_ops.reconnect_backup_storage(bs[0].uuid)
    
    bs = res_ops.query_resource_with_num(res_ops.BACKUP_STORAGE, cond, limit = 1)
    if flavor['ceph']:
        bs[0].managementIp = bs[0].mons[0].hostname
    else:
        bs[0].managementIp = bs[0].hostname

    if bs[0].totalCapacity != saved_bs[0].totalCapacity:
        test_util.test_fail('totalCapacity %s not updated after reconnect bs' % (bs[0].totalCapacity))
    if bs[0].availableCapacity == 0:
        test_util.test_fail('availableCapacity %s not updated after reconnect bs' % (bs[0].availableCapacity))

    test_util.test_pass('Test backup storage capacity after reconnect bs pass.')

#Will be called only if exception happens in test().
def env_recover():
    global bs
    flavor = case_flavor[os.environ.get('CASE_FLAVOR')]
    if flavor['ceph']:
        test_stub.remove_fake_ceph(bs[0])
    else:
        test_stub.remove_fake_fs(bs[0], saved_bs[0].url)
