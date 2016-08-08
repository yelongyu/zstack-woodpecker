'''

All VM operations for test.

@author: Youyk
'''

import apibinding.inventory as inventory
import apibinding.api_actions as api_actions
import zstackwoodpecker.test_util as test_util
import account_operations
import config_operations

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
        create_vm.timeout = 600000
    else:
        create_vm.timeout = timeout

    create_vm.dataDiskOfferingUuids = vm_create_option.get_data_disk_uuids()
    create_vm.rootDiskOfferingUuid = vm_create_option.get_root_disk_uuid()

    test_util.action_logger('Create VM: %s with [image:] %s and [l3_network:] %s' % (create_vm.name, create_vm.imageUuid, create_vm.l3NetworkUuids))
    evt = account_operations.execute_action_with_session(create_vm, vm_create_option.get_session_uuid())
    test_util.test_logger('[vm:] %s is created.' % evt.inventory.uuid)
    return evt.inventory

#The root volume will not be deleted immediately. It will only be reclaimed by system maintenance checking.
def destroy_vm(vm_uuid, session_uuid=None):
    action = api_actions.DestroyVmInstanceAction()
    action.uuid = vm_uuid
    action.timeout = 120000
    test_util.action_logger('Destroy VM [uuid:] %s' % vm_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def stop_vm(vm_uuid, session_uuid=None):
    action = api_actions.StopVmInstanceAction()
    action.uuid = vm_uuid
    action.timeout = 120000
    test_util.action_logger('Stop VM [uuid:] %s' % vm_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def stop_vm_scheduler(vm_uuid, type, name, start_date=None, interval=None, repeatCount=None, cron=None, session_uuid=None):
    action = api_actions.CreateStopVmInstanceSchedulerAction()
    action.vmUuid = vm_uuid
    action.type = type
    action.schedulerName = name
    action.startDate = start_date
    action.interval = interval
    action.repeatCount = repeatCount
    action.cron = cron
    action.timeout = 120000
    test_util.action_logger('Create Stop VM Scheduler [uuid:] %s [type:] %s [startTimeStamp:] %s [interval:] %s [repeatCount:] %s [cron:] %s' % (vm_uuid, type, start_date, interval, repeatCount, cron))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def start_vm(vm_uuid, session_uuid=None, timeout=120000):
    action = api_actions.StartVmInstanceAction()
    action.uuid = vm_uuid
    action.timeout = timeout
    test_util.action_logger('Start VM [uuid:] %s' % vm_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def start_vm_scheduler(vm_uuid, type, name, start_date=None, interval=None, repeatCount=None, cron=None, session_uuid=None, timeout=120000):
    action = api_actions.CreateStartVmInstanceSchedulerAction()
    action.vmUuid = vm_uuid
    action.type = type
    action.schedulerName = name
    action.startDate = start_date
    action.interval = interval
    action.repeatCount = repeatCount
    action.cron = cron
    action.timeout = timeout
    test_util.action_logger('Start VM Scheduler [uuid:] %s [type:] %s [startDate:] %s [interval:] %s [repeatCount:] %s [cron:] %s' % (vm_uuid, type, start_date, interval, repeatCount, cron))
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def reboot_vm(vm_uuid, session_uuid=None):
    action = api_actions.RebootVmInstanceAction()
    action.uuid = vm_uuid
    action.timeout = 120000
    test_util.action_logger('Reboot VM [uuid:] %s' % vm_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory

def migrate_vm(vm_uuid, host_uuid, timeout = 240000, session_uuid = None):
    action = api_actions.MigrateVmAction()
    action.vmInstanceUuid = vm_uuid
    action.hostUuid = host_uuid
    if not timeout:
        timeout = 240000
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
    action.timeout = 300000
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
    action.timeout = 10000
    test_util.action_logger('Expunge VM [uuid:] %s ' % vm_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory 

def recover_vm(vm_uuid, session_uuid = None):
    action = api_actions.RecoverVmInstanceAction()
    action.uuid = vm_uuid
    action.timeout = 20000
    test_util.action_logger('Recover VM [uuid:] %s ' % vm_uuid)
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt.inventory 
