'''

Root Volume Image test with GetHostTask for Mini

@author: Jiajun
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import time
import os
import random

vm = None

def test():
    global vm
    global new_vm
    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = os.getenv('zstackHaVip')
    vm_creation_option = test_util.VmOption()
    image_name = os.environ.get('imageName_s')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    l3_name = os.environ.get('l3VlanNetworkName1')

    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    vm_creation_option.set_l3_uuids([l3_net_uuid])
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_name('test_vm_template')
    vm_creation_option.set_cpu_num(2)
    vm_creation_option.set_memory_size(2147483648)
    vm = test_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    vm.stop() 
    vm.check()

    volume_uuid = test_lib.lib_get_root_volume(vm.get_vm()).uuid
    bs_list = test_lib.lib_get_backup_storage_list_by_vm(vm.vm)

    test_util.test_logger('Start to check host task for APICreateRootVolumeTemplateFromRootVolumeMsg with at most 10 iterations')
    for i in range(1, 10):
        image_option = test_util.ImageOption()
        image_option.set_root_volume_uuid(volume_uuid)
        image_option.set_name('image_vm_template_image_'+str(i))
        image_option.set_backup_storage_uuid_list([bs_list[0].uuid])
        image = img_ops.create_root_volume_template(image_option)

        hosts = test_lib.lib_find_hosts_by_status("Connected")
        for host in hosts:
            tasks = host_ops.get_host_task(host.uuid.split(' '))
            for k,v in tasks.items():
                if v['runningTask']:
                    for rtask in v['runningTask']:
                        if 'apiName' in rtask:
                            if rtask['apiName'] == 'org.zstack.header.image.APICreateRootVolumeTemplateFromRootVolumeMsg':
                                test_util.test_pass('%s is found running on host %s with Ip %s' % (rtask['apiName'], host.uuid, host.managementIp))
                            else:
                                test_util.test_logger('task %s found running on host %s with Ip %s, but it is not APICreateRootVolumeTemplateFromRootVolumeMsg' % (rtask['apiName'], host.uuid, host.managementIp))

        test_util.test_logger('No task found at Iteration %s' % str(i))

    vm.destroy()
    vm.expunge()
    test_util.test_fail('No task found after 10 iterations for APICreateRootVolumeTemplateFromRootVolumeMsg')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    if vm:
        try:
            vm.destroy()
            vm.expunge()
        except:
            pass
