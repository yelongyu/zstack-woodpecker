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
import apibinding.inventory as inventory
import os
import sys
import traceback
import threading
import time

#global exception information for thread usage
exc_info = []
AddKVMHostTimeOut = 10*60*1000
IMAGE_THREAD_LIMIT = 2
DEPLOY_THREAD_LIMIT = 500

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
                                if vm.backupStorageRef.type_ == 'ceph':
                                    nic_id = get_ceph_storages_mon_nic_id(vm.backupStorageRef.text_, scenarioConfig)
                                    if nic_id == None:
                                        ip_list.append(s_vm.ip_)
                                    else:
            	                        ip_list.append(s_vm.ips.ip[nic_id].ip_)
                                else:
                                    ip_list.append(s_vm.ip_)
    return ip_list

#Add Backup Storage
def add_backup_storage(scenarioConfig, scenarioFile, deployConfig, session_uuid):
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
            thread = threading.Thread(target = _thread_for_action, args = (action, ))
            wait_for_thread_queue()
            thread.start()

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
            thread = threading.Thread(target=_add_zone, args=(zone, i, ))
            wait_for_thread_queue()
            thread.start()

    wait_for_thread_done()

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

    ip_list = []
    for host in xmlobject.safe_list(scenarioConfig.deployerConfig.hosts.host):
        for vm in xmlobject.safe_list(host.vms.vm):
            if xmlobject.has_element(vm, 'primaryStorageRef'):
                if vm.primaryStorageRef.text_ == primaryStorageRefName:
                    with open(scenarioFile, 'r') as fd:
                        xmlstr = fd.read()
                        fd.close()
                        scenario_file = xmlobject.loads(xmlstr)
                        for s_vm in xmlobject.safe_list(scenario_file.vms.vm):
                            if s_vm.name_ == vm.name_:
                                if vm.backupStorageRef.type_ == 'ceph':
                                    nic_id = get_ceph_storages_mon_nic_id(vm.backupStorageRef.text_, scenarioConfig)
                                    if nic_id == None:
                                        ip_list.append(s_vm.ip_)
                                    else:
            	                        ip_list.append(s_vm.ips.ip[nic_id].ip_)
                                else:
                                    ip_list.append(s_vm.ip_)
    return ip_list

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
        action.availableCapacity = sizeunit.get_size(pr.availableCapacity_)
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
                else:
                    action.url = pr.url_
                action.zoneUuid = zinv.uuid
                thread = threading.Thread(target=_thread_for_action, args=(action,))
                wait_for_thread_queue()
                thread.start()

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

    for zone in xmlobject.safe_list(deployConfig.zones.zone):
        if zone_name and zone.name_ != zone_name:
            continue
        _deploy_primary_storage(zone)

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

        if xmlobject.has_element(cluster, 'l2VxlanNetworkPoolRef'):
            for l2vxlanpoolref in xmlobject.safe_list(cluster.l2VxlanNetworkPoolRef):
                l2_vxlan_pool_name = l2vxlanpoolref.text_
                poolinvs = res_ops.get_resource(res_ops.L2_VXLAN_NETWORK_POOL, session_uuid, name=l2_vxlan_pool_name)
                poolinv = get_first_item_from_list(poolinvs, 'L2 Vxlan Network Pool', l2_vxlan_pool_name, 'Cluster')

                l2_vxlan_pool_name = l2vxlanpoolref.text_
                action_vxlan = api_actions.AttachL2NetworkToClusterAction()
                action_vxlan.l2NetworkUuid = poolinv.uuid
                action_vxlan.clusterUuid = cinv.uuid
                action_vxlan.systemTags = ["l2NetworkUuid::%s::clusterUuid::%s::cidr::{%s}" % (poolinv.uuid, cinv.uuid, l2vxlanpoolref.cidr_)]
                action_vxlan.sessionUuid = session_uuid
                evt = action_vxlan.run()

	if xmlobject.has_element(zone.l2Networks, 'l2VxlanNetwork'):
            for l2_vxlan in zone.l2Networks.l2VxlanNetwork:
                if xmlobject.has_element(l2_vxlan, 'l2VxlanNetworkPoolRef'):
                    l2_vxlan_invs = res_ops.get_resource(res_ops.L2_VXLAN_NETWORK, session_uuid, name=l2_vxlan.name_)
                    if len(l2_vxlan_invs) > 0:
                        continue
                    l2_vxlan_pool_name = l2vxlanpoolref.text_
                    poolinvs = res_ops.get_resource(res_ops.L2_VXLAN_NETWORK_POOL, session_uuid, name=l2_vxlan_pool_name)
                    poolinv = get_first_item_from_list(poolinvs, 'L2 Vxlan Network Pool', l2_vxlan_pool_name, 'Cluster')
                    action_vxlan = api_actions.createL2VxlanNetworkAction()
                    action_vxlan.poolUuid = poolinv.uuid
                    action_vxlan.name = l2_vxlan.name_
                    action_vxlan.zoneUuid = action.zoneUuid
                    action_vxlan.sessionUuid = session_uuid

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
                    action = api_actions.CreateClusterAction()
                    action.sessionUuid = session_uuid
                    action.name = generate_dup_name(generate_dup_name(cluster.name_, zone_ref, 'z'), cluster_ref, 'c')
                    action.description = generate_dup_name(generate_dup_name(cluster.description__, zone_ref, 'z'), cluster_ref, 'c')
        
                    action.hypervisorType = cluster.hypervisorType_
                    zone_name = generate_dup_name(zone.name_, zone_ref, 'z')
        
                    zinvs = res_ops.get_resource(res_ops.ZONE, session_uuid, name=zone_name)
                    zinv = get_first_item_from_list(zinvs, 'Zone', zone_name, 'Cluster')
                    action.zoneUuid = zinv.uuid
                    thread = threading.Thread(target=_add_cluster, args=(action, zone_ref, cluster, cluster_ref, ))
                    wait_for_thread_queue()
                    thread.start()

    for zone in xmlobject.safe_list(deployConfig.zones.zone):
        if zone_name and zone_name != zone.name_:
            continue 

        _deploy_cluster(zone)

    wait_for_thread_done()

def get_node_from_scenario_file(nodeRefName, scenarioConfig, scenarioFile, deployConfig):
    if scenarioConfig == None or scenarioFile == None or not os.path.exists(scenarioFile):
        return None

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
        for host in xmlobject.safe_list(cluster.hosts.host):
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
                if zone_ref == 0 and cluster_ref == 0 and i == 0:
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

                thread = threading.Thread(target=_thread_for_action, args = (action, ))
                wait_for_thread_queue()
                thread.start()

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
        action.l2NetworkUuid = l2inv_uuid
        action.name = l3Name
        action.type = inventory.L3_BASIC_NETWORK_TYPE
        if l3.domain_name__:
            action.dnsDomain = l3.domain_name__

        try:
            evt = action.run()
        except:
            exc_info.append(sys.exc_info())

        test_util.test_logger(jsonobject.dumps(evt))
        l3_inv = evt.inventory

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
            do_add_ip_range(l3.ipRange, l3_inv.uuid, session_uuid)

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
        zone_name= None, l3_name = None):
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
            do_add_ip_range(l3.ipRange, l3_inv.uuid, session_uuid, \
                    ip_range_name)

def do_add_ip_range(ip_range_xml_obj, l3_uuid, session_uuid, \
        ip_range_name = None):

    for ir in xmlobject.safe_list(ip_range_xml_obj):
        if ip_range_name and ip_range_name != ir.name_:
            continue

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
        action.cpuSpeed = instance_offering_xml_obj.cpuSpeed_
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

    #Add VM -- Pass

def _thread_for_action(action):
    try:
        evt = action.run()
        test_util.test_logger(jsonobject.dumps(evt))
    except:
        exc_info.append(sys.exc_info())

#Add Virtual Router Offering
def add_virtual_router(scenarioConfig, scenarioFile, deployConfig, session_uuid, l3_name = None, \
        zone_name = None):

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
        action.cpuSpeed = i.cpuSpeed_
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

def deploy_initial_database(deploy_config, scenario_config = None, scenario_file = None):
    operations = [
            add_backup_storage,
            add_zone,
            add_l2_network,
            add_primary_storage,
            add_cluster,
            add_host,
            add_l3_network,
            add_image,
            add_disk_offering,
            add_instance_offering,
            add_virtual_router
            ]
    for operation in operations:
        session_uuid = account_operations.login_as_admin()
        try:
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
