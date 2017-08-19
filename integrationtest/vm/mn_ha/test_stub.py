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
    for host in mn_host_list:
        host_config = sce_ops.get_scenario_config_vm(host.name_, scenarioConfig)
        cmd = "consul info |grep -i leader_addr | awk '{print $3}' | awk -F ':' '{print $1}'"
        try:
            host_ip = test_lib.lib_execute_ssh_cmd(host.ip_, host_config.imageUsername_, host_config.imagePassword_,cmd)
        except:
            continue
        if host_ip != "" and host_ip != False and host_ip.count('.') == 3:
            return host_ip.strip()
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
    host_list = []
    for host in mn_host_list:
        host_config = sce_ops.get_scenario_config_vm(host.name_, scenarioConfig)
        cmd = "virsh list | grep -v paused | grep \"ZStack Management Node VM\""
        try:
            vm_list = test_lib.lib_execute_ssh_cmd(host.ip_, host_config.imageUsername_, host_config.imagePassword_,cmd)
            if vm_list:
                host_list.append(host)
        except:
            continue
    return host_list

def get_mn_host(scenarioConfig, scenarioFile):
    mn_host_list = []

    if scenarioConfig == None or scenarioFile == None or not os.path.exists(scenarioFile):
        return mn_host_list

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
    return mn_host_list

def migrate_mn_vm(origin_host, target_host, scenarioConfig):
    cmd = 'zsha migrate %s' % (target_host.ip_)
    host_config = sce_ops.get_scenario_config_vm(origin_host.name_, scenarioConfig)
    test_lib.lib_execute_ssh_cmd(origin_host.ip_, host_config.imageUsername_, host_config.imagePassword_,cmd)

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

def prepare_config_json(scenarioConfig, scenarioFile, deploy_config, config_json):
    mn_host_list = get_mn_host(scenarioConfig, scenarioFile)
    if len(mn_host_list) < 1:
        return False
    l2network_name = os.environ.get('l2PublicNetworkName')
    #nic_name = os.environ.get('nodeNic').replace("eth", "zsn")
    mn_ip = os.environ.get('zstackHaVip')
    mn_netmask = os.environ.get('nodeNetMask')
    mn_gateway = os.environ.get('nodeGateway')
    for i in range(len(mn_host_list)):
        os.system('sed -i s/host-%d/%s/g %s' % (i+1, mn_host_list[i].ip_,config_json))

    os.system('sed -i s/nic/%s/g %s' % ("zsn", config_json))
    os.system('sed -i s/mn_ip/%s/g %s' % (mn_ip,config_json))
    os.system('sed -i s/mn_netmask/%s/g %s' % (mn_netmask,config_json))
    os.system('sed -i s/mn_gateway/%s/g %s' % (mn_gateway,config_json))
    mn_ha_storage_type = sce_ops.get_mn_ha_storage_type(scenarioConfig, scenarioFile, deploy_config)
    if mn_ha_storage_type == 'ceph':
        os.system('sed -i s/FileConf/CephConf/g %s' % (config_json))

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
    if mn_ha_storage_type == 'ceph':
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
    if mn_ha_storage_type == 'ceph':
        cmd1="ceph osd pool create zstack 128"
        cmd2="qemu-img convert -f qcow2 -O raw %s rbd:zstack/mnvm.img" % mn_image_path
    elif mn_ha_storage_type == 'nfs':
        prepare_etc_hosts(scenarioConfig, scenarioFile, deploy_config, config_json)
        cmd1 = "cp %s /storage/mnvm.img" % (mn_image_path)
        cmd2 = "chmod a+x %s" % (installer_path)
    cmd3='%s install -p %s -c %s' % (installer_path, host_password, config_path)
    test_util.test_logger("[%s] %s" % (test_host_ip, cmd1))
    ssh.execute(cmd1, test_host_ip, test_host_config.imageUsername_, test_host_config.imagePassword_, True, 22)
    test_util.test_logger("[%s] %s" % (test_host_ip, cmd2))
    ssh.execute(cmd2, test_host_ip, test_host_config.imageUsername_, test_host_config.imagePassword_, True, 22)
    test_util.test_logger("[%s] %s" % (test_host_ip, cmd3))
    ssh.execute(cmd3, test_host_ip, test_host_config.imageUsername_, test_host_config.imagePassword_, True, 22)

def shutdown_host_network(host_vm, scenarioConfig):
    zstack_management_ip = scenarioConfig.basicConfig.zstackManagementIp.text_
    cond = res_ops.gen_query_conditions('vmNics.ip', '=', host_vm.ip_)
    host_vm_inv = sce_ops.query_resource(zstack_management_ip, res_ops.VM_INSTANCE, cond).inventories[0]
    cond = res_ops.gen_query_conditions('uuid', '=', host_vm_inv.hostUuid)
    host_inv = sce_ops.query_resource(zstack_management_ip, res_ops.HOST, cond).inventories[0]

    host_vm_config = sce_ops.get_scenario_config_vm(host_vm_inv.name_, scenarioConfig)
    l2network_nic = os.environ.get('l2ManagementNetworkInterface').replace("eth", "zsn")
    cmd = "ifdown %s" % (l2network_nic)
    sce_ops.execute_in_vm_console(zstack_management_ip, host_inv.managementIp, host_vm_inv.uuid, host_vm_config, cmd)

def reopen_host_network(host_vm, scenarioConfig):
    zstack_management_ip = scenarioConfig.basicConfig.zstackManagementIp.text_
    cond = res_ops.gen_query_conditions('vmNics.ip', '=', host_vm.ip_)
    host_vm_inv = sce_ops.query_resource(zstack_management_ip, res_ops.VM_INSTANCE, cond).inventories[0]
    cond = res_ops.gen_query_conditions('uuid', '=', host_vm_inv.hostUuid)
    host_inv = sce_ops.query_resource(zstack_management_ip, res_ops.HOST, cond).inventories[0]

    host_vm_config = sce_ops.get_scenario_config_vm(host_vm_inv.name_, scenarioConfig)
    l2network_nic = os.environ.get('l2ManagementNetworkInterface').replace("eth", "zsn")
    cmd = "ifup %s" % (l2network_nic)
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
        ensure_vr_is_running(l3_net_uuid)

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
        time.sleep(1)
        ps_list = res_ops.query_resource(res_ops.PRIMARY_STORAGE)
        for ps in ps_list:
            if not "connected" in ps.status.lower():
                test_util.test_logger("found not connected ps status: %s" %(ps.status))
                break
        else:
            return
    else:
        test_util.test_fail("ps status didn't change to Connected within 300s, therefore, failed")

def ensure_bss_connected():
    for i in range(300):
        time.sleep(1)
        bs_list = res_ops.query_resource(res_ops.BACKUP_STORAGE)
        for bs in bs_list:
            if not "connected" in bs.status.lower():
                test_util.test_logger("found not connected ps status: %s" %(bs.status))
                break
        else:
            return
    else:
        test_util.test_fail("bs status didn't change to Connected within 300s, therefore, failed")

def ensure_hosts_connected():
    for i in range(300):
        time.sleep(1)
        host_list = res_ops.query_resource(res_ops.HOST)
        for host in host_list:
            if not "connected" in host.status.lower():
                test_util.test_logger("found not connected ps status: %s" %(host.status))
                break
        else:
            return
    else:
        test_util.test_fail("host status didn't change to Connected within 300s, therefore, failed")

def ensure_host_disconnected(test_host, wait_time):
    cond = res_ops.gen_query_conditions('managementIp', '=', test_host.ip_)
    for i in range(wait_time):
        time.sleep(1)
        host_list = res_ops.query_resource(res_ops.HOST, cond)
        if "disconnected" in host_list[0].status.lower():
            test_util.test_logger("successfully got host disconnected: %s" %(host_list[0].status))
            return

def ensure_vr_is_running(l3_uuid):
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
        if vr1.state == "Running":
            break
    else:
        test_util.test_fail("virtualrouter has not been started within 300s")

