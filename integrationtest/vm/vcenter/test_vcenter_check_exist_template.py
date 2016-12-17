'''
test for checking if template existed in newly add vcenter
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
vcenter1_domain_name = "172.20.76.250"
vcenter1_username = "administrator@vsphere.local"
vcenter1_password = "Testing%123"

vcenter_uuid = None

ova_template_pattern1 = "MicroCore-Linux.ova"

def test():
    global vcenter_uuid

    #add vcenter senario1:
    zone_uuid = res_ops.get_resource(res_ops.ZONE)[0].uuid
    inv = vct_ops.add_vcenter(vcenter1_name, vcenter1_domain_name, vcenter1_username, vcenter1_password, True, zone_uuid)
    vcenter_uuid = inv.uuid

    if vcenter_uuid == None:
        test_util.test_fail("vcenter_uuid is None")

    #insert the basic operations for the newly join in vcenter resourse
    image_list = []
    image_names = res_ops.query_resource_fields(res_ops.IMAGE, [], None, fields=['name'])
    for image_name in image_names:
        image_list.append(image_name.name)

    test_util.test_logger( ", ".join( [ str(image_name_tmp) for image_name_tmp in image_list ] ) )

    if ova_template_pattern1 not in image_list:
        test_util.test_fail("newly joined vcenter missing fingerprint vm1, test failed")

    vct_ops.delete_vcenter(vcenter_uuid)
    test_util.test_pass("add && delete vcenter test passed.")



def error_cleanup():
    global vcenter_uuid
    if vcenter_uuid:
        vct_ops.delete_vcenter(vcenter_uuid)
