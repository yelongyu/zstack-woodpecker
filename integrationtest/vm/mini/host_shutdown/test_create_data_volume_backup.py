'''

Integration test for testing create thick/thick data volume backup with GetHostTask on mini.

@author: Jiajun
'''

import apibinding.inventory as inventory
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import zstackwoodpecker.zstack_test.zstack_test_volume as test_volume_header
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.operations.host_operations as host_ops
import time
import os
import random
import threading

test_obj_dict = test_state.TestStateDict()
def test():
    global test_obj_dict
    VM_CPU= 2
    VM_MEM = 2147483648 #2GB 

    #1.create VM
    vm_creation_option = test_util.VmOption()
    image_name = os.environ.get('imageName_s')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    l3_name = os.environ.get('l3VlanNetworkName1')
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    vm_creation_option.set_l3_uuids([l3_net_uuid])
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_cpu_num(VM_CPU)
    vm_creation_option.set_memory_size(VM_MEM)
    vm_creation_option.set_name('MINI_Backup_test')
    vm = test_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    vm.check()
    test_obj_dict.add_vm(vm)

    #2.create thin/thick data volume & attach to vm
    volume_creation_option = test_util.VolumeOption()
    ps_uuid = res_ops.query_resource(res_ops.PRIMARY_STORAGE)[0].uuid
    volume_creation_option.set_primary_storage_uuid(ps_uuid)
    max_size = (res_ops.query_resource(res_ops.PRIMARY_STORAGE)[0].availableCapacity - 1048576)/(20 * 512)
    disk_size = random.randint(2048, max_size) * 512
    #disk_size = 107374182400 #100GB
    volume_creation_option.set_diskSize(disk_size)
    volume_name_thick = "mini_data_volume_thick"
    volume_name_thin = "mini_data_volume_thin"
    #thick
    volume_creation_option.set_name(volume_name_thick)
    volume_creation_option.set_system_tags(['miniStorage::clusterUuid::%s' % (vm.get_vm().clusterUuid)])
    volume_thick = test_volume_header.ZstackTestVolume()
    volume_thick.set_volume(vol_ops.create_volume_from_diskSize(volume_creation_option))
    volume_thick.attach(vm)
    volume_thick_uuid = volume_thick.volume.uuid
    #thin
    volume_creation_option.set_name(volume_name_thin)
    volume_creation_option.set_system_tags(['volumeProvisioningStrategy::ThinProvisioning', 'miniStorage::clusterUuid::%s' % (vm.get_vm().clusterUuid)])
    #volume_creation_option.set_system_tags(["volumeProvisioningStrategy::ThinProvisioning"])
    volume_thin = test_volume_header.ZstackTestVolume()
    volume_thin.set_volume(vol_ops.create_volume_from_diskSize(volume_creation_option))
    volume_thin.attach(vm)
    volume_thin_uuid = volume_thin.volume.uuid

    #3.create thick/thin data volume backup
    backup_creation_option = test_util.BackupOption()
    bs_uuid = res_ops.query_resource(res_ops.BACKUP_STORAGE)[0].uuid
    backup_creation_option.set_backupStorage_uuid(bs_uuid)

    for i in range(1, 10):
        if random.choice([True, False]):
            #thick
            backup_name_thick = "mini_volume_backup_thick%s" % time.time()
            backup_creation_option.set_name(backup_name_thick)
            backup_creation_option.set_volume_uuid(volume_thick_uuid)
            thread = threading.Thread(target=vol_ops.create_backup, args=(backup_creation_option,))
            thread.start()
	else:
            #thin
            backup_name_thin = "mini_volume_backup_thin%s" % time.time()
            backup_creation_option.set_name(backup_name_thin)
            backup_creation_option.set_volume_uuid(volume_thin_uuid)
            thread = threading.Thread(target=vol_ops.create_backup, args=(backup_creation_option,))
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

    test_util.test_fail('No task found after 10 iterations for APICreateVolumeBackup')


def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)

def env_recover():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
