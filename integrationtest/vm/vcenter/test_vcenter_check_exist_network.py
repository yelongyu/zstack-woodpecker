'''
test for add and delete vcenter
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



vcenter1_name = os.environ['vcenter1_name']
vcenter1_domain_name = os.environ['vcenter1_ip']
vcenter1_username = os.environ['vcenter1_domain_name']
vcenter1_password = os.environ['vcenter1_password']
vm_network_pattern1 = os.environ['vcenter1_network_pattern1']

vcenter_uuid = None


def test():
    global vcenter_uuid

    #add vcenter senario1:
    zone_uuid = res_ops.get_resource(res_ops.ZONE)[0].uuid
    inv = vct_ops.add_vcenter(vcenter1_name, vcenter1_domain_name, vcenter1_username, vcenter1_password, True, zone_uuid)
    vcenter_uuid = inv.uuid

    if vcenter_uuid == None:
        test_util.test_fail("vcenter_uuid is None")

    #insert the basic operations for the newly join in vcenter resourse
    vm_network_list = []
    vm_network_names = res_ops.query_resource_fields(res_ops.L3_NETWORK, [], None, fields=['name'])
    for vm_network in vm_network_names:
        vm_network_list.append(vm_network.name)

    test_util.test_logger( ", ".join( [ str(vm_network_tmp) for vm_network_tmp in vm_network_list ] ) )

    if vm_network_pattern1 not in vm_network_list:
        test_util.test_fail("newly joined vcenter missing vm network1, test failed")

    vct_ops.delete_vcenter(vcenter_uuid)
    test_util.test_pass("add && delete vcenter test passed.")



def error_cleanup():
    global vcenter_uuid
    if vcenter_uuid:
        vct_ops.delete_vcenter(vcenter_uuid)
