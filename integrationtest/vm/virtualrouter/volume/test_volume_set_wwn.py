'''
New Integration Test for setting Data Volume WWN.
@author: Mirabel
'''
import os
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.tag_operations as tag_ops

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    test_util.test_dsc('Test Set Data Volume WWN')
    vm1=test_stub.create_basic_vm()
    vm2=test_stub.create_basic_vm()
    vm1.check()
    vm2.check()
    test_obj_dict.add_vm(vm1)
    test_obj_dict.add_vm(vm2)

    volume1 = test_stub.create_volume()
    tag_ops.create_system_tag('VolumeVO',volume1.get_volume().uuid,"capability::virtio-scsi")
    volume2 = test_stub.create_volume()
    tag_ops.create_system_tag('VolumeVO',volume2.get_volume().uuid,"capability::virtio-scsi")
    test_obj_dict.add_volume(volume1)
    test_obj_dict.add_volume(volume2)
    vm1_inv = vm1.get_vm()
    vm2_inv = vm2.get_vm()
    mount_point_1 = '/tmp/zstack/test1'
    mount_point_2 = '/tmp/zstack/test2'
    test_lib.lib_mkfs_for_volume(volume1.get_volume().uuid, vm1_inv)
    test_stub.attach_mount_volume(volume1, vm1, mount_point_1)
    test_lib.lib_mkfs_for_volume(volume2.get_volume().uuid, vm1_inv)
    test_stub.attach_mount_volume(volume2, vm1, mount_point_2)
    wwn_dev_cmd=" ls /dev/disk/by-id -la | awk '$9~/^wwn-.*-part1/ {print $9,$11}'"
    wwn_dev_list=test_lib.lib_execute_command_in_vm(vm1_inv,wwn_dev_cmd)
    if not wwn_dev_list or wwn_dev_list == "<no stdout output>":
        test_util.test_fail('vm [%s] cannot show data volume wwn '%(vm1.get_vm().uuid))

    for wwn_dev in wwn_dev_list.strip().split('\n'):
        wwn = wwn_dev.split()[0]
        device = wwn_dev.split()[1].split('/')[-1]
        path_cmd = "mount | awk '/^\/dev\/"+device+"/ {print $3}'"
        mount_point = test_lib.lib_execute_command_in_vm(vm1_inv, path_cmd).strip()
        test_stub.create_test_file(vm1_inv,mount_point+'/'+wwn)
        test_lib.lib_execute_command_in_vm(vm1_inv, 'umount '+mount_point+' >/dev/null')
    volume1.detach()
    volume2.detach()

    wwn_cmd="ls /dev/disk/by-id -la | awk '$9~/^wwn-.*-part1/ {print $9}'"

    test_stub.attach_mount_volume(volume1, vm2, mount_point_1)
    set_wwn_1 = test_lib.lib_execute_command_in_vm(vm2_inv, wwn_cmd).strip()
    check_file_cmd = "ls "+mount_point_1
    file_list = test_lib.lib_execute_command_in_vm(vm2_inv, check_file_cmd)
    if set_wwn_1 not in file_list.split():
        test_util.test_fail('wwn [%s] file does not exist in wwn [%s] volume' % (set_wwn_1, set_wwn_1))
    wwn_1 = set_wwn_1.split('-')[1]
    cond = res_ops.gen_query_conditions('resourceUuid', '=', volume1.get_volume().uuid)
    cond = res_ops.gen_query_conditions('tag','=','kvm::volume::%s' % (wwn_1),cond)
    volume1_tag_invs = res_ops.query_resource(res_ops.SYSTEM_TAG, cond)
    if not volume1_tag_invs:
        cond = res_ops.gen_query_conditions('resourceUuid', '=', volume1.get_volume().uuid)
        volume1_tag_invs = res_ops.query_resource(res_ops.SYSTEM_TAG, cond)
	for tag_inv in volume1_tag_invs:
            if tag_inv.tag.startswith("kvm::volume::"):
                volume1_tag = tag_inv.tag.split("::")[2]
                test_util.test_fail('data volume [%s] with tag [%s] does not match its wwn number [%s] in vm' % (volume2.get_volume().uuid,volume1_tag, wwn_1))
                break
    volume1.detach()

    test_stub.attach_mount_volume(volume2, vm2, mount_point_2)
    set_wwn_2 = test_lib.lib_execute_command_in_vm(vm2_inv, wwn_cmd).strip()
    check_file_cmd = "ls "+mount_point_2
    file_list = test_lib.lib_execute_command_in_vm(vm2_inv, check_file_cmd)
    if set_wwn_2 not in file_list.split():
        test_util.test_fail('wwn [%s] file does not exist in wwn [%s] volume' % (set_wwn_2, set_wwn_2))
    wwn_2 = set_wwn_2.split('-')[1]
    cond = res_ops.gen_query_conditions('resourceUuid', '=', volume2.get_volume().uuid)
    cond = res_ops.gen_query_conditions('tag','=','kvm::volume::%s'%(wwn_2),cond)
    volume2_tag_invs = res_ops.query_resource(res_ops.SYSTEM_TAG, cond)
    if not volume2_tag_invs:
        cond = res_ops.gen_query_conditions('resourceUuid', '=', volume2.get_volume().uuid)
        volume2_tag_invs = res_ops.query_resource(res_ops.SYSTEM_TAG, cond)
	for tag_inv in volume2_tag_invs:
            if tag_inv.tag.startswith("kvm::volume::"):
                volume2_tag = tag_inv.tag.split("::")[2]
                test_util.test_fail('data volume [%s] with tag [%s] does not match its wwn number [%s] in vm' % (volume2.get_volume().uuid,volume2_tag, wwn_2))
                break
    volume2.detach()

    test_lib.lib_robot_cleanup(test_obj_dict)

    test_util.test_pass('Set Data Volume WWN Test Pass')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
