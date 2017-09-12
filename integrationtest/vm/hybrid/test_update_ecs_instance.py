'''

New Integration Test for hybrid.

@author: Legion
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.hybrid_operations as hyb_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import time


postfix = time.strftime('%m%d-%H%M%S', time.localtime())
test_obj_dict = test_state.TestStateDict()
test_stub = test_lib.lib_get_test_stub()
hybrid = test_stub.HybridObject()

def test():
    hybrid.create_ecs_instance()
    ecs_name = 'test-ecs-instance-%s' % postfix
    # Update ECS name
    hyb_ops.update_ecs_instance(hybrid.ecs_instance.uuid, name=ecs_name)
    time.sleep(5)
    hyb_ops.sync_ecs_instance_from_remote(hybrid.datacenter.uuid)
    ecs_local = hyb_ops.query_ecs_instance_local()
    ecs_2 = [e for e in ecs_local if e.ecsInstanceId == hybrid.ecs_instance.ecsInstanceId][0]
    assert ecs_2.name == ecs_name
    # Update ECS description
    hyb_ops.update_ecs_instance(hybrid.ecs_instance.uuid, description='test-ecs-instance')
    time.sleep(5)
    hyb_ops.sync_ecs_instance_from_remote(hybrid.datacenter.uuid)
    ecs_local = hyb_ops.query_ecs_instance_local()
    ecs_3 = [e for e in ecs_local if e.ecsInstanceId == hybrid.ecs_instance.ecsInstanceId][0]
    assert ecs_3.description == 'test-ecs-instance'
    test_util.test_pass('Update ECS Instance name & description Test Success')

def env_recover():
    if hybrid.ecs_instance:
        hybrid.del_ecs_instance()

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
