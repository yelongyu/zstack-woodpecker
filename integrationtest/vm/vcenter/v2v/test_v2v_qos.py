'''
test for migrate vcenter vm with volume to zstack
1.Create a vcenter vm with volume
2.Create v2v conversion host 
3.Set qos for v2v conversion host
4.Create migrate task
5.Wait for task finished
6.Check the mem cpu storage and qos
@author: chenyuan.xu
'''

import apibinding.inventory as inventory
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.tag_operations as tag_ops
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.vcenter_operations as vct_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import time
import zstacklib.utils.ssh as ssh
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
vm = None

def test():
    global vm
    ova_image_name = 'centos-dhcp'
    network_pattern1 = os.environ['vcenterDefaultNetwork']
    cpuNum = 2
    memorySize = 2*1024*1024*1024

    cond = res_ops.gen_query_conditions('type', '!=', 'Vcenter')
    ps = res_ops.query_resource(res_ops.PRIMARY_STORAGE, cond)
    for i in ps:
        if (i.type == 'Ceph') or (i.type == 'Sharedblock'):
            break
    else:
        test_util.test_skip('Skip test on non ceph or sharedblock PS')
    ps_uuid = ps[0].uuid
    cond = res_ops.gen_query_conditions('primaryStorage.uuid', '=', ps_uuid)
    cluster_uuid = res_ops.query_resource(res_ops.CLUSTER, cond)[0].uuid
    cond = res_ops.gen_query_conditions('clusterUuid', '=', cluster_uuid)    
    host = res_ops.query_resource(res_ops.HOST, cond)[0]  

    new_offering = test_lib.lib_create_instance_offering(cpuNum = cpuNum, memorySize = memorySize)
    vm = test_stub.create_vm_in_vcenter(vm_name = 'v2v-test', image_name = ova_image_name, l3_name = network_pattern1, instance_offering_uuid = new_offering.uuid)
    vm.check()
    disk_offering = test_lib.lib_get_disk_offering_by_name(os.environ.get('smallDiskOfferingName'))
    volume_creation_option = test_util.VolumeOption()
    volume_creation_option.set_disk_offering_uuid(disk_offering.uuid)
    volume_creation_option.set_name('vcenter_volume')
    volume = test_stub.create_volume(volume_creation_option)
    test_obj_dict.add_volume(volume)
    volume.check()
    volume.attach(vm)

    l3_name = os.environ.get('l3VlanNetworkName1')
    l3_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    v2v_conversion_host = test_stub.add_v2v_conversion_host('v2v_host', host.uuid, '/tmp/zstack', 'VMWARE')
    tag_ops.create_system_tag("V2VConversionHostVO", v2v_conversion_host.uuid, "networkInboundBandwidth::167772160")
    url = 'vmware://%s' % vm.vm.uuid
    avail_mem = test_lib.lib_get_cpu_memory_capacity(host_uuids = [host.uuid]).availableMemory
    avail_cpu = test_lib.lib_get_cpu_memory_capacity(host_uuids = [host.uuid]).availableCpu
    avail_cap = test_lib.lib_get_storage_capacity(ps_uuids = [ps_uuid]).availableCapacity
    migrate_task = test_stub.convert_vm_from_foreign_hypervisor('test', url, cpuNum, memorySize, ps_uuid, [l3_uuid], cluster_uuid, v2v_conversion_host.uuid)

    for i in range(30):
        cond = res_ops.gen_query_conditions('uuid', '=', migrate_task.uuid)
        long_job = res_ops.query_resource(res_ops.LONGJOB, cond)[0]
        if long_job.state == 'Failed':
            test_util.test_fail('v2v long job failed.')
        elif long_job.state == 'Running':
            time.sleep(60)
        elif long_job.state == 'Succeeded':
            test_util.test_logger('v2v long job has been finished.')
            break
    avail_mem2 = test_lib.lib_get_cpu_memory_capacity(host_uuids = [host.uuid]).availableMemory
    avail_cpu2 = test_lib.lib_get_cpu_memory_capacity(host_uuids = [host.uuid]).availableCpu
    avail_cap2 = test_lib.lib_get_storage_capacity(ps_uuids = [ps_uuid]).availableCapacity

    if (avail_mem - memorySize) != avail_mem2:
        test_util.test_fail('Available memory: %d is different with expected available memory: %d' % (avail_mem2, avail_mem - memorySize))
    if (avail_cpu - cpuNum) != avail_cpu2:
        test_util.test_fail('Available cpuNum: %d is different with expected available cpuNum: %d' % (avail_cpu2, avail_cpu1 - memorySize))
    cond = res_ops.gen_query_conditions('type', '=', 'root')
    cond = res_ops.gen_query_conditions('primaryStorageUuid', '=', ps_uuid, cond)
    vm_root_volume_size = res_ops.query_resource(res_ops.VOLUME, cond)[0].size
    if (avail_cap - vm_root_volume_size - disk_offering.diskSize) != avail_cap2:
        test_util.test_fail('Available storage: %d is different with expected available storage: %d' % (avail_cap2, avail_cap - vm_root_volume_size - disk_offering.diskSize))
    actual_qos = (vm_root_volume_size + disk_offering.diskSize) / long_job.executeTime

    if actual_qos > 167772160:
        test_util.test_fail('Fail to set qos for converting vm, expect qos:167772160 < actual_qos:%s.' % actual_qos)

    #cleanup
    test_lib.lib_error_cleanup(test_obj_dict)
    test_util.test_pass("Migrate vcenter vm to zstack successfully.")



def error_cleanup():
    global vm
    if vm:
        vm.destroy()
        vm.expunge()
