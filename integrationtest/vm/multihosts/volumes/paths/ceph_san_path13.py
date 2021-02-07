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
                    path_list=[[TestAction.create_volume, "ceph_shared_volume1", "=ps_uuid::%s,scsi,shareable" % ceph_ps[0]],
                               [TestAction.create_volume, "san_shared_volume1", "=ps_uuid::%s,scsi,shareable" % san_ps[0]],  
                               [TestAction.create_volume, "san_shared_volume2", "=ps_uuid::%s,scsi,shareable" % san_ps[1]], 
                               [TestAction.create_volume, "san_shared_volume3", "=ps_uuid::%s,scsi,shareable" % san_ps[2]], 
                               [TestAction.attach_volume, san_vms[0].name, "ceph_shared_volume1"], 
                               [TestAction.attach_volume, san_vms[1].name, "ceph_shared_volume1"], 
                               [TestAction.attach_volume, san_vms[2].name, "ceph_shared_volume1"], 
                               [TestAction.attach_volume, ceph_vms[0].name, "ceph_shared_volume1"], 
                               [TestAction.attach_volume, san_vms[0].name, "san_shared_volume1"], 
                               [TestAction.attach_volume, san_vms[1].name, "san_shared_volume1"], 
                               [TestAction.attach_volume, san_vms[2].name, "san_shared_volume1"], 
                               [TestAction.attach_volume, ceph_vms[0].name, "san_shared_volume1"], 
                               [TestAction.attach_volume, san_vms[0].name, "san_shared_volume2"], 
                               [TestAction.attach_volume, san_vms[1].name, "san_shared_volume2"], 
                               [TestAction.attach_volume, san_vms[2].name, "san_shared_volume2"], 
                               [TestAction.attach_volume, ceph_vms[0].name, "san_shared_volume2"], 
                               [TestAction.attach_volume, san_vms[0].name, "san_shared_volume3"], 
                               [TestAction.attach_volume, san_vms[1].name, "san_shared_volume3"], 
                               [TestAction.attach_volume, san_vms[2].name, "san_shared_volume3"], 
                               [TestAction.attach_volume, ceph_vms[0].name, "san_shared_volume3"], 
                               san_vms[0].stop, 
                               san_vms[1].stop, 
                               san_vms[2].stop, 
                               ceph_vms[0].stop, 
                               san_vms[0].reinit,
                               san_vms[1].reinit,
                               san_vms[2].reinit, 
                               ceph_vms[0].reinit, 
                               san_vms[0].change_image(), 
                               san_vms[1].change_image(), 
                               san_vms[2].change_image(), 
                               ceph_vms[0].change_image(), 
                               san_vms[0].start, 
                               san_vms[1].start, 
                               san_vms[2].start, 
                               ceph_vms[0].start, 
                               [TestAction.create_volume_backup, san_vms[0].name + "-root", san_vms[0].name + "-backup1"], 
                               san_vms[0].stop, 
                               san_vms[1].stop, 
                               san_vms[2].stop, 
                               ceph_vms[0].stop, 
                               [TestAction.create_volume_snapshot, san_vms[0].name + '-root', san_vms[0].name + "-sp1"], 
                               [TestAction.create_volume_snapshot, san_vms[1].name + '-root', san_vms[1].name + "-sp1"], 
                               [TestAction.create_volume_snapshot, san_vms[2].name + '-root', san_vms[2].name + "-sp1"], 
                               [TestAction.create_volume_snapshot, ceph_vms[0].name + '-root', ceph_vms[0].name + "-sp1"],
                               [TestAction.create_volume_snapshot, "ceph_shared_volume1", "ceph_shared_volume1-sp1"], 
                               san_vms[0].start, 
                               san_vms[1].start, 
                               san_vms[2].start, 
                               ceph_vms[0].start,  
                               san_vms[0].migrate,
                               san_vms[1].migrate, 
                               san_vms[2].migrate, 
                               ceph_vms[0].migrate, 
                               san_vms[1].clone(full=True), 
                               ceph_vms[0].clone(full=True), 
                               san_vms[0].stop, 
                               san_vms[1].stop, 
                               san_vms[2].stop, 
                               ceph_vms[0].stop, 
                               [TestAction.use_volume_snapshot, san_vms[0].name + "-sp1"], 
                               [TestAction.use_volume_snapshot, san_vms[1].name + "-sp1"], 
                               [TestAction.use_volume_snapshot, san_vms[2].name + "-sp1"], 
                               [TestAction.use_volume_snapshot, ceph_vms[0].name + "-sp1"], 
                               san_vms[0].start, 
                               san_vms[1].start, 
                               san_vms[2].start, 
                               ceph_vms[0].start, 
                               VM(san_vms[1].cloned_name_list[0]).migrate, 
                               VM(ceph_vms[0].cloned_name_list[0]).migrate,   
                               [TestAction.attach_volume, san_vms[1].cloned_name_list[0], "san_shared_volume2"], 
                               [TestAction.attach_volume, ceph_vms[0].cloned_name_list[0], "san_shared_volume2"], 
                               [TestAction.use_volume_snapshot, "ceph_shared_volume1-sp1"], 
                               [TestAction.batch_delete_volume_snapshot, [san_vms[0].name + '-sp1', san_vms[1].name + '-sp1', san_vms[2].name + '-sp1', ceph_vms[0].name + '-sp1']], 
                               [TestAction.batch_delete_volume_snapshot, ["san_shared_volume1-sp1", "san_shared_volume2-sp1", "san_shared_volume3-sp1", "ceph_shared_volume1-sp1"]]
                               ])
    else:
        return dict(initial_formation="template3", path_list=[])
