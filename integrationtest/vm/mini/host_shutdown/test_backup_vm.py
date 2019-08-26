'''

New Integration test for testing vm backup for mini with GetHostTask

@author: Jiajun
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.header.vm as vm_header
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import zstackwoodpecker.zstack_test.zstack_test_kvm_host as test_kvm_host
import zstackwoodpecker.header.host as host_header
import zstacklib.utils.linux as linux
import zstackwoodpecker.operations.host_operations as host_ops
import time
import os
import random
import threading


vm = None
test_stub = test_lib.lib_get_test_stub()

def back_up(vm_obj):
     global backup
     bs = res_ops.query_resource(res_ops.BACKUP_STORAGE)[0]
     backup_option = test_util.BackupOption()
     backup_option.set_name("test_compare")
     backup_option.set_volume_uuid(test_lib.lib_get_root_volume(vm_obj.get_vm()).uuid)
     backup_option.set_backupStorage_uuid(bs.uuid)
     backup = vol_ops.create_backup(backup_option)
     return backup

def test():
    global vm
    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = os.getenv('zstackHaVip')
    vm_cpu = 1
    vm_memory = 1073741824 #1G
    cond = res_ops.gen_query_conditions('name', '=', 'ttylinux')
    image_uuid = res_ops.query_resource(res_ops.IMAGE, cond)[0].uuid
    l3_network_uuid = res_ops.query_resource(res_ops.L3_NETWORK)[0].uuid
    vm = test_stub.create_mini_vm([l3_network_uuid], image_uuid, cpu_num = vm_cpu, memory_size = vm_memory)
    vm.check()

    for i in range(1, 10):
        thread = threading.Thread(target=back_up, args=(vm,))
        thread.start()

        hosts = test_lib.lib_find_hosts_by_status("Connected")
        for host in hosts:
            tasks = host_ops.get_host_task(host.uuid.split(' '))
            for k,v in tasks.items():
                if v['runningTask']:
                    for rtask in v['runningTask']:
                        if 'apiName' in rtask:
                            if rtask['apiName'] == 'org.zstack.header.storage.volume.backup.APICreateVolumeBackupMsg':
                                test_util.test_pass('%s is found running on host %s with Ip %s' % (rtask['apiName'], host.uuid, host.managementIp))
                            else:
                                test_util.test_logger('task %s found running on host %s with Ip %s, but it is not APICreateVolumeBackupMsg' % (rtask['apiName'], host.uuid, host.managementIp))

        test_util.test_logger('No task found at Iteration %s' % str(i))
        time.sleep(5)
  
    vm.destroy()
    vm.expunge()
    test_util.test_fail('No task found after 10 iterations for APICreateVolumeBackup')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    if vm:
        try:
            vm.destroy()
            vm.expunge()
        except:
            pass
