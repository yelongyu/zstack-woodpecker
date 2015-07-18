'''

@author: Frank
'''

import os
import time
import zstacklib.utils.xmlobject as xmlobject
import string
import sys
import traceback
import string

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

class DataOption(object):
    def __init__(self):
        self.session_uuid = None
        self.timeout = 300000   #5 mins
        self.name = None
        self.description = None

    def set_session_uuid(self, session_uuid):
        self.session_uuid = session_uuid

    def get_session_uuid(self):
        return self.session_uuid

    def set_name(self, name):
        self.name = name

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

class ClusterOption(DataOption):
    def __init__(self):
        self.hypervisor_type = None
        self.type = 'zstack'
        super(ClusterOption, self).__init__()

    def set_hypervisor_type(self, hypervisor_type):
        self.hypervisor_type = hypervisor_type

    def get_hypervisor_type(self):
        return self.hypervisor_type

    def set_type(self, type):
        self.type = type

    def get_type(self):
        return self.type

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

class VipOption(DataOption):
    def __init__(self):
        self.l3_uuid = None
        self.allocateStrategy = None
        super(VipOption, self).__init__()

    def set_l3_uuid(self, l3_uuid):
        self.l3_uuid = l3_uuid

    def get_l3_uuid(self):
        return self.l3_uuid

    def set_allocateStrategy(self, strategy):
        self.allocateStrategy = strategy

    def get_allocateStrategy(self):
        return self.allocateStrategy

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
            #system tag is an array
            self.system_tags = None
            self.user_tags = None
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
            self.default_l3_uuid = vm_opt.get_default_l3_uuid()
            self.system_tags = vm_opt.get_system_tags()
            self.user_tags = vm_opt.get_user_tags()
            super(VmOption, self).__init__()

    def set_l3_uuids(self, l3_uuids):
        if not isinstance(l3_uuids, list):
            raise TestError('l3_uuids is not a list.')
        self.l3_uuids = l3_uuids

    def get_l3_uuids(self):
        return self.l3_uuids

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

class VolumeOption(DataOption):
    def __init__(self):
        self.disk_offering_uuid = None #used when create volume from template
        self.url = None #used when add volume from url.
        self.volume_type = None #used when add volume from url
        self.backup_storage_uuid_list = [] #used when add volume from url
        super(VolumeOption, self).__init__()

    def set_disk_offering_uuid(self, disk_offering_uuid):
        self.disk_offering_uuid = disk_offering_uuid

    def get_disk_offering_uuid(self):
        return self.disk_offering_uuid

    def set_backup_storage_uuid_list(self, backup_storage_uuid_list):
        self.backup_storage_uuid_list = backup_storage_uuid_list

    def get_backup_storage_uuid_list(self):
        return self.backup_storage_uuid_list

    def set_url(self, url):
        self.url = url

    def get_url(self):
        return self.url

    def set_volume_type(self, volume_type):
        self.volume_type = volume_type

    def get_volume_type(self):
        return self.volume_type

class ImageOption(DataOption):
    def __init__(self):
        self.root_volume_uuid = None #for create template from root volume
        self.backup_storage_uuid_list = [] #
        self.guest_os_type = None #CentOS7
        self.platform = None #Linux, Windows, Unknown
        self.bits = None #64/32
        self.url = None #http:// for add a new image
        self.mediaType = None #Template, ISO
        self.format = None #qcow/raw for KVM, simulator, 
        self.system = None #used for system image
        super(ImageOption, self).__init__()

    def set_root_volume_uuid(self, root_volume_uuid):
        self.root_volume_uuid = root_volume_uuid

    def get_root_volume_uuid(self):
        return self.root_volume_uuid

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
        #for salt minion specific id, which is not /etc/machine_id. e.g. VMs, 
        # which use same test image template and have same machine_id. 
        #self.machine_id = None

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

class SecurityGroupOption(DataOption):
    def __init__(self):
        super(SecurityGroupOption, self).__init__()

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

    def add_action_history(self, action):
        self.action_history.append(action)

    def get_action_history(self):
        return self.action_history

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
