# encoding=utf-8


RUNNING = "RUNNING"
STOPPED = "STOPPED"

DELETED = "DELETED"
EXPUNGED = "EXPUNGED"

ATTACHED = "ATTACHED"
DETACHED = "DETACHED"
ENABLED = "ENABLED"
HA = "HA"

DATA = "'data'"
ROOT = "'root'"

VM = "'VM'"
VOLUME = "'VOLUME'"

QCOW2 = "'qcow2'"
ISO = "'iso'"

MINI = False


class resource_dict(object):
    def __init__(self):
        self.running = []
        self.enabled = []
        self.stopped = []
        self.attached = []
        self.detached = []
        self.deleted = []
        self.expunged = []
        self.ha = []
        self.len = 0
        self.group = {}

    def __repr__(self):
        temp = "Running:"
        temp += str(self.running)
        temp += "\nStopped:"
        temp += str(self.stopped)
        temp += "\nEnadbled:"
        temp += str(self.enabled)
        temp += "\nattached:"
        temp += str(self.attached)
        temp += "\nDetached:"
        temp += str(self.detached)
        temp += "\nDeleted:"
        temp += str(self.deleted)
        temp += "\nExpunged:"
        temp += str(self.expunged)
        temp += "\nHa:"
        temp += str(self.ha)
        temp += "\nGroup:"
        for k, v in self.group.items():
            temp += ("\n\t%s:%s") % (str(k), str(v))
            temp += "---%s" % v[0].description
        return temp

    def __str__(self):
        return self.__repr__()

    def __add__(self, other):
        resource = resource_dict()
        resource.group = dict(self.group, **other.group)
        resource.running = self.running + other.running
        resource.enabled = self.enabled + other.enabled
        resource.stopped = self.stopped + other.stopped
        resource.attached = self.attached + other.attached
        resource.detached = self.detached + other.detached
        resource.deleted = self.deleted + other.deleted
        resource.expunged = self.expunged + other.expunged
        resource.ha = self.ha + other.ha
        resource.len = self.len + other.len
        return resource

    def change_state(self, resource, src_sdt=None, dst_sdt=None):
        if src_sdt == RUNNING:
            self.running.remove(resource)
        elif src_sdt == ENABLED:
            self.enabled.remove(resource)
        elif src_sdt == ATTACHED:
            self.attached.remove(resource)
        elif src_sdt == DETACHED:
            self.detached.remove(resource)
        elif src_sdt == STOPPED:
            self.stopped.remove(resource)
        elif src_sdt == DELETED:
            self.deleted.remove(resource)
        elif src_sdt == HA:
            self.ha.remove(resource)

        if dst_sdt == RUNNING:
            self.running.append(resource)
        elif dst_sdt == ENABLED:
            self.enabled.append(resource)
        elif dst_sdt == ATTACHED:
            self.attached.append(resource)
        elif dst_sdt == DETACHED:
            self.detached.append(resource)
        elif dst_sdt == STOPPED:
            self.stopped.append(resource)
        elif dst_sdt == DELETED:
            self.deleted.append(resource)
        elif dst_sdt == EXPUNGED:
            self.expunged.append(resource)
        elif dst_sdt == HA:
            self.ha.append(resource)

    def add(self, resource, dst_sdt=None):
        if dst_sdt == RUNNING:
            self.running.append(resource)
        elif dst_sdt == STOPPED:
            self.stopped.append(resource)
        elif dst_sdt == ATTACHED:
            self.attached.append(resource)
        elif dst_sdt == ENABLED:
            self.enabled.append(resource)
        elif dst_sdt == DETACHED:
            self.detached.append(resource)

        self.len += 1

    def get_not_ha_resource(self):
        r_list = []
        for resource in self.running:
            if resource not in self.ha:
                r_list.append(resource)
        return r_list


all_volumes = resource_dict()
all_vms = resource_dict()
all_snapshots = resource_dict()
all_backups = resource_dict()
all_images = resource_dict()


def reset():
    global all_volumes
    global all_vms
    global all_snapshots
    global all_backups
    global all_images
    all_volumes = resource_dict()
    all_vms = resource_dict()
    all_snapshots = resource_dict()
    all_backups = resource_dict()
    all_images = resource_dict()


class Resource(object):
    def __init__(self, name=None, type=None):
        print "Resource %s has been created" % self.name

    def __repr__(self):
        return self.name

    def change_state(self, state):
        print "Resource [%s] changes state [%s] to [%s]" % (self.name, self.state, state)
        self.state = state

    def do_change(self, state, action_name):
        print "Resource [%s] must changes state [%s] to [%s] to do [%s]" % (self.name, self.state, state, action_name)
        pass


class Vm(Resource):
    def __init__(self, name=None):
        self.state = RUNNING
        if not name:
            self.name = "'vm" + str(all_vms.len + 1) + "'"
        else:
            self.name = name
        self.root_name = self.name[:-1] + "-root'"
        self.haveHA = False
        self.volumes = []
        self.backups = []
        self.snapshots = []
        self.root_volume = Volume(self.root_name, type=ROOT)
        self.root_volume.vm = self
        super(Vm, self).__init__()

    def start(self):
        all_vms.change_state(self, self.state, RUNNING)
        self.state = RUNNING
        return "[TestAction.start_vm, %s]" % self.name

    def stop(self):
        all_vms.change_state(self, self.state, STOPPED)
        self.state = STOPPED
        return "[TestAction.stop_vm, %s]" % self.name

    def delete(self):
        all_vms.change_state(self, self.state, DELETED)
        self.state = DELETED
        if self.haveHA:
            all_vms.change_state(self, src_sdt=HA)
            self.haveHA = not self.haveHA
        for volume in self.volumes:
            all_volumes.change_state(volume, ATTACHED, DETACHED)
            volume.state = DETACHED
            volume.vm = None
        self.volumes = []
        return "[TestAction.destroy_vm, %s]" % self.name

    def expunge(self):
        all_vms.change_state(self, self.state, EXPUNGED)
        self.state = EXPUNGED
        for snapshot in self.snapshots:
            all_snapshots.change_state(snapshot, ENABLED, DELETED)
            snapshot.state = DELETED
            self.snapshots.remove(snapshot)
            if snapshot.groupId:
                all_snapshots.group.pop(snapshot.groupId)
        return "[TestAction.expunge_vm, %s]" % self.name

    def recover(self):
        all_vms.change_state(self, self.state, STOPPED)
        self.state = STOPPED
        return "[TestAction.recover_vm, %s]" % self.name

    def change_ha(self):
        if self.haveHA:
            all_vms.change_state(self, src_sdt=HA)
        else:
            all_vms.change_state(self, dst_sdt=HA)
            if self.state == STOPPED:
                all_vms.change_state(self, self.state, RUNNING)
        self.haveHA = not self.haveHA
        self.state = RUNNING
        return "[TestAction.change_vm_ha, %s]" % self.name

    def create(self, tags=None):
        all_vms.add(self, RUNNING)
        self.state = RUNNING
        if tags and "'data_volume=true'" in tags:
            volume = Volume("'auto-volume" + str(all_vms.len + 1) + "'")
            self.volumes.append(volume)
            volume.vm = self
            all_volumes.add(volume, ATTACHED)
            volume.state = ATTACHED
        if MINI:
            return "[TestAction.create_mini_vm, %s, %s]" % (self.name, ", ".join(tags))
        return "[TestAction.create_vm, %s, %s]" % (self.name, ", ".join(tags))

    def reinit(self):
        return "[TestAction.reinit_vm, %s]" % self.name

    def change_vm_image(self):
        return "[TestAction.change_vm_image, %s]" % (self.name)

    def migrate(self):
        return "[TestAction.migrate_vm, %s]" % self.name

    def resize(self, tags):
        if not tags:
            return "[TestAction.resize_volume, %s, 5*1024*1024]" % self.name
        else:
            return "[TestAction.resize_volume, %s, %s]" % (self.name, ", ".join(tags))

    def clone_vm(self):
        name = "'clone-" + self.name[1:]
        new_vm = Vm(name)
        all_vms.add(new_vm, RUNNING)
        return "[TestAction.clone_vm, %s, %s]" % (self.name, new_vm.name)

    def clone_vm_with_volume(self):
        vm_name = "'clone-" + self.name[1:-1] + str(all_vms.len) + "'"
        new_vm = Vm(vm_name)
        all_vms.add(new_vm, RUNNING)
        for volume in self.volumes:
            name = vm_name.replace(self.name[1:-1], volume.name[1:-1])
            new_volume = Volume(name)
            all_volumes.add(new_volume, ATTACHED)
        return "[TestAction.clone_vm, %s, %s, 'full']" % (self.name, vm_name)

    def reboot(self):
        return "[TestAction.reboot_vm, %s]" % self.name

    def ps_migrate(self):
        return "[TestAction.ps_migrate_vm, %s]" % self.name

    def create_root_snapshot(self):
        # name: vm1-root-snapshot-1
        snapshot_name = self.root_name[:-1] + "-snapshot" + str(all_snapshots.len + 1) + "'"
        snapshot = Snapshot(snapshot_name)
        snapshot.create()
        snapshot.set_volume(self.root_volume)
        self.snapshots.append(snapshot)
        return "[TestAction.create_volume_snapshot, %s, %s]" % (self.root_name, snapshot.name)

    def delete_root_snapshot(self, snapshot):
        self.snapshots.remove(snapshot)
        if snapshot.groupId and all_snapshots.group.has_key(snapshot.groupId):
            all_snapshots.group.pop(snapshot.groupId)
        return snapshot.delete()

    def use_root_snapshot(self, snapshot):
        return snapshot.use()

    def create_vm_snapshot(self):
        groupId = "vm_snap" + str(len(all_snapshots.group) + 1)
        description = (self.name + "" + "_".join([vol.name for vol in self.volumes])).replace("'", "")
        all_snapshots.group[groupId] = []
        root_snapshot_name = self.name[:-1] + "-snapshot" + str(all_snapshots.len + 1) + "'"
        root_snapshot = Snapshot(root_snapshot_name)
        root_snapshot.create()
        root_snapshot.set_volume(self.root_volume)
        root_snapshot.set_groupId(groupId, description)
        self.snapshots.append(root_snapshot)
        for volume in self.volumes:
            snapshot_name = root_snapshot_name.replace(self.name[:-1], volume.name[:-1])
            vol_snapshot = Snapshot(snapshot_name)
            vol_snapshot.create()
            vol_snapshot.set_volume(volume)
            vol_snapshot.set_groupId(groupId, description)
        return "[TestAction.create_vm_snapshot, %s, %s]" % (self.name, root_snapshot.name)

    def delete_vm_snapshot(self, groupId):
        vm_snapshot_name = ''
        for snapshot in self.root_volume.snapshots:
            if snapshot.groupId == groupId:
                self.snapshots.remove(snapshot)
                for vol_snapshot in all_snapshots.group[groupId]:
                    all_snapshots.change_state(vol_snapshot, vol_snapshot.state, DELETED)
                    vol_snapshot.volume.snapshots.remove(vol_snapshot)
                vm_snapshot_name = snapshot.name
        all_snapshots.group.pop(groupId)
        return "[TestAction.delete_vm_snapshot, %s]" % vm_snapshot_name

    def use_vm_snapshot(self, groupId):
        vm_snapshot_name = ''
        for snapshot in self.root_volume.snapshots:
            if snapshot.groupId == groupId:
                vm_snapshot_name = snapshot.name
        return "[TestAction.use_vm_snapshot, %s]" % vm_snapshot_name

    def create_root_backup(self):
        # name: vm1-root-backup-1
        backup_name = self.root_name[:-1] + "-backup" + str(all_backups.len + 1) + "'"
        backup = Backup(backup_name)
        backup.create()
        backup.set_volume(self.root_volume)
        self.backups.append(backup)
        return "[TestAction.create_volume_backup, %s, %s]" % (self.root_name, backup.name)

    def delete_root_backup(self, backup):
        self.backups.remove(backup)
        if backup.groupId and all_backups.group.has_key(backup.groupId):
            all_backups.group.pop(backup.groupId)
        return backup.delete()

    def use_root_backup(self, backup):
        return backup.use()

    def create_vm_backup(self):
        groupId = "vm_backup" + str(len(all_backups.group) + 1)
        description = (self.name + "_" + "_".join([vol.name for vol in self.volumes])).replace("'", "")
        all_backups.group[groupId] = []
        root_backup_name = self.name[:-1] + "-backup" + str(all_backups.len + 1) + "'"
        root_backup = Backup(root_backup_name)
        root_backup.create()
        root_backup.set_volume(self.root_volume)
        root_backup.set_groupId(groupId, description)
        self.backups.append(root_backup)
        for volume in self.volumes:
            backup_name = root_backup_name.replace(self.name[:-1], volume.name[:-1])
            vol_backup = Backup(backup_name)
            vol_backup.create()
            vol_backup.set_volume(volume)
            vol_backup.set_groupId(groupId, description)
        return "[TestAction.create_vm_backup, %s, %s]" % (self.name, root_backup.name)

    def delete_vm_backup(self, groupId):
        vm_backup_name = ''
        for backup in self.root_volume.backups:
            if backup.groupId == groupId:
                self.backups.remove(backup)
                for vol_backup in all_backups.group[groupId]:
                    all_backups.change_state(vol_backup, vol_backup.state, DELETED)
                    vol_backup.volume.backups.remove(vol_backup)
                vm_backup_name = backup.name
        all_backups.group.pop(groupId)
        return "[TestAction.delete_vm_backup, %s]" % vm_backup_name

    def use_vm_backup(self, groupId):
        vm_backup_name = ''
        for backup in self.root_volume.backups:
            if backup.groupId == groupId:
                vm_backup_name = backup.name
        return "[TestAction.use_vm_backup, %s]" % vm_backup_name

    def create_image(self):
        image = Image(self.name)
        image.type = ROOT
        all_images.add(image, ENABLED)
        return "[TestAction.create_image_from_volume, %s, %s]" % (self.name, image.name)


class Volume(Resource):
    def __init__(self, name=None, type=DATA):
        if not name:
            self.name = "'volume" + str(all_volumes.len + 1) + "'"
        else:
            self.name = name
        Resource.__init__(self)
        self.state = DETACHED
        self.vm = None
        self.backups = []
        self.snapshots = []
        self.type = type

    def create(self, tags):
        all_volumes.add(self, DETACHED)
        self.state = DETACHED
        if tags and "flag" in tags[-1]:
            tags[-1] = tags[-1][:-1] + ",scsi" + "'"
        elif not tags or "flag" not in tags[-1]:
            tags.append("'flag=scsi'")
        return "[TestAction.create_volume, %s, %s]" % (self.name, ", ".join(tags))

    def attach(self, vm):
        all_volumes.change_state(self, self.state, ATTACHED)
        self.state = ATTACHED
        vm.volumes.append(self)
        self.vm = vm
        return "[TestAction.attach_volume, %s, %s]" % (vm.name, self.name)

    def detach(self):
        all_volumes.change_state(self, self.state, DETACHED)
        self.state = DETACHED
        self.vm.volumes.remove(self)
        self.vm = None
        return "[TestAction.detach_volume, %s]" % self.name

    def resize(self, tags):
        if not tags:
            return "[TestAction.resize_data_volume, %s, 5*1024*1024]" % self.name
        else:
            return "[TestAction.resize_data_volume, %s, %s]" % (self.name, ", ".join(tags))

    def delete(self):
        all_volumes.change_state(self, self.state, DELETED)
        self.state = DELETED
        if self.vm:
            self.vm.volumes.remove(self)
        self.vm = None
        return "[TestAction.delete_volume, %s]" % self.name

    def expunge(self):
        all_volumes.change_state(self, self.state, EXPUNGED)
        self.state = EXPUNGED
        for snapshot in self.snapshots:
            all_snapshots.change_state(snapshot, ENABLED, DELETED)
            snapshot.state = DELETED
        return "[TestAction.expunge_volume, %s]" % self.name

    def recover(self):
        all_volumes.change_state(self, self.state, DETACHED)
        self.state = DETACHED
        return "[TestAction.recover_volume, %s]" % self.name

    def ps_migrate(self):
        return "[TestAction.ps_migrate_volume, %s]" % self.name

    def migrate(self):
        return "[TestAction.migrate_volume, %s]" % self.name

    def create_volume_snapshot(self):
        # name: volume1-snapshot1
        snapshot_name = self.name[:-1] + "-snapshot" + str(all_snapshots.len + 1) + "'"
        snapshot = Snapshot(snapshot_name)
        snapshot.create()
        self.snapshots.append(snapshot)
        snapshot.volume = self
        return "[TestAction.create_volume_snapshot, %s, %s]" % (self.name, snapshot.name)

    def delete_volume_snapshot(self, snapshot):
        self.snapshots.remove(snapshot)
        return snapshot.delete()

    def use_volme_snapshot(self, snapshot):
        return snapshot.use()

    def create_volume_backup(self):
        backup_name = self.name[:-1] + "-backup" + str(all_backups.len + 1) + "'"
        backup = Backup(backup_name)
        backup.create()
        self.backups.append(backup)
        backup.volume = self
        return "[TestAction.create_volume_backup, %s, %s]" % (self.name, backup.name)

    def delete_volume_backup(self, backup):
        self.backups.remove(backup)
        return backup.delete()

    def use_volume_backup(self, backup):
        return backup.use()

    def create_image(self):
        image = Image(self.name)
        image.type = DATA
        all_images.add(image, ENABLED)
        return "[TestAction.create_data_vol_template_from_volume, %s, %s]" % (self.name, image.name)


class Snapshot(Resource):
    def __init__(self, name):
        self.name = name
        self.state = ENABLED
        self.volume = None
        self.groupId = None
        self.description = ""
        Resource.__init__(self)

    def create(self):
        all_snapshots.add(self, ENABLED)

    def set_groupId(self, groupId, description=None):
        self.groupId = groupId
        self.description = description
        all_snapshots.group[groupId].append(self)

    def set_volume(self, volume):
        self.volume = volume
        volume.snapshots.append(self)

    def delete(self):
        all_snapshots.change_state(self, self.state, DELETED)
        self.state = DELETED
        return "[TestAction.delete_volume_snapshot, %s]" % self.name

    def use(self):
        return "[TestAction.use_volume_snapshot, %s]" % self.name

    def detach_vm_snapshot(self):
        all_snapshots.group.pop(self.groupId)
        return "[TestAction.ungroup_volume_snapshot, %s]" % self.name

    def create_image(self):
        image_name = self.name.split('-')[0] + "'"
        image = Image(image_name)
        if "vm" in self.name:
            image.type = ROOT
        else:
            image.type = DATA
        all_images.add(image, ENABLED)
        return "[TestAction.create_image_from_snapshot, %s, %s]" % (self.name, image.name)


class Backup(Resource):
    def __init__(self, name):
        self.name = name
        self.state = ENABLED
        self.volume = None
        self.groupId = None
        self.description = ""
        Resource.__init__(self)

    def create(self):
        all_backups.add(self, ENABLED)

    def set_groupId(self, groupId, description=None):
        self.groupId = groupId
        self.description = description
        all_backups.group[groupId].append(self)

    def set_volume(self, volume):
        self.volume = volume
        volume.backups.append(self)

    def delete(self):
        all_backups.change_state(self, self.state, DELETED)
        self.state = DELETED
        return "[TestAction.delete_volume_backup, %s]" % self.name

    def use(self):
        return "[TestAction.use_volume_backup, %s]" % self.name

    def create_vm(self):
        vm = None
        volumes = []
        for res in all_backups.group[self.groupId]:
            new_name = res.name.split("-")[0] + "-from-" + res.name.split("-")[1]
            if "vm" in res.name:
                vm = Vm(new_name)
                all_vms.add(vm, RUNNING)
            else:
                volume = Volume(new_name)
                all_volumes.add(volume, ATTACHED)
                volumes.append(volume)
        vm.volumes = volumes
        for volume in volumes:
            volume.vm = vm
        return "[TestAction.create_vm_from_backup, %s]" % self.name

    def create_image(self):
        image_name = self.name.split('-')[0] + "'"
        image = Image(image_name)
        if "vm" in self.name:
            image.type = ROOT
        else:
            image.type = DATA
        all_images.add(image, ENABLED)
        return "[TestAction.create_image_from_backup, %s, %s]" % (self.name, image.name)


class Image(Resource):
    def __init__(self, name=None):
        if not name:
            self.name = "'image" + str(all_images.len + 1) + "'"
        else:
            self.name = name[:-1] + "-image" + str(all_images.len + 1) + "'"
        self.state = ENABLED
        self.volume = None
        self.groupId = None
        self.type = ROOT
        self.format = QCOW2
        Resource.__init__(self)

    def add(self, type = ROOT, url="'http://172.20.1.28/mirror/diskimages/centos_vdbench.qcow2'"):
        all_images.add(self, ENABLED)
        if self.format == ISO:
            url = "os.environ.get('isoForVmUrl')"
        return "[TestAction.add_image, %s, %s, %s]" % (self.name, type, url)

    def delete(self):
        all_images.change_state(self, self.state, DELETED)
        self.state = DELETED
        return "[TestAction.delete_image, %s]" % self.name

    def recover(self):
        all_images.change_state(self, self.state, ENABLED)
        self.state = ENABLED
        return "[TestAction.recover_image, %s]" % self.name

    def expunge(self):
        all_images.change_state(self, self.state, EXPUNGED)
        self.state = EXPUNGED
        return "[TestAction.expunge_image, %s]" % self.name

    def create_vm(self, tags):
        vm = Vm()
        all_vms.add(vm, RUNNING)
        return "[TestAction.create_vm_by_image, %s, %s, %s]" % (self.name, self.format, vm.name)

    def create_volume(self):
        # todo: mini robot action must support this function
        volume = Volume()
        all_volumes.add(volume, DETACHED)
        # return [TestAction.create_data_volume_from_image, "volume2", "=scsi"],
        return "[TestAction.create_volume_from_image, %s, %s]" % (self.name, volume.name)


def batch_delete_snapshot(snapshots):
    for snap in snapshots:
        all_snapshots.change_state(snap, snap.state, DELETED)
        if snap.groupId and all_snapshots.group.has_key(snap.groupId):
            all_snapshots.group.pop(snap.groupId)
    return ("TestAction.batch_delete_snapshots, [" + "%s," * len(snapshots) + "]") % tuple(snapshots.name)


if __name__ == "__main__":
    vm1 = Vm()
    print vm1.create([])
    vm2 = Vm()
    print vm2.create([])

    vol1 = Volume()
    print vol1.create([])
    vol2 = Volume()
    print vol2.create([])
    vol3 = Volume()
    print vol3.create([])

    print vol1.attach(vm1)
    print vol3.attach(vm1)
    print vol2.attach(vm2)
    #
    #
    # print vol1.create_volume_snapshot()
    # print vm1.create_vm_snapshot()
    # print vm2.create_vm_snapshot()

    print vol1.create_volume_backup()
    print vm1.create_vm_backup()
    print vm2.create_root_backup()

    all_resources = all_vms + all_volumes + all_snapshots + all_backups + all_images
    print all_resources
