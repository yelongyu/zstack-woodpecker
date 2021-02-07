import zstackwoodpecker.test_state as ts_header
import zstackwoodpecker.operations.resource_operations as res_ops
import random

TestAction = ts_header.TestAction

class VM(object):
    def __init__(self, name=None):
        self.name = name

    def start(self):
        return [TestAction.start_vm, self.name]

    def stop(self):
        return [TestAction.stop_vm, self.name]

    def reinit(self):
        return [TestAction.reinit_vm, self.name]

    def migrate(self):
        return [TestAction.migrate_vm, self.name]

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
                               [TestAction.attach_volume, san_vms[0].name, "ceph_volume1"],
                               [TestAction.create_volume_snapshot, "ceph_volume1", "ceph_volume1_snapshot2"],
                               [TestAction.create_data_vol_template_from_volume, "ceph_volume1", "volume_template1", "=bs_uuid::%s" % imagestore[0].uuid],
                               [TestAction.create_data_volume_from_image, "san_volume1", '=scsi, ps_uuid::%s' % random.choice(san_ps)],
                               [TestAction.create_volume_snapshot, "san_volume1", "san_volume1_snapshot1"],
                               [TestAction.attach_volume, ceph_vms[0].name, "san_volume1"],
                               [TestAction.create_volume_snapshot, "san_volume1", "san_volume1_snapshot2"],
                               ceph_vms[0].stop(),
                               [TestAction.use_volume_snapshot, "san_volume1_snapshot1"],
                               ceph_vms[0].start(),
                               [TestAction.create_volume_snapshot, "san_volume1", "san_volume1_snapshot3"],
                               [TestAction.detach_volume, "san_volume1"],
                               ceph_vms[0].migrate(),
                               [TestAction.ps_migrate_volume, "san_volume1"],
                               [TestAction.attach_volume, ceph_vms[0].name, "san_volume1"],
                               [TestAction.create_volume_snapshot, "san_volume1", "san_volume1_snapshot4"],
                               [TestAction.detach_volume, "san_volume1"],
                               [TestAction.attach_volume, san_vms[1].name, "san_volume1"],
                               [TestAction.create_volume_snapshot, "san_volume1", "san_volume1_snapshot5"],
                               san_vms[1].stop(),
                               [TestAction.use_volume_snapshot, "san_volume1_snapshot3"],
                               san_vms[1].start(),
                               [TestAction.detach_volume, "san_volume1"],
                               [TestAction.use_volume_snapshot, "san_volume1_snapshot4"],
                               [TestAction.create_data_vol_template_from_volume, "san_volume1", "volume_template2", "=bs_uuid::%s" % imagestore[0].uuid],
                               [TestAction.create_data_volume_from_image, "ceph_volume2", '=scsi, ps_uuid::%s' % random.choice(ceph_ps)],
                               [TestAction.create_volume_snapshot, "ceph_volume2", "ceph_volume1_snapshot1"],
                               [TestAction.attach_volume, san_vms[0].name, "ceph_volume2"],
                               [TestAction.create_volume_snapshot, "ceph_volume2", "ceph_volume1_snapshot2"],
                               san_vms[1].migrate(),
                               [TestAction.detach_volume, "ceph_volume2"],
                               [TestAction.attach_volume, ceph_vms[0].name, "ceph_volume2"],
                               [TestAction.create_volume_snapshot, "ceph_volume2", "ceph_volume1_snapshot3"],
                               ceph_vms[0].stop(),
                               [TestAction.use_volume_snapshot, "ceph_volume1_snapshot2"],
                               ceph_vms[0].start()
                               ])
    else:
        return dict(initial_formation="template3", path_list=[])

