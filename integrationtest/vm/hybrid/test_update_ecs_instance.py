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
import os
import commands

date_s = time.strftime('%m%d-%H%M%S', time.localtime())
test_obj_dict = test_state.TestStateDict()
test_stub = test_lib.lib_get_test_stub()
ks_inv = None
datacenter_inv = None
bucket_inv = None
vpc_inv = None
vswitch_inv = None
iz_inv = None
sg_inv = None
ecs_inv = None
ecs_eip = None

def test():
    global ks_inv
    global datacenter_inv
    global bucket_inv
    global sg_inv
    global iz_inv
    global vswitch_inv
    global vpc_inv
    global ecs_inv
    global ecs_eip
    datacenter_type = os.getenv('datacenterType')
    ks_existed = hyb_ops.query_aliyun_key_secret()
    if not ks_existed:
        ks_inv = hyb_ops.add_aliyun_key_secret('test_hybrid', 'test for hybrid', os.getenv('aliyunKey'), os.getenv('aliyunSecret'))
    datacenter_list = hyb_ops.get_datacenter_from_remote(datacenter_type)
    regions = [ i.regionId for i in datacenter_list]
    for r in regions:
        if 'shanghai' in r:
            region_id = r
    datacenter_local = hyb_ops.query_datacenter_local()
    if datacenter_local:
        for d in datacenter_local:
            hyb_ops.del_datacenter_in_local(d.uuid)
    datacenter_inv = hyb_ops.add_datacenter_from_remote(datacenter_type, region_id, 'datacenter for test')
    ecs_inv = test_stub.create_ecs_instance(datacenter_type, datacenter_inv.uuid, region_id, allocate_public_ip=True)
    eip_local = hyb_ops.query_hybrid_eip_local()
    ecs_eip = [e for e in eip_local if e.allocateResourceUuid == ecs_inv.uuid][0]
    # Update ECS password
    hyb_ops.update_ecs_instance(ecs_inv.uuid, password='TestPassword123456')
    time.sleep(5)
    hyb_ops.reboot_ecs_instance(ecs_inv.uuid)
    for _ in xrange(600):
        hyb_ops.sync_ecs_instance_from_remote(datacenter_inv.uuid)
        ecs = [e for e in hyb_ops.query_ecs_instance_local() if e.ecsInstanceId == ecs_inv.ecsInstanceId][0]
        if ecs.ecsStatus.lower() == "running":
            break
        else:
            time.sleep(1)
    cmd = "sshpass -p TestPassword123456 ssh -o StrictHostKeyChecking=no root@%s 'ls /'" % ecs_eip.eipAddress
    for _ in xrange(60):
        cmd_status = commands.getstatusoutput(cmd)[0]
        if cmd_status == 0:
            break
        else:
            time.sleep(3)
    assert cmd_status == 0, "Login Ecs via public ip failed!"
    ecs_name = 'test-ecs-instance-%s' % date_s
    # Update ECS name
    hyb_ops.update_ecs_instance(ecs_inv.uuid, name=ecs_name)
    time.sleep(5)
    hyb_ops.sync_ecs_instance_from_remote(datacenter_inv.uuid)
    ecs_local = hyb_ops.query_ecs_instance_local()
    ecs_2 = [e for e in ecs_local if e.ecsInstanceId == ecs_inv.ecsInstanceId][0]
    assert ecs_2.name == ecs_name
    # Update ECS description
    hyb_ops.update_ecs_instance(ecs_inv.uuid, description='test-ecs-instance')
    time.sleep(5)
    hyb_ops.sync_ecs_instance_from_remote(datacenter_inv.uuid)
    ecs_local = hyb_ops.query_ecs_instance_local()
    ecs_3 = [e for e in ecs_local if e.ecsInstanceId == ecs_inv.ecsInstanceId][0]
    assert ecs_3.description == 'test-ecs-instance'
    test_util.test_pass('Update ECS Instance Test Success')

def env_recover():
    global ecs_inv
    global datacenter_inv
    if ecs_inv:
        test_stub.delete_ecs_instance(datacenter_inv, ecs_inv)

    global ecs_eip
    if ecs_eip:
        time.sleep(10)
        hyb_ops.del_hybrid_eip_remote(ecs_eip.uuid)

    global iz_inv
    if iz_inv:
        hyb_ops.del_identity_zone_in_local(iz_inv.uuid)

    if datacenter_inv:
        hyb_ops.del_datacenter_in_local(datacenter_inv.uuid)
    global ks_inv
    if ks_inv:
        hyb_ops.del_aliyun_key_secret(ks_inv.uuid)

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
