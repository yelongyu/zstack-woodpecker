'''
New Integration Test for create ceph pool.

@author: Lei Liu
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.primarystorage_operations as ps_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.header.vm as vm_header
import apibinding.inventory as inventory
import zstacklib.utils.ssh as ssh
import os

_config_ = {
        'timeout' : 1000,
        'noparallel' : True
        }

test_obj_dict = test_state.TestStateDict()
ps_uuid = None
host_uuid = None
vr_uuid = None

def test():
    test_util.test_dsc('create ceph pool')
    try:
        ps = res_ops.query_resource(res_ops.CEPH_PRIMARY_STORAGE)[0]
    except Exception as e:
        test_util.test_dsc(str(e))
        test_util.test_skip('Skip for not finding ceph ps')
    ps_uuid = ps.uuid
    try:
        ceph_node_ip = ps.mons[0].monAddr
    except Exception as e:
        test_util.test_dsc(str(e))
        test_util.test_fail('Fail to get mon ip')
    create_pool_cmd = 'ceph osd pool create for_test_pool_create 4'
    try:
        (ret, out, eout) = ssh.execute(create_pool_cmd, ceph_node_ip, 'root', 'password')
    except Exception as e:
        test_util.test_dsc(str(e))
        test_util.test_fail('Fail to create pool by using ceph command')
    aliasName = 'test_aliasName_new'
    poolName = 'test_poolName'
    description = 'test_description'
    isCreate = 'true'
    test_util.test_dsc('add new pool by zstack')
    ps_ops.add_ceph_primary_storage_pool(ps_uuid, poolName, aliasName, isCreate, poolType="Data")
    cond = res_ops.gen_query_conditions('aliasName', '=', aliasName)
    pool = res_ops.query_resource(res_ops.CEPH_PRIMARY_STORAGE_POOL, cond)[0]
    print pool
    test_util.test_dsc("poolName: " + str(pool.poolName))
    if pool.poolName != poolName:
        test_util.test_fail('Find wrong pool should find: ' + str(poolName) + 'But find: ' + str(pool.poolName))
    test_util.test_dsc('add exist pool by zstack')
    aliasName = 'test_aliasName_exist'
    ps_ops.add_ceph_primary_storage_pool(ps_uuid, 'for_test_pool_create', aliasName, poolType="Data")
    cond = res_ops.gen_query_conditions('aliasName', '=', aliasName)
    pool = res_ops.query_resource(res_ops.CEPH_PRIMARY_STORAGE_POOL, cond)[0]
    test_util.test_dsc("poolName: " + str(pool.poolName))
    if pool.poolName != 'for_test_pool_create':
        test_util.test_fail('Find wrong pool should find: for_test_pool_create But find: ' + str(pool.poolName))

#Will be called only if exception happens in test().
def error_cleanup():
    global ps_uuid
    if ps_uuid != None:
        ps_ops.change_primary_storage_state(ps_uuid, 'Enabled')
    global host_uuid
    if host_uuid != None:
        host_ops.reconnect_host(host_uuid)
    global vr_uuid
    if vr_uuid != None:
        vm_ops.reconnect_vr(vr_uuid)
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
