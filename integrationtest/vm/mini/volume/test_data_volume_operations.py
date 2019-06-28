'''

Integration test for testing thick/thick data volume operations on mini.

@author: zhaohao.chen
'''

import apibinding.inventory as inventory
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_volume as test_volume_header
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.header.volume as volume_header
import time
import os
import random
import threading

PROVISION = ["volumeProvisioningStrategy::ThinProvisioning","volumeProvisioningStrategy::ThickProvisioning"]
round_num = 10
volume = None
vm = None
volumes = []
ts_attach = []
ts = []

#state
CREATED = volume_header.CREATED
DETACHED = volume_header.DETACHED
ATTACHED = volume_header.ATTACHED
DELETED = volume_header.DELETED
EXPUNGED = volume_header.EXPUNGED


def vol_random_ops(vol, vm, vm_uuid):
    i = 0
    while vol.state != EXPUNGED:
        test_util.test_logger("op round%s: volume state %s" % (i,vol.state))
        i += 1
        if vol.state == CREATED or vol.state == DETACHED:
            op = random.choice([vol.delete, vol.attach])
            if op == vol.attach:
                op(vm)
            else:
                op()
            continue
        elif vol.state == ATTACHED:
            op = random.choice([vol.delete, vol.detach])
            if op == vol.detach:
               op(vm_uuid)
            else:
               op()
            continue
        elif vol.state == DELETED:
            op = random.choice([vol.expunge, vol.recover])
            op()
            continue 
    return 

def test():
    global vm
    VM_CPU= 2
    VM_MEM = 2147483648
    #1.create vm
    vm_creation_option = test_util.VmOption()
    image_name = os.environ.get('imageName_s')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    l3_name = os.environ.get('l3VlanNetworkName1')
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    vm_creation_option.set_l3_uuids([l3_net_uuid])
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_name('Mini_vm_datavolume_test')
    vm_creation_option.set_cpu_num(VM_CPU)
    vm_creation_option.set_memory_size(VM_MEM)
    vm = test_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    vm.check()
    vm_uuid = vm.get_vm().uuid

    #2.data volume operations test
    volume_creation_option = test_util.VolumeOption()
    ps_uuid = res_ops.query_resource(res_ops.PRIMARY_STORAGE)[0].uuid
    volume_creation_option.set_primary_storage_uuid(ps_uuid)
    #create thin/thick data volume with random disksize and random provision type
    for i in range(round_num):
        volume_name = "volume_%s" % i
        volume_creation_option.set_name(volume_name)
        max_size = (res_ops.query_resource(res_ops.PRIMARY_STORAGE)[0].availableCapacity - 1073741824)/2
        disk_size = random.randint(1048576, max_size)
        volume_creation_option.set_diskSize(disk_size)
        volume_creation_option.set_system_tags([random.choice(PROVISION)])
        volume = test_volume_header.ZstackTestVolume()
        volume.set_volume(vol_ops.create_volume_from_diskSize(volume_creation_option))
        volume.check()
        volume.state = CREATED
        volumes.append(volume)
    for vol in volumes:
        t = threading.Thread(target=vol_random_ops,args=(vol, vm, vm_uuid))
        ts.append(t)
        test_util.test_logger("thread added")
        t.start()
        test_util.test_logger("thread started")
    for t in ts:
        t.join()
    test_util.test_pass("Mini Data Volume Operations Test Success")

def error_cleanup():
    global vm
    if vm:
        try:
            vm.destroy()
        except:
            pass
