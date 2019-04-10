import zstackwoodpecker.test_state as ts_header
import zstackwoodpecker.operations.resource_operations as res_ops
import random

TestAction = ts_header.TestAction

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
    san_vms = ['utility_vm_for_robot_test' + '-' + ps.name for ps in ps_inv if ps.type == 'SharedBlock']
    ceph_vms = ['utility_vm_for_robot_test' + '-' + ps.name for ps in ps_inv if ps.type == 'Ceph']

    if san_ps and ceph_ps:
        return dict(initial_formation="template3",
                    path_list=[[TestAction.create_volume, "volume1", "=ps_uuid::%s" % san_ps[0]],
                               [TestAction.attach_volume, san_vms[-1], "volume1"],
                               [TestAction.resize_volume, san_vms[-1], 5*1024*1024],
                               [TestAction.clone_vm, san_vms[-1], "vm2", "=full"],
                               [TestAction.detach_volume, "volume1"],
                               [TestAction.attach_volume, ceph_vms[0], "volume1"],
                               [TestAction.stop_vm, san_vms[-1]], 
                               [TestAction.reinit_vm, san_vms[-1]], 
                               [TestAction.start_vm, san_vms[-1]],
                               [TestAction.clone_vm, ceph_vms[0], "vm3"],
                               [TestAction.resize_volume, ceph_vms[0], 5*1024*1024], 
                               [TestAction.detach_volume, "volume1"],
                               [TestAction.create_image_from_volume, ceph_vms[0], 'image_created_from_%s' % ceph_vms[0], "=bs_uuid::%s" % imagestore[0].uuid],
                               [TestAction.create_vm_by_image, 'image_created_from_%s' % ceph_vms[0], 'qcow2', 'vm4', '=ps_uuid::%s' % random.choice(san_ps)],
                               [TestAction.stop_vm, 'vm4'],
                               [TestAction.ps_migrage_vm, 'vm4'],
                               [TestAction.attach_volume, 'vm4', "volume1"]])
    else:
        return dict(initial_formation="template3", path_list=[])
