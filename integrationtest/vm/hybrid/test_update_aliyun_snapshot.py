'''

New Integration Test for hybrid.

@author: Legion
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import time

test_stub = test_lib.lib_get_test_stub()
hybrid = test_stub.HybridObject()

def test():
    hybrid.create_ecs_instance()
    test_obj_dict.add_hybrid_obj(hybrid)
    hybrid.create_aliyun_disk()
    hybrid.attach_aliyun_disk()
    hybrid.create_aliyun_snapshot()

    hybrid.update_aliyun_snapshot(name='Aliyun-Snapshot')
    hybrid.update_aliyun_snapshot(description='test-Aliyun-Snapshot')

    test_util.test_pass('Update Aliyun Snapshot Test Success')

def env_recover():
    if hybrid.disk:
        time.sleep(30)
        hybrid.del_aliyun_disk()

    if hybrid.ecs_instance:
        hybrid.del_ecs_instance()

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
