'''
Test baremetal instance operation

@author chenyuan.xu
'''
import zstackwoodpecker.operations.baremetal_operations as baremetal_operations
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.zstack_test.zstack_test_image as test_image
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.cluster_operations as cluster_ops
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as zstack_vm_header
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
from vncdotool import api
import test_stub
import time
import os

vm = None
baremetal_cluster_uuid = None
pxe_uuid = None
host_ip = None
test_obj_dict = test_state.TestStateDict()
def test():
    global test_obj_dict
    global vm, baremetal_cluster_uuid, pxe_uuid, host_ip
    test_util.test_dsc('Create baremetal cluster and attach network')
    zone_uuid = res_ops.query_resource(res_ops.ZONE)[0].uuid
    cond = res_ops.gen_query_conditions('type', '=', 'baremetal')
    origin_bm_clusters = res_ops.query_resource(res_ops.CLUSTER, cond)
    if origin_bm_clusters != []:
        for i in range(len(origin_bm_clusters)):
            cluster_ops.delete_cluster(origin_bm_clusters[i].uuid)
    baremetal_cluster_uuid = test_stub.create_cluster(zone_uuid).uuid
    cond = res_ops.gen_query_conditions('name', '=', os.environ.get('scenl3VPCNetworkName1'))
    l3_network = res_ops.query_resource(res_ops.L3_NETWORK, cond)[0]
    l3_uuid_list = []
    l3_uuid_list.append(l3_network.uuid)
    l3s = res_ops.query_resource(res_ops.L3_NETWORK)
    for l3 in l3s:
        l3_net_uuid = l3.uuid
        if l3.uuid != l3_network.uuid:
            l3_uuid_list.append(l3_net_uuid)
        cond = res_ops.gen_query_conditions('l3Network.uuid', '=', l3_net_uuid)
        l2_uuid = res_ops.query_resource(res_ops.L2_NETWORK, cond)[0].uuid
        cidr = l3.ipRanges[0].networkCidr
        sys_tags = "l2NetworkUuid::%s::clusterUuid::%s::cidr::{%s}" %(l2_uuid, baremetal_cluster_uuid, cidr)
        net_ops.attach_l2(l2_uuid, baremetal_cluster_uuid, [sys_tags])

    test_util.test_dsc('Create pxe server')
    pxe_servers = res_ops.query_resource(res_ops.PXE_SERVER)
    [pxe_ip, interface] = test_stub.get_pxe_info()
    if not pxe_servers:
        pxe_uuid = test_stub.create_pxe(dhcp_interface = interface, hostname = pxe_ip, zoneUuid = zone_uuid).uuid
        baremetal_operations.attach_pxe_to_cluster(pxe_uuid, baremetal_cluster_uuid)
    else:
        pxe_uuid = pxe_servers[0].uuid

    test_util.test_dsc('Create a vm to simulate baremetal host')
    #mn_ip = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].hostName
    #cond = res_ops.gen_query_conditions('managementIp', '=', mn_ip)
    host = res_ops.query_resource(res_ops.HOST)[0]
    host_uuid = host.uuid
    host_ip = host.managementIp
    cond = res_ops.gen_query_conditions('hypervisorType', '=', 'KVM')
    cluster_uuid = res_ops.query_resource(res_ops.CLUSTER, cond)[0].uuid
    vm = test_stub.create_vm_multi_l3(host_uuid = host_uuid, cluster_uuid = cluster_uuid, l3_uuid_list=l3_uuid_list, default_l3_uuid = l3_network.uuid)

    test_util.test_dsc('Create chassis')
    test_stub.create_vbmc(vm, host_ip, 623)
    chassis = test_stub.create_chassis(baremetal_cluster_uuid, address = host_ip)
    chassis_uuid = chassis.uuid
   #Hack inspect ks file to support vbmc, include ipmi device logic and ipmi addr to 127.0.0.1
    test_stub.hack_inspect_ks(pxe_ip, host_ip)

    test_util.test_dsc('Inspect chassis, Because vbmc have bugs, \
        reset vm unable to enable boot options, power off/on then reset is worked')
    baremetal_operations.inspect_chassis(chassis_uuid)
    baremetal_operations.power_off_baremetal(chassis_uuid)
    time.sleep(10)
    baremetal_operations.power_on_baremetal(chassis_uuid)
    time.sleep(30)
    baremetal_operations.inspect_chassis(chassis_uuid)
    time.sleep(2)
    console = test_lib.lib_get_vm_console_address(vm.get_vm().uuid)
    display = str(int(console.port)-5900)
    client = api.connect(console.hostIp+":"+display)
    client.keyPress('esc')
    client.keyPress('4')
    hwinfo = test_stub.check_hwinfo(chassis_uuid)
    if not hwinfo:
        test_util.test_fail('Fail to get hardware info during the first inspection')

    test_util.test_dsc('Add c72 image')
    img_option = test_util.ImageOption()
    image_name = 'centos-7.2'
    img_option.set_name(image_name)
    bs_uuid = res_ops.query_resource_fields(res_ops.BACKUP_STORAGE, [], None)[0].uuid
    img_option.set_backup_storage_uuid_list([bs_uuid])
    img_option.set_format('iso')
    img_option.set_url(os.environ.get('imageServer')+"/iso/CentOS-7-x86_64-DVD-1708.iso")
    image_inv = img_ops.add_root_volume_template(img_option)
    image = test_image.ZstackTestImage()
    image.set_image(image_inv)
    image.set_creation_option(img_option)
    test_obj_dict.add_image(image)

    test_util.test_dsc('Create provision template')
    content = '''
################################
# USE NETWORK INSTALLATION
################################
url --url={{ REPO_URL }}

################################
# BASIC CONFIGURATIONS
################################
# System language
lang en_US.UTF-8

# Keyboard layout
keyboard --vckeymap=us --xlayouts='us'

# System timezone
timezone Asia/Shanghai --isUtc

# SELinux configuration
selinux --disabled

# System services
services --enabled="chronyd"
firstboot --disable

# Use graphical install
graphical

# Reboot after installation
reboot

# System authorization information
auth --enableshadow --passalgo=sha512

################################
# ROOT PASSWORD
################################
{{ USERNAME }}
rootpw --iscrypted {{ PASSWORD }}

################################
# NETWORK CONFIGURATIONS
################################
network --hostname={{hostname}}
{{ NETWORK_CFGS }}

################################
# DISK PARTITIONS
################################
%include /tmp/ignoredisk.cfg
autopart --type=lvm
{{ FORCE_INSTALL }}

################################
# PRE SCRIPTS
################################
%pre
touch /tmp/ignoredisk.cfg
ls /dev/disk/by-path/*usb* && echo "ignoredisk --drives=/dev/disk/by-path/*usb*" >/tmp/ignoredisk.cfg
ls /dev/vda && echo "ignoredisk --only-use=vda" > /tmp/ignoredisk.cfg
ls /dev/hda && echo "ignoredisk --only-use=hda" > /tmp/ignoredisk.cfg
ls /dev/sda && echo "ignoredisk --only-use=sda" > /tmp/ignoredisk.cfg

### NECESSARY: PRE SCRIPTS FOR ZSTACK
{{ PRE_SCRIPTS }}
%end

################################
# POST SCRIPTS
################################
%post
systemctl enable sshd

### NECESSARY: POST SCRIPTS FOR ZSTACK
{{ POST_SCRIPTS }}
%end

################################
# PACKAGES
################################
%packages
@core
chrony
kexec-tools
%end

%addon com_redhat_kdump --enable --reserve-mb='auto'
%end

'''

    template = baremetal_operations.add_preconfiguration_template('centos7.2', 'kickstart', 'centos-x86_64', content)


    test_util.test_dsc('Create baremetal instance')
    cond = res_ops.gen_query_conditions('name', '=', 'centos-7.2')
    image_uuid = res_ops.query_resource(res_ops.IMAGE, cond)[0].uuid
    #test_stub.ca_pem_workaround(host_ip)
    vm_inv = vm.get_vm()
    bond0 = baremetal_operations.create_baremetal_bonding(chassis_uuid, 'bond0', '4', slaves='%s,%s'  %(vm_inv.vmNics[1].mac, vm_inv.vmNics[2].mac))

    cond = res_ops.gen_query_conditions('name', '=', os.environ.get('l3PublicNetworkName'))
    l3_vlan_network1 = res_ops.query_resource(res_ops.L3_NETWORK, cond)[0]
    ip_address1 = net_ops.get_free_ip(l3_vlan_network1.uuid)[0].ip
    cond = res_ops.gen_query_conditions('name', '=', os.environ.get('scenl3VPCNetworkName3'))
    l3_vlan_network2 = res_ops.query_resource(res_ops.L3_NETWORK, cond)[0]
    ip_address2 = net_ops.get_free_ip(l3_vlan_network2.uuid)[0].ip
    tag = ["staticIp::%s::%s" % (l3_vlan_network1.uuid, ip_address1),"staticIp::%s::%s" % (l3_vlan_network2.uuid, ip_address2),"forceInstall"]

    cond = res_ops.gen_query_conditions("vmInstanceUuid","=", vm_inv.uuid)
    cond = res_ops.gen_query_conditions("l3NetworkUuid","=", l3_vlan_network1.uuid, cond)
    vm_nic_mac = res_ops.query_resource_fields(res_ops.VM_NIC, cond, None, ['mac'])[0].mac        
    nic_cfgs = {vm_nic_mac:l3_vlan_network1.uuid}
    bonding_cfgs = {bond0.uuid:l3_vlan_network2.uuid}
    customConfigurations={"hostname":"zstack"}
    baremetal_ins = test_stub.create_baremetal_ins(image_uuid, chassis_uuid, template.uuid, 'root', 'password', nic_cfgs, bonding_cfgs, customConfigurations, systemTags=tag)
    baremetal_ins_uuid = baremetal_ins.uuid
    
    test_util.test_dsc('wait for iso installation')    
#    vm_ip = vm_inv.vmNics[0].ip
    for i in range(0, 30):
        cond = res_ops.gen_query_conditions('uuid', '=', baremetal_ins_uuid)
        bm_status = res_ops.query_resource(res_ops.BAREMETAL_INS, cond)[0].status
        if bm_status == 'Provisioned':
            baremetal_operations.stop_baremetal_instance(baremetal_ins_uuid)
            time.sleep(10)
            baremetal_operations.start_baremetal_instance(baremetal_ins_uuid)
            break
        else:
            time.sleep(60)    

    cond = res_ops.gen_query_conditions('name', '=', 'vm-for-baremetal')
    vm_inv = res_ops.query_resource(res_ops.VM_INSTANCE, cond)[0]
    vm_ip = vm_inv.vmNics[0].ip
    if not test_lib.lib_wait_target_up(ip_address1, '22', 180):
        test_util.test_fail("iso has not been failed to installed.")

    test_util.test_dsc('Check baremetal instance operations')
    cmd = 'hostname'
    result = test_lib.lib_execute_ssh_cmd(ip_address1, 'root', 'password', cmd, 180)
    if 'zstack' not in result:
        test_util.test_fail('Fail to set hostname in vm')
    cmd = 'ip a |grep -C 2 %s' % ip_address1
    result = test_lib.lib_execute_ssh_cmd(ip_address1, 'root', 'password', cmd, 180)
    if vm_nic_mac not in result:
        test_util.test_fail('Fail to set static ip to vlan network')
    cmd = 'ip a |grep bond0'
    result = test_lib.lib_execute_ssh_cmd(ip_address1, 'root', 'password', cmd, 180)
    if ip_address2 not in result:
        test_util.test_fail('Fail to set static ip to bond0')


    #test_util.test_dsc('Clear env')
    baremetal_operations.destory_baremetal_instance(baremetal_ins_uuid)
    baremetal_operations.expunge_baremetal_instance(baremetal_ins_uuid)
    test_stub.delete_vbmc(vm, host_ip)
    baremetal_operations.delete_chassis(chassis_uuid)
    vm.destroy()
    baremetal_operations.delete_pxe(pxe_uuid)
    cluster_ops.delete_cluster(baremetal_cluster_uuid)
    test_util.test_pass('Create chassis Test Success')

def error_cleanup():
    global vm, baremetal_cluster_uuid, pxe_uuid, host_ip
    if vm:
        test_stub.delete_vbmc(vm, host_ip)
        chassis = os.environ.get('ipminame')
        chassis_uuid = test_lib.lib_get_chassis_by_name(chassis).uuid
        baremetal_operations.delete_chassis(chassis_uuid)
        vm.destroy()
        if host_ip:
            test_stub.delete_vbmc(vm, host_ip)
    if baremetal_cluster_uuid:
        cluster_ops.delete_cluster(baremetal_cluster_uuid)
    if pxe_uuid:
        baremetal_ops.delete_pxe(pxe_uuid)
