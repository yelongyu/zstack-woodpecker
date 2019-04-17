import zstackwoodpecker.operations.scheduler_operations as sch_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_util as test_util
import time

test_stub = test_lib.lib_get_test_stub()

def test():
    imagestore = test_lib.lib_get_image_store_backup_storage()
    if imagestore == None:
        test_util.test_skip('Required imagestore to test')
    image_uuid = test_stub.get_image_by_bs(imagestore.uuid)
    pss = res_ops.query_resource(res_ops.PRIMARY_STORAGE)
    ps_uuid = pss[0].uuid

    vmBackup = 'vmBackup'
    volumeBackup = 'volumeBackup'
    parameters = {'retentionType': 'Count',
                  'retentionValue': '10',
                  'backupStorageUuids': imagestore.uuid,
                  'remoteBackupStorageUuid': '',
                  'networkWriteBandwidth': '',
                  'networkReadBandwidth': '',
                  'volumeReadBandwidth': '',
                  'volumeWriteBandwidth': ''}
    test_util.test_logger(parameters)    

    vm1 = test_stub.create_vm(image_uuid=image_uuid, ps_uuid=ps_uuid)
    vm1_uuid = vm1.get_vm().uuid
    volume1 = test_stub.create_volume()
    vol1_uuid = volume1.get_volume().uuid
    test_lib.lib_attach_volume(vol1_uuid, vm1_uuid)
    job1 = sch_ops.create_scheduler_job(name='vm1', description='vm1 with volume backup', target_uuid=vm1_uuid, type=vmBackup, parameters=parameters)


    vm2 = test_stub.create_vm(image_uuid=image_uuid, ps_uuid=ps_uuid)
    vm2_uuid = vm2.get_vm().uuid
    volume2 = test_stub.create_volume()
    vol2_uuid = volume2.get_volume().uuid
    test_lib.lib_attach_volume(vol2_uuid, vm2_uuid)
    job2 = sch_ops.create_scheduler_job(name='vm2-root', description='vm2 root volume backup', target_uuid=vm2.get_vm().allVolumes[0].uuid, type=volumeBackup, parameters=parameters)

    name1 = 'job_group_1'
    job_group_1 = sch_ops.create_scheduler_job_group(name=name1, description='vmbackup', type=vmBackup, parameters=parameters)
    sch_ops.add_jobs_to_job_group([job1.uuid], job_group_1.uuid)

    name2 = 'job_group_2'
    job_group_2 = sch_ops.create_scheduler_job_group(name=name2, description='volumebackup', type=volumeBackup, parameters=parameters)
    sch_ops.add_jobs_to_job_group([job2.uuid], job_group_2.uuid)

    trigger = sch_ops.create_scheduler_trigger('10sec', start_time = int(time.time()+5), type = 'cron', cron = '0/10 * * * * ?')

    sch_ops.add_scheduler_job_group_to_trigger(trigger.uuid, job_group_1.uuid, triggerNow=True)
    sch_ops.add_scheduler_job_group_to_trigger(trigger.uuid, job_group_2.uuid, triggerNow=False)

    time.sleep(9)
    # check
    # vm1/vol1 backups.lenth == 2
    # vm2 backups.lenth == 1

    cond = res_ops.gen_query_conditions('volumeUuid', '=', vm1.get_vm().allVolumes[0].uuid)
    backups = res_ops.query_resource(res_ops.VOLUME_BACKUP, cond)

    assert len(backups) == 2

    cond = res_ops.gen_query_conditions('volumeUuid', '=', volume1.get_volume().uuid)
    backups = res_ops.query_resource(res_ops.VOLUME_BACKUP, cond)

    assert len(backups) == 2

    cond = res_ops.gen_query_conditions('volumeUuid', '=', vm1.get_vm().allVolumes[0].uuid)
    backups = res_ops.query_resource(res_ops.VOLUME_BACKUP, cond)

    assert len(backups) == 1

    cond = res_ops.gen_query_conditions('volumeUuid', '=',  volume1.get_volume().uuid)
    backups = res_ops.query_resource(res_ops.VOLUME_BACKUP, cond)

    assert len(backups) == 0

    sch_ops.remove_scheduler_job_from_trigger(trigger.uuid, job_group_1.uuid)
    # sch_ops.remove_scheduler_job_from_trigger(trigger.uuid, job_group_2.uuid)

    cond = res_ops.gen_query_conditions('uuid', '=', job_group_1.uuid)
    job_group_inv = res_ops.query_resource(res_ops.SCHEDULERJOBGROUP, cond)[0]

    assert len(job_group_inv.triggersUuid) == 0

    sch_ops.del_scheduler_trigger(trigger.uuid)

    cond = res_ops.gen_query_conditions('uuid', '=', trigger.uuid)
    trigger_inv = res_ops.query_resource(res_ops.SCHEDULERTRIGGER, cond)
    cond = res_ops.gen_query_conditions('uuid', '=', job_group_2.uuid)
    job_group_inv = res_ops.query_resource(res_ops.SCHEDULERJOBGROUP, cond)[0]

    assert len(job_group_inv.triggersUuid) == 0
    assert len(trigger_inv) == 0

    sch_ops.remove_jobs_from_job_group([job1.uuid], job_group_1.uuid)

    cond = res_ops.gen_query_conditions('uuid', '=', job_group_1.uuid)
    job_group_inv = res_ops.query_resource(res_ops.SCHEDULERJOBGROUP, cond)[0]

    assert len(job_group_inv.jobsUuid) == 0

    sch_ops.del_scheduler_job_group(job_group_2.uuid)

    cond = res_ops.gen_query_conditions('uuid', '=', job_group_2.uuid)
    job_group_inv = res_ops.query_resource(res_ops.SCHEDULERJOBGROUP, cond)

    assert len(job_group_inv) == 0

    cond = res_ops.gen_query_conditions('uuid', '=', job2.uuid)
    job_inv = res_ops.query_resource(res_ops.SCHEDULERJOB, cond)

    assert len(job_inv) == 0

def error_cleanup():
    pass
