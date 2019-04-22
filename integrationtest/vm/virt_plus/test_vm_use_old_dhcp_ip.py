'''

New Integration Test for creating KVM VM using old DHCP IP.

@author: Hengguo.Ge
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.net_operations as net_ops
import zstacklib.utils.ssh as ssh
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import time
import os
import commands

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

public_ip="223.5.5.5"
ext_host_ip="172.20.1.106"
ext_host_pwd="zstack.org"

def test():
    global test_obj_dict
    cond_l3 = res_ops.gen_query_conditions('name', '=', os.environ.get('l3PublicNetworkName'))
    l3_uuid = res_ops.query_resource(res_ops.L3_NETWORK, cond_l3)[0].uuid
    ip_range_uuid = res_ops.query_resource(res_ops.L3_NETWORK, cond_l3)[0].ipRanges[0].uuid
    vm = test_stub.create_vm()

    #Get dhcp ip
    dhcp_ip = net_ops.get_l3network_dhcp_ip(l3NetworkUuid=l3_uuid)
    sys_tag = ["staticIp::%s::%s" % (l3_uuid, dhcp_ip)]
    vm.destroy()
    vm.expunge()
    time.sleep(10)
    ip_range=test_lib.lib_get_ip_range_by_l3_uuid(l3NetworkUuid=l3_uuid)
    net_ops.delete_ip_range(ip_range_uuid)
    time.sleep(2)
    ip_range_option = test_util.IpRangeOption()
    ip_range_option.set_l3_uuid(l3_uuid=l3_uuid)
    ip_range_option.set_startIp(startIp=ip_range.startIp)
    ip_range_option.set_endIp(endIp=ip_range.endIp)
    ip_range_option.set_gateway(gateway=ip_range.gateway)
    ip_range_option.set_netmask(netmask=ip_range.netmask)
    ip_range_option.set_name(name=ip_range.name)
    net_ops.add_ip_range(ip_range_option=ip_range_option)
    time.sleep(2)
    vm = test_stub.create_vm(vm_name='vm-dhcp-ip', system_tags=sys_tag)
    test_obj_dict.add_vm(vm)
    time.sleep(60)
    vm_ip = vm.vm.vmNics[0].ip

    cmd = "ping -c 5 %s" % (vm_ip)
    (retcode, output, erroutput) = ssh.execute(cmd, ext_host_ip, "root", ext_host_pwd, True, 22)
    print "retcode is: %s; output is : %s.; erroutput is: %s" % (retcode, output, erroutput)
    vm.destroy()
    vm.expunge()
    if retcode != 0:
        test_util.test_fail('Cannot ping public IP, test Failed.')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
