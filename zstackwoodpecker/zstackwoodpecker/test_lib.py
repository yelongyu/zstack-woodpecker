'''

Create a common test libs for all integration test stubs. 

@author: Youyk
'''
import time
import os
import string
import random
import traceback
import sys
import threading
import uuid

import zstackwoodpecker.setup_actions as setup_actions 
import zstackwoodpecker.test_util as test_util 
import zstackwoodpecker.test_state as ts_header
import zstackwoodpecker.action_select as action_select
import zstackwoodpecker.operations.resource_operations as res_ops 
import zstackwoodpecker.operations.deploy_operations as dep_ops 
import zstackwoodpecker.operations.vm_operations as vm_ops 
import zstackwoodpecker.operations.account_operations as acc_ops 
import zstackwoodpecker.operations.volume_operations as vol_ops 
import zstackwoodpecker.operations.net_operations as net_ops 
import zstackwoodpecker.operations.tag_operations as tag_ops
import zstackwoodpecker.operations.node_operations as node_ops

import zstackwoodpecker.header.vm as vm_header
import zstackwoodpecker.header.volume as vol_header

import apibinding.api as api
import zstacklib.utils.http as http
import zstacklib.utils.jsonobject as jsonobject
import zstacklib.utils.linux as linux
import zstacklib.utils.lock as lock
import zstacklib.utils.shell as shell
import zstacklib.utils.ssh as ssh
import zstacklib.utils.filedb as filedb
import zstacklib.utils.xmlobject as xmlobject
import zstacklib.utils.debug as debug

import apibinding.inventory as inventory
import zstacktestagent.plugins.vm as vm_plugin
import zstacktestagent.plugins.host as host_plugin
import zstacktestagent.testagent as testagent

debug.install_runtime_tracedumper()
test_stage = ts_header.TestStage
TestAction = ts_header.TestAction
SgRule = ts_header.SgRule
Port = ts_header.Port
WOODPECKER_MOUNT_POINT = '/tmp/zstack/mnt'
SSH_TIMEOUT = 60

class FakeObject(object):
    '''
    Use to print warning message
    '''
    def __getitem__(self, name):
        raise test_util.TestError("WOODPECKER_TEST_CONFIG_FILE is NOT set, which will be used in ZStack test. It is usually set by zstack-woodpecker when executing integration test or exporting environment parameter when executing python command manually(e.g. WOODPECKER_TEST_CONFIG_FILE=/WOODPECKER_TEST_PATH/virtualrouter/test-config.xml). ")

    def __getattr__(self, name):
        self.__getitem__(name)

#Following lines were not expected to be changed.
#---------------
test_config_path = os.environ.get('WOODPECKER_TEST_CONFIG_FILE')
if test_config_path:
    test_config_obj = test_util.TestConfig(test_config_path)
    #Special config in test-config.xml, such like test ping target. 
    test_config = test_config_obj.get_test_config()
    #All configs in deploy.xml.
    all_config = test_config_obj.get_deploy_config()
    #Detailed zstack deployment information, including zones/cluster/hosts...
    deploy_config = all_config.deployerConfig
    setup_plan = setup_actions.Plan(all_config)
    test_config_obj.expose_config_variable()
    #Since ZStack management server might be not the same machine of test 
    #machine, so it needs to set management server ip for apibinding/api.py,
    #before calling ZStack APIs. 
    if not os.environ.get('ZSTACK_BUILT_IN_HTTP_SERVER_IP'):
        os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = xmlobject.safe_list(deploy_config.nodes.node)[0].ip_
else:
    test_config_obj = FakeObject()
    test_config = FakeObject()
    all_config = FakeObject()
    deploy_config = FakeObject()
    setup_plan = FakeObject() 
#---------------

#TestHarness will define how testing will try to connect VM. 
#Default is through Host. If the host is VMWare, it should be changed to VR.
#---------------
TestHarnessVR = 'VR'
TestHarnessHost = 'HOST'
TestHarness = TestHarnessHost
#---------------

#Test Host Default Ethernet device. It is for zstack management device. 
#Please change it to right one.
#---------------
HostDefaultEth = 'eth0'
#---------------

#File name for save host L2 IP dictionary. It doesn't need to be changed. 
#It will be saved in /var/lib/zstack/filedb/host_l2_ip.db
HostL2IpDb = 'host_l2_ip.db'

def lib_install_testagent_to_host(host):
    host_pub_ip = host.managementIp
    try:
        #shell.call('echo "quit" | telnet %s 9393|grep "Escape character"' % host_pub_ip)
        shell.call('nc -w1 %s 9393' % host_pub_ip)
        test_util.test_logger('Testagent is running on Host: %s . Skip testagent installation.' % host.name)
    except:
        test_host = test_util.HostOption()
        test_host.managementIp = host_pub_ip
        test_host.username = os.environ.get('hostUsername')
        test_host.password = os.environ.get('hostPassword')
        test_host.uuid = host.uuid
        test_util.test_logger('Testagent is not running on [host:] %s . Will install Testagent.\n' % host.name)
        setup_plan.deploy_test_agent(test_host)

def lib_check_system_cmd(command):
    '''
    Check if system has command.
    '''
    try:
        shell.call('which %s' % command)
        test_util.test_logger('find command: %s on system' % command)
        return True
    except:
        test_util.test_warn('not find command: %s on system' % command)
        return False

def lib_check_testagent_status(target_ip):
    '''
    Check if test agent is running on target
    '''
    return lib_network_check(target_ip, '9393')

def lib_install_testagent_to_vr_with_vr_vm(vr_vm):
    vr = test_util.HostOption()
    test_util.test_logger("Begin to install testagent to VR: %s" % vr_vm.uuid)
    vr.managementIp = lib_find_vr_mgmt_ip(vr_vm)
    #lib_check_system_cmd('telnet')
    lib_check_system_cmd('nc')
    try:
        #shell.call('echo "quit" | telnet %s 9393|grep "Escape character"' % vr.managementIp)
        shell.call('nc -w1 %s 9393' % vr.managementIp)
        test_util.test_logger('Testagent is running on VR: %s . Skip testagent installation.' % vr.managementIp)
    except:
        vr.username = lib_get_vm_username(vr_vm)
        vr.password = lib_get_vm_password(vr_vm)
        vr.uuid = vr_vm.uuid
        vr.machine_id = vr_vm.uuid
        test_util.test_logger('Testagent is not running on [VR:] %s . Will install Testagent.\n' % vr.managementIp)
        setup_plan.deploy_test_agent(vr)

def lib_install_testagent_to_vr(vm):
    '''
    Install testagent to Vm's VR.

    vm: it is not vr_vm. It is the vm behind of target VR. If want to directly 
    install to vr_vm. Please use lib_install_testagent_to_vr_with_vr_vm(vr_vm)
    '''
    vr_vms = lib_find_vr_by_vm(vm)
    for vr_vm in vr_vms:
        lib_install_testagent_to_vr_with_vr_vm(vr_vm)
    return True

#will clean up log files in virtual router to save is hard driver.
def lib_check_cleanup_vr_logs(vr_vm):
    cleanup_cmd = "free_disk=`df --direct /var/log|grep 'var/log'|awk '{print $5}'|awk -F% '{print $1}'`; if [ $free_disk -ge 90 ]; then rm -f /var/log/zstack/*; rm -f /var/log/dnsmasq.log; fi"
    vr_vm_mgmt_ip = lib_find_vr_mgmt_ip(vr_vm)
    lib_install_testagent_to_vr_with_vr_vm(vr_vm)
    lib_execute_sh_cmd_by_agent_with_retry(vr_vm_mgmt_ip, cleanup_cmd)

def lib_check_cleanup_vr_logs_by_vm(vm):
    vr_vms = lib_find_vr_by_vm(vm)
    for vr_vm in vr_vms:
        lib_check_cleanup_vr_logs(vr_vm)
    return True

def lib_ssh_vm_cmd_by_agent(test_agent_ip, vm_ip, username, password, command, timeout=SSH_TIMEOUT, retry=1):
    cmd = vm_plugin.SshInVmCmd()
    cmd.ip = vm_ip
    cmd.username = username
    cmd.password = password
    cmd.command = command
    cmd.timeout = timeout
    rsp = None
    rsp = lib_try_http_cmd(testagent.build_http_path(test_agent_ip, vm_plugin.SSH_GUEST_VM_PATH), cmd, retry)
    return rsp

def lib_ssh_vm_cmd_by_agent_with_retry(test_agent_ip, vm_ip, username, password, command, expected_result = True):
    '''
    retry the ssh command if ssh is failed in TIMEOUT
    Before this API, lib_set_vm_host_l2_ip() should be called to setup host
    ip address for connect vm. 
    '''
    timeout = time.time() + SSH_TIMEOUT
    rsp = None
    while time.time() < timeout:
        try:
            rsp = lib_ssh_vm_cmd_by_agent(test_agent_ip, vm_ip, username, \
                    password, command)
            if expected_result and not rsp.success:
                time.sleep(1)
                continue
            break
        except:
            test_util.test_logger('Execute ssh cmd: %s on :%s failed. Will try again in 1s.' % (command, test_agent_ip))
            time.sleep(1)
    else:
        test_util.test_logger('Execute ssh cmd: %s on :%s failed for %s seconds. Give up trying.' % (command, test_agent_ip, SSH_TIMEOUT))
    
    if not rsp:
        test_util.test_logger('Meet exception when doing ssh [command:] %s in test [vm:] %s throught [host:] %s. ' % (command, vm_ip, test_agent_ip))
        return False

    if not rsp.success:
        test_util.test_logger('Fail to execute ssh [command:] %s in test [vm:] %s throught [host:] %s. [error:] %s' % (command, vm_ip, test_agent_ip, rsp.error))
        return False

    if not rsp.result:
        return True

    return str(rsp.result)

def lib_execute_sh_cmd_by_agent(test_agent_ip, command):
    shell_cmd = host_plugin.HostShellCmd()
    shell_cmd.command = command
    rsp = lib_try_http_cmd(testagent.build_http_path(test_agent_ip, \
            host_plugin.HOST_SHELL_CMD_PATH), shell_cmd)
    return rsp

def lib_execute_sh_cmd_by_agent_with_retry(test_agent_ip, command, \
        expected_result = True):
    '''
    execute shell command on target machine, which installed test agent. Will
    try execute 3 times, if there is not success result. It is return False

    params:
        test_agent_ip: target machine ip address.
        command: shell command, which will be executed.

    return:
        False: the shell command execute failed.
        True: the shell command executed without stdout
        STDOUT_LOG: the stdout log of shell command. 

    Before this API, lib_set_vm_host_l2_ip() should be called to setup host
    ip address for connect vm. 
    '''
    timeout = time.time() + SSH_TIMEOUT
    rsp = None
    while time.time() < timeout:
        try:
            rsp = lib_execute_sh_cmd_by_agent(test_agent_ip, command)
            if expected_result and rsp.return_code != 0:
                time.sleep(1)
                continue
            break
        except:
            test_util.test_logger('Execute shell cmd: %s on :%s failed. Will try again in 1s.' % (command, test_agent_ip))
            time.sleep(1)
    else:
        test_util.test_logger('Execute shell cmd: %s on :%s failed for %s second. Give up trying.' % (command, test_agent_ip, SSH_TIMEOUT))

    if not rsp:
        test_util.test_logger('Execute shell [cmd:] %s ERROR on [target:] %s ' % (command, test_agent_ip))
        return False

    if rsp.return_code != 0:
        test_util.test_logger('Execute shell [cmd:] %s ERROR on [target:] %s [info:] %s' % (command, test_agent_ip, rsp.stderr))
        return False

    if not rsp.stdout:
        return True
    #avoid of possible unicode result. Need a mandatory type translation
    return str(rsp.stdout)

#-----------Check VM Status-------------
def lib_check_vm_network_status(vm):
    lib_check_vm_running_status(vm)
    lib_install_testagent_to_vr(vm)
    if lib_check_vm_dhcp(vm):
        test_util.test_logger('[vm:] %s mac/ip was assigned in VR /etc/host.dhcp' % vm.uuid)
    else:
        test_util.test_fail('cannot find mac/ip pair in vr for [vm:] %s' % vm.uuid)

    lib_check_mac(vm)
    lib_check_vm_resolv_conf(vm)
    lib_check_ping_gateway(vm)

def lib_check_vm_dhcp(vm):
    return _check_dhcp_cmd(vm, 'cat /etc/hosts.dhcp')

def lib_check_dhcp_leases(vm):
    return _check_dhcp_cmd(vm, 'cat /etc/hosts.leases')

def _check_dhcp_cmd(vm, command):
    vr_vms = lib_find_vr_by_vm(vm)
    for vr_vm in vr_vms:
        test_util.test_logger("Begin to check VM DHCP binding setting in VR: %s" % vr_vm.uuid)
        vr_ip = lib_find_vr_pub_ip(vr_vm)
        nic = lib_get_vm_nic_by_vr(vm, vr_vm)
        guest_mac = nic.mac
        lib_install_testagent_to_vr_with_vr_vm(vr_vm)
        rsp = lib_execute_sh_cmd_by_agent(vr_ip, command)

        if not rsp.success:
            test_util.test_fail('cannot execute shell command: %s in %s. [error:] %s' % (command, vr_ip, rsp.error))
        
        dhcp_res = str(rsp.result)
        if not guest_mac in dhcp_res:
            test_util.test_logger('[vm:] %s [mac:] %s is not found in %s .' % (vm.uuid, guest_mac, command))
            return False
        else:
            test_util.test_logger('[vm:] %s [mac:] %s is found in %s .' % (vm.uuid, guest_mac, command))

    return True

def lib_get_vm_blk_status(vm):
    host = lib_get_vm_host(vm)
    cmd = vm_plugin.VmStatusCmd()
    cmd.vm_uuids = [vm.uuid]
    test_util.test_logger('Begin to check [vm:] %s blk status on [host:] %s.' % (vm.uuid, host.name))
    rspstr = http.json_dump_post(testagent.build_http_path(host.managementIp, vm_plugin.VM_BLK_STATUS), cmd)
    rsp = jsonobject.loads(rspstr)
    if rsp.vm_status[vm.uuid]:
        test_util.test_logger('vm [uuid:%s] blk status: %s .' % (vm.uuid, jsonobject.dumps(rsp.vm_status[vm.uuid])))
        return True
    else:
        test_util.test_logger('Can not get vm [uuid:%s] blk status.' % vm.uuid)
        return False

def lib_check_vm_running_status(vm):
    host = lib_get_vm_host(vm)
    cmd = vm_plugin.VmStatusCmd()
    cmd.vm_uuids = [vm.uuid]
        
    test_util.test_logger('Begin to check [vm:] %s status on [host:] %s.' % (vm.uuid, host.name))
    rspstr = http.json_dump_post(testagent.build_http_path(host.managementIp, vm_plugin.IS_VM_RUNNING_PATH), cmd)
    rsp = jsonobject.loads(rspstr)
    if rsp.vm_status[vm.uuid]:
        test_util.test_logger('vm [uuid:%s] is running on host: %s .' % (vm.uuid, host.name))
        return True
    else:
        test_util.test_logger('vm [uuid:%s] is not running on host: %s .' % (vm.uuid,host.name))
        return False

def lib_check_vm_stopped_status(vm):
    host = lib_get_vm_host(vm)
    cmd = vm_plugin.VmStatusCmd()
    cmd.vm_uuids = [vm.uuid]
    rspstr = http.json_dump_post(testagent.build_http_path(host.managementIp, vm_plugin.IS_VM_STOPPED_PATH), cmd)
    rsp = jsonobject.loads(rspstr)
    if rsp.vm_status[vm.uuid]:
        test_util.test_logger('vm[uuid:%s] is stopped on [host:] %s' % (vm.uuid, host.name))
        return True
    else:
        test_util.test_logger('vm[uuid:%s] is not stopped on [host:] %s . Test failed' % (vm.uuid, host.name))
        return False

def lib_check_vm_resolv_conf(vm):
    imageUsername = lib_get_vm_username(vm)
    imagePassword = lib_get_vm_password(vm)
    vr_vms = lib_find_vr_by_vm(vm)
    for vr_vm in vr_vms:
        test_util.test_logger("Begin to check VM DNS setting behind of VR: %s" % vr_vm.uuid)
        nic = lib_get_vm_nic_by_vr(vm, vr_vm)
        if TestHarness == TestHarnessHost:
            test_harness_ip = lib_find_host_by_vm(vm).managementIp
            #assign host l2 bridge ip.
            lib_set_vm_host_l2_ip(vm)
        else:
            test_harness_ip = lib_find_vr_mgmt_ip(vr_vm)
            lib_install_testagent_to_vr_with_vr_vm(vr_vm)

        guest_ip = nic.ip
        command = 'cat /etc/resolv.conf'
        username = lib_get_vm_username(vm)
        password = lib_get_vm_password(vm)
        rsp = lib_ssh_vm_cmd_by_agent(test_harness_ip, guest_ip, username, \
                password, command)
        
        if not rsp.success:
            test_util.test_fail('cannot execute test ssh command in test vm. [error:] %s' % rsp.error)
        
        dns_res = str(rsp.result)
        vr_guest_ip = lib_find_vr_private_ip(vr_vm)
        if vr_guest_ip in dns_res:
            test_util.test_logger('[VR IP:] %s is set in guest vm /etc/resolv.conf of guest:%s . VM network checking pass.' % (vr_guest_ip, dns_res))
        else:
            test_util.test_fail('[Guest IP:] %s is not set in guest vm, content of /etc/resolv.conf of guest:%s' % (vr_guest_ip, dns_res))

#TODO: add check vlan operations.
def lib_check_vlan(vm):
    pass

#consider possible connection failure on stress test. Better to repeat the same command several times.
def lib_try_http_cmd(http_path, cmd, times=5):
    interval = 1
    current_round = 1
    exception = None

    # avoid of too long time wait for impossible connection
    timeout = time.time() + SSH_TIMEOUT
    while current_round <= times and time.time() < timeout:
        try:
            current_round += 1
            rspstr = http.json_dump_post(http_path, cmd)
            rsp = jsonobject.loads(rspstr)
            test_util.test_logger('http call response result: %s' % rspstr)
            return rsp
        except Exception as e:
            test_util.test_logger('meet error when call zstack test agent API, will try again...the trace logs are:')
            traceback.print_exc(file=sys.stdout)
            exception = e
        time.sleep(1)

    test_util.test_logger('Error. [http connection:] %s with [command:] %s is failed %s times execution.' % (http_path, cmd.command, times))
    raise test_util.TestError(str(exception))

#check guest mac address and ip address
def lib_check_mac(vm):
    vr_vms = lib_find_vr_by_vm(vm)
    for vr_vm in vr_vms:
        test_util.test_logger("Begin to check IP/MAC for [VM:] %s behind of [VR:] %s" % (vm.uuid, vr_vm.uuid))
        nic = lib_get_vm_nic_by_vr(vm, vr_vm)
        guest_ip = nic.ip
        guest_mac = nic.mac
 
        if TestHarness == TestHarnessHost:
            test_harness_ip = lib_find_host_by_vm(vm).managementIp
            #assign host l2 bridge ip.
            lib_set_vm_host_l2_ip(vm)
        else:
            test_harness_ip = lib_find_vr_mgmt_ip(vr_vm)
            lib_install_testagent_to_vr_with_vr_vm(vr_vm)

        command = '/sbin/ifconfig'
        username = lib_get_vm_username(vm)
        password = lib_get_vm_password(vm)
        rsp = lib_ssh_vm_cmd_by_agent(test_harness_ip, guest_ip, username, \
                password, command)
        
        if not rsp.success:
            test_util.test_fail('Cannot execute test ssh command in test vm through [ip:] %s. [error:] %s' % (test_harness_ip, rsp.error))
        
        ip_res = str(rsp.result)
        if (guest_mac in ip_res) or (string.upper(guest_mac) in ip_res):
            test_util.test_logger('[MAC:] %s is set in guest vm, guest IP is: %s . VM MAC checking pass.' % (guest_mac, guest_ip))
            #test_util.test_logger('ifconfig result: %s' % ip_res)
        else:
            test_util.test_fail('[MAC:] %s is not found in guest vm, guest IP is:%s . VM MAC checking fail.' % (guest_mac, guest_ip))

def lib_is_vm_vr(vm):
    '''
    Return True if vm is an appliance vm.
    '''
    cond = res_ops.gen_query_conditions('uuid', '=', vm.uuid)
    vr = res_ops.query_resource(res_ops.APPLIANCE_VM, cond)
    if vr:
        return True

#login vm and ping target
def lib_check_ping(vm, target, no_exception=None):
    '''target is IP address or hostname'''
    vr_vms = lib_find_vr_by_vm(vm)
    command = 'ping -c 3 -W 5 %s >/tmp/ping_result 2>&1' % target
    if lib_is_vm_vr(vm):
        vm_ip = lib_find_vr_pub_ip(vm)
        lib_install_testagent_to_vr_with_vr_vm(vm)
        if lib_execute_sh_cmd_by_agent_with_retry(vm_ip, command):
            test_util.test_logger("Ping [target:] %s from [vm:] %s Test Pass" % (target, vm.uuid))
        else:
            if not no_exception:
                test_util.test_fail("Fail: [vm:] %s ping target: %s fail. [error:] %s" %(vm.uuid, target, rsp.error))
            else:
                test_util.test_logger("Fail: [vm:] %s ping target: %s fail. [error:] %s" %(vm.uuid, target, rsp.error))
    else:
        vr_vm = vr_vms[0]
        nic = lib_get_vm_nic_by_vr(vm, vr_vm)
        guest_ip = nic.ip
        if TestHarness == TestHarnessHost:
            test_harness_ip = lib_find_host_by_vm(vm).managementIp
            #assign host l2 bridge ip.
            lib_set_vm_host_l2_ip(vm)
            print 'test_harness ip: %s' % test_harness_ip
        else:
            test_harness_ip = lib_find_vr_mgmt_ip(vr_vm)
            lib_install_testagent_to_vr_with_vr_vm(vr_vm)

        test_util.test_logger("Begin to test ping target: %s from VM through L3 behind of VR: %s by connection from test_harness: %s" % (target, vr_vm.uuid, test_harness_ip))
    
        username = lib_get_vm_username(vm)
        password = lib_get_vm_password(vm)
        rsp = lib_ssh_vm_cmd_by_agent(test_harness_ip, guest_ip, username, \
                password, command)
        
        if not rsp.success:
            if not no_exception:
                test_util.test_fail("Fail: [vm:] %s ping target: %s fail. [error:] %s" %(vm.uuid, target, rsp.error))
            else:
                test_util.test_logger("Fail: [vm:] %s ping target: %s fail. [error:] %s" %(vm.uuid, target, rsp.error))
                return False
    
            test_util.test_logger("Ping [target:] %s from [vm:] %s Test Pass" % (target, vm.uuid))
            #return True
    return True

def lib_check_directly_ping(target_ip):
    try:
        shell.call('ping -c 1 -W 1 %s' % target_ip)
    except:
        test_util.test_logger('ping %s failed' % target_ip)
        return False
    else:
        test_util.test_logger('ping %s successfully' % target_ip)
        return True

#login vm and ping gateway
def lib_check_ping_gateway(vm, no_exception=None):
    '''
        Ping gateway. 
    '''
    return lib_check_ping(vm, vm.vmNics[0].gateway, no_exception)

def lib_check_ping_external_machine(vm, no_exception=None):
    '''
        Ping pre-setting external machine in plan.xml.
        Check if dns and dhcp is setting correctly. 
    '''
    return lib_check_ping(vm, test_config.pingTestTarget.text_, no_exception)

def lib_scp_file_to_vm(vm, src_file, dst_file, l3_uuid = None):
    '''
    scp source file to destination in vm. 
    @params: 
        vm: target vm
        src_file: source file in current host
        dst_file: destination file name in vm. dst_folder should be ready.
        l3_uuid: the optional l3 uuid for find target vm's nic

    @return:
        scp response object: scp successfully
        False: scp failed
    '''
    def _full_path(path):
        if path.startswith('~'):
            return os.path.expanduser(path)
        elif path.startswith('/'):
            return path
        else:
            return os.path.join(self.config_base_path, path)

    lib_set_vm_host_l2_ip(vm)
    host_ip = lib_find_host_by_vm(vm).managementIp
    h_username = os.environ.get('hostUsername')
    h_password = os.environ.get('hostPassword')

    temp_script = '/tmp/%s' % uuid.uuid1().get_hex()

    #copy the target script to target host firstly.
    src_file = _full_path(src_file)
    ssh.scp_file(src_file, temp_script, host_ip, h_username, h_password)

    username = lib_get_vm_username(vm)
    password = lib_get_vm_password(vm)

    if not l3_uuid:
        vm_ip = vm.vmNics[0].ip
    else:
        vm_ip = lib_get_vm_nic_by_l3(vm, l3_uuid).ip

    #copy the target script to target vm
    scp_cmd = vm_plugin.SshInVmCmd()
    scp_cmd.ip = vm_ip
    scp_cmd.username = username
    scp_cmd.password = password
    scp_cmd.src_file = temp_script
    scp_cmd.dst_file = dst_file
    rspstr = http.json_dump_post(testagent.build_http_path(host_ip, vm_plugin.SCP_GUEST_VM_PATH), scp_cmd)

    rsp = jsonobject.loads(rspstr)
    if not rsp.success:
        test_util.test_logger('scp error info: %s' % rsp.error)
        return False

    #cleanup temporay script in host.
    ssh.execute('rm -f %s' % temp_script, host_ip, h_username, h_password)

    return rsp

def lib_execute_shell_script_in_vm(vm_inv, script_file, l3_uuid=None, timeout=SSH_TIMEOUT):
    '''
    execute shell script in vm. Will only use vm's host to ssh vm

    @params:

    vm_inv: target vm to execute the script file
    script_file: the local script file, which will be copied and runned on 
        target vm.
    l3_uuid: [optional] l3_uuid for target vm's nic. It is used, when VM has 
        multiple nics.
    timeout: [default:60s] the script should be executed completed in timeout.

    @return:
        ssh response object: Pass
        False: ssh fail
    '''
    lib_set_vm_host_l2_ip(vm_inv)
    host_ip = lib_find_host_by_vm(vm_inv).managementIp
    h_username = os.environ.get('hostUsername')
    h_password = os.environ.get('hostPassword')

    temp_script = '/tmp/%s' % uuid.uuid1().get_hex()
    if not lib_scp_file_to_vm(vm_inv, script_file, temp_script, l3_uuid):
        return False

    if not l3_uuid:
        vm_ip = vm_inv.vmNics[0].ip
    else:
        vm_ip = lib_get_vm_nic_by_l3(vm_inv, l3_uuid).ip

    command = 'sh %s' % temp_script
    username = lib_get_vm_username(vm_inv)
    password = lib_get_vm_password(vm_inv)
    rsp = lib_ssh_vm_cmd_by_agent(host_ip, vm_ip, username, \
            password, command, timeout)
        
    if not rsp.success:
        test_util.test_logger('ssh error info: %s when execute [script:] %s in [vm:] %s ' % (rsp.error, open(script_file).readlines(), vm_inv.uuid))
        return False

    test_util.test_logger('Successfully execute [script:] >>> %s <<< in [vm:] %s' % \
            (script_file, vm_inv.uuid))

    print rsp.result
    #cleanup temporay script in host.
    ssh.execute('rm -f %s' % temp_script, host_ip, h_username, h_password)
    return rsp

def lib_execute_command_in_vm(vm, cmd, l3_uuid=None):
    '''
    The cmd was assumed to be returned as soon as possible.
    '''
    vr_vm = lib_find_vr_by_vm(vm)
    ret = True
    #if vr_vm[0].uuid == vm.uuid:
    #    lib_install_testagent_to_vr_with_vr_vm(vm)
    #    try:
    #        vm_ip = lib_find_vr_mgmt_ip(vm)
    #        vr_vm = vm
    #    except:
    #        test_util.test_logger("[vm:] %s is not a VR or behind any VR. Can't connect to it to execute [cmd:] %s " % (vm.uuid, cmd))
    #        return False
    #    shell_cmd = host_plugin.HostShellCmd()
    #    shell_cmd.command = cmd
    #    rspstr = http.json_dump_post(testagent.build_http_path(vm_ip, host_plugin.HOST_SHELL_CMD_PATH), shell_cmd)
    #    rsp = jsonobject.loads(rspstr)
    #    if rsp.return_code != 0:
    #        ret = False
    #        test_util.test_logger('shell error info: %s' % rsp.stderr)
    #    else:
    #        ret = rsp.stdout
    #else:
    #    vr_vm = vr_vm[0]
    #    if TestHarness == TestHarnessHost:
    #        #assign host l2 bridge ip.
    #        lib_set_vm_host_l2_ip(vm)
    #        test_harness_ip = lib_find_host_by_vm(vm).managementIp
    #    else:
    #        test_harness_ip = lib_find_vr_mgmt_ip(vr_vm)

    #    if not l3_uuid:
    #        vm_ip = vm.vmNics[0].ip
    #    else:
    #        vm_ip = lib_get_vm_nic_by_l3(vm, l3_uuid).ip

    #    ssh_cmd = vm_plugin.SshInVmCmd()
    #    ssh_cmd.ip = vm_ip
    #    ssh_cmd.username = lib_get_vr_image_username(vr_vm)
    #    ssh_cmd.password = lib_get_vr_image_password(vr_vm)
    #    ssh_cmd.command = cmd
    #    rspstr = http.json_dump_post(testagent.build_http_path(test_harness_ip, vm_plugin.SSH_GUEST_VM_PATH), ssh_cmd)

    #    rsp = jsonobject.loads(rspstr)
    #    if not rsp.success:
    #        ret = False
    #        test_util.test_logger('ssh error info: %s' % rsp.error)
    #    else:
    #        ret = str(rsp.result)

    vr_vm = vr_vm[0]
    if TestHarness == TestHarnessHost:
        #assign host l2 bridge ip.
        lib_set_vm_host_l2_ip(vm)
        test_harness_ip = lib_find_host_by_vm(vm).managementIp
    else:
        test_harness_ip = lib_find_vr_mgmt_ip(vr_vm)
        lib_install_testagent_to_vr_with_vr_vm(vr_vm)

    if lib_is_vm_vr(vm):
        vm_ip = lib_find_vr_mgmt_ip(vm)
    else:
        if not l3_uuid:
            vm_ip = vm.vmNics[0].ip
        else:
            vm_ip = lib_get_vm_nic_by_l3(vm, l3_uuid).ip

    username = lib_get_vr_image_username(vr_vm)
    password = lib_get_vr_image_password(vr_vm)
    test_util.test_logger("Do testing through test agent: %s to ssh vm: %s, ip: %s, with cmd: %s" % (test_harness_ip, vm.uuid, vm_ip, cmd))
    rsp = lib_ssh_vm_cmd_by_agent(test_harness_ip, vm_ip, username, \
            password, cmd)
        
    if not rsp.success:
        ret = False
        test_util.test_logger('ssh error info: %s' % rsp.error)
    else:
        ret = str(rsp.result)

    if ret:
        test_util.test_logger('Successfully execute [command:] >>> %s <<< in [vm:] %s' % (cmd, vm_ip))
        return ret
    else:
        test_util.test_logger('Fail execute [command:] %s in [vm:] %s' % (cmd, vm_ip))
        return False

#-----------VM operations-------------
def lib_create_vm(vm_cre_opt=test_util.VmOption(), session_uuid=None): 
    '''If not provide vm_cre_opt, it creates random vm '''
    if not vm_cre_opt.get_name():
        vm_cre_opt.set_name('test-vm')

    if not vm_cre_opt.get_instance_offering_uuid():
        #pick up random user vm instance offering.
        instance_offerings = res_ops.get_resource(res_ops.INSTANCE_OFFERING, session_uuid)
        user_vm_offerings = []
        for instance in instance_offerings:
            if instance.type == 'UserVm':
                user_vm_offerings.append(instance)
        vm_cre_opt.set_instance_offering_uuid(random.choice(user_vm_offerings).uuid)

    if not vm_cre_opt.get_image_uuid():
        #pick up random image
        images = lib_get_not_vr_images()
        #Virtual Router image is CentOS image, which will automatically create /etc/udev/rules.d/70-persistent-net.rules. If the CentOS image was bootup and save as a new image template, when the other VM using the new template, its valid network device will be eth1, rather than eth0. But there isn't eth1 config in CentOS image, so it will cause VM networking checking failure. In Robot testing, we have to avoid of using virtual router image. 
        #images = lib_remove_image_from_list_by_desc(images, img_desc="virtual router image")
        image = random.choice(images)
        vm_cre_opt.set_image_uuid(image.uuid)

    #pick up random l3 network
    if not vm_cre_opt.get_l3_uuids():
        #If setting zone_uuid, will pick a l3 from this zone.
        zone_uuid = vm_cre_opt.get_zone_uuid()
        if not zone_uuid:
            cluster_uuid = vm_cre_opt.get_cluster_uuid()
            if not cluster_uuid:
                host_uuid = vm_cre_opt.get_host_uuid()
                if host_uuid:
                    zone_uuid = res_ops.get_resource(res_ops.HOST, uuid = host_uuid)[0].zoneUuid
            else:
                zone_uuid = res_ops.get_resource(res_ops.CLUSTER, uuid = cluster_uuid)[0].zoneUuid

        vm_cre_opt.set_l3_uuids([lib_get_random_l3(zone_uuid = zone_uuid).uuid])

        test_util.test_logger('VM creation selection: [image uuid:] %s; [l3 uuid:] %s' % (vm_cre_opt.image_uuid, vm_cre_opt.l3_uuids))

    if not vm_cre_opt.get_timeout():
        vm_cre_opt.set_timeout(300000 + 300000*len(vm_cre_opt.l3_uuids))

    #To avoid of import loop, move this import here.
    #[Inlined import]
    import zstackwoodpecker.zstack_test.zstack_test_vm as zstack_vm_header
    vm = zstack_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_cre_opt)
    vm.create()

    return vm

def lib_create_vm_static_ip_tag(l3_uuid, ip_address):
    return ['staticIp::%s::%s' % (l3_uuid, ip_address)]

def lib_create_vm_hostname_tag(hostname):
    hostname = '-'.join(hostname.split('_'))
    return ['hostname::%s' % hostname]

def lib_vm_random_idel_time(min_stay_time=1, max_stay_time=120):
    random_time_interval = 1
    random_exist_time = random.randrange(min_stay_time, max_stay_time, random_time_interval)
    test_util.test_logger('[Random stay:] will stay for %s seconds .' % random_exist_time)
    time.sleep(random_exist_time)
    test_util.test_logger('[Random stay:] have stayed for %s seconds .' % random_exist_time)

#-----------Get Host resource-------------
def lib_is_image_kvm(image):
    if lib_get_hv_type_of_image(image) ==  inventory.KVM_HYPERVISOR_TYPE:
        return True
    else:
        return False

#does image type is simulator type.
def lib_is_image_sim(image):
    if lib_get_hv_type_of_image(image) ==  inventory.SIMULATOR_HYPERVISOR_TYPE:
        return True
    else:
        return False

#Does VM's hypervisor is KVM.
def lib_is_vm_kvm(vm):
    if lib_get_hv_type_of_vm(vm) == inventory.KVM_HYPERVISOR_TYPE:
        return True
    else:
        return False

def lib_is_vm_sim(vm):
    if lib_get_hv_type_of_vm(vm) == inventory.SIMULATOR_HYPERVISOR_TYPE:
        return True
    else:
        return False

def lib_get_hv_type_of_vm(vm):
    #host = lib_get_vm_host(vm)
    #return host.hypervisorType
    return vm.hypervisorType

def lib_get_hv_type_of_image(image):
    image_format = image.format
    if image_format == 'qcow2' or image_format == 'raw':
        return 'KVM'
    test_util.test_warn('not supported format: %s in test' % image_format)

def lib_get_hv_type_of_cluster(cluster):
    return cluster.hypervisorType

def lib_get_hv_type_of_host(host):
    return host.hypervisorType

def lib_get_all_hosts_from_plan():
    hosts = []
    for zone in deploy_config.zones.get_child_node_as_list('zone'):
        for cluster in zone.clusters.get_child_node_as_list('cluster'):
                for host in cluster.hosts.get_child_node_as_list('host'):
                    hosts.append(host)
    return hosts

def lib_get_cluster_hosts(cluster_uuid = None):
    if cluster_uuid:
       conditions = res_ops.gen_query_conditions('clusterUuid', '=', \
               cluster_uuid)
    else:
       conditions = res_ops.gen_query_conditions('clusterUuid', '!=', \
               'impossible_uuid')

    hosts = res_ops.query_resource(res_ops.HOST, conditions)
    return hosts

def lib_get_vm_host(vm):
    vm_host_uuid = vm.hostUuid
    if not vm_host_uuid:
        vm_host_uuid = vm.lastHostUuid

    hosts = res_ops.get_resource(res_ops.HOST, session_uuid=None, \
            uuid=vm_host_uuid)

    if hosts:
        #test_util.test_logger('[vm:] %s [host uuid:] %s [host name:] %s is found' % (vm.uuid, host.uuid, host.name))
        return hosts[0]
    else:
        test_util.test_logger('Did not find [vm:] %s host' % vm.uuid)

def lib_get_primary_storage_uuid_list_by_backup_storage(bs_uuid):
    '''
    Get primary storage uuid list, which belongs to the zone of backup storage
    Since bs might be attached to multi zones, the ps might be blonged to multi
    zones as well.
    '''
    cond = res_ops.gen_query_conditions('uuid', '=', bs_uuid)
    bss = res_ops.query_resource(res_ops.BACKUP_STORAGE, cond)
    if bss:
        zone_uuids = bss[0].attachedZoneUuids
        cond = res_ops.gen_query_conditions('zoneUuid', 'in', ','.join(zone_uuids))
        pss = res_ops.query_resource_fields(res_ops.PRIMARY_STORAGE, cond, \
                None, ['uuid'])
        ps_uuids = []
        for ps in pss:
            ps_uuids.append(ps.uuid)

        return ps_uuids

def lib_get_backup_storage_uuid_list_by_zone(zone_uuid):
    '''
    Get backup storage uuid list which attached to zone uuid
    '''
    cond = res_ops.gen_query_conditions('attachedZoneUuids', 'in', zone_uuid)
    bss = res_ops.query_resource_fields(res_ops.BACKUP_STORAGE, cond, None, ['uuid'])
    bs_list = []
    for bs in bss:
        bs_list.append(bs.uuid)

    return bs_list

def lib_get_backup_storage_host(bs_uuid):
    '''
    Get host, who has backup storage uuid.
    '''
    #session_uuid = acc_ops.login_as_admin()
    #try:
    #    bss = res_ops.get_resource(res_ops.BACKUP_STORAGE, session_uuid)
    #finally:
    #    acc_ops.logout(session_uuid)
    #
    #if not bss:
    #    test_util.test_fail('can not get zstack backup storage inventories.')

    host = test_util.HostOption()

    #for bs in bss:
    #    if bs.uuid == bs_uuid:
    #        host.managementIp = bs.hostname
    #        host.username = bs.username
    #        host.password = bs.password
    #        break

    host.managementIp = os.environ.get('sftpBackupStorageHostname')
    host.username = os.environ.get('sftpBackupStorageUsername')
    host.password = os.environ.get('sftpBackupStoragePassword')
    
    return host

#return any host in zone_uuid
def lib_find_host_by_zone(zone_uuid):
    conditions = res_ops.gen_query_conditions('zoneUuid', '=', zone_uuid)
    hosts = res_ops.query_resource(res_ops.HOST, conditions, None)
    if hosts:
        return hosts[0]

def lib_find_host_tag(host_inv, conditions = None):
    '''
    conditions is res_ops.gen_query_conditions(), it will include a special 
    condition, like {'name':'tag', 'op':'=', 'value':'capability:liveSnapshot'}

    return Tag_inv
    '''
    condition = res_ops.gen_query_conditions('resourceUuid', '=', \
            host_inv.uuid, conditions)
    if host_inv.hypervisorType == inventory.KVM_HYPERVISOR_TYPE:
        condition = res_ops.gen_query_conditions('resourceType', '=', \
                'HostVO', condition)
    ret = res_ops.query_resource(res_ops.SYSTEM_TAG, condition)
    return ret

def lib_get_cpu_memory_capacity(zone_uuids = None, cluster_uuids = None, \
        host_uuids = None, session_uuid = None):
    import apibinding.api_actions as api_actions
    action = api_actions.GetCpuMemoryCapacityAction()
    if zone_uuids:
        action.zoneUuids = zone_uuids
    if cluster_uuids:
        action.clusterUuids = host_uuids
    if host_uuids:
        action.hostUuids = host_uuids

    ret = acc_ops.execute_action_with_session(action, session_uuid)
    return ret

def lib_get_host_libvirt_tag(host_inv):
    '''
    find and return given host's libvirt version. 
    '''
    condition = res_ops.gen_query_conditions('tag', 'like', '%libvirt::version%')
    tag_info = lib_find_host_tag(host_inv, condition)
    if tag_info:
        libvirt_ver = tag_info[0].tag.split('::')[2]
        test_util.test_logger('host: %s libvirt version is: %s' % \
                (host_inv.uuid, libvirt_ver))
        return libvirt_ver
    else:
        test_util.test_logger('Did not find libvirt version for host: %s ' % \
                host_inv.uuid)
        return None

def lib_check_live_snapshot_cap(host_inv):
    '''
    check if host support live snapshot operations.
    '''
    conditions = res_ops.gen_query_conditions('tag', '=', \
            'capability:liveSnapshot')
    tag_info = lib_find_host_tag(host_inv, conditions)
    if tag_info:
        test_util.test_logger('host: %s support live snapshot' % host_inv.uuid)
        return True
    else:
        test_util.test_logger('host: %s does not support live snapshot' \
                % host_inv.uuid)
        return False

#return host inventory
def lib_find_host_by_vm(vm_inv):
    '''
    Get host inventory by providing vm inventory. 
    '''
    if not vm_inv.hostUuid:
        host_uuid = vm_inv.lastHostUuid
    else:
        host_uuid = vm_inv.hostUuid

    if not host_uuid:
        test_util.test_logger("Host UUID is None. Can't get Host IP address for [vm:] %s" % vm_inv.uuid)
        return None

    hosts = res_ops.get_resource(res_ops.HOST, session_uuid=None, \
            uuid=host_uuid)
    if hosts:
        return hosts[0]

def lib_find_host_by_iscsi_ps(ps_inv):
    '''
    Get host information from deploy.xml for ISCSI filesystem backend.
    '''
    ps_name = ps_inv.name
    iscsi_host = test_util.HostOption()
    iscsi_host.managementIp = os.environ.get('iscsiHostname')
    iscsi_host.username = os.environ.get('iscsiUserName')
    iscsi_host.password = os.environ.get('iscsiPassword')
    return iscsi_host

def lib_get_primary_storage_by_uuid(ps_uuid):
    cond = res_ops.gen_query_conditions('uuid', '=', ps_uuid)
    return res_ops.query_resource(res_ops.PRIMARY_STORAGE, cond)[0]

def lib_is_ps_iscsi_backend(ps_uuid):
    ps = lib_get_primary_storage_by_uuid(ps_uuid)
    if ps.type == inventory.ISCSI_FILE_SYSTEM_BACKEND_PRIMARY_STORAGE_TYPE:
        return True
    return False

def lib_find_random_host(vm = None):
    '''
    Return a random host inventory. 
    
    If Vm is provided, the returned host should not be the host of VM. But it 
    should belong to the same cluster of VM.
    '''
    import zstackwoodpecker.header.host as host_header
    target_hosts = []
    cluster_id = None
    current_host_uuid = None
    if vm:
        current_host = lib_get_vm_host(vm)
        cluster_id = vm.clusterUuid
        current_host_uuid = current_host.uuid

    all_hosts = lib_get_cluster_hosts(cluster_id)
    for host in all_hosts:
        if host.uuid != current_host_uuid and \
                host.status == host_header.CONNECTED and \
                host.state == host_header.ENABLED:
            target_hosts.append(host)

    if not target_hosts:
        return None

    return random.choice(target_hosts)

def _lib_assign_host_l3_ip(host_pub_ip, cmd):
    with lock.FileLock(host_pub_ip):
        http.json_dump_post(testagent.build_http_path(host_pub_ip, \
                host_plugin.SET_DEVICE_IP_PATH), cmd)

def _lib_flush_host_l2_ip(host_ip, net_device):
    cmd = host_plugin.FlushDeviceIpCmd()
    cmd.ethname = net_device
    test_util.test_logger('Flush ip address for net device: %s from host: %s' \
            % (net_device, host_ip))
    with lock.FileLock(host_ip):
        http.json_dump_post(testagent.build_http_path(host_ip, \
                host_plugin.FLUSH_DEVICE_IP_PATH), cmd)

def lib_create_host_vlan_bridge(host, cmd):
    with lock.FileLock(host.uuid):
        http.json_dump_post(testagent.build_http_path(host.managementIp, host_plugin.CREATE_VLAN_DEVICE_PATH), cmd)

#will based on x.y.*.*/16 address. 
#Host ip address will assigned from x.y.128.0 to x.y.255.254
def _lib_gen_host_next_ip_addr(network_address, addr_list):
    network_addr = network_address.split('.')
    available_ip_list = list(network_addr)
    net_3_num = int(network_addr[2])
    if net_3_num < 128:
        net_3_num += 128
        available_ip_list[2] = str(net_3_num)

    available_ip = '.'.join(available_ip_list)

    return available_ip

    #if not addr_list:
    #    network_addr = network_address.split('.')
    #    network_addr[2] = '128'
    #    return ('.').join(network_addr)

    #addr_list.sort()
    #assigned_last_ip = addr_list[-1].split('.')
    #assigned_last_ip_f3 = string.atoi(assigned_last_ip[3])
    #assigned_last_ip_f2 = string.atoi(assigned_last_ip[2])
    #if assigned_last_ip_f2 == 255 and assigned_last_ip_f3 == 254:
    #    test_util.test_fail('No available ip address. Current used ip address: %s' % addr_list)
    #if assigned_last_ip_f3 != 255:
    #    assigned_last_ip[3] = str(assigned_last_ip_f3 + 1)
    #else:
    #    assigned_last_ip[2] = str(assigned_last_ip_f2 + 1)
    #    assigned_last_ip[3] = str(0)
    #    
    #return ('.').join(assigned_last_ip)

def lib_get_stored_host_ip_dict(l2_vlan_value):
    host_ip_db = filedb.FileDB(HostL2IpDb)
    return host_ip_db.get(str(l2_vlan_value))

def lib_set_host_ip_dict(l2_vlan_value, host_ip_dict):
    host_ip_db = filedb.FileDB(HostL2IpDb)
    host_ip_db.set(str(l2_vlan_value), host_ip_dict)

def lib_set_vm_host_l2_ip(vm):
    host = lib_find_host_by_vm(vm)
    if not host:
        test_util.test_logger('Not find host: %s for VM: %s. Skip host IP assignment.' % (vm.hostUuid, vm.uuid))
        return False
    l2s = lib_get_private_l2s_by_vm(vm)
    for l2 in l2s: 
        lib_assign_host_l2_ip(host, l2)

def lib_assign_host_l2_ip(host, l2):
    '''
    Assign an IP address for Host L2 bridge dev. It is for test connection.
    
    It will assign IP to either vlan or no vlan device bridge. e.g. br_eth1
    br_eth0.10 br_eth0_20 etc. 

    br_eth1 means the vm will use no vlan network eth1.
    br_eth0.10 means the vm will use pre-defined vlan eth0.10. pre-defined
        means the vlan is created by user and not controlled by zstack.
    br_eth0_20 means the vm will use zstack assigned vlan eth0.20. 
  
    In currently testing, it assumes each L2 only have 1 L3. It is because 
    multipal L3 will have different network mask. Then the sigle Host L2 IP 
    can't know which L3 network it needs to connect. Test netmask is assume 
    to be 255.255.0.0. The reason is test case will use x.y.0.1~x.y.127.255 
    for VM IP assignment; x.y.128.1~x.y.255.254 for hosts IP assignment.

    It assumes L3 only has 1 ipRange. Multi ipRange will impact test, since
    host IP can only belong to 1 subnet.

    It assumes different L3 should not have same ipRange, although they are 
    in different vlans. e.g. you can't config 2 L3 with 10.10.0.1~10.10.127.255
    , although 1 vlan is 20, another is 21. From host 2 bridge IP, they will be
    assigned with same subnet. Then test connection will not be routed to 
    right place. 
    
    Test should avoid changing host's default eth0's ip address. If Host's 
    default network device (for zstack management) is not eth0, please change 
    HostDefaultEth.
    '''
    def _do_set_host_l2_ip(host_pub_ip, next_avail_ip, dev_name):
        #Has to use use br_eth0_vlan device to assign ip address,
        #as guest vlan device can't ping each other in nested env.
        #This may be wrong, but using bridge ip works.
        cmd_ip = host_plugin.SetDeviceIpCmd() 
        cmd_ip.ethname = dev_name
        cmd_ip.ip = next_avail_ip
        cmd_ip.netmask = l3_ip_ranges.netmask
        _lib_assign_host_l3_ip(host_pub_ip, cmd_ip)
        test_util.test_logger("Successfully config %s to [host:] %s [dev:] %s with IP: %s" % (next_avail_ip, host_pub_ip, dev_name, next_avail_ip))
        if not linux.wait_callback_success(lib_check_directly_ping, next_avail_ip, 10, 1):
            test_util.test_warn("[host:] %s [IP:] %s is Not connectable after 10 seconds. This will make future testing failure." % (host_pub_ip, next_avail_ip))
        return next_avail_ip

    def _generate_and_save_host_l2_ip(host_pub_ip, dev_name):
        host_pub_ip_list = host_pub_ip.split('.')

        host_ip_dict = lib_get_stored_host_ip_dict(dev_name)
        if host_ip_dict and host_ip_dict.has_key(host_pub_ip):
            next_avail_ip = host_ip_dict[host_pub_ip]
            return next_avail_ip

        net_address = l3_ip_ranges.startIp.split('.')
        net_address[2] = host_pub_ip_list[2]
        net_address[3] = host_pub_ip_list[3]
        net_address = '.'.join(net_address)
        
        next_avail_ip = _lib_gen_host_next_ip_addr(net_address, None)
        host_ip_dict = {host_pub_ip: next_avail_ip}
        #following lines generate not fixed host ip address.
        #if not host_ip_dict or not isinstance(host_ip_dict, dict):
        #    next_avail_ip = _lib_gen_host_next_ip_addr(net_address, None)
        #    host_ip_dict = {host_pub_ip: next_avail_ip}
        #else:
        #    next_avail_ip = _lib_gen_host_next_ip_addr(net_address, \
        #            host_ip_dict.values())
        #    host_ip_dict[host_pub_ip] = next_avail_ip
        lib_set_host_ip_dict(dev_name, host_ip_dict)
        return next_avail_ip

    def _set_host_l2_ip(host_pub_ip):
        br_ethname = 'br_%s' % l2.physicalInterface
        if l2_vlan:
            br_ethname = '%s_%s' % (br_ethname, l2_vlan)
        if br_ethname == 'br_%s' % HostDefaultEth:
            test_util.test_warn('Dangours: should not change host default network interface config for %s' % br_dev)
            return

        next_avail_ip = _generate_and_save_host_l2_ip(host_pub_ip, br_ethname)
        #if ip has been set to other host, following code will do something wrong.
        #if lib_check_directly_ping(next_avail_ip):
        #    test_util.test_logger("[host:] %s [bridge IP:] %s is connectable. Skip setting IP." % (host_pub_ip, next_avail_ip))
        #    return next_avail_ip
        #else:
        #    return _do_set_host_l2_ip(host_pub_ip, next_avail_ip)
    
        return _do_set_host_l2_ip(host_pub_ip, next_avail_ip, br_ethname)

    with lock.FileLock('lib_assign_host_l2_ip'):
        host_pub_ip = host.managementIp

        l2_vlan = lib_get_l2_vlan(l2.uuid)
        if not l2_vlan:
            l2_vlan = ''
            if l2.physicalInterface == HostDefaultEth:
                test_util.test_logger('Not Vlan. Will not change br_%s ip.' \
                        % HostDefaultEth)
                return host_pub_ip
            else:
                test_util.test_logger('%s might be manually created vlan dev.' \
                        % l2.physicalInterface)

        else:
            l2_vlan = str(l2_vlan)
    
        l3 = lib_get_l3_by_l2(l2.uuid)[0]
        if l3.system:
            test_util.test_logger('will not change system management network l3: %s' % l3.name)
            return 

        l3_ip_ranges = l3.ipRanges[0]
        if (l3_ip_ranges.netmask != '255.255.0.0'):
            test_util.test_warn('L3 name: %s uuid: %s network [mask:] %s is not 255.255.0.0 . Will not assign IP to host. Please change test configuration to make sure L3 network mask is 255.255.0.0.' % (l3.name, l3.uuid, l3_ip_ranges.netmask))
            return

        #Need to set vlan bridge ip address for local host firstly. 
        cond = res_ops.gen_query_conditions('hypervisorType', '=', inventory.KVM_HYPERVISOR_TYPE)
        all_hosts_ips = res_ops.query_resource_fields(res_ops.HOST, cond, None, \
                ['managementIp'])

        for host_ip in all_hosts_ips:
            #if current host is ZStack host, will set its bridge l2 ip firstly.
            if linux.is_ip_existing(host_ip.managementIp):
                current_host_ip = host_ip.managementIp
                _set_host_l2_ip(current_host_ip)
                break
        else:
            test_util.test_logger("Current machine is not in ZStack Hosts. Will directly add vlan device:%s and set ip address." % l2_vlan)
            any_host_ip = all_hosts_ips[0].managementIp
            if not linux.is_network_device_existing(l2.physicalInterface):
                test_util.test_fail("network device: %s is not on current test machine. Test machine needs to have same network connection with KVM Hosts." % l2.physicalInterface)

            current_host_ip = linux.find_route_interface_ip_by_destination_ip(any_host_ip)
            if not current_host_ip:
                current_host_ip = '127.0.0.1'
            if l2_vlan:
                dev_name = '%s.%s' % (l2.physicalInterface, l2_vlan)
                br_dev = 'br_%s_%s' % (l2.physicalInterface, l2_vlan)
            else:
                dev_name = l2.physicalInterface
                br_dev = 'br_%s' % dev_name

            if br_dev == 'br_%s' % HostDefaultEth:
                test_util.test_warn('Dangours: should not change host default network interface config for %s' % br_dev)
                return

            next_avail_ip = _generate_and_save_host_l2_ip(current_host_ip, \
                    br_dev)

            if not linux.is_ip_existing(next_avail_ip):
                if l2_vlan:
                    if not linux.is_network_device_existing(br_dev):
                        linux.create_vlan_eth(l2.physicalInterface, l2_vlan, \
                                next_avail_ip, l3_ip_ranges.netmask)
                        linux.create_bridge(br_dev, dev_name)
                        test_util.test_logger('create bridge:%s and set ip:%s' % (br_dev, next_avail_ip))
                    else:
                        linux.set_device_ip(br_dev, next_avail_ip, \
                                l3_ip_ranges.netmask)
                        test_util.test_logger('set ip:%s for bridge: %s' % (next_avail_ip, br_dev))

                else:
                    if not linux.is_network_device_existing(dev_name):
                        test_util.test_warn('l2 dev: %s does not exist' \
                                % dev_name)
                    else:
                        if not linux.is_network_device_existing(br_dev):
                            linux.set_device_ip(dev_name, next_avail_ip, \
                                    l3_ip_ranges.netmask)
                            linux.create_bridge(br_dev, dev_name)
                            test_util.test_logger('create bridge:%s and set ip:%s' % (br_dev, next_avail_ip))
                        else:
                            linux.set_device_ip(br_dev, next_avail_ip, \
                                    l3_ip_ranges.netmask)
                            test_util.test_logger('set ip:%s for bridge: %s' % (next_avail_ip, br_dev))


        #set remote host ip address
        if not linux.is_ip_existing(host_pub_ip):
            _set_host_l2_ip(host_pub_ip)

#host_l2_ip db should do regular cleanup, as its file size will be increased. 
#the function should be put into suite_teardown.
def lib_cleanup_host_ip_dict():
    host_ip_file = filedb.ZSTACK_FILEDB_DIR + HostL2IpDb
    if os.path.exists(host_ip_file):
        host_ip_db = filedb.FileDB(HostL2IpDb)
        db_dict = host_ip_db.get_all()
        for device, ip_info in db_dict.iteritems():
            for host in ip_info.keys():
                _lib_flush_host_l2_ip(host, device)

        os.remove(host_ip_file)

def lib_network_check(target_ip, target_port, expect_result=True):
    '''
    check target machine's target port connectibility
    '''
    #if not lib_check_system_cmd('telnet'):
    if not lib_check_system_cmd('nc'):
        return False == expect_result

    try:
        #shell.call('echo "quit" | telnet %s %s|grep "Escape character"' % (target_ip, target_port))
        shell.call('nc -w1 %s %s' % (target_ip, target_port))
        test_util.test_logger('check target: %s port: %s connection success')
        return True == expect_result
    except:
        test_util.test_logger('check target: %s port: %s connection failed')
        return False == expect_result

def lib_wait_target_down(target_ip, target_port, timeout=60):
    '''
        wait for target "machine" shutdown by checking its network connection, 
        until timeout. 
    '''
    def wait_network_check(param_list):
        return lib_network_check(param_list[0], param_list[1], param_list[2])

    return linux.wait_callback_success(wait_network_check, (target_ip, target_port, False), timeout)

def lib_wait_target_up(target_ip, target_port, timeout=60):
    '''
        wait for target "machine" startup by checking its network connection, 
        until timeout. 
    '''
    def wait_network_check(param_list):
        return lib_network_check(param_list[0], param_list[1], param_list[2])

    return linux.wait_callback_success(wait_network_check, (target_ip, target_port, True), timeout)

#-----------Get L2 Network resource-------------
def lib_get_l2s():
    return res_ops.get_resource(res_ops.L2_NETWORK, session_uuid=None)

def lib_get_l2s_uuid_by_vm(vm):
    l3_uuids = lib_get_l3s_uuid_by_vm(vm)
    all_l3s = lib_get_l3s()
    l2_uuids = []
    for l3 in all_l3s :
        if l3.uuid in l3_uuids:
            l2_uuids.append(l3.l2NetworkUuid)
    return l2_uuids 

def lib_get_private_l2s_by_vm(vm):
    '''
    Will return VM's l2 inventory list, who are not belonged to public or
    management L2.
    '''
    l3_uuids = lib_get_private_l3s_uuid_by_vm(vm)
    all_l3s = lib_get_l3s()
    l2_uuids = []
    for l3 in all_l3s :
        if l3.uuid in l3_uuids:
            l2_uuids.append(l3.l2NetworkUuid)

    cond = res_ops.gen_query_conditions('uuid', 'in', ','.join(l2_uuids))
    return res_ops.query_resource(res_ops.L2_NETWORK, cond)

def lib_get_l2s_by_vm(vm):
    l2_uuids = lib_get_l2s_uuid_by_vm(vm)

    l2s = []
    all_l2s = lib_get_l2s()
    for l2 in all_l2s:
        if l2.uuid in l2_uuids:
            l2s.append(l2)

    return l2s

def lib_get_l2_vlan(l2_uuid, session_uuid=None):
    '''
        return vlan value for L2. If L2 doesn't have vlan, will return None
    '''
    #conditions = res_ops.gen_query_conditions('uuid', '=', l2_uuid)
    #l2_vlan = res_ops.query_resource(res_ops.L2_VLAN_NETWORK, conditions, session_uuid)
    #if not l2_vlan:
    #    test_util.test_logger('Did not find L2: %s ' % l2_uuid)
    #    return None
    #else:
    #    return l2_vlan[0].vlan
    l2_vlan = res_ops.get_resource(res_ops.L2_VLAN_NETWORK, session_uuid, uuid=l2_uuid)
    if l2_vlan:
        return l2_vlan[0].vlan
    test_util.test_logger('L2: %s did not have vlan. ' % l2_uuid)
    return None

#-----------Get L3 Network resource-------------
def lib_get_l3_uuid_by_nic(nic_uuid, session_uuid=None):
    conditions = res_ops.gen_query_conditions('uuid', '=', nic_uuid)
    vm_nics = res_ops.query_resource(res_ops.VM_NIC, conditions)
    return vm_nics[0].l3NetworkUuid

def lib_get_l3_service_type(l3_uuid):
    '''
        Get L3 Network Service type, e.g. DNS, SNAT, DHCP etc.
    '''
    l3 = lib_get_l3_by_uuid(l3_uuid)
    service_type = []
    for service in l3.networkServices:
        service_type.append(service.networkServiceType)
    return service_type

def lib_get_l3_by_uuid(l3_uuid, session_uuid=None):
    conditions = res_ops.gen_query_conditions('uuid', '=', l3_uuid)
    l3 = res_ops.query_resource(res_ops.L3_NETWORK, conditions)
    if l3:
        return l3[0]

def lib_get_l3s_uuid_by_vm(vm):
    vmNics = vm.vmNics
    l3s = []
    for vmnic in vmNics:
        l3s.append(vmnic.l3NetworkUuid)

    return l3s

def lib_get_private_l3s_uuid_by_vm(vm):
    '''
    Will return all l3 uuids, if they are not belonged to public network or 
    management network
    '''
    vmNics = vm.vmNics
    l3s = []
    for vmnic in vmNics:
        if not vmnic.metaData or (int(vmnic.metaData) & 4 == 4):
            l3s.append(vmnic.l3NetworkUuid)

    return l3s

def lib_get_l3s_by_vm(vm):
    '''
    Get VM's all L3 inventories
    '''
    l3s_uuid = ','.join(lib_get_l3s_uuid_by_vm(vm))
    conditions = res_ops.gen_query_conditions('uuid', 'in', l3s_uuid)
    l3s = res_ops.query_resource(res_ops.L3_NETWORK, conditions)
    if l3s:
        return l3s

def lib_get_l3s_service_type(vm):
    l3s = lib_get_l3s_by_vm(vm)
    if not l3s:
        test_util.test_logger('Did not find l3 for [vm:] %s' % vm.uuid)
        return False
    svr_type = []
    for l3 in l3s:
        l3_svr = lib_get_l3_service_type(l3.uuid)
        if l3_svr:
            svr_type.extend(l3_svr)

    return list(set(svr_type))

def lib_get_l3_by_l2(l2_uuid):
    all_l3s = lib_get_l3s()
    l3s = []
    for l3 in all_l3s:
        if l3.l2NetworkUuid == l2_uuid:
            l3s.append(l3)
    if not l3s:
        test_util.test_logger('Did not find l3 for [l2:] %s' % l2_uuid)

    return l3s

#get VM's IP based on providing L3 uuid
def lib_get_vm_ip_by_l3(vm, l3_uuid):
    for nic in vm.vmNics:
        if nic.l3NetworkUuid == l3_uuid:
            return nic.ip

All_L3 = []
PickUp_Limited = 5
def lib_get_random_l3(l3_desc = None, zone_uuid = None):
    '''
If not provide l3 description, it will return a random l3.
If providing a zone uuid, it will return a random l3 from given zone. 

Should remove "system=true" l3 network.

Due to too many l3 network in multi hosts testing. The Random will only pick up
 the first 5 l3 networks, if there is only 1 zone. If there are multi zones, it
 will pick up first 3 l3 networks for first 2 zones. 
    '''
    global All_L3
    global PickUp_Limited
    cond = res_ops.gen_query_conditions('state', '=', 'Enabled')
    cond = res_ops.gen_query_conditions('system', '!=', True, cond)
    if l3_desc:
        cond = res_ops.gen_query_conditions('description', '=', l3_desc, cond)
        if zone_uuid:
            cond = res_ops.gen_query_conditions('zoneUuid', '=', zone_uuid, \
                    cond)
    else:
        if zone_uuid:
            cond = res_ops.gen_query_conditions('zoneUuid', '=', zone_uuid, \
                    cond)
        else:
            if All_L3:
                return random.choice(All_L3[0:PickUp_Limited])

    l3_invs = res_ops.query_resource(res_ops.L3_NETWORK, cond)
    if not l3_desc:
        if not zone_uuid:
            All_L3 = list(l3_invs)
            return random.choice(All_L3[0:PickUp_Limited])
        else:
            return random.choice(l3_invs[0:PickUp_Limited])

    return random.choice(l3_invs)

def lib_get_random_l3_conf_from_plan(l3_net_desc = None, zone_name = None):
    global PickUp_Limited
    if not l3_net_desc and All_L3:
        return random.choice(All_L3[0:PickUp_Limited])
    l3_nets = lib_get_l3_confs_from_plan(zone_name)

    if l3_net_desc:
        for l3 in l3_nets:
            if l3.description_ == l3_net_desc:
                return l3
    else:
        if len(l3_nets) < PickUp_Limited:
            choice_limit = len(l3_nets)
        else:
            choice_limit = PickUp_Limited

        return random.choice(l3_nets[0:PickUp_Limited])

def lib_get_5_l3_network():
    '''
    return l3 inventory
    '''
    if not All_L3:
        lib_get_random_l3()
    return All_L3[0:PickUp_Limited]

def lib_get_limited_l3_network(start_l3, end_l3):
    '''
    return l3 inventory
    '''
    if not All_L3:
        lib_get_random_l3()
    return All_L3[start_l3:end_l3]

def lib_get_l3s():
    return res_ops.get_resource(res_ops.L3_NETWORK, session_uuid=None)

def lib_get_l3_by_name(l3_name):
    cond = res_ops.gen_query_conditions('name', '=', l3_name)
    l3s = res_ops.query_resource_with_num(res_ops.L3_NETWORK, cond, None, 0, 1)
    if l3s:
        return l3s[0]
    test_util.test_logger("Did not find L3 by [l3 name:] %s" % l3_name)

def lib_get_l3_confs_from_plan(zone_name = None):
    '''
    If providing zone_name, will only return the zone's L3 configurations.
    If not, will provide all zones' l3 configurations
    '''
    l2s = []
    l3_nets = []
    for zone in deploy_config.zones.get_child_node_as_list('zone'):
        if zone_name and zone_name != zone.name_:
            continue
        if xmlobject.has_element(zone, 'l2Networks'):
            if xmlobject.has_element(zone.l2Networks, 'l2NoVlanNetwork'):
                l2NoVlanNet = zone.l2Networks.l2NoVlanNetwork
                if l2NoVlanNet:
                    if isinstance(l2NoVlanNet, list):
                        l2s.extend(l2NoVlanNet)
                    else:
                        l2s.append(l2NoVlanNet)

            if xmlobject.has_element(zone.l2Networks, 'l2VlanNetwork'):
                l2VlanNet = zone.l2Networks.l2VlanNetwork
                if l2VlanNet:
                    if isinstance(l2VlanNet, list):
                        l2s.extend(l2VlanNet)
                    else:
                        l2s.append(l2VlanNet)

    for l2 in l2s:
        l3s = l2.l3Networks.l3BasicNetwork
        if not isinstance(l3s, list):
            l3_nets.append(l3s)
        else:
            l3_nets.extend(l3s)

    return l3_nets

def lib_get_all_living_vms():
    conditons = res_ops.gen_query_conditions('state', '=', vm_header.RUNNING)
    vms = res_ops.query_resource(res_ops.VM_INSTANCE, conditons)
    return vms

def lib_find_vms_same_l3_uuid(vm_list):
    vms_nics = []
    for vm in vm_list:
        vms_nics.append([])
        for nic in vm.vmNics:
            vms_nics[-1].append(nic.l3NetworkUuid)

    for l3_uuid in vms_nics[0]:
        for other_vm in range(len(vms_nics) - 1):
            if not l3_uuid in vms_nics[other_vm + 1]:
                continue
            if other_vm == (len(vms_nics) - 2):
                return l3_uuid

def lib_gen_l3_nic_dict_by_nics(nic_list):
    l3_nic_dict = {}
    for nic in nic_list:
        if not nic.l3NetworkUuid in l3_nic_dict.keys():
            l3_nic_dict[nic.l3NetworkUuid] = [nic]
        else:
            l3_nic_dict[nic.l3NetworkUuid].append(nic)

    return l3_nic_dict

#-----------Get VM resource-------------
def lib_is_vm_running(vm_inv):
    if vm_inv.state == 'Running':
        return True

    return False

def lib_get_vm_by_uuid(vm_uuid):
    conditions = res_ops.gen_query_conditions('uuid', '=', vm_uuid)
    vms = res_ops.query_resource(res_ops.VM_INSTANCE, conditions)
    if vms:
        return vms[0]

def lib_get_vm_nic_by_l3(vm, l3_uuid):
    '''
        @params: 
            vm is vm inventory
            l3_uuid: l3 network uuid
        @return:
            The vm nic inventory
    '''
    for vmNic in vm.vmNics:
        if vmNic.l3NetworkUuid == l3_uuid:
            return vmNic

def lib_get_vm_nic_by_vr(vm, vr):
    '''
    Find VM's the guest (private) nic by giving its VR VM.
    If the guest nic is also a public nic (like public l3 also provide DNS/DHCP
     service), it will also return it.
    '''
    test_util.test_logger('vm: %s, vr: %s' % (vm.uuid, vr.uuid))
    if vm.uuid == vr.uuid:
        return lib_find_vr_pub_nic(vr)

    nics = vm.vmNics
    for vr_nic in vr.vmNics:
        if int(vr_nic.metaData) & 4 == 4 :
            for nic in nics:
                if nic.l3NetworkUuid == vr_nic.l3NetworkUuid:
                    return nic

def lib_get_vm_internal_id(vm):
    cmd = "virsh dumpxml %s|grep internalId|awk -F'>' '{print $2}'|\
            awk -F'<' '{print $1}'" % vm.uuid
    host_ip = lib_find_host_by_vm(vm).managementIp
    rsp = lib_execute_sh_cmd_by_agent(host_ip, cmd)
    if rsp.return_code == 0:
        ret = rsp.stdout.strip()
        test_util.test_logger('Find [vm:] %s [internalId:] %s on [host:] %s iptables' % (vm.uuid, ret, host_ip))
        return ret
    else:
        test_util.test_logger('shell error info: %s' % rsp.stderr)
        #test_util.test_logger('shell command: %s' % rsp.command)
        test_util.test_logger('Can not get [vm:] %s internal ID on [host:] %s' % (vm.uuid, host_ip))
        return None

def lib_get_root_image_from_vm(vm):
    for volume in vm.allVolumes:
        if volume.type == vol_header.ROOT_VOLUME:
            vm_root_image_uuid = volume.rootImageUuid

    if not vm_root_image_uuid:
        test_util.logger("Can't find root device for [vm:] %s" % vm.uuid)
        return False

    condition = res_ops.gen_query_conditions('uuid', '=', vm_root_image_uuid)
    image = res_ops.query_resource(res_ops.IMAGE, condition)[0]
    return image

def lib_get_vm_username(vm):
    image = lib_get_root_image_from_vm(vm)
    image_plan = lib_get_image_from_plan(image)
    if image_plan:
        username = image_plan.username_
    else:
        #image might be created from other root image template
        #So there isn't pre-set username/password. Try to use default username.
        username = os.environ.get('imageUsername')
    return username

def lib_get_vm_password(vm):
    image = lib_get_root_image_from_vm(vm)
    image_plan = lib_get_image_from_plan(image)
    if image_plan:
        password = image_plan.password_
    else:
        #image might be created from other root image template
        #So there isn't pre-set username/password. try to use default password.
        password = os.environ.get('imagePassword')
    return password

def lib_get_nic_by_uuid(vm_nic_uuid, session_uuid=None):
    if vm_nic_uuid:
        condition = res_ops.gen_query_conditions('uuid', '=', vm_nic_uuid)
        return res_ops.query_resource(res_ops.VM_NIC, condition)[0]
    else:
        test_util.test_logger('vm_nic_uuid is None, so can not get nic inventory')

def lib_get_nic_by_ip(ip_addr, session_uuid=None):
    conditions = res_ops.gen_query_conditions('ip', '=', ip_addr)
    vm_nic = res_ops.query_resource(res_ops.VM_NIC, conditions, session_uuid)[0]
    return vm_nic 

def lib_get_vm_by_ip(ip_addr, session_uuid=None):
    vm_nic = lib_get_nic_by_ip(ip_addr, session_uuid)
    vm_uuid = vm_nic.vmInstanceUuid
    return lib_get_vm_by_uuid(vm_uuid)

def lib_get_vm_by_nic(vm_nic_uuid, session_uuid=None):
    '''
    use compound query method to find vm_inv by vm_nic_uuid. 
    '''
    conditions = res_ops.gen_query_conditions('vmNics.uuid', '=', vm_nic_uuid)
    vm_invs = res_ops.query_resource(res_ops.VM_INSTANCE, conditions, \
            session_uuid)
    if not vm_invs:
        test_util.test_logger('Could not find VM by [vmNic:] %s ' % vm_nic_uuid)
    else:
        return vm_invs[0]

def lib_is_vm_l3_has_vr(vm):
    vm_nics = vm.vmNics
    vr_l3 = lib_get_all_vr_l3_uuid()
    for nic in vm_nics:
        if nic.l3NetworkUuid in vr_l3:
            test_util.test_logger('[vm:] %s [l3 uuid:] %s has VR network .' % (vm.uuid, nic.l3NetworkUuid))
            return True

    test_util.test_logger('[vm:] %s l3 network did not find VR network .' % vm.uuid)
    return False

#-----------Get Virtual Router resource-------------
def lib_find_vr_mgmt_nic(vm):
    for nic in vm.vmNics:
        if nic.hasattr('metaData') and (int(nic.metaData) & 2 == 2):
            return nic

def lib_find_vr_pub_nic(vm):
    for nic in vm.vmNics:
        if nic.hasattr('metaData') and (int(nic.metaData) & 1 == 1):
            return nic

def lib_find_vr_private_nic(vm):
    for nic in vm.vmNics:
        if nic.hasattr('metaData') and (int(nic.metaData) & 4 == 4):
            return nic

def lib_find_vr_by_pri_l3(l3_uuid):
    '''
    private l3 can only be belonged to 1 VR. So the return should be explicit VR.
    '''
    #use compound query condition
    condition = res_ops.gen_query_conditions('vmNics.l3NetworkUuid', '=', \
            l3_uuid)
    condition = res_ops.gen_query_conditions('vmNics.metaData', '!=', '1', \
            condition)
    condition = res_ops.gen_query_conditions('vmNics.metaData', '!=', '2', \
            condition)
    condition = res_ops.gen_query_conditions('vmNics.metaData', '!=', '3', \
            condition)
    vrs = res_ops.query_resource_with_num(res_ops.APPLIANCE_VM, condition, \
            None, 0, 1)

    if vrs:
        return vrs[0]

def lib_find_vr_by_l3_uuid(l3_uuid):
    '''
    @params: l3_uuid could be any l3_uuid. 
    l3_uuid could be any of management L3, public L3 and private L3.

    @return: will return all VRs, which has vnic belongs to l3_uuid.  
    '''
    vrs = lib_get_all_vrs()
    target_vrs = []
    for vr in vrs:
        for vm_nic in vr.vmNics:
            if vm_nic.l3NetworkUuid == l3_uuid:
                target_vrs.append(vr)

    return target_vrs

def lib_find_vr_by_vm_nic(vm_nic, vm=None):
    '''
    Return the exact VR by giving a vm nic. Will find NIC's L3 network's VR.
    @params:
    vm_nic: nic inventory
    vm: [Optional] vm inventory
    '''
    if not vm:
        if vm_nic:
            vm = lib_get_vm_by_nic(vm_nic.uuid)
        else:
            test_util.test_warn('Can not find VR, since no VM and VM_NIC is provided.')
            return

    l3_uuid = vm_nic.l3NetworkUuid
    return lib_find_vr_by_pri_l3(l3_uuid)

def lib_find_vr_pub_ip(vr_vm):
    vr_guest_nic_ip = lib_find_vr_pub_nic(vr_vm).ip
    if not vr_guest_nic_ip:
        test_util.test_fail('cannot find public nic IP on [virtual router uuid:] %s' % vr_vm.uuid)
    return vr_guest_nic_ip

def lib_find_vr_mgmt_ip(vr_vm):
    vr_guest_nic_ip = lib_find_vr_mgmt_nic(vr_vm).ip
    if not vr_guest_nic_ip:
        test_util.test_fail('cannot find management nic IP on [virtual router uuid:] %s' % vr_vm.uuid)
    return vr_guest_nic_ip

def lib_find_vr_private_ip(vr_vm):
    vr_guest_nic_ip = lib_find_vr_private_nic(vr_vm).ip
    if not vr_guest_nic_ip:
        test_util.test_fail('cannot find private nic IP on [virtual router uuid:] %s' % vr_vm.uuid)
    return vr_guest_nic_ip

def lib_print_vr_dhcp_tables(vr_vm):
    '''
    Print VR DHCP tables. This API is usually be called, when checking DHCP
    result failed.

    params:
        vr_vm: target VR VM.

    return:
        False: ssh VR or print VR DHCP table command execution failed.
    '''
    #Check VR DNS table
    shell_cmd = host_plugin.HostShellCmd()
    shell_cmd.command = 'echo cat /etc/hosts.dhcp:; cat /etc/hosts.dhcp; echo cat /etc/hosts.leases: ; cat /etc/hosts.lease'
    vr_public_ip = lib_find_vr_mgmt_ip(vr_vm)
    lib_install_testagent_to_vr_with_vr_vm(vr_vm)
    rspstr = http.json_dump_post(testagent.build_http_path(vr_public_ip, host_plugin.HOST_SHELL_CMD_PATH), shell_cmd)
    rsp = jsonobject.loads(rspstr)
    if rsp.return_code != 0:
        test_util.test_logger('Can not get [VR:] %s DHCP tables, error log is: %s ' % (vr_vm.uuid, rsp.stderr))
        return False
    else:
        test_util.test_logger("[VR:] %s VR DHCP tables are: \n%s" % (vr_vm.uuid, rsp.stdout))

def lib_print_vr_network_conf(vr_vm):
    '''
    Print VR network config. This API is usually be called, when do testing
    is failed. 

    params: 
        vr_vm: target VR VM.

    return:
        False: ssh VR or print VR network config failed. 
    '''
    #Check VR DNS table
    lib_install_testagent_to_vr_with_vr_vm(vr_vm)
    shell_cmd = host_plugin.HostShellCmd()
    shell_cmd.command = 'echo cat /etc/resolv.conf:; cat /etc/resolv.conf; echo ifconfig: ; ifconfig; echo iptables-save:; iptables-save'
    vr_public_ip = lib_find_vr_mgmt_ip(vr_vm)
    rspstr = http.json_dump_post(testagent.build_http_path(vr_public_ip, host_plugin.HOST_SHELL_CMD_PATH), shell_cmd)
    rsp = jsonobject.loads(rspstr)
    if rsp.return_code != 0:
        test_util.test_logger('Can not get [VR:] %s network config, error log is: %s ' % (vr_vm.uuid, rsp.stderr))
        return False
    else:
        test_util.test_logger("[VR:] %s network configuration information is: \n%s" % (vr_vm.uuid, rsp.stdout))
        return True

def lib_get_all_appliance_vms(session_uuid=None):
    vms = res_ops.get_resource(res_ops.APPLIANCE_VM, session_uuid)
    return vms

def lib_get_all_vrs(session_uuid=None):
    conditions = res_ops.gen_query_conditions('applianceVmType', '=', 'VirtualRouter')
    vrs = res_ops.query_resource(res_ops.APPLIANCE_VM, conditions, session_uuid)
    return vrs

def lib_get_all_user_vms(session_uuid=None):
    conditions = res_ops.gen_query_conditions('type', '=', inventory.USER_VM_TYPE)
    vms = res_ops.query_resource(res_ops.VM_INSTANCE, conditions, session_uuid)
    return vms

def lib_does_l3_has_network_service(l3_uuid):
    cond = res_ops.gen_query_conditions('l3NetworkUuid', '=', l3_uuid)
    l3_serv = res_ops.query_resource(res_ops.NETWORK_SERVICE_PROVIDER_L3_REF,\
            cond)
    if l3_serv:
        return True

#return a vr list
def lib_find_vr_by_vm(vm, session_uuid=None):
    '''
    Find VM's all VRs and return a list, which include VR inventory objects.
    If vm is VR, will return itself in a list.

    params:
        - vm: vm inventory object. 
        - session_uuid: [Optional] current session_uuid, default is admin.
    '''
    if lib_is_vm_vr(vm):
        return [vm]

    vm_l3s = []
    for vm_nic in vm.vmNics:
        vm_l3s.append(vm_nic.l3NetworkUuid)

    #need to remove metaData l3NetworkUuid 
    tmp_l3_list = list(vm_l3s)
    for l3_uuid in tmp_l3_list:
        if not lib_does_l3_has_network_service(l3_uuid):
            vm_l3s.remove(l3_uuid)

    if not vm_l3s:
        return []

    cond = res_ops.gen_query_conditions('vmNics.l3NetworkUuid', 'in', \
            ','.join(vm_l3s))
    cond = res_ops.gen_query_conditions('vmNics.metaData', '!=', '1', cond)
    cond = res_ops.gen_query_conditions('vmNics.metaData', '!=', '2', cond)
    cond = res_ops.gen_query_conditions('vmNics.metaData', '!=', '3', cond)
    vrs = res_ops.query_resource(res_ops.APPLIANCE_VM, cond, session_uuid)

    if not vrs:
        test_util.test_logger("Cannot find VM: [%s] 's Virtual Router VM" \
                % vm.uuid)

    return vrs

def lib_get_all_vr_l3_uuid():
    vr_l3 = []
    all_l3 = lib_get_l3s()
    for l3 in all_l3:
        if len(l3.networkServices) != 0:
            vr_l3.append(l3.uuid)

    return vr_l3

#-----------VM volume operations-------------
def lib_create_volume_from_offering(volume_creation_option=test_util.VolumeOption(), session_uuid=None):
    disk_offering_uuid = volume_creation_option.get_disk_offering_uuid()
    if not disk_offering_uuid :
        result = res_ops.get_resource(res_ops.DISK_OFFERING, session_uuid)
        disk_offering_uuid = random.choice(result).uuid
        volume_creation_option.set_disk_offering_uuid(disk_offering_uuid)

    name = volume_creation_option.get_name()
    if not name:
        name = "TestVolume"
        volume_creation_option.set_name(name)

    #[Inlined import]
    import zstackwoodpecker.zstack_test.zstack_test_volume as zstack_volume_header
    volume = zstack_volume_header.ZstackTestVolume()
    volume.set_creation_option(volume_creation_option)
    volume.create()

    return volume
          
def lib_delete_volume(volume_uuid, session_uuid=None):
    result = vol_ops.delete_volume(volume_uuid, session_uuid)
    test_util.test_logger('[volume] uuid: %s is deleted.' % volume_uuid)

def lib_retry_when_exception(function, params, times = 5):
    '''
    If some function might bring unstable result and when it failed, it will 
    rasie exception, this function will help to do retry. When it meets firstly
    pass, it will return the execution result. 
    '''
    result = False
    while times:
        try:
            result = function(*params)
        except Exception as e:
            times -= 1
            test_util.test_logger('Execute Function: %s meets exeception: %s , will retry: %s times' % (function.__name__, e, times))
            time.sleep(0.5)
        else:
            return result

    return False

def lib_attach_volume(volume_uuid, vm_uuid, session_uuid=None):
    result = lib_retry_when_exception(vol_ops.attach_volume, [volume_uuid, vm_uuid, session_uuid])
    test_util.test_logger('[volume:] uuid: %s is attached to [vm:] %s .' % (volume_uuid, vm_uuid))
    return result

def lib_detach_volume(volume_uuid, session_uuid=None):
    result = vol_ops.detach_volume(volume_uuid, session_uuid)
    test_util.test_logger('[volume:] uuid: %s is detached from [vm].' % volume_uuid)
    return result

#check if volumeInventory structure is existed.
def lib_check_volume_db_exist(volume):
    try:
        find_volume = res_ops.get_resource(res_ops.VOLUME, session_uuid=None, uuid=volume.uuid)[0]
    except Exception as e:
        test_util.test_logger('[volumeInventory uuid:] %s does not exist in database.' % volume.uuid)
        return False

    test_util.test_logger('[volumeInventory uuid:] %s exist in database.' % volume.uuid)
    return find_volume

def lib_get_volume_by_uuid(volume_uuid):
    try:
        conditions = res_ops.gen_query_conditions('uuid', '=', volume_uuid)
        volume = res_ops.query_resource(res_ops.VOLUME, conditions)[0]
        return volume
    except:
        test_util.test_logger('Did not find volume in database with [uuid:] %s' % volume_uuid)

def lib_get_volume_host(volume):
    try:
        primaryStorageUuid = volume.primaryStorageUuid
        if not primaryStorageUuid:
            test_util.test_logger('Did not find any primary storage for [volume:] %s. Can not find [host] for this volume. It mostly means the volume is not attached to any VM yet. ' % volume.uuid)
            return None

        conditions = res_ops.gen_query_conditions('uuid', '=', \
                primaryStorageUuid)

        ps_inv = res_ops.query_resource(res_ops.PRIMARY_STORAGE, conditions, None)[0]
        attached_cluster = ','.join(ps_inv.attachedClusterUuids)
        conditions = res_ops.gen_query_conditions('clusterUuid', 'in', \
                attached_cluster)
        conditions = res_ops.gen_query_conditions('state', '=', 'Enabled', \
                conditions)
        conditions = res_ops.gen_query_conditions('status', '=', \
                'Connected', conditions)
        
        host_invs = res_ops.query_resource(res_ops.HOST, conditions)

        if host_invs:
            host = host_invs[0]
            test_util.test_logger('Find [host:] %s for volume' % host.uuid)
            return host
        else:
            test_util.test_logger('Did not find any host, who attached primary storage: [%s] to hold [volume:] %s.' % (primaryStorageUuid, volume.uuid))
    except:
        test_util.test_logger('Could not find any host for [volume:] %s.' % volume.uuid)

#check if volume file is created in primary storage
def lib_check_volume_file_exist(volume, host=None):
    volume_installPath = volume.installPath
    if not volume_installPath:
        test_util.test_logger('[installPath] is Null for [volume uuid: ] %s .' % volume.uuid)
        return False
    if not host:
        host = lib_get_volume_host(volume)

    cmd = host_plugin.HostShellCmd()
    file_exist = "file_exist"
    cmd.command = '[ -f %s ] && echo %s' % (volume_installPath, file_exist)
    rspstr = http.json_dump_post(testagent.build_http_path(host.managementIp, host_plugin.HOST_SHELL_CMD_PATH), cmd)
    rsp = jsonobject.loads(rspstr)
    output = jsonobject.dumps(rsp.stdout)
    if file_exist in output:
        test_util.test_logger('[volume file: ] %s exist on [host name:] %s .' % (volume.uuid, host.name))
        return True
    else:
        test_util.test_logger('[volume file: ] %s does not exist on [host name:] %s .' % (volume.uuid, host.name))
        return False

#check if volume is attached to vm in Database
def lib_check_is_volume_attached_to_vm_in_db(vm, volume):
    find_volume = lib_check_volume_db_exist(volume)
    if not find_volume:
        return False

    if find_volume.vmInstanceUuid == vm.uuid:
        test_util.test_logger('[volume:] %s is attached to [vm:] %s in zstack database.' % (volume.uuid, vm.uuid))
        return find_volume
    else:
        test_util.test_logger('[volume:] %s is NOT attached to [vm:] %s in zstack database.' % (volume.uuid, vm.uuid))
        return False

#check if volume file is attached to vm
def lib_check_is_volume_attached_to_vm(vm, volume):
    find_volume = lib_check_is_volume_attached_to_vm_in_db(vm, volume)
    if not find_volume:
        return False

    if vm.state == vm_header.STOPPED:
        test_util.test_logger('[vm:] %s is stopped. Skip volume existence checking.' % volume.uuid)
        return True

    volume_installPath = volume.installPath
    if not volume_installPath:
        test_util.test_logger('[installPath] is Null for [volume uuid: ] %s .' % volume.uuid)
        return False
    host = lib_get_vm_host(vm)
    cmd = vm_plugin.VmStatusCmd()
    cmd.vm_uuids = [vm.uuid]
    rspstr = http.json_dump_post(testagent.build_http_path(host.managementIp, vm_plugin.VM_BLK_STATUS), cmd)
    rsp = jsonobject.loads(rspstr)
    output = jsonobject.dumps(rsp.vm_status[vm.uuid])
    if volume_installPath in output:
        test_util.test_logger('[volume file:] %s is found in [vm:] %s on [host:] %s .' % (volume.uuid, vm.uuid, host.managementIp))
        return True
    else:
        test_util.test_logger('[volume file:] %s is not found in [vm:] %s on [host:] %s .' % (volume.uuid, vm.uuid, host.managementIp))
        return False

def lib_get_primary_storage_by_vm(vm):
    ps_uuid = vm.allVolumes[0].primaryStorageUuid
    cond = res_ops.gen_query_conditions('uuid', '=', ps_uuid)
    ps = res_ops.query_resource(res_ops.PRIMARY_STORAGE, cond)[0]
    return ps

def lib_get_backup_storage_list_by_vm(vm, session_uuid=None):
    '''
    Return backup storage list which attached to the VM's zone.
    '''
    zone_uuid = vm.zoneUuid
    conditions = res_ops.gen_query_conditions('attachedZoneUuids', 'in', zone_uuid)
    bss = res_ops.query_resource(res_ops.BACKUP_STORAGE, conditions, session_uuid)
    if not bss:
        test_util.test_logger('Can not find [backup storage] record for [vm:] %s.' % vm.uuid)
    else:
        return bss

def lib_create_template_from_volume(volume_uuid, session_uuid=None):
    bs_uuid = res_ops.get_resource(res_ops.BACKUP_STORAGE, session_uuid)[0].uuid
    #[Inlined import]
    import zstackwoodpecker.zstack_test.zstack_test_image as zstack_image_header
    image = zstack_image_header.ZstackTestImage()
    image_creation_option = test_util.ImageOption()
    image_creation_option.set_backup_storage_uuid_list([bs_uuid])
    image_creation_option.set_root_volume_uuid(volume_uuid)
    image_creation_option.set_name('test_image')
    image.set_creation_option(image_creation_option)
    image.create()

    return image

def lib_get_root_volume(vm):
    '''
    get root volume inventory by vm inventory
    '''
    volumes = vm.allVolumes
    for volume in volumes:
        if volume.type == vol_header.ROOT_VOLUME:
            return volume

def lib_get_root_volume_uuid(vm):
    return vm.rootVolumeUuid

def lib_get_all_volumes(vm):
    return vm.allVolumes

#-----------Get Image resource-------------
#Assume all image are using same username and password
def lib_get_vr_image_username(vr_vm):
    username = lib_get_vr_image_from_plan(vr_vm).username_
    return username

def lib_get_vr_image_password(vr_vm):
    password = lib_get_vr_image_from_plan(vr_vm).password_
    return password

def lib_get_vr_image_from_plan(vr_vm=None):
    if vr_vm:
        return lib_get_image_from_plan(lib_get_root_image_from_vm(vr_vm))

    vr_image_name = os.environ.get('virtualRouterImageName')
    if not vr_image_name:
        test_util.logger("Can't find 'virtualRouterImageName' env params, which is used to identify vritual router image")
        return None

    images = deploy_config.images.image
    if not isinstance(images, list):
        if images.name_ == vr_image_name:
            return images
        else:
            return None
    for image in images:
        if image.name_ == vr_image_name:
            return image

def lib_get_image_from_plan(image):
    images = deploy_config.images.image
    if not isinstance(images, list):
        if images.name_ == image.name:
            return images
        else:
            return None
    for img in images:
        if img.name_ == image.name:
            return img

def lib_get_disk_offering_by_name(do_name):
    conditions = res_ops.gen_query_conditions('name', '=', do_name)
    disk_offering = res_ops.query_resource(res_ops.DISK_OFFERING, conditions)
    if not disk_offering:
        test_util.test_logger('Could not find disk offering with [name:]%s ' % do_name)
        return None
    else:
        return disk_offering[0]
    #disk_offerings = res_ops.get_resource(res_ops.DISK_OFFERING, session_uuid=None)
    #for disk_offering in disk_offerings:
    #    if disk_offering.name == do_name:
    #        return disk_offering

def lib_get_images():
    return res_ops.get_resource(res_ops.IMAGE, session_uuid=None)

def lib_get_root_images():
    cond = res_ops.gen_query_conditions('mediaType', '=', 'RootVolumeTemplate')
    return res_ops.query_resource(res_ops.IMAGE, cond)

def lib_get_data_images():
    cond = res_ops.gen_query_conditions('mediaType', '=', 'DataVolumeTemplate')
    return res_ops.query_resource(res_ops.IMAGE, cond)

def lib_get_ISO():
    cond = res_ops.gen_query_conditions('mediaType', '=', 'ISO')
    return res_ops.query_resource(res_ops.IMAGE, cond)

def lib_get_image_by_uuid(image_uuid, session_uuid = None):
    condition = res_ops.gen_query_conditions('uuid', '=', image_uuid)
    images = res_ops.query_resource(res_ops.IMAGE, condition, session_uuid)
    if images:
        return images[0]

def lib_get_vm_image(vm_inv):
    '''
    return vm_inv's image template inventory
    '''
    root_volume_inv = lib_get_root_image_from_vm(vm_inv)
    return lib_get_image_by_uuid(root_volume_inv.rootImageUuid)

def lib_get_not_vr_images():
    '''
    return all images, besides of the images for Virtual Router Offering
    '''
    images = lib_get_root_images()
    vr_offerings = res_ops.query_resource(res_ops.VR_OFFERING, [])
    vr_images = []
    for vr_offering in vr_offerings:
        vr_images.append(vr_offering.imageUuid)

    temp_images = list(images)
    for img in images:
        if img.uuid in vr_images:
            temp_images.remove(img)

    return temp_images

def lib_get_image_by_desc(img_desc):
    images = lib_get_images()
    for image in images:
        if image.description == img_desc:
            return image

def lib_get_image_by_name(img_name):
    cond = res_ops.gen_query_conditions('name', '=', img_name)
    images = res_ops.query_resource(res_ops.IMAGE, cond)
    if images:
        return images[0]

    test_util.test_logger("not find image with name: %s" % img_name)
    return False

def lib_remove_image_from_list_by_desc(images, img_desc):
    imgs = images
    for image in images:
        if image.description == img_desc:
            imgs.remove(image)

    return imgs

def lib_check_image_db_exist(image):
    imgs = test_stub.lib_get_images()
    for img in imgs:
        if img.uuid == image.uuid:
            test_util.test_logger('[image:] %s is found in zstack database' % img.uuid)
            return True
    test_util.test_logger('[image:] %s is not found in zstack database' % img.uuid)
    return False

#Should depend on backup storage uuid to get host info
def lib_check_backup_storage_image_file(image):
    image_url = image.url
    host = lib_get_backup_storage_host(image.backupStorageUuid)
    return lib_check_file_exist(host, image_url)

def lib_check_file_exist(host, file_path):
    command = 'ls -l %s' % file_path
    eout = ''
    try:
        (ret, out, eout) = ssh.execute(command, host.managementIp, host.username, host.password)
        test_util.test_logger('[file:] %s was found in [host:] %s' % (file_path, host.managementIp))
        return True
    except:
        #traceback.print_exc(file=sys.stdout)
        test_util.test_logger('Fail to execute: ssh [host:] %s with [username:] %s and [password:] %s to check [file:] %s . This might be expected behavior.'% (host.managementIp, host.username, host.password, file_path))
        test_util.test_logger('ssh execution stderr output: %s' % eout)
        test_util.test_logger(linux.get_exception_stacktrace())
        return False

def lib_check_two_files_md5(host1, file1, host2, file2):
    command1 = "md5sum %s" % file1
    command2 = "md5sum %s" % file2
    (ret, out1, eout) = ssh.execute(command1, host1.managementIp, host1.username, host1.password)
    (ret, out2, eout) = ssh.execute(command2, host2.managementIp, host2.username, host2.password)

    if out1.split[0] == out2.split[0]:
        test_util.test_logger('[file1:] %s and [file2:] %s MD5 checksum are same.' % (file1, file2))
        return True
    else:
        test_util.test_logger('[file1:] %s and [file2:] %s MD5 checksum are different' % (file1, file2))
        return False
    
def lib_delete_image(img_uuid, session_uuid=None):
    vol_ops.delete_image(img_uuid, session_uuid)

def lib_mkfs_for_volume(volume_uuid, vm_inv):
    '''
    Will check if volume's 1st partition could be mountable. If not, it will try
    to make a partition and make an ext3 file system on it. 
    @params:
        volume_uuid: the target volume's uuid
        vm_inv: the utility vm, which will help to make fs in volume. 
    '''
    volume = lib_get_volume_by_uuid(volume_uuid)

    #Root volume can not be detached. 
    if volume.type == vol_header.ROOT_VOLUME:
        test_util.test_logger("[volume:] %s is Root Volume. It can not be make filesystem." % volume_uuid)
        return False

    old_vm_uuid = None
    if volume.vmInstanceUuid:
        old_vm_uuid = volume.vmInstanceUuid
        lib_detach_volume(volume_uuid)

    lib_attach_volume(volume_uuid, vm_inv.uuid)

    mount_point = '/tmp/zstack/mnt'
    import tempfile
    script_file = tempfile.NamedTemporaryFile(delete=False)
    script_file.write('''
mkdir -p %s
device=`fdisk -l|grep Disk|tail -2|head -1|awk '{print $2}'|awk -F: '{print $1}'`
mount ${device}1 %s
if [ $? -ne 0 ]; then
    fdisk $device <<EOF
n
p
1


w
EOF
    mkfs.ext3 ${device}1
else
    umount %s
fi
''' % (mount_point, mount_point, mount_point))
    script_file.close()

    if not lib_execute_shell_script_in_vm(vm_inv, script_file.name):
        test_util.test_fail("make partition and make filesystem operation failed in [volume:] %s in [vm:] %s" % (volume_uuid, vm_inv.uuid))

        lib_detach_volume(volume_uuid)
        os.unlink(script_file.name)
        return False

    test_util.test_logger("Successfully make partition and make filesystem operation in [volume:] %s in [vm:] %s" % (volume_uuid, vm_inv.uuid))

    lib_detach_volume(volume_uuid)
    os.unlink(script_file.name)

    if old_vm_uuid:
        lib_attach_volume(volume_uuid, old_vm_uuid)

    return True

#-----------Snapshot Operations-----------
def lib_get_volume_snapshot_tree(volume_uuid = None, tree_uuid = None, session_uuid = None):
    if not volume_uuid and not tree_uuid:
        test_util.test_logger("volume_uuid and tree_uuid should not be None at the same time")
        return 

    import apibinding.api_actions as api_actions
    action = api_actions.GetVolumeSnapshotTreeAction()
    action.volumeUuid = volume_uuid
    action.treeUuid = tree_uuid
    ret = acc_ops.execute_action_with_session(action, session_uuid).inventories
    return ret

#-----------Security Group Operations-------------
def lib_create_security_group(name=None, desc=None, session_uuid=None):
    if not name:
        name = "Security_Group_Testing"
    if not desc:
        desc = "Security Group For Testing"
    sg_creation_option = test_util.SecurityGroupOption()
    sg_creation_option.set_name(name)
    sg_creation_option.set_description(desc)

    #[Inlined import]
    import zstackwoodpecker.zstack_test.zstack_test_security_group as zstack_sg_header
    sg = zstack_sg_header.ZstackTestSecurityGroup()
    sg.set_creation_option(sg_creation_option)
    sg.create()
    return sg

def lib_delete_security_group(sg_uuid, session_uuid=None):
    return net_ops.delete_security_group(sg_uuid, session_uuid)

def lib_add_sg_rules(sg_uuid, rules, session_uuid=None):
    return net_ops.add_rules_to_security_group(sg_uuid, rules, session_uuid)

def lib_remove_sg_rules(rules, session_uuid=None):
    return net_ops.remove_rules_from_security_group(rules, session_uuid)

def lib_add_nic_to_sg(sg_uuid, vm_nics, session_uuid=None):
    return net_ops.add_nic_to_security_group(sg_uuid, vm_nics, session_uuid)

def lib_remove_nic_from_sg(sg_uuid, nic_uuid, session_uuid=None):
    return net_ops.remove_nic_from_security_group(sg_uuid, [nic_uuid], \
            session_uuid)

def lib_attach_security_group_to_l3(sg_uuid, l3_uuid, session_uuid=None):
    return net_ops.attach_security_group_to_l3(sg_uuid, l3_uuid, session_uuid)

def lib_detach_security_group_from_l3(sg_uuid, l3_uuid, session_uuid=None):
    return net_ops.detach_security_group_from_l3(sg_uuid, l3_uuid, session_uuid)

def lib_attach_security_group_to_l3_by_nic(sg_uuid, vm_nic, session_uuid=None):
    l3_uuid = vm_nic.l3NetworkUuid
    lib_attach_security_group_to_l3(sg_uuid, l3_uuid, session_uuid)

def lib_has_rule_in_sg(sg_inv, protocol=None, target_ip=None, direction=None, port=None):
    for rule in sg_inv.rules:
        if protocol and not rule.protocol == protocol:
            continue
        if target_ip and not rule.allowedCidr == (target_ip + '/32'):
            continue
        if direction and not rule.type == direction:
            continue
        if port and not rule.port == port:
            continue
        return True

def lib_get_sg_invs_by_nic_uuid(nic_uuid):
    '''
    Get all SG inventorys related with nic_uuid
    '''
    conditions = res_ops.gen_query_conditions('vmNicUuid', '=', nic_uuid)
    sg_nics = res_ops.query_resource(res_ops.VM_SECURITY_GROUP, conditions)
    if not sg_nics:
        return False

    sg_invs = []

    for sg_nic in sg_nics:
        sg_uuid = sg_nic.securityGroupUuid
        conditions = res_ops.gen_query_conditions('uuid', '=', sg_uuid)
        sg = res_ops.query_resource(res_ops.SECURITY_GROUP, conditions)[0]
        sg_invs.append(sg)

    return sg_invs

def lib_is_sg_rule_exist(nic_uuid, protocol=None, target_ip=None, direction=None, port=None):
    sg_invs = lib_get_sg_invs_by_nic_uuid(nic_uuid)
    if sg_invs:
        return lib_is_sg_rule_exist_in_sg_invs(sg_invs, protocol=protocol, target_ip=target_ip, direction=direction, port=port)

def lib_is_sg_rule_exist_in_sg_invs(sg_invs, protocol=None, target_ip=None, direction=None, port=None):
    if not sg_invs:
        return False

    for sg in sg_invs:
        if not sg.rules:
            continue
        
        if not protocol and not target_ip and not direction and not port:
            return True

        if lib_has_rule_in_sg(sg, protocol, target_ip, direction, port):
            return True

    return False

#assume vm is behind vr. vr image was assume to have required commands, e.g. nc, telnet, ssh etc. We will use nc to open vm's port.
#will check and open all ports for vm
def lib_open_vm_listen_ports(vm, ports, l3_uuid=None):
    if not l3_uuid:
        target_ip = vm.vmNics[0].ip
    else:
        for nic in vm.vmNics:
            if nic.l3NetworkUuid == l3_uuid:
                target_ip = nic.ip
                break
        else:
            test_util.test_fail("Can not find [vm:] %s IP for [l3 uuid:] %s. Can not open ports for it." % (vm.uuid, l3_uuid))

    lib_check_nc_exist(vm, l3_uuid)
    target_ports = ' '.join(str(port) for port in ports)
    port_checking_cmd = 'result=""; for port in `echo %s`; do echo "hello" | nc -w1 %s $port >/dev/null 2>&1; if [ $? -eq 0 ]; then result="${result}0";else result="${result}1"; (nohup nc -k -l %s $port >/dev/null 2>&1 </dev/null &); fi ; done; echo $result' % (target_ports, target_ip, target_ip)

    test_util.test_logger("Doing opening vm port operations, might need 1 min")
    test_result = lib_execute_command_in_vm(vm, port_checking_cmd)
    if not test_result:
        test_util.test_fail("check [vm:] %s ports failure. Please check the failure information. " % vm.uuid)
    test_result = test_result.strip()
    if len(ports) != len(test_result):
        test_util.test_fail("open/check vm ports failure. Expected to get %s results, but get %s results: %s." % (len(ports), len(test_result), test_result))
    test_util.test_logger("Has open all [ports:] %s for [vm:] %s [ip:] %s" % (ports, vm.uuid, target_ip))

def lib_check_nc_exist(vm, l3_uuid=None):
    if not l3_uuid:
        target_ip = vm.vmNics[0].ip
    else:
        for nic in vm.vmNics:
            if nic.l3NetworkUuid == l3_uuid:
                target_ip = nic.ip
                break
        else:
            test_util.test_fail("Can not find [vm:] %s IP for [l3 uuid:] %s. Can not open ports for it." % (vm.uuid, l3_uuid))

    nc_checking_cmd = "which nc"
    test_result = lib_execute_command_in_vm(vm, nc_checking_cmd)
    if not test_result:
        test_util.test_fail('Test [vm:] %s does not have command "nc" for testing. [error:]' % vm.uuid)

#assume vm is behind vr. vr image was assume to have required commands, e.g. nc, telnet, ssh etc. We will use nc to open vm's port.
def lib_open_vm_listen_port(vm, port, l3_uuid=None):
    if not l3_uuid:
        target_ip = vm.vmNics[0].ip
    else:
        for nic in vm.vmNics:
            if nic.l3NetworkUuid == l3_uuid:
                target_ip = nic.ip
                break
        else:
            test_util.test_fail("Can not find [vm:] %s IP for [l3 uuid:] %s. Can not open ports for it." % (vm.uuid, l3_uuid))

    lib_check_nc_exist(vm, l3_uuid)
    open_port_cmd = 'nohup nc -k -l %s %s >/dev/null 2>&1 </dev/null &' % (guest_ip, port)
    test_result = lib_execute_command_in_vm(vm, open_port_cmd)
    if not test_result:
        test_util.test_fail('cannot execute test ssh [command:] %s in test vm: %s. ' % (open_port_cmd, vm.uuid))
    test_util.test_logger('has open [port:] %s on [vm:] %s [ip:] %s' % (port, vm.uuid, guest_ip))
    return True

def lib_check_vm_port(src_vm, dst_vm, port):
    '''
    lib_check_vm_port could use either vr or native host to check dst_vm's port connection from src_vm.
    vr image or native host was assume to install commands, e.g. nc, telnet, ssh etc.
    '''
    print "connect %s : %s from %s" % (dst_vm.uuid, port, src_vm.uuid)
    vr_vm = lib_find_vr_by_vm(src_vm)
    target_ip = dst_vm.vmNics[0].ip
    #telnet might wait 1 mins time out.
    #cmd = 'echo "quit" | telnet %s %s|grep "Escape character"' % (target_ip, port)
    cmd = 'echo "hello"|nc -w 1 %s %s' % (target_ip, port)
    ret = True
    if vr_vm[0].uuid == src_vm.uuid:
        try:
            src_vm_ip = lib_find_vr_mgmt_ip(src_vm)
            lib_install_testagent_to_vr_with_vr_vm(src_vm)
            vr_vm = src_vm
        except:
            test_util.test_logger("[vm:] %s is not a VR or behind any VR. Can't connect to it to test [vm:] %s [port:] %s" % (src_vm.uuid, dst_vm.uuid, port))
            return False
        shell_cmd = host_plugin.HostShellCmd()
        shell_cmd.command = cmd
        rspstr = http.json_dump_post(testagent.build_http_path(src_vm_ip, host_plugin.HOST_SHELL_CMD_PATH), shell_cmd)
        rsp = jsonobject.loads(rspstr)
        if rsp.return_code != 0:
            ret = False
            test_util.test_logger('shell error info: %s' % rsp.stderr)
    else:
        vr_vm = vr_vm[0]
        if TestHarness == TestHarnessHost:
            test_harness_ip = lib_find_host_by_vm(src_vm).managementIp
            #assign host l2 bridge ip.
            lib_set_vm_host_l2_ip(src_vm)
        else:
            test_harness_ip = lib_find_vr_mgmt_ip(vr_vm)
            lib_install_testagent_to_vr_with_vr_vm(vr_vm)

        src_vm_ip = src_vm.vmNics[0].ip
        username = lib_get_vr_image_username(vr_vm)
        password = lib_get_vr_image_password(vr_vm)
        rsp = lib_ssh_vm_cmd_by_agent(test_harness_ip, src_vm_ip, username, \
                password, cmd)
        
        if not rsp.success:
            ret = False

    if ret:
        test_util.test_logger('Successfully connect [vm:] %s [ip:] %s [port:] %s from [vm:] %s' % (dst_vm.uuid, target_ip, port, src_vm_ip))
        return True
    else:
        test_util.test_logger('Fail to connect [vm:] %s [ip:] %s [port:] %s from [vm:] %s' % (dst_vm, target_ip, port, src_vm_ip))
        return False

def lib_check_vm_ports_in_a_command(src_vm, dst_vm, allowed_ports, denied_ports):
    '''
    Check VM a group of ports connectibility within 1 ssh command.
    1 means connection refused. 0 means connection success. 
    '''
    common_l3 = lib_find_vms_same_l3_uuid([src_vm, dst_vm])
    target_ip = lib_get_vm_nic_by_l3(dst_vm, common_l3).ip
    src_ip = lib_get_vm_nic_by_l3(src_vm, common_l3).ip
    test_util.test_logger("[target vm:] %s [ip:] %s" % (dst_vm.uuid, target_ip))
    lib_check_ports_in_a_command(src_vm, src_ip, target_ip, allowed_ports, denied_ports, dst_vm, common_l3)

def lib_check_ports_in_a_command(src_vm, src_ip, target_ip, allowed_ports, \
        denied_ports, dst_vm, l3_uuid=None):
    '''
        Check target_ip ports connectibility from src_ip. 

        If the allowed_ports are not connectable, or the denied ports are 
        connectable, it will raise execption. 
    '''
    all_ports = allowed_ports + denied_ports
    target_ports = ' '.join(str(port) for port in (allowed_ports + denied_ports))
    expected_result = ''.join(str(0) for item in allowed_ports) + '' + ''.join(str(1) for item in denied_ports)
 
    #Tihs is old script to do serial port checking. 
    #port_checking_cmd = 'result=""; for port in `echo %s`; do echo "hello" | nc -w1 %s $port >/dev/null 2>&1; if [ $? -ne 0 ]; then result="${result}1";else result="${result}0"; fi ; done; echo $result' % (target_ports, target_ip)

    #The script is optimized to be executed in 2 seconds. We found sometime  
    # nc will return more than 1 second, although we set -w1
            #{ echo "hello" | nc -w1 %s $1 ; \
            #{ echo "hello" | nc -w1 %s $1 >/dev/null 2>&1 ; \
    port_checking_cmd = '\
            check_port()\
            { echo "hello" | nc -w1 %s $1 >/dev/null 2>&1 ; \
              echo $? > /tmp/port_$1; \
            } ; \
            result=""; \
            for port in `echo %s`; \
            do rm -f /tmp/port_$port; \
            (check_port $port &); \
            done; \
            sleep 2; \
            for port in `echo %s`; \
            do if [ -f /tmp/port_$port ]; \
                then result=$result`cat /tmp/port_$port`; \
                else result="${result}2"; \
                fi; \
            done; \
            echo $result > /tmp/result_`date +%%s`; \
            echo $result' \
            % (target_ip, target_ports, target_ports)

    test_util.test_logger("Doing port checking, might need 1 min or longer.")
    test_result = lib_execute_command_in_vm(src_vm, port_checking_cmd, l3_uuid)
    if not test_result:
        test_util.test_fail("check [ip:] %s ports failure. Please check the failure information. " % target_ip)
    test_result = test_result.strip()
    if len(expected_result) != len(test_result):
        test_util.test_fail("check vm ports failure. Expected to get %s results: %s, but get %s results: %s. The checking ports are: %s" % (len(expected_result), expected_result, len(test_result), test_result, target_ports))
    else:
        test_util.test_logger("Expected to get results: %s, and get results: %s.The checking ports are: %s" % (expected_result, test_result, target_ports))
    for i in range(len(expected_result)):
        if expected_result[i] == test_result[i]:
            if expected_result[i] == '0':
                test_util.test_logger('(Expected result:) Successfully connect [vm:] %s [ip:] %s [port:] %s from [vm:] %s [ip:] %s' % (dst_vm.uuid, target_ip, all_ports[i], src_vm.uuid, src_ip))
            else:
                test_util.test_logger('(Expected result:) Fail to connect [vm:] %s [ip:] %s [port:] %s from [vm:] %s [ip:] %s' % (dst_vm.uuid, target_ip, all_ports[i], src_vm.uuid, src_ip))
        else:
            src_vm_nic_id = 'vnic%s.x-out' % lib_get_vm_internal_id(src_vm)
            dst_vm_nic_id = 'vnic%s.x-in' % lib_get_vm_internal_id(dst_vm)
            if expected_result[i] == '0':
                test_util.test_fail("(network port checking error:) [vm:] %s [ip:] %s \
[port:] %s [vnic id:] %s is not connectable from [vm:] %s [ip:] %s [vnic id:] \
%s. Expected: connection success." \
                    % (dst_vm.uuid, target_ip, all_ports[i], dst_vm_nic_id, \
                    src_vm.uuid, src_ip, src_vm_nic_id))
            else:
                test_util.test_fail("(nework port checking checking error:) [vm:] %s [ip:] %s [port:] %s [vnic id:] %s is connectable from [vm:] %s [ip:] %s [vnic id:] %s. Expected: connection failed." % (dst_vm.uuid, target_ip, all_ports[i], dst_vm_nic_id, src_vm.uuid, src_ip, src_vm_nic_id))
 
def lib_check_vm_ports(src_vm, dst_vm, allowed_ports, denied_ports):
    test_util.test_logger("Following ports should be allowed to access from [vm] %s to [vm] %s : %s" % (src_vm.uuid, dst_vm.uuid, allowed_ports))
    test_util.test_logger("Following ports should be denied to access from [vm] %s to [vm] %s : %s" % (src_vm.uuid, dst_vm.uuid, denied_ports))
    #Do all operations in 1 commands
    lib_check_vm_ports_in_a_command(src_vm, dst_vm, allowed_ports, denied_ports)
    return True

    #Check port one by one, will trigger a lot of ssh connection.
    for port in allowed_ports:
        if not lib_check_vm_port(src_vm, dst_vm, port):
            test_util.test_fail("Network port checking error: [vm:] %s [port:] %s is not connectable from [vm:] %s ." % (dst_vm.uuid, port, src_vm.uuid))

    for port in denied_ports:
        if lib_check_vm_port(src_vm, dst_vm, port):
            test_util.test_fail("Network port checking error: [vm:] %s [port:] %s is connectable from [vm:] %s ." % (dst_vm.uuid, port, src_vm.uuid))

def lib_check_src_vm_group_ports(src_vms, dst_vm, allowed_ports, denied_ports):
    for src_vm in src_vms:
        lib_check_vm_ports(src_vm, dst_vm, allowed_ports, denied_ports)
    if len(src_vms) > 1:
        for nsrc_vm in src_vms:
            for src_vm in src_vms:
                if nsrc_vm != src_vm:
                    lib_check_vm_ports(nsrc_vm, src_vm, allowed_ports, denied_ports)

def lib_check_dst_vm_group_ports(src_vm, dst_vms, allowed_ports, denied_ports):
    for dst_vm in dst_vms:
        lib_check_vm_ports(src_vms, dst_vm, allowed_ports, denied_ports)

    if len(dst_vms) > 1:
        for nsrc_vm in dst_vms:
            for dst_vm in dst_vms:
                if nsrc_vm != dst_vm:
                    lib_check_vm_ports(nsrc_vm, dst_vm, allowed_ports, denied_ports)

def lib_check_vm_group_ports(src_vms, dst_vms, allowed_ports, denied_ports):
    if isinstance(src_vms, list):
        for src_vm in src_vms:
            lib_check_vm_ports(src_vm, dst_vms, allowed_ports, denied_ports)
        if len(src_vms) > 1:
            for nsrc_vm in src_vms:
                for src_vm in src_vms:
                    if nsrc_vm != src_vm:
                        lib_check_vm_ports(nsrc_vm, src_vm, allowed_ports, denied_ports)

    if isinstance(dst_vms, list):
        for dst_vm in dst_vms:
            lib_check_vm_ports(src_vms, dst_vm, allowed_ports, denied_ports)

        if len(dst_vms) > 1:
            for nsrc_vm in dst_vms:
                for dst_vm in dst_vms:
                    if nsrc_vm != dst_vm:
                        lib_check_vm_ports(nsrc_vm, dst_vm, allowed_ports, denied_ports)

def lib_get_sg_rule_by_uuid(rule_uuid, session_uuid=None):
    conditions = res_ops.gen_query_conditions('uuid', '=', rule_uuid)
    sg_rules = res_ops.query_resource(res_ops.SECURITY_GROUP_RULE, conditions)
    if sg_rules:
        return sg_rules[0]

def lib_get_sg_rule(sg_uuid, rule=None, session_uuid=None):
    '''
    get Security group rule by sg_uuid and rule object. The rule object is like
    rule inventory. 
    '''
    conditions = res_ops.gen_query_conditions('uuid', '=', sg_uuid)
    sg = res_ops.query_resource(res_ops.SECURITY_GROUP, conditions)[0]
    sg_rules = sg.rules

    if rule == None:
        return sg_rules

    for sg_rule in sg_rules:    
        if sg_rule.type == rule.type and sg_rule.protocol == rule.protocol and sg_rule.allowedCidr == rule.allowedCidr and sg_rule.startPort == rule.startPort and sg_rule.endPort == rule.endPort:
            return sg_rule

def lib_get_sg_direction_rules(sg_uuid, direction, session_uuid=None):
    sg = res_ops.get_resource(res_ops.SECURITY_GROUP, session_uuid, uuid=sg_uuid)[0]
    rules = []
    for sg_rule in sg.rules:
        if sg_rule.type == direction:
            rules.append(sg_rule)
    return rules

def lib_gen_sg_rule(port, protocol, type, addr):
    '''
    will return a rule object by giving parameters
    port: rule key, like Port.rule1_ports
    '''
    startPort, endPort = Port.get_start_end_ports(port)
    rule = inventory.SecurityGroupRuleAO()
    rule.allowedCidr = '%s/32' % addr
    rule.endPort = endPort
    rule.startPort = startPort
    rule.protocol = protocol
    rule.type = type
    return rule

def lib_get_sg_rule_uuid_by_rule_obj(sg_uuid, rules, session_uuid=None):
    sg = res_ops.get_resource(res_ops.SECURITY_GROUP, session_uuid, uuid=sg_uuid)[0]
    target_rules = []

    sg_rules = sg.rules

    for rule in rules:
        for sg_rule in sg_rules:
            if sg_rule.type == rule.type and sg_rule.protocol == rule.protocol and sg_rule.allowedCidr == rule.allowedCidr and sg_rule.startPort == rule.startPort and sg_rule.endPort == rule.endPort:
                target_rules.append(sg_rule.uuid)
                test_util.test_logger('find sg [rule:] %s' % sg_rule.uuid)
                break

    if len(target_rules) != len(rules):
        test_util.test_logger('Require to delete %s rules, but find %s rules in database ' % (len(rules), len(target_rules)))

    return target_rules

def lib_delete_rule_from_sg(sg_uuid, rules, session_uuid=None):
    target_rules = lib_get_sg_rule_uuid_by_rule_obj(sg_uuid, rules, session_uuid)
    if target_rules:
        lib_remove_sg_rules(target_rules)

def lib_check_vm_pf_rule_exist_in_iptables(pf_rule):
    '''
    Check if vm pf rule is set in vm's VR.

    @params: 
    pf_rule: the pf inventory
    '''
    test_util.test_logger('Begin to test [Port Forwarding:] %s ' % pf_rule.uuid)
    vr = lib_find_vr_by_vm_nic(lib_get_nic_by_uuid(pf_rule.vmNicUuid))
    check_string1 = pf_rule.allowedCidr
    if pf_rule.protocolType == inventory.TCP:
        check_string2 = '-p tcp'
    else:
        check_string2 = '-p udp'

    check_string3 = '--dport %s:%s' % (pf_rule.vipPortStart, pf_rule.vipPortEnd)

    check_cmd = "iptables-save| grep -Fe '%s'|grep -Fe '%s'|grep -Fe '%s'" % (check_string1, check_string2, check_string3)
    lib_install_testagent_to_vr_with_vr_vm(vr)

    vr_ip = lib_find_vr_mgmt_ip(vr)
    shell_cmd = host_plugin.HostShellCmd()
    shell_cmd.command = check_cmd
    rspstr = http.json_dump_post(testagent.build_http_path(vr_ip, \
            host_plugin.HOST_SHELL_CMD_PATH), shell_cmd)
    rsp = jsonobject.loads(rspstr)
    if rsp.return_code == 0:
        test_util.test_logger('shell cmd result: %s' % rsp.stdout)
        test_util.test_logger('Find [port forwarding:] %s rule on [vr:] %s iptables' % (pf_rule.uuid, vr.uuid))
        return True
    else:
        test_util.test_logger('shell error info: %s' % rsp.stderr)
        test_util.test_logger('Can not find [port forwarding:] %s rule on [vr:] %s iptables' % (pf_rule.uuid, vr.uuid))
        return False

def lib_check_vm_sg_rule_exist_in_iptables(vm, rule_type=None, \
        special_string=None, additional_string=None):
    '''
        rule_type = 'ingress' or 'egress'
        If special_string is not None, test will only grep special_string for 
            vm sg rule and skip all other params including additional_string. 
        If special_string is None and additional_string is not None.
            test will grep additional string, besides of common vm and rule_type
    '''
    if rule_type == inventory.INGRESS:
        rule = 'in'
    elif rule_type == inventory.EGRESS:
        rule = 'out'
    else:
        rule = ''

    if not special_string:
        if additional_string:
            cmd = "nic_id=`virsh dumpxml %s|grep internalId|awk -F'>' '{print $2}'|awk -F'<' '{print $1}'`; iptables-save |grep vnic${nic_id}.0-%s |grep -Fe '%s'" % (vm.uuid, rule, additional_string)
        else:
            cmd = "nic_id=`virsh dumpxml %s|grep internalId|awk -F'>' '{print $2}'|awk -F'<' '{print $1}'`; iptables-save |grep vnic${nic_id}.0-%s" % (vm.uuid, rule)
    else:
        cmd = "iptables-save |grep -Fe '%s'" % special_string
    host_ip = lib_find_host_by_vm(vm).managementIp
    shell_cmd = host_plugin.HostShellCmd()
    shell_cmd.command = cmd
    rspstr = http.json_dump_post(testagent.build_http_path(host_ip, host_plugin.HOST_SHELL_CMD_PATH), shell_cmd)
    rsp = jsonobject.loads(rspstr)
    if rsp.return_code == 0:
        test_util.test_logger('shell cmd result: %s' % rsp.stdout)
        test_util.test_logger('Find [vm:] %s related security rules on [host:] %s iptables' % (vm.uuid, host_ip))
        return True
    else:
        test_util.test_logger('shell error info: %s' % rsp.stderr)
        #test_util.test_logger('shell command: %s' % rsp.command)
        test_util.test_logger('Can not find [vm:] %s related security rules on [host:] %s iptables' % (vm.uuid, host_ip))
        return False

def lib_execute_random_sg_rule_operation(test_dict, target_vm, cre_vm_opt):
    sg_vm = test_dict.get_sg_vm()
    target_vm_nics = target_vm.vm.vmNics
    sg_action, target_sg, target_nic, target_rule_uuid = SgRule.generate_random_sg_action(sg_vm, target_vm_nics)

    test_util.test_logger('Select [SG Operataion:] %s, [sg uuid:] %s, [target_vm:] %s, [target nic:] %s, [target_rule]: %s .' % (sg_action, target_sg.security_group.uuid, target_vm.vm.uuid, target_nic.uuid, target_rule_uuid))

    if sg_action == SgRule.add_rule_to_sg:
        target_l3_uuid = target_nic.l3NetworkUuid
        sg_stub_vm = sg_vm.get_stub_vm(target_l3_uuid)
        #create test stub vm, if it is not exist. Why create test_vm here?
        #1, we need to make sure there is SG test, then create test vm. 
        #2, when creating sg rule, it need to bind with an target IP 
        # address. So the target IP address is test VM's ip address. 
        # Since the IP address is meanless to set with different L3's 
        # test vm, so it need to have a test vm when add a SG Rule.
        if not sg_stub_vm:
            #sg testing need to set cre_vm_opt. 
            create_sg_vm_option = test_util.VmOption()
            create_sg_vm_option.set_name('sg_test_vm')
            create_sg_vm_option.set_l3_uuids([target_l3_uuid])
            create_sg_vm_option.set_image_uuid(cre_vm_opt.get_image_uuid())
            create_sg_vm_option.set_instance_offering_uuid(cre_vm_opt.get_instance_offering_uuid())
            create_sg_vm_option.set_instance_offering_uuid(cre_vm_opt.get_instance_offering_uuid())
            sg_stub_vm = lib_create_vm(create_sg_vm_option)
            try:
                sg_stub_vm.check()
            except:
                test_util.test_logger("Create Test Stub [VM:] %s (for SG testing) fail, as it's network checking failure. Has to quit." % sg_stub_vm.vm.uuid)
                traceback.print_exc(file=sys.stdout)
                test_util.test_fail("Create SG test stub vm fail.")
            test_util.test_logger("Create Test [VM:] %s (for SG testing) successfully." % sg_stub_vm.vm.uuid)
            sg_vm.add_stub_vm(target_l3_uuid, sg_stub_vm)

        sg_stub_vm_l3_vmnic = lib_get_vm_nic_by_l3(sg_stub_vm.vm, target_l3_uuid)
        sg_stub_vm_ip = sg_stub_vm_l3_vmnic.ip
        #Generate a random SG rule
        sg_target_rule = SgRule.generate_sg_rule(sg_stub_vm_ip)
        #ZStack will not allow adding duplicated SR Rule. Might remove checking, if it is harmless. 
        if not lib_get_sg_rule(target_sg.security_group.uuid, sg_target_rule):
            test_util.test_dsc(\
                'Robot Action: %s; on SG: %s' % \
                (sg_action, target_sg.get_security_group().uuid))

            rules = target_sg.add_rule([sg_target_rule])
            rules_uuid = []
            for rule in rules:
                rules_uuid.append(rule.uuid)

            test_util.test_dsc(\
                'Robot Action Result: %s; new Rule: %s; on SG: %s' % \
                (sg_action, rules_uuid, target_sg.get_security_group().uuid))

        else:
            test_util.test_logger(\
                    "skip add rule to sg: %s, since there is already one" \
                    % target_sg.security_group.uuid)
            test_util.test_dsc('Robot Action: %s is skipped' % sg_action)

    elif sg_action == SgRule.remove_rule_from_sg:
        test_util.test_dsc(\
                'Robot Action: %s; on SG: %s; on Rule: %s' % \
                (sg_action, target_sg.get_security_group().uuid, \
                target_rule_uuid))

        target_sg.delete_rule_by_uuids([target_rule_uuid])

    elif sg_action == SgRule.add_sg_to_vm:
        test_util.test_dsc(\
                'Robot Action: %s; on SG: %s; on VM: %s; on Nic: %s' % \
                (sg_action, target_sg.get_security_group().uuid, \
                target_vm.get_vm().uuid, target_nic.uuid))

        sg_vm.attach(target_sg, [(target_nic.uuid, target_vm)])

    elif sg_action == SgRule.remove_sg_from_vm:
        test_util.test_dsc(\
                'Robot Action: %s; on SG: %s; on VM: %s; on Nic: %s' % \
                (sg_action, target_sg.get_security_group().uuid, \
                target_vm.get_vm().uuid, target_nic.uuid))

        sg_vm.detach(target_sg, target_nic.uuid)

#VIP Library
def lib_get_vm_eip_list(vm_uuid, session_uuid=None):
    '''
        if vm was attached with any eip, it will return the eip list.
        If not, it will return empty list [].
    '''
    vm_inv = lib_get_vm_by_uuid(vm_uuid, session_uuid)
    vmNics = vm_inv.vmNics
    if not vmNics:
        return []

    vmNics_uuid = []
    for nic in vmNics:
        vmNics_uuid.append(nic.uuid)

    cond = res_ops.gen_query_conditions('vmNicUuid', 'in', \
            ','.join(vmNics_uuid))
    result = res_ops.query_resource(res_ops.EIP, cond, session_uuid)
    return result

def lib_get_vm_pf_list(vm_uuid, session_uuid=None):
    '''
        if vm was attached with any portForwarding, it will return the pf list.
        If not, it will return empty list [].
    '''
    vm_inv = lib_get_vm_by_uuid(vm_uuid, session_uuid)
    vmNics = vm_inv.vmNics
    if not vmNics:
        return []

    vmNics_uuid = ''
    for nic in vmNics:
        vmNics_uuid.append(nic.uuid)

    cond = res_ops.gen_query_conditions('vmNicUuid', 'in', \
            ','.join(vmNics_uuid))
    result = res_ops.query_resource(res_ops.PORT_FORWARDING, cond, session_uuid)
    return result

def lib_create_vip_obj(vm=None, name='vip', l3_uuid=None, session_uuid=None):
    '''
    vm should be a VM behind of a VR. The VIP will be get from VR's public IP.
    If vm=None, will pick up any VR public L3 network

    @return: vip_test_obj
    '''
    if not l3_uuid:
        if vm:
            vrs = lib_find_vr_by_vm(vm)
            for vr in vrs:
                nic = lib_find_vr_pub_nic(vr)
                if nic:
                    l3_uuid = nic.l3NetworkUuid
                    break
        if not l3_uuid:
            vr_offering = deploy_config.instanceOfferings.virtualRouterOffering
            if isinstance(vr_offering, list):
                l3_name = vr_offering[0].publicL3NetworkRef.text_
            else:
                l3_name = vr_offering.publicL3NetworkRef.text_
    
            condition = res_ops.gen_query_conditions('name', '=', l3_name)
            l3s = res_ops.query_resource(res_ops.L3_NETWORK, condition)
            if l3s:
                l3_uuid = l3s[0].uuid

    if l3_uuid:
        import zstackwoodpecker.zstack_test.zstack_test_vip as zstack_vip_header
        vip = zstack_vip_header.ZstackTestVip()
        vip_option = test_util.VipOption()
        vip_option.set_name(name)
        vip_option.set_l3_uuid(l3_uuid)
        vip.set_creation_option(vip_option)
        vip.create()
        return vip

def lib_delete_vip(vip_uuid):
    net_ops.delete_vip(vip_uuid)

def lib_get_vip_by_uuid(vip_uuid):
    conditions = res_ops.gen_query_conditions('uuid', '=', vip_uuid)
    vip = res_ops.query_resource(res_ops.VIP, conditions)
    return vip[0]

def lib_get_eip_by_uuid(eip_uuid):
    conditions = res_ops.gen_query_conditions('uuid', '=', eip_uuid)
    eip = res_ops.query_resource(res_ops.EIP, conditions)
    return eip[0]

#----------- Robot Library -------------
def lib_robot_cleanup(test_dict):
    for vm in test_dict.get_vm_list(vm_header.RUNNING):
        vm.destroy()
        test_dict.mv_volumes(vm.vm.uuid, test_stage.free_volume)
    for vm in test_dict.get_vm_list(vm_header.STOPPED):
        vm.destroy()
        test_dict.mv_volumes(vm.vm.uuid, test_stage.free_volume)
    for vl in test_dict.get_volume_list():
        vl.delete()
    for img in test_dict.get_image_list():
        img.delete()

    sg_vm = test_dict.get_sg_vm()
    for vm in sg_vm.get_all_stub_vm():
        if vm:
            vm.destroy()
    for sg in sg_vm.get_all_sgs():
        sg_vm.delete_sg(sg)

    #Depricated
    #for sg_uuid in test_dict.get_sg_list():
    #    lib_delete_security_group(sg_uuid)
    for vip in test_dict.get_all_vip_list():
        vip.delete()

    for sp in test_dict.get_all_snapshots():
        sp.delete()

    for vm in test_dict.get_all_utility_vm():
        vm.destroy()

def lib_error_cleanup(test_dict):
    test_util.test_logger('- - - Error cleanup: running VM - - -')
    for vm in test_dict.get_vm_list(vm_header.RUNNING):
        try:
            vm.destroy()
        except:
            pass

    test_util.test_logger('- - - Error cleanup: stopped VM - - -')
    for vm in test_dict.get_vm_list(vm_header.STOPPED):
        try:
            vm.destroy()
        except:
            pass

    test_util.test_logger('- - - Error cleanup: volume - - -')
    for vl in test_dict.get_all_volume_list():
        try:
            vl.delete()
        except:
            pass

    test_util.test_logger('- - - Error cleanup: image - - -')
    for img in test_dict.get_image_list():
        try:
            img.delete()
        except:
            pass

    test_util.test_logger('- - - Error cleanup: SG stub_vm - - -')
    sg_vm = test_dict.get_sg_vm()
    for vm in sg_vm.get_all_stub_vm():
        if vm:
            try:
                vm.destroy()
            except:
                pass

    test_util.test_logger('- - - Error cleanup: SG - - -')
    for sg in sg_vm.get_all_sgs():
        try:
            sg_vm.delete_sg(sg)
        except:
            pass

    for sg_uuid in test_dict.get_sg_list():
        try:
            lib_delete_security_group(sg_uuid)
        except:
            pass

    test_util.test_logger('- - - Error cleanup: Vip/Eip/Pf - - -')
    for vip in test_dict.get_all_vip_list():
        try:
            vip.delete()
        except:
            pass

    test_util.test_logger('- - - Error cleanup: snapshots - - -')
    for sp in test_dict.get_all_snapshots():
        try:
            sp.delete()
        except:
            pass

    test_util.test_logger('- - - Error cleanup: utiltiy vm - - -')
    for vm in test_dict.get_all_utility_vm():
        try:
            vm.destroy()
        except:
            pass

def lib_robot_status_check(test_dict):
    print 'target checking test dict: %s' % test_dict
    test_util.test_logger('- - - check running VMs status - - -')
    for vm in test_dict.get_vm_list(vm_header.RUNNING):
        vm.check()

    test_util.test_logger('- - - check stopped vm status - - -')
    for vm in test_dict.get_vm_list(vm_header.STOPPED):
        vm.check()

    test_util.test_logger('- - - check volume status - - -')
    for volume in test_dict.get_all_volume_list():
        volume.check()

    test_util.test_logger('- - - check image status - - -')
    for image in test_dict.get_image_list():
        image.check()

    test_util.test_logger('- - - check SG rules - - -')
    sg_vm = test_dict.get_sg_vm()
    sg_vm.check()

    test_util.test_logger('- - - check vip eip/pf - - -')
    for vip in test_dict.get_all_vip_list():
        if vip:
            vip.check()

    test_util.test_logger('- - - check Snapshot  - - -')
    volume_snapshots = test_dict.get_all_snapshots()
    for snapshots in volume_snapshots:
        snapshots.check()

    test_util.test_logger("- - - Robot check pass - - -" )

def lib_vm_random_operation(robot_test_obj):
    '''
        Random operations for robot testing
    '''
    test_dict = robot_test_obj.get_test_dict()
    print 'target test dict for random operation: %s' % test_dict
    excluded_actions_list = robot_test_obj.get_exclusive_actions_list()
    cre_vm_opt = robot_test_obj.get_vm_creation_option()
    priority_actions = robot_test_obj.get_priority_actions()
    random_type = robot_test_obj.get_random_type()
    public_l3 = robot_test_obj.get_public_l3()

    test_stage_obj = test_stage()

    target_vm = None
    attached_volume = None
    ready_volume = None
    snapshot_volume = None
    target_snapshot = None

    #Firstly, choose a target VM state for operation. E.g. Running. 
    if test_dict.get_vm_list(vm_header.STOPPED):
        target_vm_state = random.choice([vm_header.RUNNING, vm_header.STOPPED])
    else:
        target_vm_state = vm_header.RUNNING 

    #Secondly, choose a target VM from target status. 
    target_vm_list = test_dict.get_vm_list(target_vm_state)
    if target_vm_list:
        target_vm = random.choice(target_vm_list)

        vm = lib_get_vm_by_uuid(target_vm.get_vm().uuid)
        #vm state in db
        vm_current_state = vm.state
        if target_vm_state != vm_current_state:
            test_util.test_fail('\
[vm:] %s current [state:] %s is not aligned with random test record [state:] \
%s .' % (target_vm.get_vm().uuid, vm_current_state, target_vm_state))
    
        test_stage_obj.set_vm_state(vm_current_state)

        #Thirdly, check VM's volume status. E.g. if could add a new volume.
        vm_volumes = test_dict.get_volume_list(target_vm.get_vm().uuid)
        vm_volume_number = len(vm_volumes)
        if vm_volume_number > 0 and vm_volume_number < 24:
            test_stage_obj.set_vm_volume_state(test_stage.vm_volume_att_not_full)
            attached_volume = random.choice(vm_volumes)
        elif vm_volume_number == 0:
            test_stage_obj.set_vm_volume_state(test_stage.vm_no_volume_att)
        else:
            test_stage_obj.set_vm_volume_state(test_stage.vm_volume_att_full)
            attached_volume = random.choice(vm_volumes)
    
    else:
        test_stage_obj.set_vm_state(test_stage.Any)
        test_stage_obj.set_vm_volume_state(test_stage.Any)

    #Fourthly, choose a available volume for possibly attach or delete
    avail_volumes = test_dict.get_volume_list(test_stage.free_volume)
    if avail_volumes:
        test_stage_obj.set_volume_state(test_stage.free_volume)
        ready_volume = random.choice(avail_volumes)
    else:
        test_stage_obj.set_volume_state(test_stage.no_free_volume)

    #Fifthly, choose a volume for possible snasphot operation 
    all_volume_snapshots = test_dict.get_all_snapshots()
    if all_volume_snapshots:
        target_volume_snapshots = random.choice(all_volume_snapshots)
        snapshot_volume_obj = target_volume_snapshots.get_target_volume()
        snapshot_volume = snapshot_volume_obj.get_volume()

        if snapshot_volume_obj.get_state() == vol_header.CREATED:
            #It means the volume is just created and not attached to any VM yet.
            #This volume can not create any snapshot. 
            test_stage_obj.set_snapshot_state(test_stage.no_volume_file)
        else:
            #if volume is not attached to any VM, we assume vm state is stopped
            # or we think its hypervisor support live snapshot creation
            if snapshot_volume_obj.get_state() != vol_header.ATTACHED:
                test_stage_obj.set_snapshot_live_cap(test_stage.snapshot_live_creation)
                test_stage_obj.set_volume_vm_state(vm_header.STOPPED)
            else:
                volume_vm = snapshot_volume_obj.get_target_vm()
                test_stage_obj.set_volume_vm_state(volume_vm.get_state())
                target_vm_inv = volume_vm.get_vm()
                host_inv = lib_find_host_by_vm(target_vm_inv)
                if lib_check_live_snapshot_cap(host_inv):
                    test_stage_obj.set_snapshot_live_cap(test_stage.snapshot_live_creation)
                else:
                    test_stage_obj.set_snapshot_live_cap(test_stage.snapshot_no_live_creation)

            #random pick up an available snapshot. Firstly choose from primary snapshot.
            target_snapshot = None

            #FIXME: current if volume is deleted, we assume there isn't snapshot in primary storage 
            if target_volume_snapshots.get_primary_snapshots() and snapshot_volume_obj.get_state() != vol_header.DELETED:
                target_snapshot = random.choice(target_volume_snapshots.get_primary_snapshots())
                if target_snapshot in target_volume_snapshots.get_backuped_snapshots():
                    if target_snapshot.get_volume_type() \
                            == vol_header.ROOT_VOLUME:
                        test_stage_obj.set_snapshot_state(test_stage.root_snapshot_in_both_ps_bs)
                    else:
                        test_stage_obj.set_snapshot_state(test_stage.data_snapshot_in_both_ps_bs)
                else:
                    if target_snapshot.get_volume_type() \
                            == vol_header.ROOT_VOLUME:
                        test_stage_obj.set_snapshot_state(test_stage.root_snapshot_in_ps)
                    else:
                        test_stage_obj.set_snapshot_state(test_stage.data_snapshot_in_ps)
            else:
                if target_volume_snapshots.get_backuped_snapshots():
                    target_snapshot = random.choice(target_volume_snapshots.get_backuped_snapshots())
                    if target_snapshot.get_volume_type() \
                            == vol_header.ROOT_VOLUME:
                        test_stage_obj.set_snapshot_state(test_stage.root_snapshot_in_bs)
                    else:
                        test_stage_obj.set_snapshot_state(test_stage.data_snapshot_in_bs)
                else:
                    test_stage_obj.set_snapshot_state(test_stage.no_snapshot)


    #Sixly, check system vip resource
    vip_available = False
    if not TestAction.create_vip in excluded_actions_list:
        if not public_l3:
            test_util.test_fail('\
Test Case need to set robot_test_obj.public_l3, before call \
lib_vm_random_operation(robot_test_obj), otherwise robot can not judge if there\
is available free vip resource in system. Or you can add "create_vip" action \
into robot_test_obj.exclusive_actions_list.')

        #check if system has available IP resource for allocation. 
        available_ip_evt = net_ops.get_ip_capacity_by_l3s([public_l3])
        if available_ip_evt and available_ip_evt.availableCapacity > 0:
            vip_available = True

    #Add template image actions
    if test_dict.get_image_list(test_stage.new_template_image):
        test_stage_obj.set_image_state(test_stage.new_template_image)

    #Add SG actions
    if test_dict.get_sg_list():
        test_stage_obj.set_sg_state(test_stage.has_sg)
    else:
        test_stage_obj.set_sg_state(test_stage.no_sg)

    #Add VIP actions
    if test_dict.get_vip_list():
        if vip_available:
            test_stage_obj.set_vip_state(test_stage.has_vip)
        else:
            test_stage_obj.set_vip_state(test_stage.no_more_vip_res)
    else:
        if vip_available:
            test_stage_obj.set_vip_state(test_stage.no_vip)
        else:
            test_stage_obj.set_vip_state(test_stage.no_vip_res)

    test_util.test_logger("action state_dict: %s" % test_stage_obj.get_state())
    action_list = ts_header.generate_action_list(test_stage_obj, \
            excluded_actions_list)

    test_util.test_logger('action list: %s' % action_list)

    # Currently is randomly picking up.
    next_action = lib_robot_pickup_action(action_list, \
            robot_test_obj.get_action_history(), priority_actions, random_type)
    robot_test_obj.add_action_history(next_action)

    if next_action == TestAction.create_vm:
        test_util.test_dsc('Robot Action: %s ' % next_action)
        new_vm = lib_create_vm(cre_vm_opt)
        test_dict.add_vm(new_vm)

        test_util.test_dsc('Robot Action Result: %s; new VM: %s' % \
            (next_action, new_vm.get_vm().uuid))

        test_dict.create_empty_volume_list(new_vm.vm.uuid)

    elif next_action == TestAction.stop_vm:
        test_util.test_dsc('Robot Action: %s; on VM: %s' \
                % (next_action, target_vm.get_vm().uuid))

        target_vm.stop()
        test_dict.mv_vm(target_vm, vm_header.RUNNING, vm_header.STOPPED)

    elif next_action == TestAction.start_vm :
        test_util.test_dsc('Robot Action: %s; on VM: %s' \
                % (next_action, target_vm.get_vm().uuid))

        target_vm.start()
        test_dict.mv_vm(target_vm, vm_header.STOPPED, vm_header.RUNNING)

    elif next_action == TestAction.reboot_vm :
        test_util.test_dsc('Robot Action: %s; on VM: %s' \
                % (next_action, target_vm.get_vm().uuid))

        target_vm.reboot()

    elif next_action == TestAction.destroy_vm :
        test_util.test_dsc('Robot Action: %s; on VM: %s' \
                % (next_action, target_vm.get_vm().uuid))
        target_vm.destroy()
        test_dict.mv_vm(target_vm, vm_current_state, vm_header.DESTROYED)
        test_dict.mv_volumes(target_vm.vm.uuid, test_stage.free_volume)

    elif next_action == TestAction.migrate_vm :
        test_util.test_dsc('Robot Action: %s; on VM: %s' \
                % (next_action, target_vm.get_vm().uuid))
        target_host = lib_find_random_host(target_vm.vm)
        if not target_host:
            test_util.test_logger('no avaiable host was found for doing vm migration')
        else:
            target_vm.migrate(target_host.uuid)

    elif next_action == TestAction.create_volume :
        test_util.test_dsc('Robot Action: %s ' % next_action)
        new_volume = lib_create_volume_from_offering()
        test_dict.add_volume(new_volume)

        test_util.test_dsc('Robot Action Result: %s; new Volume: %s' % \
            (next_action, new_volume.get_volume().uuid))

    elif next_action == TestAction.attach_volume :
        test_util.test_dsc('Robot Action: %s; on Volume: %s; on VM: %s' % \
            (next_action, ready_volume.get_volume().uuid, \
            target_vm.get_vm().uuid))

        ready_volume.attach(target_vm)
        test_dict.mv_volume(ready_volume, test_stage.free_volume, target_vm.vm.uuid)

    elif next_action == TestAction.detach_volume:
        test_util.test_dsc('Robot Action: %s; on Volume: %s' % \
            (next_action, attached_volume.get_volume().uuid))

        attached_volume.detach()
        test_dict.mv_volume(attached_volume, target_vm.vm.uuid, test_stage.free_volume)

    elif next_action == TestAction.delete_volume:
        #if there is no free volume, but action is delete_volume. It means the 
        # the target volume is attached volume.
        if not ready_volume:
            ready_volume = attached_volume

        test_util.test_dsc('Robot Action: %s; on Volume: %s' % \
            (next_action, ready_volume.get_volume().uuid))
        ready_volume.delete()
        test_dict.rm_volume(ready_volume)

    elif next_action == TestAction.idel :
        test_util.test_dsc('Robot Action: %s ' % next_action)
        lib_vm_random_idel_time(1, 5)

    elif next_action == TestAction.create_image_from_volume:
        root_volume_uuid = lib_get_root_volume(target_vm.vm).uuid

        test_util.test_dsc('Robot Action: %s; on Volume: %s; on VM: %s' % \
            (next_action, root_volume_uuid, target_vm.get_vm().uuid))

        new_image = lib_create_template_from_volume(root_volume_uuid)
        test_util.test_dsc('Robot Action Result: %s; new RootVolume Image: %s'\
                % (next_action, new_image.get_image().uuid))

        test_dict.add_image(new_image)

    elif next_action == TestAction.create_data_vol_template_from_volume:
        vm_volumes = target_vm.get_vm().allVolumes
        vm_target_vol = random.choice(vm_volumes)
        test_util.test_dsc('Robot Action: %s; on Volume: %s; on VM: %s' % \
            (next_action, vm_target_vol.uuid, target_vm.get_vm().uuid))
        new_data_vol_temp = lib_create_data_vol_template_from_volume(target_vm, vm_target_vol)
        test_util.test_dsc('Robot Action Result: %s; new DataVolume Image: %s' \
                % (next_action, new_data_vol_temp.get_image().uuid))

        test_dict.add_image(new_data_vol_temp)

    elif next_action == TestAction.create_data_volume_from_image:
        image_list = test_dict.get_image_list(test_stage.new_template_image)
        target_image = random.choice(image_list)

        test_util.test_dsc('Robot Action: %s; on Image: %s' % \
            (next_action, target_image.get_image().uuid))

        new_volume = lib_create_data_volume_from_image(target_image)

        test_util.test_dsc('Robot Action Result: %s; new Volume: %s' % \
            (next_action, new_volume.get_volume().uuid))
        test_dict.add_volume(new_volume)

    elif next_action == TestAction.delete_image:
        image_list = test_dict.get_image_list(test_stage.new_template_image)
        target_image = random.choice(image_list)

        test_util.test_dsc('Robot Action: %s; on Image: %s' % \
            (next_action, target_image.get_image().uuid))

        target_image.delete()
        test_dict.rm_image(target_image, test_stage.new_template_image)

    elif next_action == TestAction.create_sg:
        test_util.test_dsc('Robot Action: %s ' % next_action)
        sg_vm = test_dict.get_sg_vm()
        sg_creation_option = test_util.SecurityGroupOption()
        sg_creation_option.set_name('robot security group')
        new_sg = sg_vm.create_sg(sg_creation_option)
        test_util.test_dsc(\
            'Robot Action Result: %s; new SG: %s' % \
            (next_action, new_sg.get_security_group().uuid))

    elif next_action == TestAction.delete_sg:
        sg_vm = test_dict.get_sg_vm()
        target_sg = random.choice(sg_vm.get_all_sgs())
        test_util.test_dsc(\
            'Robot Action: %s; on SG: %s' % \
            (next_action, target_sg.get_security_group().uuid))

        sg_vm.delete_sg(target_sg)

    #sg rule actions
    elif next_action == TestAction.sg_rule_operations:
        lib_execute_random_sg_rule_operation(test_dict, target_vm, cre_vm_opt)

    #vip actions
    elif next_action == TestAction.create_vip:
        test_util.test_dsc('Robot Action: %s ' % next_action)
        if target_vm:
            vip = lib_create_vip_obj(target_vm.vm)
        else:
            vip = lib_create_vip_obj()

        if not vip:
            test_util.test_warn('vip creation failed. It is mostly because can not find public l3 network.')
            test_util.test_dsc('Robot Action Result: %s; Fail.' % next_action)
        else:
            test_dict.add_vip(vip)
            test_util.test_dsc('Robot Action Result: %s; new VIP: %s' % \
                (next_action, vip.get_vip().uuid))

    elif next_action == TestAction.delete_vip:
        target_vip = random.choice(test_dict.get_all_vip_list())
        test_util.test_dsc('Robot Action: %s; on VIP: %s' % \
            (next_action, target_vip.get_vip().uuid))

        net_ops.delete_vip(target_vip.get_vip().uuid)
        test_dict.rm_vip(target_vip)

    elif next_action == TestAction.vip_operations:
        vip_action = ts_header.VipAction(test_dict, target_vm)
        vip_action.execute_random_vip_ops()

    elif next_action == TestAction.create_volume_snapshot:
        target_volume_inv = \
                target_volume_snapshots.get_target_volume().get_volume()
        if target_volume_inv.type == vol_header.ROOT_VOLUME:
            test_util.test_dsc('Robot Action: %s; on Root Volume: %s; on VM: %s' % \
                   (next_action, \
                    target_volume_inv.uuid, target_volume_inv.vmInstanceUuid))
        else:
            test_util.test_dsc('Robot Action: %s; on Volume: %s' % \
                   (next_action, \
                    target_volume_inv.uuid))

        new_snapshot = lib_create_volume_snapshot_from_volume(target_volume_snapshots, robot_test_obj, test_dict, cre_vm_opt)

        test_util.test_dsc('Robot Action Result: %s; new SP: %s' % \
            (next_action, new_snapshot.get_snapshot().uuid))

    elif next_action == TestAction.delete_volume_snapshot:
        target_volume_snapshots.delete_snapshot(target_snapshot)
        test_util.test_dsc('Robot Action: %s; on Volume: %s; on SP: %s' % \
            (next_action, \
            target_volume_snapshots.get_target_volume().get_volume().uuid, \
            target_snapshot.get_snapshot().uuid))

        #If both volume and snapshots are deleted, volume_snapshot obj could be 
        # removed.
        if not target_volume_snapshots.get_backuped_snapshots():
            target_volume_obj = target_volume_snapshots.get_target_volume()
            if target_volume_obj.get_state == vol_header.DELETED \
                    or (target_volume_snapshots.get_volume_type() == \
                        vol_header.ROOT_VOLUME \
                        and target_volume_obj.get_target_vm().get_state() == \
                            vm_header.DESTROYED):
                test_dict.rm_volume_snapshot(target_volume_snapshots)

    elif next_action == TestAction.use_volume_snapshot:
        test_util.test_dsc('Robot Action: %s; on Volume: %s; on SP: %s' % \
            (next_action, \
            target_volume_snapshots.get_target_volume().get_volume().uuid, \
            target_snapshot.get_snapshot().uuid))

        target_volume_snapshots.use_snapshot(target_snapshot)

    elif next_action == TestAction.backup_volume_snapshot:
        test_util.test_dsc('Robot Action: %s; on Volume: %s; on SP: %s' % \
            (next_action, \
            target_volume_snapshots.get_target_volume().get_volume().uuid, \
            target_snapshot.get_snapshot().uuid))

        target_volume_snapshots.backup_snapshot(target_snapshot)

    elif next_action == TestAction.delete_backup_volume_snapshot:
        test_util.test_dsc('Robot Action: %s; on Volume: %s; on SP: %s' % \
            (next_action, \
            target_volume_snapshots.get_target_volume().get_volume().uuid, \
            target_snapshot.get_snapshot().uuid))

        target_volume_snapshots.delete_backuped_snapshot(target_snapshot)

        #Both volume and snapshots are deleted, volume_snapshot obj could be 
        # removed.
        if not target_volume_snapshots.get_backuped_snapshots():
            target_volume_obj = target_volume_snapshots.get_target_volume()
            if target_volume_obj.get_state() == vol_header.DELETED \
                    or (target_volume_snapshots.get_volume_type() == \
                        vol_header.ROOT_VOLUME \
                        and target_volume_obj.get_target_vm().get_state() == \
                            vm_header.DESTROYED):
                test_dict.rm_volume_snapshot(target_volume_snapshots)

    elif next_action == TestAction.create_volume_from_snapshot:
        test_util.test_dsc('Robot Action: %s; on Volume: %s; on SP: %s' % \
            (next_action, \
            target_volume_snapshots.get_target_volume().get_volume().uuid, \
            target_snapshot.get_snapshot().uuid))

        new_volume_obj = target_snapshot.create_data_volume()
        test_dict.add_volume(new_volume_obj)
        test_util.test_dsc('Robot Action Result: %s; new Volume: %s; on SP: %s'\
                % (next_action, new_volume_obj.get_volume().uuid,\
                target_snapshot.get_snapshot().uuid))

    elif next_action == TestAction.create_image_from_snapshot:
        test_util.test_dsc('Robot Action: %s; on Volume: %s; on SP: %s' % \
            (next_action, \
            target_volume_snapshots.get_target_volume().get_volume().uuid, \
            target_snapshot.get_snapshot().uuid))

        new_image_obj = lib_create_image_from_snapshot(target_snapshot)

        test_dict.add_image(new_image_obj)
        test_util.test_dsc('Robot Action Result: %s; new Image: %s; on SP: %s'\
                % (next_action, new_image_obj.get_image().uuid,\
                target_snapshot.get_snapshot().uuid))

    test_util.test_logger('Finsih action: %s execution' % next_action)

#TODO: add more action pickup strategy
def lib_robot_pickup_action(action_list, pre_robot_actions, \
        priority_actions, selector_type):

    test_util.test_logger('Action history: %s' % pre_robot_actions)

    if not selector_type:
        selector_type = action_select.default_strategy

    action_selector = action_select.action_selector_table[selector_type]
    return action_selector(action_list, pre_robot_actions, \
            priority_actions).select()

def lib_get_test_stub():
    '''test_stub lib is not global test library. It is test suite level common
    lib. Test cases might be in different sub folders under test suite folder. 
    This function will help test case to find and load test_stub.py.'''
    import inspect
    import zstacklib.utils.component_loader as component_loader
    caller_info_list = inspect.getouterframes(inspect.currentframe())[1]
    caller_path = os.path.realpath(caller_info_list[1])
    test_stub_cl = component_loader.ComponentLoader('test_stub', os.path.dirname(caller_path), 4)
    test_stub_cl.load()
    return test_stub_cl.module

#---------------------------------------------------------------
#Robot actions.
def lib_create_data_vol_template_from_volume(target_vm, vm_target_vol=None):
    import zstackwoodpecker.header.image as image_header
    import zstackwoodpecker.zstack_test.zstack_test_image as zstack_image_header
    vm_inv = target_vm.get_vm()

    backup_storage_uuid_list = lib_get_backup_storage_uuid_list_by_zone(vm_inv.zoneUuid)
    new_data_vol_inv = vol_ops.create_volume_template(vm_target_vol.uuid, \
            backup_storage_uuid_list, \
            'vol_temp_for_volume_%s' % vm_target_vol.uuid)
    new_data_vol_temp = zstack_image_header.ZstackTestImage()
    new_data_vol_temp.set_image(new_data_vol_inv)
    new_data_vol_temp.set_state(image_header.CREATED)
    return new_data_vol_temp

def lib_create_volume_snapshot_from_volume(target_volume_snapshots, robot_test_obj, test_dict, cre_vm_opt=None):
    target_volume_inv = \
            target_volume_snapshots.get_target_volume().get_volume()
    if not target_volume_snapshots.get_utility_vm():
        ps_uuid = target_volume_inv.primaryStorageUuid
        vol_utiltiy_vm = robot_test_obj.get_utility_vm(ps_uuid)
        if not vol_utiltiy_vm:
            #create utiltiy_vm on given primary storage.
            util_vm_opt = test_util.VmOption(cre_vm_opt)
            instance_offering_uuid = util_vm_opt.get_instance_offering_uuid()
            if not instance_offering_uuid:
                instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING)[0].uuid
            tag = tag_ops.create_system_tag('InstanceOfferingVO', \
                    instance_offering_uuid, \
                    'primaryStorage::allocator::uuid::%s' % ps_uuid)
            possible_cluster = target_volume_inv.clusterUuid
            if not possible_cluster:
                possible_cluster = res_ops.query_resource_with_num(\
                        res_ops.CLUSTER, [], None, 0, 1)[0].uuid

            cond = res_ops.gen_query_conditions('attachedClusterUuids', \
                    '=', possible_cluster)
            possible_l2 = res_ops.query_resource(res_ops.L2_VLAN_NETWORK, \
                    cond)[0].uuid
            cond = res_ops.gen_query_conditions('l2NetworkUuid', '=', \
                    possible_l2)
            possible_l3 = res_ops.query_resource(res_ops.L3_NETWORK, \
                    cond)[0].uuid
            util_vm_opt.set_l3_uuids([possible_l3])

            vol_utiltiy_vm  = lib_create_vm(util_vm_opt)
            tag_ops.delete_tag(tag.uuid)
            robot_test_obj.set_utility_vm(vol_utiltiy_vm)
            test_dict.add_utility_vm(vol_utiltiy_vm)
            vol_utiltiy_vm.check()
            
        target_volume_snapshots.set_utility_vm(vol_utiltiy_vm)

    return target_volume_snapshots.create_snapshot()

def lib_create_image_from_snapshot(target_snapshot):
    snapshot_volume = target_snapshot.get_target_volume()
    root_image_uuid = snapshot_volume.get_volume().rootImageUuid
    root_img_inv = lib_get_image_by_uuid(root_image_uuid)
    image_option = test_util.ImageOption()
    image_option.set_name('creating_image_from_snapshot')
    image_option.set_guest_os_type(root_img_inv.guestOsType)
    image_option.set_bits(root_img_inv.bits)
    image_option.set_root_volume_uuid(target_snapshot.get_snapshot().uuid)
    image_option.set_backup_storage_uuid_list([root_img_inv.backupStorageRefs[0].backupStorageUuid])
    target_snapshot.set_image_creation_option(image_option)
    new_image_obj = target_snapshot.create_image_template()
    return new_image_obj

def lib_create_data_volume_from_image(target_image):
    bs_uuid = target_image.get_image().backupStorageRefs[0].backupStorageUuid
    ps_uuid_list = \
            lib_get_primary_storage_uuid_list_by_backup_storage(bs_uuid)
    new_volume = target_image.create_data_volume(ps_uuid_list[0], \
            'new_volume_from_template_%s' % target_image.get_image().uuid)
    return new_volume 
