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

def setup_node_vm(vm_ip, vm_config, deploy_config):
    for nodeRef in xmlobject.safe_list(vm_config.nodeRef):
        print nodeRef.text_

def setup_host_vm(vm_ip, vm_config, deploy_config):
    for l2networkref in xmlobject.safe_list(vm_config.l3Networks.l3Network.l2NetworkRef):
        if l2networkref.hasattr('vlan_'):
            test_util.test_logger('[vm:] %s vlan %s is created.' % (vm_ip, l2networkref.vlan_))
            cmd = 'vconfig add eth0 %s' % (l2networkref.vlan_)
            ssh.execute(cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, 22)

def setup_backupstorage_vm(vm_ip, vm_config, deploy_config):
    for backupStorageRef in xmlobject.safe_list(vm_config.backupStorageRef):
        print backupStorageRef.text_
        if backupStorageRef.type_ == 'sftp':
            for sftpBackupStorage in xmlobject.safe_list(deploy_config.backupStorages.sftpBackupStorage):
                if backupStorageRef.text_ == sftpBackupStorage.name_:
                    # TODO: sftp may setup with non-root or non-default user/password port
                    test_util.test_logger('[vm:] %s setup sftp service.' % (vm_ip))
                    cmd = "mkdir -p %s" % (sftpBackupStorage.url_)
                    ssh.execute(cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, 22)
                    return

def setup_primarystorage_vm(vm_ip, vm_config, deploy_config):
    for primaryStorageRef in xmlobject.safe_list(vm_config.primaryStorageRef):
        print primaryStorageRef.text_
        if primaryStorageRef.type_ == 'nfs':
            for zone in xmlobject.safe_list(deploy_config.zones.zone):
                for nfsPrimaryStorage in xmlobject.safe_list(zone.primaryStorages.nfsPrimaryStorage):
                    if primaryStorageRef.text_ == nfsPrimaryStorage.name_:
                        test_util.test_logger('[vm:] %s setup nfs service.' % (vm_ip))
                        # TODO: multiple NFS PS may refer to same host's different DIR
                        nfsPath = nfsPrimaryStorage.url_.split(':')[1]
                        cmd = "echo '%s *(rw,sync,no_root_squash)' > /etc/exports" % (nfsPath)
                        ssh.execute(cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, 22)
                        cmd = "mkdir -p %s && service rpcbind restart && service nfs restart" % (nfsPath)
                        ssh.execute(cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, 22)
                        cmd = "iptables -I INPUT -p tcp -m tcp --dport 2049 -j ACCEPT && iptables -I INPUT -p udp -m udp --dport 2049 -j ACCEPT"
                        ssh.execute(cmd, vm_ip, vm_config.imageUsername_, vm_config.imagePassword_, True, 22)
                        return

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

def deploy_scenario(scenario_config, scenario_file, deploy_config):
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
            vm_xml.set('ip', vm_ip)
            if xmlobject.has_element(vm, 'nodeRef'):
                setup_node_vm(vm_ip, vm, deploy_config)
            if xmlobject.has_element(vm, 'hostRef'):
                setup_host_vm(vm_ip, vm, deploy_config)
                vm_xml.set('managementIp', vm_ip)
            if xmlobject.has_element(vm, 'backupStorageRef'):
                setup_backupstorage_vm(vm_ip, vm, deploy_config)
            if xmlobject.has_element(vm, 'primaryStorageRef'):
                setup_primarystorage_vm(vm_ip, vm, deploy_config)
            destroy_vm(zstack_management_ip, vm_inv.uuid)
    xml_string = etree.tostring(root_xml, 'utf-8')
    xml_string = minidom.parseString(xml_string).toprettyxml(indent="  ")
    open(scenario_file, 'w+').write(xml_string)
