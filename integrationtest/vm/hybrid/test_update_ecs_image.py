'''

New Integration Test for hybrid.

@author: Legion
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state

test_obj_dict = test_state.TestStateDict()
test_stub = test_lib.lib_get_test_stub()
hybrid = test_stub.HybridObject()

def test():
    hybrid.add_datacenter_iz(add_datacenter_only=True, region_id='cn-shenzhen')
    hybrid.add_bucket()
    hybrid.create_ecs_image()

    hybrid.update_ecs_image(name='ECS-Image-%s' % test_stub._postfix)
    hybrid.update_ecs_image(description='test-ECS-Image-%s' % test_stub._postfix)

    test_util.test_pass('Update Ecs Image Test Success')

def env_recover():
    if hybrid.ecs_image:
        hybrid.del_ecs_image()

    if hybrid.oss_bucket_create:
        hybrid.del_bucket()

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
