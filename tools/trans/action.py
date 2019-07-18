# encoding=utf-8

import random

import resource


class Action(object):
    def __init__(self):
        self.run_state = None
        self.path = []

    def __repr__(self):
        return self.__class__.__name__

    def check(self, resource_dict, tags):
        pass

    def run(self, tags):
        print "Run action %s %s" % (self.__class__.__name__, tags)


class create_vm(Action):
    def __init__(self):
        super(create_vm, self).__init__()
        self.run_state = None

    def check(self, resource_dict, tag):
        super(create_vm, self).check(resource_dict, tag)

    def run(self, tags=None):
        super(create_vm, self).run(tags)
        vm = resource.Vm()
        self.path.append(vm.create(tags))
        return self.path


class start_vm(Action):
    def __init__(self):
        Action.__init__(self)
        self.run_state = resource.STOPPED

    def check(self, all_vms, tags):
        Action.check(self, all_vms, tags)
        if (len(all_vms.stopped + all_vms.running) - len(all_vms.ha)) == 0:
            print "There is no resource vm to start.Must add create_vm"
            self.path.append(resource.Vm().create([]))
        if len(all_vms.stopped) > 0:
            vm = random.choice(all_vms.stopped)
            return vm
        vm = random.choice(all_vms.get_not_ha_resource())
        self.path.append(vm.stop())
        return vm

    def run(self, tags):
        super(start_vm, self).run(tags)
        vm = self.check(resource.all_vms, tags)
        self.path.append(vm.start())
        return self.path


class stop_vm(Action):
    def __init__(self):
        Action.__init__(self)
        self.run_state = resource.RUNNING

    def check(self, all_vms, tags):
        Action.check(self, all_vms, tags)
        if (len(all_vms.stopped + all_vms.running) - len(all_vms.ha)) == 0:
            print "There is no resource vm to stop.Must add create_vm"
            self.path.append(resource.Vm().create([]))
        running_vm = all_vms.get_not_ha_resource()
        if running_vm:
            return random.choice(running_vm)
        else:
            vm = random.choice(all_vms.ha + all_vms.stopped)
            if vm.haveHA:
                self.path.append(vm.change_ha())
            else:
                self.path.append(vm.start())
            return vm

    def run(self, tags):
        Action.run(self, tags)
        vm = self.check(resource.all_vms, tags)
        self.path.append(vm.stop())
        return self.path


class destroy_vm(Action):
    def __init__(self):
        Action.__init__(self)
        self.run_state = [resource.STOPPED, resource.RUNNING]

    def check(self, all_vms, tags):
        Action.check(self, all_vms, tags)
        if (len(all_vms.stopped + all_vms.running)) == 0:
            print "There is no resource vm to destroy.Must add create_vm"
            self.path.append(resource.Vm().create([]))
        return random.choice(all_vms.stopped + all_vms.running)

    def run(self, tags):
        Action.run(self, tags)
        vm = self.check(resource.all_vms, tags)
        self.path.append(vm.delete())
        return self.path


class change_vm_ha(Action):
    def __init__(self):
        Action.__init__(self)
        self.run_state = [resource.STOPPED, resource.RUNNING]

    def check(self, all_vms, tags):
        Action.check(self, all_vms, tags)
        if (len(all_vms.stopped + all_vms.running)) == 0:
            print "There is no resource vm to change_ha.Must add create_vm"
            self.path.append(resource.Vm().create([]))
        return random.choice(all_vms.stopped + all_vms.running)

    def run(self, tags):
        Action.run(self, tags)
        vm = self.check(resource.all_vms, tags)
        self.path.append(vm.change_ha())
        return self.path


class change_vm_image(Action):
    def __init__(self):
        Action.__init__(self)
        self.run_state = resource.STOPPED

    def check(self, all_vms, tags):
        Action.check(self, all_vms, tags)
        if (len(all_vms.stopped + all_vms.running) - len(all_vms.ha)) == 0:
            print "There is no resource vm to start.Must add create_vm"
            self.path.append(resource.Vm().create([]))
        if len(all_vms.stopped) > 0:
            vm = random.choice(all_vms.stopped)
            return vm
        vm = random.choice(all_vms.get_not_ha_resource())
        self.path.append(vm.stop())
        return vm

    def run(self, tags):
        Action.run(self, tags)
        vm = self.check(resource.all_vms, tags)
        self.path.append(vm.change_vm_image())
        return self.path

class reboot_vm(Action):
    def __init__(self):
        Action.__init__(self)
        self.run_state = resource.RUNNING

    def check(self, all_vms, tags):
        Action.check(self, all_vms, tags)
        if (len(all_vms.stopped + all_vms.running) - len(all_vms.ha)) == 0:
            print "There is no resource vm to stop.Must add create_vm"
            self.path.append(resource.Vm().create([]))
        running_vm = all_vms.get_not_ha_resource()
        if running_vm:
            return random.choice(running_vm)
        else:
            vm = random.choice(all_vms.ha + all_vms.stopped)
            if vm.state == resource.STOPPED:
                self.path.append(vm.start())
            return vm

    def run(self, tags):
        Action.run(self, tags)
        vm = self.check(resource.all_vms, tags)
        self.path.append(vm.reboot())
        return self.path

class recover_vm(Action):
    def __init__(self):
        Action.__init__(self)
        self.run_state = resource.DELETED

    def check(self, all_vms, tags):
        Action.check(self, all_vms, tags)
        if len(all_vms.running + all_vms.stopped + all_vms.deleted) == 0:
            print "There is no resource vm to recover.Must add create_vm"
            self.path.append(resource.Vm().create([]))
        vm = random.choice(all_vms.running + all_vms.stopped + all_vms.deleted)
        if vm.state != resource.DELETED:
            self.path.append(vm.delete())
        return vm

    def run(self, tags):
        Action.run(self, tags)
        vm = self.check(resource.all_vms, tags)
        self.path.append(vm.recover())
        return self.path


class expunge_vm(Action):
    def __init__(self):
        Action.__init__(self)
        self.run_state = resource.DELETED

    def check(self, all_vms, tags):
        Action.check(self, all_vms, tags)
        if len(all_vms.running + all_vms.stopped + all_vms.deleted) == 0:
            print "There is no resource vm to recover.Must add create_vm"
            self.path.append(resource.Vm().create([]))
        vm = random.choice(all_vms.running + all_vms.stopped + all_vms.deleted)
        if vm.state != resource.DELETED:
            self.path.append(vm.delete())
        return vm

    def run(self, tags):
        Action.run(self, tags)
        vm = self.check(resource.all_vms, tags)
        self.path.append(vm.expunge())
        return self.path


class reinit_vm(Action):
    def __init__(self):
        Action.__init__(self)
        self.run_state = resource.STOPPED

    def check(self, all_vms, tags):
        Action.check(self, all_vms, tags)
        if (len(all_vms.stopped + all_vms.running) - len(all_vms.ha)) == 0:
            print "There is no resource vm to start.Must add create_vm"
            self.path.append(resource.Vm().create([]))
        if len(all_vms.stopped) > 0:
            vm = random.choice(all_vms.stopped)
            return vm
        vm = random.choice(all_vms.get_not_ha_resource())
        self.path.append(vm.stop())
        return vm

    def run(self, tags):
        Action.run(self, tags)
        vm = self.check(resource.all_vms, tags)
        self.path.append(vm.reinit())
        return self.path


class migrate_vm(Action):
    def __init__(self):
        Action.__init__(self)
        self.run_state = resource.RUNNING

    def check(self, all_vms, tags):
        Action.check(self, all_vms, tags)
        if (len(all_vms.stopped + all_vms.running)) == 0:
            print "There is no resource vm to stop.Must add create_vm"
            self.path.append(resource.Vm().create([]))
        vm = random.choice(all_vms.running + all_vms.stopped)
        if vm.state != resource.RUNNING:
            self.path.append(vm.start())
        return vm

    def run(self, tags):
        Action.run(self, tags)
        vm = self.check(resource.all_vms, tags)
        self.path.append(vm.migrate())
        return self.path


class resize_root_volume(Action):
    def __init__(self):
        Action.__init__(self)
        self.run_state = [resource.RUNNING, resource.STOPPED]

    def check(self, all_vms, tags):
        Action.check(self, all_vms, tags)
        if (len(all_vms.stopped + all_vms.running)) == 0:
            print "There is no resource vm to change_ha.Must add create_vm"
            self.path.append(resource.Vm().create([]))
        return random.choice(all_vms.stopped + all_vms.running)

    def run(self, tags):
        Action.run(self, tags)
        vm = self.check(resource.all_vms, tags)
        self.path.append(vm.resize(tags))
        return self.path


class clone_vm(Action):
    def __init__(self):
        Action.__init__(self)
        self.run_state = [resource.RUNNING, resource.STOPPED]

    def check(self, all_vms, tags):
        Action.check(self, all_vms, tags)
        if (len(all_vms.stopped + all_vms.running)) == 0:
            print "There is no resource vm to change_ha.Must add create_vm"
            self.path.append(resource.Vm().create([]))
        return random.choice(all_vms.stopped + all_vms.running)

    def run(self, tags):
        Action.run(self, tags)
        vm = self.check(resource.all_vms, tags)
        self.path.append(vm.clone_vm())
        return self.path


class clone_vm_with_volume(Action):
    def __init__(self):
        Action.__init__(self)
        self.run_state = [resource.RUNNING, resource.STOPPED]

    def check(self, all_vms, tags):
        Action.check(self, all_vms, tags)
        if (len(all_vms.stopped + all_vms.running)) == 0:
            print "There is no resource vm to change_ha.Must add create_vm"
            self.path.append(resource.Vm().create([]))
        return random.choice(all_vms.stopped + all_vms.running)

    def run(self, tags):
        Action.run(self, tags)
        vm = self.check(resource.all_vms, tags)
        self.path.append(vm.clone_vm_with_volume())
        return self.path


class ps_migrate_vm(Action):
    def __init__(self):
        Action.__init__(self)
        self.run_state = resource.STOPPED
        self.restart = False

    def check(self, all_vms, tags):
        Action.check(self, all_vms, tags)
        if (len(all_vms.stopped + all_vms.running) - len(all_vms.ha)) == 0:
            print "There is no resource vm to start.Must add create_vm"
            self.path.append(resource.Vm().create([]))
        if len(all_vms.stopped) > 0:
            vm = random.choice(all_vms.stopped)
            return vm
        vm = random.choice(all_vms.get_not_ha_resource())
        self.restart = True
        self.path.append(vm.stop())
        return vm

    def run(self, tags):
        Action.run(self, tags)
        vm = self.check(resource.all_vms, tags)
        self.path.append(vm.ps_migrate())
        if self.restart:
            self.path.append(vm.start())
        return self.path


class create_volume(Action):
    def __init__(self):
        Action.__init__(self)

    def check(self, all_volumes, tags):
        Action.check(self, all_volumes, tags)

    def run(self, tags):
        Action.run(self, tags)
        vol = resource.Volume()
        self.path.append(vol.create(tags))
        return self.path


class attach_volume(Action):
    def __init__(self):
        Action.__init__(self)
        self.run_state = resource.DETACHED
        self.vm = None
        self.volume = None

    def check(self, all_vms, tags):
        Action.check(self, all_vms, tags)
        if (len(all_vms.stopped + all_vms.running)) == 0:
            print "There is no resource vm to attch_volume.Must add create_vm"
            self.vm = resource.Vm()
            self.path.append(self.vm.create([]))
        else:
            self.vm = random.choice(all_vms.stopped + all_vms.running)
        if len(resource.all_volumes.detached) > 0:
            self.volume = random.choice(resource.all_volumes.detached)
        else:
            print "There is no resource volume to attch_volume.Must add create_volume"
            self.volume = resource.Volume()
            self.path.append(self.volume.create([]))
        return self.vm, self.volume

    def run(self, tags):
        Action.run(self, tags)
        vm, volume = self.check(resource.all_vms, tags)
        self.path.append(volume.attach(vm))
        return self.path


class detach_volume(Action):
    def __init__(self):
        Action.__init__(self)
        self.run_state = resource.DETACHED
        self.vm = None
        self.volume = None

    def check(self, all_volumes, tags):
        Action.check(self, all_volumes, tags)
        if (len(resource.all_vms.stopped + resource.all_vms.running)) == 0:
            print "There is no resource vm to detach_volume.Must add create_vm"
            self.vm = resource.Vm()
            self.path.append(self.vm.create([]))
        else:
            self.vm = random.choice(resource.all_vms.stopped + resource.all_vms.running)
        if len(all_volumes.attached) > 0:
            self.volume = random.choice(all_volumes.attached)
        elif len(all_volumes.detached) > 0:
            self.volume = random.choice(all_volumes.detached)
            self.path.append(self.volume.attach(self.vm))
        else:
            print "There is no resource volume to detatch_volume.Must add create_volume"
            self.volume = resource.Volume()
            self.path.append(self.volume.create([]))
            self.path.append(self.volume.attach(self.vm))
        return self.vm, self.volume

    def run(self, tags):
        Action.run(self, tags)
        vm, volume = self.check(resource.all_volumes, tags)
        self.path.append(volume.detach())
        return self.path


class delete_volume(Action):
    def __init__(self):
        Action.__init__(self)
        self.run_state = [resource.ATTACHED, resource.DETACHED]
        self.volume = None

    def check(self, all_volumes, tags):
        Action.check(self, all_volumes, tags)
        if len(all_volumes.attached + all_volumes.detached) > 0:
            self.volume = random.choice(all_volumes.attached + all_volumes.detached)
        else:
            print "There is no resource volume to delete_volume.Must add create_volume"
            self.volume = resource.Volume()
            print self.volume.name
            self.path.append(self.volume.create([]))
        return self.volume

    def run(self, tags):
        Action.run(self, tags)
        volume = self.check(resource.all_volumes, tags)
        self.path.append(volume.delete())
        return self.path


class expunge_volume(Action):
    def __init__(self):
        Action.__init__(self)
        self.run_state = [resource.DELETED]
        self.volume = None

    def check(self, all_volumes, tags):
        Action.check(self, all_volumes, tags)
        if len(all_volumes.detached + all_volumes.attached + all_volumes.detached) > 0:
            self.volume = random.choice(all_volumes.detached * 5 + all_volumes.attached + all_volumes.detached * 3)
            if self.volume.state != resource.DELETED:
                self.path.append(self.volume.delete())
        else:
            print "There is no resource volume to expunge_volume.Must add create_volume"
            self.volume = resource.Volume()
            self.path.append(self.volume.create([]))
            self.path.append(self.volume.delete())
        return self.volume

    def run(self, tags):
        Action.run(self, tags)
        volume = self.check(resource.all_volumes, tags)
        self.path.append(volume.expunge())
        return self.path


class recover_volume(Action):
    def __init__(self):
        Action.__init__(self)
        self.run_state = [resource.DELETED]
        self.volume = None

    def check(self, all_volumes, tags):
        Action.check(self, all_volumes, tags)
        if len(all_volumes.detached + all_volumes.attached + all_volumes.detached) > 0:
            self.volume = random.choice(all_volumes.detached * 5 + all_volumes.attached + all_volumes.detached * 3)
            if self.volume.state != resource.DELETED:
                self.path.append(self.volume.delete())
        else:
            print "There is no resource volume to recover_volume.Must add create_volume"
            self.volume = resource.Volume()
            self.path.append(self.volume.create([]))
            self.path.append(self.volume.delete())
        return self.volume

    def run(self, tags):
        Action.run(self, tags)
        volume = self.check(resource.all_volumes, tags)
        self.path.append(volume.recover())
        return self.path


class resize_volume(Action):
    def __init__(self):
        Action.__init__(self)
        self.run_state = [resource.ATTACHED, resource.DETACHED]
        self.volume = None

    def check(self, all_volumes, tags):
        Action.check(self, all_volumes, tags)
        if len(all_volumes.attached + all_volumes.detached) > 0:
            self.volume = random.choice(all_volumes.attached + all_volumes.detached)
        else:
            print "There is no resource volume to resize_volume.Must add create_volume"
            self.volume = resource.Volume()
            self.path.append(self.volume.create([]))
        return self.volume

    def run(self, tags):
        Action.run(self, tags)
        volume = self.check(resource.all_volumes, tags)
        self.path.append(volume.resize(tags))
        return self.path


class migrate_volume(Action):
    def __init__(self):
        Action.__init__(self)
        self.run_state = [resource.ATTACHED, resource.DETACHED]
        self.volume = None

    def check(self, all_volumes, tags):
        Action.check(self, all_volumes, tags)
        if len(all_volumes.attached + all_volumes.detached) > 0:
            self.volume = random.choice(all_volumes.attached + all_volumes.detached)
        else:
            print "There is no resource volume to migrate_volume.Must add create_volume"
            self.volume = resource.Volume()
            self.path.append(self.volume.create([]))
        return self.volume

    def run(self, tags):
        Action.run(self, tags)
        volume = self.check(resource.all_volumes, tags)
        self.path.append(volume.migrate())
        return self.path


class ps_migrate_volume(Action):
    def __init__(self):
        Action.__init__(self)
        self.run_state = [resource.ATTACHED, resource.DETACHED]
        self.volume = None
        self.restart = False

    def check(self, all_volumes, tags):
        Action.check(self, all_volumes, tags)
        if len(all_volumes.attached + all_volumes.detached + all_volumes.deleted) > 0:
            self.volume = random.choice(all_volumes.attached * 2 + all_volumes.detached * 2 + all_volumes.deleted)
        else:
            print "There is no resource volume to ps_migrate_volume.Must add create_volume"
            self.volume = resource.Volume()
            self.path.append(self.volume.create([]))
        if self.volume.state == resource.ATTACHED and self.volume.vm.state == resource.RUNNING:
            self.restart = True
            self.path.append(self.volume.vm.stop())
        elif self.volume.state == resource.DELETED:
            self.path.append(self.volume.recover())
        return self.volume

    def run(self, tags):
        Action.run(self, tags)
        volume = self.check(resource.all_volumes, tags)
        self.path.append(volume.ps_migrate())
        if self.restart:
            self.path.append(volume.vm.start())
        return self.path


class create_root_snapshot(Action):
    def __init__(self):
        Action.__init__(self)
        self.run_state = [resource.RUNNING, resource.STOPPED]

    def check(self, all_vms, tags):
        Action.check(self, all_vms, tags)
        if (len(all_vms.stopped + all_vms.running)) == 0:
            print "There is no resource vm to change_ha.Must add create_vm"
            self.path.append(resource.Vm().create([]))
        return random.choice(all_vms.stopped + all_vms.running)

    def run(self, tags):
        Action.run(self, tags)
        vm = self.check(resource.all_vms, tags)
        self.path.append(vm.create_root_snapshot())
        return self.path


class delete_root_snapshot(Action):
    def __init__(self):
        Action.__init__(self)
        self.run_state = [resource.RUNNING, resource.STOPPED]

    def check(self, all_vms, tags):
        Action.check(self, all_vms, tags)
        if (len(all_vms.stopped + all_vms.running)) == 0:
            print "There is no resource vm to change_ha.Must add create_vm"
            vm1 = resource.Vm()
            self.path.append(vm1.create([]))
            self.path.append(vm1.create_root_snapshot())
        vm_list = all_vms.stopped + all_vms.running
        random.shuffle(vm_list)
        for vm in vm_list:
            if vm.snapshots:
                snapshot = random.choice(vm.snapshots)
                return vm, snapshot
        else:
            vm = random.choice(all_vms.stopped + all_vms.running)
            self.path.append(vm.create_root_snapshot())
            return vm, vm.snapshots[0]

    def run(self, tags):
        Action.run(self, tags)
        vm, snapshot = self.check(resource.all_vms, tags)
        self.path.append(vm.delete_root_snapshot(snapshot))
        return self.path


class use_root_snapshot(Action):
    def __init__(self):
        Action.__init__(self)
        self.run_state = resource.STOPPED
        self.restart = False

    def check(self, all_vms, tags):
        Action.check(self, all_vms, tags)
        if (len(all_vms.stopped + all_vms.running) - len(all_vms.ha)) == 0:
            print "There is no resource vm to start.Must add create_vm"
            vm1 = resource.Vm()
            self.path.append(vm1.create([]))
            self.path.append(vm1.create_root_snapshot())
            self.path.append(vm1.stop())
        if len(all_vms.stopped) > 0:
            random.shuffle(all_vms.stopped)
            for vm in all_vms.stopped:
                if vm.snapshots:
                    snapshot = random.choice(vm.snapshots)
                    return vm, snapshot
            else:
                vm = random.choice(all_vms.stopped)
                self.path.append(vm.create_root_snapshot())
                return vm, vm.snapshots[0]
        self.restart = True
        vm_list = all_vms.get_not_ha_resource()
        random.shuffle(vm_list)
        for vm in vm_list:
            if vm.snapshots:
                snapshot = random.choice(vm.snapshots)
                self.path.append(vm.stop())
                return vm, snapshot
        else:
            vm = random.choice(all_vms.get_not_ha_resource())
            self.path.append(vm.create_root_snapshot())
            self.path.append(vm.stop())
            return vm, vm.snapshots[0]

    def run(self, tags):
        Action.run(self, tags)
        vm, snapshot = self.check(resource.all_vms, tags)
        self.path.append(vm.use_root_snapshot(snapshot))
        if self.restart:
            self.path.append(vm.start())
        return self.path


class create_root_backup(Action):
    def __init__(self):
        Action.__init__(self)
        self.run_state = [resource.RUNNING, resource.STOPPED, resource.DELETED]
        self.vm = None
        self.reStop = False
        self.reDeleted = False

    def check(self, all_vms, tags):
        Action.check(self, all_vms, tags)
        if (len(all_vms.stopped + all_vms.running + all_vms.deleted)) == 0:
            print "There is no resource vm to change_ha.Must add create_vm"
            self.vm = resource.Vm()
            self.path.append(self.vm.create([]))
        self.vm = random.choice(all_vms.stopped + all_vms.running + all_vms.deleted)
        if self.vm.state == resource.DELETED:
            self.reDeleted = True
            self.path.append(self.vm.recover())
        if self.vm.state == resource.STOPPED:
            self.reStop = True
            self.path.append(self.vm.start())
        return self.vm

    def run(self, tags):
        Action.run(self, tags)
        vm = self.check(resource.all_vms, tags)
        self.path.append(vm.create_root_backup())
        if self.reStop:
            self.path.append(vm.stop())
        if self.reDeleted:
            self.path.append(vm.delete())
        return self.path


class delete_root_backup(Action):
    def __init__(self):
        Action.__init__(self)
        self.run_state = [resource.RUNNING, resource.STOPPED]
        self.vm = None
        self.reStop = False

    def check(self, all_vms, tags):
        Action.check(self, all_vms, tags)
        if (len(all_vms.stopped + all_vms.running)) == 0:
            print "There is no resource vm to change_ha.Must add create_vm"
            vm1 = resource.Vm()
            self.path.append(vm1.create([]))
            self.path.append(vm1.create_root_backup())
        vm_list = all_vms.stopped + all_vms.running
        random.shuffle(vm_list)
        for vm in vm_list:
            if vm.backups:
                backup = random.choice(vm.backups)
                return vm, backup
        else:
            vm = random.choice(all_vms.stopped + all_vms.running)
            if vm.state is not resource.RUNNING:
                self.reStop = True
                self.path.append(vm.start())
            self.path.append(vm.create_root_backup())
            return vm, vm.backups[0]

    def run(self, tags):
        Action.run(self, tags)
        vm, backup = self.check(resource.all_vms, tags)
        self.path.append(vm.delete_root_backup(backup))
        if self.reStop:
            self.path.append(vm.stop())
        return self.path


class use_root_backup(Action):
    def __init__(self):
        Action.__init__(self)
        self.run_state = resource.STOPPED
        self.vm = None
        self.restart = False

    def check(self, all_vms, tags):
        Action.check(self, all_vms, tags)
        if (len(all_vms.stopped + all_vms.running) - len(all_vms.ha)) == 0:
            print "There is no resource vm to start.Must add create_vm"
            self.vm = resource.Vm()
            self.path.append(self.vm.create([]))
            self.path.append(self.vm.create_root_backup())
            self.path.append(self.vm.stop())
        if len(all_vms.stopped) > 0:
            random.shuffle(all_vms.stopped)
            for vm in all_vms.stopped:
                if vm.backups:
                    backup = random.choice(vm.backups)
                    return vm, backup
            else:
                vm = random.choice(all_vms.stopped)
                self.path.append(vm.start())
                self.path.append(vm.create_root_backup())
                self.path.append(vm.stop())
                return vm, vm.backups[0]
        self.restart = True
        vm_list = all_vms.get_not_ha_resource()
        random.shuffle(vm_list)
        for vm in vm_list:
            if vm.backups:
                backup = random.choice(vm.backups)
                self.path.append(vm.stop())
                return vm, backup
        else:
            vm = random.choice(all_vms.get_not_ha_resource())
            self.path.append(vm.create_root_backup())
            self.path.append(vm.stop())
            return vm, vm.backups[0]

    def run(self, tags):
        Action.run(self, tags)
        vm, backup = self.check(resource.all_vms, tags)
        self.path.append(vm.use_root_backup(backup))
        if self.restart:
            self.path.append(vm.start())
        return self.path


class create_vm_backup(Action):
    def __init__(self):
        Action.__init__(self)
        self.run_state = [resource.DETACHED, resource.ATTACHED]
        self.vm = None
        self.restop = False

    def check(self, all_vms, tags):
        Action.check(self, all_vms, tags)
        if (len(all_vms.stopped + all_vms.running)) == 0:
            print "There is no resource vm to change_ha.Must add create_vm"
            self.path.append(resource.Vm().create([]))
        self.vm = random.choice(all_vms.stopped + all_vms.running)
        if self.vm.state == resource.STOPPED:
            self.restop = True
            self.path.append(self.vm.start())
        return self.vm

    def run(self, tags):
        Action.run(self, tags)
        vm = self.check(resource.all_vms, tags)
        self.path.append(vm.create_vm_backup())
        if self.restop:
            self.path.append(vm.stop())
        return self.path


class delete_vm_backup(Action):
    def __init__(self):
        Action.__init__(self)
        self.run_state = [resource.STOPPED, resource.DELETED, resource.RUNNING]
        self.vm = None
        self.restop = False

    def check(self, all_vms, tags):
        Action.check(self, all_vms, tags)
        if (len(all_vms.stopped + all_vms.running)) == 0:
            print "There is no resource vm to change_ha.Must add create_vm"
            self.vm = resource.Vm()
            self.path.append(self.vm.create([]))
            self.path.append(self.vm.create_vm_backup())
            return self.vm, self.vm.backups[0]
        vm_list = all_vms.stopped + all_vms.running
        random.shuffle(vm_list)
        for vm in vm_list:
            if vm.backups:
                for backup in vm.backups:
                    if backup.groupId:
                        return vm, backup
        else:
            vm = random.choice(all_vms.stopped + all_vms.running)
            if vm.state == resource.STOPPED:
                self.restop = True
                self.path.append(vm.start())
            self.path.append(vm.create_vm_backup())
            return vm, vm.backups[0]

    def run(self, tags):
        Action.run(self, tags)
        vm, backup = self.check(resource.all_vms, tags)
        self.path.append(vm.delete_vm_backup(backup.groupId))
        if self.restop:
            self.path.append(vm.stop())
        return self.path


class use_vm_backup(Action):
    def __init__(self):
        Action.__init__(self)
        self.run_state = [resource.DETACHED, resource.ATTACHED]
        self.vm = None
        self.restart = False

    def check(self, all_vms, tags):
        Action.check(self, all_vms, tags)
        Action.check(self, all_vms, tags)
        if (len(all_vms.stopped + all_vms.running) - len(all_vms.ha)) == 0:
            print "There is no resource vm to delete_vm_backup.Must add create_vm"
            self.vm = resource.Vm()
            self.path.append(self.vm.create([]))
            self.path.append(self.vm.create_vm_backup())
            self.path.append(self.vm.stop())
        if len(all_vms.stopped) > 0:
            random.shuffle(all_vms.stopped)
            for vm in all_vms.stopped:
                for backup in vm.backups:
                    if backup.groupId:
                        return vm, backup
            else:
                vm = random.choice(all_vms.stopped)
                self.path.append(vm.start())
                self.path.append(vm.create_vm_backup())
                self.path.append(vm.stop())
                return vm, vm.backups[0]
        self.restart = True
        vm_list = all_vms.get_not_ha_resource()
        random.shuffle(vm_list)
        for vm in vm_list:
            for backup in vm.backups:
                if backup.groupId:
                    self.path.append(vm.stop())
                    return vm, backup
        else:
            vm = random.choice(all_vms.get_not_ha_resource())
            self.path.append(vm.create_vm_backup())
            self.path.append(vm.stop())
            return vm, vm.backups[0]

    def run(self, tags):
        Action.run(self, tags)
        vm, backup = self.check(resource.all_vms, tags)
        self.path.append(vm.use_vm_backup(backup.groupId))
        if self.restart:
            self.path.append(vm.start())
        return self.path


class create_volume_snapshot(Action):
    def __init__(self):
        Action.__init__(self)
        self.run_state = [resource.DETACHED, resource.ATTACHED]
        self.volume = None
        self.restate = False

    def check(self, all_volumes, tags):
        Action.check(self, all_volumes, tags)
        if len(all_volumes.detached + all_volumes.attached + all_volumes.deleted) == 0:
            print "There is no resource volume to create_volume_snapshot.Must add create_volume"
            self.volume = resource.Volume()
            self.path.append(self.volume.create([]))
        self.volume = random.choice(all_volumes.detached * 2 + all_volumes.attached * 3 + all_volumes.deleted)
        if self.volume.state == resource.DELETED:
            self.path.append(self.volume.recover())
        return self.volume

    def run(self, tags):
        Action.run(self, tags)
        volume = self.check(resource.all_volumes, tags)
        self.path.append(volume.create_volume_snapshot())
        return self.path


class delete_volume_snapshot(Action):
    def __init__(self):
        Action.__init__(self)
        self.run_state = [resource.DETACHED, resource.ATTACHED]
        self.volume = None
        self.restate = None

    def check(self, all_volumes, tags):
        Action.check(self, all_volumes, tags)
        if len(all_volumes.detached + all_volumes.attached + all_volumes.deleted) == 0:
            print "There is no resource volume to delete_volume_snapshot.Must add create_volume"
            self.volume = resource.Volume()
            self.path.append(self.volume.create([]))
        volume_list = all_volumes.detached + all_volumes.attached + all_volumes.deleted
        random.shuffle(volume_list)
        for volume in volume_list:
            for snapshot in volume.snapshots:
                self.volume = volume
                return self.volume, snapshot
        else:
            self.volume = random.choice(volume_list)
            if self.volume.state == resource.DELETED:
                self.path.append(self.volume.recover())
            self.path.append(self.volume.create_volume_snapshot())
        return self.volume, self.volume.snapshots[-1]

    def run(self, tags):
        Action.run(self, tags)
        volume, snapshot = self.check(resource.all_volumes, tags)
        self.path.append(volume.delete_volume_snapshot(snapshot))
        return self.path


class use_volume_snapshot(Action):
    def __init__(self):
        Action.__init__(self)
        self.run_state = [resource.DETACHED, resource.ATTACHED]
        self.volume = None
        self.restate = None

    def check(self, all_volumes, tags):
        Action.check(self, all_volumes, tags)
        if len(all_volumes.detached + all_volumes.attached + all_volumes.deleted) == 0:
            print "There is no resource volume to use_volume_snapshot.Must add create_volume"
            self.volume = resource.Volume()
            self.path.append(self.volume.create([]))
        volume_list = all_volumes.detached + all_volumes.attached + all_volumes.deleted
        random.shuffle(volume_list)
        for volume in volume_list:
            for snapshot in volume.snapshots:
                self.volume = volume
                if self.volume.state == resource.ATTACHED and self.volume.vm.state == resource.RUNNING:
                    self.restate = True
                    self.path.append(self.volume.vm.stop())
                elif self.volume.state == resource.DELETED:
                    self.path.append(self.volume.recover())
                return self.volume, snapshot
        else:
            self.volume = random.choice(volume_list)
            if self.volume.state == resource.DELETED:
                self.path.append(self.volume.recover())
                self.path.append(self.volume.create_volume_snapshot())
            elif self.volume.state == resource.ATTACHED and self.volume.vm.state == resource.RUNNING:
                self.restate = True
                self.path.append(self.volume.create_volume_snapshot())
                self.path.append(self.volume.vm.stop())
            else:
                self.path.append(self.volume.create_volume_snapshot())
            return self.volume, self.volume.snapshots[-1]

    def run(self, tags):
        Action.run(self, tags)
        volume, snapshot = self.check(resource.all_volumes, tags)
        self.path.append(volume.use_volme_snapshot(snapshot))
        if self.restate:
            self.path.append(volume.vm.start())
        return self.path


class create_volume_backup(Action):
    def __init__(self):
        Action.__init__(self)
        self.run_state = [resource.DETACHED, resource.ATTACHED]
        self.vm = None
        self.volume = None
        self.restop = False
        self.redetach = False

    def check(self, all_volumes, tags):
        Action.check(self, all_volumes, tags)
        if len(all_volumes.detached + all_volumes.attached) == 0:
            print "There is no resource volume to create_volume_backup.Must add create_volume"
            self.volume = resource.Volume()
            self.path.append(self.volume.create([]))
        if len(resource.all_vms.stopped + resource.all_vms.running) == 0:
            print "There is no resource volume to create_volume_backup.Must add create_vm"
            self.vm = resource.Vm()
            self.path.append(self.vm.create([]))
        self.volume = random.choice(all_volumes.detached * 2 + all_volumes.attached * 3)
        if self.volume.state == resource.ATTACHED and self.volume.vm.state == resource.RUNNING:
            return self.volume
        elif self.volume.state == resource.ATTACHED and self.volume.vm.state == resource.STOPPED:
            self.restop = True
            self.path.append(self.volume.vm.start())
        elif self.volume.state == resource.DETACHED:
            self.vm = random.choice(resource.all_vms.running * 3 + resource.all_vms.stopped)
            self.redetach = True
            self.path.append(self.volume.attach(self.vm))
            if self.vm.state == resource.STOPPED:
                self.restop = True
                self.path.append(self.vm.start())
        return self.volume

    def run(self, tags):
        Action.run(self, tags)
        volume = self.check(resource.all_volumes, tags)
        self.path.append(volume.create_volume_backup())
        if self.restop:
            self.path.append(volume.vm.stop())
        if self.redetach:
            self.path.append(volume.detach())
        return self.path


class delete_volume_backup(Action):
    def __init__(self):
        Action.__init__(self)
        self.run_state = [resource.DETACHED, resource.ATTACHED]
        self.vm = None
        self.volume = None
        self.redetach = False
        self.restop = False

    def check(self, all_volumes, tags):
        Action.check(self, all_volumes, tags)
        if len(all_volumes.detached + all_volumes.attached + all_volumes.deleted) == 0:
            print "There is no resource volume to delete_volume_backup.Must add create_volume"
            self.volume = resource.Volume()
            self.path.append(self.volume.create([]))
        if len(resource.all_vms.stopped + resource.all_vms.running) == 0:
            print "There is no resource volume to create_volume_backup.Must add create_vm"
            self.vm = resource.Vm()
            self.path.append(self.vm.create([]))
        volume_list = all_volumes.detached + all_volumes.attached + all_volumes.deleted
        random.shuffle(volume_list)
        for volume in volume_list:
            for backup in volume.backups:
                if not backup.groupId:
                    self.volume = volume
                    return self.volume, backup
        else:
            self.volume = random.choice(volume_list)
            if self.volume.state == resource.DELETED:
                self.path.append(self.volume.recover())
            if self.volume.state == resource.ATTACHED and self.volume.vm.state == resource.STOPPED:
                self.restop = True
                self.path.append(self.volume.vm.start())
            if self.volume.state == resource.DETACHED:
                self.vm = random.choice(resource.all_vms.running * 3 + resource.all_vms.stopped)
                self.redetach = True
                self.path.append(self.volume.attach(self.vm))
                if self.vm.state == resource.STOPPED:
                    self.restop = True
                    self.path.append(self.vm.start())
            self.path.append(self.volume.create_volume_backup())
        return self.volume, self.volume.backups[-1]

    def run(self, tags):
        Action.run(self, tags)
        volume, backup = self.check(resource.all_volumes, tags)
        self.path.append(volume.delete_volume_backup(backup))
        if self.restop:
            self.path.append(volume.vm.stop())
        if self.redetach:
            self.path.append(volume.detach())
        return self.path


class use_volume_backup(Action):
    def __init__(self):
        Action.__init__(self)
        self.run_state = [resource.DETACHED, resource.ATTACHED]
        self.vm = None
        self.volume = None
        self.restart = False
        self.redetach = False
        self.restop = False
        self.reha = False

    def check(self, all_volumes, tags):
        Action.check(self, all_volumes, tags)
        if len(all_volumes.detached + all_volumes.attached + all_volumes.deleted) == 0:
            print "There is no resource volume to use_volume_backup.Must add create_volume"
            self.volume = resource.Volume()
            self.path.append(self.volume.create([]))
        if len(resource.all_vms.stopped + resource.all_vms.running) == 0:
            print "There is no resource volume to create_volume_backup.Must add create_vm"
            self.vm = resource.Vm()
            self.path.append(self.vm.create([]))
        volume_list = all_volumes.detached + all_volumes.attached + all_volumes.deleted
        random.shuffle(volume_list)
        for volume in volume_list:
            for backup in volume.backups:
                if not backup.groupId:
                    self.volume = volume
                    if self.volume.state == resource.DELETED:
                        self.path.append(self.volume.recover())
                    if self.volume.state == resource.DETACHED and resource.MINI:
                        self.redetach = True
                        self.vm = random.choice(resource.all_vms.running * 3 + resource.all_vms.stopped)
                        self.path.append(self.volume.attach(self.vm))
                    if self.volume.state == resource.ATTACHED and self.volume.vm.state == resource.RUNNING:
                        self.restart = True
                        if self.volume.vm.haveHA:
                            self.reha = True
                            self.path.append(self.volume.vm.change_ha())
                        self.path.append(self.volume.vm.stop())
                    return self.volume, backup
        else:
            self.restart = True
            self.volume = random.choice(volume_list)
            if self.volume.state == resource.DELETED:
                self.path.append(self.volume.recover())
            if self.volume.state == resource.DETACHED:
                self.redetach = True
                self.vm = random.choice(resource.all_vms.running * 3 + resource.all_vms.stopped)
                self.path.append(self.volume.attach(self.vm))
            if self.volume.state == resource.ATTACHED and self.volume.vm.state == resource.STOPPED:
                self.restart = False
                self.path.append(self.volume.vm.start())
            self.path.append(self.volume.create_volume_backup())
            if self.volume.vm.haveHA:
                self.reha = True
                self.path.append(self.volume.vm.change_ha())
            self.path.append(self.volume.vm.stop())
            return self.volume, self.volume.backups[-1]

    def run(self, tags):
        Action.run(self, tags)
        volume, backup = self.check(resource.all_volumes, tags)
        self.path.append(volume.use_volume_backup(backup))
        if self.reha:
            self.path.append(volume.vm.change_ha())
        if self.restart:
            self.path.append(volume.vm.start())
        if self.redetach:
            self.path.append(volume.detach())
        return self.path


class create_vm_snapshot(Action):
    def __init__(self):
        Action.__init__(self)
        self.run_state = [resource.RUNNING, resource.STOPPED]

    def check(self, all_vms, tags):
        Action.check(self, all_vms, tags)
        if (len(all_vms.stopped + all_vms.running)) == 0:
            print "There is no resource vm to change_ha.Must add create_vm"
            self.path.append(resource.Vm().create([]))
        return random.choice(all_vms.stopped + all_vms.running)

    def run(self, tags):
        Action.run(self, tags)
        vm = self.check(resource.all_vms, tags)
        self.path.append(vm.create_vm_snapshot())
        return self.path


class delete_vm_snapshot(Action):
    def __init__(self):
        Action.__init__(self)
        self.run_state = [resource.RUNNING, resource.STOPPED]

    def check(self, all_vms, tags):
        Action.check(self, all_vms, tags)
        if (len(all_vms.stopped + all_vms.running)) == 0:
            print "There is no resource vm to change_ha.Must add create_vm"
            vm1 = resource.Vm()
            self.path.append(vm1.create([]))
            self.path.append(vm1.create_vm_snapshot())
            return vm1, vm1.snapshots[0]
        vm_list = all_vms.stopped + all_vms.running
        random.shuffle(vm_list)
        for vm in vm_list:
            if vm.snapshots:
                for snapshot in vm.snapshots:
                    if snapshot.groupId:
                        return vm, snapshot
        else:
            vm = random.choice(all_vms.stopped + all_vms.running)
            self.path.append(vm.create_vm_snapshot())
            return vm, vm.snapshots[0]

    def run(self, tags):
        Action.run(self, tags)
        vm, snapshot = self.check(resource.all_vms, tags)
        self.path.append(vm.delete_vm_snapshot(snapshot.groupId))
        return self.path


class use_vm_snapshot(Action):
    def __init__(self):
        Action.__init__(self)
        self.run_state = resource.STOPPED
        self.restart = False

    def check(self, all_vms, tags):
        Action.check(self, all_vms, tags)
        if (len(all_vms.stopped + all_vms.running) - len(all_vms.ha)) == 0:
            print "There is no resource vm to start.Must add create_vm"
            vm1 = resource.Vm()
            self.path.append(vm1.create([]))
            self.path.append(vm1.create_vm_snapshot())
            self.path.append(vm1.stop())
        if len(all_vms.stopped) > 0:
            random.shuffle(all_vms.stopped)
            for vm in all_vms.stopped:
                for snapshot in vm.snapshots:
                    if snapshot.groupId:
                        return vm, snapshot
            else:
                vm = random.choice(all_vms.stopped)
                self.path.append(vm.create_vm_snapshot())
                return vm, vm.snapshots[0]
        self.restart = True
        vm_list = all_vms.get_not_ha_resource()
        random.shuffle(vm_list)
        for vm in vm_list:
            for snapshot in vm.snapshots:
                if snapshot.groupId:
                    self.path.append(vm.stop())
                    return vm, snapshot
        else:
            vm = random.choice(all_vms.get_not_ha_resource())
            self.path.append(vm.create_vm_snapshot())
            self.path.append(vm.stop())
            return vm, vm.snapshots[0]

    def run(self, tags):
        Action.run(self, tags)
        vm, snapshot = self.check(resource.all_vms, tags)
        self.path.append(vm.use_vm_snapshot(snapshot.groupId))
        if self.restart:
            self.path.append(vm.start())
        return self.path


class detach_vm_snapshot(Action):
    def __init__(self):
        Action.__init__(self)

    def check(self, all_snapshots, tags):
        if len(all_snapshots.group) == 0:
            self.path.extend(create_vm_snapshot().run([]))
        group, snapshot_list = random.choice(all_snapshots.group.items())
        for snapshot in snapshot_list:
            if "vm" in snapshot.name :
                return snapshot

    def run(self, tags):
        Action.run(self, tags)
        snapshot = self.check(resource.all_snapshots, tags)
        self.path.append(snapshot.detach_vm_snapshot())
        return self.path


class batch_delete_snapshots(Action):
    def __init__(self):
        Action.__init__(self)

    def check(self, all_snapshots, tags):
        Action.check(self, all_snapshots, tags)
        if len(all_snapshots.enabled) != 0:
            if len(all_snapshots.enabled) > 2:
                return random.sample(all_snapshots.enabled, 2)
            return all_snapshots.enabled
        else:
            if len(resource.all_vms.running + resource.all_vms.stopped) == 0:
                vm = resource.Vm()
                self.path.append(vm.create([]))
            else:
                vm = random.choice(resource.all_vms.running + resource.all_vms.stopped)

            self.path.append(vm.create_root_snapshot())
            return vm.snapshots

    def run(self, tags):
        Action.run(self, tags)
        snapshots = self.check(resource.all_snapshots, tags)
        self.path.append(resource.batch_delete_snapshot(snapshots))
        return self.path


class add_iso(Action):
    def __init__(self):
        Action.__init__(self)

    def check(self, all_images, tags):
        Action.check(self, all_images, tags)

    def run(self, tags):
        Action.run(self, tags)
        image = resource.Image()
        image.format = resource.ISO
        self.path.append(image.add())


class add_image(Action):
    def __init__(self):
        Action.__init__(self)

    def check(self, all_images, tags):
        Action.check(self, all_images, tags)

    def run(self, tags):
        Action.run(self, tags)
        Action.run(self, tags)
        image = resource.Image()
        self.path.append(image.add())
        return self.path


class delete_image(Action):
    def __init__(self):
        Action.__init__(self)

    def check(self, all_images, tags):
        Action.check(self, all_images, tags)
        if len(all_images.enabled + all_images.deleted) == 0:
            image = resource.Image()
            self.path.append(image.add())
            return image
        else:
            image = random.choice(all_images.enabled + all_images.deleted)
            if image.state == resource.DELETED:
                self.path.append(image.recover())
            return image

    def run(self, tags):
        Action.run(self, tags)
        image = self.check(resource.all_images, tags)
        self.path.append(image.delete())
        return self.path


class recover_image(Action):
    def __init__(self):
        Action.__init__(self)

    def check(self, all_images, tags):
        Action.check(self, all_images, tags)
        if len(all_images.enabled + all_images.deleted) == 0:
            image = resource.Image()
            self.path.append(image.add())
            return image
        else:
            image = random.choice(all_images.enabled + all_images.deleted)
            if image.state == resource.ENABLED:
                self.path.append(image.delete())
            return image

    def run(self, tags):
        Action.run(self, tags)
        image = self.check(resource.all_images, tags)
        self.path.append(image.recover())
        return self.path


class expunge_image(Action):
    def __init__(self):
        Action.__init__(self)

    def check(self, all_images, tags):
        Action.check(self, all_images, tags)
        if len(all_images.enabled + all_images.deleted) == 0:
            image = resource.Image()
            self.path.append(image.add())
            return image
        else:
            image = random.choice(all_images.enabled + all_images.deleted)
            if image.state == resource.ENABLED:
                self.path.append(image.delete())
            return image

    def run(self, tags):
        Action.run(self, tags)
        image = self.check(resource.all_images, tags)
        self.path.append(image.expunge())
        return self.path


class create_image_from_vm(Action):
    def __init__(self):
        Action.__init__(self)
        self.vm = None
        self.redelete = None

    def check(self, all_vms, tags):
        Action.check(self, all_vms, tags)
        if len(all_vms.stopped + all_vms.running + all_vms.deleted) == 0:
            self.vm = resource.Vm()
            self.path.append(self.vm.create([]))
        else:
            self.vm = random.choice(all_vms.stopped + all_vms.running + all_vms.deleted)
            if self.vm.state == resource.DELETED:
                self.redelete = True
                self.path.append(self.vm.recover())
        return self.vm

    def run(self, tags):
        Action.run(self, tags)
        vm = self.check(resource.all_vms, tags)
        self.path.append(vm.create_image())
        if self.redelete:
            self.path.append(vm.delete())
        return self.path


class create_image_from_volume(Action):
    def __init__(self):
        Action.__init__(self)
        self.volume = None
        self.redelete = None

    def check(self, all_volumes, tags):
        Action.check(self, all_volumes, tags)
        if len(all_volumes.attached + all_volumes.detached + all_volumes.deleted) == 0:
            self.volume = resource.Volume()
            self.path.append(self.volume.create([]))
        else:
            self.volume = random.choice(all_volumes.attached + all_volumes.detached + all_volumes.deleted)
            if self.volume.state == resource.DELETED:
                self.redelete = True
                self.path.append(self.volume.recover())
        return self.volume

    def run(self, tags):
        Action.run(self, tags)
        volume = self.check(resource.all_volumes, tags)
        self.path.append(volume.create_image())
        if self.redelete:
            self.path.append(volume.delete())
        return self.path


class create_image_from_snapshot(Action):
    def __init__(self):
        Action.__init__(self)
        self.snapshot = None

    def check(self, all_snapshots, tags):
        Action.check(self, all_snapshots, tags)
        if len(all_snapshots.enabled) != 0:
            return random.choice(all_snapshots.enabled)
        else:
            vm_tag = random.choice([True, False])
            if vm_tag:
                if len(resource.all_vms.running + resource.all_vms.stopped) == 0:
                    vm = resource.Vm()
                    self.path.append(vm.create([]))
                else:
                    vm = random.choice(resource.all_vms.running * 2 + resource.all_vms.stopped)
                self.path.append(vm.create_root_snapshot())
                return vm.snapshots[0]
            else:
                if len(resource.all_volumes.detached + resource.all_volumes.attached) == 0:
                    volume = resource.Volume()
                    self.path.append(volume.create([]))
                else:
                    volume = random.choice(resource.all_volumes.attached * 2 + resource.all_volumes.detached)
                self.path.append(volume.create_volume_snapshot())
                return volume.snapshots[0]

    def run(self, tags):
        Action.run(self, tags)
        snapshot = self.check(resource.all_snapshots, tags)
        self.path.append(snapshot.create_image())
        return self.path


class create_image_from_backup(Action):
    def __init__(self):
        Action.__init__(self)

    def check(self, all_backups, tags):
        Action.check(self, all_backups, tags)
        if len(all_backups.enabled) != 0:
            return random.choice(all_backups.enabled)
        else:
            if len(resource.all_vms.running + resource.all_vms.stopped) == 0:
                vm = resource.Vm()
                self.path.append(vm.create([]))
            else:
                vm = random.choice(resource.all_vms.running * 2 + resource.all_vms.stopped)
                if vm.state == resource.STOPPED:
                    self.restop = True
                    self.path.append(vm.start())
            self.path.append(vm.create_root_backup())
            if self.restop:
                self.path.append(vm.stop())
            return vm.backups[0]

    def run(self, tags):
        Action.run(self, tags)
        backup = self.check(resource.all_backups, tags)
        self.path.append(backup.create_image())


class create_vm_from_vmbackup(Action):
    def __init__(self):
        Action.__init__(self)
        self.snapshots = []

    def check(self, all_backups, tags):
        Action.check(self, all_backups, tags)
        if len(all_backups.enabled) != 0:
            backup_list = all_backups.enabled
            random.shuffle(backup_list)
            for backup in backup_list:
                if backup.groupId:
                    return backup
        else:
            if len(resource.all_vms.running + resource.all_vms.stopped) == 0:
                vm = resource.Vm()
                self.path.append(vm.create([]))
            else:
                vm = random.choice(resource.all_vms.running * 2 + resource.all_vms.stopped)
                if vm.state == resource.STOPPED:
                    self.restop = True
                    self.path.append(vm.start())
            self.path.append(vm.create_vm_backup())
            if self.restop:
                self.path.append(vm.stop())
            return vm.backups[0]

    def run(self, tags):
        Action.run(self, tags)
        backup = self.check(resource.all_backups, tags)
        self.path.append(backup.create_vm())
        return self.path


class create_vm_from_image(Action):
    def __init__(self):
        Action.__init__(self)
        self.redelete = False

    def check(self, all_images, tags):
        Action.check(self, all_images, tags)
        if len(all_images.enabled + all_images.deleted) != 0:
            image_list = all_images.enabled + all_images.deleted
            random.shuffle(image_list)
            for image in  image_list:
                if image.type == resource.ROOT:
                    if image.state == resource.DELETED:
                        self.redelete = True
                        self.path.append(image.recover())
                return image
        image = resource.Image()
        self.path.append(image.add())
        return image

    def run(self, tags):
        Action.run(self, tags)
        image = self.check(resource.all_images, tags)
        self.path.append(image.create_vm())
        if self.redelete:
            self.path.append(image.delete())
        return self.path


class create_vm_from_iso(Action):
    def __init__(self):
        Action.__init__(self)
        self.redelete = False

    def check(self, all_images, tags):
        Action.check(self, all_images, tags)
        if len(all_images.enabled + all_images.deleted) != 0:
            image_list = all_images.enabled + all_images.deleted
            random.shuffle(image_list)
            for image in image_list:
                if image.type == resource.ROOT and image.format == resource.ISO:
                    if image.state == resource.DELETED:
                        self.redelete = True
                        self.path.append(image.recover())
                    return image
        image = resource.Image()
        image.format = resource.ISO
        self.path.append(image.add())
        return image

    def run(self, tags):
        Action.run(self, tags)
        image = self.check(resource.all_images, tags)
        self.path.append(image.create_vm([]))
        if self.redelete:
            self.path.append(image.delete())
        return self.path


class create_volume_from_image(Action):
    def __init__(self):
        Action.__init__(self)
        self.redelete = False

    def check(self, all_images, tags):
        Action.check(self, all_images, tags)
        Action.check(self, all_images, tags)
        if len(all_images.enabled + all_images.deleted) != 0:
            image_list = all_images.enabled + all_images.deleted
            random.shuffle(image_list)
            for image in image_list:
                if image.type == resource.DATA:
                    if image.state == resource.DELETED:
                        self.redelete = True
                        self.path.append(image.recover())
                return image
        image = resource.Image()
        image.format = resource.ISO
        self.path.append(image.add())

    def run(self, tags):
        Action.run(self, tags)


if __name__ == "__main__":
    print create_volume().run([])
    print attach_volume().run([])
    print recover_image().run([])
