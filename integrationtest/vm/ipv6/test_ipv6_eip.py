'''

@author: Pengtao.Zhang
'''

import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_util as test_util
from zstackwoodpecker.operations import net_operations as net_ops
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.zstack_test.zstack_test_image as test_image
import zstackwoodpecker.operations.resource_operations as res_ops
import zstacklib.utils.ssh as ssh
import time
import os


test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()


def test():

    image_name = os.environ.get('ipv6ImageName')
    vm1 = test_stub.create_vm(l3_name = "%s,%s" %(os.environ.get('l3PublicNetworkName1'), os.environ.get('l3PublicNetworkName')), vm_name = 'IPv6 2 stack test ipv4 and ipv6', image_name = image_name)
    vm2 = test_stub.create_vm(l3_name = os.environ.get('l3PrivateNetworkName'), vm_name = 'IPv6 private vm', image_name = image_name)
    time.sleep(90) #waiting for vm bootup
    vm1_nic1 = vm1.get_vm().vmNics[0].ip
    vm1_nic2 = vm1.get_vm().vmNics[1].ip
    vm2_nic1 = vm2.get_vm().vmNics[0].ip
    for ip in (vm1_nic1, vm1_nic2):
        if "." in ip:
            ipv4 = ip
    print "vm1_nic1 : %s, vm1_nic2: %s, vm2_nic1 :%s, ipv4 :%s." %(vm1_nic1, vm1_nic2, vm2_nic1,ipv4)
#######################################################################
    pub_l3_name = os.environ.get('l3PublicNetworkName1')
    pub_l3_uuid = test_lib.lib_get_l3_by_name(pub_l3_name).uuid

    vm2_nic_uuid = vm2.get_vm().vmNics[0].uuid
    vip = test_stub.create_vip('create_eip_test', pub_l3_uuid)
    test_obj_dict.add_vip(vip)
    eip = test_stub.create_eip('create eip test', vip_uuid=vip.get_vip().uuid, vnic_uuid=vm2_nic_uuid, vm_obj=vm2)

    vip.attach_eip(eip)
    eip_ip = res_ops.query_resource(res_ops.EIP)[0].vipIp

    print "eip_ip : %s, vm1_nic2: %s, vm2_nic1 :%s, ipv4 :%s." %(eip_ip, vm1_nic2, vm2_nic1,ipv4)
    cmd = "ping6 -c 4 %s" %(eip_ip)
    (retcode, output, erroutput) = ssh.execute(cmd, ipv4, "root", "password", True, 22)
    print "ping6 EIP retcode is: %s; output is : %s.; erroutput is: %s" %(retcode, output , erroutput)
    if retcode != 0:
        test_util.test_fail('Test Create IPv6 VM Failed.')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
