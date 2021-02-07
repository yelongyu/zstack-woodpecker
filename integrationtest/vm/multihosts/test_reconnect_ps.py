'''
Test for reconnect primary storage

@author: quarkonics
'''

import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.primarystorage_operations as ps_ops

_config_ = {
        'timeout' : 360,
        'noparallel' : True
        }

def test():
    test_util.test_dsc('primary storage reconnection check test')

    for ps in res_ops.query_resource(res_ops.PRIMARY_STORAGE):
        reconnect_ret = ps_ops.reconnect_primary_storage(ps.uuid)
        if reconnect_ret.status != "Connected":
            test_util.test_pass("Reconnect primary storage fail: %s" % (reconnect_ret.status))

    test_util.test_pass("Reconnect primary storage pass")

