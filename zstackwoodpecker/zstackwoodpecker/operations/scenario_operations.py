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

def setup_node_vm(vm_config, deploy_config):
    for nodeRef in xmlobject.safe_list(vm_config.nodeRef):
        print nodeRef.text_

def setup_host_vm(vm_config, deploy_config):
    for hostRef in xmlobject.safe_list(vm_config.hostRef):
        print hostRef.text_
        for zone in xmlobject.safe_list(deploy_config.zones.zone):
            for cluster in xmlobject.safe_list(zone.clusters.cluster):
                for host in xmlobject.safe_list(cluster.hosts.host):
                    print host.name_
                    if hostRef.text_ == host.name_:
                        print 'vm ref host found'
                        return

def setup_backupstorage_vm(vm_config, deploy_config):
    for backupStorageRef in xmlobject.safe_list(vm_config.backupStorageRef):
        print backupStorageRef.text_
        if backupStorageRef.type_ == 'sftp':
            for sftpBackupStorage in xmlobject.safe_list(deploy_config.backupStorages.sftpBackupStorage):
                if backupStorageRef.text_ == sftpBackupStorage.name_:
                    print 'vm ref bs found'
                    return

def setup_primarystorage_vm(vm_config, deploy_config):
    for primaryStorageRef in xmlobject.safe_list(vm_config.primaryStorageRef):
        print primaryStorageRef.text_
        if primaryStorageRef.type_ == 'nfs':
            for zone in xmlobject.safe_list(deploy_config.zones.zone):
                for nfsPrimaryStorage in xmlobject.safe_list(zone.primaryStorages.nfsPrimaryStorage):
                    if primaryStorageRef.text_ == nfsPrimaryStorage.name_:
                        print 'vm ref ps found'
                        return

def deploy_scenario(scenario_config, scenario_file, deploy_config):
    print scenario_config.basicConfig.zstackManagementIp.text_
    session_uuid = login_as_admin(scenario_config.basicConfig.zstackManagementIp.text_)
    logout(scenario_config.basicConfig.zstackManagementIp.text_, session_uuid)
    action = api_actions.QueryHostAction()
    action.conditions = []
    execute_action_with_session(scenario_config.basicConfig.zstackManagementIp.text_, action, None, False)
    root_xml = etree.Element("deployerConfig")
    vms_xml = etree.SubElement(root_xml, 'vms')
    for host in xmlobject.safe_list(scenario_config.deployerConfig.hosts.host):
        print host.uuid_
        for vm in xmlobject.safe_list(host.vms.vm):
            vm_xml = etree.SubElement(vms_xml, 'vm')
            vm_xml.set('name', vm.name_)
            vm_xml.set('ip', '172.20.197.111')
	    print xmlobject.loads(etree.tostring(root_xml)).dump()
            print vm.name_, vm.vmInstranceOfferingUuid_, vm.imageUuid_
	    #create_vm(host.uuid_, vm.name_, vm.vmInstranceOfferingUuid_, vm.imageUuid_)
            if xmlobject.has_element(vm, 'nodeRef'):
                setup_node_vm(vm, deploy_config)
            if xmlobject.has_element(vm, 'hostRef'):
                setup_host_vm(vm, deploy_config)
                vm_xml.set('managementIp', '172.20.197.111')
            if xmlobject.has_element(vm, 'backupStorageRef'):
                setup_backupstorage_vm(vm, deploy_config)
            if xmlobject.has_element(vm, 'primaryStorageRef'):
                setup_primarystorage_vm(vm, deploy_config)
    xml_string = etree.tostring(root_xml, 'utf-8')
    xml_string = minidom.parseString(xml_string).toprettyxml(indent="  ")
    open(scenario_file, 'w+').write(xml_string)
