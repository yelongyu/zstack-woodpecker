'''
@author: yixin.wang
For bug ZSTAC-21094
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import random
import os
import subprocess
import time

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

vpc_name = 'vpc-test'
vpc_l3_list = test_stub.vpc1_l3_list
vr_list = []

@test_lib.pre_execution_action(test_stub.remove_all_vpc_vrouter)

def test():
    test_util.test_dsc("set global config ha is false")
    cmd = 'zstack-cli \ LogInByAccount accountName=admin password=password \ UpdateGlobalConfig category=ha name=enable value=false'
    subprocess.call(cmd, shell=True)
    test_util.test_dsc("create vpc vrouter and attach l3")
    vr = test_stub.create_vpc_vrouter(vpc_name)
    test_stub.attach_l3_to_vpc_vr(vr, vpc_l3_list)

    test_util.test_dsc("make vr host management_network down and vr host disconnect")
    host_man_ip = test_lib.lib_find_host_by_vr(vr.inv).managementIp
    mn_man_ip = subprocess.call("ifconfig br_eth0 |grep 172.24 |awk '{print $2}'", shell=True)
    if host_man_ip == mn_man_ip:
    	vr.migrate_to_random_host(vr)
    vr_host_man_ip = test_lib.lib_find_host_by_vr(vr.inv).managementIp
    cmd1 = 'ifconfig br_eth1 down'
    test_lib.lib_execute_ssh_cmd(vr_host_man_ip, 'root', 'password', cmd1)
    time.sleep(60)
    while True:
        time.sleep(3)
	if res_ops.get_resource(res_ops.APPLIANCE_VM, name=vpc_name)[0].state == "Unknown":
                break

    test_util.test_dsc("recover vr host management_network")
    cmd2 = 'ifconfig br_eth1 up'
    test_lib.lib_execute_ssh_cmd(vr_host_man_ip, 'root', 'password', cmd2)
    time.sleep(60)
    while True:
        time.sleep(3)
	if (res_ops.get_resource(res_ops.APPLIANCE_VM, name=vpc_name)[0].state == "Running") & (res_ops.get_resource(res_ops.APPLIANCE_VM, name=vpc_name)[0].status == "Connected"):
    		test_util.test_pass("when vr host management_network recover then vpc can reconnect")
                break

    test_stub.remove_all_vpc_vrouter()

def env_recover():
    test_stub.remove_all_vpc_vrouter()







