'''
test for vcenter sync of vm start and stop
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


vcenter_uuid1 = None
vcenter_uuid2 = None

mevoco1_ip = None
mevoco2_ip = None

vm_uuid = None

def test():
    global vcenter_uuid1
    global vcenter_uuid2
    global mevoco1_ip
    global mevoco2_ip
    global vm_uuid


    vcenter1_name = os.environ['vcenter2_name']
    vcenter1_domain_name = os.environ['vcenter2_ip']
    vcenter1_username = os.environ['vcenter2_domain_name']
    vcenter1_password = os.environ['vcenter2_password']
    sync_vm = os.environ['vcenter2_sync_vm_create_delete']
    sync_image_name = os.environ['vcenter2_template_exist']
    network_pattern1 = os.environ['vcenter2_network_pattern1']



    mevoco1_ip = os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP']
    mevoco2_ip = os.environ['serverIp2']    


    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco1_ip
    zone_uuid = res_ops.get_resource(res_ops.ZONE)[0].uuid
    inv = vct_ops.add_vcenter(vcenter1_name, vcenter1_domain_name, vcenter1_username, vcenter1_password, True, zone_uuid)
    vcenter_uuid1 = inv.uuid
    if vcenter_uuid1 == None:
        test_util.test_fail("vcenter_uuid is None")


    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco2_ip
    zone_uuid = res_ops.get_resource(res_ops.ZONE)[0].uuid
    inv = vct_ops.add_vcenter(vcenter1_name, vcenter1_domain_name, vcenter1_username, vcenter1_password, True, zone_uuid)
    vcenter_uuid2 = inv.uuid
    if vcenter_uuid2 == None:
        test_util.test_fail("vcenter_uuid is None")



    #create vm in remote and check
    test_util.test_logger("create vm for sync test")
    vm = test_stub.create_vm_in_vcenter(vm_name = sync_vm, image_name = sync_image_name, l3_name = network_pattern1)
    vm.check()

    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco1_ip
    vm_cond = res_ops.gen_query_conditions("name", '=', sync_vm)
    vm_inv = res_ops.query_resource_fields(res_ops.VM_INSTANCE, vm_cond, None, fields=['uuid', 'state'])
    if not vm_inv:
        test_util.test_fail("not found target vm being sync")

    vm_uuid = vm_inv[0].uuid
    if not vm_uuid:
        test_util.test_fail("remote woodpecker vm uuid is null")

    vm_state = vm_inv[0].state.strip().lower()
    if vm_state != "running":
        test_util.test_fail("vcenter sync vm start failed.")



    #delete vm in remote and check
    test_util.test_logger("delete vm for sync test")
    if vm_uuid:
        vm_ops.destroy_vm(vm_uuid)
        vm_ops.expunge_vm(vm_uuid)

    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco2_ip
    vm_inv = res_ops.query_resource_fields(res_ops.VM_INSTANCE, vm_cond, None, fields=['uuid', 'state'])
    if vm_inv:
        test_util.test_fail("found the expected deleted vm")




    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco2_ip
    if vcenter_uuid2:
        vct_ops.delete_vcenter(vcenter_uuid2)

    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco1_ip
    if vcenter_uuid1:
        vct_ops.delete_vcenter(vcenter_uuid1)

    test_util.test_pass("vcenter sync start and stop vm test passed.")



def error_cleanup():
    global vcenter_uuid1
    global vcenter_uuid2
    global mevoco2_ip
    global vm_uuid

    if vm_uuid:
        vm_ops.destroy_vm(vm_uuid)
        vm_ops.expunge_vm(vm_uuid)

    if vcenter_uuid1:
        vct_ops.delete_vcenter(vcenter_uuid1)

    if vcenter_uuid2:
        os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mevoco2_ip
        vct_ops.delete_vcenter(vcenter_uuid2)
