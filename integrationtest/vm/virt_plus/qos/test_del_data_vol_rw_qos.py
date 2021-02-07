'''
This case can not execute parallelly
@author: Legion 
'''
import os
import time
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.volume_operations as vol_ops

_config_ = {
        'timeout' : 1000,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
volume_offering_uuid = None

def test():
    global volume_offering_uuid
    test_util.test_dsc('Test VM disk bandwidth QoS by 20MB')

    #unit is KB
    read_bandwidth = 10*1024*1024
    write_bandwidth = 5*1024*1024
    new_volume_offering = test_lib.lib_create_disk_offering(read_bandwidth=read_bandwidth, write_bandwidth=write_bandwidth)

    volume_offering_uuid = new_volume_offering.uuid

    vm = test_stub.create_vm(vm_name = 'vm_volume_qos', disk_offering_uuids = [volume_offering_uuid])
    vm.check()
    test_obj_dict.add_vm(vm)
    vm_inv = vm.get_vm()
    cond = res_ops.gen_query_conditions("vmInstanceUuid", '=', vm_inv.uuid)
    cond = res_ops.gen_query_conditions("type", '=', 'Data', cond)
    volume_uuid = res_ops.query_resource(res_ops.VOLUME, cond)[0].uuid
    test_lib.lib_wait_target_up(vm_inv.ip, '22', 120)
    test_lib.lib_mkfs_for_volume(volume_uuid, vm_inv)
    time.sleep(10)
    path = '/mnt'
    user_name = 'root'
    user_password = 'password'
    os.system("sshpass -p '%s' ssh %s@%s 'mount /dev/vdb1 %s'"%(user_password, user_name, vm_inv.vmNics[0].ip, path))
    test_stub.make_ssh_no_password(vm_inv)
    test_stub.install_fio(vm_inv)
    vm_ops.set_vm_disk_qos(test_lib.lib_get_data_volumes(vm_inv)[0].uuid, read_bandwidth*2)
    if vm_ops.get_vm_disk_qos(test_lib.lib_get_data_volumes(vm_inv)[0].uuid).volumeBandwidth != read_bandwidth*2:
        test_util.test_fail('Retrieved disk qos not match')
    if vm_ops.get_vm_disk_qos(test_lib.lib_get_data_volumes(vm_inv)[0].uuid).volumeBandwidthRead == read_bandwidth:
        test_util.test_fail('read qos must be cleared after set total qos')
    if vm_ops.get_vm_disk_qos(test_lib.lib_get_data_volumes(vm_inv)[0].uuid).volumeBandwidthWrite == write_bandwidth:
        test_util.test_fail('write qos must be cleared after set total qos')
#     test_stub.test_fio_bandwidth(vm_inv, read_bandwidth, '/dev/vdb')
    # check read bw
    vm_ops.set_vm_disk_qos(test_lib.lib_get_data_volumes(vm_inv)[0].uuid, read_bandwidth*2, 'read')
    if vm_ops.get_vm_disk_qos(test_lib.lib_get_data_volumes(vm_inv)[0].uuid).volumeBandwidthRead != read_bandwidth*2:
        test_util.test_fail('Retrieved disk qos not match')

    test_stub.test_fio_bandwidth(vm_inv, read_bandwidth*2, '/dev/vdb')
    vm_ops.del_vm_disk_qos(test_lib.lib_get_data_volumes(vm_inv)[0].uuid, mode='all')
    if test_stub.test_fio_bandwidth(vm_inv, read_bandwidth, '/dev/vdb', raise_exception=False):
        test_util.test_fail('disk qos is not expected to have limit after qos setting is deleted')

    # check write bw
    vm_ops.set_vm_disk_qos(test_lib.lib_get_data_volumes(vm_inv)[0].uuid, write_bandwidth*2, 'write')
    if vm_ops.get_vm_disk_qos(test_lib.lib_get_data_volumes(vm_inv)[0].uuid).volumeBandwidthWrite != write_bandwidth*2:
        test_util.test_fail('Retrieved disk qos not match')

    test_stub.test_fio_bandwidth(vm_inv, write_bandwidth*2, path)
    vm_ops.del_vm_disk_qos(test_lib.lib_get_data_volumes(vm_inv)[0].uuid, mode='all')
    if test_stub.test_fio_bandwidth(vm_inv, write_bandwidth, path, raise_exception=False):
        test_util.test_fail('disk qos is not expected to have limit after qos setting is deleted')

    vol_ops.delete_disk_offering(volume_offering_uuid)
    test_lib.lib_robot_cleanup(test_obj_dict)

    test_util.test_pass('VM data volume QoS Test Pass')

#Will be called only if exception happens in test().
def error_cleanup():
    global volume_offering_uuid
    test_lib.lib_error_cleanup(test_obj_dict)
    try:
        vol_ops.delete_disk_offering(volume_offering_uuid)
    except:
        pass
