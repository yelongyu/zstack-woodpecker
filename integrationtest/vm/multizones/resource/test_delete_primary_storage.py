'''

Delete Primary Storage will destroy VM and delete Volumes.

@author: Youyk
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.header.vm as vm_header
import zstackwoodpecker.header.volume as vol_header
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.export_operations as exp_ops
import zstackwoodpecker.operations.tag_operations as tag_ops
import zstackwoodpecker.operations.primarystorage_operations as ps_ops
import time
import os

_config_ = {
        'timeout' : 1200,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
ps_inv = None
tag = None

def recover_ps():
    global ps_inv
    ps_config = test_util.PrimaryStorageOption()

    ps_config.set_name(ps_inv.name)
    ps_config.set_description(ps_inv.description)
    ps_config.set_zone_uuid(ps_inv.zoneUuid)
    ps_config.set_type(ps_inv.type)
    ps_config.set_url(ps_inv.url)

    #avoid of ps is already created successfully. 
    cond = res_ops.gen_query_conditions('zoneUuid', '=', ps_inv.zoneUuid)
    cond = res_ops.gen_query_conditions('url', '=', ps_inv.url, cond)
    curr_ps = res_ops.query_resource(res_ops.PRIMARY_STORAGE, cond)
    if curr_ps:
        ps = curr_ps[0]
    else:
        ps = ps_ops.create_nfs_primary_storage(ps_config)

    for cluster_uuid in ps_inv.attachedClusterUuids:
        ps_ops.attach_primary_storage(ps.uuid, cluster_uuid)

def test():
    global ps_inv
    global tag
    curr_deploy_conf = exp_ops.export_zstack_deployment_config(test_lib.deploy_config)

    vm_creation_option = test_util.VmOption()
    image_name = os.environ.get('imageName_s')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    zone1_name = os.environ.get('zoneName1')
    zone1 = res_ops.get_resource(res_ops.ZONE, name = zone1_name)[0]
    #pick up primary storage 1 and set system tag for instance offering.
    ps_name1 = os.environ.get('nfsPrimaryStorageName1')
    ps_inv = res_ops.get_resource(res_ops.PRIMARY_STORAGE, name = ps_name1)[0]

    conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
    instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_name('multizones_vm_detach_ps')
    vm_creation_option.set_zone_uuid(zone1.uuid)

    tag = tag_ops.create_system_tag('InstanceOfferingVO', \
            instance_offering_uuid, \
            'primaryStorage::allocator::uuid::%s' % ps_inv.uuid)

    l3_name = os.environ.get('l3VlanNetworkName1')
    l3 = res_ops.get_resource(res_ops.L3_NETWORK, name = l3_name)[0]
    vm_creation_option.set_l3_uuids([l3.uuid])

    vm1 = test_lib.lib_create_vm(vm_creation_option)
    test_obj_dict.add_vm(vm1)

    volume1 = test_stub.create_volume()
    test_obj_dict.add_volume(volume1)
    volume1.attach(vm1)

    test_util.test_dsc("Delete Primary Storage")
    #need to delete tag as well
    tag_ops.delete_tag(tag.uuid)
    ps_ops.delete_primary_storage(ps_inv.uuid)

    test_obj_dict.mv_vm(vm1, vm_header.RUNNING, vm_header.DESTROYED)
    vm1.update()

    test_obj_dict.rm_volume(volume1)
    volume1.update()

    test_lib.lib_robot_status_check(test_obj_dict)

    test_util.test_dsc("Recover Primary Storage")
    recover_ps()
    test_lib.lib_robot_status_check(test_obj_dict)

    #update tag
    ps_inv = res_ops.get_resource(res_ops.PRIMARY_STORAGE, name = ps_name1)[0]

    tag = tag_ops.create_system_tag('InstanceOfferingVO', \
            instance_offering_uuid, \
            'primaryStorage::allocator::uuid::%s' % ps_inv.uuid)

    test_util.test_dsc("Create new VM and Volume")
    vm2 = test_lib.lib_create_vm(vm_creation_option)
    test_obj_dict.add_vm(vm2)

    volume2 = test_stub.create_volume()
    test_obj_dict.add_volume(volume2)
    volume2.attach(vm2)
    vm2.check()
    volume2.check()

    tag_ops.delete_tag(tag.uuid)
    test_lib.lib_robot_cleanup(test_obj_dict)
    test_util.test_pass('Test deleting primary storage Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global tag
    test_lib.lib_error_cleanup(test_obj_dict)
    try:
        tag_ops.delete_tag(tag.uuid)
    except:
        pass
    recover_ps()
