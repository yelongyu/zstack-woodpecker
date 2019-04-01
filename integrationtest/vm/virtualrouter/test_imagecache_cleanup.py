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

    bs = res_ops.query_resource(res_ops.BACKUP_STORAGE)
    for i in bs:
        if i.type == 'AliyunEBS':
            test_util.test_skip('Skip test on AliyunEBS backup storage')

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

    vm = test_stub.create_vm([l3_net_uuid], new_image.image.uuid, 'imagecache_vm', \
            default_l3_uuid = l3_net_uuid)
    test_obj_dict.add_vm(vm)
    vm.check()
    host = test_lib.lib_find_host_by_vm(vm.get_vm())
    ps = test_lib.lib_get_primary_storage_by_vm(vm.get_vm())
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

    vm.destroy()
    if test_lib.lib_get_vm_delete_policy() != 'Direct':
        vm.expunge()

    new_image.delete()
    if test_lib.lib_get_image_delete_policy() != 'Direct':
        new_image.expunge()

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
            time.sleep(5)
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
