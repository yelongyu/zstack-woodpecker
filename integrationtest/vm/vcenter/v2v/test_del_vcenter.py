'''
test for deleting vcenter when migrating,migrate task should not be affected.
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
import zstackwoodpecker.operations.primarystorage_operations as ps_ops
import zstackwoodpecker.operations.longjob_operations as longjob_ops
import time
import zstacklib.utils.ssh as ssh
import os
import uuid

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
    url = 'vmware://%s' % vm.vm.uuid
    migrate_task = test_stub.convert_vm_from_foreign_hypervisor('test', url, cpuNum, memorySize, ps_uuid, [l3_uuid], cluster_uuid, v2v_conversion_host.uuid)

    vcenter_uuid = res_ops.get_resource(res_ops.VCENTER)[0].uuid
    vct_ops.delete_vcenter(vcenter_uuid)
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
    #cleanup
    test_lib.lib_error_cleanup(test_obj_dict)
   
def error_cleanup():
    global vm
    if vm:
        vm.destroy()
        vm.expunge()


