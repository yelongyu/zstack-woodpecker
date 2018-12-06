import zstackwoodpecker.operations.baremetal_operations as bare_operations
import zstackwoodpecker.operations.cluster_operations as cluster_ops
import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as zstack_vm_header
import zstacklib.utils.jsonobject as jsonobject
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstacklib.utils.shell as shell
import subprocess
import os
import re
import time

def deploy_vbmc(host_ips):
    for host_ip in host_ips.strip().split(' '):
        test_util.test_logger('Candidate host ip is %s' %host_ip)
        ssh_cmd = 'sshpass -p password ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null'
        shell.call('%s %s yum --disablerepo=epel --enablerepo=qemu-kvm-ev install -y \
             /opt/zstack-dvd/Extra/qemu-kvm-ev/libvirt-4.1.0/libvirt-devel-*' %(ssh_cmd, host_ip))
        shell.call('%s %s wget http://192.168.200.100/mirror/scripts/get-pip.py'%(ssh_cmd, host_ip))
        shell.call('%s %s python  get-pip.py' %(ssh_cmd, host_ip))
        shell.call('%s %s pip install virtualbmc' %(ssh_cmd, host_ip))
    test_util.test_logger('Virtualbmc has been deployed on Host')

def add_hosts(host_ips):
    for host_ip in host_ips:
        host_option = test_tuil.HostOption()
        host_option = set_cluster_uuid()
        host_option = set_username('root')
        host_option = set_password('password')
        host_option = set_management_ip(host_ip) 
        host_option = set_name(host_ip) 
        host_ops.add_kvm_host(host_option)
    test_util.test_logger('Add KVM hosts finished')

def create_cluster(zone_uuid, cluster_name = None, session_uuid = None):
    if not cluster_name:
        cluster_name = 'baremetal_cluster'
    cluster_option = test_util.ClusterOption()
    cluster_option.set_name(cluster_name)
    cluster_option.set_hypervisor_type('baremetal')
    cluster_option.set_type('baremetal')
    cluster_option.set_zone_uuid(zone_uuid)
    cluster_option.set_session_uuid(session_uuid)
    cluster = cluster_ops.create_cluster(cluster_option)
    return cluster

def create_pxe(dhcp_interface = None, name = None, range_begin = None, \
		hostname = '127.0.0.1', storagePath = 'pxe_store', sshUsername = 'root', \
		sshPassword = 'password', sshPort = 22, zoneUuid = None,  
		range_end = None, netmask = None, session_uuid = None):
    pxe_option = test_util.PxeOption()
    if not dhcp_interface:
        dhcp_interface = os.environ.get('dhcpinterface')
    if not range_begin:
        range_begin = os.environ.get('scenvpcIpRangeStart1')
    if not range_end:
        range_end = os.environ.get('scenvpcIpRangeEnd1')
    if not netmask:
        netmask = os.environ.get('scenvpcIpRangeNetmask1')
    pxe_option.set_dhcp_interface(dhcp_interface)
    pxe_option.set_dhcp_range_end(range_end)
    pxe_option.set_dhcp_range_begin(range_begin)
    pxe_option.set_dhcp_netmask(netmask)
    pxe_option.set_hostname(hostname)
    pxe_option.set_storagePath(storagePath)
    pxe_option.set_sshUsername(sshUsername)
    pxe_option.set_sshPassword(sshPassword)
    pxe_option.set_sshPort(sshPort)
    pxe_option.set_zoneUuid(zoneUuid)
    if session_uuid:
        pxe_option.set_session_uuid(session_uuid)
    pxe = bare_operations.create_pxe(pxe_option)
    return pxe

def create_vm(vm_name = 'vm_for_baremetal', image_name = None, \
             l3_name = None, instance_offering_uuid = None, \
             host_uuid = None, disk_offering_uuid = None, cluster_uuid = None, \
             system_tags = None, password = None, session_uuid = None):
    if not instance_offering_uuid:
        instance_offering_name = os.environ.get('instanceOfferingName_m')
        instance_offering_uuid = test_lib.lib_get_instance_offering_by_name(instance_offering_name).uuid
    if not image_name:
        image_name = os.environ.get('imageName_s')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    if not l3_name:
        l3_name = os.environ.get('scenl3VPCNetworkName1')
    l3_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid

    vm_creation_option = test_util.VmOption()
    vm_creation_option.set_name(vm_name)
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_l3_uuids([l3_uuid])
    if cluster_uuid:
        vm_creation_option.set_cluster_uuid(cluster_uuid)
    if system_tags: 
        vm_creation_option.set_system_tags(system_tags)
    if disk_offering_uuid:
        vm_creation_option.set_data_disk_uuids(disk_offering_uuid)
    if password:
        vm_creation_option.set_root_password(password)
    if host_uuid:
        vm_creation_option.set_host_uuid(host_uuid)
    if session_uuid:
        vm_creation_option.set_session_uuid(session_uuid)
    vm = zstack_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    return vm

def create_chassis(cluster_uuid, name = None, address = None, username = None, \
     password = None, port = None, session_uuid=None):

    if not name:
        name = os.environ.get('ipminame')
    if not address:
        address = os.environ.get('ipmiaddress')
    if not username:
        username = os.environ.get('ipmiusername')
    if not password:
        password = os.environ.get('ipmipassword')
    if not port:
        port = os.environ.get('ipmiport')
    chassis_option = test_util.ChassisOption()
    chassis_option.set_name(name)
    chassis_option.set_ipmi_address(address)
    chassis_option.set_ipmi_username(username)
    chassis_option.set_ipmi_password(password)
    chassis_option.set_ipmi_port(port)
    chassis_option.set_cluster_uuid(cluster_uuid)
    chassis_option.set_session_uuid(session_uuid)
    chassis = bare_operations.create_chassis(chassis_option)
    return chassis

def create_baremetal_ins(image_uuid, chassis_uuid, password = 'password', \
	nic_cfgs = None, strategy = None, name = None, session_uuid = None):
    if not name:
        name = 'baremetal_instance'

    baremetal_ins_option = test_util.BaremetalInstanceOption()
    baremetal_ins_option.set_name(name)
    baremetal_ins_option.set_password(password)
    baremetal_ins_option.set_image_uuid(image_uuid)
    baremetal_ins_option.set_chassis_uuid(chassis_uuid)
    if nic_cfgs:
        baremetal_ins_option.set_nic_cfgs(nic_cfgs)
    if strategy:
        baremetal_ins_option.set_strategy(strategy)
    baremetal_ins = bare_operations.create_baremetal_instance(baremetal_ins_option, session_uuid)
    return baremetal_ins

def create_hostcfg(chassis_uuid=None, unattended=True, vnc=True, \
                   password="password", cfgItems=None, session_uuid=None):
    hostcfg_option = test_util.BaremetalHostCfgOption()
    hostcfg_option.set_chassis_uuid(chassis_uuid)
    hostcfg_option.set_unattended(unattended)
    hostcfg_option.set_vnc(vnc)
    hostcfg_option.set_cfgItems(cfgItems)
    if session_uuid:
        hostcfg_option.set_session_uuid(session_uuid)
    hostcfg = bare_operations.create_hostcfg(hostcfg_option, session_uuid)
    return hostcfg

def gen_nicCfg(**dicargs):
    niccfg={}
    for k in dicargs:
        niccfg[k] = dicargs[k]
    return niccfg

def gen_bond(**dicargs):
    bonding={}
    for k in dicargs:
        bonding[k] = dicargs[k]
    return bonding

def generate_bond(bond_num, slave_num, mac_list, mode):
    bondCfg=[]
    for i in range(bond_num):
        ip = os.environ.get("bondip%d" % i)
        netmask = os.environ.get("bondmask%d" % i)
        name = os.environ.get("bondname%d" % i)
        mode = mode
        mac_list1 = mac_list[:slave_num]
        slaves = ','.join(mac_list1)
        mac_list = mac_list[slave_num:]
        bondcfg = gen_bond(name=name, slaves=slaves, mode=mode, ip=ip, netmask=netmask)
        bondCfg.append(bondcfg)
    return bondCfg

def get_nicinfo(chassis_uuid=None):
    hwinfo = test_lib.lib_get_hwinfo(chassis_uuid)
    for i in range(len(hwinfo)):
        if hwinfo[i].type == "nic":
            nic_num = len(hwinfo[i].content)
            nic_info = hwinfo[i].content
    return nic_info

#nic_flag=True indicates dont need to set ip for pxe nic
def generate_nicCfg(nic_flag, mac_list):
    #nic_info = get_nicinfo(chassis_uuid)
    #nic_info1 = jsonobject.loads(nic_info)
    nicCfg=[]
    for i in range(len(mac_list)):
        mac = mac_list[i]
        pxe = "true" if i==0 else "false"
        if nic_flag and i == 0:
            niccfg = gen_nicCfg(mac=mac, pxe=pxe)
        else:
            ip = os.environ.get("nicip%d" % i)
            netmask = os.environ.get("nicnetmask%d" % i)
            niccfg = gen_nicCfg(mac=mac, pxe=pxe, ip=ip, netmask=netmask)
        nicCfg.append(niccfg)
    return nicCfg

def generate_cfgItems(chassis_uuid=None, nic_num=1, nic_flag=True, bond_num=0, slave_num=1, mode=4):
    cfgItems={}
    mac_list = []
    nic_info = jsonobject.loads(get_nicinfo(chassis_uuid))
    for i in range(len(nic_info)):
        mac_list.append(nic_info[i]["mac"])
    nic_mac = mac_list[:nic_num]
    bond_mac = mac_list[nic_num:]
    
    nicCfg = generate_nicCfg(nic_flag=nic_flag, mac_list=nic_mac)
    cfgItems["nicCfgs"] = map(str, nicCfg)
    test_util.test_logger(cfgItems["nicCfgs"])
    bondCfg = generate_bond(bond_num=bond_num, slave_num=slave_num, mac_list=bond_mac, mode=mode)
    if bondCfg:
        cfgItems["bondings"] = map(str, bondCfg)
    return cfgItems, nicCfg[0]["mac"]
    
def create_vbmc(vm, host_ip, port):
    ssh_cmd = 'ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null'
    vm_uuid = vm.vm.uuid
    ipmi_port = port
    #vmbc process unable to exit, so use subprocess
    child = subprocess.Popen('%s %s vbmc add %s --port  %d' % (ssh_cmd, host_ip, vm_uuid, ipmi_port),shell=True)
    time.sleep(10)
    #child.kill()
    child = subprocess.Popen('%s %s vbmc start %s' % (ssh_cmd, host_ip, vm_uuid), shell=True)
    #time.sleep(1)
    #child.kill()

def delete_vbmc(vm, host_ip):
    vm_uuid = vm.vm.uuid
    child = subprocess.Popen('ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null \
                %s vbmc delete %s' %(host_ip, vm_uuid), shell=True)
    time.sleep(1)
    child.kill()

def hack_inspect_ks(host_ip, port = 623, ks_file='inspector_ks.cfg'):
    path = '/var/lib/zstack/baremetal/ftp/ks'
    shell.call('scp %s:%s/%s .' %(host_ip, path, ks_file))
    ks = ks_file
    with open(ks, 'r') as ks_in:
        lines = ks_in.readlines()
    with open(ks, 'w') as ks_out:
        for line in lines:
            if 'status1:' in line:
                line = re.sub('if not status1:', 'if status1:', line)
            if 'ipmiPort = 623' in line:
                line = line + '\nipmiAddress = "127.0.0.1"\nipmiPort = 623\n' 
            ks_out.write(line)
    shell.call('scp %s %s:%s'  %(ks_file, host_ip, path))

def hack_generic_ks(host_ip):
    path = '/var/lib/zstack/virtualenv/baremetalpxeserver/lib/python2.7/site-packages/baremetalpxeserver/ks_tmpl/generic_ks_tmpl'
    shell.call('scp %s:%s .' %(host_ip, path))
    ks = 'generic_ks_tmpl'
    with open(ks, 'r') as ks_in:
        lines = ks_in.readlines()
    with open(ks, 'w') as ks_out:
        for line in lines:
            if 'EXTRA_REPO' in line:
                line = 'clearpart --all --initlabel\nautopart --type=lvm\n%packages\n@^minimal\n%end\n' + line
            ks_out.write(line)
    shell.call('scp %s %s:%s'  %(ks, host_ip, path))

def ca_pem_workaround(host_ip):
    ssh_cmd = 'ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null'
    dst_folder = '/usr/local/zstack/imagestore/bin/certs'
    src_file = '/usr/local/zstacktest/imagestore/bin/certs/ca.pem'
    shell.call('%s %s "mkdir -p %s && cp %s %s" ' % (ssh_cmd, host_ip, dst_folder, src_file, dst_folder))

def check_hwinfo(chassis_uuid):
    count = 0
    hwinfo = None
    while not hwinfo:
        hwinfo, status = test_lib.lib_get_hwinfo(chassis_uuid)
        if status == "PxeBootFailed":
            test_util.test_logger('Fail: Get Hardware Info Failed')
            break
        time.sleep(30)
        count += 1
        if count > 20:
            test_util.test_logger('Fail: Get Hardware Info 10 mins Timeout')
            break
    return hwinfo

def check_baremetal_ins(ins_uuid, password, ins_ip, mn_ip, chassis_uuid, ipmi):
    ssh_cmd = 'ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null'
    count = 0
    result = False
    while not result:
        status = bare_operations.get_power_status(chassis_uuid).status
        if status.find('off') != -1:
            test_util.test_logger('Power on Baremetal instance %s' %ins_uuid)
            shell.call('%s %s ipmitool -I lanplus -H %s -U admin -P password \
		chassis bootdev disk' %(ssh_cmd, mn_ip, ipmi))
            time.sleep(60)
            bare_operations.power_on_baremetal(chassis_uuid)
        else:
            output = os.system('sshpass -p %s ssh %s exit' %(password, ins_ip))
            if output == 0:
                result = True
                test_util.test_logger('SSH Baremetal Instance Success')
                break
        time.sleep(60)
        count += 1
        if count > 20:
            test_util.test_logger('Fail: Get Hardware Info 20 mins Timeout')
            break
    return result

def check_chassis_status(chassis_uuid):
    chassis = test_lib.lib_get_chassis_by_uuid(chassis_uuid)
    return chassis.status

def verify_chassis_status(chassis_uuid, status):
    current_status = check_chassis_status(chassis_uuid)
    expect_status = status
    count = 0
    timeout = 20 if expect_status == "Rebooting" else 120
    while current_status != expect_status:
        time.sleep(15)
        count += 1
        if count > timeout:
            test_util.test_logger('Fail: Get chassis status timeout, expect status: %s current status %s' % (expect_status, current_status))
	    break
        current_status = check_chassis_status(chassis_uuid)
    return (current_status == expect_status)
