'''

scenario operations for setup zstack test.

@author: quarkonics
'''

import zstacklib.utils.shell as shell
import apibinding.api_actions as api_actions
from apibinding import api
import zstacklib.utils.xmlobject as xmlobject
import json
import xml.etree.cElementTree as etree
import apibinding.inventory as inventory
import os
import sys
import traceback
import time
import urllib2
import xml.dom.minidom as minidom
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstacklib.utils.ssh as ssh
import zstacklib.utils.http as http
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.operations.vpc_operations as vpc_ops
import zstackwoodpecker.operations.volume_operations as volume_ops
import zstackwoodpecker.zstack_test.zstack_test_eip as zstack_eip_header
import zstackwoodpecker.zstack_test.zstack_test_vip as zstack_vip_header
from threading import Thread

def wait_for_target_vm_retry_after_reboot(zstack_management_ip, vm_ip, vm_uuid):
    retry_count = 0
    while retry_count < 3 and not test_lib.lib_wait_target_up(vm_ip, '22', 360):
        test_util.test_warn("Could not reach target vm: %s %s, retry after reboot it" % (vm_ip, vm_uuid))
        reboot_vm(zstack_management_ip, vm_uuid)
        retry_count += 1

    if test_lib.lib_wait_target_up(vm_ip, '22', 360):
        os.system('sshpass -p password ssh root@%s swapoff -a' % vm_ip)
        return True
    return False

def replace_env_params_if_scenario():
    """
    This is aim to replace environment parameters those are used and different 
    if the current env is not scenario.
    """
    
    #ceph url:
    pss = res_ops.query_resource(res_ops.PRIMARY_STORAGE)
    for ps in pss:
        if ps.type.lower() == 'ceph':
            ps_mon_ip = ps.mons[0].monAddr
            os.environ['cephPrimaryStorageMonUrls'] = 'root:password@%s' % ps_mon_ip
            os.environ['cephBackupStorageMonUrls'] = 'root:password@%s' % ps_mon_ip
            break

    return

def create_eip(eip_name=None, vip_uuid=None, vnic_uuid=None, vm_obj=None, \
        session_uuid = None):
    if not vip_uuid:
        l3_name = os.environ.get('l3PublicNetworkName')
        l3_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
        vip_uuid = net_ops.acquire_vip(l3_uuid).uuid

    eip_option = test_util.EipOption()
    eip_option.set_name(eip_name)
    eip_option.set_vip_uuid(vip_uuid)
    eip_option.set_vm_nic_uuid(vnic_uuid)
    eip_option.set_session_uuid(session_uuid)
    eip = zstack_eip_header.ZstackTestEip()
    eip.set_creation_option(eip_option)
    if vnic_uuid and not vm_obj:
        test_util.test_fail('vm_obj can not be None in create_eip() API, when setting vm_nic_uuid.')
    eip.create(vm_obj)
    return eip

def create_vip(vip_name=None, l3_uuid=None, session_uuid = None):
    if not vip_name:
        vip_name = 'test vip'
    if not l3_uuid:
        l3_name = os.environ.get('l3PublicNetworkName')
        l3_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid

    vip_creation_option = test_util.VipOption()
    vip_creation_option.set_name(vip_name)
    vip_creation_option.set_l3_uuid(l3_uuid)
    vip_creation_option.set_session_uuid(session_uuid)

    vip = zstack_vip_header.ZstackTestVip()
    vip.set_creation_option(vip_creation_option)
    vip.create()

    return vip

def sync_call(http_server_ip, apicmd, session_uuid):
    api_instance = api.Api(host = http_server_ip, port = '8080')
    if session_uuid:
        api_instance.set_session_to_api_message(apicmd, session_uuid)
    (name, reply) = api_instance.sync_call(apicmd)
    if not reply.success: raise api.ApiError("Sync call at %s: [%s] meets error: %s." % (http_server_ip, apicmd.__class__.__name__, api.error_code_to_string(reply.error)))
    print("[Sync call at %s]: [%s] Success" % (http_server_ip, apicmd.__class__.__name__))
    return reply

def async_call(http_server_ip, apicmd, session_uuid):
    api_instance = api.Api(host = http_server_ip, port = '8080')
    api_instance.set_session_to_api_message(apicmd, session_uuid)
    (name, event) = api_instance.async_call_wait_for_complete(apicmd)
    if not event.success: raise api.ApiError("Async call at %s: [%s] meets error: %s." % (http_server_ip, apicmd.__class__.__name__, api.error_code_to_string(reply.error)))
    print("[Async call at %s]: [%s] Success" % (http_server_ip, apicmd.__class__.__name__))
    return event

def login_as_admin(http_server_ip):
    accountName = inventory.INITIAL_SYSTEM_ADMIN_NAME
    password = inventory.INITIAL_SYSTEM_ADMIN_PASSWORD
    return login_by_account(http_server_ip, accountName, password)

def login_by_account(http_server_ip, name, password, timeout = 60000):
    login = api_actions.LogInByAccountAction()
    login.accountName = name
    login.password = password
    #login.timeout = 15000
    #since system might be hang for a while, when archive system log in 00:00:00
    #, it is better to increase timeout time to 60000 to avoid of no response
    login.timeout = timeout
    session_uuid = async_call(http_server_ip, login, None).inventory.uuid
    return session_uuid

def logout(http_server_ip, session_uuid):
    logout = api_actions.LogOutAction()
    logout.timeout = 300000
    logout.sessionUuid = session_uuid
    async_call(http_server_ip, logout, session_uuid)

def execute_action_with_session(http_server_ip, action, session_uuid, async=True):
    if session_uuid:
        action.sessionUuid = session_uuid
        if async:
            evt = async_call(http_server_ip, action, session_uuid)
        else:
            evt = sync_call(http_server_ip, action, session_uuid)
    else:
        session_uuid = login_as_admin(http_server_ip)
        try:
            action.sessionUuid = session_uuid
            if async:
                evt = async_call(http_server_ip, action, session_uuid)
            else:
                evt = sync_call(http_server_ip, action, session_uuid)
        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            raise e
        finally:
            logout(http_server_ip, session_uuid)

    return evt

def setup_node_vm(vm_inv, vm_config, deploy_config):
    for nodeRef in xmlobject.safe_list(vm_config.nodeRef):
        print nodeRef.text_
        import commands
        vm_ip = test_lib.lib_get_vm_nic_by_l3(vm_inv, vm_inv.defaultL3NetworkUuid).ip
        src_file = '/home/jacocoagent.jar'
        dst_file = '/home/jacocoagent.jar' 
        check_exist_cmd = 'ls %s' %dst_file
        try:
            (retcode, output, erroutput) = ssh.execute(check_exist_cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_)
        except Exception as e:
            test_util.test_logger("Copy file %s from woodpecker node to %s on mn node" %(src_file, dst_file))
            ssh.scp_file(src_file, dst_file, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_)

def get_ref_l2_nic_name(l2network_name, deploy_config):
    for zone in xmlobject.safe_list(deploy_config.zones.zone):
        if hasattr(zone.l2Networks, 'l2NoVlanNetwork'):
            for l2novlannetwork in xmlobject.safe_list(zone.l2Networks.l2NoVlanNetwork):
                if l2novlannetwork.name_ == l2network_name:
                    return l2novlannetwork.physicalInterface_
        if hasattr(zone.l2Networks, 'l2VlanNetwork'):
            for l2vlannetwork in xmlobject.safe_list(zone.l2Networks.l2VlanNetwork):
                if l2vlannetwork.name_ == l2network_name:
                    return l2vlannetwork.physicalInterface_
        if hasattr(zone.l2Networks, 'l2VxlanNetwork'):
            for l2vxlannetwork in xmlobject.safe_list(zone.l2Networks.l2VxlanNetwork):
                if l2vxlannetwork.name_ == l2network_name:
                    return 'eth0'
    return None

def get_deploy_host(vm_name, deploy_config):
    for zone in xmlobject.safe_list(deploy_config.zones.zone):
        for cluster in xmlobject.safe_list(zone.clusters.cluster):
            for host in xmlobject.safe_list(cluster.hosts.host):
                if host.name_ == vm_name:
                    return host

def setup_vm_console(vm_inv, vm_config, deploy_config):
    vm_ip = test_lib.lib_get_vm_nic_by_l3(vm_inv, vm_inv.defaultL3NetworkUuid).ip
    cmd = "sed -i 's/quiet/quiet console=ttyS0/g' /etc/default/grub"
    ssh.execute(cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, 22)
    cmd = "grub2-mkconfig -o /boot/grub2/grub.cfg; sync; sync; sync"
    ssh.execute(cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, 22)

def execute_in_vm_console(zstack_management_ip, host_ip, vm_name, vm_config, cmd):
    test_util.test_logger("DEBUG.execute_in_vm_console:%s" %(cmd))
    try:
        import pexpect
    except:
        test_util.test_logger('pexpect not installed')
        return ''

    try:
        ssh_cmd = "sshpass -p %s ssh -t -t -t %s" % (os.environ.get('scenarioHostPassword'), host_ip)
        child = pexpect.spawn("%s virsh console %s" % (ssh_cmd, vm_name))
        child.expect('Escape character is', timeout=20)
    except:
        ssh_cmd = "sshpass -p %s ssh -t -t -t %s" % ("password", host_ip)
        child = pexpect.spawn("%s virsh console %s" % (ssh_cmd, vm_name))
        child.expect('Escape character is', timeout=20)
    child.send('\n')

    i = child.expect(['login:', '[#\$] ', '~]# '], timeout=10)
    if i == 0:
        test_util.test_logger('login to guest vm')
        child.send("%s\n" % (vm_config.imageUsername_))
        child.expect('Password:', timeout=10)
        child.send("%s\n" % (vm_config.imagePassword_))
        child.expect('[#\$] ', timeout=10)
    elif i == 1 or i == 2:
        test_util.test_logger('already login guest vm')
    child.send("%s\n" % (cmd))
    child.expect(['[#\$] ', '~]# '], timeout=10)
    child.close()
    return child.before
#    check_ret_cmd = 'echo RET=$?'
#    pexpect.send(cmd)
    

def setup_vm_no_password(vm_inv, vm_config, deploy_config):
    vm_ip = test_lib.lib_get_vm_nic_by_l3(vm_inv, vm_inv.defaultL3NetworkUuid).ip
#    ssh.scp_file(os.environ.get('scenarioPriKey'), '/root/.ssh/id_rsa', vm_ip, vm_config.imageUsername_, vm_config.imagePassword_)
#    ssh.scp_file(os.environ.get('scenarioPubKey'), '/root/.ssh/authorized_keys', vm_ip, vm_config.imageUsername_, vm_config.imagePassword_)
    ssh.scp_file('/home/id_rsa', '/root/.ssh/id_rsa', vm_ip, vm_config.imageUsername_, vm_config.imagePassword_)
    ssh.scp_file('/home/id_rsa.pub', '/root/.ssh/authorized_keys', vm_ip, vm_config.imageUsername_, vm_config.imagePassword_)
    cmd = 'chmod go-rwx /root/.ssh/authorized_keys /root/.ssh/id_rsa'
    ssh.execute(cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, 22)
    cmd = "sed -i 's/.*StrictHostKeyChecking.*$/StrictHostKeyChecking no/g' /etc/ssh/ssh_config"
    ssh.execute(cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, 22)

def ensure_nic_all_have_cfg(vm_inv, vm_config, num_of_cfg):
    vm_ip = test_lib.lib_get_vm_nic_by_l3(vm_inv, vm_inv.defaultL3NetworkUuid).ip
    cmd = 'cp /etc/sysconfig/network-scripts/ifcfg-eth0 /root/ifcfg-eth0;sync;sync;sync'
    ssh.execute(cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, 22)

    for num_idx in range(num_of_cfg-1): 
        cmd = 'cp /root/ifcfg-eth0 /etc/sysconfig/network-scripts/ifcfg-eth%s;sync;sync;sync' %(str(num_idx+1))
        test_util.test_logger("@@@DEBUG@@@:cmd=%s" %(cmd))
        ssh.execute(cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, 22)

        cmd = "sed -i 's:eth0:eth%s:g' /etc/sysconfig/network-scripts/ifcfg-eth%s;sync;sync;sync" %((str(num_idx+1),)*2)
        test_util.test_logger("@@@DEBUG@@@:cmd=%s" %(cmd))
        ssh.execute(cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, 22)
    

def setup_2ha_mn_vm(zstack_management_ip, vm_inv, vm_config, deploy_config):
    vm_ip = test_lib.lib_get_vm_nic_by_l3(vm_inv, vm_inv.defaultL3NetworkUuid).ip
    cmd = 'hostnamectl set-hostname %s' % (vm_ip.replace('.', '-'))
    ssh.execute(cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, 22)

    udev_config = ''
    change_nic_back_cmd = ''
    nic_id = 0
    modify_cfg = []
    modify_cfg.append(r"cp /etc/sysconfig/network-scripts/ifcfg-eth0 /root/ifcfg-eth0;sync;sync;sync")
    for l3network in xmlobject.safe_list(vm_config.l3Networks.l3Network):
        if hasattr(l3network, 'scenl3NetworkRef'):
            for scenl3networkref in xmlobject.safe_list(l3network.scenl3NetworkRef):
                conf = res_ops.gen_query_conditions('name', '=', '%s' % (scenl3networkref.text_))
                l3_network = query_resource(zstack_management_ip, res_ops.L3_NETWORK, conf).inventories[0]
                for vmnic in vm_inv.vmNics:
                    if vmnic.l3NetworkUuid == l3_network.uuid:
                        vmnic_mac = vmnic.mac
                        break
        else:
            for vmnic in vm_inv.vmNics:
                if vmnic.l3NetworkUuid == l3network.uuid_:
                    vmnic_mac = vmnic.mac
                    break
        nic_name = "zsn%s" % (nic_id)
        udev_config = udev_config + r'\\nACTION==\"add\", SUBSYSTEM==\"net\", DRIVERS==\"?*\", ATTR{type}==\"1\", ATTR{address}==\"%s\", NAME=\"%s\"' % (vmnic_mac, nic_name)
        modify_cfg.append(r"rm -rf /etc/sysconfig/network-scripts/ifcfg-eth%s || True" %(nic_id))
        modify_cfg.append(r"cp /root/ifcfg-eth0 /etc/sysconfig/network-scripts/ifcfg-zsn%s" %(nic_id))
        modify_cfg.append(r"sed -i 's:eth0:zsn%s:g' /etc/sysconfig/network-scripts/ifcfg-zsn%s" %(nic_id, nic_id))
        nic_id += 1

    cmd = 'echo -e %s > /etc/udev/rules.d/70-persistent-net.rules' % (udev_config)
    ssh.execute(cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, 22)
    modify_cfg.append(r"sleep 1")
    modify_cfg.append(r"sync")
    modify_cfg.append(r"fsfreeze -f /")
    modify_cfg.append(r"sync")
    modify_cfg.append(r"sync")

    for cmd in modify_cfg:
        test_util.test_logger("execute cmd: %s" %(cmd))
        ret, output, stderr = ssh.execute(cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, 22)
        if int(ret) != 0:
            test_util.test_fail("cmd %s failed" %(cmd))


    # NOTE: need to make filesystem in sync in VM before cold stop VM
    reboot_vm(zstack_management_ip, vm_inv.uuid)
    if not wait_for_target_vm_retry_after_reboot(zstack_management_ip, vm_ip, vm_inv.uuid):
        test_util.test_fail('VM:%s can not be accessible as expected' %(vm_ip))

    for l3network in xmlobject.safe_list(vm_config.l3Networks.l3Network):
        if hasattr(l3network, 'l2NetworkRef'):
            for l2networkref in xmlobject.safe_list(l3network.l2NetworkRef):
                nic_name = get_ref_l2_nic_name(l2networkref.text_, deploy_config)
                if nic_name.find('.') >= 0:
                    vlan = nic_name.split('.')[1]
                    test_util.test_logger('[vm:] %s %s is created.' % (vm_ip, nic_name.replace("eth", "zsn")))
                    cmd = 'vconfig add %s %s' % (nic_name.split('.')[0].replace("eth", "zsn"), vlan)
                    ssh.execute(cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, 22)

    #host = get_deploy_host(vm_config.hostRef.text_, deploy_config)
    #if hasattr(host, 'port_') and host.port_ != '22':
    #    cmd = "sed -i 's/#Port 22/Port %s/g' /etc/ssh/sshd_config && iptables -I INPUT -p tcp -m tcp --dport %s -j ACCEPT && service sshd restart" % (host.port_, host.port_)
    #    ssh.execute(cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, 22)
    #else:
    #    host.port_ = '22'

    #if host.username_ != 'root':
    #    cmd = 'adduser %s && echo -e %s\\\\n%s | passwd %s' % (host.username_, host.password_, host.password_, host.username_)
    #    ssh.execute(cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, int(host.port_))
    #    cmd = "echo '%s        ALL=(ALL)       NOPASSWD: ALL' >> /etc/sudoers" % (host.username_)
    #    ssh.execute(cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, int(host.port_))


def setup_host_vm(zstack_management_ip, vm_inv, vm_config, deploy_config):
    vm_ip = test_lib.lib_get_vm_nic_by_l3(vm_inv, vm_inv.defaultL3NetworkUuid).ip
    cmd = 'hostnamectl set-hostname %s' % (vm_ip.replace('.', '-'))
    ssh.execute(cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, 22)

    udev_config = ''
    change_nic_back_cmd = ''
    nic_id = 0
    modify_cfg = []
    modify_cfg.append(r"cp /etc/sysconfig/network-scripts/ifcfg-eth0 /root/ifcfg-eth0;sync;sync;sync")
    for l3network in xmlobject.safe_list(vm_config.l3Networks.l3Network):
        if hasattr(l3network, 'scenl3NetworkRef'):
            for scenl3networkref in xmlobject.safe_list(l3network.scenl3NetworkRef):
                conf = res_ops.gen_query_conditions('name', '=', '%s' % (scenl3networkref.text_))
                l3_network = query_resource(zstack_management_ip, res_ops.L3_NETWORK, conf).inventories[0]
                for vmnic in vm_inv.vmNics:
                    if vmnic.l3NetworkUuid == l3_network.uuid:
                        vmnic_mac = vmnic.mac
                        break
        else:
            for vmnic in vm_inv.vmNics:
                if vmnic.l3NetworkUuid == l3network.uuid_:
                    vmnic_mac = vmnic.mac
                    break
        #nic_name = None
        #if hasattr(l3network, 'l2NetworkRef'):
        #    for l2networkref in xmlobject.safe_list(l3network.l2NetworkRef):
        #        nic_name = get_ref_l2_nic_name(l2networkref.text_, deploy_config)
        #        if nic_name.find('.') < 0:
        #            break
        #if nic_name == None:
            #nic_name = "eth%s" % (nic_id)
        nic_name = "zsn%s" % (nic_id)
        udev_config = udev_config + r'\\nACTION==\"add\", SUBSYSTEM==\"net\", DRIVERS==\"?*\", ATTR{type}==\"1\", ATTR{address}==\"%s\", NAME=\"%s\"' % (vmnic_mac, nic_name)
        modify_cfg.append(r"rm -rf /etc/sysconfig/network-scripts/ifcfg-eth%s || True" %(nic_id))
        modify_cfg.append(r"cp /root/ifcfg-eth0 /etc/sysconfig/network-scripts/ifcfg-zsn%s" %(nic_id))
        modify_cfg.append(r"sed -i 's:eth0:zsn%s:g' /etc/sysconfig/network-scripts/ifcfg-zsn%s" %(nic_id, nic_id))
        nic_id += 1

    cmd = 'echo -e %s > /etc/udev/rules.d/70-persistent-net.rules' % (udev_config)
    ssh.execute(cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, 22)
    modify_cfg.append(r"sleep 1")
    modify_cfg.append(r"sync")
    modify_cfg.append(r"sync")
    modify_cfg.append(r"sync")

    for cmd in modify_cfg:
        test_util.test_logger("execute cmd: %s" %(cmd))
        ret, output, stderr = ssh.execute(cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, 22)
        if int(ret) != 0:
            test_util.test_fail("cmd %s failed" %(cmd))


    # NOTE: need to make filesystem in sync in VM before cold stop VM
    reboot_vm(zstack_management_ip, vm_inv.uuid)

    if not wait_for_target_vm_retry_after_reboot(zstack_management_ip, vm_ip, vm_inv.uuid):
        test_util.test_fail('VM:%s can not be accessible as expected' %(vm_ip))

    for l3network in xmlobject.safe_list(vm_config.l3Networks.l3Network):
        if hasattr(l3network, 'l2NetworkRef'):
            for l2networkref in xmlobject.safe_list(l3network.l2NetworkRef):
                nic_name = get_ref_l2_nic_name(l2networkref.text_, deploy_config)
                if nic_name.find('.') >= 0:
                    vlan = nic_name.split('.')[1]
                    test_util.test_logger('[vm:] %s %s is created.' % (vm_ip, nic_name.replace("eth", "zsn")))
                    cmd = 'vconfig add %s %s' % (nic_name.split('.')[0].replace("eth", "zsn"), vlan)
                    ssh.execute(cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, 22)

    host = get_deploy_host(vm_config.hostRef.text_, deploy_config)
    if host:
        if hasattr(host, 'port_') and host.port_ != '22':
            cmd = "sed -i 's/#Port 22/Port %s/g' /etc/ssh/sshd_config && iptables -I INPUT -p tcp -m tcp --dport %s -j ACCEPT && service sshd restart" % (host.port_, host.port_)
            ssh.execute(cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, 22)
        else:
            host.port_ = '22'

        if host.username_ != 'root':
            cmd = 'adduser %s && echo -e %s\\\\n%s | passwd %s' % (host.username_, host.password_, host.password_, host.username_)
            ssh.execute(cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, int(host.port_))
            cmd = "echo '%s        ALL=(ALL)       NOPASSWD: ALL' >> /etc/sudoers" % (host.username_)
            ssh.execute(cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, int(host.port_))

def recover_after_host_vm_reboot(vm_inv, vm_config, deploy_config):
    vm_ip = test_lib.lib_get_vm_nic_by_l3(vm_inv, vm_inv.defaultL3NetworkUuid).ip
    for l3network in xmlobject.safe_list(vm_config.l3Networks.l3Network):
        if hasattr(l3network, 'l2NetworkRef'):
            for l2networkref in xmlobject.safe_list(l3network.l2NetworkRef):
                nic_name = get_ref_l2_nic_name(l2networkref.text_, deploy_config)
                if nic_name.find('.') >= 0:
                    vlan = nic_name.split('.')[1]
                    test_util.test_logger('[vm:] %s %s is created.' % (vm_ip, nic_name.replace("eth", "zsn")))
                    cmd = 'vconfig add %s %s' % (nic_name.split('.')[0].replace("eth", "zsn"), vlan)
                    try:
                        ssh.execute(cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, 22)
                    except:
                        pass


#def get_mn_ha_nfs_url(scenario_config, scenario_file, deploy_config, use_nas=True):
def get_mn_ha_nfs_url(scenario_config, scenario_file, deploy_config, use_nas=False):
    for host in xmlobject.safe_list(scenario_config.deployerConfig.hosts.host):
        for vm in xmlobject.safe_list(host.vms.vm):
            if hasattr(vm, 'primaryStorageRef'):
            #if xmlobject.has_element(vm, 'primaryStorageRef'):
	        for primaryStorageRef in xmlobject.safe_list(vm.primaryStorageRef):
	            for zone in xmlobject.safe_list(deploy_config.zones.zone):
	                if primaryStorageRef.type_ == 'nfs':
	                    for nfsPrimaryStorage in xmlobject.safe_list(zone.primaryStorages.nfsPrimaryStorage):
	                        if primaryStorageRef.text_ == nfsPrimaryStorage.name_:
                                    if use_nas != True:
	                                return nfsPrimaryStorage.url_
                                    else:
	                                return create_and_clean_nfs_sub_url_in_server()
    return None

def create_and_clean_nfs_sub_url_in_server():
    woodpecker_vm_ip = shell.call("ip r | grep src | head -1 | awk '{print $NF}'").strip()
    shell.call("mkdir -p /opt/mnt_nfs")
    shell.call("mount 172.20.1.7:/mnt/test /opt/mnt_nfs")
    nfs_sub_folder = "/opt/mnt_nfs/%s" % woodpecker_vm_ip
    shell.call("mkdir -p %s" % nfs_sub_folder)
    shell.call("rm -rf %s/mnvm.*" % nfs_sub_folder)
    shell.call("umount /opt/mnt_nfs")
    nfs_sub_url = "172.20.1.7:/mnt/test/" + woodpecker_vm_ip
    return nfs_sub_url
    

def get_nfs_ip_for_net_sep(scenarioConfig, virtual_host_ip, nfs_ps_name):
    zstack_management_ip = scenarioConfig.basicConfig.zstackManagementIp.text_

    storageNetworkUuid = None
    for host in xmlobject.safe_list(scenarioConfig.deployerConfig.hosts.host):
        for vm in xmlobject.safe_list(host.vms.vm):
            for l3Network in xmlobject.safe_list(vm.l3Networks.l3Network):
                test_util.test_logger("nfs_ps_name=:%s" %(nfs_ps_name))
                if xmlobject.has_element(l3Network, 'primaryStorageRef'):
                #if xmlobject.has_element(l3Network, 'primaryStorageRef') and l3Network.primaryStorageRef.text_ == nfs_ps_name:
                    test_util.test_logger("ps_name_in_config:%s" %(l3Network.primaryStorageRef.text_))
                    storageNetworkUuid = l3Network.uuid_
                    cond = res_ops.gen_query_conditions('vmNics.ip', '=', virtual_host_ip)
                    vm_inv_nics = query_resource(zstack_management_ip, res_ops.VM_INSTANCE, cond).inventories[0].vmNics
                    if len(vm_inv_nics) < 2:
                        test_util.test_fail("virtual host:%s not has 2+ nics as expected, incorrect for seperate network case" %(virtual_host_ip))
                    for vm_inv_nic in vm_inv_nics:
                        test_util.test_logger("network_uuid:%s:%s" %(vm_inv_nic.l3NetworkUuid, storageNetworkUuid))
                        if vm_inv_nic.l3NetworkUuid == storageNetworkUuid:
                            return vm_inv_nic.ip

    return None

def get_vm_gateway(vm_ip, vm_config):
    cmd = "ip r|head -n 1|awk '{print $3}'"
    ret, output, stderr = ssh.execute(cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, 22)
    return output


def setup_mn_host_vm(scenario_config, scenario_file, deploy_config, vm_inv, vm_config):
    vm_ip = test_lib.lib_get_vm_nic_by_l3(vm_inv, vm_inv.defaultL3NetworkUuid).ip
    vm_nic = os.environ.get('nodeNic').replace("eth", "zsn")
    vm_netmask = os.environ.get('nodeNetMask')
    vm_gateway = os.environ.get('nodeGateway')
    if os.path.basename(os.environ.get('WOODPECKER_SCENARIO_CONFIG_FILE')).strip() == "scenario-config-vpc-ceph-3-sites.xml":
        vm_gateway = get_vm_gateway(vm_ip, vm_config)
        vm_netmask = "255.255.255.0"
        cmd = '/usr/local/bin/zs-network-setting -b %s %s %s %s' % (vm_nic, vm_ip, vm_netmask, vm_gateway)
        ssh.execute(cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, 22)
    else:
        cmd = '/usr/local/bin/zs-network-setting -b %s %s %s %s' % (vm_nic, vm_ip, vm_netmask, vm_gateway)
        ssh.execute(cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, 22)
    mn_ha_storage_type = get_mn_ha_storage_type(scenario_config, scenario_file, deploy_config)
    if mn_ha_storage_type == "nfs":
        nfs_url = get_mn_ha_nfs_url(scenario_config, scenario_file, deploy_config)
        test_util.test_logger("setup_mn_host.nfs_branch")
        nfsIP = nfs_url.split(':')[0]
        nfsPath = nfs_url.split(':')[1]
        vm_net_uuids_lst = []
        for vmNic in vm_inv.vmNics:
            vm_net_uuids_lst.append(vmNic.l3NetworkUuid)
        vm_net_uuids_lst.remove(vm_inv.defaultL3NetworkUuid)
        if vm_net_uuids_lst:
            nfs_network_uuid = vm_net_uuids_lst[0]
            nfs_vm_ip = test_lib.lib_get_vm_nic_by_l3(vm_inv, nfs_network_uuid).ip
            if test_lib.lib_cur_cfg_is_a_and_b(["test-config-vyos-flat-dhcp-nfs-sep-pub-man.xml", "test-config-vyos-flat-dhcp-nfs-mul-net-pubs.xml"], \
                                               ["scenario-config-nfs-sep-man.xml"]):
                test_util.test_logger("setup_mn_host.nfs_branch.sep_man")
                nfs_vm_nic = os.environ.get('storNic').replace("eth", "zsn")
                nfs_vm_netmask = os.environ.get('manNetMask')
                nfs_vm_gateway = os.environ.get('manGateway')
            elif test_lib.lib_cur_cfg_is_a_and_b(["test-config-vyos-flat-dhcp-nfs-sep-pub-man.xml", "test-config-vyos-flat-dhcp-nfs-mul-net-pubs.xml"], \
                                                 ["scenario-config-nfs-sep-pub.xml"]):
                test_util.test_logger("setup_mn_host.nfs_branch.mul_net_pubs")
                nfs_url = get_mn_ha_nfs_url(scenario_config, scenario_file, deploy_config, False)
                test_util.test_logger("setup_mn_host.nfs_branch.mul_net_pubs.after_get_mn_ha_nfs_url")
                nfsIP = nfs_url.split(':')[0]
                nfsPath = nfs_url.split(':')[1]
                nfs_vm_nic = os.environ.get('storNic').replace("eth", "zsn")
                nfs_vm_netmask = os.environ.get('manNetMask')
                nfs_vm_gateway = os.environ.get('manGateway')
                test_util.test_logger("setup_mn_host.nfs_branch.mul_net_pubs.before_get_nfs_ip_for_net_sep")
                nfsIP = get_nfs_ip_for_net_sep(scenario_config, nfsIP, nfsPath)
                test_util.test_logger("setup_mn_host.nfs_branch.mul_net_pubs.after_get_nfs_ip_for_net_sep")
            elif test_lib.lib_cur_cfg_is_a_and_b(["test-config-vyos-nfs.xml"], \
                                                 ["scenario-config-storage-separate-nfs.xml"]):
                test_util.test_logger("setup_mn_host.nfs_branch.sep_nfs_branch")
                nfs_vm_nic = os.environ.get('storNic').replace("eth", "zsn")
                nfs_vm_netmask = os.environ.get('storNetMask')
                nfs_vm_gateway = os.environ.get('storGateway')
            else:
                test_util.test_fail("not supported nfs testconfig and scenario combination")
        
            nfs_cmd = '/usr/local/bin/zs-network-setting -b %s %s %s %s' % (nfs_vm_nic, nfs_vm_ip, nfs_vm_netmask, nfs_vm_gateway)
            test_util.test_logger("nfs_cmd=%s" %(nfs_cmd))
            ssh.execute(nfs_cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, 22)
            #TODO: should dynamically change gw followed config.json, but currently there is only one case, thus always change 
            #default gw to public network gw
            set_default_gw_cmd = "route del default gw %s && route add default gw %s" %(nfs_vm_gateway, vm_gateway)
            test_util.test_logger("set_default_gw_cmd=%s" %(set_default_gw_cmd))
            ssh.execute(set_default_gw_cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, 22)

        #TODO: should make image folder configarable
        cmd = 'mkdir -p /storage'
        test_util.test_logger("cmd=%s" %(cmd))
        ssh.execute(cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, 22)

        #cmd = 'echo mount %s:%s /storage >> /etc/rc.local' % (nfsIP, nfsPath)
        #cmd = 'echo mount -t nfs -o rw,soft,timeo=30,retry=3 %s:%s /storage >> /etc/rc.local' % (nfsIP, nfsPath)
        cmd = 'echo mount -t nfs -o rw,soft,timeo=20,retry=10,retrans=6 %s:%s /storage >> /etc/rc.local' % (nfsIP, nfsPath)
        test_util.test_logger("cmd=%s" %(cmd))
        ssh.execute(cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, 22)

        cmd = 'chmod a+x /etc/rc.local /etc/rc.d/rc.local'
        test_util.test_logger("cmd=%s" %(cmd))
        ssh.execute(cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, 22)

        #cmd = 'mount %s:%s /storage' % (nfsIP, nfsPath)
        #cmd = 'mount -t nfs -o rw,soft,timeo=30,retry=3 %s:%s /storage' % (nfsIP, nfsPath)
        cmd = 'mount -t nfs -o rw,soft,timeo=20,retry=10,retrans=6 %s:%s /storage' % (nfsIP, nfsPath)
        test_util.test_logger("cmd=%s" %(cmd))
        ssh.execute(cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, 22)

    elif mn_ha_storage_type == "ceph":
        vm_net_uuids_lst = []
        for vmNic in vm_inv.vmNics:
            vm_net_uuids_lst.append(vmNic.l3NetworkUuid)
        vm_net_uuids_lst.remove(vm_inv.defaultL3NetworkUuid)
        if vm_net_uuids_lst:
            ceph_network_uuid = vm_net_uuids_lst[0]
            ceph_vm_ip = test_lib.lib_get_vm_nic_by_l3(vm_inv, ceph_network_uuid).ip
            if test_lib.lib_cur_cfg_is_a_and_b(["test-config-vyos-ceph-3-nets-sep.xml"], \
                                               ["scenario-config-ceph-sep-man.xml", \
                                                "scenario-config-ceph-sep-pub.xml", \
                                                "scenario-config-ceph-3-nets-sep.xml"]):
                ceph_vm_nic = os.environ.get('storNic').replace("eth", "zsn")
                ceph_vm_netmask = os.environ.get('manNetMask')
                ceph_vm_gateway = os.environ.get('manGateway')
            elif test_lib.lib_cur_cfg_is_a_and_b(["test-config-vyos-nonmon-ceph.xml"], \
                                                 [ #"scenario-config-separate-ceph.xml", \
                                                "scenario-config-storage-separate-ceph.xml"]):
                ceph_vm_nic = os.environ.get('storNic').replace("eth", "zsn")
                ceph_vm_netmask = os.environ.get('storNetMask')
                ceph_vm_gateway = os.environ.get('storGateway')
                #for vm_l3network in xmlobject.safe_list(vm_config.l3Networks.l3Network):
                #    if vm_l3network.uuid_ == os.environ.get('vmManageL3Uuid'):
                #        ceph_vm_ip = test_lib.lib_get_vm_nic_by_l3(vm_inv, vm_l3network.uuid_).ip
                #        ceph_vm_nic = os.environ.get('storNic').replace("eth", "zsn")
                #        ceph_vm_netmask = os.environ.get('manNetMask')
                #        ceph_vm_gateway = os.environ.get('manGateway')
                #    elif vm_l3network.uuid_ == os.environ.get('vmStorageL3Uuid'):
                #        ceph_vm_ip = test_lib.lib_get_vm_nic_by_l3(vm_inv, vm_l3network.uuid_).ip
                #        ceph_vm_nic = os.environ.get('fstrStorNic').replace("eth", "zsn")
                #        ceph_vm_netmask = os.environ.get('storNetMask')
                #        ceph_vm_gateway = os.environ.get('storGateway')
                #    else:
                #        test_util.test_logger("@@@BUG@@@ vm.uuid=%s, but vmManageL3Uuid=%s, vmStorageL3Uuid=%s" %(vm_l3network.uuid_, os.environ.get('vmManageL3Uuid'), os.environ.get('vmStorageL3Uuid')))
                #        continue

                #    ceph_cmd = '/usr/local/bin/zs-network-setting -b %s %s %s %s' % (ceph_vm_nic, ceph_vm_ip, ceph_vm_netmask, ceph_vm_gateway)
                #    test_util.test_logger("%s" %(ceph_cmd))
                #    ssh.execute(ceph_cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, 22)

                #set_default_gw_cmd = "route del default && route add default gw %s" %(vm_gateway)
                #ssh.execute(set_default_gw_cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, 22)
            else:
                test_util.test_fail("not supported ceph testconfig and scenario combination")
        

            if os.path.basename(os.environ.get('WOODPECKER_SCENARIO_CONFIG_FILE')).strip() == "scenario-config-vpc-ceph-3-sites.xml":
                pass
            elif os.path.basename(os.environ.get('WOODPECKER_SCENARIO_CONFIG_FILE')).strip() == "scenario-config-storage-separate-ceph.xml":
                #ensure_set_ip_to_bridge(vm_ip, "zsn0", vm_inv, vm_config, scenario_config)

                ceph_cmd = '/usr/local/bin/zs-network-setting -b %s %s %s %s' % (ceph_vm_nic, ceph_vm_ip, ceph_vm_netmask, ceph_vm_gateway)
                ssh.execute(ceph_cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, 22)

                set_default_gw_cmd = "route del default && route add default gw %s" %(vm_gateway)
                ssh.execute(set_default_gw_cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, 22)

            else:
                ceph_cmd = '/usr/local/bin/zs-network-setting -b %s %s %s %s' % (ceph_vm_nic, ceph_vm_ip, ceph_vm_netmask, ceph_vm_gateway)
                ssh.execute(ceph_cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, 22)

                #TODO: should dynamically change gw followed config.json, but currently there is only one case, thus always change 
                #default gw to public network gw
                set_default_gw_cmd = "route del default && route add default gw %s" %(vm_gateway)
                ssh.execute(set_default_gw_cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, 22)
        
    elif mn_ha_storage_type == "fusionstor":
        if test_lib.lib_cur_cfg_is_a_and_b(["test-config-vyos-fusionstor-3-nets-sep.xml"], ["scenario-config-fusionstor-3-nets-sep.xml"]):
            for vm_l3network in xmlobject.safe_list(vm_config.l3Networks.l3Network):
                if vm_l3network.uuid_ == os.environ.get('vmManageL3Uuid'):
                    fstor_vm_ip = test_lib.lib_get_vm_nic_by_l3(vm_inv, vm_l3network.uuid_).ip
                    fstor_vm_nic = os.environ.get('storNic').replace("eth", "zsn")
                    fstor_vm_netmask = os.environ.get('manNetMask')
                    fstor_vm_gateway = os.environ.get('manGateway')
                elif vm_l3network.uuid_ == os.environ.get('vmStorageL3Uuid'):
                    fstor_vm_ip = test_lib.lib_get_vm_nic_by_l3(vm_inv, vm_l3network.uuid_).ip
                    fstor_vm_nic = os.environ.get('fstrStorNic').replace("eth", "zsn")
                    fstor_vm_netmask = os.environ.get('storNetMask')
                    fstor_vm_gateway = os.environ.get('storGateway')
                else:
                    test_util.test_logger("@@@BUG@@@ vm.uuid=%s, but vmManageL3Uuid=%s, vmStorageL3Uuid=%s" %(vm_l3network.uuid_, os.environ.get('vmManageL3Uuid'), os.environ.get('vmStorageL3Uuid')))
                    continue

                fstor_cmd = '/usr/local/bin/zs-network-setting -b %s %s %s %s' % (fstor_vm_nic, fstor_vm_ip, fstor_vm_netmask, fstor_vm_gateway)
                test_util.test_logger("%s" %(fstor_cmd))
                ssh.execute(fstor_cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, 22)
        else:
            test_util.test_fail("not supported fusionstor testconfig and scenario combination")
            
        set_default_gw_cmd = "route del default && route add default gw %s" %(vm_gateway)
        ssh.execute(set_default_gw_cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, 22)


def ensure_set_ip_to_bridge(vm_ip, nic, vm_inv, vm_config, scenario_config):
 
    zstack_management_ip = scenario_config.basicConfig.zstackManagementIp.text_

    cond = res_ops.gen_query_conditions('uuid', '=', vm_inv.hostUuid)
    host_inv = query_resource(zstack_management_ip, res_ops.HOST, cond).inventories[0]

    bridge = "br_" + nic
    cmd = "ip a del %s/16 dev %s;ip a add %s/16 dev %s" %(vm_ip, nic, vm_ip, bridge)
    test_util.test_logger("cmd=%s" %(cmd))
    execute_in_vm_console(zstack_management_ip, host_inv.managementIp, vm_inv.uuid, vm_config, cmd)

    if not test_lib.lib_wait_target_up(vm_ip, '22', 120):
        #cmd = r"brif_not_null=$(brctl show|grep br_zsn0|awk '{print $4}'); [ -z \"$brif_not_null\" ] && brctl addif br_zsn0 zsn0"
        cmd = r"brif_not_null=$(brctl show|grep %s|awk '{print $4}'); [ -z \"$brif_not_null\" ] && brctl addif %s %s" %(bridge, bridge, nic)
        test_util.test_logger("cmd=%s" %(cmd))
        execute_in_vm_console(zstack_management_ip, host_inv.managementIp, vm_inv.uuid, vm_config, cmd)


def get_backup_storage_type(deploy_config, bs_name):
    for backupStorage in deploy_config.backupStorages.get_child_node_as_list('sftpBackupStorage'):
        if backupStorage.name_ == bs_name:
            return 'sftp'
    for backupStorage in deploy_config.backupStorages.get_child_node_as_list('imageStoreBackupStorage'):
        if backupStorage.name_ == bs_name:
            return 'imagestore'
    for backupStorage in deploy_config.backupStorages.get_child_node_as_list('cephBackupStorage'):
        if backupStorage.name_ == bs_name:
            return 'ceph'
    for backupStorage in deploy_config.backupStorages.get_child_node_as_list('xskycephBackupStorage'):
        if backupStorage.name_ == bs_name:
            return 'xsky'
    for backupStorage in deploy_config.backupStorages.get_child_node_as_list('fusionstorBackupStorage'):
        if backupStorage.name_ == bs_name:
            return 'fusionstor'

    return None

def get_primary_storage_type(deploy_config, ps_name):
    for zone in xmlobject.safe_list(deploy_config.zones.zone):
        for primaryStorage in zone.primaryStorages.get_child_node_as_list('cephPrimaryStorage'):
            if primaryStorage.name_ == ps_name:
                return 'ceph'
        for primaryStorage in zone.primaryStorages.get_child_node_as_list('xskycephPrimaryStorage'):
            if primaryStorage.name_ == ps_name:
                return 'xsky'
        for primaryStorage in zone.primaryStorages.get_child_node_as_list('fusionPrimaryStorage'):
            if primaryStorage.name_ == ps_name:
                return 'fusionstor'
        for primaryStorage in zone.primaryStorages.get_child_node_as_list('localPrimaryStorage'):
            if primaryStorage.name_ == ps_name:
                return 'local'
        for primaryStorage in zone.primaryStorages.get_child_node_as_list('nfsPrimaryStorage'):
            if primaryStorage.name_ == ps_name:
                return 'nfs'
        for primaryStorage in zone.primaryStorages.get_child_node_as_list('sharedMountPointPrimaryStorage'):
            if primaryStorage.name_ == ps_name:
                return 'smp'
        for primaryStorage in zone.primaryStorages.get_child_node_as_list('zbsPrimaryStorage'):
            if primaryStorage.name_ == ps_name:
                return 'zbs'
        for primaryStorage in zone.primaryStorages.get_child_node_as_list('aliyunNASPrimaryStorage'):
            if primaryStorage.name_ == ps_name:
                return 'nas'
        for primaryStorage in zone.primaryStorages.get_child_node_as_list('aliyunEBSPrimaryStorage'):
            if primaryStorage.name_ == ps_name:
                return 'ebs'

    return None


def setup_backupstorage_vm(vm_inv, vm_config, deploy_config):
    vm_ip = test_lib.lib_get_vm_nic_by_l3(vm_inv, vm_inv.defaultL3NetworkUuid).ip
    if hasattr(vm_config, 'hostRef'):
        host = get_deploy_host(vm_config.hostRef.text_, deploy_config)
        if not hasattr(host, 'port_') or host.port_ == '22':
            host_port = '22'
        else:
            host_port = host.port_
    else:
        # TODO: sftp may setup with non-root or non-default user/password port
        host_port = '22'

    for backupStorageRef in xmlobject.safe_list(vm_config.backupStorageRef):
        print backupStorageRef.text_
        backup_storage_type = get_backup_storage_type(deploy_config, backupStorageRef.text_)
        if backup_storage_type == 'sftp':
            for sftpBackupStorage in xmlobject.safe_list(deploy_config.backupStorages.sftpBackupStorage):
                if backupStorageRef.text_ == sftpBackupStorage.name_:
                    # TODO: sftp may setup with non-root or non-default user/password port
                    test_util.test_logger('[vm:] %s setup sftp service.' % (vm_ip))
                    cmd = "mkdir -p %s" % (sftpBackupStorage.url_)
                    ssh.execute(cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, int(host_port))
                    return
        if backup_storage_type == 'imagestore':
            for imageStoreBackupStorage in xmlobject.safe_list(deploy_config.backupStorages.imageStoreBackupStorage):
                if backupStorageRef.text_ == imageStoreBackupStorage.name_:
                    # TODO: image store may setup with non-root or non-default user/password port
                    test_util.test_logger('[vm:] %s setup image store service.' % (vm_ip))
                    cmd = "mkdir -p %s" % (imageStoreBackupStorage.url_)
                    ssh.execute(cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, int(host_port))
                    return

SMP_SERVER_IP = None
def setup_primarystorage_vm(vm_inv, vm_config, deploy_config):
    global SMP_SERVER_IP
    nas_mt = None
    vm_ip = test_lib.lib_get_vm_nic_by_l3(vm_inv, vm_inv.defaultL3NetworkUuid).ip
    if hasattr(vm_config, 'hostRef'):
        host = get_deploy_host(vm_config.hostRef.text_, deploy_config)
        if not hasattr(host, 'port_') or host.port_ == '22':
            host_port = '22'
        else:
            host_port = host.port_
    else:
        host_port = '22'

    for primaryStorageRef in xmlobject.safe_list(vm_config.primaryStorageRef):
        #the type is get from deploy, here we also need to define the condition based on scenario config
        if primaryStorageRef.type_ == 'ocfs2smp':
            #directly return when find the current config is for ocfs2
            continue
        for zone in xmlobject.safe_list(deploy_config.zones.zone):
            primary_storage_type = get_primary_storage_type(deploy_config, primaryStorageRef.text_)
            if primary_storage_type == 'nfs':
                for nfsPrimaryStorage in xmlobject.safe_list(zone.primaryStorages.nfsPrimaryStorage):
                    if primaryStorageRef.text_ == nfsPrimaryStorage.name_:
                        test_util.test_logger('[vm:] %s setup nfs service.' % (vm_ip))
                        # TODO: multiple NFS PS may refer to same host's different DIR^M
                        nfsPath = nfsPrimaryStorage.url_.split(':')[1]
                        cmd = "echo '%s *(rw,sync,no_root_squash)' > /etc/exports" % (nfsPath)
                        ssh.execute(cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, int(host_port))
                        cmd = "mkdir -p %s && service rpcbind restart && service nfs restart" % (nfsPath)
                        ssh.execute(cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, int(host_port))
                        cmd = "iptables -w 20 -I INPUT -p tcp -m tcp --dport 2049 -j ACCEPT && iptables -w 20 -I INPUT -p udp -m udp --dport 2049 -j ACCEPT"
                        ssh.execute(cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, int(host_port))
                        if primary_storage_type == 'nas':
                            nas_mt = vm_ip
                        continue
            elif primary_storage_type == 'smp':
                for smpPrimaryStorage in xmlobject.safe_list(zone.primaryStorages.sharedMountPointPrimaryStorage):
                    if primaryStorageRef.text_ == smpPrimaryStorage.name_:
                        test_util.test_logger('[vm:] %s setup smp service.' % (vm_ip))
                        if primaryStorageRef.type_ == 'smp':
                            if hasattr(primaryStorageRef, 'tag_') and primaryStorageRef.tag_ == "smpserver":
                                nfsPath = "/home/nfs"
                                cmd = "echo '%s *(rw,sync,no_root_squash)' > /etc/exports" % (nfsPath)
                                ssh.execute(cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, int(host_port))
                                cmd = "mkdir -p %s && service rpcbind restart && service nfs restart" % (nfsPath)
                                ssh.execute(cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, int(host_port))
                                cmd = "iptables -w 20 -I INPUT -p tcp -m tcp --dport 2049 -j ACCEPT && iptables -w 20 -I INPUT -p udp -m udp --dport 2049 -j ACCEPT"
                                ssh.execute(cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, int(host_port))
                                SMP_SERVER_IP = vm_ip
                                continue
                            else:
                                if not SMP_SERVER_IP:
                                    test_util.test_fail("smp server can't be None, SMP_SERVER_IP=%s" %(str(SMP_SERVER_IP)))
                                cmd = "mkdir -p /home/smp-ps/"
                                ssh.execute(cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, int(host_port))
                                cmd = "echo 'mount %s:/home/nfs /home/smp-ps/' >> /etc/rc.local" %(SMP_SERVER_IP)
                                ssh.execute(cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, int(host_port))
                                cmd = "chmod a+x /etc/rc.d/rc.local"
                                ssh.execute(cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, int(host_port))
                                cmd = "mount %s:/home/nfs /home/smp-ps/" %(SMP_SERVER_IP)
                                ssh.execute(cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, int(host_port))
                                continue
            elif primary_storage_type == 'nas':
                for aliyunNASPrimaryStorage in xmlobject.safe_list(zone.primaryStorages.aliyunNASPrimaryStorage):
                    if primaryStorageRef.text_ == aliyunNASPrimaryStorage.name_:
                        test_util.test_logger('[vm:] %s setup nfs service.' % (vm_ip))
                        nasPath = aliyunNASPrimaryStorage.url_.split(':')[1]
                        cmd = "echo '%s *(rw,sync,no_root_squash)' > /etc/exports" % (nasPath)
                        ssh.execute(cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, int(host_port))
                        cmd = "mkdir -p %s && service rpcbind restart && service nfs restart" % (nasPath)
                        ssh.execute(cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, int(host_port))
                        cmd = "iptables -w 20 -I INPUT -p tcp -m tcp --dport 2049 -j ACCEPT && iptables -w 20 -I INPUT -p udp -m udp --dport 2049 -j ACCEPT"
                        ssh.execute(cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, int(host_port))
                        nas_mt = vm_ip
                        continue
    if nas_mt:
        return nas_mt
    else:
        return None


def exec_cmd_in_vm(cmd, vm_ip, vm_config, raise_if_exception, host_port):
    test_util.test_logger(cmd)
    ssh.execute(cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, raise_if_exception, int(host_port))


def scp_iscsi_repo_to_host(vm_config, vm_ip):
    import commands
    status, woodpecker_ip = commands.getstatusoutput("ip addr show zsn0 | sed -n '3p' | awk '{print $2}' | awk -F / '{print $1}'")
    iscsi_repo_cfg_src = "/home/%s/zstack-internal-yum.repo" %(woodpecker_ip)
    iscsi_repo_cfg_dst = "/etc/yum.repos.d/zstack-internal-yum.repo"
    ssh.scp_file(iscsi_repo_cfg_src, iscsi_repo_cfg_dst, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_)

def setup_iscsi_target_kernel(zstack_management_ip, vm_inv, vm_config, deploy_config):
    vm_ip = test_lib.lib_get_vm_nic_by_l3(vm_inv, vm_inv.defaultL3NetworkUuid).ip
    if hasattr(vm_config, 'hostRef'):
        host = get_deploy_host(vm_config.hostRef.text_, deploy_config)
        if not hasattr(host, 'port_') or host.port_ == '22':
            host_port = '22'
        else:
            host_port = host.port_
    else:
        host_port = '22'

    cmd = "wget http://172.20.1.15/kernel-ml-4.20.3-1.el7.elrepo.x86_64.rpm"
    exec_cmd_in_vm(cmd, vm_ip, vm_config, True, host_port)

    cmd = 'rpm -ivh kernel-ml-4.20.3-1.el7.elrepo.x86_64.rpm && grub2-set-default "CentOS Linux (4.20.3-1.el7.elrepo.x86_64) 7 (Core)" && sync && sync && sync'
    exec_cmd_in_vm(cmd, vm_ip, vm_config, True, host_port)

    reboot_vm(zstack_management_ip, vm_inv.uuid)
    if not wait_for_target_vm_retry_after_reboot(zstack_management_ip, vm_ip, vm_inv.uuid):
        test_util.test_fail('VM:%s can not be accessible as expected' %(vm_ip))

ISCSI_TARGET_IP = []
ISCSI_TARGET_UUID = []
def setup_iscsi_target(vm_inv, vm_config, deploy_config):
    global ISCSI_TARGET_IP
    global ISCSI_TARGET_UUID
    ISCSI_TARGET_UUID.append(vm_inv.uuid)
    vm_ip = test_lib.lib_get_vm_nic_by_l3(vm_inv, vm_inv.defaultL3NetworkUuid).ip
    if hasattr(vm_config, 'hostRef'):
        host = get_deploy_host(vm_config.hostRef.text_, deploy_config)
        if not hasattr(host, 'port_') or host.port_ == '22':
            host_port = '22'
        else:
            host_port = host.port_
    else:
        host_port = '22'

    #TODO: install with local repo
    cmd = "sysctl -w vm.dirty_ratio=10"
    exec_cmd_in_vm(cmd, vm_ip, vm_config, True, host_port)

    cmd = "sysctl -w vm.dirty_background_ratio=5"
    exec_cmd_in_vm(cmd, vm_ip, vm_config, True, host_port)
    
    cmd = "sysctl -p"
    exec_cmd_in_vm(cmd, vm_ip, vm_config, True, host_port)

    cmd = "sed -i 's/enabled=1/enabled=0/g' /etc/yum/pluginconf.d/fastestmirror.conf"
    exec_cmd_in_vm(cmd, vm_ip, vm_config, True, host_port)

    #scp_iscsi_repo_to_host(vm_config, vm_ip)
    cmd = "yum --disablerepo=* --enablerepo=alibase install targetcli -y"
    exec_cmd_in_vm(cmd, vm_ip, vm_config, True, host_port)

    #cmd = "iptables -I INPUT -p tcp -m tcp --dport 3260 -j ACCEPT"
    cmd = "iptables -F"
    exec_cmd_in_vm(cmd, vm_ip, vm_config, True, host_port)

    cmd = "service iptables save"
    exec_cmd_in_vm(cmd, vm_ip, vm_config, True, host_port)

    cmd = "systemctl start target"
    exec_cmd_in_vm(cmd, vm_ip, vm_config, True, host_port)

    cmd = "systemctl enable target"
    exec_cmd_in_vm(cmd, vm_ip, vm_config, True, host_port)

    cmd = "echo 'sleep 15' >>/etc/rc.local"
    exec_cmd_in_vm(cmd, vm_ip, vm_config, True, host_port)

    cmd = "echo 'targetcli /backstores/block create blkvdb /dev/vdb 2>&1 >>/tmp/tgtadm.log' >>/etc/rc.local"
    exec_cmd_in_vm(cmd, vm_ip, vm_config, True, host_port)

    cmd = "echo 'targetcli /iscsi create iqn.2018-06.org.disk1 2>&1 >>/tmp/tgtadm.log' >>/etc/rc.local"
    exec_cmd_in_vm(cmd, vm_ip, vm_config, True, host_port)

    cmd = "echo 'targetcli /iscsi/iqn.2018-06.org.disk1/tpg1/luns create /backstores/block/blkvdb 2>&1 >>/tmp/tgtadm.log' >>/etc/rc.local"
    exec_cmd_in_vm(cmd, vm_ip, vm_config, True, host_port)

    cmd = "echo 'targetcli /iscsi/iqn.2018-06.org.disk1/tpg1/ set attribute authentication=0 demo_mode_write_protect=0 generate_node_acls=1 cache_dynamic_acls=1 2>&1 >>/tmp/tgtadm.log' >>/etc/rc.local"
    exec_cmd_in_vm(cmd, vm_ip, vm_config, True, host_port)

    cmd = "echo 'targetcli saveconfig 2>&1 >>/tmp/tgtadm.log' >>/etc/rc.local"
    exec_cmd_in_vm(cmd, vm_ip, vm_config, True, host_port)

    cmd = "echo 'echo 0 > /proc/sys/kernel/hung_task_timeout_secs' >>/etc/rc.local"
    exec_cmd_in_vm(cmd, vm_ip, vm_config, True, host_port)

    cmd = "bash -x /etc/rc.local"
    exec_cmd_in_vm(cmd, vm_ip, vm_config, True, host_port)

    ISCSI_TARGET_IP.append(vm_ip)
    test_util.test_logger("ISCSI_TARGET_IP=%s" %(vm_ip))


def get_vm_inv_by_vm_ip(zstack_management_ip, vm_ip):
    cond = res_ops.gen_query_conditions('vmNics.ip', '=', vm_ip)
    vm_inv = query_resource(zstack_management_ip, res_ops.VM_INSTANCE, cond).inventories[0]
    return vm_inv

def get_vm_config(vm_inv, scenario_config):
    if hasattr(scenario_config.deployerConfig, 'hosts'):
        for host in xmlobject.safe_list(scenario_config.deployerConfig.hosts.host):
            for vm in xmlobject.safe_list(host.vms.vm):
                if vm.name_ == vm_inv.name:
                    return vm
    return None

HOST_INITIATOR_COUNT = 0
HOST_INITIATOR_IP_LIST = []
HOST_INITIATOR_VM_CONFIG_LIST = []
def setup_iscsi_initiator(zstack_management_ip, vm_inv, vm_config, deploy_config):
    global HOST_INITIATOR_COUNT
    global HOST_INITIATOR_IP_LIST
    global HOST_INITIATOR_VM_CONFIG_LIST
    global ISCSI_TARGET_IP
    global ISCSI_TARGET_UUID

    iscsi_target_ip = ISCSI_TARGET_IP
    vm_ip = test_lib.lib_get_vm_nic_by_l3(vm_inv, vm_inv.defaultL3NetworkUuid).ip

    HOST_INITIATOR_IP_LIST.append(vm_ip)
    HOST_INITIATOR_VM_CONFIG_LIST.append(vm_config)

    if hasattr(vm_config, 'hostRef'):
        host = get_deploy_host(vm_config.hostRef.text_, deploy_config)
        if not hasattr(host, 'port_') or host.port_ == '22':
            host_port = '22'
        else:
            host_port = host.port_
    else:
        host_port = '22'

    #scp_iscsi_repo_to_host(vm_config, vm_ip)
    cmd = "sysctl -w vm.dirty_ratio=10"
    exec_cmd_in_vm(cmd, vm_ip, vm_config, True, host_port)

    cmd = "sysctl -w vm.dirty_background_ratio=5"
    exec_cmd_in_vm(cmd, vm_ip, vm_config, True, host_port)
    
    cmd = "sysctl -p"
    exec_cmd_in_vm(cmd, vm_ip, vm_config, True, host_port)

    cmd = "yum -y install iscsi-initiator-utils"
    exec_cmd_in_vm(cmd, vm_ip, vm_config, True, host_port)

    cmd = "service iscsi start"
    exec_cmd_in_vm(cmd, vm_ip, vm_config, True, host_port)

    cmd = "chkconfig iscsi on"
    exec_cmd_in_vm(cmd, vm_ip, vm_config, True, host_port)

    cmd = "service iscsid start"
    exec_cmd_in_vm(cmd, vm_ip, vm_config, True, host_port)

    cmd = "chkconfig iscsid on"
    exec_cmd_in_vm(cmd, vm_ip, vm_config, True, host_port)

    cmd = "yum -y install device-mapper device-mapper-multipath"
    exec_cmd_in_vm(cmd, vm_ip, vm_config, True, host_port)

    #add longer timeout for ping and heartbeat to avoid iscsi connection issue
    cmd = "sed -i 's/noop_out_interval = 5/noop_out_interval = 30/g' /etc/iscsi/iscsid.conf; sync; sync"
    exec_cmd_in_vm(cmd, vm_ip, vm_config, True, host_port)

    cmd = "sed -i 's/noop_out_timeout = 5/noop_out_timeout = 30/g' /etc/iscsi/iscsid.conf; sync; sync"
    exec_cmd_in_vm(cmd, vm_ip, vm_config, True, host_port)

    cmd = "service iscsid restart"
    exec_cmd_in_vm(cmd, vm_ip, vm_config, True, host_port)

    #cmd = "chkconfig --level 2345 multipathd on"
    #exec_cmd_in_vm(cmd, vm_ip, vm_config, True, host_port)
 
    for i in iscsi_target_ip:
        cmd = "echo 'iscsiadm -m discovery -t sendtargets -p %s:3260 2>&1 >>/tmp/tgtadm.log' >>/etc/rc.local; sync" %(i)
        exec_cmd_in_vm(cmd, vm_ip, vm_config, True, host_port)

        cmd = "echo 'iscsiadm -m node -T iqn.2016-06.io.spdk:disk1 -p %s:3260 -l >>/tmp/tgtadm.log' >>/etc/rc.local; sync" %(i)
        exec_cmd_in_vm(cmd, vm_ip, vm_config, True, host_port)

    cmd = "bash -x /etc/rc.local"
    exec_cmd_in_vm(cmd, vm_ip, vm_config, True, host_port)

    #cmd = "modprobe dm-multipath"
    #exec_cmd_in_vm(cmd, vm_ip, vm_config, True, host_port)

    #cmd = "modprobe dm-round-robin"
    #exec_cmd_in_vm(cmd, vm_ip, vm_config, True, host_port)
    
    import commands
    status, woodpecker_ip = commands.getstatusoutput("ip addr show zsn0 | sed -n '3p' | awk '{print $2}' | awk -F / '{print $1}'")
    #multipath_cfg_src = "/home/%s/multipath.conf" %(woodpecker_ip)
    #multipath_cfg_dst = "/etc/multipath.conf"
    #ssh.scp_file(multipath_cfg_src, multipath_cfg_dst, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_)
    #cmd = "service multipathd start"
    #exec_cmd_in_vm(cmd, vm_ip, vm_config, True, host_port)

    #cmd = "multipath -v2"
    #exec_cmd_in_vm(cmd, vm_ip, vm_config, True, host_port)

    #HOST_INITIATOR_COUNT = HOST_INITIATOR_COUNT + 1
    #if HOST_INITIATOR_COUNT == 3:
    #    fdisk_cfg_src = "/home/%s/fdiskIscsiUse.cmd" %(woodpecker_ip)
    #    fdisk_cfg_dst = "/tmp/fdiskIscsiUse.cmd"
    #    ssh.scp_file(fdisk_cfg_src, fdisk_cfg_dst, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_)

    #    cmd = "fdisk /dev/mapper/mpatha </tmp/fdiskIscsiUse.cmd"
    #    exec_cmd_in_vm(cmd, vm_ip, vm_config, False, host_port)

    #    stop_vm(zstack_management_ip, ISCSI_TARGET_UUID, 'cold')
    #    start_vm(zstack_management_ip, ISCSI_TARGET_UUID)

    #    time.sleep(180) #This is a must, or host will not find mpatha and mpatha2 uuid

    #    #Below is aim to migrate sanlock to a separated partition, don't delete!!!
    #    #IF separated_partition:
    #    #cmd = "pvcreate /dev/mapper/mpatha1"
    #    #exec_cmd_in_vm(cmd, vm_ip, vm_config, True, host_port)

    #    #cmd = "pvcreate /dev/mapper/mpatha2 --metadatasize 512m"
    #    #exec_cmd_in_vm(cmd, vm_ip, vm_config, True, host_port)

    #    #ELSE
    #    cmd = "pvcreate /dev/mapper/mpatha1"
    #    exec_cmd_in_vm(cmd, vm_ip, vm_config, True, host_port)
    #    #ENDIF

    #    cmd = "systemctl restart multipathd.service"
    #    exec_cmd_in_vm(cmd, vm_ip, vm_config, True, host_port)

    #    import threading
    #    def _reboot_vm_wrapper(zstack_management_ip, vm_ip, vm_config, deploy_config):
    #        vm_inv = get_vm_inv_by_vm_ip(zstack_management_ip, vm_ip)
    #        vm_uuid = vm_inv.uuid
    #        stop_vm(zstack_management_ip, vm_uuid, 'cold')
    #        start_vm(zstack_management_ip, vm_uuid)
    #        time.sleep(180) #This is a must, or host will not find mpatha and mpatha2 uuid
    #        recover_after_host_vm_reboot(vm_inv, vm_config, deploy_config)
    #        
    #    thd_list = []
    #    for vm_ip,vm_config in zip(HOST_INITIATOR_IP_LIST, HOST_INITIATOR_VM_CONFIG_LIST):
    #        thd = threading.Thread(target = _reboot_vm_wrapper, args=(zstack_management_ip, vm_ip, vm_config, deploy_config))
    #        thd_list.append(thd)
    #        thd.daemon = True
    #        thd.start()

    #    for thd in thd_list:
    #        thd.join()


def get_scenario_config_vm(vm_name, scenario_config):
    for host in xmlobject.safe_list(scenario_config.deployerConfig.hosts.host):
        for vm in xmlobject.safe_list(host.vms.vm):
            if vm.name_ == vm_name:
                return vm

def dump_scenario_file_ips(scenario_file):
    ips = []
    with open(scenario_file, 'r') as fd:
        xmlstr = fd.read()
        fd.close()
        scenariofile = xmlobject.loads(xmlstr)
        for vm in xmlobject.safe_list(scenariofile.vms.vm):
            for ip in xmlobject.safe_list(vm.ips.ip):
                ips.append(ip.ip_)
    return ips


def get_host_management_ip_by_public_ip_from_scenario_file(scenario_file, public_ip):
    if not scenario_file or not os.path.exists(scenario_file):
        return None

    with open(scenario_file, 'r') as fd:
        xmlstr = fd.read()
        fd.close()
        scenariofile = xmlobject.loads(xmlstr)
        for vm in xmlobject.safe_list(scenariofile.vms.vm):
            if vm.ip_ == public_ip:
                return vm.managementIp_
    return None


def get_scenario_file_vm(vm_name, scenario_file):
    with open(scenario_file, 'r') as fd:
        xmlstr = fd.read()
        fd.close()
        scenariofile = xmlobject.loads(xmlstr)
        for s_vm in xmlobject.safe_list(scenariofile.vms.vm):
            if s_vm.name_ == vm_name:
                return s_vm

def get_ceph_storages_nic_id(ceph_name, scenario_config):
    for host in xmlobject.safe_list(scenario_config.deployerConfig.hosts.host):
        for vm in xmlobject.safe_list(host.vms.vm):
            nic_id = 0
            for l3network in xmlobject.safe_list(vm.l3Networks.l3Network):
                if hasattr(l3network, 'backupStorageRef') and not hasattr(l3network.backupStorageRef, 'monIp_') and l3network.backupStorageRef.text_ == ceph_name:
                    return nic_id
                if hasattr(l3network, 'primaryStorageRef') and not hasattr(l3network.primaryStorageRef, 'monIp_') and l3network.primaryStorageRef.text_ == ceph_name:
                    return nic_id
                nic_id += 1
       
    for host in xmlobject.safe_list(scenario_config.deployerConfig.hosts.host):
        for vm in xmlobject.safe_list(host.vms.vm):
            nic_id = 0
            for l3network in xmlobject.safe_list(vm.l3Networks.l3Network):
                if hasattr(l3network, 'backupStorageRef') and l3network.backupStorageRef.text_ == ceph_name:
                    return nic_id
                if hasattr(l3network, 'primaryStorageRef') and l3network.primaryStorageRef.text_ == ceph_name:
                    return nic_id
                nic_id += 1
    return None

def get_fusionstor_storages_nic_id(fusionstor_name, scenario_config):
    for host in xmlobject.safe_list(scenario_config.deployerConfig.hosts.host):
        for vm in xmlobject.safe_list(host.vms.vm):
            nic_id = 0
            for l3network in xmlobject.safe_list(vm.l3Networks.l3Network):
                if hasattr(l3network, 'backupStorageRef') and not hasattr(l3network.backupStorageRef, 'monIp_') and l3network.backupStorageRef.text_ == fusionstor_name:
                    return nic_id
                if hasattr(l3network, 'primaryStorageRef') and not hasattr(l3network.primaryStorageRef, 'monIp_') and l3network.primaryStorageRef.text_ == fusionstor_name:
                    return nic_id
                nic_id += 1

    for host in xmlobject.safe_list(scenario_config.deployerConfig.hosts.host):
        for vm in xmlobject.safe_list(host.vms.vm):
            nic_id = 0
            for l3network in xmlobject.safe_list(vm.l3Networks.l3Network):
                if hasattr(l3network, 'backupStorageRef') and l3network.backupStorageRef.text_ == fusionstor_name:
                    return nic_id
                if hasattr(l3network, 'primaryStorageRef') and l3network.primaryStorageRef.text_ == fusionstor_name:
                    return nic_id
                nic_id += 1
    return None

def setup_ceph_storages(scenario_config, scenario_file, deploy_config):
    ceph_storages = dict()
    for host in xmlobject.safe_list(scenario_config.deployerConfig.hosts.host):
        for vm in xmlobject.safe_list(host.vms.vm):
            vm_name = vm.name_

            if hasattr(vm, 'backupStorageRef'):
                for backupStorageRef in xmlobject.safe_list(vm.backupStorageRef):
                    print backupStorageRef.text_
                    backup_storage_type = get_backup_storage_type(deploy_config, backupStorageRef.text_)
                    if backup_storage_type in ['ceph', 'xsky']:
#                     if backup_storage_type == 'ceph':
                        key = (backupStorageRef.text_, backup_storage_type)
                        if ceph_storages.has_key(key):
                            if vm_name in ceph_storages[key]:
                                continue
                            else:
                                ceph_storages[key].append(vm_name)
                        else:
                            ceph_storages[key] = [ vm_name ]

            if hasattr(vm, 'primaryStorageRef'):
                for primaryStorageRef in xmlobject.safe_list(vm.primaryStorageRef):
                    primary_storage_type = get_primary_storage_type(deploy_config, primaryStorageRef.text_)
                    for zone in xmlobject.safe_list(deploy_config.zones.zone):
#                         if primary_storage_type == 'ceph':
                        if primary_storage_type in ['ceph', 'xsky']:
                            key = (primaryStorageRef.text_, primary_storage_type)
                            if ceph_storages.has_key(key):
                                if vm_name in ceph_storages[key]:
                                    continue
                                else:
                                    ceph_storages[key].append(vm_name)
                            else:
                                vals = ceph_storages.values()
                                val_list = [v for pv in vals for v in pv]
                                if vm_name not in val_list:
                                    ceph_storages[key] = [ vm_name ]

#     for ceph_storage in ceph_storages:
    def deploy_ceph(ceph_storages, ceph_storage):
        test_util.test_logger('setup ceph [%s] service.' % (ceph_storage[0]))
        node1_name = ceph_storages[ceph_storage][0]
        node1_config = get_scenario_config_vm(node1_name, scenario_config)
        node1_ip = get_scenario_file_vm(node1_name, scenario_file).ip_
        if not hasattr(node1_config, 'hostRef'):
            node_host_port = '22'
        else:
            node_host = get_deploy_host(node1_config.hostRef.text_, deploy_config)
            if not hasattr(node_host, 'port_') or node_host.port_ == '22':
                node_host_port = '22'
            else:
                node_host_port = node_host.port_

        vm_ips = ''
        for ceph_node in ceph_storages[ceph_storage]:
            vm_nic_id = get_ceph_storages_nic_id(ceph_storage[0], scenario_config)
            vm = get_scenario_file_vm(ceph_node, scenario_file)
            if vm_nic_id == None:
                vm_ips += vm.ip_ + ' '
            else:
                vm_ips += vm.ips.ip[vm_nic_id].ip_ + ' '
        ssh.scp_file("%s/%s" % (os.environ.get('woodpecker_root_path'), '/tools/setup_ceph_nodes.sh'), '/tmp/setup_ceph_nodes.sh', node1_ip, node1_config.imageUsername_, node1_config.imagePassword_, port=int(node_host_port))
        ssh.scp_file("%s/%s" % (os.environ.get('woodpecker_root_path'), '/tools/setup_ceph_j_nodes.sh'), '/tmp/setup_ceph_j_nodes.sh', node1_ip, node1_config.imageUsername_, node1_config.imagePassword_, port=int(node_host_port))
        ssh.scp_file("%s/%s" % (os.environ.get('woodpecker_root_path'), '/tools/setup_ceph_h_nodes.sh'), '/tmp/setup_ceph_h_nodes.sh', node1_ip, node1_config.imageUsername_, node1_config.imagePassword_, port=int(node_host_port))
        cmd = "bash -ex /tmp/setup_ceph_nodes.sh %s" % (vm_ips)
        ssh.execute(cmd, node1_ip, node1_config.imageUsername_, node1_config.imagePassword_, True, int(node_host_port))
#     thread_list = []
#     for ceph_storage in ceph_storages:
#         thread_list.append(Thread(target=deploy_ceph, args=(ceph_storages, ceph_storage)))
#     for thrd in thread_list:
#         thrd.start()
#     for _thrd in thread_list:
#         _thrd.join()

# def setup_xsky_ceph_storages(scenario_config, scenario_file, deploy_config):
#     ceph_storages = dict()
#     for host in xmlobject.safe_list(scenario_config.deployerConfig.hosts.host):
#         for vm in xmlobject.safe_list(host.vms.vm):
#             vm_name = vm.name_
#             if hasattr(vm, 'backupStorageRef'):
#                 for backupStorageRef in xmlobject.safe_list(vm.backupStorageRef):
#                     print backupStorageRef.text_
#                     backup_storage_type = get_backup_storage_type(deploy_config, backupStorageRef.text_)
#                     test_util.test_logger("@@@DEBUG-> backup_storage_type %s" %(backup_storage_type))
#                     if backup_storage_type == 'ceph':
#                         if ceph_storages.has_key(backupStorageRef.text_):
#                             if vm_name in ceph_storages[backupStorageRef.text_]:
#                                 continue
#                             else:
#                                 ceph_storages[backupStorageRef.text_].append(vm_name)
#                         else:
#                             ceph_storages[backupStorageRef.text_] = [ vm_name ]
#             if hasattr(vm, 'primaryStorageRef'):
#                 for primaryStorageRef in xmlobject.safe_list(vm.primaryStorageRef):
#                     print primaryStorageRef.text_
#                     primary_storage_type = get_primary_storage_type(deploy_config, primaryStorageRef.text_)
#                     test_util.test_logger(" @@@DEBUG-> primary_storage_type %s" %(primary_storage_type))
#                     for zone in xmlobject.safe_list(deploy_config.zones.zone):
#                         if primary_storage_type == 'ceph':
#                             if ceph_storages.has_key(backupStorageRef.text_):
#                                 if vm_name in ceph_storages[backupStorageRef.text_]:
#                                     continue
#                                 else:
#                                     ceph_storages[backupStorageRef.text_].append(vm_name)
#                             else:
#                                 ceph_storages[backupStorageRef.text_] = [ vm_name ]
    def deploy_xsky(ceph_storages, ceph_storage):
        test_util.test_logger('setup ceph [%s] service.' % (ceph_storage[0]))
        node1_name = ceph_storages[ceph_storage][0]
        node1_config = get_scenario_config_vm(node1_name, scenario_config)
        node1_ip = get_scenario_file_vm(node1_name, scenario_file).ip_
        if not hasattr(node1_config, 'hostRef'):
            node_host_port = '22'
        else:
            node_host = get_deploy_host(node1_config.hostRef.text_, deploy_config)
            if not hasattr(node_host, 'port_') or node_host.port_ == '22':
                node_host_port = '22'
            else:
                node_host_port = node_host.port_

        vm_ips = ''
        for ceph_node in ceph_storages[ceph_storage]:
            vm_nic_id = get_ceph_storages_nic_id(ceph_storage[0], scenario_config)
            vm = get_scenario_file_vm(ceph_node, scenario_file)
            if vm_nic_id == None:
                vm_ips += vm.ip_ + ' '
            else:
                vm_ips += vm.ips.ip[vm_nic_id].ip_ + ' '
        ssh.scp_file("%s/%s" % (os.environ.get('woodpecker_root_path'), '/tools/setup-xsky-3nodes.sh'), '/root/setup-xsky-3nodes.sh', node1_ip, node1_config.imageUsername_, node1_config.imagePassword_, port=int(node_host_port))
        os.system("sshpass -p password ssh root@%s \"bash -ex /root/setup-xsky-3nodes.sh %s > /root/setup.log 2>&1 \"" %(node1_ip, vm_ips))
        time.sleep(2)
        cmd1 = "rados lspools"
        (retcode, output, erroutput) = ssh.execute(cmd1, node1_ip, node1_config.imageUsername_, node1_config.imagePassword_, True, int(node_host_port))
        output += "\n"
        print "output is %s" % (output)
        dvpn = "cephPrimaryStorageDataVolumePoolName ="
        rvpn = "cephPrimaryStorageRootVolumePoolName ="
        icpn = "cephPrimaryStorageImageCachePoolName ="
        cbsp = "cephBackupStoragePoolName ="
        data_volume_name = "%s %s" % (dvpn, output)
        root_volume_name = "%s %s" % (rvpn, output)
        image_cache_name = "%s %s" % (icpn, output)
        backup_storage_pool = "%s %s" % (cbsp, output)
        print "data_volume_name is %s" % (data_volume_name)
        with open('/root/.zstackwoodpecker/integrationtest/vm/multihosts/deploy-xsky-ceph-ps.tmpt', 'a+') as infile:
                lines = infile.readlines()
                print "lines is %s" % (lines)
                infile.write(data_volume_name)
                infile.write(root_volume_name)
                infile.write(image_cache_name)
                infile.write(backup_storage_pool)
    thread_list = []
    for ceph_storage in ceph_storages:
        if 'xsky' in ceph_storage:
            thread_list.append(Thread(target=deploy_xsky, args=(ceph_storages, ceph_storage)))
        else:
            thread_list.append(Thread(target=deploy_ceph, args=(ceph_storages, ceph_storage)))
    for thrd in thread_list:
        thrd.start()
    for _thrd in thread_list:
        _thrd.join()

def setup_xsky_storages(scenario_config, scenario_file, deploy_config):
    #Stop nodes
    if hasattr(scenario_config.basicConfig, 'xskyNodesMN'):
        xskyNodesMN = scenario_config.basicConfig.xskyNodesMN.text_
    else:
        xskyNodesMN = None
    print xskyNodesMN

    if hasattr(scenario_config.deployerConfig, 'xsky') == True:
        for node in xmlobject.safe_list(scenario_config.deployerConfig.xsky.nodes.node):
            vmUuid = node.uuid_
            print "vm uuid %s" % (str(vmUuid))
            # NOTE: need to make filesystem in sync in VM before cold stop VM
            stop_vm(xskyNodesMN, vmUuid)

        #Wait nodes down
        for node in xmlobject.safe_list(scenario_config.deployerConfig.xsky.nodes.node):
            vmUuid = node.uuid_
            vmIp = node.nodeIP_
            test_lib.lib_wait_target_down(vmIp, '22', 120)

        time.sleep(30)
        #revert snapshot
        for node in xmlobject.safe_list(scenario_config.deployerConfig.xsky.nodes.node):
            nodesnapshot = node.snapshot_
            conditions = res_ops.gen_query_conditions('name', '=', nodesnapshot)
            snapshot_inventories = query_resource(xskyNodesMN, res_ops.VOLUME_SNAPSHOT, conditions).inventories[0]
            snapshot_uuid = snapshot_inventories.uuid

            use_snapshot(xskyNodesMN, snapshot_uuid)
            for volume in xmlobject.safe_list(node.volumeDisks.volumeDisk):
                volume_snapshot = volume.snapshot_
                conditions = res_ops.gen_query_conditions('name', '=', volume_snapshot)
                snapshot_inventories = query_resource(xskyNodesMN, res_ops.VOLUME_SNAPSHOT, conditions).inventories[0]
                snapshot_uuid = snapshot_inventories.uuid
                use_snapshot(xskyNodesMN, snapshot_uuid)

        time.sleep(30)
        #start nodes
        for node in xmlobject.safe_list(scenario_config.deployerConfig.xsky.nodes.node):
            vmUuid = node.uuid_
            print "vm uuid %s" % (str(vmUuid))
            start_vm(xskyNodesMN, vmUuid)

        #Wait nodes up
        for node in xmlobject.safe_list(scenario_config.deployerConfig.xsky.nodes.node):
            vmUuid = node.uuid_
            vmIp = node.nodeIP_
            if not wait_for_target_vm_retry_after_reboot(xskyNodesMN, vmIp, vmUuid):
                test_util.test_fail('VM:%s can not be accessible as expected' %(vmIp))

        #check xsky ENV
        xskyUser = scenario_config.deployerConfig.xsky.account.user.text_
        xskyPassword = scenario_config.deployerConfig.xsky.account.password.text_
        xskyUrl = scenario_config.deployerConfig.xsky.url.text_
        xmsNode = scenario_config.deployerConfig.xsky.xmsNode.xmsNodeIP.text_
        xmsNodeLoginUser = scenario_config.deployerConfig.xsky.xmsNode.xmsNodeLoginUser.text_
        xmsNodeLoginPassword = scenario_config.deployerConfig.xsky.xmsNode.xmsNodeLoginPassword.text_
        host_status_cmd = 'xms-cli --user ' + xskyUser + ' --password ' + xskyPassword + ' --url ' + xskyUrl + ' --format "json" host list'
        osd_status_cmd = 'xms-cli --user ' + xskyUser + ' --password ' + xskyPassword + ' --url ' + xskyUrl + ' --format "json" osd list'
        unhealthy = False
        for i in range(0, 10):
            unhealthy = False
            print "round %s" % (str(i))
            time.sleep(20)
            try:
                (ret, out, eout) = ssh.execute(host_status_cmd, xmsNode, xmsNodeLoginUser, xmsNodeLoginPassword)
                print "xms output"
                print out
                print eout
                xsky_host_info = json.loads(out)
                for xskyhost in xsky_host_info['hosts']:
                    status = xskyhost['status']
                    print status
                    isUp = xskyhost['up']
                    print isUp
                    if status != 'active':
                       unhealthy = True
                    if isUp != True:
                       unhealthy = True
                print "host status: " + str(unhealthy)

                (ret, out, eout) = ssh.execute(osd_status_cmd, xmsNode, xmsNodeLoginUser, xmsNodeLoginPassword)
                print "xms output"
                print out
                print eout
                unhealthy = False
                xsky_host_info = json.loads(out)
                for xskyhost in xsky_host_info['osds']:
                    status = xskyhost['status']
                    print status
                    isUp = xskyhost['up']
                    print isUp
                    if status != 'active':
                       unhealthy = True
                    if isUp != True:
                       unhealthy = True
                print "osd status:" + str(unhealthy)
            except Exception as e:
                unhealthy = True
                print str(e)
                continue
            if unhealthy == False:
                break
        if unhealthy:
            test_util.test_fail('Xsky poc evn is not healthy')
            

def modify_setup_script_for_mn_ha_fusionstor():
    if test_lib.lib_cur_cfg_is_a_and_b(["test-config-vyos-fusionstor-3-nets-sep.xml"], ["scenario-config-fusionstor-3-nets-sep.xml"]):
        cmd = "sed -i 's/solomode   on/solomode   off/g' %s/%s" %(os.environ.get('woodpecker_root_path'), '/tools/setup_fusionstor_nodes.sh')
        test_util.test_logger("@@@DEBUG-> change solomode@@@ %s" %(cmd))
        os.system(cmd)
        cmd = "sed -i 's:172.20.0.1/16:192.168.0.1/16:g' %s/%s" %(os.environ.get('woodpecker_root_path'), '/tools/setup_fusionstor_nodes.sh')
        test_util.test_logger("@@@DEBUG-> change ip@@@ %s" %(cmd))
        os.system(cmd)
    else:
        pass

def setup_fusionstor_storages(scenario_config, scenario_file, deploy_config):
    fusionstor_storages = dict()
    for host in xmlobject.safe_list(scenario_config.deployerConfig.hosts.host):
        for vm in xmlobject.safe_list(host.vms.vm):
            vm_name = vm.name_

            if hasattr(vm, 'backupStorageRef'):
               for backupStorageRef in xmlobject.safe_list(vm.backupStorageRef):
                   print backupStorageRef.text_
                   backup_storage_type = get_backup_storage_type(deploy_config, backupStorageRef.text_)
                   if backup_storage_type == 'fusionstor':
                       if fusionstor_storages.has_key(backupStorageRef.text_):
                           if vm_name in fusionstor_storages[backupStorageRef.text_]:
                               continue
                           else:
                               fusionstor_storages[backupStorageRef.text_].append(vm_name)
                       else:
                           fusionstor_storages[backupStorageRef.text_] = [ vm_name ]
            if hasattr(vm, 'primaryStorageRef'):
                for primaryStorageRef in xmlobject.safe_list(vm.primaryStorageRef):
                    print primaryStorageRef.text_
                    primary_storage_type = get_primary_storage_type(deploy_config, primaryStorageRef.text_)
                    for zone in xmlobject.safe_list(deploy_config.zones.zone):
                        if primary_storage_type == 'fusionstor':
                            if fusionstor_storages.has_key(backupStorageRef.text_):
                                if vm_name in fusionstor_storages[backupStorageRef.text_]:
                                    continue
                                else:
                                    fusionstor_storages[backupStorageRef.text_].append(vm_name)
                            else:
                                fusionstor_storages[backupStorageRef.text_] = [ vm_name ]
    if len(fusionstor_storages) > 0:
        test_util.test_logger('get fusionstor pkg')
        fusionstorPkg = os.environ['fusionstorPkg']
    else:
        test_util.test_logger('no fusionstor pkg return here')
        return

    for fusionstor_storage in fusionstor_storages:
        test_util.test_logger('setup fusionstor [%s] service.' % (fusionstor_storage))
        node1_name = fusionstor_storages[fusionstor_storage][0]
        node1_config = get_scenario_config_vm(node1_name, scenario_config)
        node1_ip = get_scenario_file_vm(node1_name, scenario_file).ip_
        node_host = get_deploy_host(node1_config.hostRef.text_, deploy_config)
        if not hasattr(node_host, 'port_') or node_host.port_ == '22':
            node_host.port_ = '22'
        vm_ips = ''
        for fusionstor_node in fusionstor_storages[fusionstor_storage]:
            vm_nic_id = get_fusionstor_storages_nic_id(fusionstor_storage, scenario_config)
            vm = get_scenario_file_vm(fusionstor_node, scenario_file)
            if vm_nic_id == None:
                vm_ips += vm.ip_ + ' '
            else:
                vm_ips += vm.ips.ip[vm_nic_id].ip_ + ' '

        modify_setup_script_for_mn_ha_fusionstor()
        ssh.scp_file("%s/%s" % (os.environ.get('woodpecker_root_path'), '/tools/setup_fusionstor_nodes.sh'), '/tmp/setup_fusionstor_nodes.sh', node1_ip, node1_config.imageUsername_, node1_config.imagePassword_, port=int(node_host.port_))
        ssh.scp_file(fusionstorPkg, fusionstorPkg, node1_ip, node1_config.imageUsername_, node1_config.imagePassword_, port=int(node_host.port_))
        cmd = "bash -ex /tmp/setup_fusionstor_nodes.sh %s %s" % ((fusionstorPkg), (vm_ips))
        try:
            ssh.execute(cmd, node1_ip, node1_config.imageUsername_, node1_config.imagePassword_, True, int(node_host.port_))
        except Exception as e:
            print str(e)
            print "re-install fusionstor"
            ssh.execute(cmd, node1_ip, node1_config.imageUsername_, node1_config.imagePassword_, True, int(node_host.port_))

def setup_ocfs2smp_primary_storages(scenario_config, scenario_file, deploy_config, vm_inv_lst, vm_cfg_lst):
    ocfs2_storages = dict()
    smp_url = None
    for host in xmlobject.safe_list(scenario_config.deployerConfig.hosts.host):
        for vm in xmlobject.safe_list(host.vms.vm):
            vm_name = vm.name_
            if hasattr(vm, 'primaryStorageRef'):
                for primaryStorageRef in xmlobject.safe_list(vm.primaryStorageRef):
                    for zone in xmlobject.safe_list(deploy_config.zones.zone):
                        if primaryStorageRef.type_ == 'ocfs2smp':
                            if ocfs2_storages.has_key(primaryStorageRef.text_):
                                if vm_name in ocfs2_storages[primaryStorageRef.text_]:
                                    continue
                                else:
                                    ocfs2_storages[primaryStorageRef.text_].append(vm_name)
                            else:
                                ocfs2_storages[primaryStorageRef.text_] = [ vm_name ]
                                if hasattr(primaryStorageRef, 'url_'):
                                    smp_url = primaryStorageRef.url_

    for ocfs2_storage in ocfs2_storages:
        test_util.test_logger('setup ocfs2 [%s] service.' % (ocfs2_storage))
        node1_name = ocfs2_storages[ocfs2_storage][0]
        node1_config = get_scenario_config_vm(node1_name, scenario_config)
        #node1_ip = get_scenario_file_vm(node1_name, scenario_file).ip_
        node_host = get_deploy_host(node1_config.hostRef.text_, deploy_config)
        if not hasattr(node_host, 'port_') or node_host.port_ == '22':
            node_host.port_ = '22'

        vm_ips = ''
        for ocfs2_node in ocfs2_storages[ocfs2_storage]:
            vm_nic_id = get_ceph_storages_nic_id(ocfs2_storage, scenario_config)
            vm = get_scenario_file_vm(ocfs2_node, scenario_file)
            if vm_nic_id == None:
                vm_ips += vm.ip_ + ' '
            else:
                vm_ips += vm.ips.ip[vm_nic_id].ip_ + ' '
        #ssh.scp_file("%s/%s" % (os.environ.get('woodpecker_root_path'), '/tools/setup_ocfs2.sh'), '/tmp/setup_ocfs2.sh', node1_ip, node1_config.imageUsername_, node1_config.imagePassword_, port=int(node_host.port_))
        import commands
        status, woodpecker_ip = commands.getstatusoutput("ip addr show zsn0 | sed -n '3p' | awk '{print $2}' | awk -F / '{print $1}'")
        if smp_url:
            cmd = "SMP_URL=%s bash %s/%s %s" % (smp_url, os.environ.get('woodpecker_root_path'), '/tools/setup_ocfs2.sh', vm_ips)
        else:
            cmd = "bash %s/%s %s" % (os.environ.get('woodpecker_root_path'), '/tools/setup_ocfs2.sh', vm_ips)
           
        test_util.test_logger('%s:%s:%s:%s:%s' % (cmd, woodpecker_ip, node1_config.imageUsername_, node1_config.imagePassword_, str(node_host.port_)))
        ssh.execute(cmd, woodpecker_ip, node1_config.imageUsername_, node1_config.imagePassword_, True, int(node_host.port_))

    if ocfs2_storages:
        for vm_inv, vm_config in zip(vm_inv_lst, vm_cfg_lst):
            recover_after_host_vm_reboot(vm_inv, vm_config, deploy_config)

def setup_zbs_primary_storages(scenario_config, scenario_file, deploy_config, vm_inv_lst, vm_cfg_lst):
    zbs_storages = dict()
    fenceip = ''
    zbs_url = ''
    drbd_utils_url = ''
    drbd_utils_rpm = ''
    for host in xmlobject.safe_list(scenario_config.deployerConfig.hosts.host):
        for vm in xmlobject.safe_list(host.vms.vm):
            vm_name = vm.name_
            if hasattr(vm, 'primaryStorageRef'):
                for primaryStorageRef in xmlobject.safe_list(vm.primaryStorageRef):
                    for zone in xmlobject.safe_list(deploy_config.zones.zone):
                        if primaryStorageRef.type_ == 'ZSES':
                            if zbs_storages.has_key(primaryStorageRef.text_):
                                if vm_name in zbs_storages[primaryStorageRef.text_]:
                                    continue
                                else:
                                    zbs_storages[primaryStorageRef.text_].append(vm_name)
                            else:
                                zbs_storages[primaryStorageRef.text_] = [ vm_name ]
                                if hasattr(primaryStorageRef, 'url_'):
                                    zbs_url = primaryStorageRef.url_
                            fenceip = primaryStorageRef.fenceip_
                            zbs_url = primaryStorageRef.zbs_url_
                            drbd_utils_url = primaryStorageRef.drbd_utils_url_
                            drbd_utils_rpm = drbd_utils_url.split('/')[-1]

    i = 0
    node1_ip = None
    node2_ip = None
    for zbs_storage in zbs_storages:
        test_util.test_logger('setup zbs [%s] service.' % (zbs_storage))
        node_name = zbs_storages[zbs_storage][0]
        node_config = get_scenario_config_vm(node_name, scenario_config)
        node_host = get_deploy_host(node_config.hostRef.text_, deploy_config)
        if not hasattr(node_host, 'port_') or node_host.port_ == '22':
            node_host.port_ = '22'

        for zbs_node in zbs_storages[zbs_storage]:
            vm = get_scenario_file_vm(zbs_node, scenario_file)
            node_ip = vm.ip_
            i += 1
            if i == 1:
                node1_ip = node_ip
            elif i == 2:
                node2_ip = node_ip

        import commands
        cmd = "cp -rnf /opt/zstack-dvd/repos/* /etc/yum.repos.d/; yum --disablerepo=* --enablerepo=zstack-local,uek4-ocfs2 \
  install kernel-uek ocfs2-tools"
        ssh.execute(cmd, node_ip, node_config.imageUsername_, node_config.imagePassword_, True, int(node_host.port_))
        cmd = 'grub2-set-default "CentOS Linux (4.1.12-37.2.2.el7uek.x86_64) 7 (Core)"; reboot'
        ssh.execute(cmd, node_ip, node_config.imageUsername_, node_config.imagePassword_, True, int(node_host.port_))
        cmd = "rm -rf %s; wget %s; rpm -i %s" %(drbd_utils_rpm, drbd_utils_url, drbd_utils_rpm)
        ssh.execute(cmd, node_ip, node_config.imageUsername_, node_config.imagePassword_, True, int(node_host.port_))
        cmd = "rm -rf zbs.bin; wget %s; bash zbs.bin" %zbs_url
        ssh.execute(cmd, node_ip, node_config.imageUsername_, node_config.imagePassword_, True, int(node_host.port_))
        status, wwn_id = commands.getstatusoutput("ls /dev/disk/by-id/|grep wwn")
        if wwn_id == '':
            test_util.test_fail('SCSI volume does not attched to the host')
        cmd = "zbs init-node --address %s --device /dev/disk/by-id/%s --fenceip %s"%(woodpecker_ip, wwn_id, fenceip)
        ssh.execute(cmd, node_ip, node_config.imageUsername_, node_config.imagePassword_, True, int(node_host.port_))
        if node2_ip:
            cmd = 'zbs pair-node --peer %s --user %s --pass %s' %(node2_ip, node_config.imageUsername_, node_config.imagePassword_)
            ssh.execute(cmd, node1_ip, node_config.imageUsername_, node_config.imagePassword_, True, int(node_host.port_))

    if zbs_storages:
        for vm_inv, vm_config in zip(vm_inv_lst, vm_cfg_lst):
            recover_after_host_vm_reboot(vm_inv, vm_config, deploy_config)

def create_sftp_backup_storage(http_server_ip, backup_storage_option, session_uuid=None):
    action = api_actions.AddSftpBackupStorageAction()
    action.timeout = 1200000
    action.name = backup_storage_option.get_name()
    action.description = backup_storage_option.get_description()
    action.type = backup_storage_option.get_type()
    action.url = backup_storage_option.get_url()
    action.hostname = backup_storage_option.get_hostname()
    action.username = backup_storage_option.get_username()
    action.password = backup_storage_option.get_password()
    action.sshPort = backup_storage_option.get_sshPort()
    action.resourceUuid = backup_storage_option.get_resource_uuid()
    action.importImages = backup_storage_option.get_import_images()
    evt = execute_action_with_session(http_server_ip, action, session_uuid)
    test_util.action_logger('Create Sftp Backup Storage [uuid:] %s [name:] %s' % \
            (evt.inventory.uuid, action.name))
    return evt.inventory

def create_image_store_backup_storage(http_server_ip, backup_storage_option, session_uuid=None):
    action = api_actions.AddImageStoreBackupStorageAction()
    action.timeout = 600000
    action.name = backup_storage_option.get_name()
    action.description = backup_storage_option.get_description()
    action.type = backup_storage_option.get_type()
    action.url = backup_storage_option.get_url()
    action.hostname = backup_storage_option.get_hostname()
    action.username = backup_storage_option.get_username()
    action.password = backup_storage_option.get_password()
    action.sshPort = backup_storage_option.get_sshPort()
    action.resourceUuid = backup_storage_option.get_resource_uuid()
    action.importImages = backup_storage_option.get_import_images()
    evt = execute_action_with_session(http_server_ip, action, session_uuid)
    test_util.action_logger('Create Image Store Backup Storage [uuid:] %s [name:] %s' % \
            (evt.inventory.uuid, action.name))
    return evt.inventory

def query_backup_storage(http_server_ip, backup_storage_uuid, session_uuid=None):
    action = api_actions.QueryBackupStorageAction()
    action.uuid = backup_storage_uuid
    action.timeout = 6000000
    test_util.action_logger('Query Backup Storage [uuid:] %s' % backup_storage_uuid)
    evt = execute_action_with_session(http_server_ip, action, session_uuid)
    return evt.inventory

def reconnect_backup_storage(http_server_ip, backup_storage_uuid, session_uuid=None):
    action = api_actions.ReconnectBackupStorageAction()
    action.uuid = backup_storage_uuid
    action.timeout = 6000000
    test_util.action_logger('Reconnect Backup Storage [uuid:] %s' % backup_storage_uuid)
    evt = execute_action_with_session(http_server_ip, action, session_uuid)
    return evt.inventory

def delete_backup_storage(http_server_ip, backup_storage_uuid, session_uuid=None):
    action = api_actions.DeleteBackupStorageAction()
    action.uuid = backup_storage_uuid
    action.timeout = 6000000
    test_util.action_logger('Delete Backup Storage [uuid:] %s' % backup_storage_uuid)
    evt = execute_action_with_session(http_server_ip, action, session_uuid)
    return evt.inventory


def create_zone(http_server_ip, zone_option, session_uuid=None):
    action = api_actions.CreateZoneAction()
    action.timeout = 30000
    action.name = zone_option.get_name()
    action.description = zone_option.get_description()
    evt = execute_action_with_session(http_server_ip, action, session_uuid)
    test_util.action_logger('Add Zone [uuid:] %s [name:] %s' % \
            (evt.uuid, action.name))
    return evt.inventory


def create_cluster(http_server_ip, cluster_option, session_uuid=None):
    action = api_actions.CreateClusterAction()
    action.timeout = 30000
    action.name = cluster_option.get_name()
    action.description = cluster_option.get_description()
    action.hypervisorType = cluster_option.get_hypervisor_type()
    action.type = cluster_option.get_type()
    action.zoneUuid = cluster_option.get_zone_uuid()
    evt = execute_action_with_session(http_server_ip, action, session_uuid)
    test_util.action_logger('Create Cluster [uuid:] %s [name:] %s' % \
            (evt.uuid, action.name))
    return evt.inventory

def add_kvm_host(http_server_ip, host_option, session_uuid=None):
    action = api_actions.AddKVMHostAction()
    action.timeout = 1200000
    action.clusterUuid = host_option.get_cluster_uuid()
    action.username = host_option.get_username()
    action.password = host_option.get_password()
    action.managementIp = host_option.get_management_ip()
    action.name = host_option.get_name()
    action.sshPort = host_option.get_sshPort()
    action.description = host_option.get_description()
    evt = execute_action_with_session(http_server_ip, action, session_uuid)
    test_util.action_logger('Add KVM Host [uuid:] %s with [ip:] %s' % \
            (evt.uuid, action.managementIp))
    return evt.inventory

def create_local_primary_storage(http_server_ip, primary_storage_option, session_uuid=None):
    action = api_actions.AddLocalPrimaryStorageAction()
    action.timeout = 30000
    action.name = primary_storage_option.get_name()
    action.description = primary_storage_option.get_description()
    action.type = primary_storage_option.get_type()
    action.url = primary_storage_option.get_url()
    action.zoneUuid = primary_storage_option.get_zone_uuid()
    evt = execute_action_with_session(http_server_ip, action, session_uuid)
    test_util.action_logger('Create Primary Storage [uuid:] %s [name:] %s' % \
            (evt.inventory.uuid, action.name))
    return evt.inventory

def attach_ps_to_cluster(http_server_ip, primary_storage_uuid, cluster_uuid, session_uuid=None):
    action = api_actions.AttachPrimaryStorageToClusterAction()
    action.clusterUuid = cluster_uuid
    action.primaryStorageUuid = primary_storage_uuid
    action.timeout = 30000
    evt = execute_action_with_session(http_server_ip, action, session_uuid)
    test_util.action_logger('Attach Primary Storage [uuid:] %s to Cluster [uuid:] %s' % \
            (primary_storage_uuid, cluster_uuid))
    return evt.inventory

def attach_bs_to_zone(http_server_ip, backup_storage_uuid, zone_uuid, session_uuid=None):
    action = api_actions.AttachBackupStorageToZoneAction()
    action.zoneUuid = zone_uuid
    action.backupStorageUuid = backup_storage_uuid
    action.timeout = 30000
    evt = execute_action_with_session(http_server_ip, action, session_uuid)
    test_util.action_logger('Attach Backup Storage [uuid:] %s to Zone [uuid:] %s' % \
            (backup_storage_uuid, zone_uuid))
    return evt.inventory

def add_image1(http_server_ip, image_option, session_uuid=None):
    action = api_actions.AddImageAction()
    action.name = image_option.get_name()
    action.url = image_option.get_url()
    action.mediaType = image_option.get_mediaType()
    action.format = image_option.get_format()
    action.platform = image_option.get_platform()
    action.backupStorageUuids = image_option.get_backup_storage_uuid_list()
    test_util.action_logger('Add [Image:] %s from [url:] %s ' % (action.name,action.url))
    evt = execute_action_with_session(http_server_ip, action, image_option.get_session_uuid())
    test_util.test_logger('[image:] %s is added.' % evt.inventory.uuid)
    return evt.inventory


def create_instance_offering1(http_server_ip, instance_offering_option, session_uuid = None):
    action = api_actions.CreateInstanceOfferingAction()
    action.cpuNum = instance_offering_option.get_cpuNum()
    action.memorySize = instance_offering_option.get_memorySize()
    action.allocatorStrategy = instance_offering_option.get_allocatorStrategy()
    action.type = instance_offering_option.get_type()
    action.name = instance_offering_option.get_name()
    action.description = instance_offering_option.get_description()

    evt = execute_action_with_session(http_server_ip, action, session_uuid)
    test_util.action_logger('create instance offering: name: %s cpuNum: %s, memorySize: %s, allocatorStrategy:%s, type: %s '\
            % (action.name, action.cpuNum, action.memorySize, action.allocatorStrategy, action.type))
    test_util.test_logger('Instance Offering: %s is created' % evt.inventory.uuid)
    return evt.inventory

def attach_flat_network_service_to_l3network(http_server_ip, l3_uuid, service_uuid, session_uuid=None):
    providers = {}
    action = api_actions.AttachNetworkServiceToL3NetworkAction()
    action.l3NetworkUuid = l3_uuid
    providers[service_uuid] = ['DHCP', 'Eip', 'Userdata']
    action.networkServices = providers
    action.timeout = 12000
    evt = execute_action_with_session(http_server_ip, action, session_uuid)
    return evt

def add_data_volume_template(http_server_ip, image_option):
    action = api_actions.AddImageAction()
    action.name = image_option.get_name()
    action.url = image_option.get_url()
    action.mediaType = 'DataVolumnTemplate'
    if image_option.get_mediaType() and \
            action.mediaType != image_option.get_mediaType():
        test_util.test_warn('image type %s was not %s' % \
                (image_option.get_mediaType(), action.mediaType))

    action.format = image_option.get_format()
    action.backupStorageUuids = image_option.get_backup_storage_list()
    test_util.action_logger('Add [Volume:] %s from [url:] %s ' % (action.name, action.url))
    evt = execute_action_with_session(http_server_ip, action, image_option.get_session_uuid())

    test_util.test_logger('[volume:] %s is added.' % evt.inventory.uuid)
    return evt.inventory


def create_vm(http_server_ip, vm_create_option):
    create_vm = api_actions.CreateVmInstanceAction()
    name = vm_create_option.get_name()
    if not name:
        create_vm.name = 'test_vm_default_name'
    else:
        create_vm.name = name

    create_vm.imageUuid = vm_create_option.get_image_uuid()
    create_vm.zoneUuid = vm_create_option.get_zone_uuid()
    create_vm.clusterUuid = vm_create_option.get_cluster_uuid()
    create_vm.hostUuid = vm_create_option.get_host_uuid()
    create_vm.instanceOfferingUuid = vm_create_option.get_instance_offering_uuid()
    create_vm.l3NetworkUuids = vm_create_option.get_l3_uuids()
    create_vm.defaultL3NetworkUuid = vm_create_option.get_default_l3_uuid()
    #If there are more than 1 network uuid, the 1st one will be the default l3.
    if len(create_vm.l3NetworkUuids) > 1 and not create_vm.defaultL3NetworkUuid:
        create_vm.defaultL3NetworkUuid = create_vm.l3NetworkUuids[0]

    vm_type = vm_create_option.get_vm_type()
    if not vm_type:
        create_vm.type = 'UserVm'
    else:
        create_vm.type = vm_type

    create_vm.systemTags = vm_create_option.get_system_tags()
    create_vm.userTags = vm_create_option.get_user_tags()
    create_vm.timeout = 1200000

    create_vm.dataDiskOfferingUuids = vm_create_option.get_data_disk_uuids()
    create_vm.rootDiskOfferingUuid = vm_create_option.get_root_disk_uuid()
    create_vm.consolePassword = vm_create_option.get_console_password()
    create_vm.primaryStorageUuidForRootVolume = vm_create_option.get_ps_uuid()
    create_vm.rootPassword = vm_create_option.get_root_password()
    test_util.action_logger('Create VM: %s with [image:] %s and [l3_network:] %s' % (create_vm.name, create_vm.imageUuid, create_vm.l3NetworkUuids))
    evt = execute_action_with_session(http_server_ip, create_vm, vm_create_option.get_session_uuid())
    test_util.test_logger('[vm:] %s is created.' % evt.inventory.uuid)
    return evt.inventory

#The root volume will not be deleted immediately. It will only be reclaimed by system maintenance checking.
def destroy_vm(http_server_ip, vm_uuid, session_uuid=None):
    action = api_actions.DestroyVmInstanceAction()
    action.uuid = vm_uuid
    action.timeout = 600000
    test_util.action_logger('Destroy VM [uuid:] %s' % vm_uuid)
    evt = execute_action_with_session(http_server_ip, action, session_uuid)


def reboot_vm(http_server_ip, vm_uuid, force=None, session_uuid=None):
    action = api_actions.RebootVmInstanceAction()
    action.uuid = vm_uuid
    action.timeout = 600000
    test_util.action_logger('Reboot VM [uuid:] %s' % vm_uuid)
    evt = execute_action_with_session(http_server_ip, action, session_uuid)
    return evt.inventory

def stop_vm(http_server_ip, vm_uuid, force=None, session_uuid=None):
    action = api_actions.StopVmInstanceAction()
    action.uuid = vm_uuid
    action.type = force
    action.timeout = 600000
    test_util.action_logger('Stop VM [uuid:] %s' % vm_uuid)
    evt = execute_action_with_session(http_server_ip, action, session_uuid)
    return evt.inventory

def start_vm(http_server_ip, vm_uuid, session_uuid=None, timeout=1200000):
    cond = res_ops.gen_query_conditions('uuid', '=', vm_uuid)
    vm_inv = query_resource(http_server_ip, res_ops.VM_INSTANCE, cond).inventories[0]

    action = api_actions.StartVmInstanceAction()
    action.uuid = vm_uuid
    action.hostUuid = vm_inv.lastHostUuid
    action.timeout = timeout
    test_util.action_logger('Start VM [uuid:] %s' % vm_uuid)
    evt = execute_action_with_session(http_server_ip, action, session_uuid)
    return evt.inventory

def update_vm(http_server_ip, vm_uuid, session_uuid=None, timeout=240000):
    cond = res_ops.gen_query_conditions('uuid', '=', vm_uuid)
    vm_inv = query_resource(http_server_ip, res_ops.VM_INSTANCE, cond).inventories[0]
    return vm_inv

def create_volume_from_offering(http_server_ip, volume_option, session_uuid=None):
    action = api_actions.CreateDataVolumeAction()
    action.primaryStorageUuid = volume_option.get_primary_storage_uuid()
    action.diskOfferingUuid = volume_option.get_disk_offering_uuid()
    action.description = volume_option.get_description()
    action.systemTags = volume_option.get_system_tags()
    timeout = volume_option.get_timeout()
    if not timeout:
        action.timeout = 240000
    else:
        action.timeout = timeout

    name = volume_option.get_name()
    if not name:
        action.name = 'test_volume'
    else:
        action.name = name

    test_util.action_logger('Create [Volume:] %s with [disk offering:] %s ' % (action.name, action.diskOfferingUuid))
    evt = execute_action_with_session(http_server_ip, action, session_uuid)

    test_util.test_logger('[volume:] %s is created.' % evt.inventory.uuid)
    return evt.inventory


def lib_get_primary_storage_by_vm(http_server_ip, vm):
    ps_uuid = vm.allVolumes[0].primaryStorageUuid
    cond = res_ops.gen_query_conditions('uuid', '=', ps_uuid)
    ps = query_resource(http_server_ip, res_ops.PRIMARY_STORAGE, cond).inventories[0]
    return ps


def lib_find_random_host(http_server_ip, vm = None):
    '''
    Return a random host inventory. 
    
    If Vm is provided, the returned host should not be the host of VM. But it 
    should belong to the same cluster of VM.
    '''
    import zstackwoodpecker.header.host as host_header
    import random
    target_hosts = []
    cluster_id = None
    current_host_uuid = None
    if vm:
        current_host = lib_get_vm_host(vm)
        cluster_id = vm.clusterUuid
        current_host_uuid = current_host.uuid

    all_hosts = lib_get_cluster_hosts(http_server_ip, cluster_id)
    # TODO: it should select non-root host for migrate after cold migrate issue is fixed
    for host in all_hosts:
        if host.uuid != current_host_uuid and \
                host.status == host_header.CONNECTED and \
                host.state == host_header.ENABLED and \
                host.username == 'root' and \
                host.sshPort == 22:
            target_hosts.append(host)

    if not target_hosts:
        return None

    return random.choice(target_hosts)
	

def lib_get_cluster_hosts(http_server_ip, cluster_uuid = None):
    if cluster_uuid:
       conditions = res_ops.gen_query_conditions('clusterUuid', '=', \
               cluster_uuid)
    else:
       conditions = res_ops.gen_query_conditions('clusterUuid', '!=', \
               'impossible_uuid')

    hosts = query_resource(http_server_ip, res_ops.HOST, conditions).inventories
    return hosts


def create_volume_from_offering_refer_to_vm(http_server_ip, volume_option, vm_inv, session_uuid=None, deploy_config=None, ps_ref_type=None):

    deploy_config = deploy_config
    action = api_actions.CreateDataVolumeAction()
    action.diskOfferingUuid = volume_option.get_disk_offering_uuid()
    action.description = volume_option.get_description()
    timeout = volume_option.get_timeout()

    ps = lib_get_primary_storage_by_vm(http_server_ip, vm_inv)
    if ps.type in [ inventory.CEPH_PRIMARY_STORAGE_TYPE ]:
        action.primaryStorageUuid = volume_option.get_primary_storage_uuid()
        action.systemTags = volume_option.get_system_tags()
    elif ps.type in [ inventory.LOCAL_STORAGE_TYPE ]:
        action.primaryStorageUuid = ps.uuid
        #host = lib_find_random_host(http_server_ip)
        #action.systemTags = ["localStorage::hostUuid::%s" % host.uuid]
        if xmlobject.has_element(deploy_config, 'zones.zone.primaryStorages.xskycephPrimaryStorage'):
            action.systemTags = ["capability::virtio-scsi", "localStorage::hostUuid::%s" % vm_inv.hostUuid]
        else:
            action.systemTags = ["localStorage::hostUuid::%s" % vm_inv.hostUuid]
        if ps_ref_type:
            if ps_ref_type == 'xskyceph':
                action.systemTags = ["capability::virtio-scsi", "localStorage::hostUuid::%s" % vm_inv.hostUuid]
            else:
                action.systemTags = ["localStorage::hostUuid::%s" % vm_inv.hostUuid]
    elif ps.type in [ 'SharedBlock' ]:
        action.primaryStorageUuid = ps.uuid
    elif ps_ref_type in [ 'mini_ps' ]:
        action.systemTags = ["capability::virtio-scsi", "localStorage::hostUuid::%s" % vm_inv.hostUuid]
    else:
        test_util.test_fail("new ps type in scenario.")

    if not timeout:
        action.timeout = 240000
    else:
        action.timeout = timeout

    name = volume_option.get_name()
    if not name:
        action.name = 'test_volume'
    else:
        action.name = name

    test_util.action_logger('Create [Volume:] %s with [disk offering:] %s ' % (action.name, action.diskOfferingUuid))
    evt = execute_action_with_session(http_server_ip, action, session_uuid)

    test_util.test_logger('[volume:] %s is created.' % evt.inventory.uuid)
    return evt.inventory

def attach_volume(http_server_ip, volume_uuid, vm_uuid, session_uuid=None):
    action = api_actions.AttachDataVolumeToVmAction()
    action.vmInstanceUuid = vm_uuid
    action.volumeUuid = volume_uuid
    action.timeout = 240000
    test_util.action_logger('Attach Data Volume [uuid:] %s to [vm:] %s' % (volume_uuid, vm_uuid))
    evt = execute_action_with_session(http_server_ip, action, session_uuid)
    return evt.inventory

def detach_volume(http_server_ip, volume_uuid, vm_uuid=None, session_uuid=None):
    action = api_actions.DetachDataVolumeFromVmAction()
    action.uuid = volume_uuid
    action.vmUuid = vm_uuid
    action.timeout = 240000
    test_util.action_logger('Detach Volume [uuid:] %s' % volume_uuid)
    evt = execute_action_with_session(http_server_ip, action, session_uuid)
    return evt.inventory

def attach_l3(http_server_ip, l3_uuid, vm_uuid, session_uuid = None):
    action = api_actions.AttachL3NetworkToVmAction()
    action.l3NetworkUuid = l3_uuid
    action.vmInstanceUuid = vm_uuid
    test_util.action_logger('[Attach L3 Network:] %s to [VM:] %s' % \
            (l3_uuid, vm_uuid))
    evt = execute_action_with_session(http_server_ip, action, session_uuid)
    test_util.test_logger('[L3 Network:] %s has been attached to [VM:] %s' % \
            (l3_uuid, vm_uuid))
    return evt.inventory

def detach_l3(http_server_ip, nic_uuid, session_uuid = None):
    action = api_actions.DetachL3NetworkFromVmAction()
    action.vmNicUuid = nic_uuid
    test_util.action_logger('[Detach L3 Network Nic]: %s' % nic_uuid)
    evt = execute_action_with_session(http_server_ip, action, session_uuid)
    test_util.test_logger('[L3 Network Nic]: %s has been detached'% nic_uuid)
    return evt.inventory

def create_security_group(http_server_ip, security_group_option, session_uuid=None):
    action = api_actions.CreateSecurityGroupAction()
    name = security_group_option.get_name()
    if not name:
        action.name = 'security_group'
    else:
        action.name = name
    action.timeout = 240000
    test_util.action_logger('Create [SecurityGroup:] %s ' %action.name)
    evt = execute_action_with_session(http_server_ip, action, session_uuid)
    test_util.test_logger('[SecurityGroup:] %s is created.' % evt.inventory.uuid)
    return evt.inventory

def add_vm_nic_to_security_group(http_server_ip, security_group_uuid, vm_nic_uuid, session_uuid=None):
    action = api_actions.AddVmNicToSecurityGroupAction()
    action.securityGroupUuid = security_group_uuid
    action.vmNicUuids = [vm_nic_uuid]
    action.timeout = 240000
    test_util.action_logger('Add [VmNic:] %s to [SecurityGroup:] %s ' %(action.vmNicUuids, action.securityGroupUuid))
    execute_action_with_session(http_server_ip, action, session_uuid)

def attach_security_group_to_l3network(http_server_ip, security_group_uuid, l3network_uuid, session_uuid=None):
    action = api_actions.AttachSecurityGroupToL3NetworkAction()
    action.securityGroupUuid = security_group_uuid
    action.l3NetworkUuid = l3network_uuid
    action.timeout = 240000
    test_util.action_logger('Attach SecurityGroup [uuid:] %s to L3Network [uuid:] %s' % (security_group_uuid, l3network_uuid))
    evt = execute_action_with_session(http_server_ip, action, session_uuid)
    return evt.inventory

def use_snapshot(http_server_ip, snapshot_uuid, session_uuid=None):
    action = api_actions.RevertVolumeFromSnapshotAction()
    action.uuid = snapshot_uuid
    action.timeout = 4800000
    test_util.action_logger('Revert Volume by [Snapshot:] %s ' % snapshot_uuid)
    evt = execute_action_with_session(http_server_ip, action, session_uuid)
    return evt

def query_resource(http_server_ip, resource, conditions = [], session_uuid=None, count='false'):
    action = res_ops._gen_query_action(resource, conditions)
    action.conditions = conditions
    ret = execute_action_with_session(http_server_ip, action, session_uuid)
    return ret

def create_vpc_vrouter(http_server_ip, name, virtualrouter_offering_uuid, resource_uuid=None, system_tags=None, use_tags=None, session_uuid=None):
    action = api_actions.CreateVpcVRouterAction()
    action.timeout = 300000
    action.name = name
    action.virtualRouterOfferingUuid = virtualrouter_offering_uuid
    action.resourceUuid = resource_uuid
    action.systemTags = system_tags
    action.userTags = use_tags
    evt = execute_action_with_session(http_server_ip, action, session_uuid)
    return evt.inventory

def change_instance_offering_state(http_server_ip, offering_uuid, state_event, system_tags=None, user_tags=None, session_uuid=None):
    action = api_actions.ChangeInstanceOfferingStateAction()
    action.uuid = offering_uuid
    action.stateEvent = state_event
    action.systemTags = system_tags
    action.userTags = user_tags
    action.timeout = 30000
    evt = execute_action_with_session(http_server_ip, action, session_uuid)
    return evt

def migrate_vm(http_server_ip, vm_uuid, host_uuid, timeout = 480000, session_uuid = None):
    action = api_actions.MigrateVmAction()
    action.vmInstanceUuid = vm_uuid
    action.hostUuid = host_uuid
    if not timeout:
        timeout = 480000
    action.timeout = timeout
    test_util.action_logger('Migrate VM [uuid:] %s to Host [uuid:] %s, in timeout: %s' % (vm_uuid, host_uuid, timeout))
    evt = execute_action_with_session(http_server_ip, action, session_uuid)
    return evt.inventory

def create_l2_vlan(http_server_ip, name, physicalInterface, vlan, zone_uuid, session_uuid = None):
    action = api_actions.CreateL2VlanNetworkAction()
    action.name = name
    action.physicalInterface = physicalInterface
    action.vlan = vlan
    action.zoneUuid = zone_uuid
    action.timeout = 300000
    evt = execute_action_with_session(http_server_ip, action, session_uuid)
    return evt

def create_l2_vxlan(http_server_ip, name, pool_uuid, zone_uuid, session_uuid=None):
    action = api_actions.CreateL2VxlanNetworkAction()
    action.timeout = 30000
    action.name = name
    action.poolUuid = pool_uuid
    action.zoneUuid = zone_uuid
    evt = execute_action_with_session(http_server_ip, action, session_uuid)
    test_util.action_logger('Create L2 Vxlan network [name:] %s, [poolUuid:] %s, [zoneUuid:] %s' \
                             %(name, pool_uuid, zone_uuid))
    return evt

def delete_l2(http_server_ip, l2_uuid, session_uuid = None):
    action = api_actions.DeleteL2NetworkAction()
    action.uuid = l2_uuid
    action.timeout = 300000
    evt = execute_action_with_session(http_server_ip, action, session_uuid)
    return evt

def attach_l2(http_server_ip, l2_uuid, cluster_uuid, session_uuid = None):
    action = api_actions.AttachL2NetworkToClusterAction()
    action.clusterUuid = cluster_uuid
    action.l2NetworkUuid = l2_uuid
    evt = execute_action_with_session(http_server_ip, action, session_uuid)
    return evt

def create_l3(http_server_ip, l3Name, type, l2_uuid, dnsDomain, session_uuid = None):
    action = api_actions.CreateL3NetworkAction()
    action.sessionUuid = session_uuid
    action.l2NetworkUuid = l2_uuid
    action.name = l3Name
    action.type = type
    action.dnsDomain = dnsDomain
    evt = execute_action_with_session(http_server_ip, action, session_uuid)
    return evt

def attach_network_service_to_l3network(http_server_ip, l3_uuid, service_uuid, session_uuid=None):
    providers = {}
    action = api_actions.AttachNetworkServiceToL3NetworkAction()
    action.l3NetworkUuid = l3_uuid
    providers[service_uuid] = ['VRouterRoute'] 
    action.networkServices = providers
    action.timeout = 12000
    evt = execute_action_with_session(http_server_ip, action, session_uuid)
    return evt

def add_dns_to_l3(http_server_ip, l3_uuid, dns, session_uuid=None):
    action = api_actions.AddDnsToL3NetworkAction()
    action.sessionUuid = session_uuid
    action.dns = dns
    action.l3NetworkUuid = l3_uuid
    evt = execute_action_with_session(http_server_ip, action, session_uuid)
    return evt

def add_ip_range(http_server_ip, name, l3_uuid, start_ip, end_ip, gateway, netmask, session_uuid=None):
    action = api_actions.AddIpRangeAction()
    action.sessionUuid = session_uuid
    action.startIp = start_ip
    action.endIp = end_ip
    action.gateway = gateway
    action.l3NetworkUuid = l3_uuid
    action.name = name
    action.netmask = netmask
    evt = execute_action_with_session(http_server_ip, action, session_uuid)
    return evt

def add_network_service(http_server_ip, l3_uuid, allservices, session_uuid=None): 
    action = api_actions.AttachNetworkServiceToL3NetworkAction()
    action.sessionUuid = session_uuid
    action.l3NetworkUuid = l3_uuid
    action.networkServices = allservices
    evt = execute_action_with_session(http_server_ip, action, session_uuid)
    return evt

def delete_image(http_server_ip, image_uuid, session_uuid=None):
    action = api_actions.DeleteImageAction()
    action.uuid = image_uuid
    evt = execute_action_with_session(http_server_ip, action, session_uuid)
    return evt

def expunge_image(http_server_ip, image_uuid, session_uuid=None):
    action = api_actions.ExpungeImageAction()
    action.imageUuid = image_uuid
    evt = execute_action_with_session(http_server_ip, action, session_uuid)
    return evt

def delete_vol(http_server_ip, vol_uuid, session_uuid=None):
    action = api_actions.DeleteDataVolumeAction()
    action.uuid = vol_uuid
    evt = execute_action_with_session(http_server_ip, action, session_uuid)
    return evt

def expunge_vol(http_server_ip, vol_uuid, session_uuid=None):
    action = api_actions.ExpungeDataVolumeAction()
    action.uuid = vol_uuid
    evt = execute_action_with_session(http_server_ip, action, session_uuid)
    return evt

def attach_l3(http_server_ip, l3_uuid, vm_uuid, session_uuid = None):
    action = api_actions.AttachL3NetworkToVmAction()
    action.l3NetworkUuid = l3_uuid
    action.vmInstanceUuid = vm_uuid
    evt = execute_action_with_session(http_server_ip, action, session_uuid)
    return evt.inventory

def get_mn_ha_storage_type(scenario_config, scenario_file, deploy_config):
    for host in xmlobject.safe_list(scenario_config.deployerConfig.hosts.host):
        for vm in xmlobject.safe_list(host.vms.vm):
            if xmlobject.has_element(vm, 'primaryStorageRef'):
                for ps_ref in xmlobject.safe_list(vm.primaryStorageRef):
			return ps_ref.type_

def get_host_management_ip(scenario_config, scenario_file, deploy_config, vm_inv, vm_config):
    vr_offering = None
    if deploy_config.hasattr('instanceOfferings'):
        if deploy_config.instanceOfferings.hasattr('virtualRouterOffering'):
            vr_offering = deploy_config.instanceOfferings.virtualRouterOffering
    # TODO: May have multiple virtualrouter offering
    if vr_offering != None and vr_offering.publicL3NetworkRef.text_ != vr_offering.managementL3NetworkRef.text_:
        for zone in xmlobject.safe_list(deploy_config.zones.zone):
            if hasattr(zone.l2Networks, 'l2NoVlanNetwork'):
                for l2novlannetwork in xmlobject.safe_list(zone.l2Networks.l2NoVlanNetwork):
                    for l3network in xmlobject.safe_list(l2novlannetwork.l3Networks.l3BasicNetwork):
                        if l3network.name_ == vr_offering.managementL3NetworkRef.text_: 
                            for vm_l3network in xmlobject.safe_list(vm_config.l3Networks.l3Network):
                                if hasattr(vm_l3network, 'l2NetworkRef'):
                                    for vm_l2networkref in xmlobject.safe_list(vm_l3network.l2NetworkRef):
                                        if vm_l2networkref.text_ == l2novlannetwork.name_:
                                            return test_lib.lib_get_vm_nic_by_l3(vm_inv, vm_l3network.uuid_).ip
    else:
        return test_lib.lib_get_vm_nic_by_l3(vm_inv, vm_inv.defaultL3NetworkUuid).ip
        
    return None

def get_host_storage_network_ip(scenario_config, scenario_file, deploy_config, vm_inv, vm_config):
    for zone in xmlobject.safe_list(deploy_config.zones.zone):
        test_util.test_logger("loop in zone")
        if hasattr(zone.primaryStorages, 'fusionstorPrimaryStorage'):
            test_util.test_logger("if fstor ps")
            for fusionstorPrimaryStorage in xmlobject.safe_list(zone.primaryStorages.fusionstorPrimaryStorage):
                test_util.test_logger("loop in fstor ps")
                for vm_l3network in xmlobject.safe_list(vm_config.l3Networks.l3Network):
                    test_util.test_logger("loop in vm_l3network %s" %(str(vm_l3network)))
                    if hasattr(vm_l3network, 'primaryStorageRef'):
                        test_util.test_logger("if in vm_l3network ps %s;%s" %(vm_l3network.primaryStorageRef.text_, fusionstorPrimaryStorage.name_))
                        if vm_l3network.primaryStorageRef.text_ == fusionstorPrimaryStorage.name_:
                            test_util.test_logger("find equal one")
                            return test_lib.lib_get_vm_nic_by_l3(vm_inv, vm_l3network.uuid_).ip
    return None

def map_ip_range(ip_addr):
    net_addr = ip_addr.split('.')
    net_addr[-1] = '0'
    return ('.').join(net_addr)

def map_ip_gateway(ip_addr):
    net_addr = ip_addr.split('.')
    net_addr[-1] = '1'
    return ('.').join(net_addr)

def install_ebs_pkg_in_host(hostname, username, password):
    extra_ev_path = '/opt/zstack-dvd/Extra/qemu-kvm-ev'
    vrbd_pkg = os.getenv('ebsVrbd')
    tdc_pkg = os.getenv('ebdTdc')
    scp_vrbd = 'sshpass -p password scp -o StrictHostKeyChecking=no -o LogLevel=quiet -o UserKnownHostsFile=/dev/null %s %s' % (vrbd_pkg, extra_ev_path)
    scp_tdc = 'sshpass -p password scp -o StrictHostKeyChecking=no -o LogLevel=quiet -o UserKnownHostsFile=/dev/null %s %s' % (tdc_pkg, extra_ev_path)
    install_createrepo = 'yum --nogpgcheck localinstall -y /opt/zstack-dvd/Packages/createrepo*.rpm'
    createrepo_cmd = 'createrepo ' + extra_ev_path
    for cmd in [install_createrepo, scp_vrbd, scp_tdc, createrepo_cmd]:
        ssh.execute(cmd, hostname, username, password, True, 22)
        time.sleep(1)

def deploy_scenario(scenario_config, scenario_file, deploy_config):
    vm_inv_lst = []
    vm_cfg_lst = []
    eip_lst = []
    vip_lst = []
    ocfs2smp_shareable_volume_is_created = False
    zstack_management_ip = scenario_config.basicConfig.zstackManagementIp.text_
    root_xml = etree.Element("deployerConfig")
    vms_xml = etree.SubElement(root_xml, 'vms')
    poolName = os.environ.get('poolName')
    primaryStorageUuid = os.environ.get('primaryStorageUuid')

    cmd = "systemctl disable mariadb"
    test_util.test_logger("@@@DEBUG-> change solomode@@@ %s" %(cmd))
    os.system(cmd)
    cmd = "systemctl stop mariadb"
    test_util.test_logger("@@@DEBUG-> change solomode@@@ %s" %(cmd))
    os.system(cmd)
    cmd = "systemctl disable httpd"
    test_util.test_logger("@@@DEBUG-> change solomode@@@ %s" %(cmd))
    os.system(cmd)
    cmd = "systemctl stop httpd"
    test_util.test_logger("@@@DEBUG-> change solomode@@@ %s" %(cmd))
    os.system(cmd)

    if hasattr(scenario_config.deployerConfig, 'vpcVrouters'):
        # Need to clean up left over VPC Vrouters
        scenvpcVrouterCleanPattern = os.environ.get('scenvpcVrouterCleanPattern')
        if scenvpcVrouterCleanPattern != None and scenvpcVrouterCleanPattern != "":
            conf = res_ops.gen_query_conditions('name', 'like', '%%%s%%' % (scenvpcVrouterCleanPattern))
            vr_list = query_resource(zstack_management_ip, res_ops.APPLIANCE_VM, conf).inventories
            for vr in vr_list:
                destroy_vm(zstack_management_ip, vr.uuid_)

        conditions = res_ops.gen_query_conditions('name', '=', 'pub-man')
        vr_instance_offering = query_resource(zstack_management_ip, res_ops.INSTANCE_OFFERING, conditions).inventories[0]
        vr_instance_offering_uuid = vr_instance_offering.uuid
        vr_instance_offering_state = vr_instance_offering.state

        for vpcvrouter in xmlobject.safe_list(scenario_config.deployerConfig.vpcVrouters.vpcVrouter):
            test_util.test_logger("@@@DEBUG-> vr_instance_offering_state=:%s: and <%s>==<%s>@@@" %(vr_instance_offering_state, vr_instance_offering_uuid, vpcvrouter.virtualRouterOfferingUuid_))
            if vr_instance_offering_state == "Disabled" and vr_instance_offering_uuid == vpcvrouter.virtualRouterOfferingUuid_:
                change_instance_offering_state(zstack_management_ip, vr_instance_offering_uuid, "enable")

            vr_inv = create_vpc_vrouter(zstack_management_ip, name=vpcvrouter.name_, virtualrouter_offering_uuid=vpcvrouter.virtualRouterOfferingUuid_)

            if vr_instance_offering_state == "Disabled" and vr_instance_offering_uuid == vpcvrouter.virtualRouterOfferingUuid_:
                change_instance_offering_state(zstack_management_ip, vr_instance_offering_uuid, "disable")

    vpc_l3_uuid = None
    if hasattr(scenario_config.deployerConfig, 'l2Networks'):
        if hasattr(scenario_config.deployerConfig.l2Networks, 'l2VlanNetwork'):
            # This currently depend on mapping to hardcoded IP range
            ip_ranges = []
            for l2network in xmlobject.safe_list(scenario_config.deployerConfig.l2Networks.l2VlanNetwork):
                # Need to clean up left over VPC networks
                scenvpcZoneUuid = os.environ.get('scenvpcZoneUuid')
                scenvpcPoolUuid = os.environ.get('scenvpcPoolUuid')
                conf = res_ops.gen_query_conditions('physicalInterface', '=', '%s' % (l2network.physicalInterface_))
                l2_network_list = query_resource(zstack_management_ip, res_ops.L2_NETWORK, conf).inventories
                for l2_network in l2_network_list:
                    if l2network.vlan_ != None and l2network.vlan_ != "":
                        if str(l2_network.vlan) == str(l2network.vlan_):
                            delete_l2(zstack_management_ip, l2_network.uuid)
                #l2_inv = create_l2_vlan(zstack_management_ip, l2network.name_, l2network.physicalInterface_, l2network.vlan_, scenvpcZoneUuid).inventory
                l2_inv = create_l2_vxlan(zstack_management_ip, l2network.name_, scenvpcPoolUuid, scenvpcZoneUuid, session_uuid=None).inventory
                scenl2Clusters = os.environ.get('scenl2Clusters').split(',')
                #for scenl2cluster in scenl2Clusters:
                #    attach_l2(zstack_management_ip, l2_inv.uuid, scenl2cluster)
                for l3network in xmlobject.safe_list(l2network.l3Networks.l3BasicNetwork):
                    l3_inv = create_l3(zstack_management_ip, l3network.name_, l3network.type_, l2_inv.uuid, l3network.domain_name_, session_uuid = None).inventory
                    vpc_l3_uuid = l3_inv.uuid
                    if xmlobject.has_element(l3network, 'dns'):
                        for dns in xmlobject.safe_list(l3network.dns):
                            add_dns_to_l3(zstack_management_ip, l3_inv.uuid, dns.text_)
                    if xmlobject.has_element(l3network, 'ipRange'):
                        for ir in xmlobject.safe_list(l3network.ipRange):
                            add_ip_range(zstack_management_ip, ir.name_, l3_inv.uuid, ir.startIp_, ir.endIp_, ir.gateway_, ir.netmask_)
                            if map_ip_range(ir.gateway_) not in ip_ranges:
                                ip_ranges.append(map_ip_range(ir.gateway_))
                                last_ip_range = map_ip_range(ir.gateway_)
                                last_ip_gateway = map_ip_gateway(ir.gateway_)
                                last_ip_netmask = ir.netmask_
                    if xmlobject.has_element(l3network, 'networkService'):
                        network_provider_list = query_resource(zstack_management_ip, res_ops.NETWORK_SERVICE_PROVIDER, []).inventories
                        providers = {}
                        for network_provider in network_provider_list:
                            providers[network_provider.name] = network_provider.uuid
                        allservices = {}
                        has_dhcp_service = False
                        for ns in xmlobject.safe_list(l3network.networkService):
                            puuid = providers.get(ns.provider_)
                            if not puuid:
                                raise test_util.TestError('cannot find network service provider[%s], it may not have been added' % ns.provider_)

                            servs = []
                            for nst in xmlobject.safe_list(ns.serviceType):
                                servs.append(nst.text_)
                                if nst.text_ == "DHCP":
                                    has_dhcp_service = True
                            allservices[puuid] = servs

                        add_network_service(zstack_management_ip, l3_inv.uuid, allservices)
                    attach_l3(zstack_management_ip, l3_inv.uuid, vr_inv.uuid)
        woodpecker_vm_ip = shell.call("ip r | grep src | head -1 | awk '{print $NF}'").strip()
        cond = res_ops.gen_query_conditions('vmNics.ip', '=', woodpecker_vm_ip)
        woodpecker_vm = query_resource(zstack_management_ip, res_ops.VM_INSTANCE, cond).inventories[0]
        attach_l3(zstack_management_ip, l3_inv.uuid, woodpecker_vm.uuid)
        if not has_dhcp_service:
            cond = res_ops.gen_query_conditions('vmInstanceUuid', '=', woodpecker_vm.uuid)
            cond = res_ops.gen_query_conditions('usedIp.gateway', '=', last_ip_gateway, cond)
            vm_nic = query_resource(zstack_management_ip, res_ops.VM_NIC, cond).inventories[0]
            ip_addr = vm_nic.ip
            shell.call("zs-network-setting -i eth0 %s %s|exit 0" %(ip_addr, last_ip_netmask) )

        shell.call("if [ `ps -ef|grep dhclient|grep -v 'grep'|wc -l` -ne 0 ]; then pkill -9 dhclient;fi") #kill dhclient process if exist
        shell.call('dhclient eth0')
        shell.call('ip route del default || true')
        shell.call('ip route add default via %s dev eth0' % last_ip_gateway)
        shell.call('ip route del 192.168.0.0/16 || true')
#        for ip_range in ip_ranges:
#            if last_ip_range != ip_range:
#                shell.call('ip route del %s/24 || true' % ip_range)
#                shell.call('ip route add %s/24 via %s dev eth0' % (ip_range, last_ip_gateway))

    mn_ip_to_post, vm_ip_to_post = (None, None)
    mini_cnt = 0
    if hasattr(scenario_config.deployerConfig, 'hosts'):
        ebs_host = {}
        ceph_disk_created = False
        for host in xmlobject.safe_list(scenario_config.deployerConfig.hosts.host):
            for vm in xmlobject.safe_list(host.vms.vm):
                vm_creation_option = test_util.VmOption()
                l3_uuid_list = []
                l3_uuid_list_ge_3 = []
                default_l3_uuid = None
                l3_cnt = 0
                for l3network in xmlobject.safe_list(vm.l3Networks.l3Network):
                    if hasattr(l3network, 'scenl3NetworkRef'):
                        for scenl3networkref in xmlobject.safe_list(l3network.scenl3NetworkRef):
                            conf = res_ops.gen_query_conditions('name', '=', '%s' % (scenl3networkref.text_))
                            l3_network = query_resource(zstack_management_ip, res_ops.L3_NETWORK, conf).inventories[0]
                        l3_uuid_list.append(l3_network.uuid)
                        if not default_l3_uuid:
                            default_l3_uuid = l3_network.uuid
                    else:
                        l3_uuid_list.append(l3network.uuid_)
                        if not default_l3_uuid:
                            default_l3_uuid = l3network.uuid_

                if len(l3_uuid_list) >=3:
                    for l3_uuid in l3_uuid_list:
                        if l3_uuid == os.environ.get('vmStorageL3Uuid') or l3_uuid == os.environ.get('vmManageL3Uuid'): 
                            l3_uuid_list_ge_3.append(l3_uuid)
                            l3_uuid_list.remove(l3_uuid)
                            if len(l3_uuid_list) < 3:
                                break

                vm_creation_option.set_instance_offering_uuid(vm.vmInstranceOfferingUuid_)
                vm_creation_option.set_l3_uuids(l3_uuid_list)
                vm_creation_option.set_image_uuid(vm.imageUuid_)
                vm_creation_option.set_name(vm.name_)
                vm_creation_option.set_timeout(1200000)
#                 if vm.dataDiskOfferingUuid__:
#                     vm_creation_option.set_data_disk_uuids([vm.dataDiskOfferingUuid_])
                #vm_creation_option.set_host_uuid(host.uuid_)
                #vm_creation_option.set_data_disk_uuids(disk_offering_uuids)
                #vm_creation_option.set_default_l3_uuid(default_l3_uuid)
                #vm_creation_option.set_system_tags(system_tags)
                #vm_creation_option.set_ps_uuid(ps_uuid)
                #vm_creation_option.set_session_uuid(session_uuid)
                if os.getenv('datacenterType') == 'AliyunEBS':
#                     vm_creation_option.set_ps_uuid(os.getenv('PSUUIDFOREBS'))
                    cond = res_ops.gen_query_conditions('type', '=', 'SharedBlock')
                    cond = res_ops.gen_query_conditions('status', '=', 'Connected', cond)
                    cond = res_ops.gen_query_conditions('state', '=', 'Enabled', cond)
                    sblk_ps_avail = query_resource(zstack_management_ip, res_ops.PRIMARY_STORAGE, cond).inventories
                    if sblk_ps_avail:
                        vm_creation_option.set_ps_uuid(sblk_ps_avail[0].uuid)
                    else:
                        test_util.test_fail('no available sblk primary storage which is enabled and connected for ebs test')
#                 if ebs_host:
#                     for k, v in ebs_host.items():
#                         if int(v['cpu']) > 6 and v['mem'] > 12:
#                             vm_creation_option.set_host_uuid(k[1])

                #if iscsiClusterUuid has been set, vm will be assigned to iscsiCluster.
                iscsi_cluster_uuid = os.environ.get('iscsiClusterUuid')
                if iscsi_cluster_uuid:
                    vm_creation_option.set_cluster_uuid(iscsi_cluster_uuid)
                #vm_creation_option.set_ps_uuid('bc97708bd0dd4a40b8a5c2da6b845b14')

                vm_inv = create_vm(zstack_management_ip, vm_creation_option)
                vm_ip = test_lib.lib_get_vm_nic_by_l3(vm_inv, default_l3_uuid).ip

                #for Mini setup
                if os.getenv('hostType') == 'miniHost':
                    if mini_cnt == 0:
                        print " mn host skip install drbd"
                        base_url = "http://192.168.200.100/mirror/kefeng.wang/mini-server/"
                        cmd = "curl %s | grep ZStack-mini-server | awk '{print $6}' |awk -F'>' '{print $1}' | awk -F'\"' '{print $2}' | tail -n1" % base_url
                        (retcode, output, erroutput) = ssh.execute(cmd, vm_ip, 'root', 'password')
                        mini_url = base_url + output
                        cmd = "cd /root; wget %s ; bash %s" % (mini_url, output)
                        (retcode, output, erroutput) = ssh.execute(cmd, vm_ip, 'root', 'password')
                    else:
                        print "Mini Host need install drbd"
                        time.sleep(60)
                        cmd = "yum install kmod-drbd84 drbd84-utils -y;depmod -a && modprobe drbd;systemctl enable drbd;systemctl start drbd"
                        ssh.execute(cmd, vm_ip, 'root', 'password', True, 22)
                mini_cnt += 1

                if vm.dataDiskOfferingUuid__:
                    volume_option = test_util.VolumeOption()
                    volume_option.set_name('data_volume')
                    volume_option.set_disk_offering_uuid(vm.dataDiskOfferingUuid__)
                    volume_inv = create_volume_from_offering_refer_to_vm(zstack_management_ip, volume_option, vm_inv)
                    attach_volume(zstack_management_ip, volume_inv.uuid, vm_inv.uuid)
                if not wait_for_target_vm_retry_after_reboot(zstack_management_ip, vm_ip, vm_inv.uuid):
                    test_util.test_fail('VM:%s can not be accessible as expected' %(vm_ip))

                #this is a walk around due to create vm with 3 networks, one network will not get ip due to 2 ifcfg-eth* file
                for l3_uuid in l3_uuid_list_ge_3:
                    attach_l3(zstack_management_ip, l3_uuid, vm_inv.uuid)
                    vm_inv = update_vm(zstack_management_ip, vm_inv.uuid)
               
                vm_xml = etree.SubElement(vms_xml, 'vm')
                vm_xml.set('name', vm.name_)
                vm_xml.set('uuid', vm_inv.uuid)
                vm_xml.set('ip', vm_ip)
                if not xmlobject.has_element(vm, 'vcenterRef'):
                    setup_vm_no_password(vm_inv, vm, deploy_config)
                    setup_vm_console(vm_inv, vm, deploy_config)
                    ensure_nic_all_have_cfg(vm_inv, vm, len(l3_uuid_list+l3_uuid_list_ge_3))
                    # NOTE: need to make filesystem in sync in VM before cold stop VM
                    reboot_vm(zstack_management_ip, vm_inv.uuid)
                    if not wait_for_target_vm_retry_after_reboot(zstack_management_ip, vm_ip, vm_inv.uuid):
                        test_util.test_fail('VM:%s can not be accessible as expected' %(vm_ip))

                ips_xml = etree.SubElement(vm_xml, 'ips')
                l3_id = 0
                for l3_uuid in l3_uuid_list+l3_uuid_list_ge_3:
                    ip_xml = etree.SubElement(ips_xml, 'ip')
                    ip = test_lib.lib_get_vm_nic_by_l3(vm_inv, l3_uuid).ip
                    ip_xml.set('ip', ip)
                    ip_xml.set('uuid', (l3_uuid_list+l3_uuid_list_ge_3)[l3_id])
                    l3_id += 1

                #setup eip
                if xmlobject.has_element(vm, 'eipRef'):
                    vm_nic = vm_inv.vm.vmNics[0]
                    vm_nic_uuid = vm_nic.uuid
                    for l3network in xmlobject.safe_list(vm.l3Networks.l3Network):
                        vip = test_stub.create_vip('scenario-auto-vip', l3network.uuid_)
                        vip_lst.append(vip)
                        eip = test_stub.create_eip(l3network.eipRef.text_, vip_uuid=vip.get_vip().uuid, vnic_uuid=vm_nic_uuid, vm_obj=vm_inv)
                        eip_lst.append(eip)
                        vip.attach_eip(eip)
                        vm_xml.set('ip', eip.get_eip().vipIp)

                if xmlobject.has_element(vm, 'nodeRef'):
                    setup_node_vm(vm_inv, vm, deploy_config)
                if xmlobject.has_element(vm, 'hostRef') and not xmlobject.has_element(vm, 'vcenterRef'):
                    setup_host_vm(zstack_management_ip, vm_inv, vm, deploy_config)
                    vm_inv_lst.append(vm_inv)
                    vm_cfg_lst.append(vm)
                    vm_management_ip = get_host_management_ip(scenario_config, scenario_file, deploy_config, vm_inv, vm)
                    if vm_management_ip:
                        vm_xml.set('managementIp', vm_management_ip)
                        if xmlobject.has_element(vm, 'nodeRef'):
                            mn_ip_to_post = vm_management_ip
#                             install_ebs_pkg_in_host(vm_ip, vm.imageUsername_, vm.imagePassword_)
                    else:
                        test_util.test_logger("@@@DEBUG-WARNING@@@: vm_management_ip is null, failed")
                    vm_storage_ip = get_host_storage_network_ip(scenario_config, scenario_file, deploy_config, vm_inv, vm)
                    if vm_storage_ip:
                        vm_xml.set('storageIp', vm_storage_ip)
                    else:
                        test_util.test_logger("@@@DEBUG-WARNING@@@: vm_storage_ip is null, failed")

                if xmlobject.has_element(vm, 'ha2MnRef'):
                    setup_2ha_mn_vm(zstack_management_ip, vm_inv, vm, deploy_config)

                if xmlobject.has_element(vm, 'mnHostRef'):
                    setup_mn_host_vm(scenario_config, scenario_file, deploy_config, vm_inv, vm)

                if not xmlobject.has_element(vm, 'vcenterRef'):
                    #walk around for ntp not start issue
                    ntp_cmd = "service ntpd start"
                    ssh.execute(ntp_cmd, vm_ip, vm.imageUsername_, vm.imagePassword_, True, 22)
                 
                if xmlobject.has_element(vm, 'backupStorageRef'):
                    volume_option = test_util.VolumeOption()
                    volume_option.set_name(os.environ.get('volumeName'))
                    for bs_ref in xmlobject.safe_list(vm.backupStorageRef):
                        if bs_ref.type_ in ['ceph', 'xskyceph']:
#                         if bs_ref.type_ == 'ceph':
                            disk_offering_uuid = bs_ref.offering_uuid_
                            volume_option.set_disk_offering_uuid(disk_offering_uuid)
                            if primaryStorageUuid != None and primaryStorageUuid != "":
                                volume_option.set_primary_storage_uuid(primaryStorageUuid)
                            if poolName != None and poolName != "":
                                volume_option.set_system_tags(['ceph::pool::%s' % (poolName)])
                            #volume_inv = create_volume_from_offering(zstack_management_ip, volume_option)
                            if bs_ref.type_ == 'ceph':
                                if xmlobject.has_element(deploy_config, 'backupStorages.cephBackupStorage'):
                                    volume_inv = create_volume_from_offering_refer_to_vm(zstack_management_ip, volume_option, vm_inv)
                                else:
                                    volume_inv = create_volume_from_offering_refer_to_vm(zstack_management_ip, volume_option, vm_inv, deploy_config=deploy_config)
                            else:
                                volume_inv = create_volume_from_offering_refer_to_vm(zstack_management_ip, volume_option, vm_inv, deploy_config=deploy_config)
                            attach_volume(zstack_management_ip, volume_inv.uuid, vm_inv.uuid)
                            ceph_disk_created = True
                            break

                        if bs_ref.type_ == 'fusionstor':
                            disk_offering_uuid = bs_ref.offering_uuid_
                            volume_option.set_disk_offering_uuid(disk_offering_uuid)
                            if primaryStorageUuid != None and primaryStorageUuid != "":
                                volume_option.set_primary_storage_uuid(primaryStorageUuid)
                            if poolName != None and poolName != "":
                                volume_option.set_system_tags(['ceph::pool::%s' % (poolName)])
                            #volume_inv = create_volume_from_offering(zstack_management_ip, volume_option)
                            volume_inv = create_volume_from_offering_refer_to_vm(zstack_management_ip, volume_option, vm_inv) 
                            attach_volume(zstack_management_ip, volume_inv.uuid, vm_inv.uuid)
                            break
                    setup_backupstorage_vm(vm_inv, vm, deploy_config)
                if xmlobject.has_element(vm, 'iscsiLunRef'):
                    for lun_ref in xmlobject.safe_list(vm.iscsiLunRef):
                        if lun_ref.type_ == 'iscsiTarget':
                            iscsi_disk_offering_uuid = lun_ref.disk_offering_uuid_
                            volume_option.set_disk_offering_uuid(iscsi_disk_offering_uuid)
                            iscsi_share_volume_inv = create_volume_from_offering_refer_to_vm(zstack_management_ip, volume_option, vm_inv)
                            attach_volume(zstack_management_ip, iscsi_share_volume_inv.uuid, vm_inv.uuid)
                            global ISCSI_TARGET_IP
                            global ISCSI_TARGET_UUID
                            ISCSI_TARGET_UUID.append(vm_inv.uuid)
                            ISCSI_TARGET_IP.append(vm_ip)
                            test_util.test_logger("ISCSI_TARGET_IP=%s" %(vm_ip))
                            #setup_iscsi_target(vm_inv, vm, deploy_config)
			    #setup_iscsi_target_kernel(zstack_management_ip, vm_inv, vm, deploy_config)
                            break

                if xmlobject.has_element(vm, 'primaryStorageRef'):
                    vm_ip_to_post = setup_primarystorage_vm(vm_inv, vm, deploy_config)
                    for ps_ref in xmlobject.safe_list(vm.primaryStorageRef):
                        if ps_ref.type_ == 'ocfs2smp':
                            if ocfs2smp_shareable_volume_is_created == False and hasattr(ps_ref, 'disk_offering_uuid_'):
				# Only sharedblock or ceph support shared volume right now
                                cond = res_ops.gen_query_conditions('type', '=', 'SharedBlock')
                                cond = res_ops.gen_query_conditions('status', '=', 'Connected', cond)
                                cond = res_ops.gen_query_conditions('state', '=', 'Enabled', cond)
                                sblk_ps_avail = query_resource(zstack_management_ip, res_ops.PRIMARY_STORAGE, cond).inventories
                                if sblk_ps_avail:
				    volume_option.set_primary_storage_uuid(sblk_ps_avail[0].uuid)
                                else:
                                    test_util.test_fail('no available sblk primary storage which is enabled and connected for ebs test')

                                ocfs2smp_disk_offering_uuid = ps_ref.disk_offering_uuid_
                                volume_option.set_disk_offering_uuid(ocfs2smp_disk_offering_uuid)
                                if poolName != None and poolName != "":
                                    volume_option.set_system_tags(['ephemeral::shareable', 'capability::virtio-scsi', 'ceph::pool::%s' % (poolName)])
                                else:
                                    volume_option.set_system_tags(['ephemeral::shareable', 'capability::virtio-scsi'])
                                share_volume_inv = create_volume_from_offering(zstack_management_ip, volume_option)
				#share_volume_inv = create_volume_from_offering_refer_to_vm(zstack_management_ip, volume_option, vm_inv) 
                                ocfs2smp_shareable_volume_is_created = True
                            attach_volume(zstack_management_ip, share_volume_inv.uuid, vm_inv.uuid)
                        elif ps_ref.type_ == 'iscsiTarget':
                            iscsi_disk_offering_uuid = ps_ref.disk_offering_uuid_
                            volume_option.set_disk_offering_uuid(iscsi_disk_offering_uuid)
                            iscsi_share_volume_inv = create_volume_from_offering_refer_to_vm(zstack_management_ip, volume_option, vm_inv) 
                            attach_volume(zstack_management_ip, iscsi_share_volume_inv.uuid, vm_inv.uuid)
                            global ISCSI_TARGET_IP
                            global ISCSI_TARGET_UUID
                            ISCSI_TARGET_UUID.append(vm_inv.uuid)
                            ISCSI_TARGET_IP.append(vm_ip)
                            test_util.test_logger("ISCSI_TARGET_IP=%s" %(vm_ip))
                            #setup_iscsi_target(vm_inv, vm, deploy_config)
			    #setup_iscsi_target_kernel(zstack_management_ip, vm_inv, vm, deploy_config)
                            break
                        elif ps_ref.type_ == 'iscsiInitiator':
                            setup_iscsi_initiator(zstack_management_ip, vm_inv, vm, deploy_config)
                            break
                        elif ps_ref.type_ == 'ZSES':
                            if zbs_virtio_scsi_volume_is_created == False and hasattr(ps_ref, 'disk_offering_uuid_'):
                                zbs_disk_offering_uuid = ps_ref.disk_offering_uuid_
                                volume_option.set_disk_offering_uuid(zbs_disk_offering_uuid)
                                if primaryStorageUuid != None and primaryStorageUuid != "":
                                    volume_option.set_primary_storage_uuid(primaryStorageUuid)
                                if poolName != None and poolName != "":
                                    volume_option.set_system_tags(['capability::virtio-scsi', 'ceph::pool::%s' % (poolName)])
                                else:
                                    volume_option.set_system_tags(['capability::virtio-scsi'])
                                #share_volume_inv = create_volume_from_offering(zstack_management_ip, volume_option)
                                share_volume_inv = create_volume_from_offering_refer_to_vm(zstack_management_ip, volume_option, vm_inv) 
                                zbs_virtio_scsi_volume_is_created = True
                                attach_volume(zstack_management_ip, share_volume_inv.uuid, vm_inv.uuid)
                        elif (not ceph_disk_created) and ps_ref.type_ in ['xskyceph','ceph']:
                            disk_offering_uuid = ps_ref.offering_uuid_
                            volume_option.set_disk_offering_uuid(disk_offering_uuid)
                            if primaryStorageUuid != None and primaryStorageUuid != "":
                                volume_option.set_primary_storage_uuid(primaryStorageUuid)
                            if poolName != None and poolName != "":
                                volume_option.set_system_tags(['ceph::pool::%s' % (poolName)])
                                volume_inv = create_volume_from_offering_refer_to_vm(zstack_management_ip, volume_option, vm_inv, deploy_config=deploy_config, ps_ref_type=ps_ref.type_)
                            attach_volume(zstack_management_ip, volume_inv.uuid, vm_inv.uuid)
                            break
                        elif ps_ref.type_ == 'ebs':
                            cond = res_ops.gen_query_conditions('uuid', '=', vm_inv.hostUuid)
                            host_inv = query_resource(zstack_management_ip, res_ops.HOST, cond).inventories[0]
                            ebs_host[(vm_inv.uuid, host_inv.uuid, vm_ip)] = {'cpu': host_inv.availableCpuCapacity, 'mem': int(host_inv.availableMemoryCapacity)/1024/1024/1024}
#                             install_ebs_pkg_in_host(vm_ip, vm.imageUsername_, vm.imagePassword_)
                        elif ps_ref.type_ == 'mini_ps':
                            disk_offering_uuid = ps_ref.offering_uuid_
                            volume_option.set_disk_offering_uuid(disk_offering_uuid)
                            volume_inv = create_volume_from_offering_refer_to_vm(zstack_management_ip, volume_option, vm_inv, deploy_config=deploy_config, ps_ref_type=ps_ref.type_)
                            attach_volume(zstack_management_ip, volume_inv.uuid, vm_inv.uuid)
                            break

        xml_string = etree.tostring(root_xml, 'utf-8')
        xml_string = minidom.parseString(xml_string).toprettyxml(indent="  ")
        open(scenario_file, 'w+').write(xml_string)
        if xmlobject.has_element(deploy_config, 'zones.zone.primaryStorages.xskycephPrimaryStorage') or xmlobject.has_element(deploy_config, 'backupStorages.cephBackupStorage') or xmlobject.has_element(deploy_config, 'zones.zone.primaryStorages.cephPrimaryStorage'):
#             setup_xsky_ceph_storages(scenario_config, scenario_file, deploy_config)
# #         else:
#         if xmlobject.has_element(deploy_config, 'backupStorages.cephBackupStorage'):
            setup_ceph_storages(scenario_config, scenario_file, deploy_config)
        setup_ocfs2smp_primary_storages(scenario_config, scenario_file, deploy_config, vm_inv_lst, vm_cfg_lst)
        setup_fusionstor_storages(scenario_config, scenario_file, deploy_config)
        if vm_ip_to_post and mn_ip_to_post:
            ak_id = (mn_ip_to_post + str(time.time())).replace('.', '')
#             os.environ['NASAKID'] = ak_id
            with open('/home/nas_ak_id', 'w') as f:
                f.write(ak_id)
            uri = 'http://' + os.getenv('apiEndPoint').split('::')[-1] + '/mntarget'
            http.json_dump_post(uri, {"ak_id": ak_id, "mn_ip": mn_ip_to_post, "nfs_ip": vm_ip_to_post})
#         if ebs_host:
#             target_host = None
#             host_list= [h[1] for h in ebs_host.keys()]
#             host_set = set(host_list)
#             if 1 < len(host_set) < len(ebs_host.keys()):
#                 vm_to_migr, host_to_escape, _vm_ip = [v for (v, _h) in ebs_host.keys() if host_list.count(_h) < 2]
#                 host_set.remove(host_to_escape)
#                 target_host = list(host_set)[0]
#                 migrate_vm(zstack_management_ip, vm_to_migr, target_host)
#                 stop_vm(zstack_management_ip, vm_to_migr)
#                 start_vm(zstack_management_ip, vm_to_migr)
#                 test_lib.lib_wait_target_up(_vm_ip, '22', 360)
#             elif len(host_set) == len(ebs_host.keys()):
#                 target_host = [k[1] for k, v in ebs_host.items() if int(v['cpu']) >= 16 and v['mem'] > 30]
#                 if target_host:
#                     for key in ebs_host.keys():
#                         if key[1] != target_host[0]:
#                             migrate_vm(zstack_management_ip, key[0], target_host[0])
#                             stop_vm(zstack_management_ip, key[0])
#                             start_vm(zstack_management_ip, key[0])
#                             test_lib.lib_wait_target_up(key[-1], '22', 360)
#                 else:
#                     test_util.test_fail('Cannot migrate ebs host vm to the same real host')
    else:
        setup_xsky_storages(scenario_config, scenario_file, deploy_config)
    #setup_zbs_primary_storages(scenario_config, scenario_file, deploy_config, vm_inv_lst, vm_cfg_lst)

    if hasattr(scenario_config.deployerConfig, 'volumes'):
        for volume in xmlobject.safe_list(scenario_config.deployerConfig.volumes.volume):
            volume_option = test_util.VolumeOption()
            if volume.name_ != '':
                volume_option.set_name(volume.name_)
            else:
                volume_option.set_name('data_volume')
            volume_option.set_disk_offering_uuid(volume.volumeDiskOfferingUuid_)
            if primaryStorageUuid != None and primaryStorageUuid != "":
                volume_option.set_primary_storage_uuid(primaryStorageUuid)
            if poolName != None and poolName != "":
                volume_option.set_system_tags(['ceph::pool::%s' % (poolName)])
            #volume_inv = create_volume_from_offering(zstack_management_ip, volume_option)
            volume_inv = create_volume_from_offering_refer_to_vm(zstack_management_ip, volume_option, vm_inv) 
            for vm in xmlobject.safe_list(volume.vms.vm):
                vm_uuid = ''
                for vm_inv in vm_inv_lst:
                    if vm_inv.name == vm.text_:
                        vm_uuid = vm_inv.uuid
                if vm_uuid != '':
                    attach_volume(zstack_management_ip, volume_inv.uuid, vm_uuid)

    if hasattr(scenario_config.deployerConfig, 'securityGroups'):
        for securityGroup in xmlobject.safe_list(scenario_config.deployerConfig.securityGroups.securityGroup):
            security_group_option = test_util.SecurityGroupOption()
            if securityGroup.name_ != '':
                security_group_option.set_name(securityGroup.name_)
            else:
                security_group_option.set_name('security_group')
            security_group_inv = create_security_group(zstack_management_ip, security_group_option) 

            if securityGroup.l3NetworkUuid_ != '':
                attach_security_group_to_l3network(zstack_management_ip, security_group_inv.uuid, securityGroup.l3NetworkUuid_)

            #Add zstack management vm nic to security group  
            #zstest_vm_hostname = os.popen('hostname|sed s/-/./g') 
            #zstest_vm_ip = zstest_vm_hostname.read().strip('\n')
            #cond = res_ops.gen_query_conditions('vmNics.ip', '=', zstest_vm_ip)
            #zstack_management_vm_uuid = query_resource(zstack_management_ip, res_ops.VM_INSTANCE, cond).inventories[0].uuid
            #cond = res_ops.gen_query_conditions('vmInstance.uuid', '=', zstack_management_vm_uuid)
            #cond = res_ops.gen_query_conditions('l3Network.uuid', '=', securityGroup.l3NetworkUuid_, cond )
            #vm_nic_uuid = query_resource(zstack_management_ip, res_ops.VM_NIC, cond).inventories[0].uuid
            #add_vm_nic_to_security_group(zstack_management_ip, security_group_inv.uuid, vm_nic_uuid)

            for vm in xmlobject.safe_list(securityGroup.vms.vm):
                vm_uuid = ''
                for vm_inv in vm_inv_lst:
                    if vm_inv.name == vm.text_:
                        vm_uuid = vm_inv.uuid
                    if vm_uuid != '' and vm_uuid != zstack_management_vm_uuid:
                        cond = res_ops.gen_query_conditions('vmInstance.uuid', '=', vm_uuid)
                        cond = res_ops.gen_query_conditions('l3Network.uuid', '=', securityGroup.l3NetworkUuid_, cond )
                        vm_nic_uuid = query_resource(zstack_management_ip, res_ops.VM_NIC, cond).inventories[0].uuid
                        #add_vm_nic_to_security_group(zstack_management_ip, security_group_inv.uuid, vm_nic_uuid)

def destroy_scenario(scenario_config, scenario_file):
    #below is for vpc ceph destroy l2 without debugging, we'll continue to complete this in the future.
    #if hasattr(scenario_config.deployerConfig, 'l2Networks'):
    #    if hasattr(scenario_config.deployerConfig.l2Networks, 'l2VlanNetwork'):
    #        # This currently depend on mapping to hardcoded IP range
    #        ip_ranges = []
    #        for l2network in xmlobject.safe_list(scenario_config.deployerConfig.l2Networks.l2VlanNetwork):
    #            # Need to clean up left over VPC networks
    #            scenvpcZoneUuid = os.environ.get('scenvpcZoneUuid')
    #            scenvpcPoolUuid = os.environ.get('scenvpcPoolUuid')
    #            conf = res_ops.gen_query_conditions('physicalInterface', '=', '%s' % (l2network.physicalInterface_))
    #            l2_network_list = query_resource(zstack_management_ip, res_ops.L2_NETWORK, conf).inventories
    #            for l2_network in l2_network_list:
    #                if l2network.vlan_ != None and l2network.vlan_ != "":
    #                    if str(l2_network.vlan) == str(l2network.vlan_):
    #                        delete_l2(zstack_management_ip, l2_network.uuid)

    with open(scenario_file, 'r') as fd:
        xmlstr = fd.read()
        fd.close()
        scenario_file = xmlobject.loads(xmlstr)
        zstack_management_ip = scenario_config.basicConfig.zstackManagementIp.text_
        for vm in xmlobject.safe_list(scenario_file.vms.vm):
            #delete eip
            if xmlobject.has_element(vm, 'eipRef'):
                for l3network in xmlobject.safe_list(vm.l3Networks.l3Network):
                    for eip in eip_lst:
                        eip.delete()
                    for vip in vip_lst:
                        vip.delete()
            destroy_vm(zstack_management_ip, vm.uuid_)
            try:
                cond_image = res_ops.gen_query_conditions('name', 'like', 'ebs-test-image-' + vm.uuid_ + '%')
                ebs_test_image = query_resource(zstack_management_ip, res_ops.IMAGE, cond_image).inventories
                for img in ebs_test_image:
                    delete_image(zstack_management_ip, img.uuid)
                    expunge_image(zstack_management_ip, img.uuid)
                cond_disk = res_ops.gen_query_conditions('name', 'like', 'ebs-test-disk-' + vm.uuid_ + '%')
                ebs_test_disk = query_resource(zstack_management_ip, res_ops.VOLUME, cond_disk).inventories
                for vol in ebs_test_disk:
                    delete_vol(zstack_management_ip, vol.uuid)
                    expunge_vol(zstack_management_ip, vol.uuid)
            except:
                pass

