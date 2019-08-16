import zstackwoodpecker.operations.scheduler_operations as sch_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.tag_operations as tag_ops
import zstackwoodpecker.operations.backupstorage_operations as bs_ops
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import time
import os

vmBackup = 'vmBackup'
volumeBackup = 'volumeBackup'

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

job1 = None
job2 = None
job_group = None
trigger1 = None
trigger2 = None


def test():
    global job1
    global job2
    global job_group
    global trigger1
    global trigger2

    imagestore = test_lib.lib_get_image_store_backup_storage()
    if imagestore == None:
        test_util.test_skip('Required imagestore to test')
    cond = res_ops.gen_query_conditions("tag", '=', "allowbackup")
    tags = res_ops.query_resource(res_ops.SYSTEM_TAG, cond)
    if not tags:
        tag_ops.create_system_tag(resourceType="ImageStoreBackupStorageVO", resourceUuid=imagestore.uuid, tag="allowbackup")
    
    cond = res_ops.gen_query_conditions("tag", '=', "remotebackup")
    tags = res_ops.query_resource(res_ops.SYSTEM_TAG, cond)
    if not tags:
        cond = res_ops.gen_query_conditions("state", '=', "Enabled")
        cond = res_ops.gen_query_conditions("status", '=', "Connected")
        hosts = res_ops.query_resource(res_ops.HOST, cond)
        if not hosts:
            test_util.test_fail("No host available for adding imagestore for backup test")
        cond = res_ops.gen_query_conditions("state", '=', "Enabled")
        cond = res_ops.gen_query_conditions("status", '=', "Connected")
        bs = res_ops.query_resource(res_ops.IMAGE_STORE_BACKUP_STORAGE, cond)[0]
        host = hosts[0]
        if host.managementIp == bs.hostname:
            host = hosts[1]
        bs_option = test_util.ImageStoreBackupStorageOption()
        bs_option.set_name("remote_bs")
        bs_option.set_url("/home/sftpBackupStorage")
        bs_option.set_hostname(host.managementIp)
        bs_option.set_password('password')
        bs_option.set_sshPort(host.sshPort)
        bs_option.set_username('root')
        bs_option.set_system_tags(["remotebackup"])
        bs_inv = bs_ops.create_image_store_backup_storage(bs_option)

        bs_ops.attach_backup_storage(bs_inv.uuid, host.zoneUuid)
        remote_uuid = bs_inv.uuid
    else:
        remote_uuid = tags[0].resourceUuid

    vm_name = "test_vm"
    cond = res_ops.gen_query_conditions("system", '=', "false")
    cond = res_ops.gen_query_conditions("mediaType", '=', "RootVolumeTemplate", cond)
    cond = res_ops.gen_query_conditions("platform", '=', "Linux", cond)
    img_name = res_ops.query_resource(res_ops.IMAGE, cond)[0].name
    cond = res_ops.gen_query_conditions("category", '=', "Private")
    l3_name = res_ops.query_resource(res_ops.L3_NETWORK,cond)[0].name

    vm1 = test_stub.create_vm(vm_name, img_name, l3_name)
    vm2 = test_stub.create_vm(vm_name, img_name, l3_name)

    volume = test_stub.create_volume()
    volume.attach(vm2)

    test_obj_dict.add_vm(vm1)
    test_obj_dict.add_vm(vm2)
    test_obj_dict.add_volume(volume)

    parameters = {'retentionType': 'Count',
                  'retentionValue': '10',
                  'backupStorageUuids': imagestore.uuid,
                  'remoteBackupStorageUuid': remote_uuid,
                  'networkWriteBandwidth': '',
                  'networkReadBandwidth': '',
                  'volumeReadBandwidth': '',
                  'fullBackupTriggerUuid': '',
                  'volumeWriteBandwidth': ''}
    test_util.test_logger(parameters)

    job1 = sch_ops.create_scheduler_job(name='vm1', description='vm1 backup', target_uuid=vm1.get_vm().rootVolumeUuid,
                                        type=vmBackup, parameters=parameters)
    job2 = sch_ops.create_scheduler_job(name='vm2', description='vm2 backup',
                                        target_uuid=vm2.get_vm().rootVolumeUuid, type=vmBackup,
                                        parameters=parameters)

    name1 = 'job_group'
    job_group = sch_ops.create_scheduler_job_group(name=name1, description='vmbackup', type=vmBackup,
                                                   parameters=parameters)

    cond = res_ops.gen_query_conditions('uuid', '=', job_group.uuid)

    sch_ops.add_jobs_to_job_group([job1.uuid], job_group.uuid)
    job_group_inv = res_ops.query_resource(res_ops.SCHEDULERJOBGROUP, cond)[0]
    assert len(job_group_inv.jobsUuid) == 1

    sch_ops.add_jobs_to_job_group([job2.uuid], job_group.uuid)
    job_group_inv = res_ops.query_resource(res_ops.SCHEDULERJOBGROUP, cond)[0]
    assert len(job_group_inv.jobsUuid) == 2

    trigger1 = sch_ops.create_scheduler_trigger('10min', start_time=int(time.time() + 5), type='cron',
                                                cron='0 0/10 * * * ?')

    sch_ops.add_scheduler_job_group_to_trigger(trigger1.uuid, job_group.uuid, triggerNow=True)
    job_group_inv = res_ops.query_resource(res_ops.SCHEDULERJOBGROUP, cond)[0]
    assert len(job_group_inv.triggersUuid) == 1

    time.sleep(60)
    cond = res_ops.gen_query_conditions('volumeUuid', '=', vm1.get_vm().rootVolumeUuid)
    backup = res_ops.query_resource(res_ops.VOLUME_BACKUP, cond)[0]
     
    assert len(backup.backupStorageRefs) == 2

    test_lib.lib_robot_cleanup(test_obj_dict)
    sch_ops.del_scheduler_job(job1.uuid)
    sch_ops.del_scheduler_job(job2.uuid)
    sch_ops.del_scheduler_job_group(job_group.uuid)
    sch_ops.del_scheduler_trigger(trigger1.uuid)
    bs_ops.delete_backup_storage(remote_uuid)
    cond = res_ops.gen_query_conditions("tag", '=', "allowbackup")
    tags = res_ops.query_resource(res_ops.SYSTEM_TAG, cond)
    tag_ops.delete_tag(tags[0].uuid)

def error_cleanup():
    global job1,job2,job_group,trigger1,trigger2
    test_lib.lib_error_cleanup(test_obj_dict)
    if job1:
        sch_ops.del_scheduler_job(job1.uuid)
    if job2:
        sch_ops.del_scheduler_job(job2.uuid)
    if job_group:
        sch_ops.del_scheduler_job_group(job_group.uuid)
    if trigger1:
        sch_ops.del_scheduler_trigger(trigger1.uuid)
    if trigger2:
        sch_ops.del_scheduler_trigger(trigger2.uuid)

