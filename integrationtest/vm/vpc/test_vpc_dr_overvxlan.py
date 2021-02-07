'''

@author: Pengtao.Zhang
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.operations.vpc_operations as vpc_ops
import zstackwoodpecker.operations.host_operations as host_ops
import random
import os
import zstackwoodpecker.operations.volume_operations as vol_ops
import time
import apibinding.api_actions as api_actions
import subprocess
import zstacklib.utils.ssh as ssh

VLAN1_NAME, VLAN2_NAME = ['l3VlanNetworkName1', "l3VlanNetwork2"]
VXLAN1_NAME, VXLAN2_NAME = ["l3VxlanNetwork11", "l3VxlanNetwork12"]

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    hosts_uuid = []
    for i in res_ops.get_resource(res_ops.HOST):
        hosts_uuid.append(i.uuid)
    test_util.test_dsc("create vpc vrouter and attach vpc l3 to vpc")
    vr = test_stub.create_vpc_vrouter()
    test_stub.attach_l3_to_vpc_vr(vr)
    conf = res_ops.gen_query_conditions('name', '=', 'test_vpc')
    vr_host_uuid = res_ops.query_resource(res_ops.APPLIANCE_VM, conf)[0].hostUuid
    vr_uuid = res_ops.query_resource(res_ops.APPLIANCE_VM, conf)[0].uuid
    vr_bridge = 'vr' + ''.join(list(vr_uuid)[0:6])
    hosts_uuid.remove(vr_host_uuid)
    test_util.test_dsc("enable dr vxlan")
    vpc_ops.set_vpc_dr_vxlan(vr_uuid, 'enable')
    vm1 = test_stub.create_vm('test_vm1', 'image_for_sg_test', 'l3VxlanNetwork11', host_uuid = hosts_uuid[0])
    vm2 = test_stub.create_vm('test_vm2', 'image_for_sg_test', 'l3VxlanNetwork12', host_uuid = hosts_uuid[1])

    vm1_host_ip = test_lib.lib_get_vm_host(vm1.get_vm()).managementIp
    vm2_host_ip = test_lib.lib_get_vm_host(vm2.get_vm()).managementIp
    [test_obj_dict.add_vm(vm) for vm in (vm1,vm2)]
    [vm.check() for vm in (vm1,vm2)]

    vip = test_stub.create_vip()
    test_obj_dict.add_vip(vip)
    eip = test_stub.create_eip(eip_name = 'test eip', vip_uuid = vip.get_vip().uuid, vnic_uuid = vm1.get_vm().vmNics[0].uuid, vm_obj = vm1.get_vm().uuid)
    eip_ip = eip.get_eip().vipIp
    vm1_ip = vm1.get_vm().vmNics[0].ip
    vm2_ip = vm2.get_vm().vmNics[0].ip
    time.sleep(30)

    cmd1 = 'sshpass -p password ssh root@%s \"ping -c 100 %s \"' % (eip_ip, vm2_ip)
    child1 = subprocess.Popen(cmd1,shell=True)
    time.sleep(5)
    subprocess.call('sshpass -p password scp /etc/yum.repos.d/zstack-local.repo root@%s:/etc/yum.repos.d' % vm1_host_ip, shell=True)
    subprocess.call('sshpass -p password scp /etc/yum.repos.d/zstack-local.repo root@%s:/etc/yum.repos.d' % vm2_host_ip, shell=True)
    subprocess.call('sshpass -p password ssh root@%s yum --disablerepo=* --enablerepo=zstack-local install tcpdump -y' % vm1_host_ip, shell=True)
    subprocess.call('sshpass -p password ssh root@%s yum --disablerepo=* --enablerepo=zstack-local install tcpdump -y' % vm2_host_ip, shell=True)
    cmd2 = 'sshpass -p password ssh root@%s \"tcpdump -c 5 -i %s > /tmp/host1_tcpdump.log\"' % (vm1_host_ip, vr_bridge)
    child2 = subprocess.Popen(cmd2,shell=True)
    cmd3 = 'sshpass -p password ssh root@%s \"tcpdump -c 5 -i %s > /tmp/host2_tcpdump.log\"' % (vm2_host_ip, vr_bridge)
    child3 = subprocess.Popen(cmd3,shell=True)
    time.sleep(10)
    cmd4 = 'sshpass -p password scp root@%s:/tmp/host1_tcpdump.log /root' % (vm1_host_ip)
    child4 = subprocess.call(cmd4,shell=True)
    cmd5 = 'sshpass -p password scp root@%s:/tmp/host2_tcpdump.log /root' % (vm2_host_ip)
    child5 = subprocess.call(cmd5,shell=True)

    with open('/root/host1_tcpdump.log' ,'r') as fd:
	line = fd.readlines()
    if vm1_ip in line[0] and vm2_ip in line[0]:
        with open('/root/host2_tcpdump.log' ,'r') as fdd:
	    linee = fdd.readlines()
        if vm1_ip in linee[0] and vm2_ip in linee[0]:
            test_util.test_dsc("check tcpdump from vr bridge pass")
            os.system('rm -f /root/host1_tcpdump.log /root/host2_tcpdump.log')
        else:
            test_util.test_fail('check tcpdump from vr bridge failed')
    else:
	test_util.test_fail('check tcpdump from vr bridge failed')

    subprocess.call('sshpass -p password ssh root@%s \"pkill ping\"' % (eip_ip),shell=True)

    test_util.test_dsc("reconnect vpc and check again")
    vr.reconnect()
    cmd1 = 'sshpass -p password ssh root@%s \"ping -c 100 %s \"' % (eip_ip, vm2_ip)
    child1 = subprocess.Popen(cmd1,shell=True)
    time.sleep(5)
    subprocess.call('sshpass -p password scp /etc/yum.repos.d/zstack-local.repo root@%s:/etc/yum.repos.d' % vm1_host_ip, shell=True)
    subprocess.call('sshpass -p password scp /etc/yum.repos.d/zstack-local.repo root@%s:/etc/yum.repos.d' % vm2_host_ip, shell=True)
    subprocess.call('sshpass -p password ssh root@%s yum --disablerepo=* --enablerepo=zstack-local install tcpdump -y' % vm1_host_ip, shell=True)
    subprocess.call('sshpass -p password ssh root@%s yum --disablerepo=* --enablerepo=zstack-local install tcpdump -y' % vm2_host_ip, shell=True)
    cmd2 = 'sshpass -p password ssh root@%s \"tcpdump -c 5 -i %s > /tmp/host1_tcpdump.log\"' % (vm1_host_ip, vr_bridge)
    child2 = subprocess.Popen(cmd2,shell=True)
    cmd3 = 'sshpass -p password ssh root@%s \"tcpdump -c 5 -i %s > /tmp/host2_tcpdump.log\"' % (vm2_host_ip, vr_bridge)
    child3 = subprocess.Popen(cmd3,shell=True)
    time.sleep(10)
    cmd4 = 'sshpass -p password scp root@%s:/tmp/host1_tcpdump.log /root' % (vm1_host_ip)
    child4 = subprocess.call(cmd4,shell=True)
    cmd5 = 'sshpass -p password scp root@%s:/tmp/host2_tcpdump.log /root' % (vm2_host_ip)
    child5 = subprocess.call(cmd5,shell=True)

    with open('/root/host1_tcpdump.log' ,'r') as fd:
	line = fd.readlines()
    if vm1_ip in line[0] and vm2_ip in line[0]:
        with open('/root/host2_tcpdump.log' ,'r') as fdd:
	    linee = fdd.readlines()
        if vm1_ip in linee[0] and vm2_ip in linee[0]:
            test_util.test_dsc("check tcpdump from vr bridge pass after reconnect vr")
            os.system('rm -f /root/host1_tcpdump.log /root/host2_tcpdump.log')
        else:
            test_util.test_fail('check tcpdump from vr bridge failed after reconnect vr')
    else:
	test_util.test_fail('check tcpdump from vr bridge failed after reconnect vr')

    subprocess.call('sshpass -p password ssh root@%s \"pkill ping\"' % (eip_ip),shell=True)

    test_util.test_dsc("reboot vpc and check again")

    vr.reboot()
    cmd1 = 'sshpass -p password ssh root@%s \"ping -c 100 %s \"' % (eip_ip, vm2_ip)
    child1 = subprocess.Popen(cmd1,shell=True)
    time.sleep(5)
    subprocess.call('sshpass -p password scp /etc/yum.repos.d/zstack-local.repo root@%s:/etc/yum.repos.d' % vm1_host_ip, shell=True)
    subprocess.call('sshpass -p password scp /etc/yum.repos.d/zstack-local.repo root@%s:/etc/yum.repos.d' % vm2_host_ip, shell=True)
    subprocess.call('sshpass -p password ssh root@%s yum --disablerepo=* --enablerepo=zstack-local install tcpdump -y' % vm1_host_ip, shell=True)
    subprocess.call('sshpass -p password ssh root@%s yum --disablerepo=* --enablerepo=zstack-local install tcpdump -y' % vm2_host_ip, shell=True)
    cmd2 = 'sshpass -p password ssh root@%s \"tcpdump -c 5 -i %s > /tmp/host1_tcpdump.log\"' % (vm1_host_ip, vr_bridge)
    child2 = subprocess.Popen(cmd2,shell=True)
    cmd3 = 'sshpass -p password ssh root@%s \"tcpdump -c 5 -i %s > /tmp/host2_tcpdump.log\"' % (vm2_host_ip, vr_bridge)
    child3 = subprocess.Popen(cmd3,shell=True)
    time.sleep(10)
    cmd4 = 'sshpass -p password scp root@%s:/tmp/host1_tcpdump.log /root' % (vm1_host_ip)
    child4 = subprocess.call(cmd4,shell=True)
    cmd5 = 'sshpass -p password scp root@%s:/tmp/host2_tcpdump.log /root' % (vm2_host_ip)
    child5 = subprocess.call(cmd5,shell=True)

    with open('/root/host1_tcpdump.log' ,'r') as fd:
	line = fd.readlines()
    if vm1_ip in line[0] and vm2_ip in line[0]:
        with open('/root/host2_tcpdump.log' ,'r') as fdd:
	    linee = fdd.readlines()
        if vm1_ip in linee[0] and vm2_ip in linee[0]:
            test_util.test_dsc("check tcpdump from vr bridge pass")
            os.system('rm -f /root/host1_tcpdump.log /root/host2_tcpdump.log')
            test_util.test_dsc("disable dr vxlan")
            vpc_ops.set_vpc_dr_vxlan(vr_uuid, 'disable')
        else:
            test_util.test_fail('check tcpdump from vr bridge failed after reboot vr')
    else:
	test_util.test_fail('check tcpdump from vr bridge failed after reboot vr')

    subprocess.call('sshpass -p password ssh root@%s \"pkill ping\"' % (eip_ip),shell=True)

    test_util.test_pass('check tcpdump from vr bridge pass')
    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_vrouter()

def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)
    test_stub.remove_all_vpc_vrouter()
