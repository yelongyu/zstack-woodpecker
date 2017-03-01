'''
test for creating vm in newly add vcenter
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

    vm = test_stub.create_vm_in_vcenter(vm_name = 'vm-create-test', image_name = ova_image_name, l3_name = network_pattern1)
    vm.check()

    vm.destroy()
    vm.check()
    vm.expunge()

    vct_ops.delete_vcenter(vcenter_uuid)
    test_util.test_pass("Creating vm of vcenter test passed.")



def error_cleanup():
    global vcenter_uuid, vm
    if vm:
        vm.delete()
        vm.expunge()

    if vcenter_uuid:
        vct_ops.delete_vcenter(vcenter_uuid)
