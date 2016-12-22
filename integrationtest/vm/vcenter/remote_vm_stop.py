'''
stop vm via remote mevoco api
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
vm_name = "vm-crt-via-rmt-mevoco"

#this script is design for stopping the vm named "vm-crt-via-rmt-mevoco"
def test():
    global vcenter_uuid, vm

    zone_uuid = res_ops.get_resource(res_ops.ZONE)[0].uuid
    inv = vct_ops.add_vcenter(vcenter1_name, vcenter1_domain_name, vcenter1_username, vcenter1_password, True, zone_uuid)
    vcenter_uuid = inv.uuid

    if vcenter_uuid == None:
        test_util.test_fail("vcenter_uuid is None")

    vm_cond = res_ops.gen_query_conditions("name", '=', vm_name)
    vm_uuid = res_ops.query_resource_fields(res_ops.VM_INSTANCE, vm_cond, None, fields=['uuid'])[0].uuid

    if vm_uuid:
        vm_ops.stop_vm(vm_uuid)


    vct_ops.delete_vcenter(vcenter_uuid)
    test_util.test_pass("stop vm-crt-via-rmt-mevoco passed.")



def error_cleanup():
    global vcenter_uuid

    if vcenter_uuid:
        vct_ops.delete_vcenter(vcenter_uuid)
