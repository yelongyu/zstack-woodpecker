'''
test_stub to share test operations
@author: SyZhao
'''
import os
import time
import hashlib
import zstacklib.utils.ssh as ssh
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_util as test_util
import zstacklib.utils.shell as shell
import zstacklib.utils.xmlobject as xmlobject
import zstacklib.utils.jsonobject as jsonobject
import zstackwoodpecker.operations.scenario_operations as sce_ops
import zstackwoodpecker.operations.deploy_operations as dpy_ops
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import zstackwoodpecker.zstack_test.zstack_test_image as test_image
import zstackwoodpecker.operations.ha_operations as ha_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.backupstorage_operations as bs_ops
import zstackwoodpecker.operations.primarystorage_operations as ps_ops
import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.zstack_test.zstack_test_volume as zstack_volume_header
import zstackwoodpecker.zstack_test.zstack_test_vm as zstack_vm_header
from zstacklib.utils.http import json_post
import zstackwoodpecker.test_state as test_state
from cherrypy.scaffold import root
import zstackwoodpecker.operations.config_operations as conf_ops


def migrate_vm_to_random_host(vm):
    test_util.test_dsc("migrate vm to random host")
    if not test_lib.lib_check_vm_live_migration_cap(vm.vm):
        test_util.test_skip('skip migrate if live migrate not supported')
    target_host = test_lib.lib_find_random_host(vm.vm)
    current_host = test_lib.lib_find_host_by_vm(vm.vm)
    vm.migrate(target_host.uuid)

    new_host = test_lib.lib_get_vm_host(vm.vm)
    if not new_host:
        test_util.test_fail('Not find available Hosts to do migration')

    if new_host.uuid != target_host.uuid:
        test_util.test_fail('[vm:] did not migrate from [host:] %s to target [host:] %s, but to [host:] %s' % (vm.vm.uuid, current_host.uuid, target_host.uuid, new_host.uuid))
    else:
        test_util.test_logger('[vm:] %s has been migrated from [host:] %s to [host:] %s' % (vm.vm.uuid, current_host.uuid, target_host.uuid))

def create_vm_with_iso(l3_uuid_list, image_uuid, vm_name = None, root_disk_uuids = None, instance_offering_uuid = None, \
                       disk_offering_uuids = None, default_l3_uuid = None, system_tags = None, \
                       session_uuid = None, ps_uuid=None):
    vm_creation_option = test_util.VmOption()
    conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
    if not instance_offering_uuid:
        instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_l3_uuids(l3_uuid_list)
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_name(vm_name)
    vm_creation_option.set_root_disk_uuid(root_disk_uuids)
    vm_creation_option.set_data_disk_uuids(disk_offering_uuids)
    vm_creation_option.set_default_l3_uuid(default_l3_uuid)
    vm_creation_option.set_system_tags(system_tags)
    vm_creation_option.set_session_uuid(session_uuid)
    vm_creation_option.set_ps_uuid(ps_uuid)
    vm_creation_option.set_timeout(600000)
    vm = zstack_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    return vm

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

def skip_if_not_storage_network_separate(scenarioConfig):
    is_storage_network_separated = False
    for host in xmlobject.safe_list(scenarioConfig.deployerConfig.hosts.host):
        for vm in xmlobject.safe_list(host.vms.vm):
            for l3Network in xmlobject.safe_list(vm.l3Networks.l3Network):
                if xmlobject.has_element(l3Network, 'primaryStorageRef'):
                    is_storage_network_separated = True
                    break
    if not is_storage_network_separated:
        test_util.test_skip("not found separate network in scenario config.")


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

def create_volume(volume_creation_option=None, from_offering=True):
    if not volume_creation_option:
        disk_offering = test_lib.lib_get_disk_offering_by_name(os.environ.get('smallDiskOfferingName'))
        volume_creation_option = test_util.VolumeOption()
        volume_creation_option.set_disk_offering_uuid(disk_offering.uuid)
        volume_creation_option.set_name('vr_test_volume')

    volume = zstack_volume_header.ZstackTestVolume()
    volume.set_creation_option(volume_creation_option)
    volume.create(from_offering)
    return volume

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

def get_sce_hosts(scenarioConfig=test_lib.all_scenario_config, scenarioFile=test_lib.scenario_file):
    host_list = []

    if scenarioConfig == None or scenarioFile == None or not os.path.exists(scenarioFile):
        return host_list

    for host in xmlobject.safe_list(scenarioConfig.deployerConfig.hosts.host):
        for vm in xmlobject.safe_list(host.vms.vm):
            with open(scenarioFile, 'r') as fd:
                xmlstr = fd.read()
                fd.close()
                scenario_file = xmlobject.loads(xmlstr)
                for s_vm in xmlobject.safe_list(scenario_file.vms.vm):
                    if s_vm.name_ == vm.name_:
                        host_list.append(s_vm)
    return host_list

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
        

def recover_host(host_vm, scenarioConfig, deploy_config):
    stop_host(host_vm, scenarioConfig)
    host_inv = start_host(host_vm, scenarioConfig)
    if not host_inv:
       return False
    recover_host_vlan(host_vm, scenarioConfig, deploy_config)

def recover_host_vlan(host_vm, scenarioConfig, deploy_config):
    host_ip = host_vm.ip_
    test_lib.lib_wait_target_up(host_ip, '22', 120)
    host_config = sce_ops.get_scenario_config_vm(host_vm.name_,scenarioConfig)
    for l3network in xmlobject.safe_list(host_config.l3Networks.l3Network):
        if hasattr(l3network, 'l2NetworkRef'):
            for l2networkref in xmlobject.safe_list(l3network.l2NetworkRef):
                nic_name = sce_ops.get_ref_l2_nic_name(l2networkref.text_, deploy_config)
                if nic_name.find('.') >= 0 :
                    vlan = nic_name.split('.')[1]
                    test_util.test_logger('[vm:] %s %s is created.' % (host_ip, nic_name.replace("eth", "zsn")))
                    cmd = 'vconfig add %s %s' % (nic_name.split('.')[0].replace("eth", "zsn"), vlan)
                    test_lib.lib_execute_ssh_cmd(host_ip, host_config.imageUsername_, host_config.imagePassword_, cmd)
    return True

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

def reboot_host(host_vm, scenarioConfig):
    host_vm_uuid = host_vm.uuid_
    mn_ip = scenarioConfig.basicConfig.zstackManagementIp.text_
    try:
        host_inv = sce_ops.reboot_vm(mn_ip, host_vm_uuid)
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

def get_host_by_index_in_scenario_file(scenarioConfig, scenarioFile, index=None, ip=None):
    test_util.test_logger("@@DEBUG@@:<scenarioConfig:%s><scenarioFile:%s><scenarioFile is existed: %s>" \
                          %(str(scenarioConfig), str(scenarioFile), str(os.path.exists(scenarioFile))))
    if scenarioConfig == None or scenarioFile == None or not os.path.exists(scenarioFile):
        return mha_s_vm_list

    test_util.test_logger("@@DEBUG@@: after config file exist check")
    with open(scenarioFile, 'r') as fd:
        xmlstr = fd.read()
        fd.close()
        scenario_file = xmlobject.loads(xmlstr)
        sce_vm_list = xmlobject.safe_list(scenario_file.vms.vm)
        if ip is not None:
            return [vm for vm in sce_vm_list if vm.ip_ == ip][0]
        else:
            return sce_vm_list[index]


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

def down_host_network(host_ip, scenarioConfig, network_type):
    zstack_management_ip = scenarioConfig.basicConfig.zstackManagementIp.text_
    cond = res_ops.gen_query_conditions('vmNics.ip', '=', host_ip)
    host_vm_inv = sce_ops.query_resource(zstack_management_ip, res_ops.VM_INSTANCE, cond).inventories[0]
    cond = res_ops.gen_query_conditions('uuid', '=', host_vm_inv.hostUuid)
    host_inv = sce_ops.query_resource(zstack_management_ip, res_ops.HOST, cond).inventories[0]

    host_vm_config = sce_ops.get_scenario_config_vm(host_vm_inv.name_, scenarioConfig)

    if network_type == "storage_net":
        filter_key = "br_vx"
    elif network_type == "managment_net":
        filter_key = "br_bond0"
    else:
        test_util.test_fail("not support netwoek_type=%s" %(str(network_type)))
    #cmd = "virsh domiflist %s|sed -n '3p'|awk '{print $1}'|xargs -i virsh domif-setlink %s {} down" % (host_vm_inv.uuid, host_vm_inv.uuid)
    cmd = "virsh domiflist %s|grep %s|awk '{print $1}'|xargs -i virsh domif-setlink %s {} down" % (host_vm_inv.uuid, filter_key, host_vm_inv.uuid)
    if test_lib.lib_execute_ssh_cmd(host_inv.managementIp, host_username, host_inv.name, "pwd"):
        test_lib.lib_execute_ssh_cmd(host_inv.managementIp, host_username, host_inv.name, cmd)
    elif test_lib.lib_execute_ssh_cmd(host_inv.managementIp, host_username, host_password, "pwd"):
        test_lib.lib_execute_ssh_cmd(host_inv.managementIp, host_username, host_password, cmd)
    elif test_lib.lib_execute_ssh_cmd(host_inv.managementIp, host_username, host_password2, "pwd"):
        test_lib.lib_execute_ssh_cmd(host_inv.managementIp, host_username, host_password2, cmd)
    else:
        test_util.test_fail("The candidate password are both not for the physical host %s, tried password %s;%s with username %s" %(host_inv.managementIp, host_password, host_password2, host_username))

def check_vm_running_on_host(vm_uuid, host_ip):
    cmd = "virsh list|grep %s|awk '{print $3}'" %(vm_uuid)
    host_username = os.environ.get('hostUsername')
    host_password = os.environ.get('hostPassword')
    vm_is_exist = True if test_lib.lib_execute_ssh_cmd(host_ip, host_username, host_password, cmd) else False

    return vm_is_exist

def up_host_network(host_ip, scenarioConfig, network_type):
    zstack_management_ip = scenarioConfig.basicConfig.zstackManagementIp.text_
    cond = res_ops.gen_query_conditions('vmNics.ip', '=', host_ip)
    host_vm_inv = sce_ops.query_resource(zstack_management_ip, res_ops.VM_INSTANCE, cond).inventories[0]
    cond = res_ops.gen_query_conditions('uuid', '=', host_vm_inv.hostUuid)
    host_inv = sce_ops.query_resource(zstack_management_ip, res_ops.HOST, cond).inventories[0]

    host_vm_config = sce_ops.get_scenario_config_vm(host_vm_inv.name_, scenarioConfig)

    if network_type == "storage_net":
        filter_key = "br_vx"
    elif network_type == "managment_net":
        filter_key = "br_bond0"
    else:
        test_util.test_fail("not support netwoek_type=%s" %(str(network_type)))

    cmd = "virsh domiflist %s|grep %s|awk '{print $1}'|xargs -i virsh domif-setlink %s {} up" % (host_vm_inv.uuid, filter_key, host_vm_inv.uuid)
    if test_lib.lib_execute_ssh_cmd(host_inv.managementIp, host_username, host_inv.name, "pwd"):
        test_lib.lib_execute_ssh_cmd(host_inv.managementIp, host_username, host_inv.name, cmd)
    elif test_lib.lib_execute_ssh_cmd(host_inv.managementIp, host_username, host_password, "pwd"):
        test_lib.lib_execute_ssh_cmd(host_inv.managementIp, host_username, host_password, cmd)
    elif test_lib.lib_execute_ssh_cmd(host_inv.managementIp, host_username, host_password2, "pwd"):
        test_lib.lib_execute_ssh_cmd(host_inv.managementIp, host_username, host_password2, cmd)
    else:
        test_util.test_fail("The candidate password are both not for the physical host %s, tried password %s;%s with username %s" %(host_inv.managementIp, host_password, host_password2, host_username))

def create_mini_vm(l3_uuid_list, image_uuid, vm_name = None, cpu_num = None, memory_size = None, \
              system_tags = None, instance_offering_uuid = None, cluster_uuid=None, \
              rootVolume_systemTags=["volumeProvisioningStrategy::ThickProvisioning"], session_uuid = None):
    if not vm_name:
        vm_name = 'mini_vm'
    if not cpu_num:
        cpu_num = 1
    if not memory_size:
        # set memory size to 1G
        memory_size = 1073741824
    vm_creation_option = test_util.VmOption()
    conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
    vm_creation_option.set_l3_uuids(l3_uuid_list)
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_name(vm_name)
    vm_creation_option.set_cpu_num(cpu_num)
    vm_creation_option.set_memory_size(memory_size)
    vm_creation_option.set_system_tags(system_tags)
    vm_creation_option.set_rootVolume_systemTags(rootVolume_systemTags)
    vm_creation_option.set_cluster_uuid(cluster_uuid)
    vm_creation_option.set_session_uuid(session_uuid)
    vm_creation_option.set_timeout(900000)
    vm = test_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    return vm

def create_vm(l3_uuid_list=[], image_name=None, vm_name=None, provisioning='thick', cpu_num=None, mem_size=None):
    if not l3_uuid_list:
        l3_net_uuid = test_lib.lib_get_l3_by_name(os.getenv('l3PublicNetworkName')).uuid
        l3_uuid_list.append(l3_net_uuid)
    image_name = image_name if image_name else os.getenv('imageName_net')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    if provisioning == 'thin':
        rootVolume_systemTags = ["volumeProvisioningStrategy::ThinProvisioning"]
    else:
        rootVolume_systemTags = ["volumeProvisioningStrategy::ThickProvisioning"]
    vm = create_mini_vm(l3_uuid_list, image_uuid, vm_name=vm_name, cpu_num=cpu_num, memory_size=mem_size, rootVolume_systemTags=rootVolume_systemTags)
    return vm

def create_windows_vm():
    l3_net_uuid = test_lib.lib_get_l3_by_name(os.getenv('l3PublicNetworkName')).uuid
    cond = res_ops.gen_query_conditions('format', '!=', 'iso')
    cond = res_ops.gen_query_conditions('platform', '=', 'Windows', cond)
    image_uuid = res_ops.query_resource(res_ops.IMAGE, cond)[0].uuid
    vm = create_mini_vm([l3_net_uuid], image_uuid, cpu_num=4, memory_size=4294967296)
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

def ensure_bss_connected(exclude_host=[]):
    for i in range(300):
        #time.sleep(1)
        bs_list = res_ops.query_resource(res_ops.BACKUP_STORAGE)
        for exh in exclude_host:
            for bs in bs_list:
                if exh.managementIp_ == bs.hostname or exh.ip_ == bs.hostname:
                    bs_list.remove(bs)

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


class ImageReplication(object):
    def __init__(self):
        self.replication_grp = None
        self.bs1 = None
        self.bs2 = None
        self.vm = None
        self.test_obj_dict = test_state.TestStateDict()
        self.image = None

    def create_replication_grp(self, name):
        grp_inv = bs_ops.create_image_replication_group(name)
        self.replication_grp = grp_inv.inventory

    def del_replication_grp(self, uuid):
        bs_ops.del_image_replication_group(uuid)

    def get_replication_grp(self, name=None):
        if name:
            conditions = res_ops.gen_query_conditions('name', '=', name)
            grp_inv = res_ops.query_resource(res_ops.REPLICATIONGROUP, conditions)
        else:
            grp_inv = res_ops.query_resource(res_ops.REPLICATIONGROUP)
        return grp_inv

    def cleanup_replication_grp(self):
        repl_grp = self.get_replication_grp()
        for grp in repl_grp:
            self.del_replication_grp(grp.uuid)

    def add_bs_to_repliction_grp(self, grp_uuid=None):
        if not grp_uuid:
            grp_uuid = self.get_replication_grp()[0].uuid
        bs_list = res_ops.query_resource(res_ops.IMAGE_STORE_BACKUP_STORAGE)
        bs_uuid_list = [bs.uuid for bs in bs_list]
        bs_ops.add_bs_to_image_replication_group(grp_uuid, bs_uuid_list)

    def get_image_inv(self, image_name):
        conditions = res_ops.gen_query_conditions('name', '=', image_name)
        image_inv = res_ops.query_resource(res_ops.IMAGE, conditions)[0]
        return image_inv

    def wait_for_image_replicated(self, image_name):
        for r in xrange(600):
            _image = self.get_image_inv(image_name)
            image_status = [bs_ref.status for bs_ref in _image.backupStorageRefs]
            if image_status.count('Ready') == 2:
                test_util.test_logger('Image [name: %s] is ready on all BS' % image_name)
                self.image = self.get_image_inv(image_name)
                break
            else:
                if r > 100 and len(image_status) != 2:
                    test_util.test_fail('Image replication was not started within 5 minutes')
                else:
                    time.sleep(3)

    def wait_for_downloading(self, image_name, timeout=600):
        for _ in xrange(timeout):
            _image = self.get_image_inv(image_name)
            image_status = [bs_ref.status for bs_ref in _image.backupStorageRefs]
            if set(image_status) == set(['Ready', 'Downloading']):
                test_util.test_logger('Image [name: %s] is being replicated' % image_name)
                break
            else:
                time.sleep(1)

    def get_chunk_md5(self, chunk_data):
        md5 = hashlib.md5(chunk_data)
        return md5.hexdigest()

    def get_img_manifests(self, uri):
        rsp = json_post(uri=uri, method='GET', fail_soon=True)
        return jsonobject.loads(rsp)

    def get_blobs_md5_list(self, bs_ip, img_uuid, digest):
        md5_list = set()
        blobs_uri = 'https://%s:8000/v1/%s/blobs/%s' % (bs_ip, img_uuid, digest)
        blobs = json_post(uri=blobs_uri, method='GET', fail_soon=True)
        blobs_chunks = jsonobject.loads(blobs).chunks
        for chunk_hash in blobs_chunks:
            chunk_uri = 'https://%s:8000/v1/%s/blobs/%s/chunks/%s' % (bs_ip, img_uuid, digest, chunk_hash)
            chunk_md5 = self.get_chunk_md5(json_post(uri=chunk_uri, method='GET', fail_soon=True))
            md5_list.add(chunk_md5)
        return md5_list

    def check_image_data(self, image_name, expunged=False):
        image = self.image if self.image else self.get_image_inv(image_name)
        bs_refs1, bs_refs2 = image.backupStorageRefs
        assert bs_refs1.installPath == bs_refs2.installPath
        bs1 = test_lib.lib_get_backup_storage_by_uuid(bs_refs1.backupStorageUuid)
        bs2 = test_lib.lib_get_backup_storage_by_uuid(bs_refs2.backupStorageUuid)
        image_url = bs_refs1.installPath
        image_info = image_url.split('://')[1].split('/')
        mainfests_uri = 'https://%s:8000/v1/%s/manifests/%s' % (bs1.hostname, image_info[0], image_info[1])
        manifests = self.get_img_manifests(mainfests_uri)
        mainfests_uri2 = 'https://%s:8000/v1/%s/manifests/%s' % (bs2.hostname, image_info[0], image_info[1])
        manifests2 = self.get_img_manifests(mainfests_uri2)
        test_util.test_logger('Response of requesting manifests from BS [hostname: %s]: %s' % \
                                                    (bs1.hostname, jsonobject.dumps(manifests)))
        test_util.test_logger('Response of requesting manifests from BS [hostname: %s]: %s' % \
                                                    (bs2.hostname, jsonobject.dumps(manifests2)))
        if expunged:
            assert manifests.code == 404
            assert manifests2.code == 404
            test_util.test_logger("Image data has been cleanup up on all BS")
        else:
            blobsum = manifests.blobsum
            blobsum2 = manifests2.blobsum
            assert blobsum == blobsum2
            md5_list1 = self.get_blobs_md5_list(bs1.hostname, image.uuid, blobsum)
            test_util.test_logger('Image chunks md5 on bs1: %s' % md5_list1)
            md5_list2 = self.get_blobs_md5_list(bs2.hostname, image.uuid, blobsum)
            test_util.test_logger('Image chunks md5 on bs2: %s' % md5_list2)
            assert len(md5_list1) == len(md5_list2), 'Image chunks check failed!'
            assert set(md5_list1) == set(md5_list2), 'Image chunks check failed!'

    def wait_for_bs_status_change(self, status='Connected', timeout=300):
        test_util.test_dsc('Wait for BS changing to %s' % status)
        expected_num = 2 if status == 'Connected' else 1
        for _ in xrange(timeout):
            bs_list = res_ops.query_resource(res_ops.IMAGE_STORE_BACKUP_STORAGE)
            bs_status_list = [bs.status for bs in bs_list]
            if bs_status_list.count(status) == expected_num:
                break
            else:
                time.sleep(1)
        else:
            test_util.test_fail('BS status was not changed to "%s" within %s seconds' % (status, timeout))

    def reconnect_host(self, timeout=300):
        test_util.test_dsc('Reconnect all Hosts')
        host_list = res_ops.query_resource(res_ops.HOST)
        for host in host_list:
            host_ops.reconnect_host(host.uuid)

    def wait_for_host_connected(self, timeout=300, retry=1):
        for _ in xrange(timeout):
            host_list = res_ops.query_resource(res_ops.HOST)
            host_status = [host.status for host in host_list]
            if host_status.count('Connected') < 2:
                time.sleep(1)
            else:
                test_util.test_logger('All hosts are connected')
                break
        # check again in case host status changed
        time.sleep(60)
        retry -= 1
        if retry > 0:
            self.wait_for_host_connected(timeout=timeout, retry=retry)

    def get_bs_list(self):
        bs_list = res_ops.query_resource(res_ops.IMAGE_STORE_BACKUP_STORAGE)
        bs_list = [bs for bs in bs_list if bs.status == 'Connected']
        if len(bs_list) < 2:
            test_util.test_fail('There is only 1 ImageStore backup storage connected')
        return bs_list

    def reclaim_space_from_bs(self):
        bs_list = self.get_bs_list()
        for bs in bs_list:
            bs_ops.reclaim_space_from_bs(bs.uuid)

    def add_image(self, image_name, bs_uuid, url=None, img_format='qcow2'):
        url = url if url else os.path.join(os.getenv('imageServer'), 'iso/iso_for_install_vm_test.iso')
        img_option = test_util.ImageOption()
        img_option.set_name(image_name)
        img_option.set_format(img_format)
        img_option.set_backup_storage_uuid_list([bs_uuid])
        img_option.set_url(url)
        img_option.set_timeout(900000)
        if img_format == 'iso':
            image_inv = img_ops.add_iso_template(img_option)
        else:
            image_inv = img_ops.add_image(img_option)
        image = test_image.ZstackTestImage()
        image.set_image(image_inv)
        image.set_creation_option(img_option)
        self.test_obj_dict.add_image(image)
        self.image = image.get_image()

    def delete_image(self, uuid=None):
        if not uuid:
            uuid = self.image.uuid
        img_ops.delete_image(uuid)

    def recover_image(self, uuid=None):
        if not uuid:
            uuid = self.image.uuid
        img_ops.recover_image(uuid)

    def expunge_image(self, uuid=None):
        if not uuid:
            uuid = self.image.uuid
        img_ops.expunge_image(uuid)

    def create_vm(self, image_name=None, vm_name=None, provisioning='thick', cpu_num=2, mem_size=2147483648):
        image_name = image_name if image_name else os.getenv('imageName_net')
        l3_name = os.environ.get('l3PublicNetworkName')
        l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
        image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
        if provisioning == 'thin':
            rootVolume_systemTags = ["volumeProvisioningStrategy::ThinProvisioning"]
        else:
            rootVolume_systemTags = ["volumeProvisioningStrategy::ThickProvisioning"]
        cluster_list = res_ops.query_resource(res_ops.CLUSTER)
        _cluster_list = cluster_list[:]
        for cluster in _cluster_list:
            conditions = res_ops.gen_query_conditions('clusterUuid', '=', cluster.uuid)
            conditions = res_ops.gen_query_conditions('status', '!=', 'Connected', conditions)
            if res_ops.query_resource(res_ops.HOST, conditions):
                cluster_list.remove(cluster)
        vm = create_mini_vm([l3_net_uuid], image_uuid, vm_name=vm_name, cpu_num=cpu_num, memory_size=mem_size, 
                            rootVolume_systemTags=rootVolume_systemTags, cluster_uuid=cluster_list[0].uuid)
        self.vm = vm
        vm_inv = self.vm.get_vm()
        if vm_inv.platform == 'Windows':
            vm_ip = vm_inv.vmNics[0].ip
            test_lib.lib_wait_target_up(vm_ip, '23', 1200)
        else:
            self.vm.check()
        return vm

    def crt_vm_image(self, image_name, bs_uuid=None):
        bs_uuid = bs_uuid if bs_uuid else self.get_bs_list()[0].uuid
        image_creation_option = test_util.ImageOption()
        image_creation_option.set_name(image_name)
        image_creation_option.set_backup_storage_uuid_list([bs_uuid])
        image_creation_option.set_root_volume_uuid(self.vm.get_vm().allVolumes[0].uuid)
        image_creation_option.set_timeout(900000)
        root_template = img_ops.create_root_volume_template(image_creation_option)
        return root_template

    def create_iso_vm(self):
        data_volume_size = 10737418240
        disk_offering_option = test_util.DiskOfferingOption()
        disk_offering_option.set_name('root-disk-iso')
        disk_offering_option.set_diskSize(data_volume_size)
        data_volume_offering = vol_ops.create_volume_offering(disk_offering_option)
        l3_name = os.environ.get('l3PublicNetworkName')
        l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
        root_disk_uuid = data_volume_offering.uuid
        self.vm = create_vm_with_iso([l3_net_uuid], self.image.uuid, 'vm-iso', root_disk_uuid)
        host_ip = test_lib.lib_find_host_by_vm(self.vm.get_vm()).managementIp
        self.test_obj_dict.add_vm(self.vm)
        vm_inv = self.vm.get_vm()
        vm_ip = vm_inv.vmNics[0].ip
        ssh_timeout = test_lib.SSH_TIMEOUT
        test_lib.SSH_TIMEOUT = 3600
        test_lib.lib_set_vm_host_l2_ip(vm_inv)
        cmd ='[ -e /root ]'
        if not test_lib.lib_ssh_vm_cmd_by_agent_with_retry(host_ip, vm_ip, 'root', 'password', cmd):
            test_lib.SSH_TIMEOUT = ssh_timeout
            test_util.test_fail("Create VM via ISO failed!")

    def clean_on_expunge(self, value='true'):
        conf_ops.change_global_config('imagestore', 'cleanOnExpunge', value)

    def operate_bs_service(self, bs_ip, op='stop'):
        cmd = 'service zstack-imagestorebackupstorage %s' % op
        ssh.execute(cmd, bs_ip, "root", "password", port=22)

