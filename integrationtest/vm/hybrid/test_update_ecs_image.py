'''

New Integration Test for hybrid.

@author: Legion
'''

import time
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state

test_obj_dict = test_state.TestStateDict()
test_stub = test_lib.lib_get_test_stub()
hybrid = test_stub.HybridObject()

def test():
    hybrid.add_datacenter_iz(add_datacenter_only=True, region_id='cn-shenzhen')
    hybrid.add_bucket()
    ecs_image = test_stub.hyb_ops.sync_ecs_image_from_remote(hybrid.datacenter.uuid)
    exist_image = [image for image in ecs_image if test_stub.ECS_IMAGE_NAME in image.name]
    if exist_image:
        hybrid.ecs_image = exist_image[0]
    else:
        hybrid.create_ecs_image()
        time.sleep(300)

    hybrid.update_ecs_image(name='%s-%s' % (test_stub.ECS_IMAGE_NAME, test_stub._postfix))
    hybrid.update_ecs_image(description='ECS-Image-Description-%s' % test_stub._postfix)

    test_util.test_pass('Update Ecs Image Test Success')

# def env_recover():
#     if hybrid.ecs_image:
#         time.sleep(300)
#         hybrid.del_ecs_image()
# 
#     if hybrid.oss_bucket_create:
#         hybrid.del_bucket()
# 
#     hybrid.tear_down()

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
#     hybrid.tear_down()
    test_lib.lib_error_cleanup(test_obj_dict)
