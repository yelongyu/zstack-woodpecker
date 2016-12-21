'''
test for vm suspend in newly add vcenter
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


vcenter1_name = "VCENTER1"
vcenter1_domain_name = "172.20.76.251"
vcenter1_username = "administrator@vsphere.local"
vcenter1_password = "Testing%123"

vcenter_uuid = None

vm = None


def test():
    global vcenter_uuid, vm

    zone_uuid = res_ops.get_resource(res_ops.ZONE)[0].uuid
    inv = vct_ops.add_vcenter(vcenter1_name, vcenter1_domain_name, vcenter1_username, vcenter1_password, True, zone_uuid)
    vcenter_uuid = inv.uuid

    if vcenter_uuid == None:
        test_util.test_fail("vcenter_uuid is None")

    vm = test_stub.create_vm_in_vcenter(vm_name = 'vm-suspend-test', image_name = "MicroCore-Linux.ova", l3_name = "L3-251-net1")
    vm.check()

    vm.suspend()
    vm.check()

    vm.resume()
    vm.check()

    vct_ops.delete_vcenter(vcenter_uuid)
    test_util.test_pass("vm suspend of vcenter test passed.")



def error_cleanup():
    global vcenter_uuid, vm
    if vm:
        vm.destroy()
        vm.expunge()

    if vcenter_uuid:
        vct_ops.delete_vcenter(vcenter_uuid)
