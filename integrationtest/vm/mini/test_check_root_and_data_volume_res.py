'''
create vm with root volume and data volume, check existence of .res file
1. create vm, root volume and data volume
2. check whether .res files exist
3. delete vm, root volume and data
4. check wthether .res files deleted as expected

@author: chen.zhou
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import zstackwoodpecker.zstack_test.zstack_test_volume as test_volume_header
import time
import os
import random

vm = None

VM_CPU = [1, 2, 3, 4]

# 128M, 256M, 512M, 1G
VM_MEM = [134217728, 268435456, 536870912, 1073741824]
test_obj_dict = test_state.TestStateDict()

host_ip_list = []

def test():
    global vm
    vm_option = test_util.VmOption()
    pri_l3_name = 'l3VlanNetwork1'
    pri_l3_uuid = test_lib.lib_get_l3_by_name(pri_l3_name).uuid
    cluster_uuid = res_ops.query_resource(res_ops.CLUSTER)[0].uuid
    image_uuid = res_ops.query_resource(res_ops.IMAGE)[0].uuid

    vm_option.set_l3_uuids([pri_l3_uuid])
    vm_option.set_image_uuid(image_uuid)

    #query host ip
    host_ip_list.append(res_ops.query_resource(res_ops.HOST)[0].managementIp)
    host_ip_list.append(res_ops.query_resource(res_ops.HOST)[1].managementIp)

    for i in range(2):

        volume_option = test_util.VolumeOption()
        ps_uuid = res_ops.query_resource(res_ops.PRIMARY_STORAGE)[0].uuid
        volume_option.set_primary_storage_uuid(ps_uuid)
        disk_size = 21474836480 #20GB
        volume_option.set_diskSize(disk_size)
        volume_name_thin = "mini_data_disk_thin"

        volume_option.set_name(volume_name_thin)
        volume_option.set_system_tags(["volumeProvisioningStrategy::ThinProvisioning"])
        volume_thin = test_volume_header.ZstackTestVolume()
        volume_thin.set_volume(vol_ops.create_volume_from_diskSize(volume_option))
        #volume_thin.attach(vm)
        volume_thin_uuid = volume_thin.volume.uuid
        test_util.test_dsc('Successfully create data volume')

        vm_option.set_cpu_num(random.choice(VM_CPU))
        vm_option.set_memory_size(random.choice(VM_MEM))
        vm_option.set_name('mini_vm_%s'%i)
        vm = test_vm_header.ZstackTestVm()
        vm.set_creation_option(vm_option)
        vm.create()
        test_obj_dict.add_vm(vm)
        vm.check()
        test_util.test_dsc('Successfully create vm')

        vm_root_volume_uuid = vm.get_vm().rootVolumeUuid
        vm_uuid = vm.vm.uuid

        vol_ops.attach_volume(volume_thin_uuid, vm_uuid)
        test_util.test_dsc('Successfully attach data volume to vm')

        test_util.test_dsc('Start to check .res file in two hosts')
        for ip in host_ip_list:
            if test_lib.lib_execute_ssh_cmd(ip, 'root', 'password', 'test -f /etc/drbd.d/%s.res && echo "Found" || echo "Not exist"'%vm_root_volume_uuid) == 'Not exist\n':
                test_util.test_fail('Expect to find %s.res file but not'%vm_root_volume_uuid)
            if test_lib.lib_execute_ssh_cmd(ip, 'root', 'password', 'test -f /etc/drbd.d/%s.res && echo "Found" || echo "Not exist"'%volume_thin_uuid) == 'Not exist\n':
                test_util.test_fail('Expect to find %s.res file but not'%volume_thin_uuid)

        volume_thin.delete()
        volume_thin.expunge()
        vm.destroy()
        vm.expunge()

        for ip in host_ip_list:
            if test_lib.lib_execute_ssh_cmd(ip, 'root', 'password', 'test -f /etc/drbd.d/%s.res && echo "Found" || echo "Not exist"'%vm_root_volume_uuid) == 'Found\n':
                test_util.test_fail('Not expect to find %s.res file'%vm_root_volume_uuid)
            if test_lib.lib_execute_ssh_cmd(ip, 'root', 'password', 'test -f /etc/drbd.d/%s.res && echo "Found" || echo "Not exist"'%volume_thin_uuid) == 'Found\n':
                test_util.test_fail('Not expect to find %s.res file'%volume_thin_uuid)

def error_cleanup():
    global vm
    if vm:
        try:
            vm.destroy()
        except:
            pass