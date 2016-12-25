'''

All VM operations for test.

@author: Youyk
'''

import apibinding.inventory as inventory
import apibinding.api_actions as api_actions
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.account_operations as account_operations
import zstackwoodpecker.operations.config_operations as config_operations

import os
import inspect

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

def start_vm(vm_uuid, session_uuid=None, timeout=240000):
    action = api_actions.StartVmInstanceAction()
    action.uuid = vm_uuid
    action.timeout = timeout
    test_util.action_logger('Start VM [uuid:] %s' % vm_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def start_vm_with_user_args(vm_uuid, system_tags = None, session_uuid=None, timeout=240000):
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

def update_vm(vm_uuid, cpu, memory, session_uuid=None):
    action = api_actions.UpdateVmInstanceAction()
    action.uuid = vm_uuid
    action.cpuCores = cpu
    action.memory = memory
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
    action.cpuSpeed = instance_offering_option.get_cpuSpeed()
    action.memorySize = instance_offering_option.get_memorySize()
    action.allocatorStrategy = instance_offering_option.get_allocatorStrategy()
    action.type = instance_offering_option.get_type()
    action.name = instance_offering_option.get_name()
    action.description = instance_offering_option.get_description()

    test_util.action_logger('create instance offering: name: %s cpuNum: %s, cpuSpeed: %s, memorySize: %s, allocatorStrategy: %s, type: %s '\
            % (action.name, action.cpuNum, action.cpuSpeed, action.memorySize, action.allocatorStrategy, action.type))
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
    action.timeout = 40000
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

def clone_vm(vm_uuid, vm_names, strategy, session_uuid = None):
    action = api_actions.CloneVmInstanceAction()
    action.vmInstanceUuid = vm_uuid
    action.names=vm_names
    action.strategy=strategy
    action.timeout = 2000000
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
    action = api_actions.SetVmNicQosAction()
    action.vmNicUuid = nic_uuid
    action.outboundBandwidth = outboundBandwidth
    actoin.inboundBandwidth = inboundBandwidth

    test_util.action_logger('SetVmNicQos [nic:] %s' % (nic_uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def get_vm_nic_qos(nic_uuid, session_uuid = None):
    action = api_actions.GetVmNicQosAction()
    action.vmNicUuid = nic_uuid

    test_util.action_logger('GetVmNicQos [nic:] %s' % (nic_uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def set_vm_disk_qos(volume_uuid, volumeBandwidth=None, volumeIOPS=None, session_uuid = None):
    action = api_actions.SetVmDiskQosAction()
    action.volumeUuid = volume_uuid
    action.volumeBandwidth = volumeBandwidth
    actoin.volumeIOPS = volumeIOPS

    test_util.action_logger('SetVmDiskQos [volume:] %s' % (volume_uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def get_vm_disk_qos(volume_uuid, session_uuid = None):
    action = api_actions.GetVmDiskQosAction()
    action.volumeUuid = volume_uuid

    test_util.action_logger('GetVmDiskQos [volume:] %s' % (volume_uuid))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt
