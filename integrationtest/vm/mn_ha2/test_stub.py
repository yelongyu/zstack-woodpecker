'''
test_stub to share test operations
@author: SyZhao
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


def check_if_vip_is_on_host(scenarioConfig, scenarioFile, host_ip, retry_times=1):
    """
    It checks whether vip is on host_ip
    """
    mha_s_vm_list = get_mha_s_vm_list_from_scenario_file(scenarioConfig, scenarioFile)
    if len(mha_s_vm_list) < 1:
        test_util.test_fail("not found mha host in check_if_vip_is_on_host")

    test_util.test_logger("@@DEBUG@@: mha_s_vm_list=<%s>" %(str(mha_s_vm_list)))
    vip = os.environ['zstackHaVip']
    cmd = "ip a|grep " + vip

    for retry_cnt in range(retry_times):
        for host in mha_s_vm_list:
            if host.ip_ == host_ip:
                host_config = sce_ops.get_scenario_config_vm(host.name_, scenarioConfig)
                is_find = test_lib.lib_execute_ssh_cmd(host.ip_, host_config.imageUsername_, host_config.imagePassword_,cmd)
                if is_find:
                    return True
        time.sleep(1)

    test_util.test_logger("not find vip in host_ip:%s" %(host_ip))
    return False


def exec_zsha2_version(host_ip, username, password):
    cmd = "zsha2 version"
    version_info = test_lib.lib_execute_ssh_cmd(host_ip, username, password, cmd)
    test_util.test_logger("current zsha2 version is %s" %(version_info))


def exec_zsha2_demote(host_ip, username, password):
    cmd = "zsha2 demote"
    test_lib.lib_execute_ssh_cmd(host_ip, username, password, cmd)


def exec_upgrade_mn(host_ip, username, password, zstack_bin_path):
    cmd = "TERM=xterm zsha2 upgrade-mn -yes -peerpass password " + zstack_bin_path
    if not test_lib.lib_execute_ssh_cmd(host_ip, username, password, cmd, 1800):
        test_util.test_fail('%s failed' %(cmd))


def exec_upgrade_iso(host_ip, username, password, zstack_iso_path):
    cmd = "TERM=xterm zsha2 upgrade-mn -yes -peerpass password " + zstack_iso_path
    if not test_lib.lib_execute_ssh_cmd(host_ip, username, password, cmd, 1800):
        test_util.test_fail('%s failed' %(cmd))


def exec_upgrade_zsha2(host_ip, username, password, zsha2_path):
    cmd = "chmod a+x " + zsha2_path
    test_lib.lib_execute_ssh_cmd(host_ip, username, password, cmd)
    cmd = zsha2_path + " upgrade-ha"
    test_lib.lib_execute_ssh_cmd(host_ip, username, password, cmd)


def get_buildtype_by_sce_file(scenarioFile):
    """
    It gets host with vip bound, while returned a s_vm config
    """
    with open(scenarioFile, 'r') as fd:
        xmlstr = fd.read()
        fd.close()
        scenario_file = xmlobject.loads(xmlstr)
        for s_vm in xmlobject.safe_list(scenario_file.vms.vm):
            raw_name = s_vm.name_
            test_util.test_logger("raw name from s_vm is %s" %(raw_name))
            sub_name_lst = raw_name.split('_')
            buildtype = sub_name_lst[2] + '_' + sub_name_lst[3]
            test_util.test_logger("get buildtype is %s" %(buildtype))

            return buildtype


def get_buildid_by_sce_file(scenarioFile):
    """
    It gets host with vip bound, while returned a s_vm config
    """
    with open(scenarioFile, 'r') as fd:
        xmlstr = fd.read()
        fd.close()
        scenario_file = xmlobject.loads(xmlstr)
        for s_vm in xmlobject.safe_list(scenario_file.vms.vm):
            raw_name = s_vm.name_
            test_util.test_logger("raw name from s_vm is %s" %(raw_name))
            sub_name_lst = raw_name.split('_')
            buildid = sub_name_lst[6]
            test_util.test_logger("get buildid is %s" %(buildid))

            return buildid


def get_s_vm_cfg_lst_vip_bind(scenarioConfig, scenarioFile, retry_times=1):
    """
    It gets host with vip bound, while returned a s_vm config
    """
    mha_s_vm_list = get_mha_s_vm_list_from_scenario_file(scenarioConfig, scenarioFile)
    if len(mha_s_vm_list) < 1:
        return []
    test_util.test_logger("@@DEBUG@@: mha_s_vm_list=<%s>" %(str(mha_s_vm_list)))
    host_list = []
    vip = os.environ['zstackHaVip']
    for host in mha_s_vm_list:
        host_config = sce_ops.get_scenario_config_vm(host.name_, scenarioConfig)
        cmd = "ip a|grep " + vip

        try:
            for retry_cnt in range(retry_times):
                if sce_is_sep_pub():
                    vm_list = test_lib.lib_execute_ssh_cmd(host.managementIp_, host_config.imageUsername_, host_config.imagePassword_,cmd)
                else:
                    vm_list = test_lib.lib_execute_ssh_cmd(host.ip_, host_config.imageUsername_, host_config.imagePassword_,cmd)
                if vm_list:
                    host_list.append(host)
                    break
                time.sleep(1)

        except Exception, e:
            test_util.test_logger("@@get host exception@@:%s" %(str(e)))
            continue

    test_util.test_logger("@@DEBUG@@: host_list=<%s>" %(str(host_list)))
    return host_list


def get_s_vm_cfg_lst_vip_not_bind(scenarioConfig, scenarioFile):
    """
    It gets host without vip bound, while returned a s_vm config
    """
    mha_s_vm_list = get_mha_s_vm_list_from_scenario_file(scenarioConfig, scenarioFile)
    if len(mha_s_vm_list) < 1:
        return []
    test_util.test_logger("@@DEBUG@@: mha_s_vm_list=<%s>" %(str(mha_s_vm_list)))
    host_list = []
    vip = os.environ['zstackHaVip']
    for host in mha_s_vm_list:
        host_config = sce_ops.get_scenario_config_vm(host.name_, scenarioConfig)
        cmd = "ip a|grep " + vip
        try:
            if sce_is_sep_pub():
                vm_list = test_lib.lib_execute_ssh_cmd(host.managementIp_, host_config.imageUsername_, host_config.imagePassword_,cmd)
            else:
                vm_list = test_lib.lib_execute_ssh_cmd(host.ip_, host_config.imageUsername_, host_config.imagePassword_,cmd)
            if not vm_list:
                host_list.append(host)
        except Exception, e:
            test_util.test_logger("@@get host exception@@:%s" %(str(e)))
            continue

    test_util.test_logger("@@DEBUG@@: host_list=<%s>" %(str(host_list)))
    return host_list


def get_expected_vip_s_vm_cfg_lst_after_switch(scenarioConfig, scenarioFile, vip_host_ip):
    """
    It will return another mHa host ip by vip_host_ip excluded in mha_s_vm_list
    """
    mha_s_vm_list = get_mha_s_vm_list_from_scenario_file(scenarioConfig, scenarioFile)
    for host in mha_s_vm_list:
        if host.ip_ != vip_host_ip:
            test_util.test_logger("find a candidate host ip that vip can be used:%s" %(host.ip_))
            return host.ip_
    else:
        test_util.test_fail("not found the differ host ip vip can be used")
        

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

def query_host(host_ip, scenarioConfig):
    mn_ip = scenarioConfig.basicConfig.zstackManagementIp.text_
    try:
        host_inv = sce_ops.get_vm_inv_by_vm_ip(mn_ip, host_ip)
        return host_inv
    except:
        test_util.test_logger("Fail to query host [%s]" % host_ip)
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


def get_host_by_mn_vm_process(scenarioConfig, scenarioFile):
    zstack_management_ip = scenarioConfig.basicConfig.zstackManagementIp.text_

    mha_s_vm_list = get_mha_s_vm_list_from_scenario_file(scenarioConfig, scenarioFile)
    if len(mha_s_vm_list) < 1:
        return []
    host_vm_inv = dict()
    host_inv = dict()
    for host in mha_s_vm_list:
        cond = res_ops.gen_query_conditions('vmNics.ip', '=', host.ip_)
        host_vm_inv[host] = sce_ops.query_resource(zstack_management_ip, res_ops.VM_INSTANCE, cond).inventories[0]
        cond = res_ops.gen_query_conditions('uuid', '=', host_vm_inv[host].hostUuid)
        host_inv[host] = sce_ops.query_resource(zstack_management_ip, res_ops.HOST, cond).inventories[0]

    host_list = []
    for host in mha_s_vm_list:
        cmd = "ps axjf |grep kvm | grep mnvm.img | grep -v grep"
        try:
            query_kvm_process = sce_ops.execute_in_vm_console(zstack_management_ip, host_inv[host].managementIp, host_vm_inv[host].uuid, host, cmd)
            test_util.test_logger("check mn vm kvm process on host %s: %s" % (host.ip_, query_kvm_process))
            if query_kvm_process.find('zstack/mnvm.img') >= 0:
                host_list.append(host)
        except:
            continue
    return host_list



def get_mha_s_vm_list_from_scenario_file(scenarioConfig, scenarioFile):
    mha_s_vm_list = []

    test_util.test_logger("@@DEBUG@@:<scenarioConfig:%s><scenarioFile:%s><scenarioFile is existed: %s>" \
                          %(str(scenarioConfig), str(scenarioFile), str(os.path.exists(scenarioFile))))
    if scenarioConfig == None or scenarioFile == None or not os.path.exists(scenarioFile):
        return mha_s_vm_list

    test_util.test_logger("@@DEBUG@@: after config file exist check")
    for host in xmlobject.safe_list(scenarioConfig.deployerConfig.hosts.host):
        for vm in xmlobject.safe_list(host.vms.vm):
            if xmlobject.has_element(vm, 'mHaHostRef'):
                with open(scenarioFile, 'r') as fd:
                    xmlstr = fd.read()
                    fd.close()
                    scenario_file = xmlobject.loads(xmlstr)
                    for s_vm in xmlobject.safe_list(scenario_file.vms.vm):
                        if s_vm.name_ == vm.name_:
                            mha_s_vm_list.append(s_vm)
    test_util.test_logger("@@DEBUG@@: %s" %(str(mha_s_vm_list)))
    return mha_s_vm_list

def get_host_by_index_in_scenario_file(scenarioConfig, scenarioFile, index):
    test_util.test_logger("@@DEBUG@@:<scenarioConfig:%s><scenarioFile:%s><scenarioFile is existed: %s>" \
                          %(str(scenarioConfig), str(scenarioFile), str(os.path.exists(scenarioFile))))
    if scenarioConfig == None or scenarioFile == None or not os.path.exists(scenarioFile):
        return mha_s_vm_list

    test_util.test_logger("@@DEBUG@@: after config file exist check")
    with open(scenarioFile, 'r') as fd:
        xmlstr = fd.read()
        fd.close()
        scenario_file = xmlobject.loads(xmlstr)
        return xmlobject.safe_list(scenario_file.vms.vm)[index]


def prepare_etc_hosts(scenarioConfig, scenarioFile, deploy_config, config_json):
    mha_s_vm_list = get_mha_s_vm_list_from_scenario_file(scenarioConfig, scenarioFile)
    if len(mha_s_vm_list) < 1:
        return False

    for i in range(len(mha_s_vm_list)):
        os.system('echo %s %s >> /etc/hosts' % (mha_s_vm_list[i].ip_, mha_s_vm_list[i].ip_.replace('.', '-')))

    for i in range(len(mha_s_vm_list)):
        test_host_config = sce_ops.get_scenario_config_vm(mha_s_vm_list[i].name_, scenarioConfig)
        ssh.scp_file('/etc/hosts', '/etc/hosts', mha_s_vm_list[i].ip_, test_host_config.imageUsername_, test_host_config.imagePassword_)


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


host_username = os.environ.get('physicalHostUsername')
host_password = os.environ.get('physicalHostPassword')
host_password2 = os.environ.get('physicalHostPassword2')

def down_host_network(host_ip, scenarioConfig):
    zstack_management_ip = scenarioConfig.basicConfig.zstackManagementIp.text_
    cond = res_ops.gen_query_conditions('vmNics.ip', '=', host_ip)
    host_vm_inv = sce_ops.query_resource(zstack_management_ip, res_ops.VM_INSTANCE, cond).inventories[0]
    cond = res_ops.gen_query_conditions('uuid', '=', host_vm_inv.hostUuid)
    host_inv = sce_ops.query_resource(zstack_management_ip, res_ops.HOST, cond).inventories[0]

    host_vm_config = sce_ops.get_scenario_config_vm(host_vm_inv.name_, scenarioConfig)

    cmd = "virsh domiflist %s|sed -n '3p'|awk '{print $1}'|xargs -i virsh domif-setlink %s {} down" % (host_vm_inv.uuid, host_vm_inv.uuid)
    if test_lib.lib_execute_ssh_cmd(host_inv.managementIp, host_username, host_password, "pwd"):
        test_lib.lib_execute_ssh_cmd(host_inv.managementIp, host_username, host_password, cmd)
    elif test_lib.lib_execute_ssh_cmd(host_inv.managementIp, host_username, host_password2, "pwd"):
        test_lib.lib_execute_ssh_cmd(host_inv.managementIp, host_username, host_password2, cmd)
    else:
        test_util.test_fail("The candidate password are both not for the physical host %s, tried password %s;%s with username %s" %(host_inv.managementIp, host_password, host_password2, host_username))

def up_host_network(host_ip, scenarioConfig):
    zstack_management_ip = scenarioConfig.basicConfig.zstackManagementIp.text_
    cond = res_ops.gen_query_conditions('vmNics.ip', '=', host_ip)
    host_vm_inv = sce_ops.query_resource(zstack_management_ip, res_ops.VM_INSTANCE, cond).inventories[0]
    cond = res_ops.gen_query_conditions('uuid', '=', host_vm_inv.hostUuid)
    host_inv = sce_ops.query_resource(zstack_management_ip, res_ops.HOST, cond).inventories[0]

    host_vm_config = sce_ops.get_scenario_config_vm(host_vm_inv.name_, scenarioConfig)

    cmd = "virsh domiflist %s|sed -n '3p'|awk '{print $1}'|xargs -i virsh domif-setlink %s {} up" % (host_vm_inv.uuid, host_vm_inv.uuid)
    if test_lib.lib_execute_ssh_cmd(host_inv.managementIp, host_username, host_password, "pwd"):
        test_lib.lib_execute_ssh_cmd(host_inv.managementIp, host_username, host_password, cmd)
    elif test_lib.lib_execute_ssh_cmd(host_inv.managementIp, host_username, host_password2, "pwd"):
        test_lib.lib_execute_ssh_cmd(host_inv.managementIp, host_username, host_password2, cmd)
    else:
        test_util.test_fail("The candidate password are both not for the physical host %s, tried password %s;%s with username %s" %(host_inv.managementIp, host_password, host_password2, host_username))



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

        mha_s_vm_list = get_mha_s_vm_list_from_scenario_file(scenarioConfig, scenarioFile)
        for bs_host_ip in bss_host_ip:
            for mn_host in mha_s_vm_list:
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

        mha_s_vm_list = get_mha_s_vm_list_from_scenario_file(scenarioConfig, scenarioFile)
        for bs_host_ip in bss_host_ip:
            for mn_host in mha_s_vm_list:
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
    for i in range(600):
        time.sleep(1)
        vr1 = res_ops.query_resource(res_ops.VM_INSTANCE, cond)[0]
        if vr1.state == "Running" and vr1.status == "Connected":
            test_util.test_logger("vr has successfully changed to Running and Connected")
            break
    else:
        test_util.test_fail("vr has not been successfully changed to Running and Connected within 300s: state=%s:status=%s" %(vr1.state, vr1.status))



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


def deploy_2ha(scenarioConfig, scenarioFile, deployConfig):
    mn_ip1 = get_host_by_index_in_scenario_file(scenarioConfig, scenarioFile, 0).ip_
    mn_ip2 = get_host_by_index_in_scenario_file(scenarioConfig, scenarioFile, 1).ip_
    if not xmlobject.has_element(deployConfig, 'backupStorages.miniBackupStorage'):
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

    woodpecker_vm_ip = shell.call("ip r | grep src | head -1 | awk '{print $NF}'").strip()
    zsha2_path = "/home/%s/zsha2" % woodpecker_vm_ip
    ssh.scp_file(zsha2_path, "/root/zsha2", mn_ip1, "root", "password")
    ssh.execute("chmod a+x /root/zsha2", mn_ip1, "root", "password", False, 22)

    zstack_hamon_path = "/home/%s/zstack-hamon" % woodpecker_vm_ip
    ssh.scp_file(zstack_hamon_path, "/root/zstack-hamon", mn_ip1, "root", "password")
    ssh.execute("chmod a+x /root/zstack-hamon", mn_ip1, "root", "password", False, 22)

    if xmlobject.has_element(deployConfig, 'backupStorages.miniBackupStorage'):
        cmd = '/root/zsha2 install-ha -nic br_zsn0 -gateway 172.20.0.1 -slave "root:password@' + mn_ip2 + '" -vip ' + vip + ' -time-server ' + mn_ip2 + ',' + mn_ip2 + ' -db-root-pw zstack.mysql.password -yes'
    else:
        cmd = '/root/zsha2 install-ha -nic br_zsn0 -gateway 172.20.0.1 -slave "root:password@' + mn_ip2 + '" -vip ' + vip + ' -time-server ' + node3_ip + ',' + mn_ip2 + ' -db-root-pw zstack.mysql.password -yes'
    test_util.test_logger("deploy 2ha by cmd: %s" %(cmd))
    ret, output, stderr = ssh.execute(cmd, mn_ip1, "root", "password", False, 22)
    test_util.test_logger("cmd=%s; ret=%s; output=%s; stderr=%s" %(cmd, ret, output, stderr))
    if ret!=0:
        test_util.test_fail("deploy 2ha failed")
