import os
import time
import random
import apibinding.inventory as inventory
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import zstackwoodpecker.zstack_test.zstack_test_image as zstack_image_header
import zstackwoodpecker.zstack_test.zstack_test_snapshot as zstack_sp_header
import zstackwoodpecker.zstack_test.zstack_test_volume as zstack_volume_header
import zstackwoodpecker.operations.scenario_operations as sce_ops
import zstackwoodpecker.header.host as host_header

test_obj_dict = test_state.TestStateDict()

def create_vm_backup(vm_obj):
    bs = res_ops.query_resource(res_ops.BACKUP_STORAGE)[0]
    backup_option = test_util.BackupOption()
    backup_option.set_name("vm_backup")
    backup_option.set_volume_uuid(test_lib.lib_get_root_volume(vm_obj.get_vm()).uuid)
    backup_option.set_backupStorage_uuid(bs.uuid)
    backup = vol_ops.create_vm_backup(backup_option)
    return backup

def create_volume_backup(vm_obj):
    bs = res_ops.query_resource(res_ops.BACKUP_STORAGE)[0]
    backup_option = test_util.BackupOption()
    backup_option.set_name("volume_backup")
    backup_option.set_volume_uuid(test_lib.lib_get_root_volume(test_lib.lib_get_data_volumes(vm_obj.get_vm())[0].uuid)
    backup_option.set_backupStorage_uuid(bs.uuid)
    backup = vol_ops.create_backup(backup_option)
    return backup

def create_database_backup():
    name = "database_backup"
    bs = res_ops.query_resource(res_ops.BACKUP_STORAGE)[0]
    backup = vol.ops.create_database_backup(name, bs.uuid)
    return backup

def test():
    vm_name = "test_vm"
    bs = res_ops.query_resource(res_ops.BACKUP_STORAGE)[0]
    cond = res_ops.gen_query_conditions("system", '=', "false")
    cond = res_ops.gen_query_conditions("mediaType", '=', "RootVolumeTemplate", cond)
    cond = res_ops.gen_query_conditions("platform", '=', "Linux", cond)
    img_name = res_ops.query_resource(res_ops.IMAGE, cond)[0].name
    cond = res_ops.gen_query_conditions("category", '=', "Private")
    l3_name = res_ops.query_resource(res_ops.L3_NETWORK,cond)[0].name

    vm1 = test_stub.create_vm(vm_name, img_name, l3_name)
    vm2 = test_stub.create_vm(vm_name, img_name, l3_name)

    volume = test_stub.create_volume()
    volume.attach(vm1)

    test_obj_dict.add_vm(vm1)
    test_obj_dict.add_vm(vm2)
    test_obj_dict.add_volume(volume)

    volume_backup = create_volume_backup(vm1)
    vol_ops.sync_volume_backup(bs.uuid)
    vol_ops.sync_vm_backup(bs.uuid)
    vol_ops.sync_database_backup(bs.uuid)
   
    cond = res_ops.gen_query_conditions('volumeUuid', '=', volume.uuid)
    vol_backup = res_ops.query_resource(res_ops.VOLUME_BACKUP, cond)[0]
    assert volume_backup.uuid == vol_backup.uuid

    vm_backup = create_vm_backup(vm1)
    vol_ops.sync_volume_backup(bs.uuid)
    vol_ops.sync_vm_backup(bs.uuid)
    vol_ops.sync_database_backup(bs.uuid)

    cond = res_ops.gen_query_conditions('volumeUuid', '=', vm1.get_vm().rootVolumeUuid)
    root_backup = res_ops.query_resource(res_ops.VOLUME_BACKUP, cond)[0]
    cond_2 = res_ops.gen_query_conditions('volumeUuid', '=', test_lib.lib_get_data_volumes(vm1.get_vm())[0].uuid)
    data_backups = res_ops.query_resource(res_ops.VOLUME_BACKUP, cond_2)
    for data in data_backups:
        if data.groupUuid:
            data_backup = data
    for b in vm_backup:
        if b.volumeUuid == vm1.get_vm().rootVolumeUuid
            assert root_backup.uuid == b.uuid
        else:
            assert data_backup.uuid == b.uuid

    #disconnect BS
    command = 'systemctl stop zstack-imagestorebackupstorage.service'
    import zstacklib.utils.ssh as ssh
    ssh.execute(command, bs.hostname, bs.username, bs.password)
    while True:
        bs = res_ops.query_resource(res_ops.BACKUP_STORAGE)[0]
        if bs.status == "Disconnected":
            break
    backups = res_ops.query_resource(res_ops.VOLUME_BACKUP)
    for bk in backups:
        vol_ops.delete_volume_backup(bs.uuid, bk.uuid)

    #reconnect BS
    command = 'systemctl start zstack-imagestorebackupstorage.service'
    ssh.execute(command, bs.hostname, bs.username, bs.password)
    while True:
        bs = res_ops.query_resource(res_ops.BACKUP_STORAGE)[0]
        if bs.status == "Connected":
            break
    backups = res_ops.query_resource(res_ops.VOLUME_BACKUP)
    assert len(bakcups) == 3

    test_lib.lib_robot_cleanup(test_obj_dict)

def error_cleanup():
    test_lib.lib_robot_cleanup(test_obj_dict)
