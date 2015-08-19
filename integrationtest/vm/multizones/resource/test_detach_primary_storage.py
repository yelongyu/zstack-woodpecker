'''

Detach Primary Storage will stop related VM 

@author: Youyk
'''
import time
import os
import apibinding.inventory as inventory
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.header.vm as vm_header
import zstackwoodpecker.header.volume as vol_header
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.export_operations as exp_ops
import zstackwoodpecker.operations.tag_operations as tag_ops
import zstackwoodpecker.operations.primarystorage_operations as ps_ops

_config_ = {
        'timeout' : 1200,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
tag = None
ps_uuid = None
cluster_uuid = None

def test():
    global ps_uuid
    global cluster_uuid
    global tag
    curr_deploy_conf = exp_ops.export_zstack_deployment_config(test_lib.deploy_config)

    vm_creation_option = test_util.VmOption()
    image_name = os.environ.get('imageName_net')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    cluster1_name = os.environ.get('clusterName1')
    cluster1 = res_ops.get_resource(res_ops.CLUSTER, name = cluster1_name)[0]
    #pick up primary storage 1 and set system tag for instance offering.
    zone_name = os.environ.get('zoneName1')
    zone_uuid = res_ops.get_resource(res_ops.ZONE, name = zone_name)[0].uuid
    cond = res_ops.gen_query_conditions('zoneUuid', '=', zone_uuid)
    ps_inv = res_ops.query_resource(res_ops.PRIMARY_STORAGE, cond)[0]
    if ps_inv.type == inventory.NFS_PRIMARY_STORAGE_TYPE:
        ps_name1 = os.environ.get('nfsPrimaryStorageName1')
    elif ps_inv.type == inventory.CEPH_PRIMARY_STORAGE_TYPE:
        ps_name1 = os.environ.get('cephPrimaryStorageName1')
    ps_inv = res_ops.get_resource(res_ops.PRIMARY_STORAGE, name = ps_name1)[0]
    ps_uuid = ps_inv.uuid
    cluster_uuid = cluster1.uuid

    conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
    instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, \
            conditions)[0].uuid
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_name('multizones_vm_detach_ps')
    vm_creation_option.set_cluster_uuid(cluster_uuid)

    tag = tag_ops.create_system_tag('InstanceOfferingVO', \
            instance_offering_uuid, \
            'primaryStorage::allocator::uuid::%s' % ps_uuid)

    l3_name = os.environ.get('l3VlanNetworkName1')
    l3 = res_ops.get_resource(res_ops.L3_NETWORK, name = l3_name)[0]
    vm_creation_option.set_l3_uuids([l3.uuid])

    vm1 = test_lib.lib_create_vm(vm_creation_option)
    test_obj_dict.add_vm(vm1)

    vm2 = test_lib.lib_create_vm(vm_creation_option)
    test_obj_dict.add_vm(vm2)

    volume1 = test_stub.create_volume()
    test_obj_dict.add_volume(volume1)
    volume1.attach(vm1)

    test_util.test_dsc("Detach Primary Storage")
    ps_ops.detach_primary_storage(ps_uuid, cluster_uuid)

    test_obj_dict.mv_vm(vm1, vm_header.RUNNING, vm_header.STOPPED)
    test_obj_dict.mv_vm(vm2, vm_header.RUNNING, vm_header.STOPPED)
    vm1.update()
    vm1.set_state(vm_header.STOPPED)
    vm2.update()
    vm2.set_state(vm_header.STOPPED)

    vm1.check()
    vm2.check()

    test_util.test_dsc("Attach Primary Storage")
    ps_ops.attach_primary_storage(ps_uuid, cluster_uuid)
    vm1.start()
    vm2.start()

    vm3 = test_lib.lib_create_vm(vm_creation_option)
    test_obj_dict.add_vm(vm3)

    vm1.check()
    volume1.check()
    vm2.check()
    vm3.check()

    test_util.test_dsc("Delete new added tag")
    tag_ops.delete_tag(tag.uuid)

    test_lib.lib_robot_cleanup(test_obj_dict)
    test_util.test_pass('Test detaching primary storage Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global tag
    global ps_uuid
    global cluster_uuid
    try:
        ps_ops.attach_primary_storage(ps_uuid, cluster_uuid)
    except:
        pass

    test_lib.lib_error_cleanup(test_obj_dict)
    try:
        tag_ops.delete_tag(tag.uuid)
    except:
        pass
