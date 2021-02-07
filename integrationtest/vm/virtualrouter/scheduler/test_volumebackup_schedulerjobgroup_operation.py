import zstackwoodpecker.operations.scheduler_operations as sch_ops
import zstackwoodpecker.operations.resource_operations as res_ops
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

    vm1 = test_stub.create_vlan_vm(os.environ.get('l3VlanNetworkName1'))
    vm2 = test_stub.create_vlan_vm(os.environ.get('l3VlanNetworkName1'))

    volume = test_stub.create_volume()
    volume.attach(vm2)

    test_obj_dict.add_vm(vm1)
    test_obj_dict.add_vm(vm2)
    test_obj_dict.add_volume(volume)

    parameters = {'retentionType': 'Count',
                  'retentionValue': '10',
                  'backupStorageUuids': imagestore.uuid,
                  'remoteBackupStorageUuid': '',
                  'networkWriteBandwidth': '',
                  'networkReadBandwidth': '',
                  'volumeReadBandwidth': '',
                  'volumeWriteBandwidth': ''}
    test_util.test_logger(parameters)

    job1 = sch_ops.create_scheduler_job(name='root_volume', description='vm1 root volume backup', target_uuid=vm1.get_vm().rootVolumeUuid,
                                        type=volumeBackup, parameters=parameters)
    job2 = sch_ops.create_scheduler_job(name='data_volume', description='data volume backup',
                                        target_uuid=volume.get_volume().uuid, type=volumeBackup,
                                        parameters=parameters)

    name1 = 'job_group'
    job_group = sch_ops.create_scheduler_job_group(name=name1, description='volumebackup', type=volumeBackup,
                                                   parameters=parameters)

    cond = res_ops.gen_query_conditions('uuid', '=', job_group.uuid)

    sch_ops.add_jobs_to_job_group([job1.uuid], job_group.uuid)
    job_group_inv = res_ops.query_resource(res_ops.SCHEDULERJOBGROUP, cond)[0]
    assert len(job_group_inv.jobsUuid) == 1

    sch_ops.add_jobs_to_job_group([job2.uuid], job_group.uuid)
    job_group_inv = res_ops.query_resource(res_ops.SCHEDULERJOBGROUP, cond)[0]
    assert len(job_group_inv.jobsUuid) == 2

    sch_ops.remove_jobs_from_job_group([job2.uuid], job_group.uuid)
    job_group_inv = res_ops.query_resource(res_ops.SCHEDULERJOBGROUP, cond)[0]
    assert len(job_group_inv.jobsUuid) == 1

    sch_ops.add_jobs_to_job_group([job2.uuid], job_group.uuid)
    job_group_inv = res_ops.query_resource(res_ops.SCHEDULERJOBGROUP, cond)[0]
    assert len(job_group_inv.jobsUuid) == 2

    sch_ops.remove_jobs_from_job_group([job1.uuid, job2.uuid], job_group.uuid)
    job_group_inv = res_ops.query_resource(res_ops.SCHEDULERJOBGROUP, cond)[0]
    assert len(job_group_inv.jobsUuid) == 0

    sch_ops.add_jobs_to_job_group([job1.uuid, job2.uuid], job_group.uuid)
    job_group_inv = res_ops.query_resource(res_ops.SCHEDULERJOBGROUP, cond)[0]
    assert len(job_group_inv.jobsUuid) == 2

    sch_ops.del_scheduler_job(job2.uuid)
    job_group_inv = res_ops.query_resource(res_ops.SCHEDULERJOBGROUP, cond)[0]
    assert len(job_group_inv.jobsUuid) == 1
    job2 = None

    trigger1 = sch_ops.create_scheduler_trigger('10sec', start_time=int(time.time() + 5), type='cron',
                                                cron='0/10 * * * * ?')
    trigger2 = sch_ops.create_scheduler_trigger('30sec', start_time=int(time.time() + 5), type='cron',
                                                cron='0/30 * * * * ?')

    sch_ops.add_scheduler_job_group_to_trigger(trigger1.uuid, job_group.uuid, triggerNow=True)
    job_group_inv = res_ops.query_resource(res_ops.SCHEDULERJOBGROUP, cond)[0]
    assert len(job_group_inv.triggersUuid) == 1

    sch_ops.add_scheduler_job_group_to_trigger(trigger2.uuid, job_group.uuid)
    job_group_inv = res_ops.query_resource(res_ops.SCHEDULERJOBGROUP, cond)[0]
    assert len(job_group_inv.triggersUuid) == 2

    sch_ops.remove_scheduler_job_group_from_trigger(trigger2.uuid, job_group.uuid)
    job_group_inv = res_ops.query_resource(res_ops.SCHEDULERJOBGROUP, cond)[0]
    assert len(job_group_inv.triggersUuid) == 1

    sch_ops.add_scheduler_job_group_to_trigger(trigger2.uuid, job_group.uuid, triggerNow=True)
    job_group_inv = res_ops.query_resource(res_ops.SCHEDULERJOBGROUP, cond)[0]
    assert len(job_group_inv.triggersUuid) == 2

    sch_ops.del_scheduler_trigger(trigger2.uuid)
    job_group_inv = res_ops.query_resource(res_ops.SCHEDULERJOBGROUP, cond)[0]
    assert len(job_group_inv.triggersUuid) == 1
    trigger2 = None

    sch_ops.del_scheduler_job_group(job_group.uuid)
    job_group_inv = res_ops.query_resource(res_ops.SCHEDULERJOBGROUP, cond)
    assert len(job_group_inv) == 0
    job_group = None

    cond1 = res_ops.gen_query_conditions('uuid', '=', job1.uuid)
    cond2 = res_ops.gen_query_conditions('uuid', '=', trigger1.uuid)

    job_inv = res_ops.query_resource(res_ops.SCHEDULERJOB, cond1)
    assert len(job_inv) == 0

    trigger_inv = res_ops.query_resource(res_ops.SCHEDULERTRIGGER, cond2)
    assert len(trigger_inv) == 1

    trigger1 = None
    job1 = None

    test_lib.lib_robot_cleanup(test_obj_dict)


def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
    if job1:
        sch_ops.del_scheduler_job(job1.uuid)
    if job2:
        sch_ops.del_scheduler_job(job1.uuid)
    if job_group:
        sch_ops.del_scheduler_job_group(job_group.uuid)
    if trigger1:
        sch_ops.del_scheduler_trigger(trigger1.uuid)
    if trigger2:
        sch_ops.del_scheduler_trigger(trigger2.uuid)

