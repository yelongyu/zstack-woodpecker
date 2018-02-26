'''

New Integration Test for hybrid.

@author: Legion
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import time


test_obj_dict = test_state.TestStateDict()
test_stub = test_lib.lib_get_test_stub()
hybrid = test_stub.HybridObject()

def test():
    hybrid.create_ecs_instance()
    test_obj_dict.add_hybrid_obj(hybrid)

    hybrid.create_aliyun_disk()
    hybrid.attach_aliyun_disk()
    hybrid.update_aliyun_disk(name='aliyun-disk')
    hybrid.update_aliyun_disk(description='test-aliyun-disk')
    hybrid.update_aliyun_disk(delete_with_instance='true')
    hybrid.del_ecs_instance()
    hybrid.sync_aliyun_disk(check=False)
    hybrid.check_resource('delete', 'diskId', hybrid.disk.diskId, 'query_aliyun_disk_local')
    test_util.test_pass('Update Aliyun Disk Test Success')

def env_recover():
    hybrid.tear_down()

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    hybrid.tear_down()
    test_lib.lib_error_cleanup(test_obj_dict)
