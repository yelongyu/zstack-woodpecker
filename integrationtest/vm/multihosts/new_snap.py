import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.datamigrate_operations as datamigr_ops
import zstackwoodpecker.action_select as action_select
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.header.vm as vm_header
import zstackwoodpecker.test_state as ts_header
import zstackwoodpecker.zstack_test.snap as robot_snapshot_header
import zstackwoodpecker.zstack_test.zstack_test_volume as volume_header
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.test_dict as test_dict
import zstackwoodpecker.robot_action as Robot
import os
import time

_config_ = {
    'timeout': 7200,
    'noparallel': True
}

test_lib.Robot = True
test_dict = test_dict.Test_Dict()
TestAction = ts_header.TestAction

case_flavor = test_util.load_paths(os.path.join(os.path.dirname(__file__), "templates"),
                                   os.path.join(os.path.dirname(__file__), "paths"))


def test():
    test_util.test_dsc('''Will mainly doing random test for all kinds of snapshot operations. VM, Volume and Image operations will also be tested. If reach 1 hour successful running condition, testing will success and quit.  SG actions, and VIP actions are removed in this robot test.
            VM resources: a special Utility vm is required to do volume attach/detach operation. 
            ''')
    test_util.test_dsc('Constant Path Test Begin.')

    robot_test_obj = Robot.robot()
    flavor = case_flavor[os.environ.get('CASE_FLAVOR')]
    initial_formation = flavor['initial_formation']
    path_list = flavor['path_list']

    # robot_test_obj.set_initial_formation(initial_formation)
    # robot_test_obj.set_path_list(path_list)

    robot_test_obj.initial(path_list, initial_formation)
    Robot.robot_run_constant_path(robot_test_obj, set_robot=True)


#     # create_utility on all ps
#     test_lib.lib_robot_create_utility_vm()
#
#     # find image
#     cond = res_ops.gen_query_conditions('name', '=', 'ttylinux')
#     cond = res_ops.gen_query_conditions('state', '=', "Enabled", cond)
#     cond = res_ops.gen_query_conditions('status', '=', "Ready", cond)
#     image = res_ops.query_resource(res_ops.IMAGE, cond)[0]
#
#     # find ps
#     cond = res_ops.gen_query_conditions('name', '=', 'ceph-ps')
#     ps = res_ops.query_resource(res_ops.PRIMARY_STORAGE, cond)[0]
#
#     # find l3
#     l3 = test_lib.lib_get_l3_by_name(os.environ.get('l3VlanNetworkName1'))
#
#     # create target vm
#     vm_create_option = test_util.VmOption()
#
#
#     vm_create_option.set_name('vm1')
#     vm_create_option.set_image_uuid(image.uuid)
#     vm_create_option.set_ps_uuid(ps.uuid)
#     vm_create_option.set_l3_uuids([l3.uuid])
#
#     vm = test_lib.lib_create_vm(vm_create_option)
#     root_volume = volume_header.ZstackTestVolume()
#     root_volume.create_from(vm.allVolumes[0].uuid)
#     root_snap_tree = robot_snapshot_header.ZstackSnapshotTree(root_volume)
#     root_snap_tree.update()
#     vm.check()
#
#     # create target volume
#     volume_creation_option = test_util.VolumeOption()
#     volume_creation_option.set_name("volume1")
#     volume_creation_option.set_primary_storage_uuid(ps.uuid)
#     systemtags = [].append("capability::virtio-scsi")
#     volume_creation_option.set_system_tags(systemtags)
#     test_volume = test_lib.lib_create_volume_from_offering(volume_creation_option)
#
#     # create snapshot tree
#     snap_tree = robot_snapshot_header.ZstackSnapshotTree(test_volume)
#     snap_tree.update()
#
#     snapshot1 = snap_tree.create_snapshot('snapshot1')
#     test_util.test_logger(snap_tree.get_checking_points())
#     test_util.test_logger(snap_tree.get_snapshot_list())
#
#     snapshot2 = snap_tree.create_snapshot('snapshot2')
#     test_util.test_logger(snap_tree.get_checking_points())
#     test_util.test_logger(snap_tree.get_snapshot_list())
#
#     snapshot3 = snap_tree.create_snapshot('snapshot3')
#     test_util.test_logger(snap_tree.get_checking_points())
#     test_util.test_logger(snap_tree.get_snapshot_list())
#
#     snapshot4 = snap_tree.create_snapshot('snapshot4')
#     test_util.test_logger(snap_tree.get_checking_points())
#     test_util.test_logger(snap_tree.get_snapshot_list())
#
#     snapshot5 = snap_tree.create_snapshot('snapshot5')
#     test_util.test_logger(snap_tree.get_checking_points())
#     test_util.test_logger(snap_tree.get_snapshot_list())
#
#     snapshot6 = snap_tree.create_snapshot('snapshot6')
#     test_util.test_logger(snap_tree.get_checking_points())
#     test_util.test_logger(snap_tree.get_snapshot_list())
#
#     snap_tree.use(snapshot2)
#     test_util.test_logger(snap_tree.get_checking_points())
#     test_util.test_logger(snap_tree.get_snapshot_list())
#
#     snapshot7 = snap_tree.create_snapshot("snapshot7")
#     test_util.test_logger(snap_tree.get_checking_points())
#     test_util.test_logger(snap_tree.get_snapshot_list())
#
#     snap_tree.delete(snapshot2)
#     test_util.test_logger(snap_tree.get_checking_points())
#     test_util.test_logger(snap_tree.get_snapshot_list())
#
#     vol_ops.batch_delete_snapshot([snapshot1.get_snapshot().uuid, snapshot3.get_snapshot().uuid])
#     snap_tree.batch_delete_snapshots([snapshot1, snapshot3])
#     test_util.test_logger(snap_tree.get_checking_points())
#     test_util.test_logger(snap_tree.get_snapshot_list())
#
#     volume_from_snapshot7 = snapshot7.create_data_volume()
#
#     for head in snap_tree.heads:
#         test_util.test_logger(head.get_all_child_list())
#         test_util.test_logger(head.get_children_tree_list())
#     test_volume.attach(vm)
#
#
#     delta = 5 * 1024 * 1024
#
#     # resize_data_volume
#     current_size = test_volume.get_volume().size
#     new_size = current_size + int(delta)
#     test_volume.resize(new_size)
#     test_volume.update()
#     test_volume.update_volume()
#     snap_tree.update()
#
#     # Todo:resize_root_volume
#     root_volume_uuid = root_volume.get_volume().uuid
#     current_size = root_volume.get_volume().size
#     new_size = current_size + int(delta)
#     vol_ops.resize_volume(root_volume_uuid, new_size)
#     root_snap_tree.update()
#
#     # Todo:clone_vm with no volume
#     clone_vm = vm.clone(name="clone_vm")
#     root_snap_tree.update()
#
#
#     # Todo:clone_vm with all volume
#     clone_vm = vm.clone(name="clone_vm", full=True)
#     for i in vm.get_test_volumes():
#         i.snapshot_tree.update()
#
#     # Todo:reinit_vm
#     vm.reinit()
#     for i in vm.get_test_volumes():
#         i.snapshot_tree.update()
#
#     # Todo:create_image/template
#     new_image = test_lib.lib_create_template_from_volume(root_volume.get_volume().uuid)
#     img_ops.update_image(new_image.get_image().uuid, "add_images", None)
#     for i in vm.get_test_volumes():
#         i.snapshot_tree.update()
#
#     new_data_vol_temp = test_lib.lib_create_data_vol_template_from_volume(None, test_volume.get_volume())
#     img_ops.update_image(new_data_vol_temp.get_image().uuid, "add_template", None)
#     snap_tree.update()
#
#     # Todo:ps_migrate_vm/root_volume/volume
#     target_pss = datamigr_ops.get_ps_candidate_for_vol_migration(test_volume.get_volume().uuid)
#     datamigr_ops.ps_migrage_volume(target_pss[0].uuid, test_volume.get_volume().uuid)
#     snap_tree.update()
#
#     target_pss = datamigr_ops.get_ps_candidate_for_vol_migration(root_volume.get_volume().uuid)
#     datamigr_ops.ps_migrage_volume(target_pss[0].uuid, root_volume.get_volume().uuid)
#     for i in vm.get_test_volumes():
#         i.snapshot_tree.update()
#
#     # Todo:create_backup volume/root_volume/vm with volume
#     cond = res_ops.gen_query_conditions("type", '=', "ImageStoreBackupStorage")
#     cond = res_ops.gen_query_conditions("name", '=', "imagestore1", cond)
#     bs = res_ops.query_resource(res_ops.BACKUP_STORAGE, cond)[0]
#
#     backup_option = test_util.BackupOption()
#     backup_option.set_name("backup1")
#     backup_option.set_volume_uuid(test_volume.get_volume().uuid)
#     backup_option.set_backupStorage_uuid(bs.uuid)
#     vol_backup1 = vol_ops.create_backup(backup_option)
#
#     backup_option.set_name("backup1")
#     backup_option.set_volume_uuid(root_volume.get_volume().uuid)
#     root_volume_backup2 = vol_ops.create_backup(backup_option)
#
#
#     backup_option.set_name("backup_vm1")
#     vm_backup1 = vm_ops.create_vm_backup(backup_option)
#
#
#
#
#
#
# # Todo:snap_tree.check


def error_cleanup():
    # test_lib.lib_robot_cleanup(test_dict)
    pass
