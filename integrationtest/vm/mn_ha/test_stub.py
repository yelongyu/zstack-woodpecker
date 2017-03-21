'''

Create an unified test_stub to share test operations

@author: Mirabel
'''
import os
import zstacklib.utils.ssh as ssh
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_util as test_util
import zstacklib.utils.shell as shell
import zstacklib.utils.xmlobject as xmlobject
import zstackwoodpecker.operations.scenario_operations as sce_ops
import zstackwoodpecker.operations.deploy_operations as dpy_ops

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
    host_config = sce_ops.get_scenario_config_vm(host_inv.name,scenarioConfig)
    for l3network in xmlobject.safe_list(host_config.l3Networks.l3Network):
        if hasattr(l3network, 'l2NetworkRef'):
            for l2networkref in xmlobject.safe_list(l3network.l2NetworkRef):
                nic_name = sce_ops.get_ref_name(l2networkref.text_, deploy_config)
                if nic_name.find('.') >= 0 :
                    vlan = nic_name.split('.')[1]
                    test_util.test_logger('[vm:] %s %s is created.' % (host_ip, nic_name))
                    cmd = 'vconfig add %s %s' % (nic_name.split('.')[0], vlan)
                    test_lib.lib_execute_ssh_cmd(host_ip, host_config.imageUsername_, vm_config.imagePassword_, cmd)
    return True

def get_host_by_mn_vm(vm_uuid, scenarioConfig, scenarioFile):
    mn_host_list = get_mn_host(scenarioConfig, scenarioFile)
    if len(mn_host_list) < 1:
        return []
    host_list = []
    for host in mn_host_list:
        host_config = sce_ops.get_scenario_config_vm(host.name_, scenarioConfig)
        cmd = "virsh list | grep \"ZStack Management Node VM\""
        vm_list = test_lib.lib_execute_ssh_cmd(host.ip_, host_config.imageUsername_, host_config.imagePassword_,cmd)
        if vm_list:
            host_list.append(host)
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

def prepare_config_json(scenarioConfig, scenarioFile, deploy_config, config_json):
    mn_host_list = get_mn_host(scenarioConfig, scenarioFile)
    if len(mn_host_list) < 1:
        return False
    l2network_name = os.environ.get('l2PublicNetworkName')
    nic_name = os.environ.get('nodeNic')
    mn_ip = os.environ.get('zstackHaVip')
    mn_netmask = os.environ.get('nodeNetMask')
    mn_gateway = os.environ.get('nodeGateway')
    for i in range(len(mn_host_list)):
        os.system('sed -i s/host-%d/%s/g %s' % (i+1, mn_host_list[i].ip_,config_json))

    os.system('sed -i s/nic/%s/g %s' % (nic_name,config_json))
    os.system('sed -i s/mn_ip/%s/g %s' % (mn_ip,config_json))
    os.system('sed -i s/mn_netmask/%s/g %s' % (mn_netmask,config_json))
    os.system('sed -i s/mn_gateway/%s/g %s' % (mn_gateway,config_json))

def deploy_ha_env(scenarioConfig, scenarioFile, deploy_config, config_json, deploy_tool, mn_img):
    prepare_config_json(scenarioConfig, scenarioFile, deploy_config, config_json)
    test_host = get_mn_host(scenarioConfig,scenarioFile)[0]
    test_host_ip = test_host.ip_
    test_host_config = sce_ops.get_scenario_config_vm(test_host.name_, scenarioConfig)
    host_password = test_host_config.imagePassword_
    installer_path = "/home/%s/z" % test_host_ip
    mn_image_path = "/home/%s/mn.qcow2" % test_host_ip
    config_path = "/home/%s/config.json" % test_host_ip
    ssh.scp_file(config_json,config_path, test_host_ip, test_host_config.imageUsername_, test_host_config.imagePassword_)
    cmd1="ceph osd pool create mevoco 128"
    cmd2="qemu-img convert -f qcow2 -O raw %s rbd:mevoco/mnvm.img" % mn_image_path
    cmd3='bash %s -i -a -p %s -c %s' % (installer_path, host_password, config_path)
    ssh.execute(cmd1, test_host_ip, test_host_config.imageUsername_, test_host_config.imagePassword_, True, 22)
    ssh.execute(cmd2, test_host_ip, test_host_config.imageUsername_, test_host_config.imagePassword_, True, 22)
    ssh.execute(cmd3, test_host_ip, test_host_config.imageUsername_, test_host_config.imagePassword_, True, 22)

def shutdown_host_network(host_vm, scenarioConfig):
    l2network_nic = os.environ.get('l2ManagementNetworkInterface')
    host_config = sce_ops.get_scenario_config_vm(host_vm.name_, scenarioConfig)
    cmd = "ifdown %s" % (l2network_nic)
    test_lib.lib_execute_ssh_cmd(host.ip_, host_config.imageUsername_, vm_config.imagePassword_,cmd)

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

def create_basic_vm(disk_offering_uuids=None, session_uuid = None):
    image_name = os.environ.get('imageName_net')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    l3_name = os.environ.get('l3PublicNetworkName')
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    return create_vm([l3_net_uuid], image_uuid, 'basic_no_vlan_vm', disk_offering_uuids, session_uuid = session_uuid)

def check_directly_up(target_ip, timeout=1):
    try:
        shell.call('ping -c 1 -W %d %s' % (timeout, target_ip)
    except:
        test_util.test_logger('ping %s failed' % target_ip)
        return False
    else:
        test_util.test_logger('ping %s successfully' % target_ip)
        return True
