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
    ipv4_net_uuid = test_lib.lib_get_l3_by_name(os.environ.get('l3PublicNetworkName')).uuid
    ipv6_net_uuid = test_lib.lib_get_l3_by_name(os.environ.get('l3PublicNetworkName1')).uuid
    print "ipv4_net_uuid is : %s , ipv6_net_uuid is : %s" %(ipv4_net_uuid, ipv6_net_uuid)
    vm1 = test_stub.create_vm(l3_name = os.environ.get('l3PublicNetworkName'), vm_name = 'vm_1 IPv6 2 stack test', system_tags = ["dualStackNic::%s::%s" %(ipv4_net_uuid, ipv6_net_uuid)], image_name = image_name)
    vm2 = vm1.clone(["dualStackNic_clone_vm"])
    time.sleep(120) #waiting for vm bootup
    ipv4 = None
    ipv6 = None
    vms = res_ops.query_resource(res_ops.VM_INSTANCE)
    vm1_nic1 = vms[1].vmNics[0].usedIps[0].ip
    vm1_nic2 = vms[1].vmNics[0].usedIps[1].ip
    vm2_nic1 = vms[0].vmNics[0].usedIps[0].ip
    vm2_nic2 = vms[0].vmNics[0].usedIps[1].ip

    print "vm1_nic1 : %s, vm1_nic2: %s, vm2_nic1 :%s,vm2_nic2 :%s." %(vm1_nic1, vm1_nic2, vm2_nic1, vm2_nic2)
    for ip in [vm1_nic1, vm1_nic2]:
        if "172.20" in ip:
            ipv4 = ip
    for ip in [vm2_nic1, vm2_nic2]:
        if "1000:2000" in ip:
            ipv6 = ip
    for ip in [vm2_nic1, vm2_nic2]:
        if "172" in ip:
            vm2_ipv4 = ip
    print "vm1_nic1 : %s, vm1_nic2: %s, vm2_nic1 :%s,vm2_nic2 :%s, ipv4 :%s, ipv6 :%s." %(vm1_nic1, vm1_nic2, vm2_nic1, vm2_nic2, ipv4, ipv6)
    cmd = "ping6 -c 4 %s" %(ipv6)
    (retcode, output, erroutput) = ssh.execute(cmd, ipv4, "root", "password", True, 22)
    cmd1 = "ping -c 4 %s" %(vm2_ipv4)
    (retcode1, output1, erroutput1) = ssh.execute(cmd1, ipv4, "root", "password", True, 22)
    print "retcode is: %s; output is : %s.; erroutput is: %s" %(retcode, output , erroutput)
    print "retcode1 is: %s; output1 is : %s.; erroutput1 is: %s" %(retcode1, output1 , erroutput1)
    if retcode != 0 and retcode1 != 0:
        test_util.test_fail('Test Create IPv6 VM Failed.')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
