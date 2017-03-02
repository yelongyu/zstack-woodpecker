'''

scenario operations for setup zstack test.

@author: quarkonics
'''

import apibinding.api_actions as api_actions
from apibinding import api
import zstacklib.utils.xmlobject as xmlobject
import xml.etree.cElementTree as etree
import apibinding.inventory as inventory
import os
import sys
import traceback
import xml.dom.minidom as minidom
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstacklib.utils.ssh as ssh

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
    logout.timeout = 60000
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
    return None

def get_deploy_host(vm_name, deploy_config):
    for zone in xmlobject.safe_list(deploy_config.zones.zone):
        for cluster in xmlobject.safe_list(zone.clusters.cluster):
            for host in xmlobject.safe_list(cluster.hosts.host):
                if host.name_ == vm_name:
                    return host

def setup_host_vm(vm_inv, vm_config, deploy_config):
    vm_ip = test_lib.lib_get_vm_nic_by_l3(vm_inv, vm_inv.defaultL3NetworkUuid).ip
    cmd = 'hostnamectl set-hostname %s' % (vm_ip.replace('.', '-'))
    ssh.execute(cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, 22)

    udev_config = ''
    nic_id = 0
    for l3network in xmlobject.safe_list(vm_config.l3Networks.l3Network):
        for vmnic in vm_inv.vmNics:
            if vmnic.l3NetworkUuid == l3network.uuid_:
                vmnic_mac = vmnic.mac
                break
        nic_name = None
        if hasattr(l3network, 'l2NetworkRef'):
            for l2networkref in xmlobject.safe_list(l3network.l2NetworkRef):
                nic_name = get_ref_l2_nic_name(l2networkref.text_, deploy_config)
                if nic_name.find('.') < 0:
                    break
        if nic_name == None:
            nic_name = "eth%s" % (nic_id)
        nic_id += 1

        udev_config = udev_config + '\\nACTION=="add", SUBSYSTEM=="net", DRIVERS=="?*", ATTR{type}=="1", ATTR{address}=="%s", NAME="%s"' % (vmnic_mac, nic_name)

    cmd = 'echo %s > /etc/udev/rules.d/70-persistent-net.rules' % (udev_config)
    ssh.execute(cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, 22)

    for l3network in xmlobject.safe_list(vm_config.l3Networks.l3Network):
        if hasattr(l3network, 'l2NetworkRef'):
            for l2networkref in xmlobject.safe_list(l3network.l2NetworkRef):
                nic_name = get_ref_l2_nic_name(l2networkref.text_, deploy_config)
                if nic_name.find('.') >= 0:
                    vlan = nic_name.split('.')[1]
                    test_util.test_logger('[vm:] %s %s is created.' % (vm_ip, nic_name))
                    cmd = 'vconfig add %s %s' % (nic_name.split('.')[0], vlan)
                    ssh.execute(cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, 22)

    host = get_deploy_host(vm_config.hostRef.text_, deploy_config)
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

def setup_backupstorage_vm(vm_inv, vm_config, deploy_config):
    vm_ip = test_lib.lib_get_vm_nic_by_l3(vm_inv, vm_inv.defaultL3NetworkUuid).ip
    host = get_deploy_host(vm_config.hostRef.text_, deploy_config)
    if not hasattr(host, 'port_') or host.port_ == '22':
        host.port_ = '22'

    for backupStorageRef in xmlobject.safe_list(vm_config.backupStorageRef):
        print backupStorageRef.text_
        if backupStorageRef.type_ == 'sftp':
            for sftpBackupStorage in xmlobject.safe_list(deploy_config.backupStorages.sftpBackupStorage):
                if backupStorageRef.text_ == sftpBackupStorage.name_:
                    # TODO: sftp may setup with non-root or non-default user/password port
                    test_util.test_logger('[vm:] %s setup sftp service.' % (vm_ip))
                    cmd = "mkdir -p %s" % (sftpBackupStorage.url_)
                    ssh.execute(cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, int(host.port_))
                    return

def setup_primarystorage_vm(vm_inv, vm_config, deploy_config):
    vm_ip = test_lib.lib_get_vm_nic_by_l3(vm_inv, vm_inv.defaultL3NetworkUuid).ip
    host = get_deploy_host(vm_config.hostRef.text_, deploy_config)
    if not hasattr(host, 'port_') or host.port_ == '22':
        host.port_ = '22'

    for primaryStorageRef in xmlobject.safe_list(vm_config.primaryStorageRef):
        print primaryStorageRef.text_
        for zone in xmlobject.safe_list(deploy_config.zones.zone):
            if primaryStorageRef.type_ == 'nfs':
                for nfsPrimaryStorage in xmlobject.safe_list(zone.primaryStorages.nfsPrimaryStorage):
                    if primaryStorageRef.text_ == nfsPrimaryStorage.name_:
                        test_util.test_logger('[vm:] %s setup nfs service.' % (vm_ip))
                        # TODO: multiple NFS PS may refer to same host's different DIR
                        nfsPath = nfsPrimaryStorage.url_.split(':')[1]
                        cmd = "echo '%s *(rw,sync,no_root_squash)' > /etc/exports" % (nfsPath)
                        ssh.execute(cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, int(host.port_))
                        cmd = "mkdir -p %s && service rpcbind restart && service nfs restart" % (nfsPath)
                        ssh.execute(cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, int(host.port_))
                        cmd = "iptables -w 20 -I INPUT -p tcp -m tcp --dport 2049 -j ACCEPT && iptables -w 20 -I INPUT -p udp -m udp --dport 2049 -j ACCEPT"
                        ssh.execute(cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, int(host.port_))
                        return

def get_scenario_config_vm(vm_name, scenario_config):
    for host in xmlobject.safe_list(scenario_config.deployerConfig.hosts.host):
        for vm in xmlobject.safe_list(host.vms.vm):
            if vm.name_ == vm_name:
                return vm

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

def setup_ceph_storages(scenario_config, scenario_file, deploy_config):
    ceph_storages = dict()
    for host in xmlobject.safe_list(scenario_config.deployerConfig.hosts.host):
        for vm in xmlobject.safe_list(host.vms.vm):
            vm_name = vm.name_

            if hasattr(vm, 'backupStorageRef'):
                for backupStorageRef in xmlobject.safe_list(vm.backupStorageRef):
                    print backupStorageRef.text_
                    if backupStorageRef.type_ == 'ceph':
                        if ceph_storages.has_key(backupStorageRef.text_):
                            if vm_name in ceph_storages[backupStorageRef.text_]:
                                continue
                            else:
                                ceph_storages[backupStorageRef.text_].append(vm_name)
                        else:
                            ceph_storages[backupStorageRef.text_] = [ vm_name ]

            if hasattr(vm, 'primaryStorageRef'):
                for primaryStorageRef in xmlobject.safe_list(vm.primaryStorageRef):
                    print primaryStorageRef.text_
                    for zone in xmlobject.safe_list(deploy_config.zones.zone):
                        if primaryStorageRef.type_ == 'ceph':
                            if ceph_storages.has_key(backupStorageRef.text_):
                                if vm_name in ceph_storages[backupStorageRef.text_]:
                                    continue
                                else:
                                    ceph_storages[backupStorageRef.text_].append(vm_name)
                            else:
                                ceph_storages[backupStorageRef.text_] = [ vm_name ]

    for ceph_storage in ceph_storages:
        test_util.test_logger('setup ceph [%s] service.' % (ceph_storage))
        node1_name = ceph_storages[ceph_storage][0]
        node1_config = get_scenario_config_vm(node1_name, scenario_config)
        node1_ip = get_scenario_file_vm(node1_name, scenario_file).ip_
        node_host = get_deploy_host(node1_config.hostRef.text_, deploy_config)
        if not hasattr(node_host, 'port_') or node_host.port_ == '22':
            node_host.port_ = '22'

        vm_ips = ''
        for ceph_node in ceph_storages[ceph_storage]:
            vm_nic_id = get_ceph_storages_nic_id(ceph_storage, scenario_config)
            vm = get_scenario_file_vm(ceph_node, scenario_file)
            if vm_nic_id == None:
                vm_ips += vm.ip_ + ' '
            else:
                vm_ips += vm.ips.ip[vm_nic_id].ip_ + ' '
        ssh.scp_file("%s/%s" % (os.environ.get('woodpecker_root_path'), '/tools/setup_ceph_nodes.sh'), '/tmp/setup_ceph_nodes.sh', node1_ip, node1_config.imageUsername_, node1_config.imagePassword_, port=int(node_host.port_))
        cmd = "bash -ex /tmp/setup_ceph_nodes.sh %s" % (vm_ips)
        ssh.execute(cmd, node1_ip, node1_config.imageUsername_, node1_config.imagePassword_, True, int(node_host.port_))

def setup_fusionstor_storages(scenario_config, scenario_file, deploy_config):
    fusionstors = dict()
    for host in xmlobject.safe_list(scenario_config.deployerConfig.hosts.host):
        for vm in xmlobject.safe_list(scenario_config.deployerConfig.hosts.host):
            vm_name = vm.name_

            if hasattr(vm, 'backupStorageRef'):
               for backupStorageRef in xmlobject.safe_list(vm.backupStorageRef):
                   print backupStorageRef.text_
                   if backupStorageRef.type == 'fusionstor':
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
                    for zone in xmlobject.safe_list(deploy_config.zones.zone):
                        if primaryStorageRef.type == 'fusionstor':
                            if fusionstor_storages.has_key(backupStorageRef.text_):
                                if vm_name in fusionstor_storages[backupStorageRef.text_]:
                                    continue
                                else:
                                    fusionstor_storages[backupStorageRef.text_].append(vm_name)
                            else:
                                fusionstor_storages[backupStorageRef.text_] = [ vm_name ]
    if len(fusionstor_storages) > 0:
        fusionstorPkg = os.environ['fusionstorPkg']
    else:
        return

    for fusionstor_storage in fusionstor_storages:
        test_util.test_logger('setup fusionstor [%s] service.' % (fusionstor_storage))
        node1_name = fusionstor_storages[fusionstor_storage][0]
        node1_config = get_scenario_config_vm(node1_name, scenario_config)
        node1_ip = get_scenario_file_vm(node1_name, scenario_file).ip_
        node_host = get_deploy_host(node_config.hostRef.text_, deploy_config)
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

        ssh.scp_file("%s/%s" % (os.environ.get('woodpecker_root_path'), '/tools/setup_fusionstor_nodes.sh'), '/tmp/setup_fusionstor_nodes.sh', node1_ip, node1_config.imageUsername_, node1_config.imagePassword_, port=int(node_host.port_))
        cmd = "bash -ex /tmp/setup_fusionstor_nodes.sh %s %s" % ((fusionstorPkg), (vm_ips))

def setup_ocfs2smp_primary_storages(scenario_config, scenario_file, deploy_config):
    ocfs2smp_pss = dict()
    for host in xmlobject.safe_list(scenario_config.deployerConfig.hosts.host):
        for vm in xmlobject.safe_list(host.vms.vm):
            vm_name = vm.name_
            if hasattr(vm, 'primaryStorageRef') and vm.primaryStorageRef.type_ == 'ocfs2smp':
                if ocfs2smp_pss.has_key(backupStorageRef.text_):
                    ocfs2smp_pss[primaryStorageRef.text_].append(vm_name)

    for ocfs2smp_ps_key in ocfs2smp_pss:
        test_util.test_logger('setup ocfs2 smp: %s.' % (ocfs2smp_ps_key))
	node1_name = ocfs2smp_pss[ocfs2smp_ps_key][0]
	node1_config = get_scenario_config_vm(node1_name, scenario_config)
	node1_ip = get_scenario_file_vm(node1_name, scenario_file).ip_
        node_host = get_deploy_host(node1_config.hostRef.text_, deploy_config)
        if not hasattr(node_host, 'port_') or node_host.port_ == '22':
            node_host.port_ = '22'

        vm_ips = ''
        for ocfs_node in ocfs2smp_pss[ocfs2smp_ps_key]:
            vm_nic_id = get_ceph_storages_nic_id(ocfs2smp_ps_key, scenario_config)
            vm = get_scenario_file_vm(ocfs_node, scenario_file)
            if vm_nic_id == None:
                vm_ips += vm.ip_ + ' '
            else:
	        vm_ips += vm.ips.ip[vm_nic_id].ip_ + ' '
        ssh.scp_file("%s/%s" % (os.environ.get('woodpecker_root_path'), '/tools/setup_ocfs2.sh'), '/tmp/setup_ocfs2.sh', node1_ip, node1_config.imageUsername_, node1_config.imagePassword_, port=int(node_host.port_))
        cmd = "bash -ex /tmp/setup_ocfs2.sh %s" % (vm_ips)
        ssh.execute(cmd, node1_ip, node1_config.imageUsername_, node1_config.imagePassword_, True, int(node_host.port_))

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
    timeout = vm_create_option.get_timeout()
    if not timeout:
        create_vm.timeout = 1200000
    else:
        create_vm.timeout = timeout

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
    action.timeout = 240000
    test_util.action_logger('Destroy VM [uuid:] %s' % vm_uuid)
    evt = execute_action_with_session(http_server_ip, action, session_uuid)

def stop_vm(http_server_ip, vm_uuid, force=None, session_uuid=None):
    action = api_actions.StopVmInstanceAction()
    action.uuid = vm_uuid
    action.type = force
    action.timeout = 240000
    test_util.action_logger('Stop VM [uuid:] %s' % vm_uuid)
    evt = execute_action_with_session(http_server_ip, action, session_uuid)
    return evt.inventory

def start_vm(http_server_ip, vm_uuid, session_uuid=None, timeout=240000):
    action = api_actions.StartVmInstanceAction()
    action.uuid = vm_uuid
    action.timeout = timeout
    test_util.action_logger('Start VM [uuid:] %s' % vm_uuid)
    evt = execute_action_with_session(http_server_ip, action, session_uuid)
    return evt.inventory

def create_volume_from_offering(http_server_ip, volume_option, session_uuid=None):
    action = api_actions.CreateDataVolumeAction()
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

def deploy_scenario(scenario_config, scenario_file, deploy_config):
    ocfs2smp_shareable_volume_is_created = false
    zstack_management_ip = scenario_config.basicConfig.zstackManagementIp.text_
    root_xml = etree.Element("deployerConfig")
    vms_xml = etree.SubElement(root_xml, 'vms')
    for host in xmlobject.safe_list(scenario_config.deployerConfig.hosts.host):
        for vm in xmlobject.safe_list(host.vms.vm):
            vm_creation_option = test_util.VmOption()
            l3_uuid_list = []
            default_l3_uuid = None
            for l3network in xmlobject.safe_list(vm.l3Networks.l3Network):
                if not default_l3_uuid:
                    default_l3_uuid = l3network.uuid_
                l3_uuid_list.append(l3network.uuid_)
            vm_creation_option.set_instance_offering_uuid(vm.vmInstranceOfferingUuid_)
            vm_creation_option.set_l3_uuids(l3_uuid_list)
            vm_creation_option.set_image_uuid(vm.imageUuid_)
            vm_creation_option.set_name(vm.name_)
            vm_creation_option.set_host_uuid(host.uuid_)
            #vm_creation_option.set_data_disk_uuids(disk_offering_uuids)
            #vm_creation_option.set_default_l3_uuid(default_l3_uuid)
            #vm_creation_option.set_system_tags(system_tags)
            #vm_creation_option.set_ps_uuid(ps_uuid)
            #vm_creation_option.set_session_uuid(session_uuid)
            vm_inv = create_vm(zstack_management_ip, vm_creation_option)
            vm_ip = test_lib.lib_get_vm_nic_by_l3(vm_inv, default_l3_uuid).ip
            test_lib.lib_wait_target_up(vm_ip, '22', 120)

            vm_xml = etree.SubElement(vms_xml, 'vm')
            vm_xml.set('name', vm.name_)
            vm_xml.set('uuid', vm_inv.uuid)
            vm_xml.set('ip', vm_ip)
            ips_xml = etree.SubElement(vm_xml, 'ips')
            for l3_uuid in l3_uuid_list:
                ip_xml = etree.SubElement(ips_xml, 'ip')
                ip = test_lib.lib_get_vm_nic_by_l3(vm_inv, l3_uuid).ip
                ip_xml.set('ip', ip)
            if xmlobject.has_element(vm, 'nodeRef'):
                setup_node_vm(vm_inv, vm, deploy_config)
            if xmlobject.has_element(vm, 'hostRef'):
                setup_host_vm(vm_inv, vm, deploy_config)
                vm_xml.set('managementIp', vm_ip)
            if xmlobject.has_element(vm, 'backupStorageRef'):
                volume_option = test_util.VolumeOption()
                volume_option.set_name('debug_scenario')
                for bs_ref in xmlobject.safe_list(vm.backupStorageRef):
                    if bs_ref.type_ == 'ceph':
                        disk_offering_uuid = bs_ref.offering_uuid_
                        volume_option.set_disk_offering_uuid(disk_offering_uuid)
                        volume_inv = create_volume_from_offering(zstack_management_ip, volume_option)
                        attach_volume(zstack_management_ip, volume_inv.uuid, vm_inv.uuid)
                        break

                    if bs_ref.type_ == 'fusionstor':
                        disk_offering_uuid = bs_ref.offering_uuid_
                        volume_option.set_disk_offering_uuid(disk_offering_uuid)
                        volume_inv = create_volume_from_offering(zstack_management_ip, volume_option)
                        volume_inv1 = create_volume_from_offering(zstack_management_ip, volume_option)
                        volume_inv2 = create_volume_from_offering(zstack_management_ip, volume_option)
                        attach_volume(zstack_management_ip, volume_inv.uuid, vm_inv.uuid)
                        attach_volume(zstack_management_ip, volume_inv1.uuid, vm_inv.uuid)
                        attach_volume(zstack_management_ip, volume_inv2.uuid, vm_inv.uuid)
                        break

                setup_backupstorage_vm(vm_inv, vm, deploy_config)
            if xmlobject.has_element(vm, 'primaryStorageRef'):
                setup_primarystorage_vm(vm_inv, vm, deploy_config)
                for ps_ref in xmlobject.safe_list(vm.primaryStorageRef):
                    if ps_ref.type_ == 'ocfs2smp':
                        if ocfs2smp_shareable_volume_is_created == false and hasattr(ps_ref, 'disk_offering_uuid_'):
                            ocfs2smp_disk_offering_uuid = ps_ref.disk_offering_uuid_
                            volume_option.set_disk_offering_uuid(ocfs2smp_disk_offering_uuid)
                            share_volume_inv = create_volume_from_offering(zstack_management_ip, volume_option)
                            ocfs2smp_shareable_volume_is_created = true
                        attach_volume(zstack_management_ip, share_volume_inv.uuid, vm_inv.uuid)
                        
                
    xml_string = etree.tostring(root_xml, 'utf-8')
    xml_string = minidom.parseString(xml_string).toprettyxml(indent="  ")
    open(scenario_file, 'w+').write(xml_string)
    setup_ceph_storages(scenario_config, scenario_file, deploy_config)
    setup_fusionstor_storages(scenario_config, scenario_file, deploy_config)
    setup_ocfs2smp_primary_storages(scenario_config, scenario_file, deploy_config)

def destroy_scenario(scenario_config, scenario_file):
    with open(scenario_file, 'r') as fd:
        xmlstr = fd.read()
        fd.close()
        scenario_file = xmlobject.loads(xmlstr)
        zstack_management_ip = scenario_config.basicConfig.zstackManagementIp.text_
        for vm in xmlobject.safe_list(scenario_file.vms.vm):
            destroy_vm(zstack_management_ip, vm.uuid_)
