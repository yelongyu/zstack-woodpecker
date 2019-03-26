import zstackwoodpecker.header.snapshot as sp_header
import zstackwoodpecker.header.vm as vm_header
import zstackwoodpecker.header.volume as volume_header
import zstackwoodpecker.header.image as image_header
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.operations.config_operations as conf_ops
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.zstack_test.zstack_test_volume as zstack_volume_header
import zstackwoodpecker.zstack_test.zstack_test_image as zstack_image_header

import uuid
import os

checking_point_folder = '%s/checking_point' % test_lib.WOODPECKER_MOUNT_POINT


class ZstackSnapshot(sp_header.TestSnapshot):
    def __init__(self):
        '''
        self.snapshot
        self.in_use
        self.state
        self.target_volume
        self.volume_type
        '''
        self.position = None
        self.children = []
        self.parent = None
        self.utility_vm = None
        self.snapshot_tree = None
        self.checking_point = uuid.uuid1().get_hex()
        self.checking_points = []
        self.name = None
        self.depth = 1
        super(ZstackSnapshot, self).__init__()

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def add_child(self, snapshot):
        self.children.append(snapshot)

    def get_children(self):
        return self.children

    def set_snapshot_tree(self, tree):
        self.snapshot_tree = tree

    def get_snapshot_tree(self):
        return self.snapshot_tree

    def set_depth(self, num):
        self.depth = num

    def get_depth(self):
        return self.depth

    def get_all_child_list(self):
        all_child = []
        temp = self.get_children()
        for i in temp:
            all_child.extend(self.get_all_child_list(i))
        return all_child

    def get_children_tree_list(self):
        children = []
        temp = self.get_children()
        for i in temp:
            children.append(self.get_all_child_list(i))
        return children

    def get_parent(self):
        return self.parent

    def set_parent(self, snapshot):
        self.parent = snapshot

    def remove_children(self):
        children = self.get_all_child_list()
        for child in children:
            child.state = sp_header.DELETED
            self.snapshot_tree.deleted.append(child)
        self.child = None

    def get_all_parent(self):
        parents = []
        if self.get_parent:
            parents.append(self.get_all_parent())
        return parents

    def set_utility_vm(self, vm):
        self.utility_vm = vm

    def get_utility_vm(self):
        return self.utility_vm

    # ps_migrate must update snapshot tree
    def update(self):
        snapshot = test_lib.lib_get_volume_snapshot(self.get_snapshot().uuid)[0]
        self.set_snapshot(snapshot)

    def set_checking_points(self, checking_points):
        self.checking_points = checking_points

    def get_checking_points(self):
        return self.checking_points

    def get_checking_point(self):
        return self.checking_point

    def set_checking_point(self):
        def _create_checking_file():
            # lib_mkfs_for_volume do not force mkfs if it can be mounted
            if not self.parent and not self.children:
                test_lib.lib_mkfs_for_volume(self.target_volume.get_volume().uuid, \
                                             self.utility_vm.get_vm())

        import tempfile
        with tempfile.NamedTemporaryFile() as script:
            script.write('''
device=/dev/`ls -ltr --file-type /dev | awk '$4~/disk/ {print $NF}' | grep -v '[[:digit:]]' | tail -1`1
mkdir -p %s
mount $device %s
mkdir -p %s
touch %s/%s
umount %s
	            ''' % (test_lib.WOODPECKER_MOUNT_POINT, \
                       test_lib.WOODPECKER_MOUNT_POINT, \
                       checking_point_folder, checking_point_folder, \
                       self.checking_point, test_lib.WOODPECKER_MOUNT_POINT))
            script.flush()
            test_lib.lib_execute_shell_script_in_vm(self.utility_vm.get_vm(),
                                                    script.name)

        if self.parent:
            test_util.test_logger('[snapshot:] %s checking file: %s is created. Its [parent:] %s' % \
                                  (self.snapshot.name, \
                                   self.checking_point, self.parent.get_snapshot().uuid))
        else:
            test_util.test_logger('[snapshot:] %s checking file: %s is created.' % (self.name, self.checking_point))

        test_volume = self.get_target_volume()
        volume = test_volume.get_volume()
        if volume.type == 'Root':
            test_util.test_logger(
                'Can not add checking point file for Root Volume: %s, since it can not be detached and reattached to utility vm for checking.' % volume.uuid)
            return

        target_vm = test_volume.get_target_vm()
        # check if volume has been attached to the living VM.
        if test_volume.get_state() == volume_header.ATTACHED:
            if target_vm.get_state() == vm_header.STOPPED or target_vm.get_state() == vm_header.RUNNING:
                test_util.test_logger('volume has been attached to living VM.')
                test_volume.detach(target_vm.get_vm().uuid)
                test_volume.attach(self.utility_vm)
                # add checking point
                _create_checking_file()
                test_volume.detach(self.utility_vm.get_vm().uuid)
                test_volume.attach(target_vm)
        else:
            test_volume.attach(self.utility_vm)
            # add_checking_point
            _create_checking_file()
            test_volume.detach(self.utility_vm.get_vm().uuid)

            self.checking_points.append(self.checking_point)

    def create_data_volume(self, name=None, ps_uuid=None):

        snapshot_uuid = self.snapshot.uuid
        if not name:
            name = 'data volume created by sp: %s' % snapshot_uuid

        volume_inv = vol_ops.create_volume_from_snapshot(snapshot_uuid, name, ps_uuid)

        volume_test_obj = zstack_volume_header.ZstackTestVolume()
        volume_test_obj.set_volume(volume_inv)
        volume_test_obj.set_state(volume_header.DETACHED)

        # add checking file
        if self.get_volume_type() != volume_header.ROOT_VOLUME:
            volume_test_obj.set_original_checking_points(self.get_checking_points())

        return volume_test_obj

    def create_image(self, image_option):

        if not image_option.get_root_volume_uuid():
            image_option.set_root_volume_uuid(self.snapshot.uuid)

        if not image_option.get_backup_storage_uuid_list():
            bs_uuid = res_ops.get_resource(res_ops.BACKUP_STORAGE)[0].uuid
            image_option.set_backup_storage_uuid_list([bs_uuid])

        img_inv = img_ops.create_template_from_snapshot(image_option)

        img_test_obj = zstack_image_header.ZstackTestImage()
        img_test_obj.set_image(img_inv)
        img_test_obj.set_state(image_header.CREATED)

        return img_test_obj


class ZstackSnapshotTree(object):
    def __init__(self, volume):
        self.heads = []
        self.target_volume = volume
        self.current_snapshot = None
        self.deleted = []
        self.snapshot_list = []
        self.utility_vm = None
        self.Maxdepth = None
        # reimage / reinit
        self.Newhead = None

    def _config_sp_depth(self):
        Maxdepth = conf_ops.get_global_config_value("volumeSnapshot", 'incrementalSnapshot.maxNum')
        return Maxdepth

    # def set_Max_depth(self, num):
    #     self.Maxdepth = num
    #
    # def get_Max_depth(self):
    #     return self.Maxdepth

    def set_current_snapshot(self, snapshot):
        self.current_snapshot = snapshot

    def get_current_snapshot(self):
        return self.current_snapshot

    def add_heads(self, snapshot):
        self.heads.append(snapshot)

    def get_heads(self):
        return self.heads

    def get_target_volume(self):
        return self.target_volume

    def get_snapshot_list(self, head=None):
        return self.snapshot_list

    def get_checking_points(self, snapshot=None):
        if snapshot:
            return snapshot.get_checking_points()
        return self.current_snapshot.get_checking_points()

    def create_snapshot(self, name):
        self.Maxdepth = self._config_sp_depth()
        sp_option = test_util.SnapshotOption()
        sp_option.set_name(name)
        sp_option.set_volume_uuid(self.target_volume.get_volume().uuid)
        snapshot = ZstackSnapshot()
        snapshot.set_utility_vm(self.utility_vm)
        snapshot.set_name(name)
        snapshot.set_target_volume(self.target_volume)
        snapshot.set_snapshot_tree(self)
        super(ZstackSnapshot, snapshot).create()

        # known issue if ps_type is ceph, every snapshot is a head node
        ps_uuid = self.target_volume.get_volume().primaryStorageUuid
        cond = res_ops.gen_query_conditions('uuid', '=', ps_uuid)
        ps = res_ops.query_resource(res_ops.PRIMARY_STORAGE, cond)[0]
        # if it is the first snapshot or it is in ceph ps
        if ps.type in ['Ceph']:
            self.Maxdepth = 1

        if self.current_snapshot:
            current_depth = self.current_snapshot.get_depth()
            next_depth = 1 if self.current_snapshot + 1 > self.Maxdepth else current_depth + 1
        else:
            next_depth = 1

        if next_depth == 1 or self.Newhead:
            self.heads.append(snapshot)
        else:
            self.current_snapshot.add_child(snapshot)
            snapshot.set_parent(self.current_snapshot)

        if os.environ.get('ZSTACK_SIMULATOR') != "yes":
            if self.current_snapshot:
                snapshot.set_checking_points(self.current_snapshot.get_checking_points())
            snapshot.set_checking_point()

        snapshot.snapshot = vol_ops.create_snapshot(sp_option)
        self.target_volume.update_volume()

        self.snapshot_list.append(snapshot)
        self.set_current_snapshot(snapshot)

        snapshot.set_depth(next_depth)

        self.Newhead = False
        return snapshot

    # resize reinit clone  create_image/template will auto create a snapshot
    def add_snapshot(self, snapshot_uuid):
        self.Maxdepth = self._config_sp_depth()
        snapshot = ZstackSnapshot()
        snapshot.set_utility_vm(self.utility_vm)
        snapshot.set_target_volume(self.target_volume)
        snapshot.set_snapshot_tree(self)
        super(ZstackSnapshot, snapshot).create()
        snapshot.snapshot = test_lib.lib_get_volume_snapshot(snapshot_uuid)[0]
        snapshot.set_name(snapshot.get_snapshot().name)
        self.target_volume.update_volume()

        # known issue if ps_type is ceph, snapshot do not have children and parent, every snapshot is a head node
        ps_uuid = self.target_volume.get_volume().primaryStorageUuid
        cond = res_ops.gen_query_conditions('uuid', '=', ps_uuid)
        ps = res_ops.query_resource(res_ops.PRIMARY_STORAGE, cond)

        # if it is the first snapshot or it is in ceph ps
        if ps.type in ['Ceph']:
            self.Maxdepth = 1

        if self.current_snapshot:
            current_depth = self.current_snapshot.get_depth()
            next_depth = 1 if self.current_snapshot + 1 > self.Maxdepth else current_depth + 1
        else:
            next_depth = 1

        if next_depth == 1 or self.Newhead:
            self.heads.append(snapshot)
        else:  # if snapshot is auto created it have the same checking_points with current_snapshot
            snapshot.set_checking_points(self.current_snapshot.get_checking_points())
            self.current_snapshot.add_child(snapshot)
            snapshot.set_parent(self.current_snapshot)
            snapshot.set_depth(self.current_snapshot.depth+1)

        self.snapshot_list.append(snapshot)
        self.set_current_snapshot(snapshot)

        snapshot.set_depth(next_depth)

        self.Newhead = False

    def delete(self, snapshot):
        cond = res_ops.gen_query_conditions('uuid', '=', snapshot.get_snapshot().uuid)
        snapshots = res_ops.query_resource(res_ops.VOLUME_SNAPSHOT, cond)
        if snapshots:
            vol_ops.delete_snapshot(snapshot.get_snapshot().uuid)

        snapshot.state = sp_header.DELETED
        self.deleted.append(self)
        snapshot.remove_children()

        # snapshot is head, snapshot.parent == None, head will be deleted
        if snapshot in self.heads:
            # current is in deleted-snapshot children
            if self.current_snapshot in snapshot.get_all_child_list():
                self.current_snapshot = None
            # current is not in deleted-snapshot children
            self.heads.remove(snapshot)


        # snapshot is not head but is current or current is in snapshot's children
        elif snapshot == self.current_snapshot or self.current_snapshot in snapshot.get_all_child_list():
            self.current_snapshot = snapshot.parent

        self.snapshot_list.remove(snapshot)

    # when snapshot_tree is the first created and ps_migrate must update snapshot tree
    def update(self):
        cond = res_ops.gen_query_conditions('name', '=', "utility_vm_for_robot_test")
        cond = res_ops.gen_query_conditions('state', '=', "Running", cond)
        vms = res_ops.query_resource(res_ops.VM_INSTANCE, cond)
        for vm in vms:
            if self.get_target_volume().get_volume().primaryStorageUuid == vm.allVolumes[0].primaryStorageUuid:
                import zstackwoodpecker.zstack_test.zstack_test_vm as zstack_vm_header
                utility_vm_uuid = vm.uuid
                utility_vm = zstack_vm_header.ZstackTestVm()
                utility_vm.create_from(utility_vm_uuid)

                self.utility_vm = utility_vm

        for snapshot in self.snapshot_list:
            snapshot.update()
            snapshot.set_utility_vm(self.utility_vm)

        new_snap = self.find_new_auto_create_snapshot()
        if new_snap:
            self.add_snapshot(new_snap)

    def use(self, snapshot):
        vol_ops.use_snapshot(snapshot.get_snapshot().uuid)
        snapshot.target_volume.update_volume()
        self.set_current_snapshot(snapshot)

    def batch_delete_snapshots(self, snapshots):
        for snapshot in snapshots:
            if snapshot.state != sp_header.DELETED:
                self.delete(snapshot)

    def find_new_auto_create_snapshot(self):
        cond = res_ops.gen_query_conditions('volumeUuid', '=', self.target_volume.get_volume().uuid)
        cond = res_ops.gen_query_conditions('sortBy', '=', 'createDate', cond)
        snaps = res_ops.query_resource(res_ops.VOLUME_SNAPSHOT, cond)
        test_util.test_logger([snap.name for snap in snaps])
        if len(snaps) == len(self.get_snapshot_list()):
            return
        return snaps[-1]
