'''
test for vm migrate with assigned host uuid in newly add vcenter
@author: SyZhao
'''

import apibinding.inventory as inventory
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.vcenter_operations as vct_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstacklib.utils.ssh as ssh
import test_stub
import os

vcenter_uuid = None
another_host_uuid = None
vm = None

def test():
    global vcenter_uuid, vm

    vcenter1_name = os.environ['vcenter2_name']
    vcenter1_domain_name = os.environ['vcenter2_ip']
    vcenter1_username = os.environ['vcenter2_domain_name']
    vcenter1_password = os.environ['vcenter2_password']
    ova_image_name = os.environ['vcenter2_template_exist']
    network_pattern1 = os.environ['vcenter2_network_pattern1']

    zone_uuid = res_ops.get_resource(res_ops.ZONE)[0].uuid
    inv = vct_ops.add_vcenter(vcenter1_name, vcenter1_domain_name, vcenter1_username, vcenter1_password, True, zone_uuid)
    vcenter_uuid = inv.uuid

    if vcenter_uuid == None:
        test_util.test_fail("vcenter_uuid is None")

    #this test suppose user has already deployed a cluster with more than 2 hosts included, 
    #the vm is created in one of the host, then start the vm with another host uuid, 
    #which leads vm migration triggering. 
    vm = test_stub.create_vm_in_vcenter(vm_name = 'vm-start-stop-test', image_name = ova_image_name, l3_name = network_pattern1)
    vm.check()

    vm.stop()
    vm.check()

    vm_host_uuid = test_lib.lib_get_vm_host(vm.get_vm()).uuid

    host_cond = res_ops.gen_query_conditions("status", '=', "Connected")
    host_uuids = res_ops.query_resource_fields(res_ops.HOST, host_cond, None, fields=['uuid'])
    for host_uuid in host_uuids:
        if host_uuid != vm_host_uuid:
            another_host_uuid = host_uuid
            break

    test_stub.start_vm_with_host_uuid(vm.get_vm(), vm_host_uuid)
    vm.check()

    vm.destroy()
    vm.check()
    vm.expunge()

    vct_ops.delete_vcenter(vcenter_uuid)
    test_util.test_pass("vm start and stop of vcenter test passed.")



def error_cleanup():
    global vcenter_uuid, vm
    if vm:
        vm.destroy()
        vm.expunge()

    if vcenter_uuid:
        vct_ops.delete_vcenter(vcenter_uuid)
