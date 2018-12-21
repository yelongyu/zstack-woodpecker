'''
Test db backup operation

@author chenyuan.xu
'''
import os
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.operations.backupstorage_operations as bs_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.tag_operations as tag_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.operations.scheduler_operations as schd_ops
import json
import time

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    test_util.test_dsc('Create Scheduler Trigger and Scheduler Job')
    cond = res_ops.gen_query_conditions('type', '=', 'ImageStoreBackupStorage')
    bs = res_ops.query_resource(res_ops.BACKUP_STORAGE, cond)
    if not bs :
        test_util.test_skip('Not find image store type backup storage.')
    image_name = os.environ.get('imageName_net')
    l3_name = os.environ.get('l3PublicNetworkName')
    remote_bs_vm = test_stub.create_vm('remote_bs_vm', image_name, l3_name)
    test_obj_dict.add_vm(remote_bs_vm)
    image_name = os.environ.get('imageName_s')
    l3_name = os.environ.get('l3VlanNetworkName1')
    test_vm = test_stub.create_vm('test-vm', image_name, l3_name)
    test_obj_dict.add_vm(test_vm)
    add_local_bs_tag = tag_ops.create_system_tag('ImageStoreBackupStorageVO', bs[0].uuid,'allowbackup')
    #wait for vm start up 
    test_lib.lib_wait_target_up(remote_bs_vm.vm.vmNics[0].ip, '22', 90)
    remote_bs = test_stub.create_image_store_backup_storage('remote_bs', remote_bs_vm.vm.vmNics[0].ip, 'root', 'password', '/zstack_bs', '22')
    add_remote_bs = tag_ops.create_system_tag('ImageStoreBackupStorageVO', remote_bs.uuid,'remotebackup')
    zone_uuid = res_ops.query_resource(res_ops.ZONE)[0].uuid
    bs_ops.attach_backup_storage(remote_bs.uuid, zone_uuid)    
    parameters= {"retentionType":"Count","retentionValue":"1","backupStorageUuids":bs[0].uuid,"remoteBackupStorageUuid":""}
    schd_job = schd_ops.create_scheduler_job('backup_database_scheduler', 'backup_database_scheduler', '7ae6456c0b01324dae6d4bef358a5772', 'databaseBackup',parameters=parameters)
    schd_trigger = schd_ops.create_scheduler_trigger('backup_database_schedule',type='cron', cron='0 * * ? * *')
    schd_ops.add_scheduler_job_to_trigger(schd_trigger.uuid, schd_job.uuid)
    #wait for 60s *2
    time.sleep(120)
 
    db_backup1 = schd_ops.query_db_backup()
    if len(db_backup1) != 1:
        test_util.test_fail('there sholuld be 1 db backup,but now there are %s' % len(db_backup1))   
    db_backup2 = schd_ops.get_db_backup_from_imagestore(url = 'ssh://root:password@%s:22/zstack_bs' % bs[0].hostname)
    if len(db_backup2.backups) != 1:
        test_util.test_fail('there sholuld be 1 db backup,but now there are %s' % len(db_backup2.backups))

    db_url = schd_ops.export_db_backup_from_bs(bs[0].uuid, db_backup1[0].uuid) 
    test_util.test_dsc('export database backup successfully,url is %s' % db_url.databaseBackupUrl)
    schd_ops.sync_db_from_imagestore_bs(remote_bs.uuid, bs[0].uuid, db_backup1[0].uuid)
    test_vm.destroy()

    test_util.test_dsc('Recover db From BackupStorage')
    backupStorageUrl = 'ssh://root:password@%s:22/zstack_bs' % remote_bs_vm.vm.vmNics[0].ip
    recover_db = schd_ops.recover_db_from_backup(backupStorageUrl = backupStorageUrl, backupInstallPath = db_backup2.backups[0].installPath, mysqlRootPassword='zstack.mysql.password')
    #wait for db recover
    time.sleep(60)
    cond = res_ops.gen_query_conditions('name', '=', 'test-vm')
    vm = res_ops.query_resource(res_ops.VM_INSTANCE, cond)
    if not vm:
        test_util.test_fail('there sholuld be a vm after recovering db from remote backup bs')
    
    #wait for db recover
    time.sleep(60)
    db_backup3 = schd_ops.query_db_backup()
    zone.delete()
    recover_db = schd_ops.recover_db_from_backup(uuid=db_backup3[0].uuid, mysqlRootPassword='zstack.mysql.password')
    vm = res_ops.query_resource(res_ops.VM_INSTANCE, cond)
    if not vm:
        test_util.test_fail('there sholuld be a vm after recovering db from local backup bs')

    test_util.test_dsc('Clear env')
    schd_ops.del_scheduler_job(schd_job.uuid)
    schd_ops.del_scheduler_trigger(schd_trigger.uuid)
    tag_ops.delete_tag(add_local_bs_tag.uuid)
    bs_ops.delete_backup_storage(remote_bs.uuid)    
    bs_ops.reclaim_space_from_bs(bs[0].uuid)
    remote_vm.destroy()

def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)

    if schd_job:
        schd_ops.del_scheduler_job(schd_job.uuid)
    if schd_trigger:
        schd_ops.del_scheduler_trigger(schd_trigger.uuid)


