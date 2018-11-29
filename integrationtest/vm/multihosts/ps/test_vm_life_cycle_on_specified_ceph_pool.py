'''
New Integration Test for create root volume ceph pool.

@author: Lei Liu
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm
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
    test_util.test_dsc('test vm life cycle on specified ceph pool')
    try:
        ps = res_ops.query_resource(res_ops.CEPH_PRIMARY_STORAGE)[0]
    except Exception as e:
        test_util.test_dsc(str(e))
        test_util.test_skip('Skip for not finding ceph ps')
    ps_uuid = ps.uuid

    aliasName = 'test_aliasName_new'
    poolName = 'for_test_root_sas_pool'
    description = 'test_description'
    isCreate = 'true'
    test_util.test_dsc('add new pool by zstack')
    ps_ops.add_ceph_primary_storage_pool(ps_uuid, poolName, aliasName, isCreate, poolType="Root")
    cond = res_ops.gen_query_conditions('aliasName', '=', aliasName)
    pool = res_ops.query_resource(res_ops.CEPH_PRIMARY_STORAGE_POOL, cond)[0]
    print pool
    test_util.test_dsc("poolName: " + str(pool.poolName))
    if pool.poolName != poolName:
        test_util.test_fail('Find wrong pool should find: ' + str(poolName) + 'But find: ' + str(pool.poolName))

    #create vm on sas pool
    instance_offering_uuid = test_lib.lib_get_instance_offering_by_name(
       os.environ.get('instanceOfferingName_s')).uuid
    cond = res_ops.gen_query_conditions('mediaType', '!=', 'ISO')
    cond = res_ops.gen_query_conditions('platform', '=', 'Linux', cond)
    image_uuid = test_lib.lib_get_image_by_name(
        os.environ.get('imageName_s')).uuid
    l3net_uuid = test_lib.lib_get_l3_by_name(
        os.environ.get('l3PublicNetworkName')).uuid

    vm_creation_option = test_util.VmOption()
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_l3_uuids([l3net_uuid])
    vm_creation_option.set_rootVolume_systemTags(["ceph::rootPoolName::for_test_root_sas_pool"])
    vm = test_vm.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    test_util.test_dsc('Create sas VM Test Success')

    #stop vm
    vm.stop()
    #vm.check()

    #start vm
    vm.start()
    vm.clone(["clone_vm"])
    target_host = test_lib.lib_find_random_host(vm.vm)
    vm.migrate(target_host.uuid)
    current_host = test_lib.lib_find_host_by_vm(vm.vm)
    new_host = test_lib.lib_get_vm_host(vm.vm)
    if not new_host:
        test_util.test_fail('Not find available Hosts to do migration')

    if new_host.uuid != target_host.uuid:
        test_util.test_fail('[vm:] did not migrate from [host:] %s to target [host:] %s, but to [host:] %s' % (vm.vm.uuid, current_host.uuid, target_host.uuid, new_host.uuid))
    else:
        test_util.test_logger('[vm:] %s has been migrated from [host:] %s to [host:] %s' % (vm.vm.uuid, current_host.uuid, target_host.uuid))

    test_util.test_pass('Test vm life cycle Success')


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
