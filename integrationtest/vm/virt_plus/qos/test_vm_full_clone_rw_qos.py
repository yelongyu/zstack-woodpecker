'''
This case can not execute parallelly
@author: Legion
'''
import os
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import apibinding.inventory as inventory

_config_ = {
        'timeout' : 1000,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
volume_offering_uuid = None
new_offering_uuid = None

def test():
    global volume_offering_uuid, new_offering_uuid
    test_util.test_dsc('Test VM data volume bandwidth QoS by 20MB')

    # Only imagestore supports full clone
    bs = res_ops.query_resource(res_ops.BACKUP_STORAGE)
    for i in bs:
        if i.type == inventory.IMAGE_STORE_BACKUP_STORAGE_TYPE:
            break
    else:
        test_util.test_skip('Skip test on non-imagestore')

    # SharedBlock and AliyunNAS not support full clone
    ps = res_ops.query_resource(res_ops.PRIMARY_STORAGE)
    for i in ps:
        if i.type in ['SharedBlock', 'AliyunNAS']:
            test_util.test_skip('Skip test on SharedBlock and AliyunNAS PS')

    #unit is KB
    write_bandwidth = 5*1024*1024
    read_bandwidth = 10*1024*1024
    new_offering = test_lib.lib_create_instance_offering(read_bandwidth=read_bandwidth, write_bandwidth=write_bandwidth)
    new_offering_uuid = new_offering.uuid
    new_volume_offering = test_lib.lib_create_disk_offering(read_bandwidth=read_bandwidth, write_bandwidth=write_bandwidth)
    volume_offering_uuid = new_volume_offering.uuid

    vm = test_stub.create_vm(vm_name='vm_volume_qos', disk_offering_uuids = [volume_offering_uuid])
    test_obj_dict.add_vm(vm)
    vm_inv = vm.get_vm()
    cond = res_ops.gen_query_conditions("vmInstanceUuid", '=', vm_inv.uuid) 
    cond = res_ops.gen_query_conditions("type", '=', 'Data', cond)
    volume_uuid = res_ops.query_resource(res_ops.VOLUME, cond)[0].uuid
    test_lib.lib_mkfs_for_volume(volume_uuid, vm_inv)
    path = '/mnt'
    user_name = 'root'
    user_password = 'password'
    os.system("sshpass -p '%s' ssh %s@%s 'mount /dev/vdb1 %s'"%(user_password, user_name, vm_inv.vmNics[0].ip, path))
    vm.check()
    test_stub.make_ssh_no_password(vm_inv)
    test_stub.install_fio(vm_inv)

    vm_ops.set_vm_disk_qos(test_lib.lib_get_data_volumes(vm_inv)[0].uuid, read_bandwidth*2, 'read')
    vm_ops.set_vm_disk_qos(test_lib.lib_get_root_volume(vm_inv).uuid, read_bandwidth*2, 'read')

    vm_ops.set_vm_disk_qos(test_lib.lib_get_data_volumes(vm_inv)[0].uuid, write_bandwidth*2, 'write')
    vm_ops.set_vm_disk_qos(test_lib.lib_get_root_volume(vm_inv).uuid, write_bandwidth*2, 'write')

    new_vm = vm.clone(['full_cloned_vm'], full=True)[0]
    new_vm.check()
    test_obj_dict.add_vm(new_vm)

    volumes_number = len(test_lib.lib_get_all_volumes(new_vm.vm))
    if volumes_number != 2:
        test_util.test_fail('Did not find 2 volumes for [vm:] %s. But we assigned 2 data volume when create the vm. We only catch %s volumes' % (new_vm.vm.uuid, volumes_number))
    else:
        test_util.test_logger('Find 2 volumes for [vm:] %s.' % new_vm.vm.uuid)

    new_vm_inv = new_vm.get_vm()

    if vm_ops.get_vm_disk_qos(test_lib.lib_get_data_volumes(new_vm_inv)[0].uuid).volumeBandwidthRead != read_bandwidth*2 and \
    vm_ops.get_vm_disk_qos(test_lib.lib_get_data_volumes(new_vm_inv)[0].uuid).volumeBandwidthWrite != write_bandwidth*2:
        test_util.test_fail('Retrieved disk qos not match')

    test_stub.test_fio_bandwidth(new_vm_inv, read_bandwidth, '/dev/vda')
    test_stub.test_fio_bandwidth(new_vm_inv, read_bandwidth, '/dev/vdb')

    vol_ops.delete_disk_offering(volume_offering_uuid)
    vol_ops.delete_disk_offering(volume_offering_uuid)
    test_lib.lib_robot_cleanup(test_obj_dict)

    test_util.test_pass('VM data volume read QoS Test Pass')

#Will be called only if exception happens in test().
def error_cleanup():
    global volume_offering_uuid, new_offering_uuid
    test_lib.lib_error_cleanup(test_obj_dict)
    try:
        vol_ops.delete_disk_offering(volume_offering_uuid)
        vol_ops.delete_disk_offering(volume_offering_uuid)
    except:
        pass
