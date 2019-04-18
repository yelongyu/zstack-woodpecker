'''

List resource API

@author: Youyk
'''

import apibinding.api_actions as api_actions
import account_operations
import deploy_operations
import apibinding.inventory as inventory
import zstackwoodpecker.test_util as test_util
import zstacklib.utils.lock as lock
import zstacklib.utils.xmlobject as xmlobject
import time
import os
import sys
import traceback
import threading

#Define default get resource method. default is using searchAPI, it can also be ListAPI.
SEARCH_RESOURCE_METHOD = 'search'
LIST_RESOURCE_METHOD = 'list'
GET_RESOURCE_METHOD_BY_GET = 'get'
#GET_RESOURCE_METHOD = SEARCH_RESOURCE_METHOD
GET_RESOURCE_METHOD = LIST_RESOURCE_METHOD

BACKUP_STORAGE = 'BackupStorage'
SFTP_BACKUP_STORAGE = 'SftpBackupStorage'
CEPH_BACKUP_STORAGE = 'CephBackupStorage'
ZONE = 'Zone'
CLUSTER = 'Cluster'
PRIMARY_STORAGE = 'PrimaryStorage'
CEPH_PRIMARY_STORAGE = 'CephPrimaryStorage'
CEPH_PRIMARY_STORAGE_POOL = 'CephPrimaryStoragePool'
L2_NETWORK = 'L2Network'
L2_VLAN_NETWORK = 'L2VlanNetwork'
L2_VXLAN_NETWORK = 'L2VxlanNetwork'
L2_VXLAN_NETWORK_POOL = 'L2VxlanNetworkPool'
VNI_RANGE = 'VniRange'
L3_NETWORK = 'L3Network'
INSTANCE_OFFERING = 'InstanceOffering'
IMAGE = 'Image'
VOLUME = 'Volume'
SHARE_VOLUME = 'ShareVolume'
VM_INSTANCE = 'VmInstance'
IP_RANGE = 'IpRange'
HOST = 'Host'
NETWORK_SERVICE_PROVIDER = 'NetworkServiceProvider'
NETWORK_SERVICE_PROVIDER_L3_REF = 'NetworkServiceProviderL3Ref'
APPLIANCE_VM = 'ApplianceVm'
VIRTUALROUTER_VM = 'VirtualRouterVm'
DISK_OFFERING = 'DiskOffering'
ACCOUNT = 'Account'
USER = 'User'
PRIMARY_STORAGE = 'PrimaryStorage'
SECURITY_GROUP = 'SecurityGroup'
SECURITY_GROUP_RULE = 'SecurityGroupRule'
VM_SECURITY_GROUP = 'VmSecurityGroup'
VM_NIC = 'VmNic'
PORT_FORWARDING = 'PortForwarding'
MANAGEMENT_NODE = 'ManagementNode'
EIP = 'Eip'
VIP = 'Vip'
IP_CAPACITY = 'IpCapacity'
VR_OFFERING = 'VirtualRouterOffering'
SYSTEM_TAG = 'SystemTag'
USER_TAG = 'UserTag'
VOLUME_SNAPSHOT_TREE = 'VolumeSnapshotTree'
VOLUME_SNAPSHOT = 'VolumeSnapshot'
LOAD_BALANCER = 'LoadBalancer'
LOAD_BALANCER_LISTENER = 'LoadBalancerListener'
LOCAL_STORAGE_RESOURCE_REF = 'LocalStorageResourceRef'
IMAGE_STORE_BACKUP_STORAGE = 'ImageStoreBackupStorage'
SCHEDULER = 'Scheduler'
SCHEDULERJOB = 'SchedulerJob'
SCHEDULERJOBGROUP = 'SchedulerJobGroup'
SCHEDULERTRIGGER = 'SchedulerTrigger'
VCENTER = 'VCenter'
VCENTER_CLUSTER = 'VCenterCluster'
VCENTER_BACKUP_STORAGE = 'VCenterBackupStorage'
VCENTER_PRIMARY_STORAGE = 'VCenterPrimaryStorage'
VCENTER_DVSWITCHES = 'VCenterDVSwitches'
MONITOR_TRIGGER = 'MonitorTrigger'
MONITOR_TRIGGER_ACTION = 'MonitorTriggerAction'
PXE_SERVER = 'PxeServer'
CHASSIS = 'Chassis'
HWINFO = 'HardwareInfo'
BAREMETAL_INS = 'BaremetalInstance'
LONGJOB = 'LongJob'
ALARM = 'Alarm'
EVENT_SUBSCRIPTION = 'EventSubscription'
SNS_APPLICATION_ENDPOINT = 'SNSApplicationEndpoint'
SNS_APPLICATION_PLATFORM ='SNSApplicationPlatform'
SNS_TOPIC = 'SNSTopic'
SNS_TOPIC_SUBSCRIBER = 'SNSTopicSubscriber'
SNS_DING_TALK_ENDPOINT = 'SNSDingTalkEndpoint'
SNS_EMAIL_ENDPOINT = 'SNSEmailEndpoint'
SNS_EMAIL_PLATFORM = 'SNSEmailPlatform'
SNS_HTTP_ENDPOINT = 'SNSHttpEndpoint'
SNS_TEXT_TEMPLATE = 'SNSTextTemplate'
AFFINITY_GROUP = "AffinityGroup"
IAM2_ORGANIZATION = 'IAM2Organization'
IAM2_PROJECT = 'IAM2Project'
IAM2_VIRTUAL_ID_GROUP = 'IAM2VirtualIDGroup'
IAM2_VIRTUAL_ID = 'IAM2VirtualID'
IAM2_PROJECT_TEMPLATE = 'IAM2ProjectTemplate'
IAM2_VIRTUAL_ID_GROUP_ATTRIBUTE = 'IAM2VirtualIDGroupAttribute'
IAM2_VIRTUAL_ID_ATTRIBUTE = 'IAM2VirtualIDAttribute'
IAM2_PROJECT_ATTRIBUTE = 'IAM2ProjectAttribute'
IAM2_ORGANIZATION_ATTRIBUTE = 'IAM2OrganizationAttribute'
ROLE='Role'
POLICY='Policy'
DATACENTER = 'DataCenter'
NAS_FILESYSTEM = 'NasFileSystem'
NAS_MOUNTTARGET = 'NasMountTarget'
ALIYUNNAS_ACCESSGROUP = 'AliyunNasAccessGroup'
STACK_TEMPLATE = "StackTemplate"
RESOURCE_STACK = "ResourceStack"
EVENT_FROM_STACK = "EventFromStack"
TICKET = 'Ticket'
TICKET_HISTORY = 'TicketHistory'
QUOTA = 'Quota'
CERTIFICATE = 'certificate'
VOLUME_BACKUP = 'VolumeBackup'
IPSEC_CONNECTION = 'IPsecConnection'
SCSI_LUN = 'ScsiLun'
ISCSI_SERVER = 'iScsiServer'
VROUTER_OSPF_AREA = 'VRouterOspfArea'
VROUTER_OSPF_NETWORK = 'VRouterOspfNetwork'
REPLICATIONGROUP = 'ReplicationGroup'

def find_item_by_uuid(inventories, uuid):
    for item in inventories:
        if item.uuid == uuid:
            #test_util.test_logger("Item found by UUID: %s" % uuid)
            return [item]
    #test_util.test_logger("Not found item with UUID: %s" % uuid)
    return None

def find_item_by_name(inventories, name):
    for item in inventories:
        if item.name == name:
            #test_util.test_logger("Item found by name: %s" % name)
            return [item]
    #test_util.test_logger("Not found item with name: %s" % name)
    return None

#Using List API
def list_resource(resource, session_uuid=None, uuid=None, name=None):
    '''
        Return: list by list API.
    '''
    if resource == BACKUP_STORAGE:
        action = api_actions.ListBackupStorageAction()
    elif resource == ZONE:
        action = api_actions.ListZonesAction()
    elif resource == PRIMARY_STORAGE:
        action = api_actions.ListPrimaryStorageAction()
    elif resource == L2_NETWORK:
        action = api_actions.ListL2NetworkAction()
    elif resource == L2_VLAN_NETWORK:
        action = api_actions.ListL2VlanNetworkAction()
    elif resource == CLUSTER:
        action = api_actions.ListClusterAction()
    elif resource == L3_NETWORK:
        action = api_actions.ListL3NetworkAction()
    elif resource == INSTANCE_OFFERING:
        action = api_actions.ListInstanceOfferingAction()
    elif resource == IMAGE:
        action = api_actions.ListImageAction()
    elif resource == VOLUME:
        action = api_actions.ListVolumeAction()
    elif resource == VM_INSTANCE:
        action = api_actions.ListVmInstanceAction()
    elif resource == IP_RANGE:
        action = api_actions.ListIpRangeAction()
    elif resource == HOST:
        action = api_actions.ListHostAction()
    elif resource == NETWORK_SERVICE_PROVIDER:
        action = api_actions.ListNetworkServiceProviderAction()
    elif resource == APPLIANCE_VM:
        action = api_actions.ListApplianceVmAction()
    elif resource == DISK_OFFERING:
        action = api_actions.ListDiskOfferingAction()
    elif resource == ACCOUNT:
        action = api_actions.ListAccountAction()
    elif resource == PRIMARY_STORAGE:
        action = api_actions.ListPrimaryStorageAction()
    elif resource == SECURITY_GROUP:
        action = api_actions.ListSecurityGroupAction()
    elif resource == VM_SECURITY_GROUP:
        action = api_actions.ListVmNicInSecurityGroupAction()
    elif resource == VM_NIC:
        action = api_actions.ListVmNicAction()
    elif resource == PORT_FORWARDING:
        action = api_actions.ListPortForwardingRuleAction()
    elif resource == MANAGEMENT_NODE:
        action = api_actions.ListManagementNodeAction()

    ret = account_operations.execute_action_with_session(action, session_uuid)

    if uuid:
        return find_item_by_uuid(ret, uuid)

    if name:
        return find_item_by_name(ret, name)

    return ret

#Using Search API
def search_resource(resource, session_uuid, uuid=None, name=None):
    '''
        Return: list by search
        This API was depricated. 
    '''
    if resource == BACKUP_STORAGE:
        action = api_actions.SearchBackupStorageAction()
    elif resource == ZONE:
        action = api_actions.SearchZoneAction()
    elif resource == PRIMARY_STORAGE:
        action = api_actions.SearchPrimaryStorageAction()
    elif resource == L2_NETWORK:
        action = api_actions.SearchL2NetworkAction()
    elif resource == L2_VLAN_NETWORK:
        action = api_actions.SearchL2VlanNetworkAction()
    elif resource == CLUSTER:
        action = api_actions.SearchClusterAction()
    elif resource == L3_NETWORK:
        action = api_actions.SearchL3NetworkAction()
    elif resource == INSTANCE_OFFERING:
        action = api_actions.SearchInstanceOfferingAction()
    elif resource == IMAGE:
        action = api_actions.SearchImageAction()
    elif resource == VOLUME:
        action = api_actions.SearchVolumeAction()
    elif resource == VM_INSTANCE:
        action = api_actions.SearchVmInstanceAction()
    elif resource == IP_RANGE:
        action = api_actions.SearchIpRangeAction()
    elif resource == HOST:
        action = api_actions.SearchHostAction()
    elif resource == NETWORK_SERVICE_PROVIDER:
        action = api_actions.SearchNetworkServiceProviderAction()
    elif resource == APPLIANCE_VM:
        action = api_actions.SearchApplianceVmAction()
    elif resource == DISK_OFFERING:
        action = api_actions.SearchDiskOfferingAction()
    elif resource == ACCOUNT:
        action = api_actions.SearchAccountAction()
    elif resource == PRIMARY_STORAGE:
        action = api_actions.SearchPrimaryStorageAction()
    #elif resource == SECURITY_GROUP:
    #    action = api_actions.SearchSecurityGroupAction()
    #elif resource == VM_SECURITY_GROUP:
    #    action = api_actions.SearchVmNicInSecurityGroupAction()

    action.sessionUuid = session_uuid
    action.nameOpValueTriples = []

    if uuid:
        t = inventory.NOVTriple()
        t.name = 'uuid'
        t.op = inventory.AND_EQ
        t.val = uuid
        action.nameOpValueTriples.append(t)

    if name:
        t = inventory.NOVTriple()
        t.name = 'name'
        t.op = inventory.AND_EQ
        t.val = name
        action.nameOpValueTriples.append(t)

    # the time delay is because of elastic search iventory will delay 0.5s after original data was created in database.
    time.sleep(0.3)
    ret = action.run()
    return ret

def get_resource_by_get(resource, session_uuid, uuid):
    '''
        Return a list by get API.
    '''
    if resource == BACKUP_STORAGE:
        action = api_actions.GetBackupStorageAction()
    elif resource == ZONE:
        action = api_actions.GetZoneAction()
    elif resource == PRIMARY_STORAGE:
        action = api_actions.GetPrimaryStorageAction()
    elif resource == L2_NETWORK:
        action = api_actions.GetL2NetworkAction()
    elif resource == L2_VLAN_NETWORK:
        action = api_actions.GetL2VlanNetworkAction()
    elif resource == CLUSTER:
        action = api_actions.GetClusterAction()
    elif resource == L3_NETWORK:
        action = api_actions.GetL3NetworkAction()
    elif resource == INSTANCE_OFFERING:
        action = api_actions.GetInstanceOfferingAction()
    elif resource == IMAGE:
        action = api_actions.GetImageAction()
    elif resource == VOLUME:
        action = api_actions.GetVolumeAction()
    elif resource == VM_INSTANCE:
        action = api_actions.GetVmInstanceAction()
    elif resource == IP_RANGE:
        action = api_actions.GetIpRangeAction()
    elif resource == HOST:
        action = api_actions.GetHostAction()
    elif resource == NETWORK_SERVICE_PROVIDER:
        action = api_actions.GetNetworkServiceProviderAction()
    elif resource == APPLIANCE_VM:
        action = api_actions.GetApplianceVmAction()
    elif resource == DISK_OFFERING:
        action = api_actions.GetDiskOfferingAction()
    elif resource == ACCOUNT:
        action = api_actions.GetAccountAction()
    elif resource == PRIMARY_STORAGE:
        action = api_actions.GetPrimaryStorageAction()
    elif resource == VR_OFFERING:
        action = api_actions.GetVirtualRouterOfferingAction()
    elif resource == VCENTER_DVSWITCHES:
        action = api_actions.GetVCenterDVSwitchesAction()
    #elif resource == SECURITY_GROUP:
    #    action = api_actions.GetSecurityGroupAction()
    #elif resource == VM_SECURITY_GROUP:
    #    action = api_actions.GetVmNicInSecurityGroupAction()

    action.uuid = uuid

    ret = account_operations.execute_action_with_session(action, session_uuid)

    return ret

def gen_query_conditions(name, op, value, conditions=[]):
    new_conditions = [{'name': name, 'op': op, 'value': value}]
    new_conditions.extend(conditions)
    return new_conditions

reimage_thread_queue = 0

@lock.lock('image_thread')
def increase_image_thread():
    global reimage_thread_queue
    reimage_thread_queue += 1

@lock.lock('image_thread')
def decrease_image_thread():
    global reimage_thread_queue
    reimage_thread_queue -= 1

def wait_for_image_thread_queue():
    while reimage_thread_queue >= IMAGE_THREAD_LIMIT:
        time.sleep(1)
        print 'reimage_thread_queue: %d' % reimage_thread_queue

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

exc_info = []
IMAGE_THREAD_LIMIT=2
def _lazyload_image(condition=None):

    def _load_image(action):
        increase_image_thread()
        try:
            #evt = action.run()
            evt = account_operations.execute_action_with_session(action, None)
        except:
            exc_info.append(sys.exc_info())
        finally:
            decrease_image_thread()

    iaction = api_actions.QueryImageAction()
    iaction.conditions = condition
    ret = account_operations.execute_action_with_session(iaction, None)

    if len(ret) != 0:
        print "no need lazy"
        return

    test_config_path = os.environ.get('WOODPECKER_TEST_CONFIG_FILE')
    test_config_obj = test_util.TestConfig(test_config_path)
    #Special config in test-config.xml, such like test ping target. 
    test_config = test_config_obj.get_test_config()
    #All configs in deploy.xml.
    all_config = test_config_obj.get_deploy_config()
    #Detailed zstack deployment information, including zones/cluster/hosts...
    deploy_config = all_config.deployerConfig
    

    for i in xmlobject.safe_list(deploy_config.images.image):
        image_action = api_actions.QueryImageAction()
        condition = gen_query_conditions('name', '=', i.name_)
        image_action.conditions = condition
        ret = account_operations.execute_action_with_session(image_action, None)
        
        if len(ret) != 0:
            print "image has beed added"
            continue

        session_uuid = None
        if i.hasattr('label_') and i.label_ == 'lazyload':
            for bsref in xmlobject.safe_list(i.backupStorageRef):
                bss = get_resource(BACKUP_STORAGE, None, name=bsref.text_)
                bs = deploy_operations.get_first_item_from_list(bss, 'backup storage', bsref.text_, 'image')
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
                thread = threading.Thread(target = _load_image, args = (action, ))
                wait_for_image_thread_queue()
                print 'before add image2: %s' % i.url_
                thread.start()
                print 'add image: %s' % i.url_
    print 'all images add command are executed'
    wait_for_thread_done(True)
    print 'all images have been added'

def _gen_query_action(resource, condition=None):
    if resource == BACKUP_STORAGE:
        action = api_actions.QueryBackupStorageAction()
    elif resource == SFTP_BACKUP_STORAGE:
        action = api_actions.QuerySftpBackupStorageAction()
    elif resource == CEPH_BACKUP_STORAGE:
        action = api_actions.QueryCephBackupStorageAction()
    elif resource == ZONE:
        action = api_actions.QueryZoneAction()
    elif resource == PRIMARY_STORAGE:
        action = api_actions.QueryPrimaryStorageAction()
    elif resource == L2_NETWORK:
        action = api_actions.QueryL2NetworkAction()
    elif resource == L2_VLAN_NETWORK:
        action = api_actions.QueryL2VlanNetworkAction()
    elif resource == L2_VXLAN_NETWORK:
        action = api_actions.QueryL2VxlanNetworkAction()
    elif resource == L2_VXLAN_NETWORK_POOL:
        action = api_actions.QueryL2VxlanNetworkPoolAction()
    elif resource == VNI_RANGE:
        action = api_actions.QueryVniRangeAction()
    elif resource == CLUSTER:
        action = api_actions.QueryClusterAction()
    elif resource == L3_NETWORK:
        action = api_actions.QueryL3NetworkAction()
    elif resource == INSTANCE_OFFERING:
        action = api_actions.QueryInstanceOfferingAction()
    elif resource == IMAGE:
        _lazyload_image(condition)
        action = api_actions.QueryImageAction()
    elif resource == VOLUME:
        action = api_actions.QueryVolumeAction()
    elif resource == SHARE_VOLUME:
        action = api_actions.QueryShareableVolumeVmInstanceRefAction()
    elif resource == VM_INSTANCE:
        action = api_actions.QueryVmInstanceAction()
    elif resource == IP_RANGE:
        action = api_actions.QueryIpRangeAction()
    elif resource == HOST:
        action = api_actions.QueryHostAction()
    elif resource == NETWORK_SERVICE_PROVIDER:
        action = api_actions.QueryNetworkServiceProviderAction()
    elif resource == NETWORK_SERVICE_PROVIDER_L3_REF:
        action = api_actions.QueryNetworkServiceL3NetworkRefAction()
    elif resource == APPLIANCE_VM:
        action = api_actions.QueryApplianceVmAction()
    elif resource == VIRTUALROUTER_VM:
        action = api_actions.QueryVirtualRouterVmAction()
    elif resource == DISK_OFFERING:
        action = api_actions.QueryDiskOfferingAction()
    elif resource == ACCOUNT:
        action = api_actions.QueryAccountAction()
    elif resource == CEPH_PRIMARY_STORAGE:
        action = api_actions.QueryCephPrimaryStorageAction()
    elif resource == CEPH_PRIMARY_STORAGE_POOL:
        action = api_actions.QueryCephPrimaryStoragePoolAction()
    elif resource == SECURITY_GROUP:
        action = api_actions.QuerySecurityGroupAction()
    elif resource == SECURITY_GROUP_RULE:
        action = api_actions.QuerySecurityGroupRuleAction()
    elif resource == VM_SECURITY_GROUP:
        action = api_actions.QueryVmNicInSecurityGroupAction()
    elif resource == VM_NIC:
        action = api_actions.QueryVmNicAction()
    elif resource == PORT_FORWARDING:
        action = api_actions.QueryPortForwardingRuleAction()
    elif resource == MANAGEMENT_NODE:
        action = api_actions.QueryManagementNodeAction()
    elif resource == EIP:
        action = api_actions.QueryEipAction()
    elif resource == VIP:
        action = api_actions.QueryVipAction()
    elif resource == VR_OFFERING:
        action = api_actions.QueryVirtualRouterOfferingAction()
    elif resource == SYSTEM_TAG:
        action = api_actions.QuerySystemTagAction()
    elif resource == USER_TAG:
        action = api_actions.QueryUserTagAction()
    elif resource == VOLUME_SNAPSHOT_TREE:
        action = api_actions.QueryVolumeSnapshotTreeAction()
    elif resource == VOLUME_SNAPSHOT:
        action = api_actions.QueryVolumeSnapshotAction()
    elif resource == USER:
        action = api_actions.QueryUserAction()
    elif resource == LOAD_BALANCER:
        action = api_actions.QueryLoadBalancerAction()
    elif resource == LOAD_BALANCER_LISTENER:
        action = api_actions.QueryLoadBalancerListenerAction()
    elif resource == LOCAL_STORAGE_RESOURCE_REF:
        action = api_actions.QueryLocalStorageResourceRefAction()
    elif resource == IMAGE_STORE_BACKUP_STORAGE:
        action = api_actions.QueryImageStoreBackupStorageAction()
    elif resource == SCHEDULER:
        action = api_actions.QuerySchedulerAction()
    elif resource == SCHEDULERJOB:
        action = api_actions.QuerySchedulerJobAction()
    elif resource == SCHEDULERJOBGROUP:
        action = api_actions.QuerySchedulerJobGroupAction()
    elif resource == SCHEDULERTRIGGER:
        action = api_actions.QuerySchedulerTriggerAction()
    elif resource == VCENTER:
        action = api_actions.QueryVCenterAction()
    elif resource == VCENTER_CLUSTER:
        action = api_actions.QueryVCenterClusterAction()
    elif resource == VCENTER_BACKUP_STORAGE:
        action = api_actions.QueryVCenterBackupStorageAction()
    elif resource == VCENTER_PRIMARY_STORAGE:
        action = api_actions.QueryVCenterPrimaryStorageAction()
    elif resource == MONITOR_TRIGGER:
        action = api_actions.QueryMonitorTriggerAction()
    elif resource == MONITOR_TRIGGER_ACTION:
        action = api_actions.QueryMonitorTriggerActionAction()
    elif resource == PXE_SERVER:
        action = api_actions.QueryBaremetalPxeServerAction()
    elif resource == CHASSIS:
        action = api_actions.QueryBaremetalChassisAction()
    elif resource == HWINFO:
        action = api_actions.QueryBaremetalHardwareInfoAction()
    elif resource == BAREMETAL_INS:
        action = api_actions.QueryBaremetalInstanceAction()
    elif resource == LONGJOB:
        action = api_actions.QueryLongJobAction()
    elif resource == ALARM:
        action = api_actions.QueryAlarmAction()
    elif resource == EVENT_SUBSCRIPTION:
        action = api_actions.QueryEventSubscriptionAction()
    elif resource == SNS_APPLICATION_ENDPOINT:
        action = api_actions.QuerySNSApplicationEndpointAction()
    elif resource == SNS_APPLICATION_PLATFORM:
        action = api_actions.QuerySNSApplicationPlatformAction()
    elif resource == SNS_TOPIC:
        action = api_actions.QuerySNSTopicAction()
    elif resource == SNS_TOPIC_SUBSCRIBER:
        action = api_actions.QuerySNSTopicSubscriberAction()
    elif resource == SNS_DING_TALK_ENDPOINT:
        action = api_actions.QuerySNSDingTalkEndpointAction()
    elif resource == SNS_EMAIL_ENDPOINT:
        action = api_actions.QuerySNSEmailEndpointAction()
    elif resource == SNS_EMAIL_PLATFORM:
        action = api_actions.QuerySNSEmailPlatformAction()
    elif resource == SNS_HTTP_ENDPOINT:
        action = api_actions.QuerySNSHttpEndpointAction()
    elif resource == SNS_TEXT_TEMPLATE:
        action = api_actions.QuerySNSTextTemplateAction()
    elif resource == AFFINITY_GROUP:
        action = api_actions.QueryAffinityGroupAction()
    elif resource == IAM2_ORGANIZATION:
        action = api_actions.QueryIAM2OrganizationAction()
    elif resource == IAM2_PROJECT:
        action = api_actions.QueryIAM2ProjectAction()
    elif resource == IAM2_VIRTUAL_ID_GROUP:
        action = api_actions.QueryIAM2VirtualIDGroupAction()
    elif resource == IAM2_VIRTUAL_ID:
        action = api_actions.QueryIAM2VirtualIDAction()
    elif resource == IAM2_PROJECT_TEMPLATE:
        action = api_actions.QueryIAM2ProjectTemplateAction()
    elif resource == IAM2_VIRTUAL_ID_GROUP_ATTRIBUTE:
        action = api_actions.QueryIAM2VirtualIDGroupAttributeAction()
    elif resource == IAM2_VIRTUAL_ID_ATTRIBUTE:
        action = api_actions.QueryIAM2VirtualIDAttributeAction()
    elif resource == IAM2_PROJECT_ATTRIBUTE:
        action = api_actions.QueryIAM2ProjectAttributeAction()
    elif resource == IAM2_ORGANIZATION_ATTRIBUTE:
        action = api_actions.QueryIAM2OrganizationAttributeAction()
    elif resource == ROLE:
        action = api_actions.QueryRoleAction()
    elif resource == POLICY:
        action = api_actions.QueryPolicyAction()
    elif resource == DATACENTER:
        action = api_actions.QueryDataCenterFromLocalAction()
    elif resource == ALIYUNNAS_ACCESSGROUP:
        action = api_actions.QueryAliyunNasAccessGroupAction()
    elif resource == NAS_FILESYSTEM:
        action = api_actions.QueryNasFileSystemAction()
    elif resource == NAS_MOUNTTARGET:
        action = api_actions.QueryNasMountTargetAction()
    elif resource == STACK_TEMPLATE:
        action = api_actions.QueryStackTemplateAction()
    elif resource == RESOURCE_STACK:
        action = api_actions.QueryResourceStackAction()
    elif resource == EVENT_FROM_STACK:
        action = api_actions.QueryEventFromResourceStackAction()
    elif resource == TICKET:
        action = api_actions.QueryTicketAction()
    elif resource == TICKET_HISTORY:
        action = api_actions.QueryTicketHistoryAction()
    elif resource == QUOTA:
        action = api_actions.QueryQuotaAction()
    elif resource == CERTIFICATE:
        action = api_actions.QueryCertificateAction()
    elif resource == VOLUME_BACKUP:
        action = api_actions.QueryVolumeBackupAction()
    elif resource == IPSEC_CONNECTION:
        action = api_actions.QueryIPSecConnectionAction()
    elif resource == SCSI_LUN:
        action = api_actions.QueryScsiLunAction()
    elif resource == ISCSI_SERVER:
        action = api_actions.QueryIscsiServerAction()
    elif resource == VROUTER_OSPF_AREA:
        action = api_actions.QueryVRouterOspfAreaAction()
    elif resource == VROUTER_OSPF_NETWORK:
        action = api_actions.QueryVRouterOspfNetworkAction()
    elif resource == REPLICATIONGROUP:
        action = api_actions.QueryImageReplicationGroupAction()
    return action

def query_event_from_resource_stack(conditions = [], resource=EVENT_FROM_STACK, session_uuid=None, count='false'):
    '''
    Call Query API and return all matched resource.

    conditions could be generated by gen_query_conditions()

    If session_uuid is missing, we will create one for you and only live in 
        this API.
    '''
    action = _gen_query_action(resource, conditions)
    action.conditions = conditions
    ret = account_operations.execute_action_with_session(action, session_uuid)
    return ret

def query_resource(resource, conditions = [], session_uuid=None, count='false'):
    '''
    Call Query API and return all matched resource.

    conditions could be generated by gen_query_conditions()

    If session_uuid is missing, we will create one for you and only live in 
        this API.
    '''
    action = _gen_query_action(resource, conditions)
    action.conditions = conditions
    ret = account_operations.execute_action_with_session(action, session_uuid)
    return ret

def query_resource_count(resource, conditions = [], session_uuid=None):
    '''
    Call Query API to return the matched resource count
    When count=true, it will only return the number of matched resource
    '''
    action = _gen_query_action(resource, conditions)
    action.conditions = conditions
    action.count='true'
    account_operations.execute_action_with_session(action, session_uuid)
    return action.reply.total

def query_resource_with_num(resource, conditions = [], session_uuid=None, \
        start=0, limit=1000):
    '''
    Query matched resource and return required numbers. 
    '''
    action = _gen_query_action(resource, conditions)
    action.conditions = conditions
    action.start = start
    action.limit = limit
    ret = account_operations.execute_action_with_session(action, session_uuid)
    return ret

def query_resource_fields(resource, conditions = [], session_uuid=None, \
        fields=[], start=0, limit=1000):
    '''
    Query matched resource by returning required fields and required numbers. 
    '''
    action = _gen_query_action(resource, conditions)
    action.conditions = conditions
    action.start = start
    action.limit = limit
    action.fields = fields
    ret = account_operations.execute_action_with_session(action, session_uuid)
    return ret

def get_resource(resource, session_uuid=None, uuid=None, name=None):
    if uuid:
        cond = gen_query_conditions('uuid', '=', uuid)
    elif name:
        cond = gen_query_conditions('name', '=', name)
    else:
        cond = gen_query_conditions('uuid', '!=', 'NULL')

    return query_resource(resource, cond, session_uuid)

    #if GET_RESOURCE_METHOD == LIST_RESOURCE_METHOD:
    #    return list_resource(resource, session_uuid, uuid=uuid, name=name)
    #elif GET_RESOURCE_METHOD == GET_RESOURCE_METHOD_BY_GET:
    #    if not uuid:
    #        raise Exception('Get_Resource function error, uuid can not be None')
    #    return get_resource_by_get(resource, session_uuid, uuid=uuid)
    #else:
    #    return search_resource(resource, session_uuid, uuid=uuid, name=name)

def safely_get_resource(res_name, cond = [], session_uuid = None, \
        fields = None, limit = 100):
    '''
    If there are a lot of resource (e.g. >1k), query all of them in 1 command
    is very dangours. It might crash ZStack, when the data is huge.
    '''
    res_count = query_resource_count(res_name, cond, session_uuid)
    res_list = []
    if res_count <= limit:
        res_list = query_resource_fields(res_name, cond, session_uuid, fields)
    else:
        curr_count = 0 
        while curr_count <= res_count:
            curr_list = query_resource_with_num(res_name, cond, \
                    session_uuid, fields, start=current_count, limit = limit)
            res_list.extend(curr_list)
            curr_count += limit

    return res_list

def change_recource_owner(accountUuid, resourceUuid, session_uuid = None):
    action = api_actions.ChangeResourceOwnerAction()
    action.accountUuid = accountUuid
    action.resourceUuid = resourceUuid
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def get_resource_owner(resourceUuid, session_uuid = None):
    action = api_actions.GetResourceAccountAction()
    action.resourceUuids = resourceUuid
    ret = account_operations.execute_action_with_session(action, session_uuid)
    return ret.inventories[resourceUuid[0]].uuid

def get_task_progress(apiId, session_uuid = None):
    action = api_actions.GetTaskProgressAction()
    action.apiId = apiId
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt

def get_progress(apiId, session_uuid = None):
    action = api_actions.GetTaskProgressAction()
    action.apiId = apiId
    evt = account_operations.execute_action_with_session(action, session_uuid)
    inventories = []
    for ei in evt.inventories:
        if ei.type == 'Progress':
            inventories.append(ei)
    return inventories


def enable_change_vm_password(is_enable, resourceUuid, resourceType, session_uuid = None):
    action = api_actions.EnableChangeVmPasswordAction()
    action.enable = is_enable
    action.resourceUuid = resourceUuid
    action.resourceType = resourceType
    evt = account_operations.execute_action_with_session(action, session_uuid)
    return evt
