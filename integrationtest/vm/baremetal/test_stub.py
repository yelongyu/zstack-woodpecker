import zstackwoodpecker.operations.baremetal_operations as bare_operations
import zstackwoodpecker.zstack_test.zstack_test_vm as zstack_vm_header
import zstacklib.utils.jsonobject as jsonobject
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstacklib.utils.shell as shell
import os
import re
import time

def create_pxe(pxe_option=None, session_uuid=None):
    if not pxe_option:
    	pxe_option = test_util.PxeOption()
        pxe_option.set_dhcp_interface(os.environ.get('dhcpinterface'))
        pxe_option.set_dhcp_range_end(os.environ.get('dhcpend'))
        pxe_option.set_dhcp_range_begin(os.environ.get('dhcpbegin'))
        pxe_option.set_dhcp_netmask(os.environ.get('dhcpnetmask'))
    if session_uuid:
        pxe_option.set_session_uuid(session_uuid)
    pxe = bare_operations.create_pxe(pxe_option)
    return pxe

def create_vm(vm_name = 'vm1', image_name = None, \
             l3_name = None, instance_offering_uuid = None, \
             host_uuid = None, disk_offering_uuid = None, \
             system_tags = None, password = None, session_uuid = None):

    if not image_name:
        image_name = os.environ.get('imageName_s')

    if not l3_name:
        l3_name1 = os.environ.get('l3PublicNetworkName')
        l3_name2 = os.environ.get('l3VlanNetworkName1')
        l3_name3 = os.environ.get('l3VlanNetworkName3')

    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    l3_uuid1 = test_lib.lib_get_l3_by_name(l3_name1).uuid
    l3_uuid2 = test_lib.lib_get_l3_by_name(l3_name2).uuid
    l3_uuid3 = test_lib.lib_get_l3_by_name(l3_name3).uuid

    if not instance_offering_uuid:
        instance_offering_name = os.environ.get('instanceOfferingName_m')

    instance_offering_uuid = test_lib.lib_get_instance_offering_by_name(instance_offering_name).uuid
    
    vm_creation_option = test_util.VmOption()
    vm_creation_option.set_l3_uuids([l3_uuid1, l3_uuid2, l3_uuid3])
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_name(vm_name)
    vm_creation_option.set_system_tags(system_tags)
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

def create_chassis(chassis_name = "Chassis_Test", chassis_option=None, session_uuid=None):
    if not chassis_option:
        chassis_option = test_util.ChassisOption()
        chassis_option.set_name(chassis_name)
        chassis_option.set_ipmi_address(os.environ.get('ipmiaddress'))
        chassis_option.set_ipmi_username(os.environ.get('ipmiusername'))
        chassis_option.set_ipmi_password(os.environ.get('ipmipassword'))
        chassis_option.set_ipmi_port(os.environ.get('ipmiport'))
    if session_uuid:
        chassis_option.set_session_uuid(session_uuid)
    chassis = bare_operations.create_chassis(chassis_option, session_uuid)
    return chassis

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
    shell.call('%s %s vbmc add %s --port  %d' % (ssh_cmd, host_ip, vm_uuid, ipmi_port))
    os.system('%s %s vbmc start %s' % (ssh_cmd, host_ip, vm_uuid))

def delete_vbmc(vm, host_ip):
    vm_uuid = vm.vm.uuid
    shell.call('ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s vbmc delete %s' %(host_ip, vm_uuid))

def hack_ks(port = 623, ks_file='inspector_ks.cfg'):
    path = '/var/lib/zstack/baremetal/ftp/ks'
    ks = os.path.join(path, ks_file)
    with open(ks, 'r') as ks_in:
        lines = ks_in.readlines()
    with open(ks, 'w') as ks_out:
        for line in lines:
            if 'status1:' in line:
                line = re.sub('if not status1:', 'if status1:', line)
            if 'ipmiPort = 623' in line:
                line = line + '\nipmiAddress = "127.0.0.1"\nipmiPort = 623' 
            #if 'ipmiAddress' in line:
            #    line = re.sub('ipmiAddress = .*$', 'ipmiAddress = "%s"' % os.environ.get('ipmiaddress'), line)
            #if 'ipmiPort'in line:
            #    line = re.sub('ipmiPort = .*$','ipmiPort = "%s"' % str(port), line)
            ks_out.write(line)

def check_hwinfo(chassis_uuid):
    count =0
    while not test_lib.lib_get_hwinfo(chassis_uuid):
        time.sleep(6)
        count += 1
        if count > 100:
            test_util.test_logger('Fail: Get Hardware Info timeout')
            break
    test_util.test_logger('Get Hardware Info')
    return test_lib.lib_get_hwinfo(chassis_uuid)

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

    



