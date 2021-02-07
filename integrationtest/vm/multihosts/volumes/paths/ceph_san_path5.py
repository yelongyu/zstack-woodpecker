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
                path_list=[[TestAction.create_volume, "volume1", "=ps_uuid::%s" % ceph_ps[0]], 
                           [TestAction.attach_volume, iscsi_vms[0], "volume1"], 
                           [TestAction.create_volume_snapshot, "volume1", "snapshot-1"], 
                           [TestAction.stop_vm, iscsi_vms[0]], 
                           [TestAction.clone_vm, iscsi_vms[0], "vm2", "=full"], 
                           [TestAction.stop_vm, "vm2"], 
                           [TestAction.reinit_vm, "vm2"],
                           [TestAction.clone_vm, "vm2", "vm3", "=full"], 
                           [TestAction.stop_vm, "vm3"], 
                           [TestAction.clone_vm, "vm3", "vm4", "=full"], 
                           [TestAction.stop_vm, "vm4"], 
                           [TestAction.reinit_vm, "vm4"], 
                           [TestAction.clone_vm, "vm4", "vm5", "=full"], 
                           [TestAction.stop_vm, "vm5"], 
                           [TestAction.clone_vm, "vm5", "vm6", "=full"], 
                           [TestAction.stop_vm, "vm6"], 
                           [TestAction.reinit_vm, "vm6"], 
                           [TestAction.clone_vm, "vm6", "vm7", "=full"], 
                           [TestAction.stop_vm, "vm7"], 
                           [TestAction.clone_vm, "vm7", "vm8"], 
                           [TestAction.create_volume, "volume2", "=ps_uuid::%s" % iscsi_ps[-1]], 
                           [TestAction.detach_volume, "volume1"],
                           [TestAction.attach_volume, "vm8", "volume1"], 
                           [TestAction.attach_volume, "vm8", "volume2"], 
                           [TestAction.stop_vm, "vm8"],
                           [TestAction.clone_vm, "vm8", "vm9", "=full"], 
                           [TestAction.stop_vm, "vm9"], 
                           [TestAction.reinit_vm, "vm9"], 
                           [TestAction.clone_vm, "vm9", "vm10", "=full"],
                           [TestAction.migrate_vm, "vm10"]])
    else:
        return dict(initial_formation="template3", path_list=[])
