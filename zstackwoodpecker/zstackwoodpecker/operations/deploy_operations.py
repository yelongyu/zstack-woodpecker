'''

deploy operations for setup zstack database.

@author: Youyk
'''

import zstackwoodpecker.test_util as test_util
import apibinding.api_actions as api_actions
import account_operations
import resource_operations as res_ops
import zstacklib.utils.sizeunit as sizeunit
import zstacklib.utils.jsonobject as jsonobject
import zstacklib.utils.xmlobject as xmlobject
import zstacklib.utils.lock as lock
import zstacklib.utils.http as http
import apibinding.inventory as inventory
import zstacklib.utils.ssh as ssh
import os
import sys
import traceback
import threading
import urllib3
import types
import simplejson
import time
import nas_operations as nas_ops
import hybrid_operations as hyb_ops
import config_operations as cfg_ops
import backupstorage_operations as bs_ops

#global exception information for thread usage
exc_info = []
AddKVMHostTimeOut = 30*60*1000
IMAGE_THREAD_LIMIT = 2
DEPLOY_THREAD_LIMIT = 500
irg_uuid = None
bs_uuid_list = []


def install_mini_server():
    vm_ip = os.getenv('ZSTACK_BUILT_IN_HTTP_SERVER_IP')
    mini_server_url = os.getenv('MINI_SERVER_URL')
    http = urllib3.PoolManager()
    rsp = http.request('GET', mini_server_url)
    data = rsp.data.split('"')
    ms_bins = [m for m in data if '.bin' in m]
    bin_url = os.path.join(mini_server_url, ms_bins[-2])
    install_cmd = 'wget -c %s -P /tmp; bash /tmp/%s' % (bin_url, ms_bins[-2])
    ssh.execute(install_cmd, vm_ip, 'root', 'password')

def get_first_item_from_list(list_obj, list_obj_name, list_obj_value, action_name):
    '''
    Judge if list is empty. If not, return the 1st item.
    list_obj: the list for judgment and return;
    list_obj_name: the list item type name;
    list_obj_value: the list item's value when do previous query;
    action_name: which action is calling this function
    '''
    if not isinstance(list_obj, list):
        raise test_util.TestError("The first parameter is not a [list] type")

    if not list_obj:
        raise test_util.TestError("Did not find %s: [%s], when adding %s" % (list_obj_name, list_obj_value, action_name))

    if len(list_obj) > 1:
        raise test_util.TestError("Find more than 1 [%s] resource with name: [%s], when adding %s. Please check your deploy.xml and make sure resource do NOT have duplicated name " % (list_obj_name, list_obj_value, action_name))

    return list_obj[0]

def get_ceph_storages_mon_nic_id(ceph_name, scenario_config):
    for host in xmlobject.safe_list(scenario_config.deployerConfig.hosts.host):
        for vm in xmlobject.safe_list(host.vms.vm):
            nic_id = 0
            for l3network in xmlobject.safe_list(vm.l3Networks.l3Network):
                if hasattr(l3network, 'backupStorageRef') and hasattr(l3network.backupStorageRef, 'monIp_') and l3network.backupStorageRef.text_ == ceph_name:
                    return nic_id
                if hasattr(l3network, 'primaryStorageRef') and hasattr(l3network.primaryStorageRef, 'monIp_') and l3network.primaryStorageRef.text_ == ceph_name:
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

def get_backup_storage_from_scenario_file(backupStorageRefName, scenarioConfig, scenarioFile, deployConfig):
    if scenarioConfig == None or scenarioFile == None or not os.path.exists(scenarioFile):
        return []

    import scenario_operations as sce_ops
    import zstackwoodpecker.test_lib as test_lib
    zstack_management_ip = scenarioConfig.basicConfig.zstackManagementIp.text_
    ip_list = []
    for host in xmlobject.safe_list(scenarioConfig.deployerConfig.hosts.host):
        for vm in xmlobject.safe_list(host.vms.vm):
            if xmlobject.has_element(vm, 'backupStorageRef'):
                if backupStorageRefName == vm.backupStorageRef.text_:
                    with open(scenarioFile, 'r') as fd:
                        xmlstr = fd.read()
                        fd.close()
                        scenario_file = xmlobject.loads(xmlstr)
                        for s_vm in xmlobject.safe_list(scenario_file.vms.vm):
                            if s_vm.name_ == vm.name_:
                                if test_lib.lib_cur_cfg_is_a_and_b(["test-config-vyos-fusionstor-3-nets-sep.xml"], ["scenario-config-fusionstor-3-nets-sep.xml"]):
            	                    ip_list.append(s_vm.storageIp_)
                                    continue
                                if vm.backupStorageRef.type_ == 'ceph':
                                    nic_id = get_ceph_storages_mon_nic_id(vm.backupStorageRef.text_, scenarioConfig)
                                    if nic_id == None:
                                        ip_list.append(s_vm.ip_)
                                    else:
            	                        ip_list.append(s_vm.ips.ip[nic_id].ip_)
                                else:
                                    for l3Network in xmlobject.safe_list(vm.l3Networks.l3Network):
                                        if xmlobject.has_element(l3Network, 'backupStorageRef') and backupStorageRefName in [ backupStorageRef.text_ for backupStorageRef in l3Network.backupStorageRef]:
                                        #if xmlobject.has_element(l3Network, 'backupStorageRef') and l3Network.backupStorageRef.text_ == backupStorageRefName:
                                            cond = res_ops.gen_query_conditions('name', '=', vm.name_)
                                            vm_inv_nics = sce_ops.query_resource(zstack_management_ip, res_ops.VM_INSTANCE, cond).inventories[0].vmNics
                                            for vm_inv_nic in vm_inv_nics:
                                                if vm_inv_nic.l3NetworkUuid == l3Network.uuid_:
                                                    ip_list.append(vm_inv_nic.ip)
                                                    return ip_list
                                    else:
                                        ip_list.append(s_vm.ip_)
    return ip_list

def get_vm_ip_from_scenariofile(scenarioFile):
    vm_ip_list = []
    with open(scenarioFile, 'r') as fd:
        xmlstr = fd.read()
        scenario_file = xmlobject.loads(xmlstr)
        for vm in xmlobject.safe_list(scenario_file.vms.vm):
            vm_ip_list.append(vm.ip__)
    return vm_ip_list


#Add Backup Storage
def add_backup_storage(scenarioConfig, scenarioFile, deployConfig, session_uuid):
    global irg_uuid
    global bs_uuid_list
    if xmlobject.has_element(deployConfig, 'backupStorages.sftpBackupStorage'):
        for bs in xmlobject.safe_list(deployConfig.backupStorages.sftpBackupStorage):
            action = api_actions.AddSftpBackupStorageAction()
            action.sessionUuid = session_uuid
            action.name = bs.name_
            action.description = bs.description__
            action.url = bs.url_
            action.username = bs.username_
            action.password = bs.password_
            hostname_list = get_backup_storage_from_scenario_file(bs.name_, scenarioConfig, scenarioFile, deployConfig)
            if len(hostname_list) == 0:
                action.hostname = bs.hostname_
            else:
                action.hostname = hostname_list[0]

	    if hasattr(bs, 'port_'):
                action.port = bs.port_
                action.sshport = bs.port_
                action.sshPort = bs.port_
            action.timeout = AddKVMHostTimeOut #for some platform slowly salt execution
            action.type = inventory.SFTP_BACKUP_STORAGE_TYPE
            thread = threading.Thread(target = _thread_for_action, args = (action, ))
            wait_for_thread_queue()
            thread.start()

    if xmlobject.has_element(deployConfig, 'backupStorages.imageStoreBackupStorage'):
        for bs in xmlobject.safe_list(deployConfig.backupStorages.imageStoreBackupStorage):
            action = api_actions.AddImageStoreBackupStorageAction()
            action.sessionUuid = session_uuid
            action.name = bs.name_
            action.description = bs.description__
            action.url = bs.url_
            action.username = bs.username_
            action.password = bs.password_
            hostname_list = get_backup_storage_from_scenario_file(bs.name_, scenarioConfig, scenarioFile, deployConfig)
            if len(hostname_list) == 0:
                action.hostname = bs.hostname_
            else:
                action.hostname = hostname_list[0]
            if hasattr(bs, 'port_'):
                action.port = bs.port_
                action.sshport = bs.port_
                action.sshPort = bs.port_
            action.timeout = AddKVMHostTimeOut #for some platform slowly salt execution
            action.type = inventory.IMAGE_STORE_BACKUP_STORAGE_TYPE
            thread = threading.Thread(target = _thread_for_action, args = (action, True))
            wait_for_thread_queue()
            thread.start()

    if xmlobject.has_element(deployConfig, 'backupStorages.miniBackupStorage'):
	vm_ip_list = get_vm_ip_from_scenariofile(scenarioFile)
        bs_uuid_list = []
        for bs in xmlobject.safe_list(deployConfig.backupStorages.miniBackupStorage):
	    action = api_actions.AddImageStoreBackupStorageAction()
	    action.sessionUuid = session_uuid
	    action.name = bs.name_
            bs_id = bs.id__
	    action.description = bs.description__
	    action.url = bs.url_
	    action.username = bs.username_
	    action.password = bs.password_
	    action.hostname = vm_ip_list[int(bs_id)]

	    if hasattr(bs, 'port_'):
	        action.port = bs.port_
	        action.sshport = bs.port_
	        action.sshPort = bs.port_
	    action.timeout = AddKVMHostTimeOut #for some platform slowly salt execution
	    action.type = inventory.IMAGE_STORE_BACKUP_STORAGE_TYPE
	    thread = threading.Thread(target = _thread_for_action, args = (action, True))
	    wait_for_thread_queue()
	    thread.start()
            wait_for_thread_done()
            bs = res_ops.get_resource(res_ops.BACKUP_STORAGE, session_uuid, name=bs.name_)[0].uuid
            bs_uuid_list.append(bs)

	action = api_actions.CreateImageReplicationGroupAction()
        action.name = 'IRG'
	action.sessionUuid = session_uuid
	thread = threading.Thread(target = _thread_for_action, args = (action, True))
	wait_for_thread_queue()
	thread.start()
        wait_for_thread_done()
        irg_uuid = res_ops.get_resource(res_ops.REPLICATIONGROUP)[0].uuid

# 	action = api_actions.AddBackupStoragesToReplicationGroupAction()
#         action.replicationGroupUuid = irg_uuid
#         action.backupStorageUuids = bs_uuid_list
# 	action.sessionUuid = session_uuid
# 	thread = threading.Thread(target = _thread_for_action, args = (action, True))
# 	wait_for_thread_queue()
# 	thread.start()
#         wait_for_thread_done()

    if xmlobject.has_element(deployConfig, 'backupStorages.cephBackupStorage'):
        for bs in xmlobject.safe_list(deployConfig.backupStorages.cephBackupStorage):
            action = api_actions.AddCephBackupStorageAction()
            action.sessionUuid = session_uuid
            action.name = bs.name_
            action.description = bs.description__
            hostname_list = get_backup_storage_from_scenario_file(bs.name_, scenarioConfig, scenarioFile, deployConfig)
            if len(hostname_list) != 0:
                # TODO: username and password should be configarable
                action.monUrls = []
                for hostname in hostname_list:
                    action.monUrls.append("root:password@%s" % (hostname))
            else:
                action.monUrls = bs.monUrls_.split(';')
            if bs.poolName__:
                action.poolName = bs.poolName_
            action.timeout = AddKVMHostTimeOut #for some platform slowly salt execution
            action.type = inventory.CEPH_BACKUP_STORAGE_TYPE
            thread = threading.Thread(target = _thread_for_action, args = (action, ))
            wait_for_thread_queue()
            thread.start()

    if xmlobject.has_element(deployConfig, 'backupStorages.xskycephBackupStorage'):
        for bs in xmlobject.safe_list(deployConfig.backupStorages.xskycephBackupStorage):
            action = api_actions.AddCephBackupStorageAction()
            action.sessionUuid = session_uuid
            action.name = bs.name_
            action.description = bs.description__
            hostname_list = get_backup_storage_from_scenario_file(bs.name_, scenarioConfig, scenarioFile, deployConfig)
            if len(hostname_list) != 0:
                # TODO: username and password should be configarable
                action.monUrls = []
                for hostname in hostname_list:
                    action.monUrls.append("root:password@%s" % (hostname))
            else:
                action.monUrls = bs.monUrls_.split(';')
            xsky_mn_ip = hostname_list[1]
            cmd = "rados lspools"
            (retcode, output, erroutput) = ssh.execute(cmd, xsky_mn_ip, "root", "password", True, 22)
            action.poolName = output
            action.timeout = AddKVMHostTimeOut #for some platform slowly salt execution
            action.type = inventory.CEPH_BACKUP_STORAGE_TYPE
            thread = threading.Thread(target = _thread_for_action, args = (action, ))
            wait_for_thread_queue()
            thread.start()

    if xmlobject.has_element(deployConfig, 'backupStorages.xskyBackupStorage'):
        for bs in xmlobject.safe_list(deployConfig.backupStorages.xskyBackupStorage):
            action = api_actions.AddCephBackupStorageAction()
            action.sessionUuid = session_uuid
            action.name = bs.name_
            action.description = bs.description__
            hostname_list = get_backup_storage_from_scenario_file(bs.name_, scenarioConfig, scenarioFile, deployConfig)
            if len(hostname_list) != 0:
                # TODO: username and password should be configarable
                action.monUrls = []
                for hostname in hostname_list:
                    action.monUrls.append("root:password@%s" % (hostname))
            else:
                if bs.monUrls_.find(';') == -1:
                    action.monUrls = [bs.monUrls_]
                else:
                    action.monUrls = bs.monUrls_.split(';')
            if bs.poolName__:
                action.poolName = bs.poolName_
            action.timeout = AddKVMHostTimeOut #for some platform slowly salt execution
            action.type = inventory.CEPH_BACKUP_STORAGE_TYPE
            thread = threading.Thread(target = _thread_for_action, args = (action, ))
            wait_for_thread_queue()
            thread.start()

    if xmlobject.has_element(deployConfig, 'backupStorages.aliyunEbsBackupStorage'):
        dc_inv = hyb_ops.query_datacenter_local()
        if dc_inv:
            dc_inv = dc_inv[0]
        else:
            test_util.test_fail("No datacenter found in local")

        # Add OSS bucket
        oss_buckt_inv = hyb_ops.add_oss_bucket_from_remote(data_center_uuid=dc_inv.uuid,
                                                           oss_bucket_name='ebs',
                                                           oss_domain=os.getenv('ebsOSSEndPoint'),
                                                           oss_key='ebs',
                                                           oss_secret='zstack')

        for bs in xmlobject.safe_list(deployConfig.backupStorages.aliyunEbsBackupStorage):
            action = api_actions.AddAliyunEbsBackupStorageAction()
            action.sessionUuid = session_uuid
            action.ossBucketUuid = oss_buckt_inv.uuid
            action.name = bs.name_
            action.description = bs.description__
            action.timeout = AddKVMHostTimeOut #for some platform slowly salt execution
            action.type = 'AliyunEBS'
            action.url = os.getenv('ebsEndPoint')
            thread = threading.Thread(target = _thread_for_action, args = (action, ))
            wait_for_thread_queue()
            thread.start()

    if xmlobject.has_element(deployConfig, 'backupStorages.fusionstorBackupStorage'):
        for bs in xmlobject.safe_list(deployConfig.backupStorages.fusionstorBackupStorage):
            action = api_actions.AddFusionstorBackupStorageAction()
            action.sessionUuid = session_uuid
            action.name = bs.name_
            action.description = bs.description__
            hostname_list = get_backup_storage_from_scenario_file(bs.name_, scenarioConfig, scenarioFile, deployConfig)
            if len(hostname_list) != 0:
                # TODO: username and password should be configarable
                action.monUrls = []
                for hostname in hostname_list:
                    action.monUrls.append("root:password@%s" % (hostname))
            else:
                action.monUrls = bs.monUrls_.split(';')
            if bs.poolName__:
                action.poolName = bs.poolName_
            action.timeout = AddKVMHostTimeOut #for some platform slowly salt execution
            action.type = inventory.FUSIONSTOR_BACKUP_STORAGE_TYPE
            thread = threading.Thread(target = _thread_for_action, args = (action, ))
            wait_for_thread_queue()
            thread.start()

    if xmlobject.has_element(deployConfig, 'backupStorages.simulatorBackupStorage'):
        for bs in xmlobject.safe_list(deployConfig.backupStorages.simulatorBackupStorage):
            action = api_actions.AddSimulatorBackupStorageAction()
            action.sessionUuid = session_uuid
            action.name = bs.name_
            action.description = bs.description__
            action.url = bs.url_
            action.type = inventory.SIMULATOR_BACKUP_STORAGE_TYPE
            action.totalCapacity = sizeunit.get_size(bs.totalCapacity_)
            action.availableCapacity = sizeunit.get_size(bs.availableCapacity_)
            thread = threading.Thread(target = _thread_for_action, args = (action, ))
            wait_for_thread_queue()
            thread.start()

    wait_for_thread_done()

#Add Zones
def add_zone(scenarioConfig, scenarioFile, deployConfig, session_uuid, zone_name = None):
    def _add_zone(zone, zone_duplication):
        action = api_actions.CreateZoneAction()
        action.sessionUuid = session_uuid
        if zone_duplication == 0:
            action.name = zone.name_
            action.description = zone.description__
        else:
            action.name = generate_dup_name(zone.name_, zone_duplication, 'z')
            action.description = generate_dup_name(zone.description__, zone_duplication, 'zone')

        try:
            evt = action.run()
            test_util.test_logger(jsonobject.dumps(evt))
            zinv = evt.inventory
        except:
            exc_info.append(sys.exc_info())
     
#        if xmlobject.has_element(zone, 'backupStorageRef'):
#            for ref in xmlobject.safe_list(zone.backupStorageRef):
#                bss = res_ops.get_resource(res_ops.BACKUP_STORAGE, session_uuid, name=ref.text_)
#                bs = get_first_item_from_list(bss, 'Backup Storage', ref.text_, 'attach backup storage to zone')

#                action = api_actions.AttachBackupStorageToZoneAction()
#                action.sessionUuid = session_uuid
#                action.backupStorageUuid = bs.uuid
#                action.zoneUuid = zinv.uuid
#                try:
#                    evt = action.run()
#                    test_util.test_logger(jsonobject.dumps(evt))
#                except:
#                    exc_info.append(sys.exc_info())


    if not xmlobject.has_element(deployConfig, 'zones.zone'):
        return

    for zone in xmlobject.safe_list(deployConfig.zones.zone):
        if zone_name and zone_name != zone.name_:
            continue 

        if zone.duplication__ == None:
            duplication = 1
        else:
            duplication = int(zone.duplication__)

        for i in range(duplication):
            thread = threading.Thread(target=_add_zone, args=(zone, i, ))
            wait_for_thread_queue()
            thread.start()

    wait_for_thread_done()


def attach_bs_to_zone(scenarioConfig, scenarioFile, deployConfig, session_uuid, zone_name = None):
    global irg_uuid
    global bs_uuid_list
    def _attach_bs_to_zone(zone, zone_duplication):
        if zone_duplication == 0:
            zone_name = zone.name_
            zone_description = zone.description__
        else:
            zone_name = generate_dup_name(zone.name_, zone_duplication, 'z')
            zone_description = generate_dup_name(zone.description__, zone_duplication, 'zone')

        zinvs = res_ops.get_resource(res_ops.ZONE, session_uuid, name=zone_name)
        zinv = get_first_item_from_list(zinvs, 'Zone', zone.name_, 'attach backup storage to zone')

        if xmlobject.has_element(zone, 'backupStorageRef'):
            for ref in xmlobject.safe_list(zone.backupStorageRef):
                bss = res_ops.get_resource(res_ops.BACKUP_STORAGE, session_uuid, name=ref.text_)
                bs = get_first_item_from_list(bss, 'Backup Storage', ref.text_, 'attach backup storage to zone')

                action = api_actions.AttachBackupStorageToZoneAction()
                action.sessionUuid = session_uuid
                action.backupStorageUuid = bs.uuid
                action.zoneUuid = zinv.uuid
                try:
                    evt = action.run()
                    test_util.test_logger(jsonobject.dumps(evt))
                except:
                    exc_info.append(sys.exc_info())


    if not xmlobject.has_element(deployConfig, 'zones.zone'):
        return

    for zone in xmlobject.safe_list(deployConfig.zones.zone):
        if zone_name and zone_name != zone.name_:
            continue

        if zone.duplication__ == None:
            duplication = 1
        else:
            duplication = int(zone.duplication__)

        for i in range(duplication):
            thread = threading.Thread(target=_attach_bs_to_zone, args=(zone, i, ))
            wait_for_thread_queue()
            thread.start()

    wait_for_thread_done()
    if irg_uuid is not None:
        bs_ops.add_bs_to_image_replication_group(irg_uuid, bs_uuid_list)

#Add L2 network
def add_l2_network(scenarioConfig, scenarioFile, deployConfig, session_uuid, l2_name = None, zone_name = None):
    '''
    If providing name, it will only add L2 network with the same name.
    '''
    if not xmlobject.has_element(deployConfig, "zones.zone"):
        return

    def _deploy_l2_vxlan_network(zone):
        if not xmlobject.has_element(deployConfig, "l2VxlanNetworkPools"):
            return

        for l2pool in xmlobject.safe_list(deployConfig.l2VxlanNetworkPools.l2VxlanNetworkPool):
            zinvs = res_ops.get_resource(res_ops.ZONE, session_uuid, name=zone.name_)
            zinv = get_first_item_from_list(zinvs, 'Zone', zone.name_, 'L2 network')

            action = api_actions.CreateL2VxlanNetworkPoolAction()
            action.name = l2pool.name_
            action.zoneUuid = zinv.uuid
            action.sessionUuid = session_uuid
            poolinv = action.run().inventory
            for vnirange in xmlobject.safe_list(l2pool.vniRanges.vniRange):
                action = api_actions.CreateVniRangeAction()
                action.name = vnirange.name_
                action.startVni = vnirange.startVni_
                action.endVni = vnirange.endVni_
                action.l2NetworkUuid = poolinv.uuid
                action.sessionUuid = session_uuid
                evt = action.run()

    def _deploy_l2_network(zone, is_vlan):
        if is_vlan:
            if not xmlobject.has_element(zone, "l2Networks.l2VlanNetwork"):
                return
            l2Network = zone.l2Networks.l2VlanNetwork
        else:
            if not xmlobject.has_element(zone, \
                    "l2Networks.l2NoVlanNetwork"):
                return
            l2Network = zone.l2Networks.l2NoVlanNetwork

        if zone.duplication__ == None:
            zone_dup = 1
        else:
            zone_dup = int(zone.duplication__)

        for zone_ref in range(zone_dup):
            zoneName = generate_dup_name(zone.name_, zone_ref, 'z')

            zinvs = res_ops.get_resource(res_ops.ZONE, session_uuid, name=zoneName)
            zinv = get_first_item_from_list(zinvs, 'Zone', zoneName, 'L2 network')

            #can only deal with single cluster duplication case.
            cluster = xmlobject.safe_list(zone.clusters.cluster)[0]
            
            if cluster.duplication__ == None:
                cluster_duplication = 1
            else:
                cluster_duplication = int(cluster.duplication__)

            for cluster_ref in range(cluster_duplication):
                for l2 in xmlobject.safe_list(l2Network):
                    if l2_name and l2_name != l2.name_:
                        continue 

                    if not is_vlan or l2.duplication__ == None:
                        l2_dup = 1
                    else:
                        l2_dup = int(l2.duplication__)

                    for j in range(l2_dup):
                        l2Name = generate_dup_name(\
                                generate_dup_name(\
                                generate_dup_name(\
                                l2.name_, zone_ref, 'z')\
                                , cluster_ref, 'c')\
                                , j, 'n')

                        l2Des = generate_dup_name(\
                                generate_dup_name(\
                                generate_dup_name(\
                                l2.description_, zone_ref, 'z')\
                                , cluster_ref, 'c')\
                                , j, 'n')

                        if is_vlan:
                            l2_vlan = int(l2.vlan_) + j

                        if is_vlan:
                            action = api_actions.CreateL2VlanNetworkAction()
                        else:
                            action = api_actions.CreateL2NoVlanNetworkAction()

                        action.sessionUuid = session_uuid
                        action.name = l2Name
                        action.description = l2Des

                        if scenarioFile != None:
                            action.physicalInterface = l2.physicalInterface_.replace("eth", "zsn")
                        else:
                            action.physicalInterface = l2.physicalInterface_

                        action.zoneUuid = zinv.uuid
                        if is_vlan:
                            action.vlan = l2_vlan

                        thread = threading.Thread(\
                                target=_thread_for_action, \
                                args=(action,))
                        wait_for_thread_queue()
                        thread.start()

    for zone in xmlobject.safe_list(deployConfig.zones.zone):
        if zone_name and zone.name_ != zone_name:
            continue

        _deploy_l2_network(zone, False)
        _deploy_l2_network(zone, True)
        _deploy_l2_vxlan_network(zone)

    wait_for_thread_done()

def get_primary_storage_from_scenario_file(primaryStorageRefName, scenarioConfig, scenarioFile, deployConfig):
    if scenarioConfig == None or scenarioFile == None or not os.path.exists(scenarioFile):
        return []

    import zstackwoodpecker.test_lib as test_lib
    ip_list = []
    for host in xmlobject.safe_list(scenarioConfig.deployerConfig.hosts.host):
        for vm in xmlobject.safe_list(host.vms.vm):
            if xmlobject.has_element(vm, 'primaryStorageRef'):
                #if vm.primaryStorageRef.text_ == primaryStorageRefName:
                if isinstance(vm.primaryStorageRef,list):
                    for ps_each in vm.primaryStorageRef:
                        if ps_each.text_ == primaryStorageRefName:
                            with open(scenarioFile, 'r') as fd:
                                xmlstr = fd.read()
                                fd.close()
                                scenario_file = xmlobject.loads(xmlstr)
                                for s_vm in xmlobject.safe_list(scenario_file.vms.vm):
                                    if s_vm.name_ == vm.name_:
                                        if test_lib.lib_cur_cfg_is_a_and_b(["test-config-vyos-fusionstor-3-nets-sep.xml"], ["scenario-config-fusionstor-3-nets-sep.xml"]):
                                            ip_list.append(s_vm.storageIp_)
                                            test_util.test_logger("@@@DEBUG->get ps->list@@@")
                                            continue
                                        if xmlobject.has_element(vm, 'backupStorageRef') and vm.backupStorageRef.type_ == 'ceph':
                                            nic_id = get_ceph_storages_mon_nic_id(vm.backupStorageRef.text_, scenarioConfig)
                                            if nic_id == None:
                                                ip_list.append(s_vm.ip_)
                                            else:
            	                                ip_list.append(s_vm.ips.ip[nic_id].ip_)
                                        else:
                                            ip_list.append(s_vm.ip_)
                else:
                    if vm.primaryStorageRef.text_ == primaryStorageRefName:
                        with open(scenarioFile, 'r') as fd:
                            xmlstr = fd.read()
                            fd.close()
                            scenario_file = xmlobject.loads(xmlstr)
                            for s_vm in xmlobject.safe_list(scenario_file.vms.vm):
                                if s_vm.name_ == vm.name_:
                                    if test_lib.lib_cur_cfg_is_a_and_b(["test-config-vyos-fusionstor-3-nets-sep.xml"], ["scenario-config-fusionstor-3-nets-sep.xml"]):
                                        ip_list.append(s_vm.storageIp_)
                                        test_util.test_logger("@@@DEBUG->get ps->not list@@@")
                                        continue
                                    if xmlobject.has_element(vm, 'backupStorageRef') and vm.backupStorageRef.type_ == 'ceph':
                                        nic_id = get_ceph_storages_mon_nic_id(vm.backupStorageRef.text_, scenarioConfig)
                                        if nic_id == None:
                                            ip_list.append(s_vm.ip_)
                                        else:
            	                            ip_list.append(s_vm.ips.ip[nic_id].ip_)
                                    else:
                                        ip_list.append(s_vm.ip_)
    return ip_list

def get_disk_uuid(scenarioFile):
    import scenario_operations as sce_ops
    import zstacklib.utils.ssh as ssh
    host_ips = sce_ops.dump_scenario_file_ips(scenarioFile)
    #Below is aim to migrate sanlock to a separated partition, don't delete!!!
    #IF separated_partition:
    #cmd = r"blkid|grep mpatha2|awk -F\" '{print $2}'"
    #ELSE
    cmd = r"ls -l /dev/disk/by-id/ | grep wwn | awk '{print $9}'"
    #ENDIF
    ret, disk_uuid, stderr = ssh.execute(cmd, host_ips[-1], "root", "password", True, 22)
    return disk_uuid.strip().split('\n')

def get_scsi_target_ip(scenarioFile):
    import scenario_operations as sce_ops
    host_ips = sce_ops.dump_scenario_file_ips(scenarioFile)
    return host_ips[0]

#Add Primary Storage
def add_primary_storage(scenarioConfig, scenarioFile, deployConfig, session_uuid, ps_name = None, \
        zone_name = None):
    if not xmlobject.has_element(deployConfig, 'zones.zone'):
        test_util.test_logger('Not find zones.zone in config, skip primary storage deployment')
        return

    def _generate_sim_ps_action(zone, pr, zone_ref, cluster_ref):
        if zone_ref == 0:
            zone_name = zone.name_
        else:
            zone_name = generate_dup_name(zone.name_, zone_ref, 'z')

        zinvs = res_ops.get_resource(res_ops.ZONE, session_uuid, name=zone_name)
        zinv = get_first_item_from_list(zinvs, 'Zone', zone_name, 'primary storage')

        action = api_actions.AddSimulatorPrimaryStorageAction()
        action.sessionUuid = session_uuid
        action.name = generate_dup_name(generate_dup_name(pr.name_, zone_ref, 'z'), cluster_ref, 'c') 
        action.description = generate_dup_name(generate_dup_name(pr.description__, zone_ref, 'zone'), cluster_ref, 'cluster')
        action.url = generate_dup_name(generate_dup_name(pr.url_, zone_ref, 'z'), cluster_ref, 'c')

        action.type = inventory.SIMULATOR_PRIMARY_STORAGE_TYPE
        action.zoneUuid = zinv.uuid
        action.totalCapacity = sizeunit.get_size(pr.totalCapacity_)
        action.totalPhysicalCapacity = sizeunit.get_size(pr.totalCapacity_)
        action.availableCapacity = sizeunit.get_size(pr.availableCapacity_)
        action.availablePhysicalCapacity = sizeunit.get_size(pr.availableCapacity_)
        return action

    def _deploy_primary_storage(zone):
        if xmlobject.has_element(zone, 'primaryStorages.IscsiFileSystemBackendPrimaryStorage'):
            zinvs = res_ops.get_resource(res_ops.ZONE, session_uuid, \
                    name=zone.name_)
            zinv = get_first_item_from_list(zinvs, 'Zone', zone.name_, 'primary storage')

            for pr in xmlobject.safe_list(zone.primaryStorages.IscsiFileSystemBackendPrimaryStorage):
                if ps_name and ps_name != pr.name_:
                    continue

                action = api_actions.AddIscsiFileSystemBackendPrimaryStorageAction()
                action.sessionUuid = session_uuid
                action.name = pr.name_
                action.description = pr.description__
                action.type = inventory.ISCSI_FILE_SYSTEM_BACKEND_PRIMARY_STORAGE_TYPE
                action.url = pr.url_
                action.zoneUuid = zinv.uuid
                action.chapPassword = pr.chapPassword_
                action.chapUsername = pr.chapUsername_
                action.sshPassword = pr.sshPassword_
                action.sshUsername = pr.sshUsername_
                action.hostname = pr.hostname_
                action.filesystemType = pr.filesystemType_
                thread = threading.Thread(target=_thread_for_action, args=(action,))
                wait_for_thread_queue()
                thread.start()

        if xmlobject.has_element(zone, 'primaryStorages.sharedBlockPrimaryStorage'):
            zinvs = res_ops.get_resource(res_ops.ZONE, session_uuid, \
                    name=zone.name_)
            zinv = get_first_item_from_list(zinvs, 'Zone', zone.name_, 'primary storage')
            if os.environ.get('ZSTACK_SIMULATOR') != "yes":
                disk_uuids = get_disk_uuid(scenarioFile)
            else:
                # TODO: hardcoded right now
                disk_uuids = ['1234567890'] * 1000

            for pr in xmlobject.safe_list(zone.primaryStorages.sharedBlockPrimaryStorage):
                if ps_name and ps_name != pr.name_:
                    continue

                action = api_actions.AddSharedBlockGroupPrimaryStorageAction()
                action.sessionUuid = session_uuid
                action.name = pr.name_
                action.description = pr.description__
                action.zoneUuid = zinv.uuid
                action.diskUuids = [disk_uuids.pop()]
                if pr.hasattr('systemtags_'):
                    action.systemTags = pr.systemtags_.split(',')
                else:
                    action.systemTags = ["primaryStorageVolumeProvisioningStrategy::ThinProvisioning", "forceWipe"]
                thread = threading.Thread(target=_thread_for_action, args=(action,))
                wait_for_thread_queue()
                thread.start()

        if xmlobject.has_element(zone, 'primaryStorages.miniPrimaryStorage'):
            zinvs = res_ops.get_resource(res_ops.ZONE, session_uuid, \
                    name=zone.name_)
            zinv = get_first_item_from_list(zinvs, 'Zone', zone.name_, 'primary storage')

            for pr in xmlobject.safe_list(zone.primaryStorages.miniPrimaryStorage):
                if ps_name and ps_name != pr.name_:
                    continue

                action = api_actions.AddMiniStorageAction()
                action.sessionUuid = session_uuid
                action.name = pr.name_
                action.description = pr.description__
                action.diskIdentifier = pr.diskIdentifier__
                action.url = pr.url__
                action.zoneUuid = zinv.uuid
                thread = threading.Thread(target=_thread_for_action, args=(action,))
                wait_for_thread_queue()
                thread.start()
                wait_for_thread_done()

            ps_uuid = res_ops.get_resource(res_ops.PRIMARY_STORAGE, session_uuid, name=pr.name_)[0].uuid
            action = api_actions.CreateSystemTagAction()
            action.sessionUuid = session_uuid
            action.tag = "primaryStorage::gateway::cidr::99.99.99.130/24"
            action.resourceUuid = ps_uuid
            action.resourceType = "PrimaryStorageVO"
            thread = threading.Thread(target=_thread_for_action, args=(action,))
            wait_for_thread_queue()
            thread.start()
            wait_for_thread_queue()


        if xmlobject.has_element(zone, 'primaryStorages.localPrimaryStorage'):
            zinvs = res_ops.get_resource(res_ops.ZONE, session_uuid, \
                    name=zone.name_)
            zinv = get_first_item_from_list(zinvs, 'Zone', zone.name_, 'primary storage')

            for pr in xmlobject.safe_list(zone.primaryStorages.localPrimaryStorage):
                if ps_name and ps_name != pr.name_:
                    continue

                action = api_actions.AddLocalPrimaryStorageAction()
                action.sessionUuid = session_uuid
                action.name = pr.name_
                action.description = pr.description__
                action.type = inventory.LOCAL_STORAGE_TYPE
                action.url = pr.url_
                action.zoneUuid = zinv.uuid
                thread = threading.Thread(target=_thread_for_action, args=(action,))
                wait_for_thread_queue()
                thread.start()

        if xmlobject.has_element(zone, 'primaryStorages.cephPrimaryStorage'):
            zinvs = res_ops.get_resource(res_ops.ZONE, session_uuid, \
                    name=zone.name_)
            zinv = get_first_item_from_list(zinvs, 'Zone', zone.name_, 'primary storage')

            for pr in xmlobject.safe_list(zone.primaryStorages.cephPrimaryStorage):
                if ps_name and ps_name != pr.name_:
                    continue

                action = api_actions.AddCephPrimaryStorageAction()
                action.sessionUuid = session_uuid
                action.name = pr.name_
                action.description = pr.description__
                action.type = inventory.CEPH_PRIMARY_STORAGE_TYPE
                hostname_list = get_primary_storage_from_scenario_file(pr.name_, scenarioConfig, scenarioFile, deployConfig)
                if len(hostname_list) != 0:
                    action.monUrls = []
                    for hostname in hostname_list:
                        action.monUrls.append("root:password@%s" % (hostname))
                else:
                    action.monUrls = pr.monUrls_.split(';')
                if pr.dataVolumePoolName__:
                    action.dataVolumePoolName = pr.dataVolumePoolName__
                if pr.rootVolumePoolName__:
                    action.rootVolumePoolName = pr.rootVolumePoolName__
                if pr.imageCachePoolName__:
                    action.imageCachePoolName = pr.imageCachePoolName__
                action.zoneUuid = zinv.uuid
                thread = threading.Thread(target=_thread_for_action, args=(action,))
                wait_for_thread_queue()
                thread.start()

        if xmlobject.has_element(zone, 'primaryStorages.cephPrimaryMultipoolsStorage'):
            zinvs = res_ops.get_resource(res_ops.ZONE, session_uuid, \
                    name=zone.name_)
            zinv = get_first_item_from_list(zinvs, 'Zone', zone.name_, 'primary storage')

            for pr in xmlobject.safe_list(zone.primaryStorages.cephPrimaryMultipoolsStorage):
                if ps_name and ps_name != pr.name_:
                    continue

                action = api_actions.AddCephPrimaryStorageAction()
                action.sessionUuid = session_uuid
                action.name = pr.name_
                action.description = pr.description__
                action.type = inventory.CEPH_PRIMARY_STORAGE_TYPE
                hostname_list = get_primary_storage_from_scenario_file(pr.name_, scenarioConfig, scenarioFile, deployConfig)
                if len(hostname_list) != 0:
                    action.monUrls = []
                    for hostname in hostname_list:
                        action.monUrls.append("root:password@%s" % (hostname))
                else:
                    action.monUrls = pr.monUrls_.split(';')
                if pr.dataVolumePoolName__:
                    action.dataVolumePoolName = pr.dataVolumePoolName__
                if pr.rootVolumePoolName__:
                    action.rootVolumePoolName = pr.rootVolumePoolName__
                if pr.imageCachePoolName__:
                    action.imageCachePoolName = pr.imageCachePoolName__
		
                action.zoneUuid = zinv.uuid
                thread = threading.Thread(target=_thread_for_action, args=(action,))
                wait_for_thread_queue()
                thread.start()
                thread.join()
            #add ceph pools
            for pr in xmlobject.safe_list(zone.primaryStorages.cephPrimaryMultipoolsStorage):
                if ps_name and ps_name != pr.name_:
                    continue

                cond = res_ops.gen_query_conditions('name', '=', pr.name_)
                ps = res_ops.query_resource(res_ops.PRIMARY_STORAGE, cond)
                action = api_actions.AddCephPrimaryStoragePoolAction()
                action.sessionUuid = session_uuid
                action.isCreate = True
                if ps:
                    action.primaryStorageUuid = ps[0].uuid
                pool_type_list = ['Data', 'Root']
                for pool_type in pool_type_list:
                    for i in range(int(pr.poolNum__)):
                        action.poolName = pr.poolPrefix__ + '-'+ pool_type +'-' + str(i+1) + '-' + ps[0].uuid
                        action.type = pool_type
                        thread = threading.Thread(target=_thread_for_action, args=(action,))
                        wait_for_thread_queue()
                        thread.start()
                        thread.join()

        if xmlobject.has_element(zone, 'primaryStorages.xskycephPrimaryStorage'):
            zinvs = res_ops.get_resource(res_ops.ZONE, session_uuid, name=zone.name_)
            zinv = get_first_item_from_list(zinvs, 'Zone', zone.name_, 'primary storage')
            for pr in xmlobject.safe_list(zone.primaryStorages.xskycephPrimaryStorage):
                if ps_name and ps_name != pr.name_:
                    continue
                action = api_actions.AddCephPrimaryStorageAction()
                action.sessionUuid = session_uuid
                action.name = pr.name_
                action.description = pr.description__
                action.type = inventory.CEPH_PRIMARY_STORAGE_TYPE
                hostname_list = get_primary_storage_from_scenario_file(pr.name_, scenarioConfig, scenarioFile, deployConfig)
                if len(hostname_list) != 0:
                    action.monUrls = []
                    for hostname in hostname_list:
                        action.monUrls.append("root:password@%s" % (hostname))
                else:
                    action.monUrls = pr.monUrls_.split(';')
                xsky_mn_ip = hostname_list[1]
                cmd = "rados lspools"
                (retcode, output, erroutput) = ssh.execute(cmd, xsky_mn_ip, "root", "password", True, 22)

                action.dataVolumePoolName = output
                action.rootVolumePoolName = output
                action.imageCachePoolName = output
                action.zoneUuid = zinv.uuid
                thread = threading.Thread(target=_thread_for_action, args=(action,))
                wait_for_thread_queue()
                thread.start()

        if xmlobject.has_element(zone, 'primaryStorages.xskyPrimaryStorage'):
            zinvs = res_ops.get_resource(res_ops.ZONE, session_uuid, \
                    name=zone.name_)
            zinv = get_first_item_from_list(zinvs, 'Zone', zone.name_, 'primary storage')

            for pr in xmlobject.safe_list(zone.primaryStorages.xskyPrimaryStorage):
                if ps_name and ps_name != pr.name_:
                    continue

                action = api_actions.AddXSkyPrimaryStorageAction()
                action.sessionUuid = session_uuid
                action.name = pr.name_
                action.description = pr.description__
                action.type = inventory.XSKY_PRIMARY_STORAGE_TYPE
                hostname_list = get_primary_storage_from_scenario_file(pr.name_, scenarioConfig, scenarioFile, deployConfig)
                if len(hostname_list) != 0:
                    action.monUrls = []
                    for hostname in hostname_list:
                        action.monUrls.append("root:password@%s" % (hostname))
                else:
                    if pr.monUrls_.find(';') == -1:
                        action.monUrls = [pr.monUrls_]
                    else:
                        action.monUrls = pr.monUrls_.split(';')

                if pr.dataVolumePoolName__:
                    action.dataVolumePoolName = pr.dataVolumePoolName__
                if pr.rootVolumePoolName__:
                    action.rootVolumePoolName = pr.rootVolumePoolName__
                if pr.imageCachePoolName__:
                    action.imageCachePoolName = pr.imageCachePoolName__
                action.zoneUuid = zinv.uuid
                thread = threading.Thread(target=_thread_for_action, args=(action,))
                wait_for_thread_queue()
                thread.start()

        if xmlobject.has_element(zone, 'primaryStorages.fusionstorPrimaryStorage'):
            zinvs = res_ops.get_resource(res_ops.ZONE, session_uuid, \
                    name=zone.name_)
            zinv = get_first_item_from_list(zinvs, 'Zone', zone.name_, 'primary storage')

            for pr in xmlobject.safe_list(zone.primaryStorages.fusionstorPrimaryStorage):
                if ps_name and ps_name != pr.name_:
                    continue

                action = api_actions.AddFusionstorPrimaryStorageAction()
                action.sessionUuid = session_uuid
                action.name = pr.name_
                action.description = pr.description__
                action.type = inventory.FUSIONSTOR_PRIMARY_STORAGE_TYPE
                hostname_list = get_primary_storage_from_scenario_file(pr.name_, scenarioConfig, scenarioFile, deployConfig)
                if len(hostname_list) != 0:
                    action.monUrls = []
                    for hostname in hostname_list:
                        action.monUrls.append("root:password@%s" % (hostname))
                else:
                    action.monUrls = pr.monUrls_.split(';')
                if pr.dataVolumePoolName__:
                    action.dataVolumePoolName = pr.dataVolumePoolName__
                if pr.rootVolumePoolName__:
                    action.rootVolumePoolName = pr.rootVolumePoolName__
                if pr.imageCachePoolName__:
                    action.imageCachePoolName = pr.imageCachePoolName__
                action.zoneUuid = zinv.uuid
                thread = threading.Thread(target=_thread_for_action, args=(action,))
                wait_for_thread_queue()
                thread.start()

        if xmlobject.has_element(zone, 'primaryStorages.nfsPrimaryStorage'):
            zinvs = res_ops.get_resource(res_ops.ZONE, session_uuid, \
                    name=zone.name_)
            zinv = get_first_item_from_list(zinvs, 'Zone', zone.name_, 'primary storage')

            for pr in xmlobject.safe_list(zone.primaryStorages.nfsPrimaryStorage):
                if ps_name and ps_name != pr.name_:
                    continue

                action = api_actions.AddNfsPrimaryStorageAction()
                action.sessionUuid = session_uuid
                action.name = pr.name_
                action.description = pr.description__
                action.type = inventory.NFS_PRIMARY_STORAGE_TYPE
                hostname_list = get_primary_storage_from_scenario_file(pr.name_, scenarioConfig, scenarioFile, deployConfig)
                if len(hostname_list) != 0:
                    action.url = "%s:%s" % (hostname_list[0], pr.url_.split(':')[1])
                    cadidate_ip = get_nfs_ip_for_seperate_network(scenarioConfig, hostname_list[0], pr.name_)
                    if cadidate_ip:
                        action.url = "%s:%s" % (cadidate_ip, pr.url_.split(':')[1])
                else:
                    action.url = pr.url_
                action.zoneUuid = zinv.uuid
                thread = threading.Thread(target=_thread_for_action, args=(action,))
                wait_for_thread_queue()
                thread.start()
            time.sleep(1) # To walk around "nfs4_discover_server_trunking unhandled error -512. Exiting with error EIO" in c74

        if xmlobject.has_element(zone, 'primaryStorages.simulatorPrimaryStorage'):
            if zone.duplication__ == None:
                duplication = 1
            else:
                duplication = int(zone.duplication__)

            for pr in xmlobject.safe_list(zone.primaryStorages.simulatorPrimaryStorage):
                for zone_ref in range(duplication):
                    for cluster in xmlobject.safe_list(zone.clusters.cluster):
                        for pref in xmlobject.safe_list(cluster.primaryStorageRef):
                            if pref.text_ == pr.name_:
                                if cluster.duplication__ == None:
                                    cluster_duplication = 1
                                else:
                                    cluster_duplication = int(cluster.duplication__)

                                for cluster_ref in range(cluster_duplication):
                                    action = _generate_sim_ps_action(zone, pr, zone_ref, cluster_ref)
                                    thread = threading.Thread(target=_thread_for_action, args=(action,))
                                    wait_for_thread_queue()
                                    thread.start()

        if xmlobject.has_element(zone, 'primaryStorages.sharedMountPointPrimaryStorage'):
            zinvs = res_ops.get_resource(res_ops.ZONE, session_uuid, \
                    name=zone.name_)
            zinv = get_first_item_from_list(zinvs, 'Zone', zone.name_, 'primary storage')

            for pr in xmlobject.safe_list(zone.primaryStorages.sharedMountPointPrimaryStorage):
                if ps_name and ps_name != pr.name_:
                    continue

                action = api_actions.AddSharedMountPointPrimaryStorageAction()
                action.sessionUuid = session_uuid
                action.name = pr.name_
                action.description = pr.description__
                action.url = pr.url_
                action.zoneUuid = zinv.uuid
                thread = threading.Thread(target=_thread_for_action, args=(action,))
                wait_for_thread_queue()
                thread.start()

        if xmlobject.has_element(zone, 'primaryStorages.aliyunNASPrimaryStorage'):
            zinvs = res_ops.get_resource(res_ops.ZONE, session_uuid, \
                    name=zone.name_)
            zinv = get_first_item_from_list(zinvs, 'Zone', zone.name_, 'primary storage')
            ak_id = None
            new_ak_id = None
            for pr in xmlobject.safe_list(zone.primaryStorages.aliyunNASPrimaryStorage):
                if ps_name and ps_name != pr.name_:
                    continue
                hostname_list = get_primary_storage_from_scenario_file(pr.name_, scenarioConfig, scenarioFile, deployConfig)
                if len(hostname_list) == 0:
                    nasPath = pr.url_.split(':')[1]
                    cmd = "echo '%s *(rw,sync,no_root_squash)' > /etc/exports" % (nasPath)
                    cmd_rst = "service nfs-server stop; service nfs-server start"
                    os.system(cmd)
                    os.system(cmd_rst)
                    mn_ip = res_ops.get_resource(res_ops.MANAGEMENT_NODE, session_uuid=session_uuid)[0].hostName
                    if mn_ip:
                        uri = 'http://' + os.getenv('apiEndPoint').split('::')[-1] + '/mntarget'
                        ak_id = (mn_ip + str(time.time())).replace('.', '')
                        http.json_dump_post(uri, {"ak_id": ak_id, "mn_ip": mn_ip, "nfs_ip": mn_ip})
#                         http.json_dump_post(uri, {"mn_ip": mn_ip, "nfs_ip": mn_ip})
                # Update Global Config: user.define.api.endpoint
                cfg_ops.change_global_config(category='aliyun',
                                             name='user.define.api.endpoint',
                                             value=os.getenv('apiEndPoint'),
                                             session_uuid=session_uuid)
                # Add KS
#                 new_ak_id = os.getenv('NASAKID')
                if os.path.exists('/home/nas_ak_id'):
                    with open('/home/nas_ak_id', 'r') as f:
                        new_ak_id = f.read()
                default_ak_id = new_ak_id if new_ak_id else os.getenv('aliyunKey')
                hyb_ops.add_hybrid_key_secret(name='ks_for_nas_test',
                                              description='ks_for_nas_test',
                                              key= ak_id if ak_id else default_ak_id,
                                              secret=os.getenv('aliyunSecret'),
                                              ks_type=os.getenv('datacenterType'),
                                              sync='false',
                                              session_uuid=session_uuid)
                # Add DataCenter
                hyb_ops.add_datacenter_from_remote(datacenter_type=os.getenv('datacenterType'),
                                                   description='dc_for_nas_test',
                                                   region_id=os.getenv('regionId'),
                                                   session_uuid=session_uuid)
                # NAS file system and access group will be synced from remote automatically since 3.2.0
                try:
                    # Add NAS File System
                    dcinvs = res_ops.get_resource(res_ops.DATACENTER, session_uuid=session_uuid)
                    if dcinvs:
                        dcinv = dcinvs[0]
                    else:
                        raise test_util.TestError("Can't find Any DataCenter.")
                    nas_ops.add_aliyun_nas_file_system(datacenter_uuid=dcinv.uuid,
                                                       fsid=os.getenv('fileSystemId'),
                                                       name='setup_nasfs',
                                                       session_uuid=session_uuid)
                    # Add Aliyun Access Group
                    nas_ops.add_aliyun_nas_access_group(datacenter_uuid=dcinv.uuid,
                                                        group_name=os.getenv('groupName'),
                                                        session_uuid=session_uuid)
                except:
                    pass
                # Add AliyunNas PS
                grpinvs = res_ops.get_resource(res_ops.ALIYUNNAS_ACCESSGROUP, session_uuid=session_uuid)
                nasinvs = res_ops.get_resource(res_ops.NAS_FILESYSTEM, session_uuid=session_uuid)
                if grpinvs and nasinvs:
                    grpinv = grpinvs[0]
                    nasinv = nasinvs[0]
                else:
                    raise test_util.TestError("Can't find Aliyun NAS Access Group or File system.")
                action = api_actions.AddAliyunNasPrimaryStorageAction()
                action.name = 'AliyunNas'
                action.nasUuid = nasinv.uuid
                action.accessGroupUuid = grpinv.uuid
                action.url = '/' + str(time.time()).split('.')[0]
                action.zoneUuid = zinv.uuid
                action.sessionUuid = session_uuid
                thread = threading.Thread(target=_thread_for_action, args=(action,))
                wait_for_thread_queue()
                thread.start()

        if xmlobject.has_element(zone, 'primaryStorages.aliyunEBSPrimaryStorage'):
            zinvs = res_ops.get_resource(res_ops.ZONE, session_uuid, \
                    name=zone.name_)
            zinv = get_first_item_from_list(zinvs, 'Zone', zone.name_, 'primary storage')

            # Add KS
            hyb_ops.add_hybrid_key_secret(name='ks_for_ebs_test',
                                            description='ks_for_ebs_test',
                                            key= 'zstack',
                                            secret='C8yz6qLPus7VuwLtGYdxUkMg',
                                            ks_type=os.getenv('datacenterType'),
                                            sync='false',
                                            session_uuid=session_uuid)

            # Add DataCenter
            dc_inv = hyb_ops.add_datacenter_from_remote(datacenter_type=os.getenv('datacenterType'),
                                                description='dc_for_ebs_test',
                                                region_id=os.getenv('regionId'),
                                                end_point=os.getenv('ebsEndPoint'),
                                                session_uuid=session_uuid)

            # Add Identity Zone
            iz_inv = hyb_ops.get_identity_zone_from_remote(datacenter_type=os.getenv('datacenterType'), dc_uuid=dc_inv.uuid)
            if iz_inv:
                ebs_iz = iz_inv[0]
            else:
                test_util.test_fail('EBS Identity Zone was not found')
            hyb_ops.add_identity_zone_from_remote(iz_type=os.getenv('datacenterType'), datacenter_uuid=dc_inv.uuid, zone_id=ebs_iz.zoneId)

            for pr in xmlobject.safe_list(zone.primaryStorages.aliyunEBSPrimaryStorage):
                if ps_name and ps_name != pr.name_:
                    continue

                # Add AliyunEBS PS
                action = api_actions.AddAliyunEbsPrimaryStorageAction()
                action.name = 'ebs'
                iz_inv = hyb_ops.query_iz_local()
                if iz_inv:
                    action.identityZoneUuid = iz_inv[0].uuid
                else:
                    test_util.test_fail("No identity zone found in local")
                action.type = os.getenv('datacenterType')
                action.url = os.getenv('ebsEndPoint')
                action.tdcConfigContent = '{"tdcPort": "20120","tdcRegion": "region1",\
                                            "riverMaster": "nuwa://ECS-river/sys/houyi/river_master",\
                                            "server": "192.168.0.1:10240,192.168.0.2:10240,192.168.0.3:10240",\
                                            "proxy": "192.168.1.1:10240,192.168.1.2:10240,192.168.1.3:10240",\
                                            "cluster": "ECS-river"}'
                action.zoneUuid = zinv.uuid
                action.sessionUuid = session_uuid
                thread = threading.Thread(target=_thread_for_action, args=(action, True))
                wait_for_thread_queue()
                thread.start()

    for zone in xmlobject.safe_list(deployConfig.zones.zone):
        if zone_name and zone.name_ != zone_name:
            continue
        _deploy_primary_storage(zone)

    wait_for_thread_done()

def add_iscsi_server(scenarioConfig, scenarioFile, deployConfig, session_uuid, cluster_name = None, zone_name = None):
    if not xmlobject.has_element(deployConfig, "zones.zone.iscsiLun"):
        return
    target_ip = get_scsi_target_ip(scenarioFile)
    pr = xmlobject.safe_list(deployConfig.zones.zone.iscsiLun)[0]

    def _add_iscsi_server(target_ip):
        action = api_actions.AddIscsiServerAction()
        action.name = pr.name_
        action.ip = target_ip
        action.port = 3260
        action.chapUserName = None
        action.chapUserPassword = None
        action.sessionUuid = session_uuid
        try:
            evt = action.run()
            test_util.test_logger(jsonobject.dumps(evt))
        except Exception as e:
            exc_info.append(sys.exc_info())

    thread = threading.Thread(target=_add_iscsi_server, args=(target_ip,))
    wait_for_thread_queue()
    thread.start()
    wait_for_thread_done()
#Add Cluster
def add_cluster(scenarioConfig, scenarioFile, deployConfig, session_uuid, cluster_name = None, \
        zone_name = None):
    if not xmlobject.has_element(deployConfig, "zones.zone"):
        return

    def _add_cluster(action, zone_ref, cluster, cluster_ref):
        evt = action.run()
        test_util.test_logger(jsonobject.dumps(evt))
        cinv = evt.inventory

        try:
            if xmlobject.has_element(cluster, 'primaryStorageRef'):
                for pref in xmlobject.safe_list(cluster.primaryStorageRef):
                    ps_name = generate_dup_name(generate_dup_name(pref.text_, zone_ref, 'z'), cluster_ref, 'c')

                    pinvs = res_ops.get_resource(res_ops.PRIMARY_STORAGE, session_uuid, name=ps_name)
                    pinv = get_first_item_from_list(pinvs, 'Primary Storage', ps_name, 'Cluster')

                    action_ps = api_actions.AttachPrimaryStorageToClusterAction()
                    action_ps.sessionUuid = session_uuid
                    action_ps.clusterUuid = cinv.uuid
                    action_ps.primaryStorageUuid = pinv.uuid
                    evt = action_ps.run()
                    test_util.test_logger(jsonobject.dumps(evt))
        except:
            exc_info.append(sys.exc_info())
     
        try:
            if xmlobject.has_element(cluster, 'iscsiLunRef'):
                for lun in xmlobject.safe_list(cluster.iscsiLunRef):
                    iscsi_server = generate_dup_name(generate_dup_name(lun.text_, zone_ref, 'z'), cluster_ref, 'c')
                    iscsi_uuid = res_ops.get_resource(res_ops.ISCSI_SERVER, session_uuid, name=iscsi_server)[0].uuid
                    action_iscsi = api_actions.AttachIscsiServerToClusterAction()
                    action_iscsi.sessionUuid = session_uuid
                    action_iscsi.uuid = iscsi_uuid
                    action_iscsi.clusterUuid = cinv.uuid
                    evt = action_iscsi.run()
                    test_util.test_logger(jsonobject.dumps(evt))
        except:
            exc_info.append(sys.exc_info())
                    

        if cluster.allL2NetworkRef__ == 'true':
            #find all L2 network in zone and attach to cluster
            cond = res_ops.gen_query_conditions('zoneUuid', '=', \
                    action.zoneUuid)
            l2_count = res_ops.query_resource_count(res_ops.L2_NETWORK, \
                    cond, session_uuid)
            l2invs = res_ops.query_resource_fields(res_ops.L2_NETWORK, \
                    [{'name':'zoneUuid', 'op':'=', 'value':action.zoneUuid}], \
                    session_uuid, ['uuid'], 0, l2_count)
        else:
            l2invs = []
            if xmlobject.has_element(cluster, 'l2NetworkRef'):
                for l2ref in xmlobject.safe_list(cluster.l2NetworkRef):
                    l2_name = generate_dup_name(generate_dup_name(l2ref.text_, zone_ref, 'z'), cluster_ref, 'c')

                    cond = res_ops.gen_query_conditions('zoneUuid', '=', \
                            action.zoneUuid)
                    cond = res_ops.gen_query_conditions('name', '=', l2_name, \
                            cond)
                            
                    l2inv = res_ops.query_resource_fields(res_ops.L2_NETWORK, \
                            cond, session_uuid, ['uuid'])
                    if not l2inv:
                        raise test_util.TestError("Can't find l2 network [%s] in database." % l2_name)
                    l2invs.extend(l2inv)

        for l2inv in l2invs:
            action = api_actions.AttachL2NetworkToClusterAction()
            action.sessionUuid = session_uuid
            action.clusterUuid = cinv.uuid
            action.l2NetworkUuid = l2inv.uuid
            thread = threading.Thread(target=_thread_for_action, args=(action,))
            wait_for_thread_queue()
            thread.start()


    #def _add_l2VxlanNetwork(zone_uuid, zone_ref, cluster, cluster_ref, cluster_uuid):
    def _add_l2VxlanNetwork(zone_uuid, cluster, cluster_uuid):
        if xmlobject.has_element(cluster, 'l2VxlanNetworkPoolRef'):
            for l2vxlanpoolref in xmlobject.safe_list(cluster.l2VxlanNetworkPoolRef):
                l2_vxlan_pool_name = l2vxlanpoolref.text_
                poolinvs = res_ops.get_resource(res_ops.L2_VXLAN_NETWORK_POOL, session_uuid, name=l2_vxlan_pool_name)
                poolinv = get_first_item_from_list(poolinvs, 'L2 Vxlan Network Pool', l2_vxlan_pool_name, 'Cluster')

                l2_vxlan_pool_name = l2vxlanpoolref.text_
                action_vxlan = api_actions.AttachL2NetworkToClusterAction()
                action_vxlan.l2NetworkUuid = poolinv.uuid
                action_vxlan.clusterUuid = cluster_uuid
                action_vxlan.systemTags = ["l2NetworkUuid::%s::clusterUuid::%s::cidr::{%s}" % (poolinv.uuid, cluster_uuid, l2vxlanpoolref.cidr_)]
                action_vxlan.sessionUuid = session_uuid
                evt = action_vxlan.run()

	if xmlobject.has_element(zone.l2Networks, 'l2VxlanNetwork'):
            for l2_vxlan in xmlobject.safe_list(zone.l2Networks.l2VxlanNetwork):
                if xmlobject.has_element(l2_vxlan, 'l2VxlanNetworkPoolRef'):
                    l2_vxlan_invs = res_ops.get_resource(res_ops.L2_VXLAN_NETWORK, session_uuid, name=l2_vxlan.name_)
                    if len(l2_vxlan_invs) > 0:
                        continue
                    l2_vxlan_pool_name = l2vxlanpoolref.text_
                    poolinvs = res_ops.get_resource(res_ops.L2_VXLAN_NETWORK_POOL, session_uuid, name=l2_vxlan_pool_name)
                    poolinv = get_first_item_from_list(poolinvs, 'L2 Vxlan Network Pool', l2_vxlan_pool_name, 'Cluster')
                    test_util.test_logger("vxlan@@:%s" %(l2_vxlan.name_))
                    action_vxlan = api_actions.CreateL2VxlanNetworkAction()
                    action_vxlan.poolUuid = poolinv.uuid
                    action_vxlan.name = l2_vxlan.name_
                    action_vxlan.zoneUuid = zone_uuid 
                    action_vxlan.sessionUuid = session_uuid
                    evt = action_vxlan.run()

        #if clustVer.allL2NetworkRef__ == 'true':
        #    #find all L2 Vxlan network in zone and attach to cluster
        #    cond = res_ops.gen_query_conditions('zoneUuid', '=', \
        #            zone_uuid)
        #    l2_count = res_ops.query_resource_count(res_ops.L2_VXLAN_NETWORK, \
        #            cond, session_uuid)
        #    l2invs = res_ops.query_resource_fields(res_ops.L2_VXLAN_NETWORK, \
        #            [{'name':'zoneUuid', 'op':'=', 'value':zone_uuid}], \
        #            session_uuid, ['uuid'], 0, l2_count)
        #else:
        #    l2invs = []
        #    if xmlobject.has_element(cluster, 'l2NetworkRef'):
        #        for l2ref in xmlobject.safe_list(cluster.l2NetworkRef):
        #            l2_name = generate_dup_name(generate_dup_name(l2ref.text_, zone_ref, 'z'), cluster_ref, 'c')

        #            cond = res_ops.gen_query_conditions('zoneUuid', '=', \
        #                    zone_uuid)
        #            cond = res_ops.gen_query_conditions('name', '=', l2_name, \
        #                    cond)
        #                    
        #            l2inv = res_ops.query_resource_fields(res_ops.L2_VXLAN_NETWORK, \
        #                    cond, session_uuid, ['uuid'])
        #            if not l2inv:
        #                raise test_util.TestError("Can't find l2 network [%s] in database." % l2_name)
        #            l2invs.extend(l2inv)

        #for l2inv in l2invs:
        #    action = api_actions.AttachL2NetworkToClusterAction()
        #    action.sessionUuid = session_uuid
        #    action.clusterUuid = cluster_uuid
        #    action.l2NetworkUuid = l2inv.uuid
        #    thread = threading.Thread(target=_thread_for_action, args=(action,))
        #    wait_for_thread_queue()
        #    thread.start()

    def _deploy_cluster(zone):
        if not xmlobject.has_element(zone, "clusters.cluster"):
            return

        if zone.duplication__ == None:
            zone_duplication = 1
        else:
            zone_duplication = int(zone.duplication__)

        for zone_ref in range(zone_duplication):
            for cluster in xmlobject.safe_list(zone.clusters.cluster):
                if cluster_name and cluster_name != cluster.name_:
                    continue

                if cluster.duplication__ == None:
                    cluster_duplication = 1
                else:
                    cluster_duplication = int(cluster.duplication__)
    
                for cluster_ref in range(cluster_duplication):
                    zone_name = generate_dup_name(zone.name_, zone_ref, 'z')
        
                    zinvs = res_ops.get_resource(res_ops.ZONE, session_uuid, name=zone_name)
                    zinv = get_first_item_from_list(zinvs, 'Zone', zone_name, 'Cluster')

                    action = api_actions.CreateClusterAction()
                    action.sessionUuid = session_uuid
                    action.name = generate_dup_name(generate_dup_name(cluster.name_, zone_ref, 'z'), cluster_ref, 'c')
                    action.description = generate_dup_name(generate_dup_name(cluster.description__, zone_ref, 'z'), cluster_ref, 'c')
        
                    action.hypervisorType = cluster.hypervisorType_
                    action.zoneUuid = zinv.uuid
                    thread = threading.Thread(target=_add_cluster, args=(action, zone_ref, cluster, cluster_ref, ))

                    wait_for_thread_queue()
                    thread.start()

    def _deploy_mini_cluster(zone):
        if not xmlobject.has_element(zone, "clusters.cluster"):
            return

        if zone.duplication__ == None:
            zone_duplication = 1
        else:
            zone_duplication = int(zone.duplication__)

        if os.getenv('ZSTACK_SIMULATOR') == 'yes':
            http = urllib3.PoolManager()
            mn_ip = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].hostName
            url = "http://%s:8080/zstack/simulators/query" % (mn_ip)
            query_data = simplejson.dumps({'sql':'select * from KvmHost', 'type':'KvmHost'})
            rsp = http.request('GET', url, body=query_data)
            host_obj = jsonobject.loads(rsp.data)
            vm_ip_list = [host.ip for host in host_obj]
        else:
            vm_ip_list = get_vm_ip_from_scenariofile(scenarioFile)
        for zone_ref in range(zone_duplication):
            for cluster in xmlobject.safe_list(zone.clusters.cluster):
                if cluster_name and cluster_name != cluster.name_:
                    continue

                if cluster.duplication__ == None:
                    cluster_duplication = 1
                else:
                    cluster_duplication = int(cluster.duplication__)
                for cluster_ref in range(cluster_duplication):
                    zone_name = generate_dup_name(zone.name_, zone_ref, 'z')
                    zinvs = res_ops.get_resource(res_ops.ZONE, session_uuid, name=zone_name)
                    zinv = get_first_item_from_list(zinvs, 'Zone', zone_name, 'Cluster')
                    action = api_actions.CreateMiniClusterAction()
                    action.sessionUuid = session_uuid
                    action.name = generate_dup_name(generate_dup_name(cluster.name_, zone_ref, 'z'), cluster_ref, 'c')
                    action.description = generate_dup_name(generate_dup_name(cluster.description__, zone_ref, 'z'), cluster_ref, 'c')
                    action.hypervisorType = cluster.hypervisorType_
                    action.zoneUuid = zinv.uuid
                    action.password = "password"
                    action.sshPort = "22"
                    hostManagementIps = vm_ip_list[0] + ',' + vm_ip_list[1]
                    action.hostManagementIps = hostManagementIps.split(',')
                    print " action.hostManagementIps : %s" % action.hostManagementIps
                    thread = threading.Thread(target=_add_cluster, args=(action, zone_ref, cluster, cluster_ref, ))
                    wait_for_thread_queue()
                    thread.start()

    for zone in xmlobject.safe_list(deployConfig.zones.zone):
        if zone_name and zone_name != zone.name_:
            continue 
        if xmlobject.has_element(deployConfig, 'backupStorages.miniBackupStorage'):
            _deploy_mini_cluster(zone)
        else:
            _deploy_cluster(zone)
    wait_for_thread_done()

    for zone in xmlobject.safe_list(deployConfig.zones.zone):
        if zone_name and zone_name != zone.name_:
            continue 

        if zone.duplication__ == None:
            zone_duplication = 1
        else:
            zone_duplication = int(zone.duplication__)

        for zone_ref in range(zone_duplication):
            for cluster in xmlobject.safe_list(zone.clusters.cluster):
                if cluster_name and cluster_name != cluster.name_:
                    continue
    
                if cluster.duplication__ == None:
                    cluster_duplication = 1
                else:
                    cluster_duplication = int(cluster.duplication__)
        
                for cluster_ref in range(cluster_duplication):
                    zone_name = generate_dup_name(zone.name_, zone_ref, 'z')
                    zinvs = res_ops.get_resource(res_ops.ZONE, session_uuid, name=zone_name)
                    zinv = get_first_item_from_list(zinvs, 'Zone', zone_name, 'Cluster')

                    cinvs = res_ops.get_resource(res_ops.CLUSTER, session_uuid, name=cluster.name_)
                    cinv = get_first_item_from_list(cinvs, 'Cluster', cluster.name_, '_add_l2VxlanNetwork')
                    _add_l2VxlanNetwork(zinv.uuid, cluster, cinv.uuid)


def get_node_from_scenario_file(nodeRefName, scenarioConfig, scenarioFile, deployConfig):
    if scenarioConfig == None or scenarioFile == None or not os.path.exists(scenarioFile):
        return None

    s_l3_uuid = None
    for zone in xmlobject.safe_list(deployConfig.deployerConfig.zones.zone):

        if hasattr(zone.l2Networks, 'l2NoVlanNetwork'):

            for l2novlannetwork in xmlobject.safe_list(zone.l2Networks.l2NoVlanNetwork):

                for l3network in xmlobject.safe_list(l2novlannetwork.l3Networks.l3BasicNetwork):
                    if hasattr(l3network, 'category_') and l3network.category_ == 'System':
                        for host in xmlobject.safe_list(scenarioConfig.deployerConfig.hosts.host):
                            for vm in xmlobject.safe_list(host.vms.vm):
                                if xmlobject.has_element(vm, 'nodeRef'):
                                    for l3Network in xmlobject.safe_list(vm.l3Networks.l3Network):
                                        if hasattr(l3Network, 'l2NetworkRef'):

                                            for l2networkref in xmlobject.safe_list(l3Network.l2NetworkRef):

                                                if l2networkref.text_ == l2novlannetwork.name_:
                                                    s_l3_uuid = l3Network.uuid_

    for host in xmlobject.safe_list(scenarioConfig.deployerConfig.hosts.host):
        for vm in xmlobject.safe_list(host.vms.vm):
            if xmlobject.has_element(vm, 'nodeRef'):
                if vm.nodeRef.text_ == nodeRefName:
                    with open(scenarioFile, 'r') as fd:
                        xmlstr = fd.read()
                        fd.close()
                        scenario_file = xmlobject.loads(xmlstr)
                        for s_vm in xmlobject.safe_list(scenario_file.vms.vm):
                            if s_vm.name_ == vm.name_:
                                if s_l3_uuid == None:
                                    return s_vm.ip_
                                else:
                                    for ip in xmlobject.safe_list(s_vm.ips.ip):
                                        if ip.uuid_ == s_l3_uuid:
                                            return ip.ip_

    for host in xmlobject.safe_list(scenarioConfig.deployerConfig.hosts.host):
        for vm in xmlobject.safe_list(host.vms.vm):
            if xmlobject.has_element(vm, 'nodeRef'):
                if vm.nodeRef.text_ == nodeRefName:
                    with open(scenarioFile, 'r') as fd:
                        xmlstr = fd.read()
                        fd.close()
                        scenario_file = xmlobject.loads(xmlstr)
                        for s_vm in xmlobject.safe_list(scenario_file.vms.vm):
                            if s_vm.name_ == vm.name_:
                                return s_vm.ip_

    return None

def get_nodes_from_scenario_file(scenarioConfig, scenarioFile, deployConfig):
    if scenarioConfig == None or scenarioFile == None or not os.path.exists(scenarioFile):
        return None

    s_l3_uuid = None
    for zone in xmlobject.safe_list(deployConfig.zones.zone):

        if hasattr(zone.l2Networks, 'l2NoVlanNetwork'):

            for l2novlannetwork in xmlobject.safe_list(zone.l2Networks.l2NoVlanNetwork):

                for l3network in xmlobject.safe_list(l2novlannetwork.l3Networks.l3BasicNetwork):
                    if hasattr(l3network, 'category_') and l3network.category_ == 'System':
                        for host in xmlobject.safe_list(scenarioConfig.deployerConfig.hosts.host):
                            for vm in xmlobject.safe_list(host.vms.vm):
                                if xmlobject.has_element(vm, 'nodeRef'):
                                    for l3Network in xmlobject.safe_list(vm.l3Networks.l3Network):
                                        if hasattr(l3Network, 'l2NetworkRef'):

                                            for l2networkref in xmlobject.safe_list(l3Network.l2NetworkRef):

                                                if l2networkref.text_ == l2novlannetwork.name_:
                                                    s_l3_uuid = l3Network.uuid_

    nodes_ip = ''
    for host in xmlobject.safe_list(scenarioConfig.deployerConfig.hosts.host):
        for vm in xmlobject.safe_list(host.vms.vm):
            if xmlobject.has_element(vm, 'nodeRef'):
                with open(scenarioFile, 'r') as fd:
                    xmlstr = fd.read()
                    fd.close()
                    scenario_file = xmlobject.loads(xmlstr)
                    for s_vm in xmlobject.safe_list(scenario_file.vms.vm):
                        if s_vm.name_ == vm.name_:
                            if s_l3_uuid == None:
                                nodes_ip += ' %s' % s_vm.ip_
                            else:
                                for ip in xmlobject.safe_list(s_vm.ips.ip):
                                    if ip.uuid_ == s_l3_uuid:
                                        return ip.ip_

    for host in xmlobject.safe_list(scenarioConfig.deployerConfig.hosts.host):
        for vm in xmlobject.safe_list(host.vms.vm):
            if xmlobject.has_element(vm, 'nodeRef'):
                with open(scenarioFile, 'r') as fd:
                    xmlstr = fd.read()
                    fd.close()
                    scenario_file = xmlobject.loads(xmlstr)
                    for s_vm in xmlobject.safe_list(scenario_file.vms.vm):
                        if s_vm.name_ == vm.name_:
                            nodes_ip += ' %s' % s_vm.ip_

    return nodes_ip

def get_host_from_scenario_file(hostRefName, scenarioConfig, scenarioFile, deployConfig):
    if scenarioConfig == None or scenarioFile == None or not os.path.exists(scenarioFile):
        return None

    for host in xmlobject.safe_list(scenarioConfig.deployerConfig.hosts.host):
        for vm in xmlobject.safe_list(host.vms.vm):
            if xmlobject.has_element(vm, 'hostRef'):
                if vm.hostRef.text_ == hostRefName:
                    with open(scenarioFile, 'r') as fd:
                        xmlstr = fd.read()
                        fd.close()
                        scenario_file = xmlobject.loads(xmlstr)
                        for s_vm in xmlobject.safe_list(scenario_file.vms.vm):
                            if s_vm.name_ == vm.name_:
                                if xmlobject.has_element(s_vm, 'managementIp_') and s_vm.managementIp_ != s_vm.ip_:
                                    return s_vm.managementIp_
                                else:
                                    return s_vm.ip_
    return None

def get_hosts_from_scenario_file(scenarioConfig, scenarioFile, deployConfig):
    if scenarioConfig == None or scenarioFile == None or not os.path.exists(scenarioFile):
        return None

    host_ips = ''
    for host in xmlobject.safe_list(scenarioConfig.deployerConfig.hosts.host):
        for vm in xmlobject.safe_list(host.vms.vm):
            if xmlobject.has_element(vm, 'hostRef'):
                    with open(scenarioFile, 'r') as fd:
                        xmlstr = fd.read()
                        fd.close()
                        scenario_file = xmlobject.loads(xmlstr)
                        for s_vm in xmlobject.safe_list(scenario_file.vms.vm):
                            if s_vm.name_ == vm.name_:
                                if xmlobject.has_element(s_vm, 'managementIp_') and s_vm.managementIp_ != s_vm.ip_:
                                    host_ips += ' %s' % s_vm.managementIp_
                                else:
                                    host_ips += ' %s' % s_vm.ip_
    return host_ips

def get_iscsi_nfs_host_from_scenario_file(hostRefName, scenarioConfig, scenarioFile, deployConfig):
    if scenarioConfig == None or scenarioFile == None or not os.path.exists(scenarioFile):
        return None

    for host in xmlobject.safe_list(scenarioConfig.deployerConfig.hosts.host):
        for vm in xmlobject.safe_list(host.vms.vm):
            if vm.name_ == hostRefName:
                with open(scenarioFile, 'r') as fd:
                    xmlstr = fd.read()
                    fd.close()
                    scenario_file = xmlobject.loads(xmlstr)
                    for s_vm in xmlobject.safe_list(scenario_file.vms.vm):
                        if s_vm.name_ == vm.name_:
                            if xmlobject.has_element(s_vm, 'managementIp_') and s_vm.managementIp_ != s_vm.ip_:
                                return s_vm.managementIp_
                            else:
                                return s_vm.ip_
    return None


def get_host_obj_from_scenario_file(hostRefName, scenarioConfig, scenarioFile, deployConfig):
    if scenarioConfig == None or scenarioFile == None or not os.path.exists(scenarioFile):
        return None

    for host in xmlobject.safe_list(scenarioConfig.deployerConfig.hosts.host):
        for vm in xmlobject.safe_list(host.vms.vm):
            if xmlobject.has_element(vm, 'hostRef'):
                if vm.hostRef.text_ == hostRefName:
                    with open(scenarioFile, 'r') as fd:
                        xmlstr = fd.read()
                        fd.close()
                        scenario_file = xmlobject.loads(xmlstr)
                        for s_vm in xmlobject.safe_list(scenario_file.vms.vm):
                            if s_vm.name_ == vm.name_:
                                return s_vm
    return None


#Add sanlock
def add_sanlock(scenarioConfig, scenarioFile, deployConfig, session_uuid):
    '''
    sanlock creation and enable for sharedblock ps
    '''

    import zstackwoodpecker.test_lib as test_lib

    if test_lib.lib_cur_cfg_is_a_and_b(["test-config-flat-imagestore-iscsi.xml"], ["scenario-config-iscsi.xml"]):
        import scenario_operations as sce_ops
        import zstacklib.utils.ssh as ssh

        def _get_vm_config(vm_inv):
            if hasattr(scenarioConfig.deployerConfig, 'hosts'):
                for host in xmlobject.safe_list(scenarioConfig.deployerConfig.hosts.host):
                    for vm in xmlobject.safe_list(host.vms.vm):
                        if vm.name_ == vm_inv.name:
                            return vm
            return None

        def _get_vm_inv_by_vm_ip(zstack_management_ip, vm_ip):
            cond = res_ops.gen_query_conditions('vmNics.ip', '=', vm_ip)
            vm_inv = sce_ops.query_resource(zstack_management_ip, res_ops.VM_INSTANCE, cond).inventories[0]
            return vm_inv

        host_ips = sce_ops.dump_scenario_file_ips(scenarioFile)
        vm_ip = host_ips[-1]
        host_port = 22
        zstack_management_ip = scenarioConfig.basicConfig.zstackManagementIp.text_

        vm_inv = _get_vm_inv_by_vm_ip(zstack_management_ip, vm_ip)
        vm_config = _get_vm_config(vm_inv)

        #Below optimize is aim to migrate sanlock to separated partition, don't delete!!!
        #cmd = "vgcreate --shared zstacksanlock /dev/mapper/mpatha1"
        #sce_ops.exec_cmd_in_vm(cmd, vm_ip, vm_config, True, host_port)

        #cmd = "vgchange --lock-start zstacksanlock"
        #sce_ops.exec_cmd_in_vm(cmd, vm_ip, vm_config, True, host_port)

        #vg_name = get_disk_uuid(scenarioFile)
        #cmd = "lvmlockctl --gl-disable %s" %(vg_name)
        #sce_ops.exec_cmd_in_vm(cmd, vm_ip, vm_config, True, host_port)

        #cmd = "lvmlockctl --gl-enable zstacksanlock"
        #sce_ops.exec_cmd_in_vm(cmd, vm_ip, vm_config, True, host_port)
    

#Add Host
def add_host(scenarioConfig, scenarioFile, deployConfig, session_uuid, host_ip = None, zone_name = None, \
        cluster_name = None):
    '''
    Base on an xml deploy config object to add hosts. 
    If providing giving zone_name, cluster_name or host_ip, this function will
    only add related hosts. 
    '''
    if not xmlobject.has_element(deployConfig, "zones.zone"):
        return

    def _deploy_host(cluster, zone_ref, cluster_ref):
        if not xmlobject.has_element(cluster, "hosts.host"):
            return

        if zone_ref == 0 and cluster_ref == 0:
            cluster_name = cluster.name_
        else:
            cluster_name = generate_dup_name(generate_dup_name(cluster.name_, zone_ref, 'z'), cluster_ref, 'c')
        
        cinvs = res_ops.get_resource(res_ops.CLUSTER, session_uuid, name=cluster_name)
        cinv = get_first_item_from_list(cinvs, 'Cluster', cluster_name, 'L3 network')
        count = 0
        for host in xmlobject.safe_list(cluster.hosts.host):
            count += 1
            if host_ip and host_ip != host.managementIp_:
                continue

            if host.duplication__ == None:
                host_duplication = 1
            else:
                host_duplication = int(host.duplication__)

            for i in range(host_duplication):
                if cluster.hypervisorType_ == inventory.KVM_HYPERVISOR_TYPE:
                    action = api_actions.AddKVMHostAction()
                    action.username = host.username_
                    action.password = host.password_
		    if hasattr(host, 'port_'):
			action.port = host.port_
			action.sshport = host.port_
			action.sshPort = host.port_
                    action.timeout = AddKVMHostTimeOut
                elif cluster.hypervisorType_ == inventory.SIMULATOR_HYPERVISOR_TYPE:
                    action = api_actions.AddSimulatorHostAction()
                    action.cpuCapacity = host.cpuCapacity_
                    action.memoryCapacity = sizeunit.get_size(host.memoryCapacity_)
    
                action.sessionUuid = session_uuid
                action.clusterUuid = cinv.uuid
                action.hostTags = host.hostTags__
                if zone_duplication == 0 and cluster_duplication == 0:
                    action.name = host.name_
                    action.description = host.description__
                    managementIp = get_host_from_scenario_file(host.name_, scenarioConfig, scenarioFile, deployConfig)
                    if managementIp != None:
                        action.managementIp = managementIp
                    else:
                        action.managementIp = host.managementIp_
                else:
                    action.name = generate_dup_name(generate_dup_name(generate_dup_name(host.name_, zone_ref, 'z'), cluster_ref, 'c'), i, 'h')
                    action.description = generate_dup_name(generate_dup_name(generate_dup_name(host.description__, zone_ref, 'z'), cluster_ref, 'c'), i, 'h')
                    action.managementIp = generate_dup_host_ip(host.managementIp_, zone_ref, cluster_ref, i)

                if count == 1 and xmlobject.has_element(deployConfig, 'backupStorages.xskycephBackupStorage'):
                    print "skip xsky MN host add to computational node"
                else:
                    thread = threading.Thread(target=_thread_for_action, args = (action, True))
                    wait_for_thread_queue()
                    thread.start()
                    if i != 1:
                        time.sleep(1)

    for zone in xmlobject.safe_list(deployConfig.zones.zone):
        if zone_name and zone_name != zone.name_:
            continue

        if not xmlobject.has_element(zone, 'clusters.cluster'):
            continue

        if zone.duplication__ == None:
            zone_duplication = 1
        else:
            zone_duplication = int(zone.duplication__)

        for zone_ref in range(zone_duplication):
            for cluster in xmlobject.safe_list(zone.clusters.cluster):
                if cluster_name and cluster_name != cluster.name_:
                    continue

                if cluster.duplication__ == None:
                    cluster_duplication = 1
                else:
                    cluster_duplication = int(cluster.duplication__)

                for cluster_ref in range(cluster_duplication):
                    if xmlobject.has_element(deployConfig, 'backupStorages.miniBackupStorage'):
                        print "Mini Host have been added while creating mini cluster"
                    else:
                        _deploy_host(cluster, zone_ref, cluster_ref)

    wait_for_thread_done()
    test_util.test_logger('All add KVM host actions are done.')

#Add L3 network
def add_l3_network(scenarioConfig, scenarioFile, deployConfig, session_uuid, l3_name = None, l2_name = None, \
        zone_name = None):
    '''
    add_l3_network will add L3 network and also add related DNS, IpRange and 
    network services. 
    '''
    if not xmlobject.has_element(deployConfig, "zones.zone"):
        return


    def _deploy_l3_network(l2, zone_ref, cluster_ref):
        if not xmlobject.has_element(l2, "l3Networks.l3BasicNetwork"):
            return

        if not l2.duplication__:
            l2_dup = 1
        else:
            l2_dup = int(l2.duplication__)

        for l2_num in range(l2_dup):
            for l3 in xmlobject.safe_list(l2.l3Networks.l3BasicNetwork):
                if l3_name and l3_name != l3.name_:
                    continue 
    
                l2Name = generate_dup_name(generate_dup_name(generate_dup_name(l2.name_, zone_ref, 'z'), cluster_ref, 'c'), l2_num, 'n')
                l3Name = generate_dup_name(generate_dup_name(generate_dup_name(l3.name_, zone_ref, 'z'), cluster_ref, 'c'), l2_num, 'n')

                l2invs = res_ops.get_resource(res_ops.L2_NETWORK, \
                        session_uuid, \
                        name=l2Name)
                l2inv = get_first_item_from_list(l2invs, \
                        'L2 Network', l2Name, 'L3 Network')

                thread = threading.Thread(target=_do_l3_deploy, \
                        args=(l3, l2inv.uuid, l3Name, session_uuid, ))
                wait_for_thread_queue()
                thread.start()

    def _do_l3_deploy(l3, l2inv_uuid, l3Name, session_uuid):
        action = api_actions.CreateL3NetworkAction()
        action.sessionUuid = session_uuid
        action.description = l3.description__
        if l3.system__ and l3.system__ != 'False':
            action.system = 'true'
            action.category = 'System'
        action.l2NetworkUuid = l2inv_uuid
        action.name = l3Name
        action.type = inventory.L3_BASIC_NETWORK_TYPE
        if l3.domain_name__:
            action.dnsDomain = l3.domain_name__

        if l3.hasattr('ipVersion_'):
            action.ipVersion = l3.ipVersion_
        if l3.hasattr('category_'):
            action.category = l3.category_
        elif not l3.hasattr('system_') or l3.system_ == False:
            action.category = 'Private'
        if l3.hasattr('type_'):
            action.type = l3.type_
        try:
            evt = action.run()
        except:
            exc_info.append(sys.exc_info())

        test_util.test_logger(jsonobject.dumps(evt))
        l3_inv = evt.inventory

        if l3.hasattr('ipVersion_'):
        #add dns
            if xmlobject.has_element(l3, 'dns'):
                for dns in xmlobject.safe_list(l3.dns):
                    action = api_actions.AddDnsToL3NetworkAction()
                    action.sessionUuid = session_uuid
                    action.dns = dns.text_
                    action.l3NetworkUuid = l3_inv.uuid
                    try:
                        evt = action.run()
                    except:
                        exc_info.append(sys.exc_info())
                    test_util.test_logger(jsonobject.dumps(evt))
            #add ip range. 
            if xmlobject.has_element(l3, 'ipRange'):
                do_add_ip_range(l3.ipRange, l3_inv.uuid, session_uuid, ipversion = 6)
            else:
                do_add_ip_cidr(l3.ipv6Cidr, l3_inv.uuid, session_uuid, ipversion = 6)
        else:
            if xmlobject.has_element(l3, 'dns'):
                for dns in xmlobject.safe_list(l3.dns):
                    action = api_actions.AddDnsToL3NetworkAction()
                    action.sessionUuid = session_uuid
                    action.dns = dns.text_
                    action.l3NetworkUuid = l3_inv.uuid
                    try:
                        evt = action.run()
                    except:
                        exc_info.append(sys.exc_info())
                    test_util.test_logger(jsonobject.dumps(evt))
            #add ip range. 
            if xmlobject.has_element(l3, 'ipRange'):
                do_add_ip_range(l3.ipRange, l3_inv.uuid, session_uuid, ipversion = 4)

        #add network service.
        providers = {}
        action = api_actions.QueryNetworkServiceProviderAction()
        action.sessionUuid = session_uuid
        action.conditions = []
        try:
            reply = action.run()
        except:
            exc_info.append(sys.exc_info())
        for pinv in reply:
            providers[pinv.name] = pinv.uuid

        if xmlobject.has_element(l3, 'networkService'):
            do_add_network_service(l3.networkService, l3_inv.uuid, \
                    providers, session_uuid)

    for zone in xmlobject.safe_list(deployConfig.zones.zone):
        if zone_name and zone_name != zone.name_:
            continue 

        l2networks = []

        if xmlobject.has_element(zone, 'l2Networks.l2NoVlanNetwork'):
            l2networks.extend(xmlobject.safe_list(zone.l2Networks.l2NoVlanNetwork))

        if xmlobject.has_element(zone, 'l2Networks.l2VlanNetwork'):
            l2networks.extend(xmlobject.safe_list(zone.l2Networks.l2VlanNetwork))

        if xmlobject.has_element(zone, 'l2Networks.l2VxlanNetwork'):
            l2networks.extend(xmlobject.safe_list(zone.l2Networks.l2VxlanNetwork))

        for l2 in l2networks:
            if l2_name and l2_name != l2.name_:
                continue

            if zone.duplication__ == None:
                duplication = 1
            else:
                duplication = int(zone.duplication__)

            if duplication == 1:
                _deploy_l3_network(l2, 0, 0)
            else:
                for zone_ref in range(duplication):
                    for cluster in xmlobject.safe_list(zone.clusters.cluster):
                        if cluster.duplication__ == None:
                            cluster_duplication = 1
                        else:
                            cluster_duplication = int(cluster.duplication__)
        
                        for cluster_ref in range(cluster_duplication):
                            if zone_ref == 1 and cluster_ref == 1:
                                zone_ref = 0
                                cluster_ref = 0
                            _deploy_l3_network(l2, zone_ref, cluster_ref)

    wait_for_thread_done()
    test_util.test_logger('All add L3 Network actions are done.')

#Add Iprange
def add_ip_range(deployConfig, session_uuid, ip_range_name = None, \
        zone_name= None, l3_name = None, ipversion = 4):
    '''
    Call by only adding an IP range. If the IP range is in L3 config, 
    add_l3_network will add ip range direclty. 

    deployConfig is a xmlobject. If using standard net_operation, please 
    check net_operations.add_ip_range(test_util.IpRangeOption())
    '''
    if not xmlobject.has_element(deployConfig, "zones.zone"):
        return

    l3networks = []
    for zone in xmlobject.safe_list(deployConfig.zones.zone):
        if zone_name and zone_name != zone.name_:
            continue

        l2networks = []

        if xmlobject.has_element(zone, 'l2Networks.l2NoVlanNetwork'):
            l2networks.extend(xmlobject.safe_list(zone.l2Networks.l2NoVlanNetwork))

        if xmlobject.has_element(zone, 'l2Networks.l2VlanNetwork'):
            l2networks.extend(xmlobject.safe_list(zone.l2Networks.l2VlanNetwork))

        for l2 in l2networks:
            if xmlobject.has_element(l2, 'l3Networks.l3BasicNetwork'):
                l3networks.extend(xmlobject.safe_list(l2.l3Networks.l3BasicNetwork))

    if zone.duplication__ == None:
        duplication = 1
    else:
        duplication = int(zone.duplication__)

    for zone_duplication in range(duplication):
        for l3 in l3networks:
            if l3_name and l3_name != l3.name_:
                continue

            if not xmlobject.has_element(l3, 'ipRange'):
                continue

            if zone_duplication == 0:
                l3Name = l3.name_
            else:
                l3Name = generate_dup_name(l3.name_, zone_duplication, 'z')

            l3_invs = res_ops.get_resource(res_ops.L3_NETWORK, session_uuid, name = l3Name)
            l3_inv = get_first_item_from_list(l3_invs, 'L3 Network', l3Name, 'IP range')
            if ipversion == 4:
                do_add_ip_range(l3.ipRange, l3_inv.uuid, session_uuid, \
                        ip_range_name, ipversion = 4)
            else:
                if xmlobject.has_element(l3, 'ipRange'):
                    do_add_ip_range(l3.ipRange, l3_inv.uuid, session_uuid, \
                        ip_range_name, ipversion = 6)
                else:
                    do_add_ip_cidr(l3.ipv6Cidr, l3_inv.uuid, session_uuid, \
                        ip_cidr_name, ipversion = 6)

def do_add_ip_range(ip_range_xml_obj, l3_uuid, session_uuid, \
        ip_range_name = None, ipversion = 4):

    for ir in xmlobject.safe_list(ip_range_xml_obj):
        if ip_range_name and ip_range_name != ir.name_:
            continue

        if ipversion == 4:
            action = api_actions.AddIpRangeAction()
            action.sessionUuid = session_uuid
            action.description = ir.description__
            action.endIp = ir.endIp_
            action.gateway = ir.gateway_
            action.l3NetworkUuid = l3_uuid
            action.name = ir.name_
            action.netmask = ir.netmask_
            action.startIp = ir.startIp_
            try:
                evt = action.run()
            except Exception as e:
                exc_info.append(sys.exc_info())
                raise e
            test_util.test_logger(jsonobject.dumps(evt))
        else:
            action = api_actions.AddIpv6RangeAction()
            action.sessionUuid = session_uuid
            action.description = ir.description__
            action.endIp = ir.endIp_
            action.gateway = ir.gateway_
            action.l3NetworkUuid = l3_uuid
            action.name = ir.name_
            action.startIp = ir.startIp_
            action.addressMode = ir.addressMode__
            action.prefixLen = ir.prefixLen_
            try:
                evt = action.run()
            except Exception as e:
                exc_info.append(sys.exc_info())
                raise e
            test_util.test_logger(jsonobject.dumps(evt))

def do_add_ip_cidr(ip_cidr_xml_obj, l3_uuid, session_uuid, \
        ip_cidr_name = None, ipversion = 4):

    for ic in xmlobject.safe_list(ip_cidr_xml_obj):
        if ip_cidr_name and ip_cidr_name != ic.name_:
            continue

        if ipversion == 4:
            action = api_actions.AddIpRangeByNetworkCidrAction()
            action.sessionUuid = session_uuid
            action.description = ic.description__
            action.endIp = ir.endIp_
            action.gateway = ir.gateway_
            action.l3NetworkUuid = l3_uuid
            action.name = ir.name_
            action.netmask = ir.netmask_
            action.startIp = ir.startIp_
            try:
                evt = action.run()
            except Exception as e:
                exc_info.append(sys.exc_info())
                raise e
            test_util.test_logger(jsonobject.dumps(evt))
        else:
            action = api_actions.AddIpv6RangeByNetworkCidrAction()
            action.sessionUuid = session_uuid
            action.description = ic.description__
            action.l3NetworkUuid = l3_uuid
            action.name = ic.name_
            action.networkCidr = ic.ipv6Cidr__
            action.addressMode = ic.addressMode__
            try:
                evt = action.run()
            except Exception as e:
                exc_info.append(sys.exc_info())
                raise e
            test_util.test_logger(jsonobject.dumps(evt))

#Add Network Service
def add_network_service(deployConfig, session_uuid):
    if not xmlobject.has_element(deployConfig, "zones.zone"):
        return

    l3networks = []
    for zone in xmlobject.safe_list(deployConfig.zones.zone):
        l2networks = []

        if xmlobject.has_element(zone, 'l2Networks.l2NoVlanNetwork'):
            l2networks.extend(xmlobject.safe_list(zone.l2Networks.l2NoVlanNetwork))

        if xmlobject.has_element(zone, 'l2Networks.l2VlanNetwork'):
            l2networks.extend(xmlobject.safe_list(zone.l2Networks.l2VlanNetwork))

        for l2 in l2networks:
            if xmlobject.has_element(l2, 'l3Networks.l3BasicNetwork'):
                l3networks.extend(xmlobject.safe_list(l2.l3Networks.l3BasicNetwork))

    providers = {}
    action = api_actions.QueryNetworkServiceProviderAction()
    action.sessionUuid = session_uuid
    action.conditions = []
    try:
       reply = action.run()
    except Exception as e:
        exc_info.append(sys.exc_info())
        raise e
    for pinv in reply:
        providers[pinv.name] = pinv.uuid

    if zone.duplication__ == None:
        duplication = 1
    else:
        duplication = int(zone.duplication__)

    for zone_duplication in range(duplication):
        for l3 in l3networks:
            if not xmlobject.has_element(l3, 'networkService'):
                continue

            if zone_duplication == 0:
                l3_name = l3.name_
            else:
                l3_name = generate_dup_name(l3.name_, zone_duplication, 'z')

            l3_invs = res_ops.get_resource(res_ops.L3_NETWORK, session_uuid, name = l3_name)
            l3_inv = get_first_item_from_list(l3_invs, 'L3 Network', l3_name, 'Network Service')
            do_add_network_service(l3.networkService, l3_inv.uuid, \
                    providers, session_uuid)

def do_add_network_service(net_service_xml_obj, l3_uuid, providers, \
        session_uuid): 
    allservices = {}
    for ns in xmlobject.safe_list(net_service_xml_obj):
        puuid = providers.get(ns.provider_)
        if not puuid:
            raise test_util.TestError('cannot find network service provider[%s], it may not have been added' % ns.provider_)

        servs = []
        for nst in xmlobject.safe_list(ns.serviceType):
            servs.append(nst.text_)
        allservices[puuid] = servs

    action = api_actions.AttachNetworkServiceToL3NetworkAction()
    action.sessionUuid = session_uuid
    action.l3NetworkUuid = l3_uuid
    action.networkServices = allservices
    try:
        evt = action.run()
    except Exception as e:
        exc_info.append(sys.exc_info())
        raise e
    test_util.test_logger(jsonobject.dumps(evt))

#Add Image
def add_image(scenarioConfig, scenarioFile, deployConfig, session_uuid):
    def _add_image(action):
        increase_image_thread()
        try:
            evt = action.run()
            test_util.test_logger(jsonobject.dumps(evt))
        except:
            exc_info.append(sys.exc_info())
        finally:
            decrease_image_thread()

    if not xmlobject.has_element(deployConfig, 'images.image'):
        return

    for i in xmlobject.safe_list(deployConfig.images.image):
        if i.hasattr('label_') and i.label_ == 'lazyload':
            print "lazyload image: %s will be added in case" % (i.name_)
            continue
        for bsref in xmlobject.safe_list(i.backupStorageRef):
            bss = res_ops.get_resource(res_ops.BACKUP_STORAGE, session_uuid, name=bsref.text_)
            bs = get_first_item_from_list(bss, 'backup storage', bsref.text_, 'image')
            action = api_actions.AddImageAction()
            action.sessionUuid = session_uuid
            #TODO: account uuid will be removed later.
            action.accountUuid = inventory.INITIAL_SYSTEM_ADMIN_UUID
            action.backupStorageUuids = [bs.uuid]
            action.bits = i.bits__
            if not action.bits:
                action.bits = 64
            action.description = i.description__
            action.format = i.format_
            action.mediaType = i.mediaType_
            action.guestOsType = i.guestOsType__
            if not action.guestOsType:
                action.guestOsType = 'unknown'
            action.platform = i.platform__
            if not action.platform:
                action.platform = 'Linux'
            action.hypervisorType = i.hypervisorType__
            action.name = i.name_
            action.url = i.url_
            action.timeout = 3600000
            if i.hasattr('system_'):
                action.system = i.system__
            if i.hasattr('systemTags_'):
                action.systemTags = i.systemTags_.split(',')
            thread = threading.Thread(target = _add_image, args = (action, ))
            print 'before add image1: %s' % i.url_
            wait_for_image_thread_queue()
            print 'before add image2: %s' % i.url_
            thread.start()
            print 'add image: %s' % i.url_

    print 'all images add command are executed'
    wait_for_thread_done(True)
    print 'all images have been added'

#Add Disk Offering
def add_disk_offering(scenarioConfig, scenarioFile, deployConfig, session_uuid):
    def _add_disk_offering(disk_offering_xml_obj, session_uuid):
        action = api_actions.CreateDiskOfferingAction()
        action.sessionUuid = session_uuid
        action.name = disk_offering_xml_obj.name_
        action.description = disk_offering_xml_obj.description_
        action.diskSize = sizeunit.get_size(disk_offering_xml_obj.diskSize_)
        try:
            evt = action.run()
            test_util.test_logger(jsonobject.dumps(evt))
        except:
            exc_info.append(sys.exc_info())

    if not xmlobject.has_element(deployConfig, 'diskOfferings.diskOffering'):
        return

    for disk_offering_xml_obj in \
            xmlobject.safe_list(deployConfig.diskOfferings.diskOffering):
        thread = threading.Thread(target = _add_disk_offering, \
                args = (disk_offering_xml_obj, session_uuid))
        wait_for_thread_queue()
        thread.start()

    wait_for_thread_done()

#Add Instance Offering
def add_instance_offering(scenarioConfig, scenarioFile, deployConfig, session_uuid):
    def _add_io(instance_offering_xml_obj, session_uuid):
        action = api_actions.CreateInstanceOfferingAction()
        action.sessionUuid = session_uuid
        action.name = instance_offering_xml_obj.name_
        action.description = instance_offering_xml_obj.description__
        action.cpuNum = instance_offering_xml_obj.cpuNum_
        #action.cpuSpeed = instance_offering_xml_obj.cpuSpeed_
        if instance_offering_xml_obj.memorySize__:
            action.memorySize = sizeunit.get_size(instance_offering_xml_obj.memorySize_)
        elif instance_offering_xml_obj.memoryCapacity_:
            action.memorySize = sizeunit.get_size(instance_offering_xml_obj.memoryCapacity_)

        try:
            evt = action.run()
            test_util.test_logger(jsonobject.dumps(evt))
        except:
            exc_info.append(sys.exc_info())

    if not xmlobject.has_element(deployConfig, \
            'instanceOfferings.instanceOffering'):
        return

    for instance_offering_xml_obj in \
            xmlobject.safe_list(deployConfig.instanceOfferings.instanceOffering):
        thread = threading.Thread(target = _add_io, \
                args = (instance_offering_xml_obj, session_uuid, ))
        wait_for_thread_queue()
        thread.start()

    wait_for_thread_done()

def add_pxe_server(scenarioConfig, scenarioFile, deployConfig, session_uuid):
    def _add_pxe_server(pxe):
        action = api_actions.CreateBaremetalPxeServerAction()
        action.name = pxe.name_
        action.sessionUuid = session_uuid
        action.description = pxe.description__
        action.dhcpInterface = pxe.dhcpInterface_
        action.dhcpRangeBegin = pxe.dhcpRangeBegin_
        action.dhcpRangeEnd = pxe.dhcpRangeEnd_
        action.dhcpRangeNetmask = pxe.dhcpRangeNetmask_

        try:
            evt = action.run()
            test_util.test_logger(jsonobject.dumps(evt))
        except Exception as e:
            exc_info.append(sys.exc_info())

    if not xmlobject.has_element(deployConfig, 'pxe'):
        return
    pxe = deployConfig.pxe
    thread = threading.Thread(target=_add_pxe_server, args=(pxe,))
    wait_for_thread_queue()
    thread.start()
    wait_for_thread_done()

    #Add VM -- Pass

def add_vcenter(scenarioConfig, scenarioFile, deployConfig, session_uuid):
    def _add_vcenter(vcenter):
        action = api_actions.AddVCenterAction()
        action.name = vcenter.name_
        action.domainName = vcenter.domainName_
        action.username = vcenter.username_
        action.password = vcenter.password_
        action.sessionUuid = session_uuid
        zinvs = res_ops.get_resource(res_ops.ZONE, session_uuid, name=vcenter.zoneRef.text_)
        zinv = get_first_item_from_list(zinvs, 'zone', vcenter.zoneRef.text_, 'add vcenter')
        action.zoneUuid = zinv.uuid
    
        try:
            evt = action.run()
            test_util.test_logger(jsonobject.dumps(evt))
        except Exception as e:
            exc_info.append(sys.exc_info())
    
    if not xmlobject.has_element(deployConfig, 'vcenter'):
        return
    vcenter = deployConfig.vcenter
    thread = threading.Thread(target=_add_vcenter, args=(vcenter,))
    wait_for_thread_queue()
    thread.start()
    wait_for_thread_done()

def add_vcenter_image(scenarioConfig, scenarioFile, deployConfig, session_uuid):
    def _add_image(action):
        increase_image_thread()
        try:
            evt = action.run()
            test_util.test_logger(jsonobject.dumps(evt))
        except:
            exc_info.append(sys.exc_info())
        finally:
            decrease_image_thread()

    if not xmlobject.has_element(deployConfig, 'vcenter.images.image'):
        return

    for i in xmlobject.safe_list(deployConfig.vcenter.images.image):
        if i.hasattr('label_') and i.label_ == 'lazyload':
            print "lazyload image: %s will be added in case" % (i.name_)
            continue
        for bsref in xmlobject.safe_list(i.backupStorageRef):
            bss = res_ops.get_resource(res_ops.BACKUP_STORAGE, session_uuid, name=bsref.text_)
            bs = get_first_item_from_list(bss, 'backup storage', bsref.text_, 'image')
            action = api_actions.AddImageAction()
            action.sessionUuid = session_uuid
            #TODO: account uuid will be removed later.
            action.accountUuid = inventory.INITIAL_SYSTEM_ADMIN_UUID
            action.backupStorageUuids = [bs.uuid]
            action.bits = i.bits__
            if not action.bits:
                action.bits = 64
            action.description = i.description__
            action.format = i.format_
            action.mediaType = i.mediaType_
            action.guestOsType = i.guestOsType__
            if not action.guestOsType:
                action.guestOsType = 'unknown'
            action.platform = i.platform__
            if not action.platform:
                action.platform = 'Linux'
            action.hypervisorType = i.hypervisorType__
            action.name = i.name_
            action.url = i.url_
            action.timeout = 1800000
            if i.hasattr('system_'):
                action.system = i.system_
            if i.hasattr('systemTags_'):
                action.systemTags = i.systemTags_.split(',')
            thread = threading.Thread(target = _add_image, args = (action, ))
            print 'before add image1: %s' % i.url_
            wait_for_image_thread_queue()
            print 'before add image2: %s' % i.url_
            thread.start()
            print 'add image: %s' % i.url_

    print 'vcenter images add command are executed'
    wait_for_thread_done(True)
    print 'vcenter images have been added'

def add_vcenter_l2l3_network(scenarioConfig, scenarioFile, deployConfig, session_uuid):
    if not xmlobject.has_element(deployConfig, "vcenter.l2Networks"):
        return

    def attachL2ToCluster(l2_inv, session_uuid):
        test_util.test_logger(l2_inv)
        datacenter = xmlobject.safe_list(vcenter.datacenters.datacenter)[0]
        cluster_name = xmlobject.safe_list(datacenter.clusters.cluster)[0].name_
        conditions = res_ops.gen_query_conditions('name', '=', cluster_name)
        cluster = res_ops.query_resource(res_ops.CLUSTER, conditions)[0]

        action = api_actions.AttachL2NetworkToClusterAction()
        action.l2NetworkUuid = l2_inv.uuid
        action.clusterUuid = cluster.uuid
        action.sessionUuid = session_uuid
        try:
            evt = action.run()
            test_util.test_logger(jsonobject.dumps(evt))
        except:
            exc_info.append(sys.exc_info())

    def createL2Network(l2, session_uuid):
        # create l2Network
        zone = res_ops.query_resource(res_ops.ZONE)[0]
        action = api_actions.CreateL2NoVlanNetworkAction()
        action.name = l2.name_
        action.physicalInterface = l2.physicalInterface_
        action.zoneUuid = zone.uuid
        action.sessionUuid = session_uuid
        if hasattr(l2, 'vlan'):
            action.vlan = l2.vlan_
        evt = action.run()
        test_util.test_logger(jsonobject.dumps(evt))
        return evt.inventory


    vcenter = xmlobject.safe_list(deployConfig.vcenter)[0]
    if  xmlobject.has_element(vcenter, "l2Networks.l2NoVlanNetwork"):
        for l2 in  xmlobject.safe_list(vcenter.l2Networks.l2NoVlanNetwork):
            # create l2Network
            l2_inv = createL2Network(l2, session_uuid)

            # attach l2Network to cluster
            attachL2ToCluster(l2_inv, session_uuid)

            # create l3Network
            if not xmlobject.has_element(l2, "l3Networks.l3BasicNetwork"):
                continue
            add_vcenter_l3_network(l2, session_uuid)

    if  xmlobject.has_element(vcenter, "l2Networks.l2VlanNetwork"):
        for l2 in  xmlobject.safe_list(vcenter.l2Networks.l2VlanNetwork):
            # create l2Network
            l2_inv = createL2Network(l2, session_uuid)

            # attach l2Network to cluster
            attachL2ToCluster(l2_inv, session_uuid)

            # create l3Network
            if not xmlobject.has_element(l2, "l3Networks.l3BasicNetwork"):
                continue
            add_vcenter_l3_network(l2, session_uuid)     
def add_vcenter_l3_network(l2, session_uuid):
    for l3 in xmlobject.safe_list(l2.l3Networks.l3BasicNetwork):
        # create l3Network
        action = api_actions.CreateL3NetworkAction()
        action.sessionUuid = session_uuid
        action.name = l3.name_
        action.type = inventory.L3_BASIC_NETWORK_TYPE

        conditions = res_ops.gen_query_conditions('name', '=', l2.name_)
        l2_network = res_ops.query_resource(res_ops.L2_NETWORK, conditions)[0]
        action.l2NetworkUuid = l2_network.uuid

        if l3.domain_name__:
            action.dnsDomain = l3.domain_name__

        if l3.hasattr('category_'):
            action.category = l3.category_
        elif not l3.hasattr('system_') or l3.system_ == False:
            action.category = 'Private'

        if l3.hasattr('type_'):
            action.type = l3.type_

        try:
            evt = action.run()
            test_util.test_logger(jsonobject.dumps(evt))
        except:
            exc_info.append(sys.exc_info())

        #add dns
        l3_inv = evt.inventory
        if xmlobject.has_element(l3, 'dns'):
            for dns in xmlobject.safe_list(l3.dns):
                action = api_actions.AddDnsToL3NetworkAction()
                action.sessionUuid = session_uuid
                action.dns = dns.text_
                action.l3NetworkUuid = l3_inv.uuid
                try:
                    evt = action.run()
                    test_util.test_logger(jsonobject.dumps(evt))
                except:
                    exc_info.append(sys.exc_info())

        #add ip range.
        if xmlobject.has_element(l3, 'ipRange'):
            do_add_ip_range(l3.ipRange, l3_inv.uuid, session_uuid, ipversion = 4)
        #add network service.
        providers = {}
        action = api_actions.QueryNetworkServiceProviderAction()
        action.sessionUuid = session_uuid
        action.conditions = []
        try:
            reply = action.run()
        except:
            exc_info.append(sys.exc_info())
        for pinv in reply:
            providers[pinv.name] = pinv.uuid

        if xmlobject.has_element(l3, 'networkService'):
            do_add_network_service(l3.networkService, l3_inv.uuid, providers, session_uuid)

def add_vcenter_vrouter(scenarioConfig, scenarioFile, deployConfig, session_uuid):
    if not xmlobject.has_element(deployConfig, 'vcenter.virtualRouterOfferings'):
        return

    for i in xmlobject.safe_list(deployConfig.vcenter.virtualRouterOfferings.virtualRouterOffering):
        action = api_actions.CreateVirtualRouterOfferingAction()
        action.sessionUuid = session_uuid
        action.name = i.name__
        action.decription = i.description_
        action.cpuNum = i.cpuNum_

        if i.memorySize__:
            action.memorySize = sizeunit.get_size(i.memorySize_)
        elif i.memoryCapacity_:
            action.memorySize = sizeunit.get_size(i.memoryCapacity_)

        action.isDefault = i.isDefault__
        action.type = 'VirtualRouter'

        zinvs = res_ops.get_resource(res_ops.ZONE, session_uuid, name=i.zoneRef.text_)
        zinv = get_first_item_from_list(zinvs, 'zone', i.zoneRef.text_, 'virtual router offering')
        action.zoneUuid = zinv.uuid

        cond = res_ops.gen_query_conditions('zoneUuid', '=', zinv.uuid)
        cond1 = res_ops.gen_query_conditions('name', '=', i.managementL3NetworkRef.text_, cond)
        minvs = res_ops.query_resource(res_ops.L3_NETWORK, cond1, session_uuid)
        minv = get_first_item_from_list(minvs, 'Management L3 Network', i.managementL3NetworkRef.text_, 'virtualRouterOffering')
        action.managementNetworkUuid = minv.uuid

        cond2 = res_ops.gen_query_conditions('name', '=', i.publicL3NetworkRef.text_, cond)
        pinvs = res_ops.query_resource(res_ops.L3_NETWORK, cond2, session_uuid)
        pinv = get_first_item_from_list(pinvs, 'Public L3 Network', i.publicL3NetworkRef.text_, 'virtualRouterOffering')
        action.publicNetworkUuid = pinv.uuid

        iinvs = res_ops.get_resource(res_ops.IMAGE, session_uuid, name=i.imageRef.text_)
        iinv = get_first_item_from_list(iinvs, 'Image', i.imageRef.text_, 'virtualRouterOffering')
        action.imageUuid = iinv.uuid

        try:
            evt = action.run()
        except:
            exc_info.append(sys.exc_info())
        test_util.test_logger(jsonobject.dumps(evt))



def _thread_for_action(action, retry=False):
    try:
        evt = action.run()
        test_util.test_logger(jsonobject.dumps(evt))
    except:
        if retry:
            _thread_for_action(action)
        else:
            exc_info.append(sys.exc_info())

#Add Virtual Router Offering
def add_virtual_router(scenarioConfig, scenarioFile, deployConfig, session_uuid, l3_name = None, \
        zone_name = None):

    if xmlobject.has_element(deployConfig, 'backupStorages.miniBackupStorage'):
        return
    if not xmlobject.has_element(deployConfig, 'instanceOfferings.virtualRouterOffering'):
        return

    for i in xmlobject.safe_list(deployConfig.instanceOfferings.virtualRouterOffering):
        if l3_name and l3_name != i.managementL3NetworkRef.text_:
            continue 

        if zone_name and zone_name != i.zoneRef.text_:
            continue 

        print "continue l3_name: %s; zone_name: %s" % (l3_name, zone_name)
        action = api_actions.CreateVirtualRouterOfferingAction()
        action.sessionUuid = session_uuid
        action.name = i.name_
        action.description = i.description__
        action.cpuNum = i.cpuNum_
        #action.cpuSpeed = i.cpuSpeed_
        if i.memorySize__:
            action.memorySize = sizeunit.get_size(i.memorySize_)
        elif i.memoryCapacity_:
            action.memorySize = sizeunit.get_size(i.memoryCapacity_)

        action.isDefault = i.isDefault__
        action.type = 'VirtualRouter'

        zinvs = res_ops.get_resource(res_ops.ZONE, session_uuid, name=i.zoneRef.text_)
        zinv = get_first_item_from_list(zinvs, 'zone', i.zoneRef.text_, 'virtual router offering')
        action.zoneUuid = zinv.uuid
        cond = res_ops.gen_query_conditions('zoneUuid', '=', zinv.uuid)
        cond1 = res_ops.gen_query_conditions('name', '=', \
                i.managementL3NetworkRef.text_, cond)
        minvs = res_ops.query_resource(res_ops.L3_NETWORK, cond1, \
                session_uuid)

        minv = get_first_item_from_list(minvs, 'Management L3 Network', i.managementL3NetworkRef.text_, 'virtualRouterOffering')

        action.managementNetworkUuid = minv.uuid
        if xmlobject.has_element(i, 'publicL3NetworkRef'):
            cond1 = res_ops.gen_query_conditions('name', '=', \
                    i.publicL3NetworkRef.text_, cond)
            pinvs = res_ops.query_resource(res_ops.L3_NETWORK, cond1, \
                    session_uuid)
            pinv = get_first_item_from_list(pinvs, 'Public L3 Network', i.publicL3NetworkRef.text_, 'virtualRouterOffering')

            action.publicNetworkUuid = pinv.uuid

        iinvs = res_ops.get_resource(res_ops.IMAGE, session_uuid, \
                name=i.imageRef.text_)
        iinv = get_first_item_from_list(iinvs, 'Image', i.imageRef.text_, 'virtualRouterOffering')

        action.imageUuid = iinv.uuid

        thread = threading.Thread(target = _thread_for_action, args = (action, ))
        wait_for_thread_queue()
        thread.start()

    wait_for_thread_done()

    for i in xmlobject.safe_list(deployConfig.instanceOfferings.virtualRouterOffering):
        if xmlobject.has_element(i, 'l3BasicNetwork'):
            for l3net in xmlobject.safe_list(i.l3BasicNetwork):
                action = api_actions.CreateSystemTagAction()
                action.sessionUuid = session_uuid
                action.timeout = 30000
                action.resourceType = 'InstanceOfferingVO'

                cond = res_ops.gen_query_conditions('type','=','VirtualRouter')
                vr_instance_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING,cond)[0].uuid
                action.resourceUuid = vr_instance_uuid

                zinvs = res_ops.get_resource(res_ops.ZONE, session_uuid, name=i.zoneRef.text_)
                zinv = get_first_item_from_list(zinvs, 'zone', i.zoneRef.text_, 'virtual router offering')
                cond = res_ops.gen_query_conditions('zoneUuid', '=', zinv.uuid)
                cond1 = res_ops.gen_query_conditions('name', '=', l3net.text_, cond)
                l3_network = res_ops.query_resource(res_ops.L3_NETWORK, cond1, session_uuid)
                action.tag = 'guestL3Network::' + l3_network[0].uuid

                thread = threading.Thread(target = _thread_for_action, args = (action, ))
                wait_for_thread_queue()
                thread.start()

    wait_for_thread_done()

def json_post(uri, body=None, headers={}, method='POST', fail_soon=False):
    ret = []
    def post(_):
        try:
            pool = urllib3.PoolManager(timeout=120.0, retries=urllib3.util.retry.Retry(15))
            header = {'Content-Type': 'application/json', 'Connection': 'close'}
            for k in headers.keys():
                header[k] = headers[k]

            if body is not None:
                assert isinstance(body, types.StringType)
                header['Content-Length'] = str(len(body))
                content = pool.urlopen(method, uri, headers=header, body=str(body)).data
            else:
                header['Content-Length'] = '0'
                content = pool.urlopen(method, uri, headers=header).data

            pool.clear()
            ret.append(content)
            return True
        except Exception as e:
            if fail_soon:
                raise e
            return False

    post(None)
    return ret[0]

#Add Backup Storage
def add_simulator_backup_storage(scenarioConfig, scenarioFile, deployConfig):
    resources = []
    if xmlobject.has_element(deployConfig, 'backupStorages.sftpBackupStorage'):
        for bs in xmlobject.safe_list(deployConfig.backupStorages.sftpBackupStorage):
            data = {}
            data['type'] = 'SftpBackupStorage'
            data['data'] = {}
            data['data']['ip'] = bs.hostname_
            data['data']['path'] = bs.url_
            data['data']['id'] = bs.name_
	    if hasattr(bs, 'totalCapacity_') and bs.totalCapacity_ != "":
               	data['data']['totalCapacity'] = bs.totalCapacity_
	    if hasattr(bs, 'availableCapacity_') and bs.availableCapacity_ != "":
               	data['data']['availableCapacity'] = bs.availableCapacity_
            resources.append(data)

    if xmlobject.has_element(deployConfig, 'backupStorages.imageStoreBackupStorage'):
        for bs in xmlobject.safe_list(deployConfig.backupStorages.imageStoreBackupStorage):
            data = {}
            data['type'] = 'ImageStoreBackupStorage'
            data['data'] = {}
            data['data']['ip'] = bs.hostname_
            data['data']['path'] = bs.url_
            data['data']['id'] = bs.name_
            resources.append(data)

    if xmlobject.has_element(deployConfig, 'backupStorages.cephBackupStorage'):
        for bs in xmlobject.safe_list(deployConfig.backupStorages.cephBackupStorage):
            data = {}
            data['type'] = 'CephBackupStorage'
            data['data'] = {}
            data['data']['fsid'] = "445ce4c1-bab0-449e-a684-a3fe80be844d"
            data['data']['id'] = bs.name_
	    if hasattr(bs, 'totalCapacity_') and bs.totalCapacity_ != "":
               	data['data']['totalCapacity'] = bs.totalCapacity_
	    if hasattr(bs, 'availableCapacity_') and bs.availableCapacity_ != "":
               	data['data']['availableCapacity'] = bs.availableCapacity_
            resources.append(data)
            for mon_url in bs.monUrls_.split(';'):
                mon_data = {}
                mon_data['type'] = 'CephBackupStorageMon'
                mon_data['data'] = {}
                mon_data['data']['ip'] = mon_url.split('@')[1]
                mon_data['data']['monAddr'] = mon_url.split('@')[1]
                mon_data['data']['id'] = mon_data['data']['ip']
                mon_data['data']['cephId'] = bs.name_
                resources.append(mon_data)

    mn_ip = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].hostName
    url = "http://%s:8080/zstack/simulators/batch-create" % (mn_ip)
    ret = json_post(url, simplejson.dumps({"resources": resources}))

#Add Primary Storage
def add_simulator_primary_storage(scenarioConfig, scenarioFile, deployConfig):
    if not xmlobject.has_element(deployConfig, 'zones.zone'):
        test_util.test_logger('Not find zones.zone in config, skip primary storage deployment')
        return

    resources = []
    for zone in xmlobject.safe_list(deployConfig.zones.zone):
        if xmlobject.has_element(zone, 'primaryStorages.localPrimaryStorage'):
            for pr in xmlobject.safe_list(zone.primaryStorages.localPrimaryStorage):
                data = {}
                data['type'] = 'LocalStorage'
                data['data'] = {}
                data['data']['path'] = pr.url_
                data['data']['id'] = pr.name_
                data['data']['name'] = pr.name_
	        if hasattr(pr, 'totalCapacity_') and pr.totalCapacity_ != "":
                    data['data']['totalCapacity'] = pr.totalCapacity_
	        if hasattr(pr, 'availableCapacity_') and pr.availableCapacity_ != "":
                    data['data']['availableCapacity'] = pr.availableCapacity_
                resources.append(data)
    
        if xmlobject.has_element(zone, 'primaryStorages.cephPrimaryStorage'):
            for pr in xmlobject.safe_list(zone.primaryStorages.cephPrimaryStorage):
                data = {}
                data['type'] = 'CephPrimaryStorage'
                data['data'] = {}
                data['data']['fsid'] = "445ce4c1-bab0-449e-a684-a3fe80be844d"
                data['data']['id'] = pr.name_
	        if hasattr(pr, 'totalCapacity_') and pr.totalCapacity_ != "":
                    data['data']['totalCapacity'] = pr.totalCapacity_
	        if hasattr(pr, 'availableCapacity_') and pr.availableCapacity_ != "":
                    data['data']['availableCapacity'] = pr.availableCapacity_
                resources.append(data)
                for mon_url in pr.monUrls_.split(';'):
                    mon_data = {}
                    mon_data['type'] = 'CephPrimaryStorageMon'
                    mon_data['data'] = {}
                    mon_data['data']['ip'] = mon_url.split('@')[1]
                    mon_data['data']['monAddr'] = mon_url.split('@')[1]
                    mon_data['data']['id'] = mon_data['data']['ip']
                    mon_data['data']['cephId'] = pr.name_
                    resources.append(mon_data)
    
                if hasattr(pr, 'dataVolumePoolName_') and pr.dataVolumePoolName_ != "":
                    pool_data = {}
                    pool_data['type'] = 'CephBackupStoragePool'
                    pool_data['data'] = {}
                    pool_data['data']['cephId'] = pr.dataVolumePoolName_
                    pool_data['data']['name'] = pr.dataVolumePoolName_
                    pool_data['data']['id'] = pr.dataVolumePoolName_
                    resources.append(pool_data)
                if hasattr(pr, 'rootVolumePoolName_') and pr.rootVolumePoolName_ != "":
                    pool_data = {}
                    pool_data['type'] = 'CephBackupStoragePool'
                    pool_data['data'] = {}
                    pool_data['data']['cephId'] = pr.dataVolumePoolName_
                    pool_data['data']['name'] = pr.dataVolumePoolName_
                    pool_data['data']['id'] = pr.dataVolumePoolName_
                    resources.append(pool_data)
                if hasattr(pr, 'imageCachePoolName_') and pr.imageCachePoolName_ != "":
                    pool_data = {}
                    pool_data['type'] = 'CephBackupStoragePool'
                    pool_data['data'] = {}
                    pool_data['data']['cephId'] = pr.dataVolumePoolName_
                    pool_data['data']['name'] = pr.dataVolumePoolName_
                    pool_data['data']['id'] = pr.dataVolumePoolName_
                    resources.append(pool_data)

        if xmlobject.has_element(zone, 'primaryStorages.nfsPrimaryStorage'):
            for pr in xmlobject.safe_list(zone.primaryStorages.nfsPrimaryStorage):
                data = {}
                data['type'] = 'NfsPrimaryStorage'
                data['data'] = {}
                data['data']['id'] = pr.name_
                data['data']['ip'] = pr.url_.split(':')[0]
                data['data']['mountPoint'] = pr.url_.split(':')[1]
	        if hasattr(pr, 'totalCapacity_') and pr.totalCapacity_ != "":
                    data['data']['totalCapacity'] = bs.totalCapacity_
	        if hasattr(pr, 'availableCapacity_') and pr.availableCapacity_ != "":
                    data['data']['availableCapacity'] = pr.availableCapacity_
                resources.append(data)
    
        if xmlobject.has_element(zone, 'primaryStorages.sharedMountPointPrimaryStorage'):
            for pr in xmlobject.safe_list(zone.primaryStorages.sharedMountPointPrimaryStorage):
                data = {}
                data['type'] = 'SharedMountPointPrimaryStorage'
                data['data'] = {}
                data['data']['path'] = pr.url_
                data['data']['id'] = pr.name_
	        if hasattr(pr, 'totalCapacity_') and pr.totalCapacity_ != "":
                    data['data']['totalCapacity'] = pr.totalCapacity_
	        if hasattr(pr, 'availableCapacity_') and pr.availableCapacity_ != "":
                    data['data']['availableCapacity'] = pr.availableCapacity_
                resources.append(data)
    mn_ip = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].hostName
    url = "http://%s:8080/zstack/simulators/batch-create" % (mn_ip)
    ret = json_post(url, simplejson.dumps({"resources": resources}))

#Add Host
def add_simulator_host(scenarioConfig, scenarioFile, deployConfig):
    if not xmlobject.has_element(deployConfig, 'zones.zone'):
        test_util.test_logger('Not find zones.zone in config, skip primary storage deployment')
        return

    resources = []
    for zone in xmlobject.safe_list(deployConfig.zones.zone):
        if not xmlobject.has_element(zone, 'clusters.cluster'):
            continue

        if zone.duplication__ == None:
            zone_duplication = 1
        else:
            zone_duplication = int(zone.duplication__)


        for zone_ref in range(zone_duplication):
            for cluster in xmlobject.safe_list(zone.clusters.cluster):
                if cluster.duplication__ == None:
                    cluster_duplication = 1
                else:
                    cluster_duplication = int(cluster.duplication__)

                for cluster_ref in range(cluster_duplication):
                    for host in xmlobject.safe_list(cluster.hosts.host):
                        if host.duplication__ == None:
                            host_duplication = 1
                        else:
                            host_duplication = int(host.duplication__)
            
                        for host_ref in range(host_duplication):
                            data = {}
                            data['type'] = 'KvmHost'
                            data['data'] = {}
                            if zone_duplication == 0 and cluster_duplication == 0 and host_duplication == 0:
                                data['data']['ip'] = host.managementIp_
                                data['data']['id'] = host.name_
                            else:
                                data['data']['ip'] = generate_dup_host_ip(host.managementIp_, zone_ref, cluster_ref, host_ref)
                                data['data']['id'] = generate_dup_name(generate_dup_name(generate_dup_name(host.name_, zone_ref, 'z'), cluster_ref, 'c'), host_ref, 'h')
                            data['data']['username'] = host.username_
                            data['data']['password'] = host.password__
                            if hasattr(host, 'cpuNum_') and host.cpuNum_ != "":
                                data['data']['cpuNum'] = host.cpuNum_
                            if hasattr(host, 'totalCpu_') and host.totalCpu_ != "":
                                data['data']['totalCpu'] = host.totalCpu_
                            if hasattr(host, 'cpuSockets_') and host.cpuSockets_ != "":
                                data['data']['cpuSockets'] = host.cpuSockets_
                            if hasattr(host, 'usedCpu_') and host.usedCpu_ != "":
                                data['data']['usedCpu'] = host.usedCpu_
                            if hasattr(host, 'totalMemory_') and host.totalMemory_ != "":
                                data['data']['totalMemory'] = host.totalMemory_
                            if hasattr(host, 'usedMemory_') and host.usedMemory_ != "":
                                data['data']['usedMemory'] = host.usedMemory_
                            resources.append(data)
    mn_ip = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].hostName
    url = "http://%s:8080/zstack/simulators/batch-create" % (mn_ip)
    ret = json_post(url, simplejson.dumps({"resources": resources}))

def deploy_simulator_database(deploy_config, scenario_config = None, scenario_file = None):
    operations = [
            add_simulator_backup_storage,
            add_simulator_primary_storage,
            add_simulator_host
            ]
    for operation in operations:
        try:
            operation(scenario_config, scenario_file, deploy_config)
        except Exception as e:
            test_util.test_logger('[Error] zstack simluator deployment meets exception when doing: %s . The real exception are:.' % operation.__name__)
            print('----------------------Exception Reason------------------------')
            traceback.print_exc(file=sys.stdout)
            print('-------------------------Reason End---------------------------\n')
            raise e

    test_util.test_logger('[Done] zstack simulator database was created successfully.')

def deploy_simulator_agent_script(url_path, script):
    data = dict()
    data['urlPath'] = url_path
    data['script'] = script
    mn_ip = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].hostName
    url = "http://%s:8080/zstack/simulators/agent-pre-handlers/add" % (mn_ip)
    ret = json_post(url, simplejson.dumps(data))

def remove_simulator_agent_script(url_path):
    mn_ip = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].hostName
    url = "http://%s:8080/zstack/simulators/agent-pre-handlers/remove" % (mn_ip)
    ret = json_post(url, url_path)

def deploy_initial_database(deploy_config, scenario_config = None, scenario_file = None, ipversion = 4):
    operations = [
            add_zone,
            add_l2_network,
            add_primary_storage,
            add_iscsi_server,
            add_cluster,
            add_host,
            add_backup_storage,
            attach_bs_to_zone,
            add_sanlock,
            add_l3_network,
            add_image,
            add_disk_offering,
            add_instance_offering,
            add_virtual_router,
            #add_pxe_server,
            add_vcenter,
            add_vcenter_image,
	    add_vcenter_l2l3_network,
            add_vcenter_vrouter
            ]
    for operation in operations:
        session_uuid = account_operations.login_as_admin()
        try:
            if ipversion == 6 and operation == "add_l3_network":
                operation(scenario_config, scenario_file, deploy_config, session_uuid, ipversion = 6)
            else:
                operation(scenario_config, scenario_file, deploy_config, session_uuid)
        except Exception as e:
            test_util.test_logger('[Error] zstack deployment meets exception when doing: %s . The real exception are:.' % operation.__name__)
            print('----------------------Exception Reason------------------------')
            traceback.print_exc(file=sys.stdout)
            print('-------------------------Reason End---------------------------\n')
            raise e
        finally:
            account_operations.logout(session_uuid)

    test_util.test_logger('[Done] zstack initial database was created successfully.')

def generate_dup_name(origin_name, num, prefix=None):
    if num == 0:
        return origin_name

    if prefix:
        return str(origin_name) + '-' + str(prefix) + str(num)
    else:
        return str(origin_name) + '-' + str(num)

def generate_dup_host_ip(origin_ip, zone_ref, cluster_ref, host_ref):
    ip_fields = origin_ip.split('.')
    ip_fields[1] = str(int(ip_fields[1]) + zone_ref)
    ip_fields[2] = str(int(ip_fields[2]) + cluster_ref)
    ip_fields[3] = str(int(ip_fields[3]) + host_ref)
    return '.'.join(ip_fields)

image_thread_queue = 0

@lock.lock('image_thread')
def increase_image_thread():
    global image_thread_queue
    image_thread_queue += 1

@lock.lock('image_thread')
def decrease_image_thread():
    global image_thread_queue
    image_thread_queue -= 1

def wait_for_image_thread_queue():
    while image_thread_queue >= IMAGE_THREAD_LIMIT:
        time.sleep(1)
        print 'image_thread_queue: %d' % image_thread_queue

def wait_for_thread_queue():
    while threading.active_count() > DEPLOY_THREAD_LIMIT:
        check_thread_exception()
        time.sleep(1)

def cleanup_exc_info():
    exc_info = []

def check_thread_exception():
    if exc_info:
        info1 = exc_info[0][1]
        info2 = exc_info[0][2]
        cleanup_exc_info()
        raise info1, None, info2

def wait_for_thread_done(report = False):
    while threading.active_count() > 1:
        check_thread_exception()
        time.sleep(1)
        if report:
            print 'thread count: %d' % threading.active_count()
    check_thread_exception()

def get_nfs_ip_for_seperate_network(scenarioConfig, virtual_host_ip, nfs_ps_name):
    import scenario_operations as sce_ops
    zstack_management_ip = scenarioConfig.basicConfig.zstackManagementIp.text_

    storageNetworkUuid = None
    for host in xmlobject.safe_list(scenarioConfig.deployerConfig.hosts.host):
        for vm in xmlobject.safe_list(host.vms.vm):
            for l3Network in xmlobject.safe_list(vm.l3Networks.l3Network):
                if xmlobject.has_element(l3Network, 'primaryStorageRef') and l3Network.primaryStorageRef.text_ == nfs_ps_name:
                    storageNetworkUuid = l3Network.uuid_
                    cond = res_ops.gen_query_conditions('vmNics.ip', '=', virtual_host_ip)
                    vm_inv_nics = sce_ops.query_resource(zstack_management_ip, res_ops.VM_INSTANCE, cond).inventories[0].vmNics
                    if len(vm_inv_nics) < 2:
                        test_util.test_fail("virtual host:%s not has 2+ nics as expected, incorrect for seperate network case" %(virtual_host_ip))
                    for vm_inv_nic in vm_inv_nics:
                        if vm_inv_nic.l3NetworkUuid == storageNetworkUuid:
                            return vm_inv_nic.ip

    return None

def create_datacenter(dcname=None, service_instance=None, folder=None):
    from pyVmomi import vim
    if folder is None:
        folder = service_instance.content.rootFolder

    if folder is not None and isinstance(folder, vim.Folder):
        dc_moref = folder.CreateDatacenter(name=dcname)
        return dc_moref

def create_cluster(datacenter=None, clustername=None, cluster_spec=None):
    from pyVmomi import vim
    if datacenter is None:
        test_util.test_fail("Miss datacenter for cluster")
    if clustername is None:
        clustername = "cluster1"
    if cluster_spec is None:
        cluster_spec = vim.cluster.ConfigSpecEx()
    host_folder = datacenter.hostFolder
    cluster = host_folder.CreateClusterEx(name=clustername, spec=cluster_spec)
    return cluster

def add_vc_host(cluster=None, host_spec=None, asConnected=True):
    from pyVim import task
    if cluster is None:
        test_util.test_fail("Miss cluster for host")
    if host_spec is None:
        test_util.test_fail("Miss host_spec for host")
    TASK = cluster.AddHost_Task(spec=host_spec, asConnected=True)
    task.WaitForTask(TASK)
    host_inf = TASK.info.result
    return host_inf

def setup_iscsi_device(host=None, target_ip=None):
    from pyVmomi import vim
    #iscsi device name -> hba.device
    def get_iscsi_device(host=None):
        hba_list = host.config.storageDevice.hostBusAdapter
        for hba in hba_list:
            if hba.model == "iSCSI Software Adapter":
                return hba

    #TODO: now iscsi adapter shares the vnic with management network,
    # we need to add a seperate storage network for this
    # vnic device name -> vnic.device
    def get_iscsi_candidate_vnic(host=None):
        iscsi_hba = get_iscsi_device(host=host).device
        available_vnic = host.configManager.iscsiManager.QueryCandidateNics(iScsiHbaName=iscsi_hba)
        for vnic in available_vnic:
            if vnic.vnic.portgroup == "Management Network":
                return vnic.vnic

    def bind_vnic_to_iscsi(iScsiHbaName=None, vnicDevice=None):
        host.configManager.iscsiManager.BindVnic(iScsiHbaName=iScsiHbaName, vnicDevice=vnicDevice)

    #targets is target object list
    def add_iscsi_send_target(iScsiHbaName=None, target_ip=None):
        targets = []
        target = vim.host.InternetScsiHba.SendTarget()
        target.address = target_ip
        targets.append(target)
        host.configManager.storageSystem.AddInternetScsiSendTargets(iScsiHbaDevice=iScsiHbaName, targets=targets)

    def rescan_allhba():
        host.configManager.storageSystem.RescanAllHba()
        host.configManager.storageSystem.RescanVmfs()

    host_obj = host
    host_obj.configManager.storageSystem.UpdateSoftwareInternetScsiEnabled(enabled=True)
    candidate_vnic_device = get_iscsi_candidate_vnic(host=host_obj).device
    iscsihba_name = get_iscsi_device(host=host_obj).device
    bind_vnic_to_iscsi(iScsiHbaName=iscsihba_name, vnicDevice=candidate_vnic_device)
    rescan_allhba()
    add_iscsi_send_target(iScsiHbaName=iscsihba_name, target_ip=target_ip)
    rescan_allhba()

def create_datastore(host=None, dsname=None):
    #TODO: support iscsi disk for now
    #device_path -> disk.devicePath
    #display_name -> disk.displayName
    def available_disk_vmfs(host=host):
        disk_list = host.configManager.datastoreSystem.QueryAvailableDisksForVmfs()
        for disk in disk_list:
            if "iSCSI" in disk.displayName:
                return disk
            else:
                continue

    def query_datastore_create_option(host=None):
        device_path = available_disk_vmfs(host=host).devicePath
        create_option = host.configManager.datastoreSystem.QueryVmfsDatastoreCreateOptions(device_path)[0]
        return create_option

    vmfs_create_spec = query_datastore_create_option(host=host).spec
    vmfs_create_spec.vmfs.volumeName = dsname
    datastore = host.configManager.datastoreSystem.CreateVmfsDatastore(vmfs_create_spec)
    return datastore

def create_nfs_datastore(host=None, remotehost=None, mount_point_path=None, ds_name=None):
    from pyVmomi import vim
    spec = vim.host.NasVolume.Specification()
    spec.accessMode="readWrite"
    spec.securityType = 'AUTH_SYS'
    spec.remoteHost = remotehost
    spec.remotePath = mount_point_path
    spec.remoteHostNames = remotehost
    spec.localPath = ds_name
    host.configManager.datastoreSystem.CreateNasDatastore(spec=spec)

#To get the vswitch list from the host
#vswitch_obj = host.config.network.vswitch
def addvswitch_portgroup(host=None, vswitch="vSwitch0", portgroup=None, vlanId=0):
    from pyVmomi import vim
    portgroup_spec = vim.host.PortGroup.Specification()
    portgroup_spec.vswitchName = vswitch
    portgroup_spec.name = portgroup
    portgroup_spec.vlanId = int(vlanId)
    network_policy = vim.host.NetworkPolicy()
    network_policy.security = vim.host.NetworkPolicy.SecurityPolicy()
    network_policy.security.allowPromiscuous = True
    network_policy.security.macChanges = False
    network_policy.security.forgedTransmits = False
    portgroup_spec.policy = network_policy

    host.configManager.networkSystem.AddPortGroup(portgroup_spec)

def cleanup_datacenter(datacenter=None):
    from pyVim import task
    TASK = datacenter.Destroy_Task()
    task.WaitForTask(TASK)

def create_dvswitch(datacenter=None, name='DvSwitch0', DVSCreateSpec=None):
    from pyVmomi import vim
    from pyVim import task
    if not DVSCreateSpec:
        DVSCreateSpec = vim.DistributedVirtualSwitch.CreateSpec(
            configSpec=vim.DistributedVirtualSwitch.ConfigSpec(name=name)
        )
    folder = datacenter.networkFolder
    Task = folder.CreateDVS_Task(spec=DVSCreateSpec)
    task.WaitForTask(Task)
    return Task.info.result


def adddvswitch_portgroup(DVSwitch=None, name='DPortGroup0', vlanId=0):
    from pyVmomi import vim
    from pyVim import task
    vlan = vim.dvs.VmwareDistributedVirtualSwitch.VlanIdSpec()
    vlan.vlanId = int(vlanId)
    defaultPortConfig = vim.dvs.VmwareDistributedVirtualSwitch.VmwarePortConfigPolicy()
    defaultPortConfig.vlan = vlan

    DVPortgroupConfigSpec = vim.dvs.DistributedVirtualPortgroup.ConfigSpec()
    DVPortgroupConfigSpec.name = name
    DVPortgroupConfigSpec.type = 'ephemeral'
    DVPortgroupConfigSpec.autoExpand = False
    DVPortgroupConfigSpec.defaultPortConfig = defaultPortConfig

    Task = DVSwitch.CreateDVPortgroup_Task(spec=DVPortgroupConfigSpec)
    task.WaitForTask(Task)
    return Task.info.result

def clone_vm_from_vm(datacenter=None, name='vm-0', power=True):
    from pyVmomi import vim
    from pyVim import task
    resource_pool = get_obj(content, [vim.ResourcePool])[0]
    vm_template = get_obj(content, [vim.VirtualMachine])[0]

    relospec = vim.vm.RelocateSpec()
    relospec.datastore = get_obj(content, [vim.Datastore])[0]
    relospec.pool = resource_pool

    relospec = vim.vm.RelocateSpec()
    clonespec = vim.vm.CloneSpec()
    clonespec.location = relospec
    clonespec.powerOn = power

    Task = vm_template.Clone(folder=datacenter.vmFolder, name=name, spec=clonespec)
    task.WaitForTask(Task)


def powerOn_vm(vm):
    from pyVim import task
    Task = vm.PowerOnVM_Task()
    task.WaitForTask(Task)

class OvfHandler(object):
    """
    OvfHandler handles most of the OVA operations.
    It processes the tarfile, matches disk keys to files and
    uploads the disks, while keeping the progress up to date for the lease.
    """

    def __init__(self, ovafile):
        """
        Performs necessary initialization, opening the OVA file,
        processing the files and reading the embedded ovf file.
        """
        import tarfile
        self.handle = self._create_file_handle(ovafile)
        self.tarfile = tarfile.open(fileobj=self.handle)
        ovffilename = list(filter(lambda x: x.endswith(".ovf"),
                                  self.tarfile.getnames()))[0]
        ovffile = self.tarfile.extractfile(ovffilename)
        self.descriptor = ovffile.read().decode()

    def _create_file_handle(self, entry):
        """
        A simple mechanism to pick whether the file is local or not.
        This is not very robust.
        """
        return WebHandle(entry)

    def get_descriptor(self):
        return self.descriptor

    def set_spec(self, spec):
        """
        The import spec is needed for later matching disks keys with
        file names.
        """
        self.spec = spec

    def get_disk(self, fileItem, lease):
        """
        Does translation for disk key to file name, returning a file handle.
        """
        ovffilename = list(filter(lambda x: x == fileItem.path,
                                  self.tarfile.getnames()))[0]
        return self.tarfile.extractfile(ovffilename)

    def get_device_url(self, fileItem, lease):
        for deviceUrl in lease.info.deviceUrl:
            if deviceUrl.importKey == fileItem.deviceId:
                return deviceUrl
        raise Exception("Failed to find deviceUrl for file %s" % fileItem.path)

    def upload_disks(self, lease, host):
        """
        Uploads all the disks, with a progress keep-alive.
        """
        from pyVmomi import vim, vmodl
        self.lease = lease
        try:
            self.start_timer()
            for fileItem in self.spec.fileItem:
                self.upload_disk(fileItem, lease, host)
            lease.Complete()
        except vmodl.MethodFault as e:
            lease.Abort(e)
        except Exception as e:
            lease.Abort(vmodl.fault.SystemError(reason=str(e)))
            raise

    def upload_disk(self, fileItem, lease, host):
        """
        Upload an individual disk. Passes the file handle of the
        disk directly to the urlopen request.
        """
        import ssl
        from six.moves.urllib.request import Request, urlopen
        ovffile = self.get_disk(fileItem, lease)
        if ovffile is None:
            return
        deviceUrl = self.get_device_url(fileItem, lease)
        url = deviceUrl.url.replace('*', host)
        headers = {'Content-length': get_tarfile_size(ovffile)}
        if hasattr(ssl, '_create_unverified_context'):
            sslContext = ssl._create_unverified_context()
        else:
            sslContext = None
        req = Request(url, ovffile, headers)
        urlopen(req, context=sslContext)

    def start_timer(self):
        from threading import Timer
        """
        A simple way to keep updating progress while the disks are transferred.
        """
        Timer(5, self.timer).start()

    def timer(self):
        """
        Update the progress and reschedule the timer if not complete.
        """
        from pyVmomi import vim
        try:
            prog = self.handle.progress()
            self.lease.Progress(prog)
            if self.lease.state not in [vim.HttpNfcLease.State.done,
                                        vim.HttpNfcLease.State.error]:
                self.start_timer()
            sys.stderr.write("Progress: %d%%\r" % prog)
        except:  # Any exception means we should stop updating progress.
            pass


class WebHandle(object):
    def __init__(self, url):
        from six.moves.urllib.request import Request, urlopen
        self.url = url
        r = urlopen(url)
        if r.code != 200:
            raise Exception('not found url')
        self.headers = self._headers_to_dict(r)
        if 'accept-ranges' not in self.headers:
            raise Exception("Site does not accept ranges")
        self.st_size = int(self.headers['content-length'])
        self.offset = 0

    def _headers_to_dict(self, r):
        result = {}
        if hasattr(r, 'getheaders'):
            for n, v in r.getheaders():
                result[n.lower()] = v.strip()
        else:
            for line in r.info().headers:
                if line.find(':') != -1:
                    n, v = line.split(': ', 1)
                    result[n.lower()] = v.strip()
        return result

    def tell(self):
        return self.offset

    def seek(self, offset, whence=0):
        if whence == 0:
            self.offset = offset
        elif whence == 1:
            self.offset += offset
        elif whence == 2:
            self.offset = self.st_size - offset
        return self.offset

    def seekable(self):
        return True

    def read(self, amount):
	from six.moves.urllib.request import Request, urlopen
        start = self.offset
        end = self.offset + amount - 1
        req = Request(self.url,
                      headers={'Range': 'bytes=%d-%d' % (start, end)})
        r = urlopen(req)
        self.offset += amount
        result = r.read(amount)
        r.close()
        return result

    # A slightly more accurate percentage
    def progress(self):
        return int(100.0 * self.offset / self.st_size)


def get_tarfile_size(tarfile):
    """
    Determine the size of a file inside the tarball.
    If the object has a size attribute, use that. Otherwise seek to the end
    and report that.
    """
    if hasattr(tarfile, 'size'):
        return tarfile.size
    size = tarfile.seek(0, 2)
    tarfile.seek(0, 0)
    return size


def deploy_ova(service_instance=None, datacenter=None, datastore=None, resourcepool=None, path=None):
    from pyVmomi import vim
    from pyVim import task
    ovf_handle = OvfHandler(path)
    ovfManager = service_instance.content.ovfManager

    cisp = vim.OvfManager.CreateImportSpecParams()
    cisr = ovfManager.CreateImportSpec(ovf_handle.get_descriptor(),
                                       resourcepool, datastore, cisp)

    if len(cisr.error):
        for error in cisr.error:
            test_util.test_logger("%s" % error)
        test_util.test_logger("some errors prevent import of this OVA")
    ovf_handle.set_spec(cisr)

    lease = resourcepool.ImportVApp(cisr.importSpec, datacenter.vmFolder)
    while lease.state == vim.HttpNfcLease.State.initializing:
        time.sleep(1)

    if lease.state == vim.HttpNfcLease.State.error:
        test_util.test_fail("vim.HttpNfcLease.State.error")
    if lease.state == vim.HttpNfcLease.State.done:
        test_util.test_fail("vim.HttpNfcLease.State.done")

    ovf_handle.upload_disks(lease, os.environ.get('vcenter'))
    return cisr.importSpec.configSpec.name


def create_vm(name="vm-0", vm_folder=None, resource_pool=None, host=None):
    from pyVim import task
    from pyVmomi import vim

    datastore = host.datastore[0].name
    datastore_path = '[' + datastore + '] ' + name

    vmx_file = vim.vm.FileInfo(logDirectory=None,
                               snapshotDirectory=None,
                               suspendDirectory=None,
                               vmPathName=datastore_path)

    config = vim.vm.ConfigSpec(name=name, memoryMB=128, numCPUs=1,
                               files=vmx_file, guestId='dosGuest',
                               version='vmx-07')
    Task = vm_folder.CreateVM_Task(config=config, pool=resource_pool)
    task.WaitForTask(Task)
    return Task.info.result

def add_vswitch_to_host(host=None, vsname=None, hostname=None):
    from pyVim import task
    from pyVmomi import vim
    tmp = os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP']
    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = os.environ.get("zstackManagementIp")
    cond = res_ops.gen_query_conditions('name', '=', hostname)
    vm = res_ops.query_resource(res_ops.VM_INSTANCE, cond)[0]
    l3_uuid = os.environ.get("vmL3Uuid2")
    for net in vm.vmNics:
        if net.l3NetworkUuid == l3_uuid:
            mac = net.mac
    for pnic in host.config.network.pnic:
        if mac == pnic.mac:
            nic = pnic.device
    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = tmp
    brige = vim.host.VirtualSwitch.BondBridge()
    brige.nicDevice = [nic,]
    spec = vim.host.VirtualSwitch.Specification()
    spec.bridge = brige
    spec.numPorts = 128
    host.configManager.networkSystem.AddVirtualSwitch(vswitchName=vsname, spec=spec)

def add_host_to_dvswitch(host=None, dvswitch=None, hostname=None):
    from pyVim import task
    from pyVmomi import vim
    tmp = os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP']
    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = os.environ.get("zstackManagementIp")
    cond = res_ops.gen_query_conditions('name', '=', hostname)
    vm = res_ops.query_resource(res_ops.VM_INSTANCE, cond)[0]
    l3_uuid = os.environ.get("vmL3Uuid3")
    for net in vm.vmNics:
        if net.l3NetworkUuid == l3_uuid:
            mac = net.mac
    for pnic in host.config.network.pnic:
        if mac == pnic.mac:
            nic = pnic.device
    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = tmp

    backing = vim.dvs.HostMember.PnicBacking(pnicSpec=[vim.dvs.HostMember.PnicSpec(pnicDevice=nic), ])
    host_config = vim.dvs.HostMember.ConfigSpec(host=host, backing=backing, operation='add')
    config = vim.DistributedVirtualSwitch.ConfigSpec(host=[host_config, ], configVersion=dvswitch.config.configVersion)
    Task = dvswitch.ReconfigureDvs_Task(spec=config)
    task.WaitForTask(Task)

def add_vm_to_dvsportgroup(vm=None, dportgroup=None):
    from pyVim import task
    from pyVmomi import vim

    virtual_nic_device = vim.vm.device.VirtualE1000()

    backing = vim.vm.device.VirtualEthernetCard.DistributedVirtualPortBackingInfo()
    backing.port = vim.dvs.PortConnection()
    backing.port.switchUuid = dportgroup.config.distributedVirtualSwitch.uuid
    backing.port.portgroupKey = dportgroup.key
    virtual_nic_device.backing = backing

    virtual_nic_device.connectable = vim.vm.device.VirtualDevice.ConnectInfo()
    virtual_nic_device.connectable.startConnected = True
    virtual_nic_device.connectable.allowGuestControl = True
    virtual_nic_device.connectable.connected = False
    virtual_nic_device.connectable.status = 'untried'

    virtual_nic_device.addressType = 'assigned'

    device_config = vim.vm.device.VirtualDeviceSpec()
    device_config.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
    device_config.device = virtual_nic_device

    spec = vim.vm.ConfigSpec(deviceChange=[device_config, ])
    Task = vm.ReconfigVM_Task(spec=spec)
    task.WaitForTask(Task)

def add_vm_to_portgroup(vm=None, portgroup=None):
    from pyVim import task
    from pyVmomi import vim

    virtual_nic_device = vim.vm.device.VirtualE1000()

    backing = vim.vm.device.VirtualEthernetCard.NetworkBackingInfo()
    backing.network = portgroup
    backing.deviceName = portgroup.name
    virtual_nic_device.backing = backing

    virtual_nic_device.connectable = vim.vm.device.VirtualDevice.ConnectInfo()
    virtual_nic_device.connectable.startConnected = True
    virtual_nic_device.connectable.allowGuestControl = True
    virtual_nic_device.connectable.connected = False
    virtual_nic_device.connectable.status = 'untried'

    virtual_nic_device.addressType = 'assigned'

    device_config = vim.vm.device.VirtualDeviceSpec()
    device_config.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
    device_config.device = virtual_nic_device

    spec = vim.vm.ConfigSpec(deviceChange=[device_config, ])
    Task = vm.ReconfigVM_Task(spec=spec)
    task.WaitForTask(Task)

def get_obj(content, vimtype, name=None):
    obj = None
    container = content.viewManager.CreateContainerView(
        content.rootFolder, vimtype, True)
    if name:
        for c in container.view:
            if c.name == name:
                obj = c
                return obj
    return container.view

def deploy_initial_vcenter(deploy_config, scenario_config = None, scenario_file = None):
    from pyVmomi import vim
    from pyVim import connect
    from pyVim import task
    import atexit
    import zstackwoodpecker.operations.vcenter_operations as vct_ops
    import zstackwoodpecker.test_lib as test_lib

    vcenter = os.environ.get('vcenter')
    vcenteruser = os.environ.get('vcenteruser')
    vcenterpwd = os.environ.get('vcenterpwd')
    SI = connect.SmartConnectNoSSL(host=vcenter, user=vcenteruser, pwd=vcenterpwd, port=443)
    if not SI:
       test_util.test_fail("Unable to connect to the vCenter %s" % vcenter) 

    atexit.register(connect.Disconnect, SI)

    content = SI.RetrieveContent()
    exist_dc = get_obj(content, [vim.Datacenter])
    for dc in exist_dc:
        exist_cluster = vct_ops.get_cluster(content)
        for cluster in exist_cluster:
            vct_ops.remove_cluster(cluster)
        cleanup_datacenter(datacenter=dc)
    
    if not xmlobject.has_element(deploy_config, 'vcenter.datacenters.datacenter'):
        return

    for datacenter in xmlobject.safe_list(deploy_config.vcenter.datacenters.datacenter):
        vc_dc = create_datacenter(dcname=datacenter.name_, service_instance=SI)
        if xmlobject.has_element(datacenter, 'dswitch'):
            for dswitch in xmlobject.safe_list(datacenter.dswitch):
                dvswitch = create_dvswitch(datacenter=vc_dc, name=dswitch.name_)
                for dportgroup in xmlobject.safe_list(dswitch.dportgroups.dportgroup):
                    adddvswitch_portgroup(DVSwitch=dvswitch, name=dportgroup.name_, vlanId=dportgroup.vlanId_)
        for cluster in xmlobject.safe_list(datacenter.clusters.cluster):
            vc_cl = create_cluster(datacenter=vc_dc, clustername=cluster.name_)
            for host in xmlobject.safe_list(cluster.hosts.host):
                managementIp = get_host_from_scenario_file(host.name_, scenario_config, scenario_file, deploy_config)
                test_lib.check_vcenter_host(managementIp)
		vc_hs_spec = vim.host.ConnectSpec(hostName=managementIp,
                                                userName=host.username_,
                                                password=host.password_,
                                                sslThumbprint=host.thumbprint_,
                                                force=False)
                vc_hs = add_vc_host(cluster=vc_cl, host_spec=vc_hs_spec, asConnected=True)
                #The ESXi hosts are created from 1 template, so the default local storage shares the
                #same devicePath for different ESXi host, which will make only 1 host can be added 
                #into datacenter, here we work around to delete the datastore after host is added.
                if xmlobject.has_element(host, "iScsiStorage"):
                    for datastore in vc_hs.datastore:
                        datastore.Destroy()
                    target = get_iscsi_nfs_host_from_scenario_file(host.iScsiStorage.target_, scenario_config, scenario_file, deploy_config)
                    setup_iscsi_device(host=vc_hs, target_ip=target)
                    time.sleep(10)
                    if not vc_hs.datastore:
                        vc_ds = create_datastore(host=vc_hs, dsname=host.iScsiStorage.vmfsdatastore.name_)
                if xmlobject.has_element(host, "nfsStorage"):
                    for datastore in vc_hs.datastore:
                        datastore.Destroy()
                    target = get_iscsi_nfs_host_from_scenario_file(host.nfsStorage.target_, scenario_config, scenario_file, deploy_config)
                    vc_ds = create_nfs_datastore(host=vc_hs, remotehost=target, mount_point_path=host.nfsStorage.path_, ds_name=host.nfsStorage.nasdatastore.name_)
                if xmlobject.has_element(host, "vswitchs"):
                    for vswitch in xmlobject.safe_list(host.vswitchs.vswitch):
                        if vswitch.name_ == "vSwitch0":
                            for port_group in xmlobject.safe_list(vswitch.portgroup):
                                addvswitch_portgroup(host=vc_hs, vswitch=vswitch.name_, portgroup=port_group.text_, vlanId=port_group.vlanId_)
                        else:
                            add_vswitch_to_host(host=vc_hs, vsname=vswitch.name_, hostname=host.ref_)
                            for port_group in xmlobject.safe_list(vswitch.portgroup):
                                addvswitch_portgroup(host=vc_hs, vswitch=vswitch.name_, portgroup=port_group.text_, vlanId=port_group.vlanId_)
                if xmlobject.has_element(host, "dswitchRef"):
                    add_host_to_dvswitch(host=vc_hs, dvswitch=dvswitch, hostname=host.ref_)
		for vm in xmlobject.safe_list(host.vms.vm):
                    resource_pool = vc_cl.resourcePool
                    vc_vm = create_vm(name=vm.name_,vm_folder=vc_dc.vmFolder,resource_pool=resource_pool,host=vc_hs)
		    powerOn_vm(vc_vm)
                    if xmlobject.has_element(vm, "portgroupRef"):
                        for portgroup1 in xmlobject.safe_list(vm.portgroupRef):
                            portgroup1_vc = get_obj(content, [vim.Network], name=portgroup1.text_)
                            add_vm_to_portgroup(vm=vc_vm, portgroup=portgroup1_vc)
                    if xmlobject.has_element(vm, "dportgroupRef"):
                        for dportgroup1 in xmlobject.safe_list(vm.dportgroupRef):
                            dportgroup1_vc = get_obj(content, [vim.dvs.DistributedVirtualPortgroup], name=dportgroup1.text_)
                            add_vm_to_dvsportgroup(vm=vc_vm, dportgroup=dportgroup1_vc)
            if xmlobject.has_element(cluster, "templates"):
	        for template in xmlobject.safe_list(cluster.templates.template):
                    name = deploy_ova(service_instance=SI,
                                      datacenter=vc_dc,
                                      datastore=vc_cl.datastore[0],
                                      resourcepool=vc_cl.resourcePool,
                                      path=template.path_)
                    get_obj(content, [vim.VirtualMachine], name).MarkAsTemplate()
    test_util.test_logger('[Done] zstack initial vcenter environment was created successfully.')

