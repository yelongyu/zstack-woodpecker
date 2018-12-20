import zstackwoodpecker.operations.baremetal_operations as bare_operations
import zstackwoodpecker.operations.cluster_operations as cluster_ops
import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as zstack_vm_header
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import zstackwoodpecker.operations.scenario_operations as sce_ops
import zstacklib.utils.jsonobject as jsonobject
import zstacklib.utils.xmlobject as xmlobject
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstacklib.utils.shell as shell
import zstacklib.utils.ssh as ssh
import subprocess
import random
import os
import re
import time

def deploy_vbmc(host_ips):
    for host_ip in host_ips.strip().split(' '):
        test_util.test_logger('Candidate host ip is %s' %host_ip)
        ssh_cmd = 'sshpass -p password ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null'
        if shell.run("%s %s which vbmc" %(ssh_cmd, host_ip)) != 0:
            shell.call('%s %s yum --disablerepo=epel install -y \
                 /opt/zstack-dvd/Extra/qemu-kvm-ev/libvirt-4.1.0/libvirt-libs-*' %(ssh_cmd, host_ip))
            shell.call('%s %s yum --disablerepo=epel install -y \
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
		hostname = None, storagePath = '/pxe_store', sshUsername = 'root', \
		sshPassword = 'password', sshPort = 22, zoneUuid = None,  
		range_end = None, netmask = None, session_uuid = None):
    pxe_option = test_util.PxeOption()
    if not hostname:
        hostname = '127.0.0.1'
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

def create_vm_with_random_offering(vm_name, image_name=None, l3_name=None, session_uuid=None,
                                   instance_offering_uuid=None, host_uuid=None, disk_offering_uuids=None,
                                   root_password=None, ps_uuid=None, system_tags=None, timeout=None):
    if image_name:
        image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    else:
        conf = res_ops.gen_query_conditions('format', '!=', 'iso')
        conf = res_ops.gen_query_conditions('mediaType', '!=', 'ISO', conf)
        conf = res_ops.gen_query_conditions('system', '=', 'false', conf)
        image_uuid = random.choice(res_ops.query_resource(res_ops.IMAGE, conf)).uuid

    if l3_name:
        l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    else:
        l3_net_uuid = random.choice(res_ops.get_resource(res_ops.L3_NETWORK)).uuid

    if not instance_offering_uuid:
        conf = res_ops.gen_query_conditions('type', '=', 'UserVM')
        instance_offering_uuid = random.choice(res_ops.query_resource(res_ops.INSTANCE_OFFERING, conf)).uuid

    vm_creation_option = test_util.VmOption()
    vm_creation_option.set_l3_uuids([l3_net_uuid])
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_name(vm_name)
    if system_tags:
        vm_creation_option.set_system_tags(system_tags)
    if disk_offering_uuids:
        vm_creation_option.set_data_disk_uuids(disk_offering_uuids)
    if root_password:
        vm_creation_option.set_root_password(root_password)
    if host_uuid:
        vm_creation_option.set_host_uuid(host_uuid)
    if session_uuid:
        vm_creation_option.set_session_uuid(session_uuid)
    if ps_uuid:
        vm_creation_option.set_ps_uuid(ps_uuid)
    if timeout:
        vm_creation_option.set_timeout(timeout)

    vm = test_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    return vm

def create_multi_vms(name_prefix='', count=None, host_uuid=None,image_name=None, l3_name=None, ps_uuid=None, data_volume_number=0, ps_uuid_for_data_vol=None, timeout=None):
    vm_list = []
    if not image_name:
        image_name = os.environ.get('imageName_s')
    if not l3_name:
        l3_name = os.environ.get('scenl3VPCNetworkName1')
    for i in xrange(count):
        if not data_volume_number:
            vm = create_vm_with_random_offering(name_prefix+"{}".format(i), image_name=image_name,
                                                l3_name=l3_name, host_uuid=host_uuid, ps_uuid=ps_uuid, timeout=timeout)
        else:
            disk_offering_list = res_ops.get_resource(res_ops.DISK_OFFERING)
            disk_offering_uuids = [random.choice(disk_offering_list).uuid for _ in xrange(data_volume_number)]
            if ps_uuid_for_data_vol:
                vm = create_vm_with_random_offering(name_prefix+"{}".format(i), image_name=image_name,
                                                    l3_name=l3_name, host_uuid=host_uuid, ps_uuid=ps_uuid,
                                                    disk_offering_uuids=disk_offering_uuids,
                                                    system_tags=['primaryStorageUuidForDataVolume::{}'.format(ps_uuid_for_data_vol)], timeout=timeout)
            else:
                vm = create_vm_with_random_offering(name_prefix+"{}".format(i), image_name=image_name,
                                                    l3_name=l3_name, host_uuid=host_uuid, ps_uuid=ps_uuid,
                                                    disk_offering_uuids=disk_offering_uuids, timeout=timeout)

        vm_list.append(vm)
    if host_uuid:
        for vm in vm_list:
            assert vm.get_vm().hostUuid == host_uuid
    if ps_uuid:
        for vm in vm_list:
            root_volume = test_lib.lib_get_root_volume(vm.get_vm())
            assert root_volume.primaryStorageUuid == ps_uuid

    if ps_uuid_for_data_vol:
        for vm in vm_list:
            data_volume_list = [volume for volume in vm.get_vm().allVolumes if volume.type != 'Root']
            for data_volume in data_volume_list:
                assert data_volume.primaryStorageUuid == ps_uuid_for_data_vol

    return vm_list

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

def setup_static_ip(scenario_file):
    ssh_cmd = 'sshpass -p password ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null'
    with open(scenario_file, 'r') as fd:
        xmlstr = fd.read()
        fd.close()
        scenario_file = xmlobject.loads(xmlstr)
        for vm in xmlobject.safe_list(scenario_file.vms.vm):
            mnip = vm.managementIp_
            if xmlobject.has_element(vm, 'ips'): 
                for ip in xmlobject.safe_list(vm.ips.ip):
                    nic_ip = ip.ip_
                    if nic_ip.startswith("10"):
                        nic = "br_zsn1"
                        netmask = "255.255.255.0"
                        shell.call("%s %s zs-network-setting -i %s %s %s|exit 0" %(ssh_cmd, mnip, nic, nic_ip, netmask) )
    return

def get_host_by_index_in_scenario_file(scenarioConfig, scenarioFile, index):
    test_util.test_logger("@@DEBUG@@:<scenarioConfig:%s><scenarioFile:%s><scenarioFile is existed: %s>" \
                          %(str(scenarioConfig), str(scenarioFile), str(os.path.exists(scenarioFile))))
    if scenarioConfig == None or scenarioFile == None or not os.path.exists(scenarioFile):
        return [] 

    test_util.test_logger("@@DEBUG@@: after config file exist check")
    with open(scenarioFile, 'r') as fd:
        xmlstr = fd.read()
        fd.close()
        scenario_file = xmlobject.loads(xmlstr)
        return xmlobject.safe_list(scenario_file.vms.vm)[index]

def query_host(host_ip, scenarioConfig):
    mn_ip = scenarioConfig.basicConfig.zstackManagementIp.text_
    try:
        host_inv = sce_ops.get_vm_inv_by_vm_ip(mn_ip, host_ip)
        return host_inv
    except:
        test_util.test_logger("Fail to query host [%s]" % host_ip)
        return False

def recover_vlan_in_host(host_ip, scenarioConfig, deploy_config):
    test_util.test_logger("func: recover_vlan_in_host; host_ip=%s" %(host_ip))

    host_inv = query_host(host_ip, scenarioConfig)
    test_lib.lib_wait_target_up(host_ip, '22', 120)
    host_config = sce_ops.get_scenario_config_vm(host_inv.name,scenarioConfig)
    for l3network in xmlobject.safe_list(host_config.l3Networks.l3Network):
        test_util.test_logger("loop in for l3network")
        if hasattr(l3network, 'l2NetworkRef'):
            test_util.test_logger("below if l2NetworkRef")
            for l2networkref in xmlobject.safe_list(l3network.l2NetworkRef):
                test_util.test_logger("loop in l2networkref")
                nic_name = sce_ops.get_ref_l2_nic_name(l2networkref.text_, deploy_config)
                test_util.test_logger("nic_name=%s; l2networkref.text_=%s" %(nic_name, l2networkref.text_))
                if nic_name.find('.') >= 0 :
                    vlan = nic_name.split('.')[1]
                    test_util.test_logger('[vm:] %s %s is created.' % (host_ip, nic_name.replace("eth","zsn")))
                    cmd = 'vconfig add %s %s' % (nic_name.split('.')[0].replace("eth","zsn"), vlan)
                    test_util.test_logger("vconfig cmd=%s" %(cmd))
                    test_lib.lib_execute_ssh_cmd(host_ip, host_config.imageUsername_, host_config.imagePassword_, cmd)
    return True

def restart_mn_node_with_long_timeout():

    mn_ip = os.environ['zstackHaVip']

    test_lib.lib_wait_target_up(mn_ip, '22', 120)

    cmd = "zstack-ctl status|grep 'MN status'|awk '{print $3}'"
    ret, stdout, stderr = ssh.execute(cmd, mn_ip, "root", "password", False, 22)

    if stdout.strip().strip('\n').lower() != "running":

        check_mn_tool_path = "%s/%s" %(os.environ.get('woodpecker_root_path'), '/tools/check_mn_start.sh')
        test_util.test_logger("check_mn_tool_path:[%s],mn_ip:[%s]" %(check_mn_tool_path, mn_ip))
        ssh.scp_file(check_mn_tool_path, "/home/check_mn_start.sh", mn_ip, "root", "password")

        cmd = "bash /home/check_mn_start.sh"
        ret1, stdout1, stderr1 = ssh.execute(cmd, mn_ip, "root", "password", False, 22)
        test_util.test_logger("check_mn_start.sh stdout1:[%s],stderr1:[%s]" %(stdout1,stderr1))

        if str(ret1) == "0" :
            cmd = "zstack-ctl stop"
            ret, stdout, stderr = ssh.execute(cmd, mn_ip, "root", "password", True, 22)
            cmd = "zstack-ctl configure ThreadFacade.maxThreadNum=200"
            ret, stdout, stderr = ssh.execute(cmd, mn_ip, "root", "password", True, 22)
            cmd = "zstack-ctl start_node --timeout 3000"
            ret, stdout, stderr = ssh.execute(cmd, mn_ip, "root", "password", True, 22)
            cmd = "zstack-ctl start_ui"
            ret, stdout, stderr = ssh.execute(cmd, mn_ip, "root", "password", True, 22)

            #modify zstack start script
            cmd = r'sed -i "s:zstack-ctl start:zstack-ctl start_node --timeout 3000:g" /etc/init.d/zstack-server'
            test_lib.lib_execute_ssh_cmd(mn_ip, "root", "password", cmd)
            time.sleep(1)
            cmd = r'sed -i "/zstack-ctl start_node --timeout 3000/ a\    ZSTACK_HOME=\$zstack_app zstack-ctl start_ui" /etc/init.d/zstack-server'
            test_lib.lib_execute_ssh_cmd(mn_ip, "root", "password", cmd)

        else:
            test_util.test_logger("find mn not self-started as expected, checked by /home/check_mn_start.sh")

    else:
        test_util.test_logger("find zstack MN is running.")

def auto_set_mn_ip(scenario_file):
    host_ip_lst = sce_ops.dump_scenario_file_ips(scenario_file)
    host_ip = host_ip_lst[0]
    for i in range(60):
        time.sleep(10)
        #cmd = "zsha2 status |grep -B 2 'Owns virtual address: *yes'|grep 'Status report from'|awk -F' ' '{print $4}'"
        cmd = "zsha2 status|grep VIP|head -n 1|awk -F' ' '{print $2}'"
        test_util.test_logger("@@@DEBUG->cmd=<%s>;host_ip=<%s>" %(cmd, host_ip))
        ret, mn_vip, stderr = ssh.execute(cmd, host_ip, "root", "password", False, 22)
        if re.match(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$", mn_vip):
            test_util.test_logger("find mn_host_ip=%s" %(mn_vip))
            break
    else:
        test_util.test_fail("not find valid mn_host_ip within 300s")

    mn_ip = mn_vip.strip()
    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mn_ip
    os.environ['zstackHaVip'] = mn_ip
    test_util.test_logger("@@@DEBUG->in auto_set_mn_ip@@@ os\.environ\[\'ZSTACK_BUILT_IN_HTTP_SERVER_IP\'\]=%s; os\.environ\[\'zstackHaVip\'\]=%s"      \
                          %(os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'], os.environ['zstackHaVip']) )
    cmd = 'sed -i "s/zstackHaVip = .*$/zstackHaVip = %s/g" /root/.zstackwoodpecker/integrationtest/vm/mn_ha/deploy.tmpt' %(mn_ip)
    test_util.test_logger("@@@DEBUG->replace zstackHaVip @@@: %s" %cmd)
    os.system(cmd)

def wrapper_of_wait_for_management_server_start(wait_start_timeout, EXTRA_SUITE_SETUP_SCRIPT=None):
    import zstackwoodpecker.operations.node_operations as node_operations
    if os.path.basename(os.environ.get('WOODPECKER_SCENARIO_CONFIG_FILE')).strip() == "scenario-config-mnha2.xml":
        test_util.test_logger("@@@DEBUG->IS MNHA2@@@")
        if os.environ.get('zstackHaVip'):
            old_mn_ip = os.environ['zstackHaVip']
        auto_set_mn_ip(test_lib.scenario_file)
        if EXTRA_SUITE_SETUP_SCRIPT and EXTRA_SUITE_SETUP_SCRIPT != "":
            cmd = 'sed -i "s/%s/%s/g" %s' %(old_mn_ip, os.environ['zstackHaVip'], EXTRA_SUITE_SETUP_SCRIPT)
            test_util.test_logger("@@@DEBUG-> run cmd: %s @@@ " %(cmd))
            os.system(cmd)
    try:
        node_operations.wait_for_management_server_start(wait_start_timeout)
    except:
        restart_mn_node_with_long_timeout()

def deploy_2ha(scenarioConfig, scenarioFile):
    mn_ip1 = get_host_by_index_in_scenario_file(scenarioConfig, scenarioFile, 0).ip_
    mn_ip2 = get_host_by_index_in_scenario_file(scenarioConfig, scenarioFile, 1).ip_
    node3_ip = get_host_by_index_in_scenario_file(scenarioConfig, scenarioFile, 2).ip_
    vip = os.environ['zstackHaVip']

    change_ip_cmd1 = "zstack-ctl change_ip --ip=" + mn_ip1
    ssh.execute(change_ip_cmd1, mn_ip1, "root", "password", False, 22)
    iptables_cmd1 = "iptables -I INPUT -d " + vip + " -j ACCEPT"
    ssh.execute(iptables_cmd1, mn_ip1, "root", "password", False, 22)

    change_ip_cmd2 = "zstack-ctl change_ip --ip=" + mn_ip2
    ssh.execute(change_ip_cmd2, mn_ip2, "root", "password", False, 22)
    iptables_cmd2 = "iptables -I INPUT -d " + vip + " -j ACCEPT"
    ssh.execute(iptables_cmd2, mn_ip2, "root", "password", False, 22)

    woodpecker_vm_ip = shell.call("ip r | grep src | grep '^172.20' | head -1 | awk '{print $NF}'").strip()
    zsha2_path = "/home/%s/zsha2" % woodpecker_vm_ip
    ssh.scp_file(zsha2_path, "/root/zsha2", mn_ip1, "root", "password")
    ssh.execute("chmod a+x /root/zsha2", mn_ip1, "root", "password", False, 22)

    zstack_hamon_path = "/home/%s/zstack-hamon" % woodpecker_vm_ip
    ssh.scp_file(zstack_hamon_path, "/root/zstack-hamon", mn_ip1, "root", "password")
    ssh.execute("chmod a+x /root/zstack-hamon", mn_ip1, "root", "password", False, 22)

    cmd = '/root/zsha2 install-ha -nic br_zsn0 -gateway 172.20.0.1 -slave "root:password@' + mn_ip2 + '" -vip ' + vip + ' -time-server ' + node3_ip + ' -db-root-pw zstack.mysql.password -yes'
    test_util.test_logger("deploy 2ha by cmd: %s" %(cmd))
    ret, output, stderr = ssh.execute(cmd, mn_ip1, "root", "password", False, 22)
    test_util.test_logger("cmd=%s; ret=%s; output=%s; stderr=%s" %(cmd, ret, output, stderr))
    if ret!=0:
        test_util.test_fail("deploy 2ha failed")

