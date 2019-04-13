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
    iscsi_ps = [ps.uuid for ps in ps_inv if ps.type == 'SharedBlock']
    ceph_ps = [ps.uuid for ps in ps_inv if ps.type == 'Ceph']
    iscsi_vms = ['utility_vm_for_robot_test' + '-' + ps.name for ps in ps_inv if ps.type == 'SharedBlock']
    ceph_vms = ['utility_vm_for_robot_test' + '-' + ps.name for ps in ps_inv if ps.type == 'Ceph']

    if iscsi_ps and ceph_ps:
        return dict(initial_formation="template3",
                path_list=[[TestAction.create_volume, "volume1", "=ps_uuid::%s" % iscsi_ps[-1]], 
                           [TestAction.attach_volume, ceph_vms[0], "volume1"], 
                           [TestAction.create_volume_snapshot, "volume1", "snapshot-1"], 
                           [TestAction.resize_data_volume, "volume1", 5*1024*1024],
                           [TestAction.stop_vm, ceph_vms[0]], 
                           [TestAction.ps_migrate_volume, "volume1"], 
                           [TestAction.start_vm, ceph_vms[0]], 
                           [TestAction.create_volume_backup, "volume1", "backup-1"],
                           [TestAction.stop_vm, ceph_vms[0]], 
                           [TestAction.use_volume_backup, "backup-1"],
                           [TestAction.use_volume_snapshot, "snapshot-1"], 
                           [TestAction.start_vm, ceph_vms[0]], 
                           [TestAction.create_volume, "volume2", "=ps_uuid::%s" % ceph_ps[-1]],
                           [TestAction.attach_volume, ceph_vms[0], "volume2"],  
                           [TestAction.create_volume_backup, "volume1", "backup-2"], 
                           [TestAction.create_volume_backup, "volume2", "backup-3"], 
                           [TestAction.stop_vm, ceph_vms[0]],
                           [TestAction.reinit_vm, ceph_vms[0]], 
                           [TestAction.use_volume_backup, "backup-2"],
                           [TestAction.use_volume_backup, "backup-3"], 
                           [TestAction.start_vm, ceph_vms[0]], 
                           [TestAction.create_image_from_volume, ceph_vms[0], "image_created_from_%s" % ceph_vms[0], "=bs_uuid::%s" % ceph_bs[0].uuid], 
                           [TestAction.create_vm_by_image, "image_created_from_%s" % ceph_vms[0], 'qcow2', "vm2", "=ps_uuid::%s" % random.choice(ceph_ps)], 
                           [TestAction.detach_volume, "volume1"], 
                           [TestAction.detach_volume, "volume2"], 
                           [TestAction.attach_volume, "vm2", "volume1"],
                           [TestAction.attach_volume, "vm2", "volume2"],
                           [TestAction.create_volume_backup, "volume1", "backup-4"], 
                           [TestAction.create_volume_backup, "volume2", "backup-5"],
                           [TestAction.stop_vm, "vm2"],
                           [TestAction.ps_migrate_volume, "volume1"], 
                           [TestAction.start_vm, "vm2"]])
    else:
        return dict(initial_formation="template3", path_list=[])
