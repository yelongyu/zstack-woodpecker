'''

Create an unified test_stub to share test operations

@author: Mirabel
'''
import os
import time
import zstacklib.utils.ssh as ssh
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_util as test_util
import zstacklib.utils.shell as shell
import zstacklib.utils.xmlobject as xmlobject
import zstackwoodpecker.operations.scenario_operations as sce_ops
import zstackwoodpecker.operations.deploy_operations as dpy_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import zstackwoodpecker.operations.ha_operations as ha_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.backupstorage_operations as bs_ops
import zstackwoodpecker.operations.primarystorage_operations as ps_ops
import zstackwoodpecker.operations.host_operations as host_ops




def wait_for_mn_ha_ready(scenarioConfig, scenarioFile):
    mn_host_list = get_mn_host(scenarioConfig, scenarioFile)
    if len(mn_host_list) < 1:
        return []
    for i in range(0, 5):
        for host in mn_host_list:
            host_config = sce_ops.get_scenario_config_vm(host.name_, scenarioConfig)
            try:
                cmd = "zsha status"
                zsha_status = test_lib.lib_execute_ssh_cmd(host.ip_, host_config.imageUsername_, host_config.imagePassword_,cmd)
                if zsha_status.find('3 osds: 3 up, 3 in') <= 0:
                    continue
                if zsha_status.count('alive') < 3:
                    continue
                if zsha_status.count(': ceph') < 3:
                    continue
                if zsha_status.count(': running') < 1:
                    continue
                if zsha_status.count('3 mons at') < 1:
                    continue
                return True
    
            except:
                continue
        time.sleep(10)
    return False

def check_vm_running_exist_on_host(vm_uuid, host_ip, scenarioConfig, scenarioFile):
    mn_host_list = get_mn_host(scenarioConfig, scenarioFile)
    cmd = "virsh list|grep %s|awk '{print $3}'" %(vm_uuid)
    host = mn_host_list[0]
    host_config = sce_ops.get_scenario_config_vm(host.name_, scenarioConfig)
    vm_is_exist = True if test_lib.lib_execute_ssh_cmd(host_ip, host_config.imageUsername_, host_config.imagePassword_,cmd) else False

    return vm_is_exist

def stop_host(host_vm, scenarioConfig, force=None):
    host_vm_uuid = host_vm.uuid_
    mn_ip = scenarioConfig.basicConfig.zstackManagementIp.text_
    try:
        host_inv = sce_ops.stop_vm(mn_ip, host_vm_uuid,force=force)
        return host_inv
    except:
        test_util.test_logger("Fail to stop host [%s]" % host_vm.ip_)
        return False

def start_host(host_vm, scenarioConfig):
    host_vm_uuid = host_vm.uuid_
    mn_ip = scenarioConfig.basicConfig.zstackManagementIp.text_
    try:
        host_inv = sce_ops.start_vm(mn_ip, host_vm_uuid)
        return host_inv
    except:
        test_util.test_logger("Fail to start host [%s]" % host_vm.ip_)
        return False

def recover_host(host_vm, scenarioConfig, deploy_config):
    stop_host(host_vm, scenarioConfig)
    host_inv = start_host(host_vm, scenarioConfig)
    if not host_inv:
       return False
    host_ip = host_vm.ip_
    test_lib.lib_wait_target_up(host_ip, '22', 120)
    host_config = sce_ops.get_scenario_config_vm(host_inv.name,scenarioConfig)
    for l3network in xmlobject.safe_list(host_config.l3Networks.l3Network):
        if hasattr(l3network, 'l2NetworkRef'):
            for l2networkref in xmlobject.safe_list(l3network.l2NetworkRef):
                nic_name = sce_ops.get_ref_l2_nic_name(l2networkref.text_, deploy_config)
                if nic_name.find('.') >= 0 :
                    vlan = nic_name.split('.')[1]
                    test_util.test_logger('[vm:] %s %s is created.' % (host_ip, nic_name.replace("eth","zsn")))
                    cmd = 'vconfig add %s %s' % (nic_name.split('.')[0].replace("eth","zsn"), vlan)
                    test_lib.lib_execute_ssh_cmd(host_ip, host_config.imageUsername_, host_config.imagePassword_, cmd)
    return True

def destroy_mn_vm(mn_host, scenarioConfig):
    cmd = "virsh destroy \"ZStack Management Node VM\""
    host_config = sce_ops.get_scenario_config_vm(mn_host.name_, scenarioConfig)
    test_lib.lib_execute_ssh_cmd(mn_host.ip_, host_config.imageUsername_, host_config.imagePassword_, cmd)

def start_consul(mn_host, scenarioConfig):
    cmd = "systemctl start consul.service"
    host_config = sce_ops.get_scenario_config_vm(mn_host.name_, scenarioConfig)
    test_lib.lib_execute_ssh_cmd(mn_host.ip_, host_config.imageUsername_, host_config.imagePassword_, cmd)

def stop_consul(mn_host, scenarioConfig):
    cmd = "systemctl stop consul.service"
    host_config = sce_ops.get_scenario_config_vm(mn_host.name_, scenarioConfig)
    test_lib.lib_execute_ssh_cmd(mn_host.ip_, host_config.imageUsername_, host_config.imagePassword_, cmd)

def stop_zsha(mn_host, scenarioConfig):
    cmd = "zsha stop"       
    host_config = sce_ops.get_scenario_config_vm(mn_host.name_, scenarioConfig)
    test_lib.lib_execute_ssh_cmd(mn_host.ip_, host_config.imageUsername_, host_config.imagePassword_, cmd)

def start_zsha(mn_host, scenarioConfig):
    cmd = "zsha start"
    host_config = sce_ops.get_scenario_config_vm(mn_host.name_, scenarioConfig)
    test_lib.lib_execute_ssh_cmd(mn_host.ip_, host_config.imageUsername_, host_config.imagePassword_, cmd)

def get_host_by_consul_leader(scenarioConfig, scenarioFile):
    mn_host_list = get_mn_host(scenarioConfig, scenarioFile)
    if len(mn_host_list) < 1:
        return []
    host_list = []
    for i in range(5):
        for host in mn_host_list:
            host_config = sce_ops.get_scenario_config_vm(host.name_, scenarioConfig)
            cmd = "consul info |grep -i leader_addr | awk '{print $3}' | awk -F ':' '{print $1}'"
            host_ip = test_lib.lib_execute_ssh_cmd(host.ip_, host_config.imageUsername_, host_config.imagePassword_,cmd)
            if host_ip != "" and host_ip != False and host_ip.count('.') == 3:
                return host_ip.strip()
            else:
                test_util.test_logger("@@@host.ip_: %s exception when execute consul info" %(host.ip_))
        time.sleep(1)

    return ""

def get_host_by_mn_vm_consul(scenarioConfig, scenarioFile):
    mn_host_list = get_mn_host(scenarioConfig, scenarioFile)
    if len(mn_host_list) < 1:
        return []
    host_list = []
    for host in mn_host_list:
        host_config = sce_ops.get_scenario_config_vm(host.name_, scenarioConfig)
        cmd = "consul kv get z/last_start_vm_output | awk -F '[' '{print $2}' | awk -F ']' '{print $1}'"
        try:
            host_ip = test_lib.lib_execute_ssh_cmd(host.ip_, host_config.imageUsername_, host_config.imagePassword_,cmd)
        except:
            continue
        if host_ip != "" and host_ip != False:
            return host_ip.strip()
    return ""

def get_host_by_mn_vm_process(scenarioConfig, scenarioFile):
    zstack_management_ip = scenarioConfig.basicConfig.zstackManagementIp.text_

    mn_host_list = get_mn_host(scenarioConfig, scenarioFile)
    if len(mn_host_list) < 1:
        return []
    host_vm_inv = dict()
    host_inv = dict()
    for host in mn_host_list:
        cond = res_ops.gen_query_conditions('vmNics.ip', '=', host.ip_)
        host_vm_inv[host] = sce_ops.query_resource(zstack_management_ip, res_ops.VM_INSTANCE, cond).inventories[0]
        cond = res_ops.gen_query_conditions('uuid', '=', host_vm_inv[host].hostUuid)
        host_inv[host] = sce_ops.query_resource(zstack_management_ip, res_ops.HOST, cond).inventories[0]

    host_list = []
    for host in mn_host_list:
        cmd = "ps axjf |grep kvm | grep mnvm.img | grep -v grep"
        try:
            query_kvm_process = sce_ops.execute_in_vm_console(zstack_management_ip, host_inv[host].managementIp, host_vm_inv[host].uuid, host, cmd)
            test_util.test_logger("check mn vm kvm process on host %s: %s" % (host.ip_, query_kvm_process))
            if query_kvm_process.find('zstack/mnvm.img') >= 0:
                host_list.append(host)
        except:
            continue
    return host_list

def get_host_by_mn_vm_console(scenarioConfig, scenarioFile):
    zstack_management_ip = scenarioConfig.basicConfig.zstackManagementIp.text_

    mn_host_list = get_mn_host(scenarioConfig, scenarioFile)
    if len(mn_host_list) < 1:
        return []
    host_vm_inv = dict()
    host_inv = dict()
    for host in mn_host_list:
        cond = res_ops.gen_query_conditions('vmNics.ip', '=', host.ip_)
        host_vm_inv[host] = sce_ops.query_resource(zstack_management_ip, res_ops.VM_INSTANCE, cond).inventories[0]
        cond = res_ops.gen_query_conditions('uuid', '=', host_vm_inv[host].hostUuid)
        host_inv[host] = sce_ops.query_resource(zstack_management_ip, res_ops.HOST, cond).inventories[0]

    host_list = []
    for host in mn_host_list:
        cmd = "virsh list | grep -v paused | grep \"ZStack Management Node VM\""
        try:
            query_kvm_process = sce_ops.execute_in_vm_console(zstack_management_ip, host_inv[host].managementIp, host_vm_inv[host].uuid, host, cmd)
            test_util.test_logger("check mn vm on host %s: %s" % (host.ip_, query_kvm_process))
            if query_kvm_process.find('running') >= 0:
                host_list.append(host)
        except:
            continue
    return host_list

def get_host_by_mn_vm(scenarioConfig, scenarioFile):
    mn_host_list = get_mn_host(scenarioConfig, scenarioFile)
    if len(mn_host_list) < 1:
        return []
    test_util.test_logger("@@DEBUG@@: mn_host_list=<%s>" %(str(mn_host_list)))
    host_list = []
    for host in mn_host_list:
        host_config = sce_ops.get_scenario_config_vm(host.name_, scenarioConfig)
        cmd = "virsh list | grep -v paused | grep \"ZStack Management Node VM\""
        try:
            if sce_is_sep_pub():
                vm_list = test_lib.lib_execute_ssh_cmd(host.managementIp_, host_config.imageUsername_, host_config.imagePassword_,cmd)
            else:
                vm_list = test_lib.lib_execute_ssh_cmd(host.ip_, host_config.imageUsername_, host_config.imagePassword_,cmd)
            if vm_list:
                host_list.append(host)
        except Exception, e:
            test_util.test_logger("@@get host exception@@:%s" %(str(e)))
            continue

    test_util.test_logger("@@DEBUG@@: host_list=<%s>" %(str(host_list)))
    return host_list

def get_mn_host(scenarioConfig, scenarioFile):
    mn_host_list = []

    test_util.test_logger("@@DEBUG@@:<scenarioConfig:%s><scenarioFile:%s><scenarioFile is existed: %s>" \
                          %(str(scenarioConfig), str(scenarioFile), str(os.path.exists(scenarioFile))))
    if scenarioConfig == None or scenarioFile == None or not os.path.exists(scenarioFile):
        return mn_host_list

    test_util.test_logger("@@DEBUG@@: after config file exist check")
    for host in xmlobject.safe_list(scenarioConfig.deployerConfig.hosts.host):
        for vm in xmlobject.safe_list(host.vms.vm):
            if xmlobject.has_element(vm, 'mnHostRef'):
                with open(scenarioFile, 'r') as fd:
                    xmlstr = fd.read()
                    fd.close()
                    scenario_file = xmlobject.loads(xmlstr)
                    for s_vm in xmlobject.safe_list(scenario_file.vms.vm):
                        if s_vm.name_ == vm.name_:
                            mn_host_list.append(s_vm)
    test_util.test_logger("@@DEBUG@@: %s" %(str(mn_host_list)))
    return mn_host_list

def get_host_by_index_in_scenario_file(scenarioConfig, scenarioFile, index):
    test_util.test_logger("@@DEBUG@@:<scenarioConfig:%s><scenarioFile:%s><scenarioFile is existed: %s>" \
                          %(str(scenarioConfig), str(scenarioFile), str(os.path.exists(scenarioFile))))
    if scenarioConfig == None or scenarioFile == None or not os.path.exists(scenarioFile):
        return mn_host_list

    test_util.test_logger("@@DEBUG@@: after config file exist check")
    with open(scenarioFile, 'r') as fd:
        xmlstr = fd.read()
        fd.close()
        scenario_file = xmlobject.loads(xmlstr)
        return xmlobject.safe_list(scenario_file.vms.vm)[index]

def migrate_mn_vm(origin_host, target_host, scenarioConfig):

    host_config = sce_ops.get_scenario_config_vm(origin_host.name_, scenarioConfig)
    set_migration_speed_cmd = "virsh migrate-setspeed 'ZStack Management Node VM' 100"
    if not test_lib.lib_execute_ssh_cmd(origin_host.managementIp_, host_config.imageUsername_, host_config.imagePassword_, set_migration_speed_cmd, 30):
        test_util.test_fail("failed to set speed on original host:<%s>" %(origin_host.managementIp_))

    if test_lib.lib_cur_cfg_is_a_and_b(["test-config-vyos-flat-dhcp-nfs-sep-pub-man.xml"], ["scenario-config-nfs-sep-pub.xml"]) or \
       test_lib.lib_cur_cfg_is_a_and_b(["test-config-vyos-ceph-3-nets-sep.xml"], ["scenario-config-ceph-sep-pub.xml"]):
        cmd = 'zsha migrate %s' % (target_host.managementIp_)
        if not test_lib.lib_execute_ssh_cmd(origin_host.managementIp_, host_config.imageUsername_, host_config.imagePassword_,cmd, 120):
            test_util.test_fail("failed to run %s, maybe timeout refer to before log." %(cmd))
    else:
        cmd = 'zsha migrate %s' % (target_host.ip_)
        if not test_lib.lib_execute_ssh_cmd(origin_host.ip_, host_config.imageUsername_, host_config.imagePassword_,cmd, 120):
            test_util.test_fail("failed to run %s, maybe timeout refer to before log." %(cmd))


def upgrade_zsha(scenarioConfig, scenarioFile):
    host_list = get_mn_host(scenarioConfig, scenarioFile)
    test_host = host_list[0]
    test_host_ip = test_host.ip_
    zsha_path = "/home/%s/zs-ha" % test_host_ip
    config_path = "/home/%s/config.json" % test_host_ip
    current_zsha_path = "/tmp/zstack-ha-installer/zsha"
    check_cmd = "ls -l %s" % current_zsha_path
    host_config = sce_ops.get_scenario_config_vm(test_host.name_, scenarioConfig)
    former_time = []
    for host in host_list:
        former_zsha = test_lib.lib_execute_ssh_cmd(host.ip_, host_config.imageUsername_, host_config.imagePassword_, check_cmd)
        former_time.append(former_zsha.split()[7])
    upgrade_zsha_cmd = "%s install -p %s -c %s" % (zsha_path, host_config.imagePassword_, config_path)
    test_lib.lib_execute_ssh_cmd(test_host_ip, host_config.imageUsername_, host_config.imagePassword_, upgrade_zsha_cmd)
    current_time = []
    for host in host_list:
        current_zsha = test_lib.lib_execute_ssh_cmd(host.ip_, host_config.imageUsername_, host_config.imagePassword_, check_cmd)
        current_time.append(current_zsha.split()[7])
    for i in range(len(former_time)):
        if current_time[i] == former_time[i]:
            return False
    return True

def update_mn_vm_config(mn_vm_host, option, content, scenarioConfig, new_config = "/tmp/zstack-ha-installer/config.json"):
    cmd1 = 'sed -i "s/\\\"%s\\\": \\\".*\\\"/\\\"%s\\\": \\\"%s\\\"/g" %s' % (option, option, content, new_config)
    cmd2 = "zsha import-config %s" % new_config
    host_config = sce_ops.get_scenario_config_vm(mn_vm_host.name_, scenarioConfig)
    test_lib.lib_execute_ssh_cmd(mn_vm_host.ip_, host_config.imageUsername_, host_config.imagePassword_, cmd1)
    test_lib.lib_execute_ssh_cmd(mn_vm_host.ip_, host_config.imageUsername_, host_config.imagePassword_, cmd2)

def adapt_pick_ip_not_used_in_scenario_file(scenarioFile, prefix="10.0.0.", pick_range=range(2,255,1)):
    ips = sce_ops.dump_scenario_file_ips(scenarioFile)
    for var in pick_range:
        combined_ip = prefix + str(var)
        if combined_ip not in ips:
            return combined_ip

def pick_randomized_ip(prefix="192.168.254."):
    import random
    var = random.randrange(2, 254, 1)
    combined_ip = prefix + str(var)
    return combined_ip

def get_ceph_mon_addr(ceph_mon_ip):
    cmd = r"ceph mon stat|grep -o '\([0-9]\{1,3\}\.\)\{3\}[0-9]\{1,3\}:6789'"
    ret, output, stderr = ssh.execute(cmd, ceph_mon_ip, "root", "password", False, 22)
    return r"\"MonAddrs\": " + str(output.strip('\n').split('\n')) + ','

def prepare_config_json(scenarioConfig, scenarioFile, deploy_config, config_json):
    mn_host_list = get_mn_host(scenarioConfig, scenarioFile)
    if len(mn_host_list) < 1:
        return False
    #l2network_name = os.environ.get('l2PublicNetworkName')
    #nic_name = os.environ.get('nodeNic').replace("eth", "zsn")
    for i in range(len(mn_host_list)):
        if test_lib.lib_cur_cfg_is_a_and_b(["test-config-vyos-fusionstor-3-nets-sep.xml"], ["scenario-config-fusionstor-3-nets-sep.xml"]):
            os.system('sed -i s/host-%d/%s/g %s' % (i+1, mn_host_list[i].storageIp_,config_json))
        elif test_lib.lib_cur_cfg_is_a_and_b(["test-config-vyos-flat-dhcp-nfs-sep-pub-man.xml"], ["scenario-config-nfs-sep-man.xml"]) or \
                         test_lib.lib_cur_cfg_is_a_and_b(["test-config-vyos-nonmon-ceph.xml"], ["scenario-config-storage-separate-ceph.xml"]) or \
                         test_lib.lib_cur_cfg_is_a_and_b(["test-config-vyos-ceph-3-nets-sep.xml"], ["scenario-config-ceph-sep-man.xml"]):
            os.system('sed -i s/host-%d/%s/g %s' % (i+1, mn_host_list[i].ip_,config_json))
        else:
            os.system('sed -i s/host-%d/%s/g %s' % (i+1, mn_host_list[i].managementIp_,config_json))

    os.system('sed -i s/nic/%s/g %s' % ("zsn", config_json))
    if os.path.basename(os.environ.get('WOODPECKER_SCENARIO_CONFIG_FILE')).strip() == "scenario-config-vpc-ceph-3-sites.xml":
        host_ips = sce_ops.dump_scenario_file_ips(scenarioFile)
        mn_ip = ""
        mn_gateway = ""
        mn_netmask = ""
        for host_ip in host_ips:
            cmd = "hostname"
            ret, hostname, stderr = ssh.execute(cmd, host_ip, "root", "password", True, 22)
            host_ip_new_lst = host_ip.split('.')
            host_ip_new_lst[3] = '200'
            mn_ip_new = '.'.join(host_ip_new_lst)
            mn_ip = mn_ip + mn_ip_new + '@' + hostname + ', '
            host_ip_new_lst[3] = '1'
            mn_gateway_new = '.'.join(host_ip_new_lst)
            mn_gateway = mn_gateway + mn_gateway_new + '@' + hostname + ', '
            mn_netmask_new = "255.255.255.0"
            mn_netmask = mn_netmask + mn_netmask_new + '@' + hostname + ', '
        mn_ip = mn_ip.strip().strip(',').replace('\n', '')
        mn_netmask = mn_netmask.strip().strip(',').replace('\n', '')
        mn_gateway = mn_gateway.strip().strip(',').replace('\n', '')
        test_util.test_logger("mn_ip=:%s:; mn_netmask=:%s:; mn_gateway=:%s:" %(mn_ip, mn_netmask, mn_gateway))
        os.system('sed -i "s/mn_ip/%s/g" %s' % (mn_ip,config_json))
        os.system('sed -i "s/mn_netmask/%s/g" %s' % (mn_netmask,config_json))
        os.system('sed -i "s/mn_gateway/%s/g" %s' % (mn_gateway,config_json))
    else:
        mn_ip = os.environ.get('zstackHaVip')
        mn_netmask = os.environ.get('nodeNetMask')
        mn_gateway = os.environ.get('nodeGateway')
        os.system('sed -i "s/mn_ip/%s/g" %s' % (mn_ip,config_json))
        os.system('sed -i "s/mn_netmask/%s/g" %s' % (mn_netmask,config_json))
        os.system('sed -i "s/mn_gateway/%s/g" %s' % (mn_gateway,config_json))

    mn_ha_storage_type = sce_ops.get_mn_ha_storage_type(scenarioConfig, scenarioFile, deploy_config)
    if mn_ha_storage_type == 'ceph':
        os.system('sed -i s/FileConf/CephConf/g %s' % (config_json))
    elif mn_ha_storage_type == 'fusionstor':
        os.system('sed -i s/FileConf/FstrConf/g %s' % (config_json))
    elif mn_ha_storage_type == 'nfs':
        #stor_vm_ip = "10.0.0.2"
        #stor_vm_ip = adapt_pick_ip_not_used_in_scenario_file(scenarioFile)
        stor_vm_ip = os.environ.get('zstackHaVip3')
        stor_vm_netmask = os.environ.get('storNetMask')
        stor_vm_gateway = os.environ.get('storGateway')
        os.system('sed -i s/stor_ip1/%s/g %s' % (stor_vm_ip,config_json))
        os.system('sed -i s/stor_netmask1/%s/g %s' % (stor_vm_netmask,config_json))
        os.system('sed -i s/stor_gateway1/%s/g %s' % (stor_vm_gateway,config_json))

    #man_vm_ip = pick_randomized_ip()
    man_vm_ip = os.environ.get('zstackHaVip2')
    man_vm_netmask = os.environ.get('manNetMask')
    man_vm_gateway = os.environ.get('manGateway')
    os.system('sed -i s/man_ip1/%s/g %s' % (man_vm_ip,config_json))
    os.system('sed -i s/man_netmask1/%s/g %s' % (man_vm_netmask,config_json))
    os.system('sed -i s/man_gateway1/%s/g %s' % (man_vm_gateway,config_json))

    if test_lib.lib_cur_cfg_is_a_and_b(["test-config-vyos-fusionstor-3-nets-sep.xml"], ["scenario-config-fusionstor-3-nets-sep.xml"]):
        #stor_vm_ip = adapt_pick_ip_not_used_in_scenario_file(scenarioFile)
        stor_vm_ip = os.environ.get('zstackHaVip3')
        stor_vm_netmask = os.environ.get('storNetMask')
        stor_vm_gateway = os.environ.get('storGateway')
        os.system('sed -i s/stor_ip1/%s/g %s' % (stor_vm_ip,config_json))
        os.system('sed -i s/stor_netmask1/%s/g %s' % (stor_vm_netmask,config_json))
        os.system('sed -i s/stor_gateway1/%s/g %s' % (stor_vm_gateway,config_json))
    elif test_lib.lib_cur_cfg_is_a_and_b(["test-config-vyos-nonmon-ceph.xml"], ["scenario-config-storage-separate-ceph.xml"]):
        ceph_mon_ip = get_host_by_index_in_scenario_file(scenarioConfig, scenarioFile, 0).ip_
        os.system("sed -i '/MonAddrs/d' %s" % (config_json))
        os.system("sed -i /Type/a\ \"%s\" %s" % (get_ceph_mon_addr(ceph_mon_ip).replace("'", '\\\"'), config_json))
        os.system("sed -i 's:\"MonAddrs:  \"MonAddrs:g' %s" % (config_json))
        stor_vm_ip = os.environ.get('zstackHaVip3')
        stor_vm_netmask = os.environ.get('storNetMask')
        stor_vm_gateway = os.environ.get('storGateway')
        os.system('sed -i s/stor_ip1/%s/g %s' % (stor_vm_ip,config_json))
        os.system('sed -i s/stor_netmask1/%s/g %s' % (stor_vm_netmask,config_json))
        os.system('sed -i s/stor_gateway1/%s/g %s' % (stor_vm_gateway,config_json))

def prepare_etc_hosts(scenarioConfig, scenarioFile, deploy_config, config_json):
    mn_host_list = get_mn_host(scenarioConfig, scenarioFile)
    if len(mn_host_list) < 1:
        return False

    for i in range(len(mn_host_list)):
        os.system('echo %s %s >> /etc/hosts' % (mn_host_list[i].ip_, mn_host_list[i].ip_.replace('.', '-')))

    for i in range(len(mn_host_list)):
        test_host_config = sce_ops.get_scenario_config_vm(mn_host_list[i].name_, scenarioConfig)
        ssh.scp_file('/etc/hosts', '/etc/hosts', mn_host_list[i].ip_, test_host_config.imageUsername_, test_host_config.imagePassword_)


def deploy_ha_env(scenarioConfig, scenarioFile, deploy_config, config_json, deploy_tool, mn_img):
    prepare_config_json(scenarioConfig, scenarioFile, deploy_config, config_json)
    mn_ha_storage_type = sce_ops.get_mn_ha_storage_type(scenarioConfig, scenarioFile, deploy_config)
    if test_lib.lib_cur_cfg_is_a_and_b(["test-config-vyos-nonmon-ceph.xml"], ["scenario-config-storage-separate-ceph.xml"]):
        pass
    elif mn_ha_storage_type == 'ceph':
        os.system('sed -i s/node/ceph-/g %s' %(config_json))
    test_host = get_mn_host(scenarioConfig,scenarioFile)[0]
    test_host_ip = test_host.ip_
    test_host_config = sce_ops.get_scenario_config_vm(test_host.name_, scenarioConfig)
    host_password = test_host_config.imagePassword_
    mn_image_path = "/home/%s/mn.qcow2" % test_host_ip
    installer_path = "/home/%s/zs-ha" % test_host_ip
    config_path = "/home/%s/config.json" % test_host_ip
    ssh.scp_file(config_json, config_path, test_host_ip, test_host_config.imageUsername_, test_host_config.imagePassword_)
    ssh.scp_file(mn_img, mn_image_path, test_host_ip, test_host_config.imageUsername_, test_host_config.imagePassword_)
    ssh.scp_file(deploy_tool, installer_path, test_host_ip, test_host_config.imageUsername_, test_host_config.imagePassword_)

    cmd0 = "chmod a+x %s" % (installer_path)
    test_util.test_logger("[%s] %s" % (test_host_ip, cmd0))
    ssh.execute(cmd0, test_host_ip, test_host_config.imageUsername_, test_host_config.imagePassword_, True, 22)

    if mn_ha_storage_type == 'ceph':

        if test_lib.lib_cur_cfg_is_a_and_b(["test-config-vyos-nonmon-ceph.xml"], ["scenario-config-storage-separate-ceph.xml"]):
            ceph_node_ip = get_host_by_index_in_scenario_file(scenarioConfig, scenarioFile, 0).ip_ 
            mn_image_path = "/home/%s/mn.qcow2" % ceph_node_ip
            ssh.scp_file(mn_img, mn_image_path, ceph_node_ip, test_host_config.imageUsername_, test_host_config.imagePassword_)
            woodpecker_vm_ip = shell.call("ip r | grep src | head -1 | awk '{print $NF}'").strip()
            qemu_kvm_repo_path = "/home/%s/qemu-kvm-ev.repo" % woodpecker_vm_ip
            ssh.scp_file(qemu_kvm_repo_path, "/etc/yum.repos.d/qemu-kvm-ev.repo", ceph_node_ip, test_host_config.imageUsername_, test_host_config.imagePassword_)
            cmd0="yum install -y --disablerepo=* --enablerepo=zstack-local,qemu-kvm-ev qemu-img"
            test_util.test_logger("[%s] %s" % (ceph_node_ip, cmd0))
            ssh.execute(cmd0, ceph_node_ip, test_host_config.imageUsername_, test_host_config.imagePassword_, True, 22)
            os.system("sshpass -p %s scp -r %s@%s:/etc/ceph /tmp/" %(test_host_config.imagePassword_, test_host_config.imageUsername_, ceph_node_ip))
            for i in xrange(1,4,1):
                mn_node_ip = get_host_by_index_in_scenario_file(scenarioConfig, scenarioFile, i).ip_ 
                cmd0="yum repolist all|grep ceph-hammer"
                ret, stdout, stderr = ssh.execute(cmd0, mn_node_ip, "root", "password", False, 22)
                test_util.test_logger("ret=%s" % (ret))
                if str(ret) == "0":
                    yum_cmd = "yum --disablerepo=* --enablerepo=zstack-local,ceph-hammer -y install ceph >/dev/null 2>&1"
                else:
                    yum_cmd = "yum --disablerepo=* --enablerepo=zstack-local,ceph -y install ceph >/dev/null 2>&1"

                test_util.test_logger("[%s] %s" % (mn_node_ip, yum_cmd))
                ssh.execute(yum_cmd, mn_node_ip, test_host_config.imageUsername_, test_host_config.imagePassword_, True, 22)
                os.system("sshpass -p %s scp -r /tmp/ceph %s@%s:/etc/" %(test_host_config.imagePassword_, test_host_config.imageUsername_, mn_node_ip))
        else:
            ceph_node_ip = test_host_ip

        cmd1="ceph osd pool create zstack 128"
        test_util.test_logger("[%s] %s" % (ceph_node_ip, cmd1))
        ssh.execute(cmd1, ceph_node_ip, test_host_config.imageUsername_, test_host_config.imagePassword_, True, 22)

        cmd2="qemu-img convert -f qcow2 -O raw %s rbd:zstack/mnvm.img" % mn_image_path
        test_util.test_logger("[%s] %s" % (ceph_node_ip, cmd2))
        if test_lib.lib_execute_ssh_cmd(ceph_node_ip, test_host_config.imageUsername_, test_host_config.imagePassword_, cmd2, timeout=7200 ) == False:
            test_util.test_fail("fail to run cmd: %s on %s" %(cmd2, ceph_node_ip))

    elif mn_ha_storage_type == 'nfs':
        prepare_etc_hosts(scenarioConfig, scenarioFile, deploy_config, config_json)
        #cmd1 = "cp %s /storage/mnvm.img" % (mn_image_path)
        #test_util.test_logger("[%s] %s" % (test_host_ip, cmd1))
        #ssh.execute(cmd1, test_host_ip, test_host_config.imageUsername_, test_host_config.imagePassword_, True, 22)
        if test_lib.lib_cur_cfg_is_a_and_b(["test-config-vyos-flat-dhcp-nfs-sep-pub-man.xml", "test-config-vyos-flat-dhcp-nfs-mul-net-pubs.xml"], \
                                                 ["scenario-config-nfs-sep-pub.xml"]):
            nfs_url = sce_ops.get_mn_ha_nfs_url(scenarioConfig, scenarioFile, deploy_config, False)
        else:
            nfs_url = sce_ops.get_mn_ha_nfs_url(scenarioConfig, scenarioFile, deploy_config)

        nfsIP = nfs_url.split(':')[0]
        nfsPath = nfs_url.split(':')[1]

        qcow2_nfs_path = "%s/mnvm.qcow2" %(nfsPath)
        raw_nfs_path = "%s/mnvm.img" %(nfsPath)
        #mn_image_nfs_server_path = "/home/%s/mn.qcow2" % nfsIP
        woodpecker_vm_ip = shell.call("ip r | grep src | head -1 | awk '{print $NF}'").strip()
        #mn_image_nfs_server_path = "/home/%s/mn.qcow2" % test_host_ip
        mn_image_nfs_server_path = "/home/%s/mn.qcow2" % woodpecker_vm_ip
        test_util.test_logger("scp from %s to %s:%s" % (mn_image_nfs_server_path, nfsIP, qcow2_nfs_path))
        ssh.scp_file(mn_image_nfs_server_path, qcow2_nfs_path, nfsIP, test_host_config.imageUsername_, test_host_config.imagePassword_)

        if test_lib.lib_cur_cfg_is_a_and_b(["test-config-vyos-flat-dhcp-nfs-sep-pub-man.xml", "test-config-vyos-flat-dhcp-nfs-mul-net-pubs.xml"], \
                                                 ["scenario-config-nfs-sep-pub.xml"]):
            cmd1 = "mv /storage/mnvm.qcow2 /storage/mnvm.img"
            test_util.test_logger("[%s] %s" % (test_host_ip, cmd1))
            ssh.execute(cmd1, test_host_ip, test_host_config.imageUsername_, test_host_config.imagePassword_, True, 22)
        else:
            woodpecker_vm_ip = shell.call("ip r | grep src | head -1 | awk '{print $NF}'").strip()
            qemu_kvm_repo_path = "/home/%s/qemu-kvm-ev.repo" % woodpecker_vm_ip
            ssh.scp_file(qemu_kvm_repo_path, "/etc/yum.repos.d/qemu-kvm-ev.repo", test_host_ip, test_host_config.imageUsername_, test_host_config.imagePassword_)
            cmd1="yum install -y --disablerepo=* --enablerepo=zstack-local,qemu-kvm-ev qemu-img"

            #cmd1 = r"yum install -y qemu-img --disablerepo=* --enablerepo=zstack-local"
            test_util.test_logger("[%s] %s" % (test_host_ip, cmd1))
            ssh.execute(cmd1, test_host_ip, test_host_config.imageUsername_, test_host_config.imagePassword_, True, 22)

            #cmd1 = "qemu-img convert -p -f qcow2 -O raw %s %s" % (qcow2_nfs_path, raw_nfs_path)
            #test_util.test_logger("[%s] %s" % (nfsIP, cmd1))
            #ssh.execute(cmd1, nfsIP, test_host_config.imageUsername_, test_host_config.imagePassword_, True, 22)
            cmd1 = "qemu-img convert -p -f qcow2 -O raw /storage/mnvm.qcow2 /storage/mnvm.img"
            test_util.test_logger("[%s] %s" % (test_host_ip, cmd1))
            ssh.execute(cmd1, test_host_ip, test_host_config.imageUsername_, test_host_config.imagePassword_, True, 22)

    elif mn_ha_storage_type == 'fusionstor':
        cmd1 = "lichbd pool create zstack -p nbd"
        test_util.test_logger("[%s] %s" % (test_host_ip, cmd1))
        ssh.execute(cmd1, test_host_ip, test_host_config.imageUsername_, test_host_config.imagePassword_, True, 22)
        cmd2 = "lichbd vol import %s zstack/mnvm.img -p nbd" %(mn_image_path)
        test_util.test_logger("[%s] %s" % (test_host_ip, cmd2))
        ssh.execute(cmd2, test_host_ip, test_host_config.imageUsername_, test_host_config.imagePassword_, True, 22)
        cmd3 = "lich.inspect --localize /default/zstack/mnvm.img 0"
        test_util.test_logger("[%s] %s" % (test_host_ip, cmd3))
        ssh.execute(cmd3, test_host_ip, test_host_config.imageUsername_, test_host_config.imagePassword_, True, 22)

    cmd3='%s install -p %s -c %s' % (installer_path, host_password, config_path)
    test_util.test_logger("[%s] %s" % (test_host_ip, cmd3))

    #ssh.execute(cmd3, test_host_ip, test_host_config.imageUsername_, test_host_config.imagePassword_, True, 22)

    ret, output, stderr = ssh.execute(cmd3, test_host_ip, test_host_config.imageUsername_, test_host_config.imagePassword_, False, 22)
    test_util.test_logger("cmd=%s; ret=%s; output=%s; stderr=%s" %(cmd3, ret, output, stderr))

    if str(ret)=="0":
        return

    allow_retry_times = 5
    while allow_retry_times > 0 and "please retry or check log" in output:
        time.sleep(5)
        ret, output, stderr = ssh.execute(cmd3, test_host_ip, test_host_config.imageUsername_, test_host_config.imagePassword_, False, 22)
        if ret==0:
            test_util.test_logger("zsha install successfully, jump out retry.")
            return
        else:
            test_util.test_logger("retry_times=%s; cmd=%s; ret=%s; output=%s; stderr=%s" %(allow_retry_times, cmd3, ret, output, stderr))
        allow_retry_times = allow_retry_times - 1

    if str(ret)!="0":
        test_util.test_fail("fail to run cmd: %s on %s" %(cmd3, test_host_ip))

    #if test_lib.lib_execute_ssh_cmd(test_host_ip, test_host_config.imageUsername_, test_host_config.imagePassword_, cmd3, timeout=3600 ) == False:
    #    test_util.test_fail("fail to run cmd: %s on %s" %(cmd3, test_host_ip))


l2network_nic = None
def shutdown_host_network(host_vm, scenarioConfig, downMagt=True):
    '''
        Here we change l2network_nic to be global is due to the maybe failed once all mn nodes disconnected
        In that case, lib_get_l2_magt_nic_by_vr_offering will be failed because of mn is disconnected.
        Of course, to be global means the management network can be only selected once in ZStack DB.
    '''
    global l2network_nic
    zstack_management_ip = scenarioConfig.basicConfig.zstackManagementIp.text_
    cond = res_ops.gen_query_conditions('vmNics.ip', '=', host_vm.ip_)
    host_vm_inv = sce_ops.query_resource(zstack_management_ip, res_ops.VM_INSTANCE, cond).inventories[0]
    cond = res_ops.gen_query_conditions('uuid', '=', host_vm_inv.hostUuid)
    host_inv = sce_ops.query_resource(zstack_management_ip, res_ops.HOST, cond).inventories[0]

    host_vm_config = sce_ops.get_scenario_config_vm(host_vm_inv.name_, scenarioConfig)

    if not l2network_nic:
        if downMagt:
            l2network_nic = test_lib.lib_get_l2_magt_nic_by_vr_offering()
        else:
            l2network_nic = test_lib.lib_get_l2_pub_nic_by_vr_offering()

    if not l2network_nic:
        test_util.test_fail("fail to get management l2 by vr offering")
    #l2network_nic = os.environ.get('l2ManagementNetworkInterface').replace("eth", "zsn")
    cmd = "ifdown %s" % (l2network_nic)
    sce_ops.execute_in_vm_console(zstack_management_ip, host_inv.managementIp, host_vm_inv.uuid, host_vm_config, cmd)


def reopen_host_network(host_vm, scenarioConfig, param_l2_nic=""):
    '''
        This function can be only invoked after shutdown_host_network.
    '''
    global l2network_nic
    zstack_management_ip = scenarioConfig.basicConfig.zstackManagementIp.text_
    cond = res_ops.gen_query_conditions('vmNics.ip', '=', host_vm.ip_)
    host_vm_inv = sce_ops.query_resource(zstack_management_ip, res_ops.VM_INSTANCE, cond).inventories[0]
    cond = res_ops.gen_query_conditions('uuid', '=', host_vm_inv.hostUuid)
    host_inv = sce_ops.query_resource(zstack_management_ip, res_ops.HOST, cond).inventories[0]

    host_vm_config = sce_ops.get_scenario_config_vm(host_vm_inv.name_, scenarioConfig)
    if not l2network_nic and not param_l2_nic:
        test_util.test_fail("fail to get management l2 by vr offering")
    #l2network_nic = os.environ.get('l2ManagementNetworkInterface').replace("eth", "zsn")
    cmd = "ifup %s" % (l2network_nic)
    if param_l2_nic:
        cmd = "ifup %s" % (param_l2_nic)
    sce_ops.execute_in_vm_console(zstack_management_ip, host_inv.managementIp, host_vm_inv.uuid, host_vm_config, cmd)


def create_vm(l3_uuid_list, image_uuid, vm_name = None, \
              disk_offering_uuids = None, default_l3_uuid = None, \
              system_tags = None, instance_offering_uuid = None, session_uuid = None):
    vm_creation_option = test_util.VmOption() 
    conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
    if not instance_offering_uuid:     
        instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid
        vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_l3_uuids(l3_uuid_list)
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_name(vm_name)
    vm_creation_option.set_data_disk_uuids(disk_offering_uuids)
    vm_creation_option.set_default_l3_uuid(default_l3_uuid)
    vm_creation_option.set_system_tags(system_tags)
    vm_creation_option.set_session_uuid(session_uuid)
    vm = test_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    return vm

def create_basic_vm(disk_offering_uuids=None, session_uuid = None, wait_vr_running = True):
    image_name = os.environ.get('imageName_net')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    l3_name = os.environ.get('l3VlanNetworkName1')
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid

    if wait_vr_running:
        ensure_vr_is_running_connected(l3_net_uuid)

    return create_vm([l3_net_uuid], image_uuid, 'basic_no_vlan_vm', disk_offering_uuids, session_uuid = session_uuid)

def create_ha_vm(disk_offering_uuids=None, session_uuid = None):
    vm = create_basic_vm(disk_offering_uuids=disk_offering_uuids, session_uuid=session_uuid)
    ha_ops.set_vm_instance_ha_level(vm.get_vm().uuid, "NeverStop")
    return vm

def skip_if_vr_not_vyos(vr_image_name):
    cond = res_ops.gen_query_conditions('name', '=', vr_image_name)
    vr_urls_list = res_ops.query_resource_fields(res_ops.IMAGE, cond, None, ['url'])
    for vr_url in vr_urls_list:
        if "vrouter" in vr_url.url:
            test_util.test_logger("find vrouter image. Therefore, no need to skip")
            break
    else:
        test_util.test_skip("not found vrouter image based on image name judgement. Therefore, skip test")

def ensure_pss_connected():
    for i in range(300):
        #time.sleep(1)
        ps_list = res_ops.query_resource(res_ops.PRIMARY_STORAGE)
        for ps in ps_list:
            ps_ops.reconnect_primary_storage(ps.uuid)
            cond = res_ops.gen_query_conditions('uuid', '=', ps.uuid)
            pss = res_ops.query_resource_fields(res_ops.PRIMARY_STORAGE, cond, None)
            if not "connected" in pss[0].status.lower():
                test_util.test_logger("time %s found not connected ps status: %s" %(str(i), pss[0].status))
                break
        else:
            return
    else:
        test_util.test_fail("ps status didn't change to Connected within 300s, therefore, failed")

def ensure_bss_connected():
    for i in range(300):
        #time.sleep(1)
        bs_list = res_ops.query_resource(res_ops.BACKUP_STORAGE)
        for bs in bs_list:
            bs_ops.reconnect_backup_storage(bs.uuid)
            cond = res_ops.gen_query_conditions('uuid', '=', bs.uuid)
            bss = res_ops.query_resource_fields(res_ops.BACKUP_STORAGE, cond, None)
            if not "connected" in bss[0].status.lower():
                test_util.test_logger("times: %s found not connected ps status: %s" %(str(i), bss[0].status))
                break
        else:
            return
    else:
        test_util.test_fail("bs status didn't change to Connected within 300s, therefore, failed")

def ensure_hosts_connected(exclude_host=[]):
    for i in range(300):
        #time.sleep(1)
        host_list = res_ops.query_resource(res_ops.HOST)
        for exh in exclude_host:
            for host in host_list:
                if exh.managementIp_ == host.managementIp or exh.ip_ == host.managementIp:
                    host_list.remove(host)

        for host in host_list:
            try:
                host_ops.reconnect_host(host.uuid)
            except Exception, e:
                test_util.test_logger("time: %s reconnect host failed: %s" %(str(i), host.uuid))
                break
            cond = res_ops.gen_query_conditions('uuid', '=', host.uuid)
            hosts = res_ops.query_resource_fields(res_ops.HOST, cond, None)
            if not "connected" in hosts[0].status.lower():
                test_util.test_logger("time %s found not connected ps status: %s" %(str(i), hosts[0].status))
                break
        else:
            return
    else:
        test_util.test_fail("host status didn't change to Connected within 300s, therefore, failed")

def ensure_bss_host_connected_from_stop(scenarioFile, scenarioConfig, deploy_config):
    '''
        This function is only support for not separated network case
    '''
    bss_host_ip = []
    bs_list = res_ops.query_resource(res_ops.BACKUP_STORAGE)
    if bs_list[0].type == "SftpBackupStorage":
        for bs in bs_list:
            bss_host_ip.append(bs.hostname)

        for bs_host_ip in bss_host_ip:
            if test_lib.lib_wait_target_up(bs_host_ip, '22', 300):
                bss_host_ip.remove(bs_host_ip)

        mn_host_list = get_mn_host(scenarioConfig, scenarioFile)
        for bs_host_ip in bss_host_ip:
            for mn_host in mn_host_list:
                if mn_host.managementIp_ == bs_host_ip or mn_host.ip_ == bs_host_ip:
                    recover_host(mn_host, scenarioConfig, deploy_config)

        for bs_host_ip in bss_host_ip:
            if test_lib.lib_wait_target_up(bs_host_ip, '22', 300):
                bss_host_ip.remove(bs_host_ip)

        if bss_host_ip:
            test_util.test_fail("still have bs host not started.")
    else:
        test_util.test_logger("the current bs is %s type, is not expected sftp, therefore, skip ensure bss host connected" %(bs_list[0].type))


def ensure_bss_host_connected_from_sep_net_down(scenarioFile, scenarioConfig, downMagt=True):
    '''
        This function is only support for separated network case
    '''
    bss_host_ip = []
    bs_list = res_ops.query_resource(res_ops.BACKUP_STORAGE)
    if bs_list[0].type == "SftpBackupStorage":
        for bs in bs_list:
            bss_host_ip.append(bs.hostname)

        for bs_host_ip in bss_host_ip:
            if test_lib.lib_wait_target_up(bs_host_ip, '22', 300):
                bss_host_ip.remove(bs_host_ip)

        if downMagt:
            l2network_nic = test_lib.lib_get_l2_magt_nic_by_vr_offering()
        else:
            l2network_nic = test_lib.lib_get_l2_pub_nic_by_vr_offering()

        mn_host_list = get_mn_host(scenarioConfig, scenarioFile)
        for bs_host_ip in bss_host_ip:
            for mn_host in mn_host_list:
                if mn_host.managementIp_ == bs_host_ip or mn_host.ip_ == bs_host_ip:
                    reopen_host_network(mn_host, scenarioConfig, param_l2_nic=l2network_nic)

        for bs_host_ip in bss_host_ip:
            if test_lib.lib_wait_target_up(bs_host_ip, '22', 300):
                bss_host_ip.remove(bs_host_ip)

        if bss_host_ip:
            test_util.test_fail("still have bs host not started.")
    else:
        test_util.test_logger("the current bs is %s type, is not expected sftp, therefore, skip ensure bss host connected" %(bs_list[0].type))


def ensure_host_disconnected(test_host, wait_time):
    cond = res_ops.gen_query_conditions('managementIp', '=', test_host.managementIp_)
    for i in range(wait_time):
        time.sleep(1)
        host_list = res_ops.query_resource(res_ops.HOST, cond)
        if "disconnected" in host_list[0].status.lower():
            test_util.test_logger("successfully got host disconnected: %s" %(host_list[0].status))
            return

def ensure_vr_is_running_connected(l3_uuid):
    vr_list = test_lib.lib_find_vr_by_l3_uuid(l3_uuid)
    if not vr_list: return

    if vr_list[0].applianceVmType == "VirtualRouter":

        if vr_list[0].state == "Stopped":
            vm_ops.start_vm(vr_list[0].uuid)

    elif vr_list[0].applianceVmType == "vrouter":
        pass
    else:
        test_util.test_fail("current vr type not support in ensure_vr_is_connected.")

    cond = res_ops.gen_query_conditions('uuid', '=', vr_list[0].uuid)
    for i in range(300):
        time.sleep(1)
        vr1 = res_ops.query_resource(res_ops.VM_INSTANCE, cond)[0]
        if vr1.state == "Running" and vr1.status == "Connected":
            test_util.test_logger("vr has successfully changed to Running and Connected")
            break
    else:
        test_util.test_fail("vr has not been successfully changed to Running and Connected within 300s: state=%s:status=%s" %(vr1.state, vr1.status))

def skip_if_scenario_is_multiple_networks(mul_nets_sce_list=[]):

    if not mul_nets_sce_list:
        mul_nets_sce_list = [ 					\
                             'scenario-config-nfs-sep-man.xml',	\
                             'scenario-config-nfs-sep-pub.xml',	\
                             'scenario-config-ceph-sep-man.xml',	\
                             'scenario-config-ceph-sep-pub.xml'	\
                            ]

    for sce_cfg in mul_nets_sce_list:
        if sce_cfg in os.environ.get('WOODPECKER_SCENARIO_CONFIG_FILE'):
            test_util.test_skip("Skip the test because scenario config is %s"	\
                          %(os.environ.get('WOODPECKER_SCENARIO_CONFIG_FILE')))

def skip_if_scenario_not_multiple_networks(mul_nets_sce_list=[]):

    if not mul_nets_sce_list:
        mul_nets_sce_list = [ 					\
                             'scenario-config-nfs-sep-man.xml',	\
                             'scenario-config-nfs-sep-pub.xml',	\
                             'scenario-config-ceph-sep-man.xml',	\
                             'scenario-config-ceph-sep-pub.xml'	\
                            ]

    for sce_cfg in mul_nets_sce_list:
        if sce_cfg in os.environ.get('WOODPECKER_SCENARIO_CONFIG_FILE'):
            break
    else:
        test_util.test_skip("Skip the test because scenario config is not %s" \
                          %(os.environ.get('WOODPECKER_SCENARIO_CONFIG_FILE')))
        

def sce_is_sep_pub():
    sep_pub_sce_list = [ 					\
                             'scenario-config-nfs-sep-pub.xml',	\
                             'scenario-config-ceph-sep-pub.xml'	\
                       ]

    for sce_cfg in sep_pub_sce_list:
        if sce_cfg in os.environ.get('WOODPECKER_SCENARIO_CONFIG_FILE'):
            return True
    else:
        return False


def sce_is_sep_man():
    sep_man_sce_list = [ 					\
                             'scenario-config-nfs-sep-man.xml',	\
                             'scenario-config-ceph-sep-man.xml' \
                       ]

    for sce_cfg in sep_man_sce_list:
        if sce_cfg in os.environ.get('WOODPECKER_SCENARIO_CONFIG_FILE'):
            return True
    else:
        return False


def auto_set_mn_ip(scenario_file):
    import re
    host_ip_lst = sce_ops.dump_scenario_file_ips(scenario_file)
    host_ip = host_ip_lst[0]
    for i in range(60):
        time.sleep(10)
        #cmd = "zsha status|head -n 2|tail -n 1|cut -d: -f1"
        cmd = "zsha status|head -n 5|grep -v stale|grep running|tail -n 1|cut -d: -f1"
        test_util.test_logger("@@@DEBUG->cmd=<%s>;host_ip=<%s>" %(cmd, host_ip))
        ret, mn_host_ip, stderr = ssh.execute(cmd, host_ip, "root", "password", False, 22) 
        if re.match(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$", mn_host_ip):
            test_util.test_logger("find mn_host_ip=%s" %(mn_host_ip))
            break
    else:
        test_util.test_fail("not find valid mn_host_ip within 300s")

    mn_host_ip_lst = mn_host_ip.split('.')
    mn_host_ip_lst[3] = '200'
    mn_ip = '.'.join(mn_host_ip_lst)
    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = mn_ip
    os.environ['zstackHaVip'] = mn_ip
    test_util.test_logger("@@@DEBUG->in auto_set_mn_ip@@@ os\.environ\[\'ZSTACK_BUILT_IN_HTTP_SERVER_IP\'\]=%s; os\.environ\[\'zstackHaVip\'\]=%s"	\
                          %(os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'], os.environ['zstackHaVip']) )
    cmd = 'sed -i "s/zstackHaVip = .*$/zstackHaVip = %s/g" /root/.zstackwoodpecker/integrationtest/vm/mn_ha/deploy.tmpt' %(mn_ip)
    test_util.test_logger("@@@DEBUG->replace zstackHaVip @@@: %s" %cmd)
    os.system(cmd)
    


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
        

def wrapper_of_wait_for_management_server_start(wait_start_timeout, EXTRA_SUITE_SETUP_SCRIPT=None):
    import zstackwoodpecker.operations.node_operations as node_operations
    if os.path.basename(os.environ.get('WOODPECKER_SCENARIO_CONFIG_FILE')).strip() == "scenario-config-vpc-ceph-3-sites.xml":
        test_util.test_logger("@@@DEBUG->IS VPC CEPH@@@")
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



def return_pass_ahead_if_3sites(msg):
    if os.path.basename(os.environ.get('WOODPECKER_SCENARIO_CONFIG_FILE')).strip() == "scenario-config-vpc-ceph-3-sites.xml":
        test_util.test_pass(msg)


def return_skip_ahead_if_3sites(msg):
    if os.path.basename(os.environ.get('WOODPECKER_SCENARIO_CONFIG_FILE')).strip() == "scenario-config-vpc-ceph-3-sites.xml":
        test_util.test_skip(msg)
