'''

New Integration Test for vm ha auto across cluster migrate .

@author: YeTian
@Date:   2019-02-19
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import zstackwoodpecker.operations.ha_operations as ha_ops
import zstackwoodpecker.operations.config_operations as conf_ops
import zstackwoodpecker.operations.scenario_operations as sce_ops
import time
import os
import tempfile
import uuid

test_stub = test_lib.lib_get_test_stub()
vm = None
tmp_file = '/tmp/%s' % uuid.uuid1().get_hex()
zstack_management_ip = os.environ.get('zstackManagementIp')

def test():
    global vm, host3_uuid

    if test_lib.lib_get_ha_enable() != 'true':
        test_util.test_skip("vm ha not enabled. Skip test")

    conf_ops.change_global_config('ha', 'allow.slibing.cross.clusters', 'true')

    vm_creation_option = test_util.VmOption()
    image_name = os.environ.get('imageName_s')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    #l3_name = os.environ.get('l3NoVlanNetworkName1')
    l3_name = os.environ.get('l3PublicNetworkName')
    host3_name = os.environ.get('hostName3')
    host4_name = os.environ.get('hostName4')

    conditions1 = res_ops.gen_query_conditions('name', '=', host3_name)
    host3_uuid = res_ops.query_resource(res_ops.HOST, conditions1)[0].uuid
    host3_ip = res_ops.query_resource(res_ops.HOST, conditions1)[0].managementIp

    conditions2 = res_ops.gen_query_conditions('name', '=', host4_name)
    host4_uuid = res_ops.query_resource(res_ops.HOST, conditions2)[0].uuid
    host4_ip = res_ops.query_resource(res_ops.HOST, conditions2)[0].managementIp

    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
    instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid
    vm_creation_option.set_l3_uuids([l3_net_uuid])
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_name('multihost_basic_vm')
    vm_creation_option.set_host_uuid(host3_uuid)
    vm = test_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    time.sleep(30)
    ha_ops.set_vm_instance_ha_level(vm.get_vm().uuid, "NeverStop")
    time.sleep(5)
    #vm.check()
    
    ssh_cmd1 = 'ssh  -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % host3_ip    
    cmd = '%s "poweroff" ' % ssh_cmd1
    process_result = test_stub.execute_shell_in_process(cmd, tmp_file)
        
    time.sleep(300)
    host3_status = res_ops.query_resource(res_ops.HOST, conditions1)[0].status    
    if host3_status == "Disconnected":
        conditions3 = res_ops.gen_query_conditions('uuid', '=', vm.vm.uuid)
        vm_status = res_ops.query_resource(res_ops.VM_INSTANCE, conditions3)[0].state
        vm_host_uuid = res_ops.query_resource(res_ops.VM_INSTANCE, conditions3)[0].hostUuid
        if vm_status != "Running" or vm_host_uuid != host4_uuid:         
            test_util.test_fail('Test ha vm auto across cluster start failed vm_status: %s, vm_host_uuid: %s', % (vm_status, vm_host_uuid))
    #vm.destroy()
    #conf_ops.change_global_config('ha', 'allow.slibing.cross.clusters', 'false')

    conditions4 = res_ops.gen_query_conditions('vmNics.ip', '=', host3_ip)
    vm3_uuid = sce_ops.query_resource(zstack_management_ip, res_ops.VM_INSTANCE, conditions4).inventories[0].uuid
    sce_ops.start_vm(zstack_management_ip, vm3_uuid)

    time.sleep(300)

    host3_new_status = res_ops.query_resource(res_ops.HOST, conditions1)[0].status    
    if host3_new_status == "Connected":
        conditions5 = res_ops.gen_query_conditions('vmNics.ip', '=', host4_ip)
        vm4_uuid = sce_ops.query_resource(zstack_management_ip, res_ops.VM_INSTANCE, conditions5).inventories[0].uuid
        sce_ops.stop_vm(zstack_management_ip, vm4_uuid) 
        time.sleep(400)
        host4_status = res_ops.query_resource(res_ops.HOST, conditions2)[0].status
        if host4_status == "Disconnected":
            conditions6 = res_ops.gen_query_conditions('uuid', '=', vm.vm.uuid)
            vm_new_status = res_ops.query_resource(res_ops.VM_INSTANCE, conditions6)[0].state
            vm_host3_uuid = res_ops.query_resource(res_ops.VM_INSTANCE, conditions6)[0].hostUuid
            if vm_new_status != "Running" or vm_host3_uuid != host3_uuid:
                test_util.test_fail('Test ha vm auto across cluster start failed vm_new_status: %s, vm_host3_uuid :  %s' % (vm_new_status, vm_host3_uuid))

    conditions5 = res_ops.gen_query_conditions('vmNics.ip', '=', host4_ip)
    vm4_uuid = sce_ops.query_resource(zstack_management_ip, res_ops.VM_INSTANCE, conditions5).inventories[0].uuid
    sce_ops.start_vm(zstack_management_ip, vm4_uuid)
    #vm.destroy()
    conf_ops.change_global_config('ha', 'allow.slibing.cross.clusters', 'false')
    test_util.test_pass('VM auto ha across cluster new Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm, host3_uuid, vm3_uuid
    if vm:
        try:
            vm.destroy()
        except:
            pass
