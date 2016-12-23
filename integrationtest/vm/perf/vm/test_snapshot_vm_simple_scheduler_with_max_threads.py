'''
New Perf Test for snapshoting KVM VMs which were stopped.
The snapshot number will depend on the environment variable: ZSTACK_TEST_NUM
This case's max thread is 1000

@author: Carl
'''

import os
import time
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.operations.scheduler_operations as schd_ops
import zstackwoodpecker.test_lib as test_lib
from test_stub import *

global snapshot_date
global vm_stat_flag

class Snapshot_VM_Simple_Scheduler_Parall(VM_Operation_Parall):
    date=int(time.time())
    def operate_vm_parall(self, vm_uuid):
        try:
            #test_lib.lib_get_root_volume_uuid(rebootvms.vms[0])
            vm=test_lib.lib_get_vm_by_uuid(vm_uuid)
            root_volume_uuid=test_lib.lib_get_root_volume_uuid(vm)
            sp_option = test_util.SnapshotOption()
            sp_option.set_name('simple_schduler_snapshot')
            sp_option.set_volume_uuid(root_volume_uuid)
            schd = vol_ops.create_snapshot_scheduler(sp_option, 'simple', 'simple_create_snapshot_scheduler',  0, 1, 1)
        except:
            self.exc_info.append(sys.exc_info())

    def query_snapshot_number(snapshot_name):
        cond = res_ops.gen_query_conditions('name', '=', snapshot_name)
        return res_ops.query_resource_count(res_ops.VOLUME_SNAPSHOT, cond)

    def check_operation_result(self):
        time.sleep(30)
        start_msg_mismatch = 1
        for k in range(0, 1000):
            for i in range(0, self.i):
                vm_stat_flag=0
                vm=test_lib.lib_get_vm_by_uuid(self.vms[i].uuid)
                root_volume_uuid=test_lib.lib_get_root_volume_uuid(vm)
                if not test_lib.lib_find_in_local_management_server_log(self.date+k, '[msg send]: {"org.zstack.header.volume.CreateVolumeSnapshotMsg', self.vms[i].uuid):
                    test_util.test_warn('CreateVolumeSnapshotMsg is expected to execute at %s' % (self.date+k))
                    vm_stat_flag=1
                start_msg_mismatch += 1
            if vm_stat_flag == 0:
                break
        if start_msg_mismatch > 1000:
            test_util.test_fail('%s of 1000 CreateVolumeSnapshotMsg not executed at expected timestamp' % (start_msg_mismatch))

def test():
    get_vm_con = res_ops.gen_query_conditions('type', '=', "UserVm")
    snapshotvms = Snapshot_VM_Simple_Scheduler_Parall(get_vm_con, "UserVm")
    snapshotvms.parall_test_run()
    snapshotvms.check_operation_result()
