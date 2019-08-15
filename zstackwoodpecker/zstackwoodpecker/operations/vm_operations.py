'''

All VM operations for test.

@author: Youyk
'''

import apibinding.inventory as inventory
import apibinding.api_actions as api_actions
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.account_operations as account_operations
import zstackwoodpecker.operations.config_operations as config_operations
import zstackwoodpecker.operations.resource_operations as res_ops

import os
import inspect

def set_vm_clean_traffic(vm_uuid, clean_traffic_enable=True, session_uuid=None):
    action = api_actions.SetVmCleanTrafficAction()
    action.uuid = vm_uuid
    action.enable = clean_traffic_enable
    action.timeout = 240000
    test_util.action_logger('Set VM clean traffic [uuid:] %s' % vm_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def create_vm(vm_create_option):
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
    create_vm.cpuNum = vm_create_option.get_cpu_num()
    create_vm.memorySize = vm_create_option.get_memory_size()
    create_vm.rootDiskSize = vm_create_option.get_root_disk_size()
    #If there are more than 1 network uuid, the 1st one will be the default l3.
    if len(create_vm.l3NetworkUuids) > 1 and not create_vm.defaultL3NetworkUuid:
        create_vm.defaultL3NetworkUuid = create_vm.l3NetworkUuids[0]

    vm_type = vm_create_option.get_vm_type()
    if not vm_type:
        create_vm.type = 'UserVm'
    else:
        create_vm.type = vm_type

    create_vm.systemTags = vm_create_option.get_system_tags()
    cond = res_ops.gen_query_conditions('resourceUuid', '=', create_vm.imageUuid)
    systags = res_ops.query_resource(res_ops.SYSTEM_TAG, cond)
    for tags in systags:
        if tags.tag == "bootMode::UEFI":
            if create_vm.systemTags:
                create_vm.systemTags.append("vmMachineType::q35")
            else:
                create_vm.systemTags = ["vmMachineType::q35"]
            break

    create_vm.userTags = vm_create_option.get_user_tags()
    create_vm.rootVolumeSystemTags = vm_create_option.get_rootVolume_systemTags()
    create_vm.dataVolumeSystemTags = vm_create_option.get_dataVolume_systemTags()
    timeout = vm_create_option.get_timeout()
    if not timeout:
        create_vm.timeout = 1200000
    else:
        create_vm.timeout = timeout

    strategy_type = vm_create_option.get_strategy_type()
    create_vm.strategy = strategy_type

    create_vm.dataDiskOfferingUuids = vm_create_option.get_data_disk_uuids()
    create_vm.rootDiskOfferingUuid = vm_create_option.get_root_disk_uuid()
    create_vm.consolePassword = vm_create_option.get_console_password()
    create_vm.primaryStorageUuidForRootVolume = vm_create_option.get_ps_uuid()
    create_vm.rootPassword = vm_create_option.get_root_password()
    test_util.action_logger('Create VM: %s with [image:] %s and [l3_network:] %s' % (create_vm.name, create_vm.imageUuid, create_vm.l3NetworkUuids))
    evt = account_operations.execute_action_with_session(create_vm, vm_create_option.get_session_uuid())
    test_util.test_logger('[vm:] %s is created.' % evt.inventory.uuid)
    return evt.inventory

#The root volume will not be deleted immediately. It will only be reclaimed by system maintenance checking.
def destroy_vm(vm_uuid, session_uuid=None):
    action = api_actions.DestroyVmInstanceAction()
    action.uuid = vm_uuid
    action.timeout = 240000
    test_util.action_logger('Destroy VM [uuid:] %s' % vm_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def stop_vm(vm_uuid, force=None, session_uuid=None):
    action = api_actions.StopVmInstanceAction()
    action.uuid = vm_uuid
    action.type = force
    action.timeout = 240000
    test_util.action_logger('Stop VM [uuid:] %s' % vm_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def stop_ha_vm(vm_uuid, force=None, stopHA=None, session_uuid=None):
    action = api_actions.StopVmInstanceAction()
    action.uuid = vm_uuid
    action.type = force
    action.stopHA = stopHA
    action.timeout = 240000
    test_util.action_logger('Stop VM [uuid:] %s' % vm_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def suspend_vm(vm_uuid, session_uuid=None):
    action = api_actions.PauseVmInstanceAction()
    action.uuid = vm_uuid
    action.timeout = 240000
    test_util.action_logger('Pause VM [uuid:] %s' % vm_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def stop_vm_scheduler(vm_uuid, type, name, start_time=None, interval=None, repeatCount=None, cron=None, session_uuid=None):
    action = api_actions.CreateStopVmInstanceSchedulerAction()
    action.vmUuid = vm_uuid
    action.type = type
    action.schedulerName = name
    action.startTime = start_time
    action.interval = interval
    action.repeatCount = repeatCount
    action.cron = cron
    action.timeout = 240000
    test_util.action_logger('Create Stop VM Scheduler [uuid:] %s [type:] %s [startTimeStamp:] %s [interval:] %s [repeatCount:] %s [cron:] %s' % (vm_uuid, type, start_time, interval, repeatCount, cron))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def start_vm(vm_uuid, session_uuid=None, timeout=300000):
    action = api_actions.StartVmInstanceAction()
    action.uuid = vm_uuid
    action.timeout = timeout
    test_util.action_logger('Start VM [uuid:] %s' % vm_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def start_vm_with_user_args(vm_uuid, session_uuid=None, system_tags=None, timeout=240000):
    action = api_actions.StartVmInstanceAction()
    action.uuid = vm_uuid
    action.systemTags = system_tags
    action.timeout = timeout
    test_util.action_logger('Start VM [uuid:] %s' % vm_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def resume_vm(vm_uuid, session_uuid=None):
    action = api_actions.ResumeVmInstanceAction()
    action.uuid = vm_uuid
    action.timeout = 240000
    test_util.action_logger('Resume VM [uuid:] %s' % vm_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def update_vm(vm_uuid, cpu=None, memory=None, system_tags=None, session_uuid=None):
    action = api_actions.UpdateVmInstanceAction()
    action.uuid = vm_uuid
    action.cpuNum = cpu
    action.memorySize = memory
    action.systemTags = system_tags
    action.timeout = 240000
    test_util.action_logger('Update VM [uuid:] %s' % vm_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def start_vm_scheduler(vm_uuid, type, name, start_time=None, interval=None, repeatCount=None, cron=None, session_uuid=None, timeout=240000):
    action = api_actions.CreateStartVmInstanceSchedulerAction()
    action.vmUuid = vm_uuid
    action.type = type
    action.schedulerName = name
    action.startTime = start_time
    action.interval = interval
    action.repeatCount = repeatCount
    action.cron = cron
    action.timeout = timeout
    test_util.action_logger('Start VM Scheduler [uuid:] %s [type:] %s [startTime:] %s [interval:] %s [repeatCount:] %s [cron:] %s' % (vm_uuid, type, start_time, interval, repeatCount, cron))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def reboot_vm(vm_uuid, session_uuid=None):
    action = api_actions.RebootVmInstanceAction()
    action.uuid = vm_uuid
    action.timeout = 240000
    test_util.action_logger('Reboot VM [uuid:] %s' % vm_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def reboot_vm_scheduler(vm_uuid, type, name, start_time=None, interval=None, repeatCount=None, cron=None, session_uuid=None, timeout=240000):
    action = api_actions.CreateRebootVmInstanceSchedulerAction()
    action.vmUuid = vm_uuid
    action.type = type
    action.schedulerName = name
    action.startTime = start_time
    action.interval = interval
    action.repeatCount = repeatCount
    action.cron = cron
    action.timeout = timeout
    test_util.action_logger('Reboot VM Scheduler [uuid:] %s [type:] %s [startTime:] %s [interval:] %s [repeatCount:] %s [cron:] %s' % (vm_uuid, type, start_time, interval, repeatCount, cron))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def migrate_vm(vm_uuid, host_uuid, timeout = 480000, session_uuid = None):
    action = api_actions.MigrateVmAction()
    action.vmInstanceUuid = vm_uuid
    action.hostUuid = host_uuid
    if not timeout:
        timeout = 480000
    action.timeout = timeout
    test_util.action_logger('Migrate VM [uuid:] %s to Host [uuid:] %s, in timeout: %s' % (vm_uuid, host_uuid, timeout))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def change_vm_static_ip(vm_uuid, l3NetworkUuid, ip, session_uuid = None):
    action = api_actions.SetVmStaticIpAction()
    action.vmInstanceUuid = vm_uuid
    action.l3NetworkUuid = l3NetworkUuid
    action.ip = ip
    test_util.action_logger('Change VM static IP to %s [uuid:] %s' % (ip, vm_uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def reconnect_vr(vr_uuid, session_uuid=None):
    action = api_actions.ReconnectVirtualRouterAction()
    action.vmInstanceUuid = vr_uuid
    action.timeout = 600000
    test_util.action_logger('Reconnect VR VM [uuid:] %s' % vr_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def change_instance_offering(vm_uuid, offering_uuid, session_uuid=None):
    action = api_actions.ChangeInstanceOfferingAction()
    action.vmInstanceUuid = vm_uuid
    action.instanceOfferingUuid = offering_uuid
    test_util.action_logger('Change VM [uuid:] %s Instance Offering to %s '\
            % (vm_uuid, offering_uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def create_instance_offering(instance_offering_option, session_uuid = None):
    action = api_actions.CreateInstanceOfferingAction()
    action.cpuNum = instance_offering_option.get_cpuNum()
    #action.cpuSpeed = instance_offering_option.get_cpuSpeed()
    action.memorySize = instance_offering_option.get_memorySize()
    action.allocatorStrategy = instance_offering_option.get_allocatorStrategy()
    action.type = instance_offering_option.get_type()
    action.name = instance_offering_option.get_name()
    action.systemTags = instance_offering_option.get_system_tags()
    action.description = instance_offering_option.get_description()

    #test_util.action_logger('create instance offering: name: %s cpuNum: %s, cpuSpeed: %s, memorySize: %s, allocatorStrategy: %s, type: %s '\
    #        % (action.name, action.cpuNum, action.cpuSpeed, action.memorySize, action.allocatorStrategy, action.type))
    test_util.action_logger('create instance offering: name: %s cpuNum: %s, memorySize: %s, allocatorStrategy: %s, type: %s '\
            % (action.name, action.cpuNum, action.memorySize, action.allocatorStrategy, action.type))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.test_logger('Instance Offering: %s is created' % evt.inventory.uuid)
    return evt.inventory

def update_instance_offering(instance_offering_option, offering_uuid, system_tags=None, session_uuid=None):
    action = api_actions.UpdateInstanceOfferingAction()
    action.uuid = offering_uuid
    action.cpuNum = instance_offering_option.get_cpuNum()
    #action.cpuSpeed = instance_offering_option.get_cpuSpeed()
    action.memorySize = instance_offering_option.get_memorySize()
    #action.allocatorStrategy = instance_offering_option.get_allocatorStrategy()
    #action.type = instance_offering_option.get_type()
    action.name = instance_offering_option.get_name()
    action.description = instance_offering_option.get_description()
    #action.systemTags += instance_offering_option.get_name()
    if system_tags:
        action.systemTags = system_tags

    #test_util.action_logger('update instance offering: name: %s cpuNum: %s, cpuSpeed: %s, memorySize: %s, allocatorStrategy: %s, type: %s, systemTags: %s '\
    #        % (action.name, action.cpuNum, action.cpuSpeed, action.memorySize, action.allocatorStrategy, action.type, action.systemTags))
    test_util.action_logger('update instance offering: name: %s cpuNum: %s, memorySize: %s, systemTags: %s '\
            % (action.name, action.cpuNum, action.memorySize, action.systemTags))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.test_logger('Instance Offering: %s is created' % evt.inventory.uuid)
    return evt.inventory

def delete_instance_offering(instance_offering_uuid, session_uuid = None):
    action = api_actions.DeleteInstanceOfferingAction()
    action.uuid = instance_offering_uuid
    test_util.action_logger('Delete Instance Offering [uuid:] %s' \
            % instance_offering_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def expunge_vm(vm_uuid, session_uuid = None):
    action = api_actions.ExpungeVmInstanceAction()
    action.uuid = vm_uuid
    action.timeout = 60000
    test_util.action_logger('Expunge VM [uuid:] %s ' % vm_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def recover_vm(vm_uuid, session_uuid = None):
    action = api_actions.RecoverVmInstanceAction()
    action.uuid = vm_uuid
    action.timeout = 40000
    test_util.action_logger('Recover VM [uuid:] %s ' % vm_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def clone_vm(vm_uuid, vm_names, strategy, full = False, ps_uuid_for_root_volume = None, ps_uuid_for_data_volume = None, root_volume_systag = None, data_volume_systag = None, systemtag = None, session_uuid = None):
    action = api_actions.CloneVmInstanceAction()
    action.vmInstanceUuid = vm_uuid
    action.names=vm_names
    action.strategy=strategy
    action.full=full
    action.timeout = 80000000
    action.primaryStorageUuidForRootVolume = ps_uuid_for_root_volume
    action.primaryStorageUuidForDataVolume = ps_uuid_for_data_volume
    action.rootVolumeSystemTags = root_volume_systag
    action.dataVolumeSystemTags = data_volume_systag
    action.systemTags = systemtag
    test_util.action_logger('Clone VM [uuid:] %s to %s' % (vm_uuid, vm_names))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    test_util.test_logger('%s VMs have been cloned from %s' % (evt.result.numberOfClonedVm, vm_uuid))
    return evt.result.inventories

def change_vm_password(vm_uuid, vm_account, vm_password, skip_stopped_vm = None, session_uuid = None):
    action = api_actions.ChangeVmPasswordAction()
    action.uuid = vm_uuid
    action.account = vm_account
    action.password = vm_password
    action.skipstop = skip_stopped_vm
    action.timeout = 2000000
    test_util.action_logger('Change VM [uuid:] %s password' % (vm_uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def reinit_vm(vm_uuid, session_uuid = None):
    action = api_actions.ReimageVmInstanceAction()
    action.vmInstanceUuid = vm_uuid

    test_util.action_logger('Reinit [Vm:] %s' % (vm_uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def set_vm_nic_qos(nic_uuid, outboundBandwidth=None, inboundBandwidth=None, session_uuid = None):
    action = api_actions.SetNicQosAction()
    action.uuid = nic_uuid
    action.outboundBandwidth = outboundBandwidth
    action.inboundBandwidth = inboundBandwidth

    test_util.action_logger('SetNicQos [nic:] %s' % (nic_uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def get_vm_nic_qos(nic_uuid, session_uuid = None):
    action = api_actions.GetNicQosAction()
    action.uuid = nic_uuid

    test_util.action_logger('GetNicQos [nic:] %s' % (nic_uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def del_vm_nic_qos(nic_uuid, direction, session_uuid = None):
    action = api_actions.DeleteNicQosAction()
    action.uuid = nic_uuid
    action.direction = direction

    test_util.action_logger('DeleteNicQos [nic:] %s' % (nic_uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def set_vm_disk_qos(volume_uuid, volumeBandwidth=None, mode=None, session_uuid = None):
    action = api_actions.SetVolumeQosAction()
    action.uuid = volume_uuid
    action.volumeBandwidth = volumeBandwidth
    if mode:
        action.mode = mode
    test_util.action_logger('SetVolumeQos [volume:] %s' % (volume_uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def get_vm_disk_qos(volume_uuid, session_uuid = None):
    action = api_actions.GetVolumeQosAction()
    action.uuid = volume_uuid

    test_util.action_logger('GetVolumeQos [volume:] %s' % (volume_uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def del_vm_disk_qos(volume_uuid, mode=None, session_uuid = None):
    action = api_actions.DeleteVolumeQosAction()
    action.uuid = volume_uuid
    if mode:
        action.mode = mode
    test_util.action_logger('DeleteVolumeQos [volume:] %s' % (volume_uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def get_vm_qga_enable(vm_uuid, session_uuid = None):
    action = api_actions.GetVmQgaEnableAction()
    action.uuid = vm_uuid
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def set_vm_qga_enable(vm_uuid, session_uuid = None):
    action = api_actions.SetVmQgaAction()
    action.uuid = vm_uuid
    action.enable = 'true'
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def set_vm_qga_disable(vm_uuid, session_uuid = None):
    action = api_actions.SetVmQgaAction()
    action.uuid = vm_uuid
    action.enable = 'false'
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def get_vm_capabilities(vm_uuid, session_uuid = None):
    action = api_actions.GetVmCapabilitiesAction()
    action.uuid = vm_uuid
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def change_vm_image(vm_uuid,image_uuid,session_uuid=None):
    action = api_actions.ChangeVmImageAction()
    action.vmInstanceUuid = vm_uuid
    action.imageUuid = image_uuid
    action.timeout = 600000
    test_util.action_logger('Change image [imageUuid:] %s for vm [vmInstanceUuid:] %s' % (image_uuid, vm_uuid))
    evt = account_operations.execute_action_with_session(action,session_uuid)
    return evt.inventory

def get_image_candidates_for_vm_to_change(vm_uuid,session_uuid=None):
    action = api_actions.GetImageCandidatesForVmToChangeAction()
    action.vmInstanceUuid = vm_uuid
    action.timeout = 2400000
    test_util.action_logger('Get image candidates for vm [uuid:] %s to change' % vm_uuid)
    evt = account_operations.execute_action_with_session(action,session_uuid)
    return evt

def get_vm_migration_candidate_hosts(vm_uuid,session_uuid=None):
    action = api_actions.GetVmMigrationCandidateHostsAction()
    action.vmInstanceUuid = vm_uuid
    test_util.action_logger('Get candidate hosts for vm [uuid:] %s to migrate' % vm_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventories

def get_vm_starting_candidate(vm_uuid,systemtag=[],session_uuid=None):
    action = api_actions.GetVmStartingCandidateClustersHostsAction()
    action.uuid = vm_uuid
    action.systemtag = systemtag
    test_util.action_logger('Get candidate hosts for starting vm [uuid:] %s to migrate' % vm_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.hostInventories

def get_vm_starting_candidate_clusters_hosts(vm_uuid,systemtag=[],session_uuid=None):
    action = api_actions.GetVmStartingCandidateClustersHostsAction()
    action.uuid = vm_uuid
    action.systemtag = systemtag
    test_util.action_logger('Get candidate hosts for starting vm [uuid:] %s to migrate' % vm_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def set_vm_boot_order(vm_uuid,boot_order,session_uuid=None):
    action = api_actions.SetVmBootOrderAction()
    action.uuid = vm_uuid
    action.bootOrder = boot_order
    test_util.action_logger('Set vm[uuid:] %s boot order %s' % (vm_uuid, boot_order))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def delete_vm_ssh_key(vm_uuid,session_uuid=None):
    action = api_actions.DeleteVmSshKeyAction()
    action.uuid = vm_uuid
    test_util.action_logger('Delete vm[uuid:] %s sshkey' % vm_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def update_vm_nic_mac(vmNic_uuid, mac, session_uuid=None):
    action = api_actions.UpdateVmNicMacAction()
    action.vmNicUuid = vmNic_uuid
    action.mac = mac
    action.timeout = 240000
    test_util.action_logger('Update VM [uuid:] %s mac[address:] %s' % (vmNic_uuid,mac))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def delete_vm_static_ip(vm_uuid, l3NetworkUuid, session_uuid = None):
    action = api_actions.DeleteVmStaticIpAction()
    action.vmInstanceUuid = vm_uuid
    action.l3NetworkUuid = l3NetworkUuid
    test_util.action_logger('Delete VM[uuid:] %s l3Network[uuid:] %s static IP ' % (vm_uuid, l3NetworkUuid))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def set_vm_rdp(vm_uuid,enable,session_uuid = None):
    action = api_actions.SetVmRDPAction()
    action.uuid = vm_uuid
    action.enable = enable
    test_util.action_logger('Set VM[uuid:] %s RDP[enable:] %s ' % (vm_uuid, enable))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def set_vm_monitor_number(vm_uuid,monitor_number,session_uuid = None):
    action = api_actions.SetVmMonitorNumberAction()
    action.uuid = vm_uuid
    action.monitorNumber = monitor_number
    test_util.action_logger('Set VM[uuid:] %s Monitor Number[number:] %s ' % (vm_uuid, monitor_number))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def set_vm_usb_redirect(uuid,enable,session_uuid = None):
    action = api_actions.SetVmUsbRedirectAction()
    action.uuid = uuid
    action.enable = enable
    test_util.action_logger('Set VM[uuid:] %s Usb Redirect[enable:] %s ' % (uuid, enable))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def start_vm_with_target_host(vm_uuid, host_uuid=None, cluster_uuid=None, session_uuid=None, timeout=240000):
    action = api_actions.StartVmInstanceAction()
    action.uuid = vm_uuid
    action.hostUuid = host_uuid
    action.clusterUuid = cluster_uuid
    action.timeout = timeout
    test_util.action_logger('Start VM [uuid:] %s' % vm_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def get_candidate_iso_for_attaching(vm_uuid, session_uuid = None):
    action = api_actions.GetCandidateIsoForAttachingVmAction()
    action.vmInstanceUuid = vm_uuid
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventories

def set_vm_hostname(uuid, hostname, session_uuid=None):
    action = api_actions.SetVmHostnameAction()
    action.uuid = uuid
    action.hostname = hostname
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def get_vm_hostname(uuid, session_uuid=None):
    action = api_actions.GetVmHostnameAction()
    action.uuid = uuid
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.hostname

def create_vm_backup(backup_option, session_uuid=None):
    action = api_actions.CreateVmBackupAction()
    action.backupStorageUuid = backup_option.get_backupStorage_uuid()
    action.name = backup_option.get_name()
    action.timeout = 7200000
    action.rootVolumeUuid = backup_option.get_volume_uuid()
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventories

def create_vm_from_backup(group_uuid, bs_uuid, session_uuid=None):
    action = api_actions.CreateVmFromVmBackupAction()
    action.groupUuid = group_uuid
    action.backupStorageUuid = bs_uuid
    evt = account_operations.execute_action_with_session(action, session_uuid)

def revert_vm_from_backup(group_uuid, bs_uuid, session_uuid=None):
    action = api_actions.CreateVmFromVmBackupAction()
    action.groupUuid = group_uuid
    action.backupStorageUuid = bs_uuid
    evt = account_operations.execute_action_with_session(action, session_uuid)

def get_vm_attachable_data_volume(vmInstanceUuid, session_uuid=None):
    action = api_actions.GetVmAttachableDataVolumeAction()
    action.vmInstanceUuid = vmInstanceUuid
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventories