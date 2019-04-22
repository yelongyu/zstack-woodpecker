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
                    path_list=[[TestAction.create_volume, "san_vol1", "=ps_uuid::%s" % san_ps[0]], 
                               [TestAction.create_volume, "ceph_vol1", "=ps_uuid::%s" % ceph_ps[0]], 
                               san_vms[0].stop, 
                               [TestAction.change_vm_image, san_vms[0].name, "ttylinux", "ImageStoreBackupStorage"], 
                               [TestAction.ps_migrage_vm, san_vms[0].name], 
                               san_vms[0].reinit, 
                               san_vms[0].start,
                               [TestAction.attach_volume, san_vms[0].name, "san_vol1"], 
                               [TestAction.attach_volume, san_vms[0].name, "ceph_vol1"], 
                               san_vms[0].migrate, 
                               [TestAction.create_image_from_volume, san_vms[0].name, "image_created_from_%s" % san_vms[0].name], 
                               san_vms[0].stop, 
                               san_vms[0].clone(3, True), 
                               san_vms[0].start, 
                               [TestAction.create_image_from_volume, san_vms[0].cloned_name_list[0], "image_created_from_%s" % san_vms[0].cloned_name_list[0]], 
                               [TestAction.create_image_from_volume, san_vms[0].cloned_name_list[1], "image_created_from_%s" % san_vms[0].cloned_name_list[1]], 
                               [TestAction.create_image_from_volume, san_vms[0].cloned_name_list[2], "image_created_from_%s" % san_vms[0].cloned_name_list[2]], 
                               VM(san_vms[0].cloned_name_list[0]).migrate, 
                               VM(san_vms[0].cloned_name_list[1]).migrate, 
                               VM(san_vms[0].cloned_name_list[2]).migrate, 
                               [TestAction.create_volume_snapshot, san_vms[0].cloned_name_list[0] + "-root", san_vms[0].cloned_name_list[0] + "-sp"], 
                               [TestAction.create_volume_snapshot, san_vms[0].cloned_name_list[1] + "-root", san_vms[0].cloned_name_list[1] + "-sp"], 
                               [TestAction.create_volume_snapshot, san_vms[0].cloned_name_list[2] + "-root", san_vms[0].cloned_name_list[2] + "-sp"], 
                               [TestAction.detach_volume, "san_vol1"], 
                               [TestAction.detach_volume, "ceph_vol1"], 
                               ceph_vms[0].migrate, 
                               ceph_vms[0].stop, 
                               ceph_vms[0].change_image(), 
                               ceph_vms[0].change_image(), 
                               ceph_vms[0].start, 
                               [TestAction.attach_volume, ceph_vms[0].name, "san_vol1"], 
                               [TestAction.attach_volume, ceph_vms[0].name, "ceph_vol1"], 
                               ceph_vms[0].stop, 
                               ceph_vms[0].clone(3, True), 
                               ceph_vms[0].start, 
                               [TestAction.create_image_from_volume, ceph_vms[0].cloned_name_list[0], "image_created_from_%s" % ceph_vms[0].cloned_name_list[0]], 
                               [TestAction.create_image_from_volume, ceph_vms[0].cloned_name_list[1], "image_created_from_%s" % ceph_vms[0].cloned_name_list[1]], 
                               [TestAction.create_image_from_volume, ceph_vms[0].cloned_name_list[2], "image_created_from_%s" % ceph_vms[0].cloned_name_list[2]], 
                               VM(ceph_vms[0].cloned_name_list[0]).migrate, 
                               VM(ceph_vms[0].cloned_name_list[1]).migrate, 
                               VM(ceph_vms[0].cloned_name_list[2]).migrate, 
                               [TestAction.create_vm_by_image, "image_created_from_%s" % san_vms[0].cloned_name_list[1], 'qcow2', 'vm2', '=ps_uuid::%s' % random.choice(san_ps)], 
                               [TestAction.create_vm_by_image, "image_created_from_%s" % ceph_vms[0].cloned_name_list[1], 'qcow2', 'vm3', '=ps_uuid::%s' % random.choice(ceph_ps)], 
                               [TestAction.delete_vm, san_vms[0].cloned_name_list[0]],
                               [TestAction.delete_vm, san_vms[0].cloned_name_list[1]],
                               [TestAction.delete_vm, san_vms[0].cloned_name_list[2]],
                               [TestAction.delete_vm, ceph_vms[0].cloned_name_list[0]], 
                               [TestAction.delete_vm, ceph_vms[0].cloned_name_list[1]],
                               [TestAction.delete_vm, ceph_vms[0].cloned_name_list[2]],
                               ])
    else:
        return dict(initial_formation="template3", path_list=[])