'''

Create an unified test_stub to share test operations

@author: Youyk
'''

import os

import apibinding.api_actions as api_actions
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm
import zstackwoodpecker.zstack_test.zstack_test_volume as test_volume
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.operations.vpc_operations as vpc_ops
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.zstack_test.zstack_test_volume as zstack_volume_header
import zstackwoodpecker.zstack_test.zstack_test_vip as zstack_vip_header
import zstackwoodpecker.zstack_test.zstack_test_image as test_image
import zstackwoodpecker.header.vm as vm_header
from zstackwoodpecker.operations import vm_operations as vm_ops
import zstackwoodpecker.operations.longjob_operations as longjob_ops
import poplib
import time
import re
from email.parser import Parser

def create_vm(vm_creation_option=None, volume_uuids=None, root_disk_uuid=None,
              image_uuid=None, session_uuid=None):
    if not vm_creation_option:
        instance_offering_uuid = test_lib.lib_get_instance_offering_by_name(
            os.environ.get('instanceOfferingName_s')).uuid
        cond = res_ops.gen_query_conditions('mediaType', '!=', 'ISO')
        cond = res_ops.gen_query_conditions('platform', '=', 'Linux', cond)
        l3net_uuid = test_lib.lib_get_l3_by_name(
            os.environ.get('l3VlanNetwork3')).uuid
	if image_uuid:
	    image_uuid = image_uuid
	else:
            image_uuid = res_ops.query_resource(
            res_ops.IMAGE, cond, session_uuid)[0].uuid
        vm_creation_option = test_util.VmOption()
        vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
        vm_creation_option.set_image_uuid(image_uuid)
        vm_creation_option.set_l3_uuids([l3net_uuid])

    if volume_uuids:
        if isinstance(volume_uuids, list):
            vm_creation_option.set_data_disk_uuids(volume_uuids)
        else:
            test_util.test_fail(
                'volume_uuids type: %s is not "list".' % type(volume_uuids))

    if root_disk_uuid:
        vm_creation_option.set_root_disk_uuid(root_disk_uuid)

    if image_uuid:
        vm_creation_option.set_image_uuid(image_uuid)

    if session_uuid:
        vm_creation_option.set_session_uuid(session_uuid)

    vm = test_vm.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    return vm

def create_windows_vm(vm_creation_option=None, volume_uuids=None, root_disk_uuid=None, image_uuid=None, session_uuid=None):
    if not vm_creation_option:
        instance_offering_uuid = test_lib.lib_get_instance_offering_by_name(
            os.environ.get('instanceOfferingName_win')).uuid
        cond = res_ops.gen_query_conditions('mediaType', '!=', 'ISO')
        cond = res_ops.gen_query_conditions('platform', '=', 'Windows', cond)
        image_uuid = res_ops.query_resource(
            res_ops.IMAGE, cond, session_uuid)[0].uuid
        l3net_uuid = test_lib.lib_get_l3_by_name(
            os.environ.get('l3VlanNetwork3')).uuid
        vm_creation_option = test_util.VmOption()
        vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
        vm_creation_option.set_image_uuid(image_uuid)
        vm_creation_option.set_l3_uuids([l3net_uuid])
    return create_vm(vm_creation_option, volume_uuids, root_disk_uuid, image_uuid, session_uuid)

def create_volume(volume_creation_option=None, session_uuid=None):
    if not volume_creation_option:
        disk_offering = test_lib.lib_get_disk_offering_by_name(
            os.environ.get('smallDiskOfferingName'))
        volume_creation_option = test_util.VolumeOption()
        volume_creation_option.set_disk_offering_uuid(disk_offering.uuid)
        volume_creation_option.set_name('test_volume')

    if session_uuid:
        volume_creation_option.set_session_uuid(session_uuid)

    volume = zstack_volume_header.ZstackTestVolume()
    volume.set_creation_option(volume_creation_option)
    volume.create()
    return volume


def create_vm_with_volume(vm_creation_option=None, data_volume_uuids=None,
                          session_uuid=None):
    if not data_volume_uuids:
        disk_offering = test_lib.lib_get_disk_offering_by_name(
            os.environ.get('smallDiskOfferingName'), session_uuid)
        data_volume_uuids = [disk_offering.uuid]
    return create_vm(vm_creation_option, data_volume_uuids,
                     session_uuid=session_uuid)


def create_vm_with_iso(vm_creation_option=None, session_uuid=None):
    img_option = test_util.ImageOption()
    img_option.set_name('iso')
    root_disk_uuid = test_lib.lib_get_disk_offering_by_name(
        os.environ.get('rootDiskOfferingName')).uuid
    bs_uuid = res_ops.query_resource_fields(res_ops.BACKUP_STORAGE, [],
                                            session_uuid)[0].uuid
    img_option.set_backup_storage_uuid_list([bs_uuid])
    os.system("echo fake iso for test only >  %s/apache-tomcat/webapps/zstack/static/test.iso" %
              (os.environ.get('zstackInstallPath')))
    img_option.set_url('http://%s:8080/zstack/static/test.iso' %
                       (os.environ.get('node1Ip')))
    image_uuid = img_ops.add_iso_template(img_option).uuid

    return create_vm(vm_creation_option, None, root_disk_uuid, image_uuid,
                     session_uuid=session_uuid)


def create_vm_with_previous_iso(vm_creation_option=None, session_uuid=None):
    cond = res_ops.gen_query_conditions('name', '=', 'iso')
    image_uuid = res_ops.query_resource(res_ops.IMAGE, cond)[0].uuid
    root_disk_uuid = test_lib.lib_get_disk_offering_by_name(
        os.environ.get('rootDiskOfferingName')).uuid
    return create_vm(vm_creation_option, None, root_disk_uuid, image_uuid,
                     session_uuid=session_uuid)


def share_admin_resource(account_uuid_list):
    instance_offerings = res_ops.get_resource(res_ops.INSTANCE_OFFERING)
    for instance_offering in instance_offerings:
        acc_ops.share_resources(account_uuid_list, [instance_offering.uuid])
    cond = res_ops.gen_query_conditions('mediaType', '!=', 'ISO')
    images = res_ops.query_resource(res_ops.IMAGE, cond)
    for image in images:
        acc_ops.share_resources(account_uuid_list, [image.uuid])
    l3net_uuid = res_ops.get_resource(res_ops.L3_NETWORK)[0].uuid
    root_disk_uuid = test_lib.lib_get_disk_offering_by_name(
        os.environ.get('rootDiskOfferingName')).uuid
    data_disk_uuid = test_lib.lib_get_disk_offering_by_name(
        os.environ.get('smallDiskOfferingName')).uuid
    acc_ops.share_resources(
        account_uuid_list, [l3net_uuid, root_disk_uuid, data_disk_uuid])


def check_libvirt_host_uuid():
    libvirt_dir = "/etc/libvirt/libvirtd.conf"
    p = re.compile(r'^host_uuid')
    with open(libvirt_dir, 'r') as a:
        lines = a.readlines()
        for line in lines:
            if re.match(p, line):
                return True
    return False

def create_spice_vm(vm_creation_option=None, volume_uuids=None, root_disk_uuid=None,
              image_uuid=None,system_tag="vmConsoleMode::spice", session_uuid=None):
    if not vm_creation_option:
        instance_offering_uuid = test_lib.lib_get_instance_offering_by_name(
            os.environ.get('instanceOfferingName_s')).uuid
        cond = res_ops.gen_query_conditions('mediaType', '!=', 'ISO')
        cond = res_ops.gen_query_conditions('platform', '=', 'Linux', cond)
        image_uuid = res_ops.query_resource(
            res_ops.IMAGE, cond, session_uuid)[0].uuid
        l3net_uuid = res_ops.get_resource(
            res_ops.L3_NETWORK, session_uuid)[0].uuid
        vm_creation_option = test_util.VmOption()
        vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
        vm_creation_option.set_image_uuid(image_uuid)
        vm_creation_option.set_l3_uuids([l3net_uuid])
        vm_creation_option.set_system_tags([system_tag])

    if volume_uuids:
        if isinstance(volume_uuids, list):
            vm_creation_option.set_data_disk_uuids(volume_uuids)
        else:
            test_util.test_fail(
                'volume_uuids type: %s is not "list".' % type(volume_uuids))

    if root_disk_uuid:
        vm_creation_option.set_root_disk_uuid(root_disk_uuid)

    if image_uuid:
        vm_creation_option.set_image_uuid(image_uuid)

    if session_uuid:
        vm_creation_option.set_session_uuid(session_uuid)

    vm = test_vm.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    return vm

def get_vm_console_protocol(uuid, session_uuid=None):
    action = api_actions.GetVmConsoleAddressAction()
    action.timeout = 30000
    action.uuid = uuid
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    test_util.action_logger('Get VM Console protocol:  %s ' % evt.protocol)
    return evt

def create_vnc_vm(vm_creation_option=None, volume_uuids=None, root_disk_uuid=None,
              image_uuid=None,system_tag="vmConsoleMode::vnc", session_uuid=None):
    if not vm_creation_option:
        instance_offering_uuid = test_lib.lib_get_instance_offering_by_name(
            os.environ.get('instanceOfferingName_s')).uuid
        cond = res_ops.gen_query_conditions('mediaType', '!=', 'ISO')
        cond = res_ops.gen_query_conditions('platform', '=', 'Linux', cond)
        image_uuid = res_ops.query_resource(
            res_ops.IMAGE, cond, session_uuid)[0].uuid
        l3net_uuid = res_ops.get_resource(
            res_ops.L3_NETWORK, session_uuid)[0].uuid
        vm_creation_option = test_util.VmOption()
        vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
        vm_creation_option.set_image_uuid(image_uuid)
        vm_creation_option.set_l3_uuids([l3net_uuid])
        vm_creation_option.set_system_tags([system_tag])

    if volume_uuids:
        if isinstance(volume_uuids, list):
            vm_creation_option.set_data_disk_uuids(volume_uuids)
        else:
            test_util.test_fail(
                'volume_uuids type: %s is not "list".' % type(volume_uuids))

    if root_disk_uuid:
        vm_creation_option.set_root_disk_uuid(root_disk_uuid)

    if image_uuid:
        vm_creation_option.set_image_uuid(image_uuid)

    if session_uuid:
        vm_creation_option.set_session_uuid(session_uuid)

    vm = test_vm.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    return vm

def create_ag_vm(vm_creation_option=None, volume_uuids=None, root_disk_uuid=None,
              image_uuid=None, affinitygroup_uuid=None, host_uuid=None, session_uuid=None):
    if not vm_creation_option:
        instance_offering_uuid = test_lib.lib_get_instance_offering_by_name(
            os.environ.get('instanceOfferingName_s')).uuid
        cond = res_ops.gen_query_conditions('mediaType', '!=', 'ISO')
        cond = res_ops.gen_query_conditions('platform', '=', 'Linux', cond)
        image_uuid = res_ops.query_resource(
            res_ops.IMAGE, cond, session_uuid)[0].uuid
        l3net_uuid = res_ops.get_resource(
            res_ops.L3_NETWORK, session_uuid)[0].uuid
        vm_creation_option = test_util.VmOption()
        vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
        vm_creation_option.set_image_uuid(image_uuid)
        vm_creation_option.set_l3_uuids([l3net_uuid])
        vm_creation_option.set_host_uuid(host_uuid)
        vm_creation_option.set_system_tags(["affinityGroupUuid::%s"] % affinitygroup_uuid)

    if volume_uuids:
        if isinstance(volume_uuids, list):
            vm_creation_option.set_data_disk_uuids(volume_uuids)
        else:
            test_util.test_fail(
                'volume_uuids type: %s is not "list".' % type(volume_uuids))

    if root_disk_uuid:
        vm_creation_option.set_root_disk_uuid(root_disk_uuid)

    if image_uuid:
        vm_creation_option.set_image_uuid(image_uuid)

    if session_uuid:
        vm_creation_option.set_session_uuid(session_uuid)

    vm = test_vm.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    return vm


def create_data_volume_template_from_volume(volume_uuid, backup_storage_uuid_list, name = None, session_uuid = None ):
    volume_temp = vol_ops.create_volume_template(volume_uuid, backup_storage_uuid_list, name, session_uuid)
    return volume_temp

def create_data_volume_from_template(image_uuid, ps_uuid, name = None, host_uuid = None ):
    vol = vol_ops.create_volume_from_template(image_uuid, ps_uuid, name, host_uuid)
    return vol

def export_image_from_backup_storage(image_uuid, bs_uuid, session_uuid = None):
    imageurl = img_ops.export_image_from_backup_storage(image_uuid, bs_uuid, session_uuid)
    return imageurl

def delete_volume_image(image_uuid):
    img_ops.delete_image(image_uuid)

def get_local_storage_volume_migratable_hosts(volume_uuid):
    hosts = vol_ops.get_volume_migratable_host(volume_uuid)
    return hosts

def migrate_local_storage_volume(volume_uuid, host_uuid):
    vol_ops.migrate_volume(volume_uuid, host_uuid)

def delete_volume(volume_uuid):
    evt = vol_ops.delete_volume(volume_uuid)
    return evt

def expunge_volume(volume_uuid):
    evt = vol_ops.expunge_volume(volume_uuid)
    return evt

def recover_volume(volume_uuid):
    evt = vol_ops.recover_volume(volume_uuid)
    return evt

def expunge_image(image_uuid):
    evt = img_ops.expunge_image(image_uuid)
    return evt

def create_vip(vip_name=None, l3_uuid=None, session_uuid = None, required_ip=None):
    if not vip_name:
        vip_name = 'test vip'
    if not l3_uuid:
        l3_name = os.environ.get('l3PublicNetworkName')
        l3_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid

    vip_creation_option = test_util.VipOption()
    vip_creation_option.set_name(vip_name)
    vip_creation_option.set_l3_uuid(l3_uuid)
    vip_creation_option.set_session_uuid(session_uuid)
    vip_creation_option.set_requiredIp(required_ip)

    vip = zstack_vip_header.ZstackTestVip()
    vip.set_creation_option(vip_creation_option)
    vip.create()
    return vip

def delete_vip(vip_uuid, session_uuid = None):
    action = api_actions.DeleteVipAction()
    action.timeout = 30000
    action.uuid = vip_uuid
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    test_util.action_logger('Delete Vip:  %s ' % vip_uuid)
    return evt 

def create_vpc_vrouter(vr_name='test_vpc'):
    conf = res_ops.gen_query_conditions('name', '=', 'test_vpc')
    vr_list = res_ops.query_resource(res_ops.APPLIANCE_VM, conf)
    if vr_list:
        return ZstackTestVR(vr_list[0])
    vr_offering = res_ops.get_resource(res_ops.VR_OFFERING)[0]
    vr_inv =  vpc_ops.create_vpc_vrouter(name=vr_name, virtualrouter_offering_uuid=vr_offering.uuid)
    return ZstackTestVR(vr_inv)


def attach_l3_to_vpc_vr(vpc_vr, l3_list):
    for l3 in l3_list:
        vpc_vr.add_nic(l3.uuid)

class ZstackTestVR(vm_header.TestVm):
    def __init__(self, vr_inv):
        super(ZstackTestVR, self).__init__()
        self._inv = vr_inv

    def __hash__(self):
        return hash(self.inv.uuid)

    def __eq__(self, other):
        return self.inv.uuid == other.inv.uuid

    @property
    def inv(self):
        return self._inv

    @inv.setter
    def inv(self, value):
        self._inv = value

    def destroy(self, session_uuid = None):
        vm_ops.destroy_vm(self.inv.uuid, session_uuid)
        super(ZstackTestVR, self).destroy()

    def reboot(self, session_uuid = None):
        self.inv = vm_ops.reboot_vm(self.inv.uuid, session_uuid)
        super(ZstackTestVR, self).reboot()

    def reconnect(self, session_uuid = None):
        self.inv = vm_ops.reconnect_vr(self.inv.uuid, session_uuid)

    def migrate(self, host_uuid, timeout = None, session_uuid = None):
        self.inv = vm_ops.migrate_vm(self.inv.uuid, host_uuid, timeout, session_uuid)
        super(ZstackTestVR, self).migrate(host_uuid)

    def migrate_to_random_host(self, timeout = None, session_uuid = None):
        host_uuid = random.choice([host.uuid for host in res_ops.get_resource(res_ops.HOST)
                                                      if host.uuid != test_lib.lib_find_host_by_vm(self.inv).uuid])
        self.inv = vm_ops.migrate_vm(self.inv.uuid, host_uuid, timeout, session_uuid)
        super(ZstackTestVR, self).migrate(host_uuid)

    def update(self):
        '''
        If vm's status was changed by none vm operations, it needs to call
        vm.update() to update vm's infromation.

        The none vm operations: host.maintain() host.delete(), zone.delete()
        cluster.delete()
        '''
        super(ZstackTestVR, self).update()
        if self.get_state != vm_header.EXPUNGED:
            update_inv = test_lib.lib_get_vm_by_uuid(self.inv.uuid)
            if update_inv:
                self.inv = update_inv
                #vm state need to chenage to stopped, if host is deleted
                host = test_lib.lib_find_host_by_vm(update_inv)
                if not host and self.inv.state != vm_header.STOPPED:
                    self.set_state(vm_header.STOPPED)
            else:
                self.set_state(vm_header.EXPUNGED)
            return self.inv

    def add_nic(self, l3_uuid):
        '''
        Add a new NIC device to VM. The NIC device will connect with l3_uuid.
        '''
        self.inv = net_ops.attach_l3(l3_uuid, self.inv.uuid)

    def remove_nic(self, nic_uuid):
        '''
        Detach a NIC from VM.
        '''
        self.inv = net_ops.detach_l3(nic_uuid)

def create_alarm(comparison_operator, period, threshold, namespace, metric_name, name=None, repeat_interval=None, labels=None, actions=None, resource_uuid=None, session_uuid=None):
    action = api_actions.CreateAlarmAction()
    action.timeout = 30000
    if not name:
        action.name = 'alarm_01'
    action.comparisonOperator=comparison_operator
    action.period=period
    action.threshold=threshold
    action.namespace=namespace
    action.metricName=metric_name
    if actions:
        action.actions=actions
    if repeat_interval:
        action.repeatInterval=repeat_interval
    if labels:
        action.labels=labels
    if resource_uuid:
        action.resourceUuid=resource_uuid
    test_util.action_logger('Create Alarm: %s ' % name)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def update_alarm(uuid, comparison_operator=None, period=None, threshold=None, name=None, repeat_interval=None, resource_uuid=None, session_uuid=None):
    action = api_actions.UpdateAlarmAction()
    action.timeout = 30000
    action.uuid = uuid
    if comparison_operator:
        action.comparisonOperator = comparison_operator
    if period:
        action.period = period
    if threshold:
        action.threshold = threshold
    if name:
        action.name = name
    test_util.action_logger('Update Alarm: %s ' % uuid)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def change_alarm_state(uuid, state_event, session_uuid=None):
    action = api_actions.ChangeAlarmStateAction()
    action.timeout = 30000
    action.uuid = uuid
    action.stateEvent = state_event
    test_util.action_logger('Change Alarm: %s State to %s' % (uuid, state_event))
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def delete_alarm(uuid, delete_mode=None, session_uuid=None):
    action = api_actions.DeleteAlarmAction()
    action.timeout = 30000
    action.uuid = uuid
    if delete_mode:
        action.deleteMode=delete_mode
    test_util.action_logger('Delete Alarm: %s ' % uuid)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def add_action_to_alarm(alarm_uuid, action_uuid, action_type, session_uuid=None):
    action = api_actions.AddActionToAlarmAction() 
    action.timeout = 30000
    action.alarmUuid = alarm_uuid
    action.actionUuid = action_uuid
    action.actionType = action_type
    test_util.action_logger('Add Action: %s to Alarm: %s ' % (action_uuid, alarm_uuid))
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def remove_action_from_alarm(alarm_uuid, action_uuid, delete_mode=None, session_uuid=None):
    action = api_actions.RemoveActionFromAlarmAction()
    action.timeout = 30000
    action.alarmUuid = alarm_uuid
    action.actionUuid = action_uuid
    if delete_mode:
        action.deleteMode = delete_mode
    test_util.action_logger('Remove Action: %s From Alarm: %s ' % (action_uuid, alarm_uuid))
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def add_label_to_alarm(alarm_uuid, key, value, operator, session_uuid=None):
    action = api_actions.AddLabelToAlarmAction()
    action.timeout = 30000
    action.alarmUuid = alarm_uuid
    action.key = key
    action.value = value
    action.operator = operator
    test_util.action_logger('Add Label to Alarm: %s ' %alarm_uuid)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def remove_label_from_alarm(uuid, delete_mode=None, session_uuid=None):
    action = api_actions.RemoveLabelFromAlarmAction()
    action.timeout = 30000
    action.uuid = uuid
    if delete_mode:
        action.deleteMode = delete_mode
    test_util.action_logger('Remove Label From Alarm: %s ' %uuid)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def subscribe_event(namespace, event_name, actions, labels=None, session_uuid=None):
    action = api_actions.SubscribeEventAction()
    action.timeout = 30000
    action.namespace = namespace
    action.eventName = event_name
    action.actions = actions
    if labels:
        action.labels = labels
    test_util.action_logger('Subscribe Event: %s ' %event_name)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def unsubscribe_event(uuid, delete_mode=None, session_uuid=None):
    action = api_actions.UnsubscribeEventAction()
    action.timeout = 30000
    action.uuid = uuid
    if delete_mode:
        action.deleteMode = delete_mode
    test_util.action_logger('Unsubscribe Event: %s ' %uuid)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def create_sns_email_endpoint(email, name, platform_uuid=None, session_uuid=None):
    action = api_actions.CreateSNSEmailEndpointAction()
    action.timeout = 30000
    action.email = email
    action.name = name
    if platform_uuid:
        action.platformUuid = platform_uuid
    test_util.action_logger('Create SNS Email Endpoint: %s ' %name)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def create_sns_email_platform(smtp_server, smtp_port, name, username=None, password=None, session_uuid=None):
    action = api_actions.CreateSNSEmailPlatformAction()
    action.timeout = 30000
    action.smtpServer = smtp_server
    action.smtpPort = smtp_port
    action.name = name
    if username:
        action.username = username
    if password:
        action.password = password
    test_util.action_logger('Create SNS Email Platform: %s ' %name)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def validate_sns_email_platform(uuid, session_uuid=None):
    action = api_actions.ValidateSNSEmailPlatformAction()
    action.timeout = 30000
    action.uuid = uuid
    test_util.action_logger('Validate SNS Email Platform: %s ' %uuid)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def create_sns_http_endpoint(url, name, username=None, password=None, session_uuid=None):
    action = api_actions.CreateSNSHttpEndpointAction()
    action.timeout = 30000
    action.url = url
    action.name = name
    if username:
        action.username = username
    if password:
        action.password = password
    test_util.action_logger('Create SNS Http Endpoint: %s ' %name)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def create_sns_dingtalk_endpoint(url, name, at_all=None, at_person_phone_numbers=None, session_uuid=None):
    action = api_actions.CreateSNSDingTalkEndpointAction()
    action.timeout = 30000
    action.url = url
    action.name = name
    if at_all:
        action.atAll = at_all
    if at_person_phone_numbers:
        action.atPersonPhoneNumbers = at_person_phone_numbers
    test_util.action_logger('Create SNS DingTalk Endpoint: %s ' %name)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def add_sns_dingtalk_at_person(phone_number, endpoint_uuid, session_uuid=None):
    action = api_actions.AddSNSDingTalkAtPersonAction()
    action.timeout = 30000
    action.phoneNumber = phone_number
    action.endpointUuid = endpoint_uuid
    test_util.action_logger('Add SNS DingTalk At Person: %s ' %phone_number)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def remove_sns_dingtalk_at_person(phone_number, endpoint_uuid, delete_mode=None, session_uuid=None):
    action = api_actions.RemoveSNSDingTalkAtPersonAction()
    action.timeout = 30000
    action.phoneNumber = phone_number
    action.endpointUuid = endpoint_uuid
    if delete_mode:
        action.deleteMode = delete_mode
    test_util.action_logger('Remove SNS DingTalk At Person: %s ' % endpoint_uuid)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def update_sns_application_endpoint(uuid, name, description, session_uuid=None):
    action = api_actions.UpdateSNSApplicationEndpointAction()
    action.timeout = 30000
    action.uuid = uuid
    action.name = name
    action.description = description
    test_util.action_logger('Update SNS Application Endpoint: %s ' %uuid)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def delete_sns_application_endpoint(uuid, delete_mode=None, session_uuid=None):
    action = api_actions.DeleteSNSApplicationEndpointAction()
    action.timeout = 30000
    action.uuid = uuid
    if delete_mode:
        action.deleteMode = delete_mode
    test_util.action_logger('Delete SNS Application Endpoint: %s ' %uuid)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def change_sns_application_endpoint_state(uuid, state_event, session_uuid=None):
    action = api_actions.ChangeSNSApplicationEndpointStateAction()
    action.timeout = 30000
    action.uuid = uuid
    action.stateEvent = state_event
    test_util.action_logger('Change SNS Application Endpoint State To: %s ' %state_event)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def update_sns_application_platform(uuid, name, description, session_uuid=None):
    action = api_actions.UpdateSNSApplicationPlatformAction()
    action.timeout = 30000
    action.uuid = uuid
    action.name = name
    action.description = description
    test_util.action_logger('Update SNS Application Platform: %s ' %uuid)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def delete_sns_application_platform(uuid, delete_mode=None, session_uuid=None):
    action = api_actions.DeleteSNSApplicationPlatformAction()
    action.timeout = 30000
    action.uuid = uuid
    if delete_mode:
        action.deleteMode = delete_mode
    test_util.action_logger('Delete SNS Application Platform: %s ' %uuid)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def change_sns_application_platform_state(uuid, state_event, session_uuid=None):
    action = api_actions.ChangeSNSApplicationPlatformStateAction()
    action.timeout = 30000
    action.uuid = uuid
    action.stateEvent = state_event
    test_util.action_logger('Change SNS Application Platform State To: %s ' %state_event)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def create_sns_topic(name, session_uuid=None):
    action = api_actions.CreateSNSTopicAction()
    action.timeout = 30000
    action.name = name
    test_util.action_logger('Create SNS Topic: %s ' %name)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def update_sns_topic(uuid, name, description, session_uuid=None):
    action = api_actions.UpdateSNSTopicAction()
    action.timeout = 30000
    action.uuid = uuid
    action.name = name
    action.description = description
    test_util.action_logger('Update SNS Topic: %s ' %uuid)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def delete_sns_topic(uuid, delete_mode=None, session_uuid=None):
    action = api_actions.DeleteSNSTopicAction()
    action.timeout = 30000
    action.uuid = uuid
    if delete_mode:
        action.deleteMode = delete_mode
    test_util.action_logger('Delete SNS Topic: %s ' %uuid)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def change_sns_topic_state(uuid, state_event, session_uuid=None):
    action = api_actions.ChangeSNSTopicStateAction()
    action.timeout = 30000
    action.uuid = uuid
    action.stateEvent = state_event
    test_util.action_logger('Change SNS Topic State To: %s ' %state_event)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def subscribe_sns_topic(topic_uuid, endpoint_uuid, session_uuid=None):
    action = api_actions.SubscribeSNSTopicAction()
    action.timeout = 30000
    action.topicUuid = topic_uuid
    action.endpointUuid = endpoint_uuid
    test_util.action_logger('Subscribe SNS Topic: %s ' %topic_uuid)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def unsubscribe_sns_topic(topic_uuid, endpoint_uuid, session_uuid=None):
    action = api_actions.UnsubscribeSNSTopicAction()
    action.timeout = 30000
    action.topicUuid = topic_uuid
    action.endpointUuid = endpoint_uuid
    test_util.action_logger('Unsubscribe SNS Topic: %s ' %topic_uuid)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def get_all_metric_metadata(session_uuid=None):
    action = api_actions.GetAllMetricMetadataAction()
    action.timeout = 30000
    test_util.action_logger('Get All Metric Metadata:')
    evt = acc_ops.execute_action_with_session(action,session_uuid)
    return evt.metrics

def get_all_event_metadata(session_uuid=None):
    action = api_actions.GetAllEventMetadataAction()
    action.timeout = 30000
    test_util.action_logger('Get All Event Metadata:')
    evt = acc_ops.execute_action_with_session(action,session_uuid)
    return evt.events

def get_audit_data(start_time=None,end_time=None,limit=None,conditions=None,session_uuid=None):
    action = api_actions.GetAuditDataAction()
    action.timeout = 30000
    if start_time:
        action.startTime=start_time
    if end_time:
        action.endTime=end_time
    if limit:
        action.limit=limit
    if conditions:
        action.conditions=conditions
    test_util.action_logger('Get Audit Data:')
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.audits

def get_metric_label_value(namespace,metric_name,label_names,filter_labels=None,session_uuid=None):
    action = api_actions.GetMetricLabelValueAction()
    action.timeout = 30000
    action.namespace = namespace
    action.metricName = metric_name
    action.labelNames = label_names
    if filter_labels:
        action.filterLabels = filter_labels
    test_util.action_logger('Get Metric Label value:[namespace]:%s [metricName]:%s [labelNames]:%s'% (namespace,metric_name,label_names))
    evt=acc_ops.execute_action_with_session(action,session_uuid)
    return evt.labels

def get_metric_data(namespace,metric_name,start_time=None,end_time=None,period=None,labels=None,session_uuid=None):
    action = api_actions.GetMetricDataAction()
    action.timeout = 30000
    action.namespace = namespace
    action.metricName = metric_name
    if start_time:
        action.startTime = start_time
    if end_time:
        action.endTime = end_time
    if period:
        action.period = period
    if labels:
        action.labels = labels
    test_util.action_logger('Get Metric Data:[namespace]:%s [metricName]:%s' % (namespace, metric_name,))
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.data

def get_event_data(start_time=None,end_time=None,labels=None,conditions=None,session_uuid=None):
    action = api_actions.GetEventDataAction()
    action.timeout = 30000
    if start_time:
        action.startTime = start_time
    if end_time:
        action.endTime = end_time
    if conditions:
        action.conditions= conditions
    if labels:
        action.labels = labels
    test_util.action_logger('Get Event Data:')
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.events

def put_metric_data(namespace,data,session_uuid=None):
    action = api_actions.PutMetricDataAction()
    action.timeout = 30000
    action.namespace = namespace
    action.data = data
    test_util.action_logger('Put Metric Data:[namespace]:%s [data]:%s'%(namespace,data))
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def create_sns_text_template(name,applicationPlatformType,template,defaultTemplate=None,description=None,session_uuid=None):
    action = api_actions.CreateSNSTextTemplateAction()
    action.timeout = 30000
    action.name = name
    action.applicationPlatformType = applicationPlatformType
    action.template = template
    if defaultTemplate:
        action.defaultTemplate = defaultTemplate
    if description:
        action.description = description
    test_util.action_logger('Create SNS Text Template:%s '% name)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def delete_sns_text_template(uuid,delete_mode=None,session_uuid=None):
    action = api_actions.DeleteSNSTextTemplateAction()
    action.timeout = 30000
    action.uuid = uuid
    if delete_mode:
        action.deleteMode = delete_mode
    test_util.action_logger('Delete SNS Text Template:%s ' % uuid)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def update_sns_text_template(uuid,name=None,description=None,template=None,default_template=None,session_uuid=None):
    action = api_actions.UpdateSNSTextTemplateAction()
    action.timeout = 30000
    action.uuid = uuid
    if name:
        action.name = name
    if description:
        action.description = description
    if template:
        action.template = template
    if default_template:
        action.defaultTemplate = default_template
    test_util.action_logger('Update SNS Text Template:%s ' % uuid)
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    return evt.inventory

def get_mail_list(pop_server, username, password):
    test_util.action_logger('Get Mail List From [pop server]:%s [user]:%s '%(pop_server,username))
    pop3 = poplib.POP3(pop_server)
    pop3.set_debuglevel(1)
    pop3.user(username)
    pop3.pass_(password)
    ret = pop3.stat()
    mail_list = []
    for i in range(ret[0] - 20, ret[0]+1):
        resp, msg, octets = pop3.retr(i)
        mail_list.append(msg)
    pop3.quit()
    return mail_list

def check_sns_email(pop_server, username, password, name, uuid):
    '''
    This function is using for checking default SNS Text Template

    :param pop_server: 'pop3.zstack.io'
    :param username: 'test.qa@zstack.io'
    :param password: 'Test1234'
    :param name: metric_name or event_name
    :param uuid: For Alarm email,this is alarm_uuid;For Event email,this is subscription_uuid or resource_uuid
    :return: 1 for found or 0 for not found
    '''
    mail_list = get_mail_list(pop_server, username, password)
    flag = 0      #check result
    test_util.action_logger('Check SNS Email:[name]:%s [uuid]:%s'% (name,uuid))
    for mail in mail_list:
        if flag == 1:
            break
        #msg_content = b'\r\n'.join(mail).decode('utf-8') #python3.x
        msg_content = '\r\n'.join(mail)  #python2.x
        msg = Parser().parsestr(msg_content)
        content=str(msg)
        if (username in content) and (name in content) and (uuid in content):
            flag = 1
            test_util.test_logger('Mail sent addr is %s' % username)
            test_util.test_logger('Got keywords uuid : %s in Mail' % uuid)
            test_util.test_logger('Got keywords name: %s in Mail' % name)

    test_util.test_logger('flag value is %s' % flag)
    return flag

def check_keywords_in_email(pop_server, username, password, first_keyword, second_keyword):
    '''
    This function is used for checking different SNS Text Template

    :param pop_server: 'pop3.zstack.io'
    :param username: 'test.qa@zstack.io'
    :param password: 'Test1234'
    :param first_keyword: keyword search in mail
    :param second_keyword: keyword search in mail
    :return: 1 for found or 0 for not found
    '''
    mail_list = get_mail_list(pop_server, username, password)
    flag = 0      #check result
    test_util.action_logger('Check Keywords In Email:[keyword]:%s [keyword]:%s'% (first_keyword,second_keyword))
    for mail in mail_list:
        if flag == 1:
            break
        #msg_content = b'\r\n'.join(mail).decode('utf-8') #python3.x
        msg_content = '\r\n'.join(mail)  #python2.x
        msg = Parser().parsestr(msg_content)
        content=str(msg)
        if (username in content) and (first_keyword in content) and (second_keyword in content):
            flag = 1
            test_util.test_logger('Mail sent addr is %s' % username)
            test_util.test_logger('Got first_keyword :[ %s ]in Mail' % first_keyword)
            test_util.test_logger('Got second_keyword :[ %s ]in Mail' % second_keyword)
    test_util.test_logger('flag value is %s' % flag)
    return flag

def sleep_util(timestamp):
   while True:
      if time.time() >= timestamp:
         break
      time.sleep(0.5)


class MulISO(object):
    def __init__(self):
        self.vm1 = None
        self.vm2 = None
        self.iso_uuids = None
        self.iso = [{'name': 'iso1', 'url': 'http://zstack.yyk.net/iso/iso1.iso'},
                    {'name': 'iso2', 'url': 'http://zstack.yyk.net/iso/iso2.iso'},
                    {'name': 'iso3', 'url': 'http://zstack.yyk.net/iso/iso3.iso'}]

    def add_iso_image(self):
        bs_uuid = res_ops.query_resource(res_ops.BACKUP_STORAGE)[0].uuid
        images = res_ops.query_resource(res_ops.IMAGE)
        image_names = [i.name for i in  images]
        if self.iso[-1]['name'] not in image_names:
            for iso in self.iso:
                img_option = test_util.ImageOption()
                img_option.set_name(iso['name'])
                img_option.set_backup_storage_uuid_list([bs_uuid])
                testIsoUrl = iso['url']
                img_option.set_url(testIsoUrl)
                image_inv = img_ops.add_iso_template(img_option)
                image = test_image.ZstackTestImage()
                image.set_image(image_inv)
                image.set_creation_option(img_option)

    def get_all_iso_uuids(self):
        cond = res_ops.gen_query_conditions('mediaType', '=', 'ISO')
        iso_images = res_ops.query_resource(res_ops.IMAGE, cond)
        self.iso_uuids = [i.uuid for i in iso_images]

    def check_iso_candidate(self, iso_name, vm_uuid=None, is_candidate=False):
        if not vm_uuid:
            vm_uuid = self.vm1.vm.uuid
        iso_cand = vm_ops.get_candidate_iso_for_attaching(vm_uuid)
        cand_name_list = [i.name for i in iso_cand]
        if is_candidate:
            assert iso_name in cand_name_list
        else:
            assert iso_name not in cand_name_list

    def create_vm(self, vm2=False):
        self.vm1 = create_vm()
        if vm2:
            self.vm2 = create_vm()

    def attach_iso(self, iso_uuid, vm_uuid=None):
        if not vm_uuid:
            vm_uuid = self.vm1.vm.uuid
        img_ops.attach_iso(iso_uuid, vm_uuid)
        self.check_vm_systag(iso_uuid, vm_uuid)

    def detach_iso(self, iso_uuid, vm_uuid=None):
        if not vm_uuid:
            vm_uuid = self.vm1.vm.uuid
        img_ops.detach_iso(vm_uuid, iso_uuid)
        self.check_vm_systag(iso_uuid, vm_uuid, tach='detach')

    def set_iso_first(self, iso_uuid, vm_uuid=None):
        if not vm_uuid:
            vm_uuid = self.vm1.vm.uuid
        system_tags = ['iso::%s::0' % iso_uuid]
        vm_ops.update_vm(vm_uuid, system_tags=system_tags)

    def check_vm_systag(self, iso_uuid, vm_uuid=None, tach='attach', order=None):
        if not vm_uuid:
            vm_uuid = self.vm1.vm.uuid
        cond = res_ops.gen_query_conditions('resourceUuid', '=', vm_uuid)
        systags = res_ops.query_resource(res_ops.SYSTEM_TAG, cond)
        iso_orders = {t.tag.split('::')[-2]: t.tag.split('::')[-1] for t in systags if 'iso' in t.tag}
        if tach == 'attach':
            assert iso_uuid in iso_orders
        else:
            assert iso_uuid not in iso_orders
        if order:
            assert iso_orders[iso_uuid] == order

class Longjob(object):
    def __init__(self):
        self.image_name = 'test'
        self.image_url = 'test'
        self.vm = None
        self.image_name_net = os.getenv('imageName_net')
        self.url = os.getenv('imageUrl_windows')
        self.add_image_job_name = 'APIAddImageMsg'
        self.crt_vm_image_job_name = 'APICreateRootVolumeTemplateFromRootVolumeMsg'
        self.crt_vol_image_job_name = 'APICreateDataVolumeTemplateFromVolumeMsg'

    def create_vm(self, vm2=False):
        self.vm = create_vm()

    def create_data_volume(self):
        conditions = res_ops.gen_query_conditions('name', '=', os.getenv('largeDiskOfferingName'))
        disk_offering_uuid = res_ops.query_resource(res_ops.DISK_OFFERING, conditions)[0].uuid
        ps_uuid = self.vm.vm.allVolumes[0].primaryStorageUuid
        volume_option = test_util.VolumeOption()
        volume_option.set_disk_offering_uuid(disk_offering_uuid)
        volume_option.set_name('data-volume-for-crt-image-test')
        volume_option.set_primary_storage_uuid(ps_uuid)
        self.data_volume = create_volume(volume_option)
        self.set_ceph_mon_env(ps_uuid)
        self.data_volume.attach(self.vm)
        self.data_volume.check()

    def set_ceph_mon_env(self, ps_uuid):
        cond_vol = res_ops.gen_query_conditions('uuid', '=', ps_uuid)
        ps = res_ops.query_resource(res_ops.PRIMARY_STORAGE, cond_vol)[0]
        if ps.type.lower() == 'ceph':
            ps_mon_ip = ps.mons[0].monAddr
            os.environ['cephBackupStorageMonUrls'] = 'root:password@%s' % ps_mon_ip

    def submit_longjob(self, job_data, name, job_type=None):
        if job_type == 'image':
            _job_name = self.add_image_job_name
        elif job_type == 'crt_vm_image':
            _job_name = self.crt_vm_image_job_name
        elif job_type == 'crt_vol_image':
            _job_name = self.crt_vol_image_job_name
        long_job = longjob_ops.submit_longjob(_job_name, job_data, name)
        assert long_job.state == "Running"
        cond_longjob = res_ops.gen_query_conditions('apiId', '=', long_job.apiId)
        for _ in xrange(60):
            longjob = res_ops.query_resource(res_ops.LONGJOB, cond_longjob)[0]
            if longjob.state == "Succeeded":
                break
            else:
                time.sleep(5)
        assert longjob.state == "Succeeded"
        assert longjob.jobResult == "Succeeded"
        progress = res_ops.get_task_progress(long_job.apiId)
        assert progress.content == '100'

    def add_image(self):
        name = "longjob_image"
        job_data = '{"name":"test-image-longjob", "url":%s, "mediaType"="RootVolumeTemplate", "format"="qcow2", "platform"="Linux", \
        "backupStorageUuids"=%s}' % (self.url, res_ops.query_resource(res_ops.BACKUP_STORAGE)[0].uuid)
        self.submit_longjob(job_data, name, job_type='image')

    def expunge_image(self):
        cond_image = res_ops.gen_query_conditions('name', '=', 'test-image-longjob')
        longjob_image = res_ops.query_resource(res_ops.IMAGE, cond_image)[0]
        img_ops.expunge_image(longjob_image.uuid, backup_storage_uuid_list=[res_ops.query_resource(res_ops.BACKUP_STORAGE)[0].uuid])

    def crt_vm_image(self):
        name = 'longjob_crt_vol_image'
        job_data = '{"name"="test-crt-vol-image", "guestOsType":"Linux","system"="false","platform"="Linux","backupStorageUuids"="%s", \
        "rootVolumeUuid"="%s"}' % (res_ops.query_resource(res_ops.BACKUP_STORAGE)[-1].uuid, self.vm.vm.rootVolumeUuid)
        self.submit_longjob(job_data, name, job_type='image')

    def crt_vol_image(self):
        name = 'longjob_crt_vol_image'
        job_data = '{"name"="test-crt-vol-image", "guestOsType":"Linux","system"="false","platform"="Linux","backupStorageUuids"="%s", \
        "dataVolumeUuid"="%s"}' %(res_ops.query_resource(res_ops.BACKUP_STORAGE)[0].uuid, self.data_volume.get_volume().uuid)
        self.submit_longjob(job_data, name, job_type='image')
