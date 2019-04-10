import zstackwoodpecker.test_state as ts_header
import zstackwoodpecker.operations.resource_operations as res_ops
import random

TestAction = ts_header.TestAction

class VM(object):
    def __init__(self, name=None):
        self.name = name
        self.cloned_name = 'cloned_from_' + self.name

    def start(self):
        return [TestAction.start_vm, self.name]

    def stop(self):
        return [TestAction.stop_vm, self.name]

    def reinit(self):
        return [TestAction.reinit_vm, self.name]

    def migrate(self):
        return [TestAction.migrate_vm, self.name]

    def clone(self, full=False):
        if full:
            return [TestAction.clone_vm, self.name, "vm2", "=full"]
        else:
            return [TestAction.clone_vm, self.name, self.cloned_name]

def path():
    cond = res_ops.gen_query_conditions('state', '=', "Enabled")
    cond = res_ops.gen_query_conditions('status', '=', "Connected", cond)
    ps_inv = res_ops.query_resource(res_ops.PRIMARY_STORAGE, cond)
    cond_imagestore = res_ops.gen_query_conditions('type', '=', "ImageStoreBackupStorage", cond)
    cond_ceph = res_ops.gen_query_conditions('type', '=', "Ceph", cond)
    imagestore = res_ops.query_resource(res_ops.BACKUP_STORAGE, cond_imagestore)
    ceph_bs = res_ops.query_resource(res_ops.BACKUP_STORAGE, cond_ceph)
    san_ps = [ps.uuid for ps in ps_inv if ps.type == 'SharedBlock']
    ceph_ps = [ps.uuid for ps in ps_inv if ps.type == 'Ceph']
    san_vms = [VM('utility_vm_for_robot_test' + '-' + ps.name) for ps in ps_inv if ps.type == 'SharedBlock']
    ceph_vms = [VM('utility_vm_for_robot_test' + '-' + ps.name) for ps in ps_inv if ps.type == 'Ceph']
    vm2 = VM('vm2')

    if san_ps and ceph_ps:
        return dict(initial_formation="template3",
                    path_list=[[TestAction.create_volume, "ceph_volume1", "=ps_uuid::%s" % ceph_ps[0]],
                               [TestAction.create_volume_snapshot, "ceph_volume1", "ceph_volume1_snapshot1"],
                               [TestAction.attach_volume, san_vms[-1].name, "ceph_volume1"],
                               [TestAction.create_volume_snapshot, "ceph_volume1", "ceph_volume1_snapshot2"],
                               [TestAction.resize_volume, san_vms[-1].name, 5*1024*1024],
                               san_vms[-1].stop(), 
                               [TestAction.reinit_vm, san_vms[-1].name],
                               [TestAction.use_volume_snapshot, "ceph_volume1_snapshot1"],
                               san_vms[-1].start(),
                               [TestAction.detach_volume, "ceph_volume1"],
                               [TestAction.create_volume, "iscsi_volume1", "=ps_uuid::%s" % san_ps[0]],
                               [TestAction.attach_volume, san_vms[-1].name, "iscsi_volume1"],
                               san_vms[-1].migrate(),
                               [TestAction.create_volume_snapshot, "iscsi_volume1", "iscsi_volume1_snapshot1"],
                               [TestAction.detach_volume, "iscsi_volume1"],
                               [TestAction.create_volume_snapshot, "iscsi_volume1", "iscsi_volume1_snapshot2"],
                               [TestAction.ps_migrate_volume, "iscsi_volume1"],
                               [TestAction.create_volume_snapshot, "iscsi_volume1", "iscsi_volume1_snapshot3"],
                               [TestAction.attach_volume, san_vms[-1].name, "iscsi_volume1"],
                               san_vms[-1].stop(),
                               [TestAction.use_volume_snapshot, "iscsi_volume1_snapshot1"],
                               san_vms[-1].start(),
                               [TestAction.detach_volume, "iscsi_volume1"],
                               [TestAction.attach_volume, san_vms[0].name, "ceph_volume1"],
                               [TestAction.create_volume_snapshot, "ceph_volume1", "ceph_volume1_snapshot3"],
                               [TestAction.create_volume_snapshot, "iscsi_volume1", "iscsi_volume1_snapshot4"],
                               [TestAction.create_image_from_volume, san_vms[0].name, 'image_created_from_%s' % san_vms[0].name, "=bs_uuid::%s" % imagestore[0].uuid],
                               san_vms[-1].migrate(),
                               [TestAction.create_vm_by_image, 'image_created_from_%s' % san_vms[0].name, 'qcow2', vm2.name, '=ps_uuid::%s' % random.choice(ceph_ps)],
                               [TestAction.create_volume, "ceph_volume2", "=ps_uuid::%s" % ceph_ps[0]],
                               [TestAction.attach_volume, vm2.name, "ceph_volume2"],
                               [TestAction.detach_volume, "iscsi_volume1"],
                               vm2.migrate(),
                               [TestAction.attach_volume, vm2.name, "iscsi_volume1"],
                               [TestAction.create_volume_snapshot, "ceph_volume1", "ceph_volume2_snapshot1"],
                               [TestAction.create_volume_snapshot, "iscsi_volume1", "iscsi_volume1_snapshot4"],
                               vm2.stop(),
                               [TestAction.ps_migrate_volume, "iscsi_volume1"],
                               vm2.start(),
                               vm2.migrate()
                               ])
    else:
        return dict(initial_formation="template3", path_list=[])

