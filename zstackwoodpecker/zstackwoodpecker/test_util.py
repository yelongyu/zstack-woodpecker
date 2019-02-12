'''

@author: Frank
'''

import os
import time
import string
import sys
import traceback
import string
import pkgutil

import zstacklib.utils.xmlobject as xmlobject
import apibinding.inventory as inventory
import zstackwoodpecker.action_select as action_select

minus_split = '-'*10 + '\n'
action_break = '\n' + '-'*10 + '\n'
log_prefix = '      <Log>'
action_prefix = '\n   <<Action>>'
dsc_prefix = '\n  ##'
warn_prefix = '\n     !!WARN!!'

class TestError(Exception):
    '''zstack test exception'''

def raise_exeception_no_cleanup(msg):
    os.environ['WOODPECKER_NO_ERROR_CLEANUP'] = True
    raise TestError(msg)

def write_to_action_log(msg):
    case_action_log = os.environ.get('WOODPECKER_CASE_ACTION_LOG_PATH')
    if not case_action_log:
        return False
        #raise TestError('CASE_ACTION_LOG_PATH is not set in environment variable.')
    try:
        fd = open(case_action_log, 'a+')
        fd.write(msg + '\n')
    except Exception as e:
        raise e
    fd.close()

#Record test warning
def test_warn(msg):
    print_msg = '[CASE WARN]:\n%s %s \n%s' % (minus_split, msg, minus_split)
    print print_msg
    log_time = time.ctime().split()[3]
    action_msg = '%s %s [%s]\n' % (warn_prefix, msg, log_time)
    action_msg = '%s %s [%s]' % (warn_prefix, msg, log_time)
    only_action_log = os.environ.get('WOODPECKER_ONLY_ACTION_LOG')
    if not only_action_log:
        write_to_action_log(action_msg)


#Record Test Log
def test_logger(msg):
    log_time = time.ctime().split()[3]
    print_msg = '[CASE LOG]: %s\n%s %s \n%s' % (log_time, minus_split, msg, minus_split)
    print print_msg
    action_msg = '%s %s [%s]\n' % (log_prefix, msg, log_time)
    action_msg = '%s %s [%s]' % (log_prefix, msg, log_time)
    only_action_log = os.environ.get('WOODPECKER_ONLY_ACTION_LOG')
    if not only_action_log:
        write_to_action_log(action_msg)

#Record Test Result
def test_result(msg):
    print_msg = '[CASE RESULT]:\n%s %s \n%s' % (minus_split, msg, minus_split)
    print print_msg
    log_time = time.ctime().split()[3]
    action_msg = '%s<Result> %s [%s]' % (action_break, msg, log_time)
    write_to_action_log(action_msg)

def test_fail(msg, no_cleanup = False):
    '''
    No test case codes will be executed, after calling this function.
    '''
    test_logger(msg)
    test_result("Failed :(")
    if no_cleanup:
        os.environ['WOODPECKER_NO_ERROR_CLEANUP'] = True
    raise TestError(msg)

def test_pass(msg):
    '''
    No test case codes will be executed, after calling this function.
    '''
    test_logger(msg)
    test_result("Pass :)")
    sys.exit(0)

def test_skip(msg):
    '''
    No test case codes will be executed, after calling this function.
    '''
    test_logger(msg)
    test_result("Skipped")
    sys.exit(2)

def test_env_not_ready(msg):
    '''
    No test case codes will be executed, after calling this function.
    '''
    test_logger(msg)
    test_result("Env not ready")
    sys.exit(3)

#Record Action Log
def action_logger(msg):
    print_msg = '[ACTION LOG]:\n%s %s \n%s' % (minus_split, msg, minus_split)
    print print_msg
    log_time = time.ctime().split()[3]
    action_msg = '%s %s [%s]\n' % (action_prefix, msg, log_time)
    write_to_action_log(action_msg)

#Test description
def test_dsc(msg):
    print_msg = '[Test DSC]:\n%s %s \n%s' % (minus_split, msg, minus_split)
    print print_msg
    action_msg = '%s %s\n' % (dsc_prefix, msg)
    write_to_action_log(action_msg)

class TestConfig(object):
    def __init__(self, config_path):
        self.config_path = config_path
        if not config_path:
            raise TestError('Test config file (test-config.xml) path is not set')
        self.config_base_path = os.path.dirname(os.path.abspath(config_path))
        self.deploy_config_template_path = None

    def _full_path(self, path):
        if path.startswith('~'):
            return os.path.expanduser(path)
        elif path.startswith('/'):
            return path
        else:
            return os.path.join(self.config_base_path, path)

    def get_test_config(self):
        cfg_path = os.path.abspath(self.config_path)
        with open(cfg_path, 'r') as fd:
            xmlstr = fd.read()
            fd.close()
            config = xmlobject.loads(xmlstr)
            return config

    def get_deploy_config(self):
        config = self.get_test_config()

        deploy_config_template_path = config.get('deployConfigTemplate')
        if deploy_config_template_path:
            deploy_config_template_path = self._full_path(deploy_config_template_path)
            if not os.path.exists(deploy_config_template_path):
                raise TestError('unable to find %s' % deploy_config_template_path)
            self.deploy_config_template_path = deploy_config_template_path
        else:
            raise TestError('not define test deploy config xml file by <deployConfigTemplate> in: %s' % self.config_path)
    
        deploy_config_path = self._full_path(config.deployConfig.text_)
        if not os.path.exists(deploy_config_path):
            raise TestError('unable to find %s' % deploy_config_path)
    
        if deploy_config_template_path:
            deploy_config = build_deploy_xmlobject_from_configure(deploy_config_path, deploy_config_template_path)
            deploy_config.put_attr('deployConfigTemplatePath', deploy_config_template_path)
        else:
            deploy_config = build_deploy_xmlobject_from_configure(deploy_config_path)

        deploy_config.put_attr('deployConfigPath', deploy_config_path)
        return deploy_config

    def expose_config_variable(self):
        if self.deploy_config_template_path:
            set_env_var_from_config_template(self.deploy_config_template_path)

class TestScenario(object):
    def __init__(self, config_path):
        self.config_path = config_path
        if not config_path:
            raise TestError('Test config file (test-config.xml) path is not set')
        self.config_base_path = os.path.dirname(os.path.abspath(config_path))
        self.deploy_config_template_path = None

    def _full_path(self, path):
        if path.startswith('~'):
            return os.path.expanduser(path)
        elif path.startswith('/'):
            return path
        else:
            return os.path.join(self.config_base_path, path)

    def get_test_config(self):
        cfg_path = os.path.abspath(self.config_path)
        with open(cfg_path, 'r') as fd:
            xmlstr = fd.read()
            fd.close()
            config = xmlobject.loads(xmlstr)
            return config

    def get_scenario_config(self):
        config = self.get_test_config()

        scenario_config_template_path = config.get('scenarioConfigTemplate')
        if scenario_config_template_path:
            scenario_config_template_path = self._full_path(scenario_config_template_path)
            if not os.path.exists(scenario_config_template_path):
                raise TestError('unable to find %s' % scenario_config_template_path)
            self.scenario_config_template_path = scenario_config_template_path
        else:
            raise TestError('not define test scenario config xml file by <scenarioConfigTemplate> in: %s' % self.config_path)
    
        scenario_config_path = self._full_path(config.scenarioConfig.text_)
        if not os.path.exists(scenario_config_path):
            raise TestError('unable to find %s' % scenario_config_path)
    
        if scenario_config_template_path:
            scenario_config = build_deploy_xmlobject_from_configure(scenario_config_path, scenario_config_template_path)
            scenario_config.put_attr('scenarioConfigTemplatePath', scenario_config_template_path)
        else:
            scenario_config = build_deploy_xmlobject_from_configure(scenario_config_path)

        scenario_config.put_attr('scenarioConfigPath', scenario_config_path)
        return scenario_config

    def expose_config_variable(self):
        if self.scenario_config_template_path:
            set_env_var_from_config_template(self.scenario_config_template_path)

class DataOption(object):
    def __init__(self):
        self.session_uuid = None
        self.timeout = 300000   #5 mins
        self.name = None
        self.ipVersion = None
        self.description = None
        self.resourceUUID = None
        #system tag is an array
        self.system_tags = None
        self.user_tags = None
        self.session_uuid = None

    def set_session_uuid(self, session_uuid):
        self.session_uuid = session_uuid

    def get_session_uuid(self):
        return self.session_uuid

    def set_name(self, name):
        self.name = name

    def set_ipVersion(self, ipVersion):
        self.ipVersion = ipVersion

    def get_ipVersion(self):
        return self.ipVersion

    def get_name(self):
        return self.name

    def set_description(self, description):
        self.description = description

    def get_description(self):
        return self.description

    def set_timeout(self, timeout):
        self.timeout = timeout

    def get_timeout(self):
        return self.timeout

    def set_resource_uuid(self, resourceUUID):
        self.resourceUUID = resourceUUID

    def get_resource_uuid(self):
        return self.resourceUUID

    def set_system_tags(self, system_tags):
        if not system_tags:
            self.system_tags = []
            return 

        if not isinstance(system_tags, list):
            raise TestError('system_tags is not a list.')
        self.system_tags = system_tags

    def get_system_tags(self):
        return self.system_tags

    def set_user_tags(self, user_tags):
        if not user_tags:
            self.user_tags = []
            return 

        if not isinstance(user_tags, list):
            raise TestError('user_tags is not a list.')
        self.user_tags = user_tags

    def get_user_tags(self):
        return self.user_tags

class ZoneOption(DataOption):
    def __init__(self):
        super(ZoneOption, self).__init__()

class ClusterOption(DataOption):
    def __init__(self):
        self.hypervisor_type = None
        self.type = 'zstack'
        self.zone_uuid = None
        super(ClusterOption, self).__init__()

    def set_hypervisor_type(self, hypervisor_type):
        self.hypervisor_type = hypervisor_type

    def get_hypervisor_type(self):
        return self.hypervisor_type

    def set_type(self, type):
        self.type = type

    def get_type(self):
        return self.type

    def set_zone_uuid(self, zone_uuid):
        self.zone_uuid = zone_uuid

    def get_zone_uuid(self):
        return self.zone_uuid

class IpRangeOption(DataOption):
    def __init__(self):
        self.l3_uuid = None
        self.startIp = None
        self.endIp = None
        self.gateway = None
        self.netmask = None
        super(IpRangeOption, self).__init__()

    def set_l3_uuid(self, l3_uuid):
        self.l3_uuid = l3_uuid

    def get_l3_uuid(self):
        return self.l3_uuid

    def set_startIp(self, startIp):
        self.startIp = startIp

    def get_startIp(self):
        return self.startIp

    def set_endIp(self, endIp):
        self.endIp = endIp

    def get_endIp(self):
        return self.endIp

    def set_gateway(self, gateway):
        self.gateway = gateway

    def get_gateway(self):
        return self.gateway

    def set_netmask(self, netmask):
        self.netmask = netmask

    def get_netmask(self):
        return self.netmask

class IpV6RangeOption(DataOption):
    def __init__(self):
        self.l3_uuid = None
        self.startIp = None
        self.endIp = None
        self.gateway = None
        self.netmask = None
        self.addressMode = None
	self.prefixLen = None
        super(IpV6RangeOption, self).__init__()

    def set_l3_uuid(self, l3_uuid):
        self.l3_uuid = l3_uuid

    def get_l3_uuid(self):
        return self.l3_uuid

    def set_startIp(self, startIp):
        self.startIp = startIp

    def get_startIp(self):
        return self.startIp

    def set_endIp(self, endIp):
        self.endIp = endIp

    def get_endIp(self):
        return self.endIp

    def set_gateway(self, gateway):
        self.gateway = gateway

    def get_gateway(self):
        return self.gateway

    def set_netmask(self, netmask):
        self.netmask = netmask

    def get_netmask(self):
        return self.netmask

    def set_addressMode(self, addressMode):
        self.addressMode = addressMode

    def get_addressMode(self):
        return self.addressMode
  
    def set_prefixLen(self, prefixLen):
        self.prefixLen = prefixLen

    def get_prefixLen(self):
        return self.prefixLen

class Ip_By_NetworkCidrOption(DataOption):
    def __init__(self):
        self.l3_uuid = None
        self.networkCidr = None
        super(Ip_By_NetworkCidrOption, self).__init__()

    def set_l3_uuid(self, l3_uuid):
        self.l3_uuid = l3_uuid

    def get_l3_uuid(self):
        return self.l3_uuid

    def set_networkCidr(self, networkCidr):
        self.networkCidr = networkCidr
	
    def get_networkCidr(self):
        return self.networkCidr

class IpV6_By_NetworkCidrOption(DataOption):
    def __init__(self):
        self.l3_uuid = None
        self.networkCidr = None
        self.addressMode = None
        super(IpV6_By_NetworkCidrOption, self).__init__()

    def set_l3_uuid(self, l3_uuid):
        self.l3_uuid = l3_uuid

    def get_l3_uuid(self):
        return self.l3_uuid

    def set_networkCidr(self, networkCidr):
        self.networkCidr = networkCidr

    def get_networkCidr(self):
        return self.networkCidr

    def set_addressMode(self, addressMode):
        self.addressMode = addressMode

    def get_addressMode(self):
        return self.addressMode

class VipOption(DataOption):
    def __init__(self):
        self.l3_uuid = None
        self.allocateStrategy = None
        self.requiredIp = None
        super(VipOption, self).__init__()

    def set_l3_uuid(self, l3_uuid):
        self.l3_uuid = l3_uuid

    def get_l3_uuid(self):
        return self.l3_uuid

    def set_allocateStrategy(self, strategy):
        self.allocateStrategy = strategy

    def get_allocateStrategy(self):
        return self.allocateStrategy

    def set_requiredIp(self, required_ip):
        self.requiredIp = required_ip

    def get_requiredIp(self):
        return self.requiredIp

class PrimaryStorageOption(DataOption):
    def __init__(self):
        self.type = None
        self.url = None
        self.zone_uuid = None
        super(PrimaryStorageOption, self).__init__()

    def set_type(self, type):
        self.type = type

    def get_type(self):
        return self.type

    def set_zone_uuid(self, zone_uuid):
        self.zone_uuid = zone_uuid

    def get_zone_uuid(self):
        return self.zone_uuid

    def set_url(self, url):
        self.url = url

    def get_url(self):
        return self.url

class CephPrimaryStorageOption(PrimaryStorageOption):
    def __init__(self):
        self.monUrls = None
        self.dataVolumePoolName = None
        self.rootVolumePoolName = None
        self.imageCachePoolName = None
        super(CephPrimaryStorageOption, self).__init__()
        self.type = inventory.CEPH_PRIMARY_STORAGE_TYPE

    def set_monUrls(self, monUrls):
        self.monUrls = monUrls

    def get_monUrls(self):
        return self.monUrls

    def set_imageCachePoolName(self, imageCachePoolName):
        self.imageCachePoolName = imageCachePoolName

    def get_imageCachePoolName(self):
        return self.imageCachePoolName

    def set_dataVolumePoolName(self, dataVolumePoolName):
        self.dataVolumePoolName = dataVolumePoolName

    def get_dataVolumePoolName(self):
        return self.dataVolumePoolName

    def set_rootVolumePoolName(self, rootVolumePoolName):
        self.rootVolumePoolName = rootVolumePoolName

    def get_rootVolumePoolName(self):
        return self.rootVolumePoolName

class BackupStorageOption(DataOption):
    def __init__(self):
        self.type = None
        self.url = None
        self.importImages = None
        super(BackupStorageOption, self).__init__()

    def set_type(self, type):
        self.type = type

    def get_type(self):
        return self.type

    def set_url(self, url):
        self.url = url

    def get_url(self):
        return self.url

    def set_import_images(self, import_images):
        self.importImages = import_images

    def get_import_images(self):
        return self.importImages

    def get_hostname(self):
        return self.hostname

    def get_username(self):
        return self.username

    def get_password(self):
        return self.password

    def get_url(self):
        return self.url

    def get_sshPort(self):
        return self.sshPort


class CephBackupStorageOption(BackupStorageOption):
    def __init__(self):
        self.monUrls = None
        self.dataVolumePoolName = None
        self.rootVolumePoolName = None
        self.imageCachePoolName = None
        super(CephBackupStorageOption, self).__init__()
        self.type = inventory.CEPH_BACKUP_STORAGE_TYPE

    def set_monUrls(self, monUrls):
        self.monUrls = monUrls

    def get_monUrls(self):
        return self.monUrls

    def set_imageCachePoolName(self, imageCachePoolName):
        self.imageCachePoolName = imageCachePoolName

    def get_imageCachePoolName(self):
        return self.imageCachePoolName

    def set_dataVolumePoolName(self, dataVolumePoolName):
        self.dataVolumePoolName = dataVolumePoolName

    def get_dataVolumePoolName(self):
        return self.dataVolumePoolName

    def set_rootVolumePoolName(self, rootVolumePoolName):
        self.rootVolumePoolName = rootVolumePoolName

    def get_rootVolumePoolName(self):
        return self.rootVolumePoolName

class SftpBackupStorageOption(BackupStorageOption):
    def __init__(self):
        self.username = None
        self.hostname = None
        self.password = None
        self.sshPort = None
        super(SftpBackupStorageOption, self).__init__()
        self.type = inventory.SFTP_BACKUP_STORAGE_TYPE

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def set_url(self, url):
        self.url = url

    def get_url(self):
        return self.url

    def set_hostname(self, ip):
        self.hostname = ip
    
    def get_hostname(self):
        return self.hostname
    
    def set_username(self, username):
        self.username = username

    def get_username(self):
        return self.username

    def set_password(self, password):
        self.password = password

    def get_password(self):
        return self.password

    def set_sshPort(self, port):
        self.sshPort = port

    def get_sshPort(self):
        return self.sshPort

class ImageStoreBackupStorageOption(BackupStorageOption):
    def __init__(self):
        self.username = None
        self.hostname = None
        self.password = None
        self.sshPort = None
        super(ImageStoreBackupStorageOption, self).__init__()
        self.type = inventory.SFTP_BACKUP_STORAGE_TYPE

    def set_hostname(self, ip):
        self.hostname = ip
    
    def get_hostname(self):
        return self.hostname
    
    def set_username(self, username):
        self.username = username

    def get_username(self):
        return self.username

    def set_password(self, password):
        self.password = password

    def get_password(self):
        return self.password

    def set_sshPort(self, port):
        self.sshPort = port

    def get_sshPort(self):
        return self.sshPort

class DiskOfferingOption(DataOption):
    def __init__(self):
        self.diskSize = None
        self.allocatorStrategy = None
        self.type = None
        super(DiskOfferingOption, self).__init__()

    def set_diskSize(self, diskSize):
        self.diskSize = diskSize

    def get_diskSize(self):
        return self.diskSize

    def set_allocatorStrategy(self, allocatorStrategy):
        self.allocatorStrategy = allocatorStrategy

    def get_allocatorStrategy(self):
        return self.allocatorStrategy

    def set_type(self, type):
        self.type = type

    def get_type(self):
        return self.type

class InstanceOfferingOption(DataOption):
    def __init__(self):
        self.cpuNum = None
        #self.cpuSpeed = None
        self.memorySize = None
        self.allocatorStrategy = None
        self.type = None
        super(InstanceOfferingOption, self).__init__()

    def set_cpuNum(self, cpuNum):
        self.cpuNum = cpuNum

    def get_cpuNum(self):
        return self.cpuNum

    #def set_cpuSpeed(self, cpuSpeed):
    #    self.cpuSpeed = cpuSpeed

    #def get_cpuSpeed(self):
    #    return self.cpuSpeed

    def set_memorySize(self, memorySize):
        self.memorySize = memorySize

    def get_memorySize(self):
        return self.memorySize

    def set_allocatorStrategy(self, allocatorStrategy):
        self.allocatorStrategy = allocatorStrategy

    def get_allocatorStrategy(self):
        return self.allocatorStrategy

    def set_type(self, type):
        self.type = type

    def get_type(self):
        return self.type

class VmOption(DataOption):
    def __init__(self, vm_opt = None):
        if not vm_opt:
            self.l3_uuids = None
            self.image_uuid = None
            self.instance_offering_uuid = None
            self.vm_type = None
            self.host_uuid = None
            self.cluster_uuid = None
            self.zone_uuid = None
            self.data_disk_uuids = None
            self.default_l3_uuid = None
            self.root_disk_uuid = None
            self.user_tags = None
            self.console_password = None
            self.ps_uuid = None
            self.root_password = None
            self.rootVolumeSystemTags = None
            self.dataVolumeSystemTags = None
            self.strategy_type = 'InstantStart'
            super(VmOption, self).__init__()
        else:
            self.l3_uuids = vm_opt.get_l3_uuids()
            self.image_uuid = vm_opt.get_image_uuid()
            self.instance_offering_uuid = vm_opt.get_instance_offering_uuid()
            self.vm_type = vm_opt.get_vm_type()
            self.host_uuid = vm_opt.get_host_uuid()
            self.cluster_uuid = vm_opt.get_cluster_uuid()
            self.zone_uuid = vm_opt.get_zone_uuid()
            self.data_disk_uuids = vm_opt.get_data_disk_uuids()
            self.root_disk_uuid = None
            self.set_name(vm_opt.get_name())
            self.set_description(vm_opt.get_description())
            self.set_timeout(vm_opt.get_timeout())
            self.set_console_password(vm_opt.get_console_password())
            self.ps_uuid = vm_opt.get_ps_uuid()
            self.root_password = vm_opt.get_root_password()
            self.default_l3_uuid = vm_opt.get_default_l3_uuid()
            self.system_tags = vm_opt.get_system_tags()
            self.user_tags = vm_opt.get_user_tags()
            self.strategy_type = vm_opt.get_strategy_type()
            self.rootVolumeSystemTags = vm_opt.get_rootVolume_systemTags()
            self.dataVolumeSystemTags = vm_opt.get_dataVolume_systemTags()
            super(VmOption, self).__init__()

    def set_l3_uuids(self, l3_uuids):
        if not isinstance(l3_uuids, list):
            raise TestError('l3_uuids is not a list.')
        self.l3_uuids = l3_uuids

    def get_l3_uuids(self):
        return self.l3_uuids

    def set_user_tags(self, user_tags):
        if not user_tages:
            self.user_tags = []
            return 

        if not isinstance(user_tags, list):
            raise TestError('user_tags is not a list.')
        self.user_tags = user_tags

    def get_user_tags(self):
        return self.user_tags

    def set_default_l3_uuid(self, l3_uuid):
        self.default_l3_uuid = l3_uuid

    def get_default_l3_uuid(self):
        return self.default_l3_uuid

    def set_root_disk_uuid(self, disk_uuid):
        self.root_disk_uuid = disk_uuid

    def set_console_password(self, console_password):
        self.console_password = console_password

    def get_console_password(self):
        return self.console_password

    def get_root_disk_uuid(self):
        return self.root_disk_uuid

    def set_zone_uuid(self, zone_uuid):
        self.zone_uuid = zone_uuid

    def get_zone_uuid(self):
        return self.zone_uuid

    def set_image_uuid(self, image_uuid):
        self.image_uuid = image_uuid

    def get_image_uuid(self):
        return self.image_uuid

    def set_cluster_uuid(self, cluster_uuid):
        self.cluster_uuid = cluster_uuid

    def get_cluster_uuid(self):
        return self.cluster_uuid

    def set_host_uuid(self, host_uuid):
        self.host_uuid = host_uuid

    def get_host_uuid(self):
        return self.host_uuid

    def set_instance_offering_uuid(self, instance_offering_uuid):
        self.instance_offering_uuid = instance_offering_uuid

    def get_instance_offering_uuid(self):
        return self.instance_offering_uuid

    def set_vm_type(self, vm_type):
        self.vm_type = vm_type

    def get_vm_type(self):
        return self.vm_type

    def set_data_disk_uuids(self, data_disk_uuids):
        self.data_disk_uuids = data_disk_uuids

    def get_data_disk_uuids(self):
        return self.data_disk_uuids

    def set_ps_uuid(self, ps_uuid):
        self.ps_uuid = ps_uuid

    def get_ps_uuid(self):
        return self.ps_uuid

    def set_root_password(self, root_password):
        self.root_password = root_password

    def get_root_password(self):
        return self.root_password

    def set_strategy_type(self, strategy_type):
        self.strategy_type = strategy_type

    def get_strategy_type(self):
        return self.strategy_type

    def set_rootVolume_systemTags(self, rootVolume_systemTags):
        self.rootVolumeSystemTags = rootVolume_systemTags

    def get_rootVolume_systemTags(self):
        return self.rootVolumeSystemTags

    def set_dataVolume_systemTags(self, dataVolume_systemTags):
        self.dataVolumeSystemTags = dataVolume_systemTags

    def get_dataVolume_systemTags(self):
        return self.dataVolumeSystemTags

class VolumeOption(DataOption):
    def __init__(self):
        self.disk_offering_uuid = None #used when create volume from template
        self.url = None #used when add volume from url.
        self.volume_type = None #used when add volume from url
        self.primary_storage_uuid = None #used when add volume from url
        self.system_tags = None
        super(VolumeOption, self).__init__()

    def set_disk_offering_uuid(self, disk_offering_uuid):
        self.disk_offering_uuid = disk_offering_uuid

    def get_disk_offering_uuid(self):
        return self.disk_offering_uuid

    def set_volume_template_uuid(self, volume_template_uuid):
        self.volume_template_uuid = volume_template_uuid

    def get_volume_template_uuid(self):
        return self.volume_template_uuid

    def set_primary_storage_uuid(self, primary_storage_uuid):
        self.primary_storage_uuid = primary_storage_uuid

    def get_primary_storage_uuid(self):
        return self.primary_storage_uuid

    def set_url(self, url):
        self.url = url

    def get_url(self):
        return self.url

    def set_volume_type(self, volume_type):
        self.volume_type = volume_type

    def get_volume_type(self):
        return self.volume_type

    def set_system_tags(self, system_tags):
        self.system_tags = system_tags

    def get_system_tags(self):
        return self.system_tags


class ImageOption(DataOption):
    def __init__(self):
        self.root_volume_uuid = None #for create template from root volume
        self.data_volume_uuid = None #for create template from data volume
        self.backup_storage_uuid_list = [] #
        self.guest_os_type = None #CentOS7
        self.platform = None #Linux, Windows, Unknown
        self.bits = None #64/32
        self.url = None #http:// for add a new image
        self.mediaType = None #Template, ISO
        self.format = None #qcow/raw for KVM, simulator, 
        self.system = None #used for system image
        self.system_tags = None #used for system tags
        self.uuid = None
        super(ImageOption, self).__init__()

    def set_uuid(self, uuid):
        self.uuid = uuid

    def get_uuid(self):
        return self.uuid

    def set_root_volume_uuid(self, root_volume_uuid):
        self.root_volume_uuid = root_volume_uuid

    def set_data_volume_uuid(self, data_volume_uuid):
        self.data_volume_uuid = data_volume_uuid

    def get_root_volume_uuid(self):
        return self.root_volume_uuid

    def get_data_volume_uuid(self):
        return self.data_volume_uuid

    def set_backup_storage_uuid_list(self, backup_storage_uuid_list):
        self.backup_storage_uuid_list = backup_storage_uuid_list

    def get_backup_storage_uuid_list(self):
        return self.backup_storage_uuid_list

    def set_guest_os_type(self, guest_os_type):
        self.guest_os_type = guest_os_type

    def get_guest_os_type(self):
        return self.guest_os_type

    def set_bits(self, bits):
        self.bits = bits

    def get_bits(self):
        return self.bits

    def set_platform(self, platform):
        self.platform = platform

    def get_platform(self):
        return self.platform

    def set_system(self, system):
        self.system = system

    def get_system(self):
        return self.system

    def set_system_tags(self, system_tags):
        self.system_tags = system_tags

    def get_system_tags(self):
        return self.system_tags

    def set_url(self, url):
        self.url = url

    def get_url(self):
        return self.url

    def set_mediaType(self, mediaType):
        self.mediaType = mediaType

    def get_mediaType(self):
        return self.mediaType

    def set_format(self, img_format):
        self.format = img_format

    def get_format(self):
        return self.format

class NodeOption(DataOption):
    def __init__(self):
        super(NodeOption, self).__init__()
        self.managementIp = None
        self.username = None
        self.password = None
        self.dockerImage = None

    def set_management_ip(self, ip):
        self.managementIp = ip
    
    def get_management_ip(self):
        return self.managementIp
    
    def set_username(self, username):
        self.username = username

    def get_username(self):
        return self.username

    def set_password(self, password):
        self.password = password

    def get_password(self):
        return self.password

    def set_docker_image(self, docker_image):
        self.dockerImage = docker_image

    def get_docker_image(self):
        return self.dockerImage
        
class HostOption(DataOption):
    def __init__(self):
        super(HostOption, self).__init__()
        self.uuid = None
        self.managementIp = None
        self.clusterUuid = None
        self.username = None
        self.password = None
        self.hostTags = None
        self.sshPort = None
        #for salt minion specific id, which is not /etc/machine_id. e.g. VMs, 
        # which use same test image template and have same machine_id. 
        #self.machine_id = None

    def set_sshPort(self, port):
        self.sshPort = port

    def get_sshPort(self):
        return self.sshPort

    def set_management_ip(self, ip):
        self.managementIp = ip
    
    def get_management_ip(self):
        return self.managementIp
    
    def set_cluster_uuid(self, uuid):
        self.clusterUuid = uuid

    def get_cluster_uuid(self):
        return self.clusterUuid

    def set_username(self, username):
        self.username = username

    def get_username(self):
        return self.username

    def set_password(self, password):
        self.password = password

    def get_password(self):
        return self.password

    def set_host_tages(self, host_tags):
        self.hostTags = host_tags

    def get_host_tags(self):
        return self.hostTags

class SnapshotOption(DataOption):
    def __init__(self):
        super(SnapshotOption, self).__init__()
        self.volume_uuid = None

    def set_volume_uuid(self, volume_uuid):
        self.volume_uuid = volume_uuid

    def get_volume_uuid(self):
        return self.volume_uuid

class BackupOption(DataOption):
    def __init__(self):
        super(BackupOption, self).__init__()
        self.volume_uuid = None
        self.backupStorage_uuid = None

    def set_volume_uuid(self, volume_uuid):
        self.volume_uuid = volume_uuid

    def get_volume_uuid(self):
        return self.volume_uuid

    def set_backupStorage_uuid(self, bs_uuid):
        self.backupStorage_uuid = bs_uuid

    def get_backupStorage_uuid(self):
        return self.backupStorage_uuid

class SecurityGroupOption(DataOption):
    def __init__(self):
        self.name = None
        self.ipVersion = None
        super(SecurityGroupOption, self).__init__()

    def set_name(self, name):
        self.name = name
    def set_ipVersion(self, ipVersion):
        self.ipVersion = ipVersion

    def get_name(self):
        return self.name
    def get_ipVersion(self):
        return self.ipVersion


class LoadBalancerListenerOption(DataOption):
    def __init__(self, lb_uuid = None, instance_port = None, \
            protocol = None, name = None, system_tags = None, \
            load_balancer_port = None):
        self.load_balancer_uuid = lb_uuid
        self.instance_port = instance_port
        self.load_balancer_port = load_balancer_port
        self.protocol = protocol
        self.system_tags = system_tags
        super(LoadBalancerListenerOption, self).__init__()
        self.name = name

    def set_load_balancer_uuid(self, load_balancer_uuid):
        self.load_balancer_uuid = load_balancer_uuid

    def get_load_balancer_uuid(self):
        return self.load_balancer_uuid

    def set_load_balancer_port(self, load_balancer_port):
        self.load_balancer_port = load_balancer_port
        if not self.instance_port:
            self.set_instance_port(load_balancer_port)

    def get_load_balancer_port(self):
        return self.load_balancer_port

    def set_instance_port(self, instance_port):
        self.instance_port = instance_port
        if not self.load_balancer_port:
            self.set_load_balancer_port(instance_port)

    def get_instance_port(self):
        return self.instance_port

    def set_protocol(self, protocol):
        self.protocol = protocol

    def get_protocol(self):
        return self.protocol

class PortForwardingRuleOption(DataOption):
    def __init__(self, vip_startPort=None, vip_endPort=None, private_startPort=None, private_endPort=None, protocol=None, allowedCidr=None, vip_uuid=None, vm_nic_uuid=None):
        self.vip_startPort = vip_startPort
        self.vip_endPort = vip_endPort
        self.private_startPort = private_startPort
        self.private_endPort = private_endPort
        self.protocol = protocol
        self.allowedCidr = allowedCidr
        self.vip_uuid = vip_uuid
        self.vm_nic_uuid = vm_nic_uuid
        super(PortForwardingRuleOption, self).__init__()

    def set_vip_ports(self, startPort, endPort):
        self.vip_startPort = startPort
        self.vip_endPort = endPort

    def get_vip_ports(self):
        return self.vip_startPort, self.vip_endPort

    def set_private_ports(self, startPort, endPort):
        self.private_startPort = startPort
        self.private_endPort = endPort

    def get_private_ports(self):
        return self.private_startPort, self.private_endPort

    def set_protocol(self, protocol):
        self.protocol = protocol

    def get_protocol(self):
        return self.protocol

    def set_allowedCidr(self, address):
        self.allowedCidr = address

    def get_allowedCidr(self):
        return self.allowedCidr

    def set_vip_uuid(self, vip_uuid):
        self.vip_uuid = vip_uuid

    def get_vip_uuid(self):
        return self.vip_uuid

    def set_vm_nic_uuid(self, vm_nic_uuid):
        self.vm_nic_uuid = vm_nic_uuid

    def get_vm_nic_uuid(self):
        return self.vm_nic_uuid

class EipOption(DataOption):
    def __init__(self):
        super(EipOption, self).__init__()
        self.vip = None
        self.vmNicUuid = None

    def set_vip_uuid(self, vip_uuid):
        self.vip_uuid = vip_uuid

    def get_vip_uuid(self):
        return self.vip_uuid

    def set_vm_nic_uuid(self, vm_nic_uuid):
        self.vmNicUuid = vm_nic_uuid

    def get_vm_nic_uuid(self):
        return self.vmNicUuid

class ChassisOption(DataOption):
    def __init__(self):
        self.ipmiAddress = None
        self.ipmiUsername = None
        self.ipmiPassword = None
        self.ipmiPort = 623
        self.clusterUuid = None
        super(ChassisOption, self).__init__()

    def set_ipmi_address(self, ipmiAddress):
        self.ipmiAddress = ipmiAddress

    def get_ipmi_address(self):
        return self.ipmiAddress

    def set_ipmi_username(self, ipmiUsername):
        self.ipmiUsername = ipmiUsername

    def get_ipmi_username(self):
        return self.ipmiUsername

    def set_ipmi_password(self, ipmiPassword):
        self.ipmiPassword = ipmiPassword

    def get_ipmi_password(self):
        return self.ipmiPassword

    def set_ipmi_port(self, ipmiPort):
        self.ipmiPort = ipmiPort

    def get_ipmi_port(self):
        return self.ipmiPort

    def set_cluster_uuid(self, clusterUuid):
        self.clusterUuid = clusterUuid

    def get_cluster_uuid(self):
        return self.clusterUuid

class BaremetalInstanceOption(DataOption):
    def __init__(self):
        self.chassisUuid = None
        self.imageUuid = None
        self.password = 'password'
        self.nicCfgs = None
        self.strategy = None
        super(BaremetalInstanceOption, self).__init__()

    def set_chassis_uuid(self, chassisUuid):
        self.chassisUuid = chassisUuid

    def get_chassis_uuid(self):
        return self.chassisUuid

    def set_image_uuid(self, imageUuid):
        self.imageUuid = imageUuid

    def get_image_uuid(self):
        return self.imageUuid

    def set_password(self, password):
        self.password = password

    def get_password(self):
        return self.password

    def set_nic_cfgs(self, nicCfgs):
        self.nicCfgs = nicCfgs

    def get_nic_cfgs(self):
        return self.nicCfgs

    def set_strategy(self, strategy):
        relf.strategy = strategy

    def get_strategy(self):
        return self.strategy

class StackTemplateOption(DataOption):
    def __init__(self):
        self.type = "zstack"
        self.name = None
        self.description = None
        self.templateContent = None
        self.url = None
        self.state = None
        super(StackTemplateOption, self).__init__()

    def set_state(self, state):
        self.state = state
    def get_state(self):
        return self.state
    def set_name(self, name):
        self.name = name
    def get_name(self):
        return self.name
    def set_description(self, description):
        self.description = description
    def get_description(self):
        return self.description
    def set_templateContent(self, templateContent):
        self.templateContent = templateContent
    def get_templateContent(self):
        return self.templateContent
    def set_url(self, url):
        self.url = url
    def get_url(self):
        return self.url

class ResourceStackOption(DataOption):
    def __init__(self):
        self.name = None
        self.description = None
        self.type = "zstack"
        self.rollback = False
        self.templateContent = None
        self.templateUuid = None
        self.parameters = None
        self.uuid = None
        super(ResourceStackOption, self).__init__()

    def get_type(self):
        return self.type
    def set_name(self, name):
        self.name = name
    def get_name(self):
        return self.name
    def set_templateContent(self, templateContent):
        self.templateContent = templateContent
    def get_templateContent(self):
        return self.templateContent
    def set_description(self, description):
        self.description = description
    def get_description(self):
        return self.description
    def set_rollback(self, rollback):
        self.rollback = rollback
    def get_rollback(self):
        return self.rollback
    def set_template_uuid(self, template_uuid):
        self.templateUuid = template_uuid
    def get_template_uuid(self):
        return self.templateUuid
    def set_parameters(self, parameters):
        self.parameters = parameters
    def get_parameters(self):
        return self.parameters
    def set_uuid(self, uuid):
        self.uuid = uuid
    def get_uuid(self):
        return self.uuid

class PxeOption(DataOption):
    def __init__(self):
        self.dhcpInterface = None
        self.dhcpRangeBegin = None
        self.dhcpRangeEnd = None
        self.dhcpRangeNetmask = None
        self.hostname = None
        self.storagePath = None
        self.sshUsername = None
        self.sshPassword = None
        self.sshPort = None
        self.zoneUuid = None
        super(PxeOption, self).__init__()

    def set_dhcp_interface(self, dhcpInterface):
        self.dhcpInterface = dhcpInterface

    def get_dhcp_interface(self):
        return self.dhcpInterface

    def set_dhcp_range_begin(self, dhcpRangeBegin):
        self.dhcpRangeBegin = dhcpRangeBegin

    def get_dhcp_range_begin(self):
        return self.dhcpRangeBegin

    def set_dhcp_range_end(self, dhcpRangeEnd):
        self.dhcpRangeEnd = dhcpRangeEnd

    def get_dhcp_range_end(self):
        return self.dhcpRangeEnd

    def set_dhcp_netmask(self, dhcpRangeNetmask):
        self.dhcpRangeNetmask = dhcpRangeNetmask

    def get_dhcp_netmask(self):
        return self.dhcpRangeNetmask

    def set_hostname(self, hostname):
        self.hostname = hostname

    def get_hostname(self):
        return self.hostname

    def set_storagePath(self, storagePath):
        self.storagePath = storagePath

    def get_storagePath(self):
        return self.storagePath

    def set_sshUsername(self, sshUsername):
        self.sshUsername = sshUsername

    def get_sshUsername(self):
        return self.sshUsername

    def set_sshPassword(self, sshPassword):
        self.sshPassword = sshPassword

    def get_sshPassword(self):
        return self.sshPassword

    def set_sshPort(self, sshPort):
        self.sshPort = sshPort

    def get_sshPort(self):
        return self.sshPort

    def set_zoneUuid(self, zoneUuid):
        self.zoneUuid = zoneUuid

    def get_zoneUuid(self):
        return self.zoneUuid

class BaremetalHostCfgOption(DataOption):
    def __init__(self):
        self.chassisUuid = None
        self.password = "password"
        self.unattended = "True"
        self.vnc = "True"
        self.cfgItems = None
        super(BaremetalHostCfgOption, self).__init__()

    def set_chassis_uuid(self, chassis_uuid):
        self.chassisUuid = chassis_uuid

    def get_chassis_uuid(self):
        return self.chassisUuid

    def set_password(self, password):
        self.password = password

    def get_password(self):
        return self.password

    def set_unattended(self, unattended):
        self.unattended = unattended

    def get_unattended(self):
        return self.unattended

    def set_vnc(self, vnc):
        self.vnc = vnc

    def get_vnc(self):
        return self.vnc

    def set_cfgItems(self, cfgItems):
        self.cfgItems = cfgItems

    def get_cfgItems(self):
        return self.cfgItems

class IscsiOption(DataOption):
    def __init__(self):
        self.ip = None
        self.port = None
        self.chapUserName = None
        self.chapUserPassword = None
        super(IscsiOption, self).__init__()

    def set_ip(self, ip):
        self.ip = ip

    def get_ip(self):
        return self.ip

    def set_port(self, port):
        self.port = port

    def get_port(self):
        return self.port

    def set_chapUserName(self, chapUserName):
        self.chapUserName = chapUserName

    def get_chapUserName(self):
        return self.chapUserName

    def set_chapUserPassword(self, chapUserName):
        self.chapUserPassword = chapUserPassword

    def get_chapUserPassword(self):
        return self.chapUserPassword
 
class VidOption(DataOption):
    def __init__(self):
        self.uuid = None
        self.name = None
        self.state = None
        self.attributes = None
        self.password = None
        super(VidOption, self).__init__()

    def set_vid_uuid(self, uuid):
        self.uuid = uuid

    def get_vid_uuid(self):
        return self.uuid

    def set_password(self, password):
        self.password = password

    def get_password(self):
        return self.password

    def set_state(self, state):
        self.state = state

    def get_state(self):
        return self.state

    def set_attributes(self, attributes):
        if not isinstance(attributes, list):
            raise TestError('Attributes is not a list.')
        self.attributes = attributes

    def get_attributes(self):
        return self.attributes

def _template_to_dict(template_file_path):
    def _parse(path, ret, done):
        if path in done:
            done.append(path)
            err = "recursive import detected, {0} is cyclically referenced, resovling path is: {1}".format(path, " --> ".join(done))
            raise Exception(err)

        done.append(path)
        with open(os.path.abspath(path), 'r') as fd:
            content = fd.read()
            line_num = 0
            for l in content.split('\n'):
                line_num += 1
                l = l.strip().strip('\t\n ')
                if l == "":
                    continue

                if l.startswith('#'):
                    continue

                if l.startswith('import'):
                    _, sub_tempt = l.split(None, 1)
                    sub_tempt = sub_tempt.strip('''\t\n"' ''')
                    if sub_tempt.startswith('.'):
                        sub_tempt = os.path.join(os.path.dirname(os.path.abspath(path)), sub_tempt)

                    # allow referring to environment variable in import
                    if "$" in sub_tempt:
                        t = string.Template(sub_tempt)
                        sub_tempt = t.substitute(os.environ)

                    _parse(sub_tempt, ret, done)
                    continue

                try:
                    (key, val) = l.split('=', 1)
                except:
                    traceback.print_exc(file=sys.stdout)
                    err = "parse error for %s in line: %d in file: %s" % (l, line_num, path)
                    raise Exception(err)

                key = key.strip()
                val = val.strip()
                ret[key] = val

        done.remove(path)
        return ret

    ret = _parse(template_file_path, {}, [])
    flag = True

    tmp = dict(os.environ)
    tmp.update(ret)
    while flag:
        d = ret
        flag = False
        for key, val in d.iteritems():
            if "$" not in val:
                continue

            t = string.Template(val)
            try:
                val = t.substitute(tmp)
                # the val may contain still place holder that has not been resolved
                tmp[key] = val
                if "$" in val:
                    flag = True
                    continue

                ret[key] = val
            except KeyError as e:
                err = "undefined variable: {0}\ncan not parse variable: {1}, it's most likely a wrong variable was defined in its value body. Note, a vairable is defined as 'ABC = xxx' and referenced as 'CBD = $ABC'.".format(str(e), key)
                raise Exception(err)

    return ret

def build_deploy_xmlobject_from_configure(xml_cfg_path, template_file_path=None):
    with open(xml_cfg_path, 'r') as fd:
        xmlstr = fd.read()    
    
    if template_file_path:
        d = _template_to_dict(template_file_path)
        tmpt = string.Template(xmlstr)
        try:
            xmlstr = tmpt.substitute(d)
        except KeyError as key:
            test_fail("Did not find value definition in [template:] '%s' for [KEY:] '%s' from [config:] '%s' " % (template_file_path, key, xml_cfg_path))
    
    return xmlobject.loads(xmlstr)

def set_env_var_from_config_template(template_file_path):
    if os.path.exists(template_file_path):
        d = _template_to_dict(template_file_path)
        for key in d:
            os.environ[key] = d[key]

class Robot_Test_Object(object):
    '''
    Robot Test Object class, which is for setting initial testing information for
    robot resource judgement and selection.
    '''
    zone = 'zone'
    cluster = 'cluster'
    host = 'host'
    l2 = 'l2Network'
    l3 = 'l3Network'
    ps = 'primaryStorage'
    bs = 'backupStorage'

    def __init__(self):
        import zstackwoodpecker.test_state as test_state
        self.test_dict = test_state.TestStateDict()
        self.exclusive_actions_list = []
        self.vm_creation_option = VmOption()
        self.priority_actions = action_select.ActionPriority()
        self.random_type = None #Preserve 
        self.public_l3 = None   #For VIP
        self.action_history = []
        self.resource_action_history = dict()
        self.required_path_list = []
        self.utility_vm_dict = {} #per primary storage
        #DMZ resource will not be selected to be deleted or moved, so utiltiy 
        # vms will be put there safely. This will be important when doing robot
        # testing with resource deletion related actions.
        self.dmz_resource = {
                self.zone: [],
                self.cluster: [],
                self.host: [],
                self.l2: [],
                self.l3: [],
                self.ps: [],
                self.bs: []
                } 
        self.initial_formation = None
        self.initial_formation_parameters = None
        self.constant_path_list = []
        self.constant_path_list_group_dict = {}
        self.configs_dict = {}

    def add_action_history(self, action):
        self.action_history.append(action)

    def get_action_history(self):
        return self.action_history

    def add_resource_action_history(self, uuid, action):
        if self.resource_action_history.has_key(uuid):
            self.resource_action_history[uuid].append(action)
        else:
            self.resource_action_history[uuid] = [ action ]

    def get_resource_action_history(self):
        return self.resource_action_history

    def set_test_dict(self, test_dict):
        self.test_dict = test_dict

    def get_test_dict(self):
        return self.test_dict

    def set_exclusive_actions_list(self, exclusive_actions_list):
        self.exclusive_actions_list = exclusive_actions_list

    def get_exclusive_actions_list(self):
        return self.exclusive_actions_list

    def set_vm_creation_option(self, vm_creation_option):
        self.vm_creation_option = vm_creation_option

    def get_vm_creation_option(self):
        return self.vm_creation_option

    def set_priority_actions(self, priority_actions):
        self.priority_actions = priority_actions

    def get_priority_actions(self):
        return self.priority_actions

    def set_random_type(self, random_type):
        self.random_type = random_type

    def get_random_type(self):
        return self.random_type

    def set_public_l3(self, public_l3):
        self.public_l3 = public_l3

    def get_public_l3(self):
        return self.public_l3

    def set_utility_vm(self, utility_vm):
        ps_uuid = utility_vm.get_vm().allVolumes[0].primaryStorageUuid
        self.utility_vm_dict[ps_uuid] = utility_vm

    def get_utility_vm(self, ps_uuid):
        if self.utility_vm_dict.has_key(ps_uuid):
            return self.utility_vm_dict[ps_uuid]

    def get_dmz_zone(self):
        return self.dmz_resource[self.zone]

    def add_dmz_zone(self, resource):
        if not resource in self.get_dmz_zone(self.zone):
            self.dmz_resource[self.zone].append(resource)

    def get_dmz_cluster(self):
        return self.dmz_resource[self.cluster]

    def add_dmz_cluster(self, resource):
        if not resource in self.get_dmz_cluster(self.cluster):
            self.dmz_resource[self.cluster].append(resource)

    def get_dmz_host(self):
        return self.dmz_resource[self.host]

    def add_dmz_host(self, resource):
        if not resource in self.get_dmz_host(self.host):
            self.dmz_resource[self.host].append(resource)

    def get_dmz_l2(self):
        return self.dmz_resource[self.l2]

    def add_dmz_l2(self, resource):
        if not resource in self.get_dmz_l2(self.l2):
            self.dmz_resource[self.l2].append(resource)

    def get_dmz_l3(self):
        return self.dmz_resource[self.l3]

    def add_dmz_l3(self, resource):
        if not resource in self.get_dmz_l3(self.l3):
            self.dmz_resource[self.l3].append(resource)

    def get_dmz_primary_storage(self):
        return self.dmz_resource[self.ps]

    def add_dmz_primary_storage(self, resource):
        if not resource in self.get_dmz_ps(self.ps):
            self.dmz_resource[self.ps].append(resource)

    def get_dmz_backup_storage(self):
        return self.dmz_resource[self.bs]

    def add_dmz_backup_storage(self, resource):
        if not resource in self.get_dmz_backup_storage(self.bs):
            self.dmz_resource[self.bs].append(resource)

    def set_required_path_list(self, path_list):
        self.required_path_list = path_list

    def get_required_path_list(self):
        return self.required_path_list

    def set_initial_formation(self, formation):
        self.initial_formation = formation

    def get_initial_formation(self):
        return self.initial_formation

    def set_initial_formation_parameters(self, parameters):
        self.initial_formation_parameters = parameters

    def get_initial_formation_parameters(self):
        return self.initial_formation_parameters

    def get_constant_path_list(self):
        return self.constant_path_list

    def set_constant_path_list(self, path_list):
        if self.constant_path_list_group_dict:
            tmp_path_list = path_list
            for list_group_name in self.constant_path_list_group_dict.keys():
                tmp_constant_path_list = []

                while True:
                    tmp_path_list_no_param = []
                    for action_with_param in tmp_path_list:
                        tmp_path_list_no_param.append(action_with_param[0]) 

                    if list_group_name in tmp_path_list_no_param:
                        idx = tmp_path_list_no_param.index(list_group_name)
                        tmp_constant_path_list.extend(tmp_path_list[:idx] + self.constant_path_list_group_dict[list_group_name])
                        del tmp_path_list[:idx+1]
                    else:
                        tmp_constant_path_list.extend(tmp_path_list)
                        break

                tmp_path_list = tmp_constant_path_list

            self.constant_path_list = tmp_path_list

        else:
            self.constant_path_list = path_list

    def get_constant_path_list_group_dict(self):
        return self.constant_path_list_group_dict

    def set_constant_path_list_group_dict(self, list_group_dict):
        self.constant_path_list_group_dict = list_group_dict

    def set_config(self, configs):
        print "shuang %s" % configs
        for config in configs:
            for key in config:
                print "shuang %s" % config
                if config[key] == "default":
                    continue
                if self.configs_dict.has_key(config[key]):
                    print "shuang2 %s" % config[key]
                    self.configs_dict[config[key]][key] = None
                else:
                    print "shuang3 %s" % config[key]
                    self.configs_dict[config[key]] = {key: None}
        for config in configs:
            for key in config:
                if config[key] == "default":
                    for cd_key in self.configs_dict:
                        if self.configs_dict[cd_key].has_key(key):
                            self.configs_dict[cd_key]['default'] = key
                            break
        print "shuang %s" % self.configs_dict

    def get_config(self):
        return self.config

class ComponentLoader(object):
    def __init__(self):
        self.components = {}

    def register(self, name, component):
        self.components[name] = component

    def get(self, name):
        return self.components[name]

component_loader = ComponentLoader()

def get_component_loader():
    return component_loader

class SPTREE(object):
    '''
    Data structure of volume snapshot tree
    '''
    def __init__(self):
        self.sp_tree = {}
        self.curr = None
        self.sp_curr = []

    def add(self, uuid):
        if self.sp_tree and uuid not in self.sp_curr:
            self.sp_curr.append(uuid)
        if uuid not in self.sp_tree:
            self.sp_tree[uuid] = self.sp_curr = []
            self.curr = uuid

    def revert(self, uuid):
        self.sp_curr = self.sp_tree[uuid]
        self.curr = uuid

    def delete(self, uuid):
        self.sp_tree.pop(uuid)
        for k, v in self.sp_tree.iteritems():
            if uuid in v:
                v.remove(uuid)
                self.sp_curr = self.sp_tree[k]
                self.curr = k
        self.clean_tree(len(self.sp_tree.keys()))

    def clean_tree(self, r=0):
        keys = self.sp_tree.keys()
        vals = self.sp_tree.values()
        nodes = [n for node in vals for n in node]
        nodes.append(self.root)
        for k in keys:
            if k not in nodes:
                self.tree.pop(k)
        r -= 1
        if r > 0:
            self.clean_tree(r)

    def parent(self, uuid):
        for k, v in self.sp_tree.iteritems():
            if uuid in v:
                return k

    def children(self, uuid):
        return self.sp_tree[uuid]

def load_paths(template_dirname, path_dirname):
    paths = dict()
    templates_dict = dict()
    for importer, package_name, _ in pkgutil.iter_modules([template_dirname]):
        full_package_name = '%s.%s' % (template_dirname, package_name)
        if full_package_name not in sys.modules:
            templates_dict[package_name] = importer.find_module(package_name).load_module(full_package_name)

    paths_dict = dict()
    for importer, package_name, _ in pkgutil.iter_modules([path_dirname]):
        full_package_name = '%s.%s' % (path_dirname, package_name)
        if full_package_name not in sys.modules:
            paths_dict[package_name] = importer.find_module(package_name).load_module(full_package_name)
            paths[package_name] = dict()
            paths[package_name]['initial_formation'] = templates_dict[paths_dict[package_name].path()['initial_formation']].template()
            paths[package_name]['path_list'] = paths_dict[package_name].path()['path_list']

    return paths
