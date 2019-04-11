import zstackwoodpecker.test_state as ts_header
import zstackwoodpecker.operations.resource_operations as res_ops
import random
import os

TestAction = ts_header.TestAction

class VM(object):
    def __init__(self, name=None):
        self.name = name
        self.cloned_name_list = [self.name + '_cloned_vm%s' % i for i in range(5)]

    @property
    def start(self):
        return [TestAction.start_vm, self.name]

    @property
    def stop(self):
        return [TestAction.stop_vm, self.name]

    @property
    def migrate(self):
        return [TestAction.migrate_vm, self.name]

    @property
    def reinit(self):
        return [TestAction.reinit_vm, self.name]

    def change_image(self, bs_type='ImageStoreBackupStorage'):
        return [TestAction.change_vm_image, self.name, os.getenv('imageName_s'), bs_type]

    def clone(self, clone_num=1, full=False):
        if full:
            return [TestAction.clone_vm, self.name, ','.join(self.cloned_name_list[:clone_num]), "=full"]
        else:
            return [TestAction.clone_vm, self.name, ','.join(self.cloned_name_list[:clone_num])]

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
                               [TestAction.create_volume, "ceph_volume2", "=ps_uuid::%s" % ceph_ps[0]],
                               [TestAction.create_volume, "ceph_volume3", "=ps_uuid::%s" % ceph_ps[0]],
                               [TestAction.create_volume, "san_volume1", "=ps_uuid::%s" % random.choice(san_ps)],
                               [TestAction.attach_volume, san_vms[0].name, "ceph_volume1"],
                               san_vms[0].migrate,
                               [TestAction.create_volume_snapshot, "ceph_volume1", "ceph_volume1_snapshot1"],
                               [TestAction.detach_volume, "ceph_volume1"],
                               [TestAction.attach_volume, san_vms[0].name, "ceph_volume2"],
                               [TestAction.attach_volume, san_vms[1].name, "ceph_volume1"],
                               san_vms[1].migrate,
                               [TestAction.create_volume_snapshot, "ceph_volume1", "ceph_volume1_snapshot2"],
                               [TestAction.detach_volume, "ceph_volume1"],
                               [TestAction.attach_volume, san_vms[1].name, "ceph_volume3"],
                               [TestAction.attach_volume, san_vms[2].name, "ceph_volume1"],
                               san_vms[2].migrate,
                               [TestAction.create_volume_snapshot, "ceph_volume1", "ceph_volume1_snapshot3"],
                               [TestAction.attach_volume, ceph_vms[-1].name, "ceph_volume1"],
                               ceph_vms[-1].migrate,
                               [TestAction.detach_volume, "ceph_volume1"],
                               [TestAction.attach_volume, ceph_vms[-1].name, "ceph_volume1"],
                               [TestAction.create_volume_snapshot, san_vms[0].name + '-root', san_vms[0].name + '-sp1'],
                               [TestAction.create_volume_snapshot, san_vms[1].name + '-root', san_vms[0].name + '-sp1'],
                               [TestAction.create_volume_snapshot, san_vms[2].name + '-root', san_vms[0].name + '-sp1'],
                               [TestAction.create_volume_snapshot, ceph_vms[-1].name + '-root', ceph_vms[-1].name + '-sp1'],
                               [TestAction.create_volume_snapshot, "ceph_volume1", "ceph_volume1_snapshot1"],
                               ceph_vms[-1].migrate,
                               [TestAction.create_volume, "ceph_shared_volume1", "=ps_uuid::%s,scsi,shareable" % ceph_ps[0]],
                               [TestAction.create_volume, "san_shared_volume1", "=ps_uuid::%s,scsi,shareable" % random.choice(san_ps)],
                               [TestAction.attach_volume, san_vms[0].name, "ceph_shared_volume1"],
                               [TestAction.attach_volume, san_vms[1].name, "ceph_shared_volume1"],
                               [TestAction.attach_volume, san_vms[2].name, "ceph_shared_volume1"],
                               [TestAction.create_volume, "san_shared_volume1", "=ps_uuid::%s,scsi,shareable" % san_ps[0]],
                               [TestAction.attach_volume, san_vms[0].name, "san_shared_volume1"],
                               [TestAction.attach_volume, san_vms[1].name, "san_shared_volume1"],
                               [TestAction.attach_volume, san_vms[2].name, "san_shared_volume1"],
                               [TestAction.attach_volume, ceph_vms[-1].name, "ceph_shared_volume1"],
                               [TestAction.attach_volume, ceph_vms[-1].name, "san_shared_volume1"],
                               san_vms[0].migrate,
                               san_vms[1].migrate,
                               san_vms[2].migrate,
                               ceph_vms[-1].migrate,
                               [TestAction.create_volume_snapshot, san_vms[0].name + '-root', san_vms[0].name + '-sp2'],
                               [TestAction.create_volume_snapshot, san_vms[1].name + '-root', san_vms[0].name + '-sp2'],
                               [TestAction.create_volume_snapshot, san_vms[2].name + '-root', san_vms[0].name + '-sp2'],
                               [TestAction.create_volume_snapshot, ceph_vms[-1].name + '-root', ceph_vms[-1].name + '-sp2'],
                               [TestAction.detach_volume, "san_shared_volume1", san_vms[1].name],
                               [TestAction.detach_volume, "san_shared_volume1", san_vms[2].name],
                               [TestAction.detach_volume, "san_shared_volume1", ceph_vms[-1].name]
                               ])
    else:
        return dict(initial_formation="template3", path_list=[])

