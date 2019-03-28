'''

New Integration Test for imagecache cleanup on primarystorate.

@author: Quarkonics
'''

import os
import time

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.primarystorage_operations as ps_ops
import zstackwoodpecker.zstack_test.zstack_test_image as zstack_image_header
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import apibinding.inventory as inventory

_config_ = {
        'timeout' : 600,
        'noparallel' : True
        }
test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    bs_cond = res_ops.gen_query_conditions("status", '=', "Connected")
    bss = res_ops.query_resource_fields(res_ops.BACKUP_STORAGE, bs_cond, \
            None, fields=['uuid'])
    if not bss:
        test_util.test_skip("not find available backup storage. Skip test")

    image_option = test_util.ImageOption()
    image_option.set_name('test_image_cache_cleanup')
    image_option.set_format('qcow2')
    image_option.set_mediaType('RootVolumeTemplate')
    image_option.set_url(os.environ.get('imageUrl_s'))
    image_option.set_backup_storage_uuid_list([bss[0].uuid])

    new_image = zstack_image_header.ZstackTestImage()
    new_image.set_creation_option(image_option)

    new_image.add_root_volume_template()

    l3_name = os.environ.get('l3VlanNetworkName1')
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid

    conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
    instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid
    conditions = res_ops.gen_query_conditions('state', '=', 'Enabled')
    conditions = res_ops.gen_query_conditions('status', '=', 'Connected', conditions)
    host_uuid = res_ops.query_resource(res_ops.HOST, conditions)[0].uuid
    vm_creation_option = test_util.VmOption()
    vm_creation_option.set_host_uuid(host_uuid)
    vm_creation_option.set_l3_uuids([l3_net_uuid])
    vm_creation_option.set_image_uuid(new_image.image.uuid)
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_name('test_image_cache_cleanup_vm1')
    vm = test_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()

    test_obj_dict.add_vm(vm)
    vm.check()
    host = test_lib.lib_find_host_by_vm(vm.get_vm())
    ps = test_lib.lib_get_primary_storage_by_vm(vm.get_vm())

    vm.destroy()
    vm.expunge()

    conditions = res_ops.gen_query_conditions('state', '=', 'Enabled')
    conditions = res_ops.gen_query_conditions('status', '=', 'Connected', conditions)
    conditions = res_ops.gen_query_conditions('uuid', '!=', host.uuid, conditions)
    host_uuid = res_ops.query_resource(res_ops.HOST, conditions)[0].uuid
    vm_creation_option.set_host_uuid(host_uuid)
    vm_creation_option.set_name('test_image_cache_cleanup_vm2')
    vm2 = test_vm_header.ZstackTestVm()
    vm2.set_creation_option(vm_creation_option)
    vm2.create()
    host2 = test_lib.lib_find_host_by_vm(vm2.get_vm())
    test_obj_dict.add_vm(vm2)
    disk_offering = test_lib.lib_get_disk_offering_by_name(os.environ.get('smallDiskOfferingName'))
    volume_creation_option = test_util.VolumeOption()
    volume_creation_option.set_disk_offering_uuid(disk_offering.uuid)
    volume1 = test_stub.create_volume(volume_creation_option)
    test_obj_dict.add_volume(volume1)
    volume1.attach(vm2)

    if ps.type == inventory.CEPH_PRIMARY_STORAGE_TYPE:
        test_util.test_skip('ceph is not directly using image cache, skip test.')

    if ps.type == "SharedBlock":
        path = "/dev/" + ps.uuid + '/' + new_image.image.uuid
        if not test_lib.lib_check_sharedblock_file_exist(host, path):
            test_util.test_fail('image cache is expected to exist')
    else:
        if ps.type == "AliyunNAS":
            image_cache_path = "%s/datas/imagecache/template/%s" % (ps.mountPath, new_image.image.uuid)
        else:
            image_cache_path = "%s/imagecache/template/%s" % (ps.mountPath, new_image.image.uuid)
        if not test_lib.lib_check_file_exist(host, image_cache_path):
            test_util.test_fail('image cache is expected to exist')
        if bss[0].type == inventory.IMAGE_STORE_BACKUP_STORAGE_TYPE:
            image_cache_path = "%s/zstore-cache/%s" % (ps.mountPath, new_image.image.uuid)
            if not test_lib.lib_check_file_exist(host, image_cache_path):
                test_util.test_fail('image cache is expected to exist') 

    new_image.delete()
    new_image.expunge()

    ps_ops.cleanup_imagecache_on_primary_storage(ps.uuid)
    if ps.type == inventory.LOCAL_STORAGE_TYPE:
        count = 0
        while True:
            image_cache_path = "%s/imagecache/template/%s/%s.qcow2" % (ps.mountPath, new_image.image.uuid, new_image.image.uuid)
            if not test_lib.lib_check_file_exist(host, image_cache_path):
                break
            elif count > 5:
                test_util.test_fail('image cache is expected to be deleted')
            test_util.test_logger('check %s times: image cache still exist' % (count))
            time.sleep(5)
            count += 1

    vm2.destroy()
    vm2.expunge()
    ps_ops.cleanup_imagecache_on_primary_storage(ps.uuid)    

    if ps.type == "SharedBlock":
        image_cache_path = "/dev/" + ps.uuid + '/' + new_image.image.uuid
        count = 0
        while True:
            if not test_lib.lib_check_sharedblock_file_exist(host, image_cache_path):
                break
            elif count > 5:
                test_util.test_fail('image cache is expected to be deleted')
            test_util.test_logger('check %s times: image cache still exist' % (count))
            time.sleep(10)
            count += 1
        test_util.test_pass('imagecache cleanup Pass.')

    if ps.type == "AliyunNAS":
        count = 0
        while True:
            image_cache_path = "%s/datas/imagecache/template/%s" % (ps.mountPath, new_image.image.uuid)
            if not test_lib.lib_check_file_exist(host, image_cache_path):
                break
            elif count > 5:
                test_util.test_fail('image cache is expected to be deleted')
            test_util.test_logger('check %s times: image cache still exist' % (count))
            time.sleep(5)
            count += 1

    count = 0
    while True:
        image_cache_path = "%s/imagecache/template/%s" % (ps.mountPath, new_image.image.uuid)
        if not test_lib.lib_check_file_exist(host, image_cache_path):
            break
        elif count > 5:
            test_util.test_fail('image cache is expected to be deleted')
        test_util.test_logger('check %s times: image cache still exist' % (count))
        time.sleep(5)
        count += 1
    
    count = 0
    while True:
        image_cache_path = "%s/zstore-cache/%s" % (ps.mountPath, new_image.image.uuid)
        if not test_lib.lib_check_file_exist(host, image_cache_path):
            break
        elif count > 5:
            test_util.test_fail('image cache is expected to be deleted')
        test_util.test_logger('check %s times: image cache still exist' % (count))
        time.sleep(5)
        count += 1

    test_util.test_pass('imagecache cleanup Pass.')

#Will be called only if exception happens in test().
def error_cleanup():
    pass
