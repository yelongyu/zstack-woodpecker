'''
This is a per test case setup that do setup work before test case execution
@author: Quarkonics
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.deploy_operations as deploy_operations
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.zone_operations as zone_operations
import zstackwoodpecker.operations.backupstorage_operations as bs_operations
import zstackwoodpecker.operations.iam2_operations as iam2_ops
import os

def destroy_initial_database():
    zoneinvs = res_ops.query_resource_fields(res_ops.ZONE, [], None, ['uuid'])
    for zoneinv in zoneinvs:
        zone_operations.delete_zone(zoneinv.uuid)
    backstorageinvs = res_ops.query_resource_fields(res_ops.BACKUP_STORAGE, [], None, ['uuid'])
    for backstorageinv in backstorageinvs:
        bs_operations.delete_backup_storage(backstorageinv.uuid)
    iam2_ops.clean_iam2_enviroment()

def test():
    if os.environ.get('ZSTACK_SIMULATOR') == "yes":
        if os.environ.get('WOODPECKER_PARALLEL') != None and os.environ.get('WOODPECKER_PARALLEL') == '0':
            destroy_initial_database()
            deploy_operations.deploy_initial_database(test_lib.deploy_config, test_lib.all_scenario_config, test_lib.scenario_file)
        else:
            test_util.test_logger('Skip case setup since parallel testing')
