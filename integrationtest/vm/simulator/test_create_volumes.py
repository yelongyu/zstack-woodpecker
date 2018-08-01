'''
New Test For VM Operations

@author: Glody 
'''
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.account_operations as acc_ops
import apibinding.api_actions as api_actions
import apibinding.inventory as inventory
import threading
import time
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

case_flavor = dict(vol_100=             	dict(vol_num=100),
                   vol_1000=                    dict(vol_num=1000),
                   vol_10000=              	dict(vol_num=10000),
                   )
  
def create_vol(vol_name, disk_offering_uuid, host_uuid, ps_uuid, session_uuid=None):
    vol_option = test_util.VolumeOption()
    vol_option.set_name(vol_name)
    vol_option.set_disk_offering_uuid(disk_offering_uuid)
    vol_option.set_primary_storage_uuid(ps_uuid)
    vol_option.set_system_tags(['localStorage::hostUuid::%s' %host_uuid])
    if session_uuid:
        vol_option.set_session_uuid(session_uuid)
    test_stub.create_volume(vol_option)

def test():
    flavor = case_flavor[os.environ.get('CASE_FLAVOR')]
    num = flavor['vol_num']
    hostUuid = ''
    hostName = ''
    diskOfferingUuid = res_ops.query_resource_fields(res_ops.DISK_OFFERING)[0].uuid
    hosts = res_ops.query_resource_fields(res_ops.HOST)
    counter = 0
    for i in range(0, 500):
        hostUuid = hosts[i].uuid
        hostName = hosts[i].name
        clusterUuid = hosts[i].clusterUuid
        cond = res_ops.gen_query_conditions('cluster.uuid', '=', clusterUuid)
        psUuid = res_ops.query_resource_fields(res_ops.PRIMARY_STORAGE, cond)[0].uuid
        for j in range(0, 20):
            counter += 1
            if counter > num:
                test_util.test_pass("Create %s volumes finished" %num)
            volName = 'vol-'+str(j)+'-on-host-'+hostName
            thread = threading.Thread(target=create_vol, args=(volName, diskOfferingUuid, hostUuid, psUuid))
            while threading.active_count() > 100:
                time.sleep(5)
            thread.start()
    test_util.test_fail("Fail to create vms")
def error_cleanup():
    pass
