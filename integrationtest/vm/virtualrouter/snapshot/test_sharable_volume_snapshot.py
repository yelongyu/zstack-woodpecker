'''

Test sharable volume snapshot 

@author:guocan
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.zstack_test.zstack_test_snapshot as zstack_sp_header
import zstackwoodpecker.zstack_test.zstack_test_volume as zstack_vol_header
import zstackwoodpecker.zstack_test.zstack_test_image as zstack_img_header
import zstackwoodpecker.header.volume as vol_header
import apibinding.inventory as inventory

import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

case_flavor = dict(online = dict(vm_running=True, vm_stopped=False),
                   offline = dict(vm_running=False, vm_stopped=True),
                   )

def test():
    allow_ps_list = [inventory.CEPH_PRIMARY_STORAGE_TYPE, "SharedBlock"]
    test_lib.skip_test_when_ps_type_not_in_list(allow_ps_list)
    flavor = case_flavor[os.environ.get('CASE_FLAVOR')]
    test_util.test_dsc('Create original vm')
    vm = test_stub.create_vlan_vm()
    test_obj_dict.add_vm(vm)
    vm1 = test_stub.create_vlan_vm()
    test_obj_dict.add_vm(vm1)
    
    test_util.test_dsc('Create Sharable Data Volume obj.')
    disk_offering = test_lib.lib_get_disk_offering_by_name(os.environ.get('smallDiskOfferingName'))
    volume_creation_option = test_util.VolumeOption()
    volume_creation_option.set_name('sharable volume')
    volume_creation_option.set_disk_offering_uuid(disk_offering.uuid)
    volume_creation_option.set_system_tags(['ephemeral::shareable', 'capability::virtio-scsi'])
    volume = test_stub.create_volume(volume_creation_option)
    test_obj_dict.add_volume(volume)

    volume.attach(vm)
    if flavor['vm_running'] == False:
        vm.stop()
        test_lib.lib_wait_target_down(vm.get_vm().vmNics[0].ip, 22)
    if flavor['vm_running'] == True:
        allow_ps_list = [inventory.CEPH_PRIMARY_STORAGE_TYPE]
        test_lib.skip_test_when_ps_type_not_in_list(allow_ps_list)

    test_util.test_dsc('create data volume snapshot')
    snapshots_data = test_obj_dict.get_volume_snapshot(volume.get_volume().uuid)
    snapshots_data.set_utility_vm(vm1)
    snapshots_data.create_snapshot('create_data_snapshot1')
    snapshots_data.check()
    snapshot1 = snapshots_data.get_current_snapshot()
    snapshots_data.create_snapshot('create_data_snapshot2')
    snapshots_data.check()

    #check data snapshots
    if flavor['vm_running'] == True:
        vm.stop()
        test_lib.lib_wait_target_down(vm.get_vm().vmNics[0].ip, 22)
        snapshots_data.use_snapshot(snapshot1)
        snapshots_data.check()
        vm.start()
        test_lib.lib_wait_target_up(vm.get_vm().vmNics[0].ip, 22)
    else:
        snapshots_data.use_snapshot(snapshot1)
        snapshots_data.check()
    snapshots_data.create_snapshot('create_snapshot1.1.1')
    snapshot2 = snapshots_data.get_current_snapshot()
    snapshots_data.check()
    snapshots_data.create_snapshot('create_snapshot1.2.1')
    snapshots_data.check()
    snapshots_data.delete_snapshot(snapshot2)
    snapshots_data.check()
    #check delete snapshot1
    sp = snapshots_data.get_current_snapshot()
    snapshots_data.delete_snapshot(snapshot1)
    snapshots_data.check()
    if flavor['vm_running'] == False:
        vm.start()
        test_lib.lib_wait_target_up(vm.get_vm().vmNics[0].ip, 22)
    import tempfile
    with tempfile.NamedTemporaryFile() as script:
        script.write('''
device=/dev/`ls -ltr --file-type /dev | awk '$4~/disk/ {print $NF}' | grep -v '[[:digit:]]' | tail -1`1
mkdir -p %s >/dev/null
mount $device %s >/dev/null
mkdir -p %s >/dev/null
checking_result=''
ls %s
umount %s >/dev/null
            ''' % (test_lib.WOODPECKER_MOUNT_POINT, \
                    test_lib.WOODPECKER_MOUNT_POINT, \
                    zstack_sp_header.checking_point_folder, \
                    zstack_sp_header.checking_point_folder, \
                    test_lib.WOODPECKER_MOUNT_POINT))
        script.flush()
        rsp = test_lib.lib_execute_shell_script_in_vm(vm.get_vm(), script.name)
    if rsp:
        result_list = rsp.result.split()
        temp_checking_list = list(result_list)

        if len(temp_checking_list) == 3:
            test_util.test_logger('Checker result: snapshot: %s integrity checking pass' % sp.get_snapshot().uuid)
        else:
            test_util.test_fail('Checker fail.')
    else:
        test_util.test_fail('Cmd fail.')

    test_lib.lib_robot_cleanup(test_obj_dict)
    test_util.test_pass('Test sharable volume snapshot success.')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
