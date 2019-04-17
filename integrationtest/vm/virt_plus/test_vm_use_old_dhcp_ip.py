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

def test():
    cond_l3 = res_ops.gen_query_conditions('name', '=', os.environ.get('l3PublicNetworkName'))
    l3_uuid = res_ops.query_resource(res_ops.L3_NETWORK, cond_l3)[0].uuid
    ip_range_uuid = res_ops.query_resource(res_ops.L3_NETWORK, cond_l3)[0].ipRanges[0].uuid
    vm = test_stub.create_vm()
    test_obj_dict.add_vm(vm)

    #Get dhcp ip
    dhcp_ip = net_ops.get_l3network_dhcp_ip(l3NetworkUuid=l3_uuid)
    sys_tag = ["staticIp::%s::%s" % (l3_uuid, dhcp_ip)]
    vm.destroy()
    vm.expunge()

    net_ops.delete_ip_range(ip_range_uuid)

    ip_range_option = test_util.IpRangeOption()
    ip_range_option.set_l3_uuid(l3_uuid=l3_uuid)
    ip_range_option.set_startIp(startIp="172.20.127.96")
    ip_range_option.set_endIp(endIp="172.20.127.127")
    ip_range_option.set_gateway(gateway="172.20.0.1")
    ip_range_option.set_netmask(netmask="255.255.0.0")
    ip_range_option.set_name(name="range-1")
    net_ops.add_ip_range(ip_range_option=ip_range_option)
    vm = test_stub.create_vm(vm_name='vm-dhcp-ip', system_tags=sys_tag)

    vm_ip = vm.vm.vmNics[0].ip
    cmd = "ping -c 4 %s" % (public_ip)
    (retcode, output, erroutput) = ssh.execute(cmd, vm_ip, "root", "password", True, 22)
    print "retcode is: %s; output is : %s.; erroutput is: %s" % (retcode, output, erroutput)
    if retcode != 0:
        test_util.test_fail('Cannot ping public IP, test Failed.')

    vm.destroy()
    vm.expunge()

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
