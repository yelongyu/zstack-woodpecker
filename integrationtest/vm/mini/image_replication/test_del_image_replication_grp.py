'''

New Integration test for image replication group.

@author: Legion
'''

import os
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib

repl_grp_name = 'test_image_replication_group'
test_stub = test_lib.lib_get_test_stub()
repl_grp = test_stub.ImageReplication()

def test():
    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = os.getenv('zstackHaVip')
    # Iamge replication group create & delete
    repl_grp.create_replication_grp(repl_grp_name)
    assert repl_grp.get_replication_grp(repl_grp_name)
    repl_grp.del_replication_grp(repl_grp.replication_grp.uuid)
    assert not repl_grp.get_replication_grp(repl_grp_name)

    test_util.test_pass('Delete Image Replication Group Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    try:
        repl_grp.del_replication_grp(repl_grp.replication_grp.uuid)
    except:
        pass
