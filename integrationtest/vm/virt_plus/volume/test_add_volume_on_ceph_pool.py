'''

@author: quarkonics
'''
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.primarystorage_operations as ps_ops
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import os
import apibinding.inventory as inventory

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    test_util.test_dsc('Create Data Volume on ceph pool for VM Test')
    cond = res_ops.gen_query_conditions('type', '=', inventory.CEPH_PRIMARY_STORAGE_TYPE)
    ps = res_ops.query_resource_with_num(res_ops.PRIMARY_STORAGE, cond, limit = 1)
    if not ps:
        test_util.test_skip('skip test that ceph ps not found.' )
    ps = ps[0]

    vm = test_stub.create_vlan_vm()
    test_obj_dict.add_vm(vm)

    pool = ps_ops.add_ceph_primary_storage_pool(ps.uuid, 'woodpecker', isCreate=True)
    test_util.test_dsc('Create volume and check')
    disk_offering = test_lib.lib_get_disk_offering_by_name(os.environ.get('rootDiskOfferingName'))
    volume_creation_option = test_util.VolumeOption()
    volume_creation_option.set_primary_storage_uuid(ps.uuid)
    volume_creation_option.set_disk_offering_uuid(disk_offering.uuid)
    volume_creation_option.set_system_tags(['ceph::pool::woodpecker'])

    volume = test_stub.create_volume(volume_creation_option)
    test_obj_dict.add_volume(volume)
    volume.check()

    test_util.test_dsc('Attach volume and check')
    #mv vm checker later, to save some time.
    vm.check()
    volume.attach(vm)
    volume.check()
    if volume.get_volume().installPath.find('woodpecker') < 0:
        test_util.test_fail('data volume is expected to create on pool woodpecker, while its %s.' % (volume.get_volume().installPath))

    test_util.test_dsc('Detach volume and check')
    volume.detach()
    volume.check()

    test_util.test_dsc('Delete volume and check')
    volume.delete()
    volume.check()
    test_obj_dict.rm_volume(volume)

    ps_ops.delete_ceph_primary_storage_pool(pool.uuid)
    vm.destroy()
    vm.check()
    test_util.test_pass('Create Data Volume on ceph pool for VM Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
