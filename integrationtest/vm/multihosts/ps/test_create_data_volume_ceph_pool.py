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
    create_pool_cmd = 'ceph osd pool create test_create_data_ssd_pool 4'
    try:
        (ret, out, eout) = ssh.execute(create_pool_cmd, ceph_node_ip, 'root', 'password')
    except Exception as e:
        test_util.test_dsc(str(e))
        test_util.test_fail('Fail to create pool by using ceph command')
    aliasName = 'test_aliasName_create_data_sas'
    rootPoolName = 'test_create_data_sas_pool'
    description = 'test_description'
    isCreate = 'true'
    test_util.test_dsc('add new pool by zstack')
    ps_ops.add_ceph_primary_storage_pool(ps_uuid, rootPoolName, aliasName, isCreate, poolType="Root")
    dataPoolName = 'for_test_create_data_sas_pool'
    aliasName = 'test_aliasName_new_data'
    ps_ops.add_ceph_primary_storage_pool(ps_uuid, dataPoolName, aliasName, isCreate, poolType="Data")
    #create vm on sas pool
    instance_offering_uuid = test_lib.lib_get_instance_offering_by_name(
       os.environ.get('instanceOfferingName_s')).uuid
    cond = res_ops.gen_query_conditions('mediaType', '!=', 'ISO')
    cond = res_ops.gen_query_conditions('platform', '=', 'Linux', cond)
    disk_offering = test_lib.lib_get_disk_offering_by_name(
        os.environ.get('smallDiskOfferingName')).uuid

    image_uuid = test_lib.lib_get_image_by_name(
        os.environ.get('imageName_s')).uuid
    l3net_uuid = test_lib.lib_get_l3_by_name(
        os.environ.get('l3PublicNetworkName')).uuid
       
    vm_creation_option = test_util.VmOption()
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_data_disk_uuids([disk_offering])
    vm_creation_option.set_l3_uuids([l3net_uuid])
    vm_creation_option.set_rootVolume_systemTags(["ceph::rootPoolName::test_create_data_ssd_pool"])
    vm_creation_option.set_dataVolume_systemTags(["ceph::pool::for_test_create_data_sas_pool"])
    vm = test_vm.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    test_util.test_dsc('Create sas VM/Volume Test Success')

    vm_creation_option.set_rootVolume_systemTags([])
    vm_creation_option.set_dataVolume_systemTags([])
    vm = test_vm.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    test_util.test_pass('Create default VM/Volume Test Success')

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
