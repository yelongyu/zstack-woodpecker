'''
test for vm start and stop in newly add vcenter
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
vm_uuid = None

def test():
    global vcenter_uuid, vm_uuid

    vcenter1_name = os.environ['vcenter2_name']
    vcenter1_domain_name = os.environ['vcenter2_ip']
    vcenter1_username = os.environ['vcenter2_domain_name']
    vcenter1_password = os.environ['vcenter2_password']
    #ova_image_name = os.environ['vcenter2_template_exist']
    vm_name = os.environ['vcenter2_no_nic_vm']
    network_pattern1 = os.environ['vcenter2_network_pattern1']

    zone_uuid = res_ops.get_resource(res_ops.ZONE)[0].uuid
    inv = vct_ops.add_vcenter(vcenter1_name, vcenter1_domain_name, vcenter1_username, vcenter1_password, True, zone_uuid)
    vcenter_uuid = inv.uuid

    if vcenter_uuid == None:
        test_util.test_fail("vcenter_uuid is None")

    #vm = test_stub.create_vm_in_vcenter(vm_name = 'vm-start-stop-test', image_name = ova_image_name, l3_name = network_pattern1)
    vm_cond = res_ops.gen_query_conditions("name", '=', vm_name)
    vm_inv = res_ops.query_resource_fields(res_ops.VM_INSTANCE, vm_cond, None, fields=['uuid', 'state'])[0]
    vm_uuid = vm_inv.uuid
    vm_state = vm_inv.state.strip().lower()
    if not vm_uuid:
        test_util.test_fail("remote woodpecker vm uuid is null")
    elif vm_uuid and vm_state != "running":
        print "#%s#" % vm_state
        vm_ops.start_vm(vm_uuid)
        if not test_lib.lib_wait_target_up(vm_inv.vmNics[0].ip, '22', 90):
            test_util.test_fail('VM is expected to running')
        vm.stop()
        if not test_lib.lib_wait_target_down(vm_inv.vmNics[0].ip, '22', 90):
            test_util.test_fail('VM is expected to stopped')
    elif vm_uuid and vm_state == "running":
        print "#%s#" % vm_state
        vm.stop()
        if not test_lib.lib_wait_target_down(vm_inv.vmNics[0].ip, '22', 90):
            test_util.test_fail('VM is expected to stopped')
        vm_ops.start_vm(vm_uuid)
        if not test_lib.lib_wait_target_up(vm_inv.vmNics[0].ip, '22', 90):
            test_util.test_fail('VM is expected to running')

    vm_ops.destroy_vm(vm_uuid)
    vm_ops.expunge_vm(vm_uuid)

    vct_ops.delete_vcenter(vcenter_uuid)
    test_util.test_pass("vm start and stop of vcenter test passed.")



def error_cleanup():
    global vcenter_uuid, vm_uuid
    if vm_uuid:
        vm_ops.destroy_vm(vm_uuid)
        vm_ops.expunge_vm(vm_uuid)

    if vcenter_uuid:
        vct_ops.delete_vcenter(vcenter_uuid)
