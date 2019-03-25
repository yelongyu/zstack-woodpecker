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
import zstackwoodpecker.operations.config_operations as conf_ops
import zstackwoodpecker.operations.console_operations as cons_ops
import zstackwoodpecker.operations.license_operations as lic_ops
import zstackwoodpecker.operations.resource_stack as resource_stack_ops

import zstackwoodpecker.header.vm as vm_header
import zstackwoodpecker.header.volume as vol_header
import zstackwoodpecker.header.image as image_header

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
from contextlib import contextmanager
import functools
from collections import defaultdict

debug.install_runtime_tracedumper()
test_stage = ts_header.TestStage
TestAction = ts_header.TestAction
SgRule = ts_header.SgRule
Port = ts_header.Port
WOODPECKER_MOUNT_POINT = '/tmp/zstack/mnt'
SSH_TIMEOUT = 600

class FakeObject(object):
    '''
    Use to print warning message
    '''
    def __getitem__(self, name):
        raise test_util.TestError("WOODPECKER_TEST_CONFIG_FILE is NOT set, which will be used in ZStack test. It is usually set by zstack-woodpecker when executing integration test or exporting environment parameter when executing python command manually(e.g. WOODPECKER_TEST_CONFIG_FILE=/WOODPECKER_TEST_PATH/virtualrouter/test-config.xml). ")

    def __getattr__(self, name):
        self.__getitem__(name)

scenario_config_path = os.environ.get('WOODPECKER_SCENARIO_CONFIG_FILE')
if scenario_config_path != None and scenario_config_path != "":
    scenario_config_obj = test_util.TestScenario(scenario_config_path)
    #Special config in test-config.xml, such like test ping target. 
    scenario_config = scenario_config_obj.get_test_config()
    #All configs in deploy.xml.
    all_scenario_config = scenario_config_obj.get_scenario_config()
    #Detailed zstack deployment information, including zones/cluster/hosts...
    deploy_scenario_config = all_scenario_config.deployerConfig
    #setup_scenario_plan = setup_actions.Plan(all_scenario_config)
    scenario_config_obj.expose_config_variable()
else:
    scenario_config = None
    all_scenario_config = None

scenario_file_path = os.environ.get('WOODPECKER_SCENARIO_FILE')
if scenario_file_path != None and scenario_file_path != "":
    scenario_file = scenario_file_path
else:
    scenario_file = None

scenario_destroy_path = os.environ.get('WOODPECKER_SCENARIO_DESTROY')
if scenario_destroy_path != None and scenario_destroy_path != "":
    scenario_destroy = scenario_destroy_path
else:
    scenario_destroy = None

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
    setup_plan = setup_actions.Plan(all_config, all_scenario_config, scenario_file)
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

def lib_install_testagent_to_host(host, username = None, password = None):
    host_pub_ip = host.managementIp
    for i in range(12):
        try:
            shell.call('echo "quit" | telnet %s 22|grep "Escape character"' % host_pub_ip)
            break
        except:
            test_util.test_logger("retry %s times: exception on telnet ip 22" %(str(i)))

        try:
            shell.call('echo "quit" | telnet %s 2222|grep "Escape character"' % host_pub_ip)
            break
        except:
            test_util.test_logger("retry %s times: exception on telnet ip 2222" %(str(i)))

        time.sleep(10)

    try:
        shell.call('echo "quit" | telnet %s 9393|grep "Escape character"' % host_pub_ip)
        #shell.call('nc -w1 %s 9393' % host_pub_ip)
        test_util.test_logger('Testagent is running on Host: %s . Skip testagent installation.' % host.name)
    except:
        test_host = test_util.HostOption()
        test_host.managementIp = host_pub_ip
        if not username:
            test_host.username = os.environ.get('hostUsername')
        else:
            test_host.username = username

        if not password:
            test_host.password = os.environ.get('hostPassword')
        else:
            test_host.password = password

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
    lib_check_system_cmd('telnet')
    #lib_check_system_cmd('nc')
    try:
        shell.call('echo "quit" | telnet %s 9393|grep "Escape character"' % vr.managementIp)
        #shell.call('nc -w1 %s 9393' % vr.managementIp)
        test_util.test_logger('Testagent is running on VR: %s . Skip testagent installation.' % vr.managementIp)
    except:
        vr.username = lib_get_vr_image_username(vr_vm)
        vr.password = lib_get_vr_image_password(vr_vm)
        vr.uuid = vr_vm.uuid
        vr.machine_id = vr_vm.uuid
        lib_wait_target_up(vr.managementIp, '22', 180)
        test_util.test_logger('Testagent is not running on [VR:] %s with username: %s password: %s. Will install Testagent.\n' % (vr.managementIp, vr.username, vr.password))
        setup_plan._copy_sshkey_from_node()
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

def lib_get_ceph_info(monUrls):
    '''
    return 1st ceph_host, username, password
    '''
    mons = monUrls.split(';')
    mon1 = mons[0]
    user_pass, ceph_host = mon1.split('@')
    username, password = user_pass.split(':')
    return ceph_host, username, password

def lib_install_testgent_to_ceph_host(monUrls):
    ceph_host, username, password = lib_get_ceph_info(monUrls)
    host = test_util.HostOption()
    host.managementIp = ceph_host
    test_util.test_logger('Install test agent to ceph host: %s' % ceph_host)
    lib_install_testagent_to_host(host, username, password)

def lib_install_testagent_to_ceph_ps():
    monUrls = os.environ.get('cephPrimaryStorageMonUrls')
    lib_install_testgent_to_ceph_host(monUrls)

def lib_install_testagent_to_ceph_bs():
    monUrls = os.environ.get('cephBackupStorageMonUrls')
    lib_install_testgent_to_ceph_host(monUrls)

def lib_delete_ceph_pool(ceph_host, username, password, poolname):
    command = 'ceph osd pool delete %s %s --yes-i-really-really-mean-it' % \
            (poolname, poolname)
    lib_execute_ssh_cmd(ceph_host, username, password, command)

def lib_get_ps_ceph_info_by_ps_inventory(ps_inv):
    mon_one = ps_inv.mons[0].hostname
    for key in os.environ.keys():
        if mon_one in os.environ.get(key):
           monUrls = os.environ.get(key).split(';')

    for mon in monUrls:
        if mon_one == mon.split('@')[1]:
            username, password = mon.split('@')[0].split(':')
            return mon_one, username, password

    test_util.test_logger('did not find predefined mon url for ps: %s' % \
            ps_inv.uuid)

def lib_get_bs_ceph_info_by_bs_inventory(bs_inv):
    mon_one = bs_inv.mons[0].hostname
    for key in os.environ.keys():
        if mon_one in os.environ.get(key):
           monUrls = os.environ.get(key).split(';')
    for mon in monUrls:
        if mon_one == mon.split('@')[1]:
            username, password = mon.split('@')[0].split(':')
            return mon_one, username, password

    test_util.test_logger('did not find predefined mon url for bs: %s' % \
            bs_inv.uuid)

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

def lib_execute_ssh_cmd(host_ip, username, password, command, timeout = 30, \
        port = 22):
    def ssh_host():
        try:

            h_port = lib_get_host_port(host_ip) 
            if not h_port:
                h_port = port
            ret, output, stderr = ssh.execute(command, host_ip, username, password, False, port=h_port)
            print("ssh: %s , return value: %d, standard output:%s, standard error: %s" % (command, ret, output, stderr))
            ssh_result['result'] = ret
            ssh_result['output'] = output
            ssh_result['err'] = stderr
            return True

        except Exception as e:
            test_util.test_logger('[SSH] unable to ssh in host[ip:%s], assume its not ready. Exception: %s' % (host_ip, str(e)))
            ssh_result['result'] = 'error'
            
        return False

    ssh_result = {'result': None, 'output': None, 'err': None}
    thread = threading.Thread(target = ssh_host)
    thread.daemon = True
    thread.start()
    time_out = time.time() + timeout 
    while ssh_result['result'] == None and time.time() < time_out:
        time.sleep(0.5)

    if ssh_result['result'] != None: 
        if ssh_result['result'] == 'error':
            test_util.test_logger('ssh command:%s met exception.' % command)
            return False
    else:
        test_util.test_logger('[SSH] ssh in vm[%s] doing %s, timeout after %s seconds' % (host_ip, command, timeout))
        return False

    test_util.test_logger('[SSH] ssh in vm[%s] doing %s done. result is %s' % (host_ip, command, ssh_result))
    if ssh_result['result'] == 0:
        return ssh_result['output']
    return False

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

        command = '/sbin/ip a'
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

    if os.environ.get('zstackManagementIp') == None:
        lib_set_vm_host_l2_ip(vm)
    host_ip = lib_find_host_by_vm(vm).managementIp
    target_host_in_plan = None
    for host_in_plan in lib_get_all_hosts_from_plan():
        if host_in_plan.managementIp_ == host_ip:
            target_host_in_plan = host_in_plan
            break
    if target_host_in_plan != None:
        h_username = target_host_in_plan.username_
        h_password = target_host_in_plan.password_
        if hasattr(target_host_in_plan, 'port_'):
            h_port = int(target_host_in_plan.port_)
        else:
            h_port = 22
    else:
        h_username = os.environ.get('hostUsername')
        h_password = os.environ.get('hostPassword')
        h_port = 22

    temp_script = '/tmp/%s' % uuid.uuid1().get_hex()

    #copy the target script to target host firstly.
    src_file = _full_path(src_file)
    ssh.scp_file(src_file, temp_script, host_ip, h_username, h_password, port=h_port)

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
    ssh.execute('rm -f %s' % temp_script, host_ip, h_username, h_password, port=h_port)

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
    target_host_in_plan = None
    for host_in_plan in lib_get_all_hosts_from_plan():
        if host_in_plan.managementIp_ == host_ip:
            target_host_in_plan = host_in_plan
            break
    if target_host_in_plan != None:
        h_username = target_host_in_plan.username_
        h_password = target_host_in_plan.password_
        if hasattr(target_host_in_plan, 'port_'):
            h_port = int(target_host_in_plan.port_)
        else:
            h_port = 22
    else:
        h_username = os.environ.get('hostUsername')
        h_password = os.environ.get('hostPassword')
        h_port = 22

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
    ssh.execute('rm -f %s' % temp_script, host_ip, h_username, h_password, port=h_port)
    return rsp

def lib_execute_command_in_vm(vm, cmd, l3_uuid=None, ipv6 = None):
    '''
    The cmd was assumed to be returned as soon as possible.
    '''
    print "pengtao ipv6 is :%s" %(ipv6)
    if not ipv6:
        vr_vm = lib_find_vr_by_vm(vm)
        vr_vm = vr_vm[0]
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

    username = lib_get_vm_username(vm)
    password = lib_get_vm_password(vm)
    test_util.test_logger("Do testing through test agent: %s to ssh vm: %s, ip: %s, with cmd: %s" % (test_harness_ip, vm.uuid, vm_ip, cmd))
    rsp = lib_ssh_vm_cmd_by_agent(test_harness_ip, vm_ip, username, \
            password, cmd)
        
    if not rsp.success:
        ret = False
        test_util.test_logger('ssh error info: %s' % rsp.error)
    else:
        if rsp.result != None:
            ret = str(rsp.result)
            if ret == "":
                ret = "<no stdout output>"
        else:
            ret = rsp.result

    if ret:
        test_util.test_logger('Successfully execute [command:] >>> %s <<< in [vm:] %s' % (cmd, vm_ip))
        return ret
    else:
        test_util.test_logger('Fail execute [command:] %s in [vm:] %s' % (cmd, vm_ip))
        return False


def lib_check_login_in_vm(vm, username, password, retry_times=5, l3_uuid=None):
    '''
    Check login with the assigned username and password.
    '''
    cmd = "exit 0"
    ret = True
    count = 1

    if not l3_uuid:
        vm_ip = vm.vmNics[0].ip
    else:
        vm_ip = lib_get_vm_nic_by_l3(vm, l3_uuid).ip

    if not lib_wait_target_up(vm_ip, '22', 120):
        test_util.test_fail('vm: %s is not startup in 120 seconds. Fail to reboot it. ' % vm.uuid)

    while(count <= retry_times):
        test_util.test_logger("retry count:%s, vm_ip:%s, username:%s, password:%s, cmd:%s" %(str(count), str(vm_ip), str(username), str(password), str(cmd)))
        try:
            ret, output, stderr = ssh.execute(cmd, vm_ip, username, password, False, 22)
        except:
            pass
        if ret == 0:
            test_util.test_logger("successfully login vm: %s" %(vm_ip))
            return True
        time.sleep(1)
        count = count + 1

    #if count > retry_times: retry one more time to raise the exception.
    test_util.test_logger("Failed login vm: %s, retry count bigger than max retry %s times" %(vm_ip, str(retry_times)))
    ret, output, stderr = ssh.execute(cmd, vm_ip, username, password, False, 22)
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
    return 'staticIp::%s::%s' % (l3_uuid, ip_address)

def lib_create_vm_hostname_tag(hostname):
    hostname = '-'.join(hostname.split('_'))
    return 'hostname::%s' % hostname

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

def lib_is_image_vcenter(image):
    if lib_get_hv_type_of_image(image) ==  inventory.VMWARE_HYPERVISOR_TYPE:
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

def lib_is_vm_vcenter(vm):
    if lib_get_hv_type_of_vm(vm) == inventory.VMWARE_HYPERVISOR_TYPE:
        return True
    else:
        return False

def lib_is_sharable_volume(volume):
    if str(volume.isShareable).strip().lower() == "true":
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

    #In local storage environment, if VM is stopped or Destroyed, and its root 
    # volume was migrated to another host. It doesn't have current Host Uuid 
    # and its lastHostUuid can not reflect its real HostUuid for new start up.
    # So we need to use root volume to check the real location.
    if vm.state != inventory.RUNNING and not lib_check_vm_live_migration_cap(vm):
        root_volume = lib_get_root_volume(vm)
        ls_ref = lib_get_local_storage_reference_information(root_volume.uuid)[0]
        vm_host_uuid = ls_ref.hostUuid

    hosts = res_ops.get_resource(res_ops.HOST, session_uuid=None, \
            uuid=vm_host_uuid)

    if hosts:
        #test_util.test_logger('[vm:] %s [host uuid:] %s [host name:] %s is found' % (vm.uuid, host.uuid, host.name))
        return hosts[0]
    else:
        test_util.test_logger('Did not find [vm:] %s host' % vm.uuid)

def lib_get_vm_last_host(vm_inv):
    '''
    Get last host inventory by providing vm inventory. 
    '''
    last_host_uuid = vm_inv.lastHostUuid

    if not last_host_uuid:
        test_util.test_logger("Last Host UUID is None. Can't get Last Host Inventory for [vm:] %s" % vm_inv.uuid)
        return None

    hosts = res_ops.get_resource(res_ops.HOST, session_uuid=None, \
            uuid=last_host_uuid)
    if hosts:
        return hosts[0]
    else:
        test_util.test_logger("Can't get Last Host Inventory for [vm:] %s, maybe the host has been deleted." % vm_inv.uuid)
        return None

def lib_get_host_by_uuid(host_uuid):
    conditions = res_ops.gen_query_conditions('uuid', '=', host_uuid)
    hosts = res_ops.query_resource(res_ops.HOST, conditions)
    if hosts:
        return hosts[0]

def lib_get_host_by_ip(host_ip):
    conditions = res_ops.gen_query_conditions('managementIp', '=', host_ip)
    hosts = res_ops.query_resource(res_ops.HOST, conditions)
    if hosts:
        return hosts[0]

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
                None)
        ps_uuids = []
        if bss[0].type == "Ceph":
            for ps in pss:
                if ps.fsid == bss[0].fsid:
                    ps_uuids.append(ps.uuid)
            return ps_uuids

        for ps in pss:
            ps_uuids.append(ps.uuid)

        return ps_uuids

def lib_get_backup_storage_by_uuid(bs_uuid):
    cond = res_ops.gen_query_conditions('uuid', '=', bs_uuid)
    bss = res_ops.query_resource(res_ops.BACKUP_STORAGE, cond)
    if not bss:
        test_util.test_logger('can not find bs which uuid is: %s' % bs_uuid)
    return bss[0]

def lib_get_another_imagestore_by_uuid(bs_uuid):
    cond = res_ops.gen_query_conditions('uuid', '=', bs_uuid)
    cond = res_ops.gen_query_conditions("type", '=', "ImageStoreBackupStorage", cond)
    bss = res_ops.query_resource(res_ops.BACKUP_STORAGE, cond)
    for bs in bss:
        test_util.test_logger("bs.uuid=%s vs bs_uuid=%s" %(bs.uuid, bs_uuid))
        if bs.uuid != bs_uuid:
            return bs
    else:
        test_util.test_fail("not found candidate bs")

def lib_get_backup_storage_uuid_list_by_zone(zone_uuid):
    '''
    Get backup storage uuid list which attached to zone uuid
    '''
    cond = res_ops.gen_query_conditions('attachedZoneUuids', 'in', zone_uuid)
    cond = res_ops.gen_query_conditions('name', '!=', "only_for_robot_backup_test", cond)
    bss = res_ops.query_resource_fields(res_ops.BACKUP_STORAGE, cond, None, ['uuid'])
    bs_list = []
    for bs in bss:
        bs_list.append(bs.uuid)

    return bs_list

def lib_get_backup_storage_host(bs_uuid):
    '''
    Get host, who has backup storage uuid.
    '''
    def _get_backup_storage_from_scenario_file(backupStorageRefName, scenarioConfig, scenarioFile, deployConfig):
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

    session_uuid = acc_ops.login_as_admin()
    try:
        bss = res_ops.get_resource(res_ops.BACKUP_STORAGE, session_uuid)
    finally:
        acc_ops.logout(session_uuid)
    
    if not bss:
        test_util.test_fail('can not get zstack backup storage inventories.')

    name = None
    for bs in bss:
        if bs.uuid == bs_uuid:
            name = bs.name
            break

    if name == None:
        test_util.test_fail('can not get zstack backup storage inventories.')

    host = test_util.HostOption()
    bss = deploy_config.backupStorages.get_child_node_as_list('sftpBackupStorage') + deploy_config.backupStorages.get_child_node_as_list('imageStoreBackupStorage')
    for bs in bss:
        if bs.name_ == name:
            host.managementIp = bs.hostname_
            host.username = bs.username_
            host.password = bs.password_
            if hasattr(bs, 'port_'):
                host.sshPort = bs.port_

    #host.managementIp = os.environ.get('sftpBackupStorageHostname')
    #host.username = os.environ.get('sftpBackupStorageUsername')
    #host.password = os.environ.get('sftpBackupStoragePassword')
    #hostname_list = _get_backup_storage_from_scenario_file(name, scenarioConfig, scenarioFile, deployConfig)
    hostname_list = _get_backup_storage_from_scenario_file(name, all_scenario_config, scenario_file, deploy_config)
    if len(hostname_list) != 0:
        host.managementIp = hostname_list[0]
    
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
    condition, like {'name':'tag', 'op':'=', 'value':'capability::liveSnapshot'}

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

def lib_get_storage_capacity(zone_uuids = None, cluster_uuids = None, \
        ps_uuids = None, session_uuid = None):
    import apibinding.api_actions as api_actions
    action = api_actions.GetPrimaryStorageCapacityAction()
    if zone_uuids:
        action.zoneUuids = zone_uuids
    if cluster_uuids:
        action.clusterUuids = cluster_uuids
    if ps_uuids:
        action.primaryStorageUuids = ps_uuids

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
            'capability::liveSnapshot')
    tag_info = lib_find_host_tag(host_inv, conditions)
    if tag_info:
        test_util.test_logger('host: %s support live snapshot' % host_inv.uuid)
        return True
    else:
        test_util.test_logger('host: %s does not support live snapshot' \
                % host_inv.uuid)
        return False

def lib_check_vm_live_migration_cap(vm_inv):
    root_volume = lib_get_root_volume(vm_inv)
    ps = lib_get_primary_storage_by_uuid(root_volume.primaryStorageUuid)
    if ps.type == inventory.LOCAL_STORAGE_TYPE:
        if conf_ops.get_global_config_value('localStoragePrimaryStorage', 'liveMigrationWithStorage.allow') == 'true':
            # Not support live migrate for VM with data volume on localstorage
            if len(lib_get_data_volumes(vm_inv)) > 0:
                return False
            return True
        return False
    return True

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

def lib_find_host_by_vr(vr_inv):
    '''
    Get host inventory by providing vr inventory.
    '''
    host_uuid = vr_inv.hostUuid
    if not host_uuid:
        test_util.test_logger("Host UUID is None. Can't get Host IP address for [vr:] %s" % vr_inv.uuid)
        return None

    hosts = res_ops.get_resource(res_ops.HOST, session_uuid=None, \
            uuid=host_uuid)
    if hosts:
        return hosts[0]

def lib_get_host_port(host_ip):
    target_host_in_plan = None
    h_port = None
    for host_in_plan in lib_get_all_hosts_from_plan():
        if host_in_plan.managementIp_ == host_ip:
            target_host_in_plan = host_in_plan
            break
    if target_host_in_plan != None:
        if hasattr(target_host_in_plan, 'port_'):
            h_port = int(target_host_in_plan.port_)

    return h_port

def lib_find_hosts_by_ps_uuid(ps_uuid):
    '''
    find all hosts which is using given ps
    '''
    cond = res_ops.gen_query_conditions('cluster.primaryStorage.uuid', '=', \
            ps_uuid)
    return res_ops.query_resource(res_ops.HOST, cond)

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
#    ps = lib_get_primary_storage_by_uuid(ps_uuid)
#    if ps.type == "SharedBlock":
#        return True
    return False

def lib_find_random_host_by_volume_uuid(volume_uuid):
    '''
    Return a random host inventory. 
    
    The returned host should not be the host holding current volume_inv. But it 
    should belong to the same cluster of volume_inv's primary storage.
    '''
    avail_hosts = vol_ops.get_volume_migratable_host(volume_uuid)
    if avail_hosts:
        return random.choice(avail_hosts)
    return None

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
    # TODO: it should select non-root host for migrate after cold migrate issue is fixed
    for host in all_hosts:
        if host.uuid != current_host_uuid and \
                host.status == host_header.CONNECTED and \
                host.state == host_header.ENABLED and \
                host.username == 'root' and \
                host.sshPort == 22:
            target_hosts.append(host)

    if not target_hosts:
        return None

    return random.choice(target_hosts)

def _lib_assign_host_l3_ip(host_pub_ip, cmd):
    with lock.FileLock(host_pub_ip, lock.Lockf()):
        http.json_dump_post(testagent.build_http_path(host_pub_ip, \
                host_plugin.SET_DEVICE_IP_PATH), cmd)

def _lib_flush_host_l2_ip(host_ip, net_device):
    cmd = host_plugin.FlushDeviceIpCmd()
    cmd.ethname = net_device
    test_util.test_logger('Flush ip address for net device: %s from host: %s' \
            % (net_device, host_ip))
    with lock.FileLock(host_ip, lock.Lockf()):
        http.json_dump_post(testagent.build_http_path(host_ip, \
                host_plugin.FLUSH_DEVICE_IP_PATH), cmd)

def lib_create_host_vlan_bridge(host, cmd):
    with lock.FileLock(host.uuid, lock.Lockf()):
        http.json_dump_post(testagent.build_http_path(host.managementIp, host_plugin.CREATE_VLAN_DEVICE_PATH), cmd)

def lib_check_stored_host_ip_dict(ip_address_list):
    ip_address = '.'.join(ip_address_list)
    host_ip_dict_all = lib_get_stored_host_ip_dict_all()
    for host_ip_dict in host_ip_dict_all:
        for host_ip in host_ip_dict_all[host_ip_dict]:
            if host_ip_dict_all[host_ip_dict][host_ip] == ip_address:
		return True
    return False

#will based on x.y.*.*/16 address. 
#Host ip address will assigned from x.y.128.0 to x.y.255.254
def _lib_gen_host_next_ip_addr(network_address, netmask, addr_list):
    network_addr = network_address.split('.')
    available_ip_list = list(network_addr)
    if netmask == "255.255.255.0":
        for candidate_ip in range(233, 254):
            available_ip_list[3] = str(candidate_ip)
	    if lib_check_stored_host_ip_dict(available_ip_list):
                continue
            else:
                break
    else:
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
def lib_get_stored_host_ip_dict_all():
    host_ip_db = filedb.FileDB(HostL2IpDb)
    return host_ip_db.get_all()

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
        l3 = lib_get_l3_by_l2(l2.uuid)[0]
        lib_assign_host_l2_ip(host, l2, l3)

def lib_assign_host_l2_ip(host, l2, l3):
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
    to be 255.255.0.0/255.255.255.0. The reason is test case will use 
    x.y.0.1~x.y.127.255/x.y.z.2~x.y.z.233 for VM IP assignment; 
    x.y.128.1~x.y.255.254/x.y.z.234~x.y.z.254 for hosts IP assignment.

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
    global HostDefaultEth
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

    def _generate_and_save_host_l2_ip(host_pub_ip, netmask, dev_name):
        host_pub_ip_list = host_pub_ip.split('.')

        host_ip_dict = lib_get_stored_host_ip_dict(dev_name)
        if host_ip_dict and host_ip_dict.has_key(host_pub_ip):
            next_avail_ip = host_ip_dict[host_pub_ip]
            return next_avail_ip

        net_address = l3_ip_ranges.startIp.split('.')
        if netmask == "255.255.0.0":
            net_address[2] = host_pub_ip_list[2]
            net_address[3] = host_pub_ip_list[3]
        net_address = '.'.join(net_address)
        
        next_avail_ip = _lib_gen_host_next_ip_addr(net_address, netmask, None)
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

    def _set_host_l2_ip(host_pub_ip, netmask):
        if scenario_config != None and scenario_file != None and os.path.exists(scenario_file):
            br_ethname = 'br_%s' % l2.physicalInterface.replace("eth", "zsn")
        else:
            br_ethname = 'br_%s' % l2.physicalInterface

        if l2_vxlan_vni:
            br_ethname = 'br_vx_%s' % (l2_vxlan_vni)
        elif l2_vlan:
            br_ethname = '%s_%s' % (br_ethname, l2_vlan)
        if br_ethname == 'br_%s' % HostDefaultEth:
            test_util.test_warn('Dangours: should not change host default network interface config for %s' % br_dev)
            return

        next_avail_ip = _generate_and_save_host_l2_ip(host_pub_ip, netmask, br_ethname+l3.uuid)
        #if ip has been set to other host, following code will do something wrong.
        #if lib_check_directly_ping(next_avail_ip):
        #    test_util.test_logger("[host:] %s [bridge IP:] %s is connectable. Skip setting IP." % (host_pub_ip, next_avail_ip))
        #    return next_avail_ip
        #else:
        #    return _do_set_host_l2_ip(host_pub_ip, next_avail_ip)
    
        return _do_set_host_l2_ip(host_pub_ip, next_avail_ip, br_ethname)

    with lock.FileLock('lib_assign_host_l2_ip', lock.Lockf()):
        host_pub_ip = host.managementIp

        l2_vlan = lib_get_l2_vlan(l2.uuid)
        l2_vxlan_vni = lib_get_l2_vxlan_vni(l2.uuid)
        if not l2_vxlan_vni:
            test_util.test_logger('l2_vx_vni is null in l2.uuid:%s' %(l2.uuid))
        else:
            l2_vxlan_vni = str(l2_vxlan_vni)
            br_vxlan_dev = 'br_vx_%s' % (l2_vxlan_vni)
            test_util.test_logger('vxlan bridge name is: %s' %(br_vxlan_dev))

        if scenario_config != None and scenario_file != None and os.path.exists(scenario_file):
            HostDefaultEth = 'zsn0'

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
    
        #l3 = lib_get_l3_by_l2(l2.uuid)[0]
        if l3.system:
            test_util.test_logger('will not change system management network l3: %s' % l3.name)
            return 

        l3_ip_ranges = l3.ipRanges[0]
        if (l3_ip_ranges.netmask != '255.255.0.0') and (l3_ip_ranges.netmask != '255.255.255.0'):
            test_util.test_warn('L3 name: %s uuid: %s network [mask:] %s is not 255.255.0.0 or 255.255.255.0. Will not assign IP to host. Please change test configuration to make sure L3 network mask is 255.255.0.0 or 255.255.255.0.' % (l3.name, l3.uuid, l3_ip_ranges.netmask))
            return

        #Need to set vlan bridge ip address for local host firstly. 
        cond = res_ops.gen_query_conditions('hypervisorType', '=', inventory.KVM_HYPERVISOR_TYPE)
        all_hosts_ips = res_ops.query_resource_fields(res_ops.HOST, cond, None, \
                ['managementIp'])


        for host_ip in all_hosts_ips:
            #if current host is ZStack host, will set its bridge l2 ip firstly.
            if linux.is_ip_existing(host_ip.managementIp):
                current_host_ip = host_ip.managementIp
                if l2_vxlan_vni:
                    next_avail_ip = _generate_and_save_host_l2_ip(current_host_ip, l3_ip_ranges.netmask, br_vxlan_dev+l3.uuid)
                    try:
                        linux.set_device_ip(br_vxlan_dev, next_avail_ip, l3_ip_ranges.netmask)
                        test_util.test_logger('vxlan set ip:%s for bridge: %s' % (next_avail_ip, br_vxlan_dev))
                    except Exception, e:
                        test_util.test_logger('@@warning: because br_vx_xxx now only created when vm that used it has been created, ignore exception %s' % (str(e)))
                else:
                    _set_host_l2_ip(current_host_ip, l3_ip_ranges.netmask)
                break
        else:
            test_util.test_logger("Current machine is not in ZStack Hosts. Will directly add vlan device:%s and set ip address." % l2_vlan)
            if l2_vxlan_vni:
                pass
            else:
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

                next_avail_ip = _generate_and_save_host_l2_ip(current_host_ip, l3_ip_ranges.netmask, \
                        br_dev+l3.uuid)

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
            _set_host_l2_ip(host_pub_ip, l3_ip_ranges.netmask)

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
    if not lib_check_system_cmd('telnet'):
    #if not lib_check_system_cmd('nc'):
        return False == expect_result

    try:
        shell.call('echo "quit" | timeout 4 telnet %s %s|grep "Escape character"' % (target_ip, target_port))
        #shell.call('nc -w1 %s %s' % (target_ip, target_port))
        test_util.test_logger('check target: %s port: %s connection success' % (target_ip, target_port))
        return True == expect_result
    except:
        test_util.test_logger('check target: %s port: %s connection failed' % (target_ip, target_port))
        return False == expect_result

def lib_wait_target_down(target_ip, target_port, timeout=60):
    '''
        wait for target "machine" shutdown by checking its network connection, 
        until timeout. 
    '''
    def wait_network_check(param_list):
        return lib_network_check(param_list[0], param_list[1], param_list[2])

    return linux.wait_callback_success(wait_network_check, (target_ip, target_port, False), timeout)

def lib_wait_target_up(target_ip, target_port, timeout=300):
    '''
        wait for target "machine" startup by checking its network connection, 
        until timeout. 
    '''
    def wait_network_check(param_list):
        return lib_network_check(param_list[0], param_list[1], param_list[2])

    return linux.wait_callback_success(wait_network_check, (target_ip, target_port, True), timeout)

def lib_check_win_target_up(vr_ip, target_ip, target_port, timeout=60):
    '''
        check windows vm already running
    '''
    global SSH_TIMEOUT
    pre_ssh_timeout = SSH_TIMEOUT 
    SSH_TIMEOUT = timeout

    cmd = 'echo "quit" | timeout 4 telnet %s %s|grep "Escape character"' % (target_ip, target_port)
    if lib_execute_sh_cmd_by_agent_with_retry(vr_ip, cmd):
        test_util.test_logger("[target_ip:] %s from [vr:] %s Test Pass" % (target_ip, vr_ip))
    else:
        test_util.test_fail("target_ip: %s is failed by telnet from vr %s." %(target_ip, vr_ip))

    SSH_TIMEOUT = pre_ssh_timeout

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

def lib_get_l2_vxlan_vni(l2_uuid, session_uuid=None):
    '''
        return vxlan vni value for L2. If L2 doesn't have vxlan, will return None
    '''
    l2_network = res_ops.get_resource(res_ops.L2_NETWORK, session_uuid, uuid=l2_uuid)
    if l2_network[0].type != "VxlanNetwork":
        return None
    else:
        test_util.test_logger('Found vxlan L2 network:%s. ' % l2_uuid)
        return l2_network[0].vni
            
    #l2_vxlan = res_ops.get_resource(res_ops.L2_VXLAN_NETWORK, session_uuid, uuid=l2_uuid)
    #if l2_vxlan:
    #    return l2_vxlan[0].vni
    #test_util.test_logger('L2: %s did not have vlan. ' % l2_uuid)
    #return None


def lib_get_l2_interface_by_name(l2_name, session_uuid=None):
    '''
        return l2 interface by the provided l2 name
    '''
    l2net = res_ops.get_resource(res_ops.L2_NETWORK, session_uuid, name=l2_name)

    if l2net:
        return l2net[0].physicalInterface
    else:
        test_util.test_logger("NOT FOUND L2 NETWORK BY NAME %s" %(l2_name))
        return None


def lib_get_l2_magt_nic_by_vr_offering(vr_offering_uuid=None, session_uuid=None):
    '''
        return l2 management interface by vr offering
    '''
    if not vr_offering_uuid:
        vr_offering_inv = res_ops.get_resource(res_ops.VR_OFFERING, session_uuid)
    else:
        vr_offering_inv = res_ops.get_resource(res_ops.VR_OFFERING, session_uuid, uuid=vr_offering_uuid)

    if not vr_offering_inv:
        test_util.test_logger("NOT FOUND VR OFFERING.")
        return None

    l3_uuid = vr_offering_inv[0].managementNetworkUuid
    l3_inv = res_ops.get_resource(res_ops.L3_NETWORK, session_uuid, uuid=l3_uuid)
    if not l3_inv:
        test_util.test_logger("NOT FOUND L3 BY l3_uuid: %s" %(l3_uuid))
        return None

    l2_uuid = l3_inv[0].l2NetworkUuid
    l2_inv = res_ops.get_resource(res_ops.L2_NETWORK, session_uuid, uuid=l2_uuid)
    if not l2_inv:
        test_util.test_logger("NOT FOUND L2 BY l2_uuid: %s" %(l2_uuid))
        return None

    return l2_inv[0].physicalInterface


def lib_get_l2_pub_nic_by_vr_offering(vr_offering_uuid=None, session_uuid=None):
    '''
        return l2 public interface by vr offering
    '''
    if not vr_offering_uuid:
        vr_offering_inv = res_ops.get_resource(res_ops.VR_OFFERING, session_uuid)
    else:
        vr_offering_inv = res_ops.get_resource(res_ops.VR_OFFERING, session_uuid, uuid=vr_offering_uuid)

    if not vr_offering_inv:
        test_util.test_logger("NOT FOUND VR OFFERING.")
        return None

    l3_uuid = vr_offering_inv[0].publicNetworkUuid
    l3_inv = res_ops.get_resource(res_ops.L3_NETWORK, session_uuid, uuid=l3_uuid)
    if not l3_inv:
        test_util.test_logger("NOT FOUND L3 BY l3_uuid: %s" %(l3_uuid))
        return None

    l2_uuid = l3_inv[0].l2NetworkUuid
    l2_inv = res_ops.get_resource(res_ops.L2_NETWORK, session_uuid, uuid=l2_uuid)
    if not l2_inv:
        test_util.test_logger("NOT FOUND L2 BY l2_uuid: %s" %(l2_uuid))
        return None

    return l2_inv[0].physicalInterface


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

def lib_get_l3_service_providers(l3):
    service_providers = []
    for ns in l3.networkServices:
        sp_uuid = ns.networkServiceProviderUuid
        sp = lib_get_network_service_provider_by_uuid(sp_uuid)
        for temp_sp in service_providers:
            if temp_sp.uuid == sp_uuid:
                break
        else:
            service_providers.append(sp)

    return service_providers

def lib_get_network_service_provider_by_uuid(sp_uuid):
    cond = res_ops.gen_query_conditions('uuid', '=', sp_uuid)
    test_util.test_logger('look for service provider: %s ' % sp_uuid)
    return res_ops.query_resource(res_ops.NETWORK_SERVICE_PROVIDER, cond)[0]

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

def lib_get_vm_first_nic(vm):
    '''
    Will return VM's first NIC 
    '''
    for nic in vm.vmNics:
        if nic.deviceId == 0:
            return nic

def lib_get_vm_last_nic(vm):
    '''
    Will return VM's last NIC 
    '''
    vmNics = vm.vmNics
    num = len(vmNics) - 1
    for nic in vmNics:
        if nic.deviceId == num:
            return nic

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

def lib_get_vm_l3_service_providers(vm):
    l3s = lib_get_l3s_by_vm(vm)
    if not l3s:
        test_util.test_logger('Did not find l3 for [vm:] %s' % vm.uuid)
        return False
    service_providers = []
    for l3 in l3s:
        sps = lib_get_l3_service_providers(l3)
        for temp_sp1 in sps:
            for temp_sp2 in service_providers:
                if temp_sp1.uuid == temp_sp2.uuid:
                    break
            else:
                service_providers.append(temp_sp1)

    return service_providers

def lib_get_vm_l3_service_provider_types(vm):
    sps = lib_get_vm_l3_service_providers(vm)
    sps_types = []
    for sp in sps:
        sps_types.append(sp.type)
    return sps_types

def lib_get_flat_dhcp_by_vm(vm):
    l3s = lib_get_l3s_by_vm(vm)
    if not l3s:
        test_util.test_logger('Did not find l3 for [vm:] %s' % vm.uuid)
        return False

    for l3 in l3s:
        sps = lib_get_l3_service_providers(l3)
        for service in l3.networkServices:
            if service.networkServiceType == "DHCP":
                for temp_sp1 in sps:
                    if temp_sp1.type == 'Flat' and service.networkServiceProviderUuid == temp_sp1.uuid:
                        return True
    return False

def lib_check_nic_in_db(vm_inv, l3_uuid):
    '''
    Check if VM has NIC in l3_uuid
    '''
    nic_inv = lib_get_vm_nic_by_l3(vm_inv, l3_uuid)
    if not nic_inv:
        return False

    return True

def lib_restart_vm_network(vm_inv, target_l3_uuid = None):
    '''
    will ssh vm and check all available nic, then use dhclient to get ip

    If target_l3_uuid provided, will ssh the IP of NIC on target_l3_uuid
    If target_l3_uuid is missed, will use Nic of deviceId=0
    '''
    if not target_l3_uuid:
        nic = lib_get_vm_first_nic(vm_inv)
        target_l3_uuid = nic.l3NetworkUuid

    script = """#!/bin/sh
pkill -9 dhclient

device_id="0 1 2 3 4 5 6 7 8 9"
available_devices=''
for i in $device_id;do
    ifconfig eth$i >/dev/null 2>&1
    if [ $? -eq 0 ];then
        available_devices="$available_devices eth$i"
    fi
done

dhclient $available_devices
"""
    lib_execute_command_in_vm(vm_inv, script, target_l3_uuid)

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

#-----------Get Baremetal resource-------------
def lib_get_chassis_by_name(name):
    conditions = res_ops.gen_query_conditions('name', '=', name)
    chassis = res_ops.query_resource(res_ops.CHASSIS, conditions)
    if chassis:
        return chassis[0]

def lib_get_hwinfo(chassis_uuid):
    conditions = res_ops.gen_query_conditions('uuid', '=', chassis_uuid)
    chassis = res_ops.query_resource(res_ops.CHASSIS, conditions)
    if chassis:
        return chassis[0].hardwareInfos, chassis[0].status

def lib_get_chassis_by_uuid(chassis_uuid):
    conditions = res_ops.gen_query_conditions('uuid', '=', chassis_uuid)
    chassis = res_ops.query_resource(res_ops.CHASSIS, conditions)
    if chassis:
        return chassis[0]

def lib_get_pxe_by_name(name):
    conditions = res_ops.gen_query_conditions('name', '=', name)
    pxe = res_ops.query_resource(res_ops.PXE_SERVER, conditions)
    if pxe:
        return pxe[0]

#-----------Get Affinity Group----------
def lib_get_affinity_group_by_name(name):
    conditions = res_ops.gen_query_conditions('name', '=', name)
    ag = res_ops.query_resource(res_ops.AFFINITY_GROUP, conditions)
    if ag:
        return ag[0]

#-----------Get VM resource-------------
def lib_is_vm_running(vm_inv):
    if vm_inv.state == 'Running':
        return True

    return False

def lib_get_instance_offering_by_uuid(io_uuid):
    conditions = res_ops.gen_query_conditions('uuid', '=', io_uuid)
    offerings = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)
    if offerings:
        return offerings[0]

def lib_get_instance_offering_by_name(ins_name):
    cond = res_ops.gen_query_conditions('name', '=', ins_name)
    ins_offerings = res_ops.query_resource_with_num(res_ops.INSTANCE_OFFERING, cond, None, 0, 1)
    if ins_offerings:
        return ins_offerings[0]
    test_util.test_logger("Did not find instance offering by [instance offering name:] %s" % ins_name)


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
    test_util.test_logger("lib_get_vm_nic_by_l3")
    for vmNic in vm.vmNics:
        test_util.test_logger("@@@DEBUG@@@: vm_l3_uuid=%s; l3_uuid=%s" %(vmNic.l3NetworkUuid, l3_uuid))
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

    test_util.test_logger("did not find NIC for VM: %s, which is using VR: %s" \
            % (vm.uuid, vr.uuid))

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

def lib_get_vm_video_type(vm):
    cmd = "virsh dumpxml %s |grep vram | awk -F 'type=' '{print $2}' | awk -F \"'\" '{print $2}'" % vm.uuid
    host_ip = lib_find_host_by_vm(vm).managementIp
    rsp = lib_execute_sh_cmd_by_agent(host_ip, cmd)
    if rsp.return_code == 0:
        ret = rsp.stdout.strip()
        test_util.test_logger('Find [vm:] %s [internalId:] %s on [host:] %s video type' % (vm.uuid, ret, host_ip))
        return ret
    else:
        test_util.test_logger('shell error info: %s' % rsp.stderr)
        #test_util.test_logger('shell command: %s' % rsp.command)
        test_util.test_logger('Can not get [vm:] %s video type on [host:] %s' % (vm.uuid, host_ip))
        return None

def lib_get_root_image_from_vm(vm):
    for volume in vm.allVolumes:
        if volume.type == vol_header.ROOT_VOLUME:
            vm_root_image_uuid = volume.rootImageUuid

    if not vm_root_image_uuid:
        test_util.test_logger("Can't find root device for [vm:] %s" % vm.uuid)
        return False

    condition = res_ops.gen_query_conditions('uuid', '=', vm_root_image_uuid)
    try:
        image = res_ops.query_resource(res_ops.IMAGE, condition)[0]
    except Exception, e:
        test_util.test_logger("QueryImage find exception: %s" %(str(e)))
        return False
    return image

def lib_get_vm_username(vm):
    image = lib_get_root_image_from_vm(vm)
    if not image:
        image_plan = False
    else:
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
    if not image:
        image_plan = False
    else:
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
    private l3 might have multi vrs, this function will only return the VR
    which has DHCP role. 
    '''
    #use compound query condition
    cond = res_ops.gen_query_conditions('vmNics.l3NetworkUuid', '=', \
            l3_uuid)
    #cond = res_ops.gen_query_conditions('vmNics.metaData', '!=', '1', \
    #        cond)
    #cond = res_ops.gen_query_conditions('vmNics.metaData', '!=', '2', \
    #        cond)
    #cond = res_ops.gen_query_conditions('vmNics.metaData', '!=', '3', \
    #        cond)
    cond = res_ops.gen_query_conditions('vmNics.metaData', '>', '3', \
            cond)
    cond = res_ops.gen_query_conditions('__systemTag__', '=', 'role::DHCP', cond)
    vrs = res_ops.query_resource_with_num(res_ops.APPLIANCE_VM, cond, \
            None, 0, 1)

    if vrs and len(vrs) != 0:
        return vrs[0]

    cond = res_ops.gen_query_conditions('vmNics.l3NetworkUuid', '=', \
            l3_uuid)
    cond = res_ops.gen_query_conditions('vmNics.metaData', '>', '3', \
            cond)
    vrs = res_ops.query_resource_with_num(res_ops.APPLIANCE_VM, cond, \
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
    vrs_virtualrouter = res_ops.query_resource(res_ops.APPLIANCE_VM, conditions, session_uuid)
    conditions = res_ops.gen_query_conditions('applianceVmType', '=', 'vrouter')
    vrs_vyos = res_ops.query_resource(res_ops.APPLIANCE_VM, conditions, session_uuid)
    conditions = res_ops.gen_query_conditions('applianceVmType', '=', 'vpcvrouter')
    vpc_vyos = res_ops.query_resource(res_ops.APPLIANCE_VM, conditions, session_uuid)

    return vrs_virtualrouter + vrs_vyos + vpc_vyos

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
    cond = res_ops.gen_query_conditions('vmNics.metaData', '>', '3', cond)
    cond = res_ops.gen_query_conditions('__systemTag__', '=', 'role::DHCP', cond)
    vrs = res_ops.query_resource(res_ops.APPLIANCE_VM, cond, session_uuid)

    if not vrs or len(vrs) == 0:
        cond = res_ops.gen_query_conditions('vmNics.l3NetworkUuid', 'in', \
                ','.join(vm_l3s))
        cond = res_ops.gen_query_conditions('vmNics.metaData', '>', '3', cond)
        vrs = res_ops.query_resource(res_ops.APPLIANCE_VM, cond, session_uuid)

        if not vrs:
            test_util.test_logger("Cannot find VM: [%s] 's Virtual Router VM" \
                    % vm.uuid)
    
    tmp_vr_list = []
    tmp_l3s_list = list(vm_l3s) 
    if vrs:
        for vr in vrs:
            for nic in vr.vmNics:
                for l3 in tmp_l3s_list:
                    if nic.l3NetworkUuid == l3 and int(nic.metaData) & 4 == 4:
                        tmp_vr_list.append(vr)
    vrs = tmp_vr_list


    return vrs

def lib_find_flat_dhcp_vr_by_vm(vm, session_uuid=None):
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
    cond = res_ops.gen_query_conditions('vmNics.metaData', '>', '3', cond)
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
    result = lib_retry_when_exception(vol_ops.attach_volume, [volume_uuid, vm_uuid, session_uuid], 1)
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

def lib_get_volume_object_host(volume_obj):
    volume = volume_obj.get_volume()
    try:
        primaryStorageUuid = volume.primaryStorageUuid
        if not primaryStorageUuid:
            test_util.test_logger('Did not find any primary storage for [volume:] %s. Can not find [host] for this volume. It mostly means the volume is not attached to any VM yet. ' % volume.uuid)
            return None

	if volume.type == 'Data':
            ps = lib_get_primary_storage_by_uuid(primaryStorageUuid)
            if ps.type == inventory.NFS_PRIMARY_STORAGE_TYPE:
                attached_cluster = ','.join(ps.attachedClusterUuids)
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

        vm = volume_obj.get_target_vm().get_vm()
        host = lib_get_vm_host(vm)
        return host
    except:
        test_util.test_logger('Could not find any host for [volume:] %s.' % volume.uuid)

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
    cond = res_ops.gen_query_conditions('name', '!=', "only_for_robot_backup_test")
    bss = res_ops.query_resource(res_ops.BACKUP_STORAGE, cond, session_uuid)
    volume = lib_get_volume_by_uuid(volume_uuid)
    bs_uuid = None
    if volume.vmInstanceUuid != None:
        vm = lib_get_vm_by_uuid(volume.vmInstanceUuid)
        if vm.state == vm_header.RUNNING:
            for bs in bss:
                if hasattr(inventory, 'IMAGE_STORE_BACKUP_STORAGE_TYPE') and bs.type == inventory.IMAGE_STORE_BACKUP_STORAGE_TYPE:
                    bs_uuid = bs.uuid
                    break
    ps = lib_get_primary_storage_by_uuid(volume.primaryStorageUuid)
    if ps.type == "Ceph":
        for bs in bss:
            if bs.fsid == ps.fsid:
                bs_uuid = bs.uuid
                break
    if bs_uuid == None:
        bs_uuid = bss[random.randint(0, len(bss)-1)].uuid
    #[Inlined import]
    import zstackwoodpecker.zstack_test.zstack_test_image as zstack_image_header
    image = zstack_image_header.ZstackTestImage()
    image_creation_option = test_util.ImageOption()
    image_creation_option.set_backup_storage_uuid_list([bs_uuid])
    image_creation_option.set_root_volume_uuid(volume_uuid)
    image_creation_option.set_name('test_image')
    image_creation_option.set_timeout(7200000)
    image.set_creation_option(image_creation_option)
    image.create()

    return image

def lib_create_template_from_data_volume(volume_uuid, session_uuid=None):
    bss = res_ops.get_resource(res_ops.BACKUP_STORAGE, session_uuid)
    volume = lib_get_volume_by_uuid(volume_uuid)
    bs_uuid = None
    if volume.vmInstanceUuid != None:
        vm = lib_get_vm_by_uuid(volume.vmInstanceUuid)
        if vm.state == vm_header.RUNNING:
            for bs in bss:
                if hasattr(inventory, 'IMAGE_STORE_BACKUP_STORAGE_TYPE') and bs.type == inventory.IMAGE_STORE_BACKUP_STORAGE_TYPE:
                    bs_uuid = bs.uuid
                    break
    if bs_uuid == None:
        bs_uuid = bss[random.randint(0, len(bss)-1)].uuid
    #[Inlined import]
    import zstackwoodpecker.zstack_test.zstack_test_image as zstack_image_header
    image = zstack_image_header.ZstackTestImage()
    image_creation_option = test_util.ImageOption()
    image_creation_option.set_backup_storage_uuid_list([bs_uuid])
    image_creation_option.set_name('test_image')
    image.set_creation_option(image_creation_option)
    image.create(apiid=None, root=False)

    return image


def lib_get_root_volume(vm):
    '''
    get root volume inventory by vm inventory
    '''
    volumes = vm.allVolumes
    for volume in volumes:
        if volume.type == vol_header.ROOT_VOLUME:
            return volume

def lib_get_data_volumes(vm):
    volumes = vm.allVolumes
    data_volumes = []
    for volume in volumes:
        if volume.type != vol_header.ROOT_VOLUME:
            data_volumes.append(volume)

    return data_volumes

def lib_destroy_vm_and_data_volumes(vm_inv):
    data_volumes = lib_get_data_volumes(vm_inv)
    vm_ops.destroy_vm(vm_inv.uuid)
    for data_volume in data_volumes:
        vol_ops.delete_volume(data_volume.uuid)

def lib_destroy_vm_and_data_volumes_objs_update_test_dict(vm_obj, test_obj_dict):
    vm_obj.destroy()
    test_obj_dict.rm_vm(vm_obj)
    for volume in test_obj_dict.get_volume_list():
        volume.clean()

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
    for img in images:
        if img.name_ == image.name:
            return img

    if not xmlobject.has_element(deploy_config, "vcenter.images"):
        return None

    images_vcenter = deploy_config.vcenter.images.image
    if not isinstance(images_vcenter, list):
        if images_vcenter.name_ == image.name:
            return images
    for img in images_vcenter:
        if img.name_ == image.name:
            return img
    return None

def lib_get_disk_offering_by_name(do_name, session_uuid = None):
    conditions = res_ops.gen_query_conditions('name', '=', do_name)
    disk_offering = res_ops.query_resource(res_ops.DISK_OFFERING, conditions, \
            session_uuid)
    if not disk_offering:
        test_util.test_logger('Could not find disk offering with [name:]%s ' % do_name)
        return None
    else:
        return disk_offering[0]
    #disk_offerings = res_ops.get_resource(res_ops.DISK_OFFERING, session_uuid=None)
    #for disk_offering in disk_offerings:
    #    if disk_offering.name == do_name:
    #        return disk_offering

def lib_get_images(session_uuid = None):
    return res_ops.get_resource(res_ops.IMAGE, session_uuid = session_uuid)

def lib_get_root_images(session_uuid = None):
    cond = res_ops.gen_query_conditions('mediaType', '=', 'RootVolumeTemplate')
    cond = res_ops.gen_query_conditions('status', '!=', 'Deleted', cond)
    return res_ops.query_resource(res_ops.IMAGE, cond, session_uuid)

def lib_get_data_images(session_uuid = None):
    cond = res_ops.gen_query_conditions('mediaType', '=', 'DataVolumeTemplate')
    return res_ops.query_resource(res_ops.IMAGE, cond, session_uuid)

def lib_get_ISO(session_uuid = None):
    cond = res_ops.gen_query_conditions('mediaType', '=', 'ISO')
    return res_ops.query_resource(res_ops.IMAGE, cond, session_uuid)

def lib_get_image_by_uuid(image_uuid, session_uuid = None):
    condition = res_ops.gen_query_conditions('uuid', '=', image_uuid)
    images = res_ops.query_resource(res_ops.IMAGE, condition, session_uuid)
    if images:
        return images[0]

def lib_get_vm_image(vm_inv, session_uuid = None):
    '''
    return vm_inv's image template inventory
    '''
    root_volume_inv = lib_get_root_image_from_vm(vm_inv)
    return lib_get_image_by_uuid(root_volume_inv.rootImageUuid, session_uuid)

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

def lib_get_ready_image_by_name(img_name, bs_type=None):
    cond = res_ops.gen_query_conditions('name', '=', img_name)
    cond = res_ops.gen_query_conditions('status', '=', 'Ready', cond)
    cond = res_ops.gen_query_conditions('state', '=', 'Enabled', cond)
    images = res_ops.query_resource(res_ops.IMAGE, cond)
    if bs_type:
        images = [img for img in images if res_ops.query_resource(res_ops.BACKUP_STORAGE, res_ops.gen_query_conditions('uuid', '=', img.backupStorageRefs[0].backupStorageUuid))[0].type == bs_type]
    if images:
        return random.choice(images)
    test_util.test_logger("not find image with name: %s" % img_name)
    return False

def lib_get_image_by_name(img_name, bs_type=None):
    cond = res_ops.gen_query_conditions('name', '=', img_name)
    images = res_ops.query_resource(res_ops.IMAGE, cond)
    if bs_type:
        images = [img for img in images if res_ops.query_resource(res_ops.BACKUP_STORAGE, res_ops.gen_query_conditions('uuid', '=', img.backupStorageRefs[0].backupStorageUuid))[0].type == bs_type]
    if images:
        return random.choice(images)
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
    backupStorages = image.backupStorageRefs
    bs_one = backupStorages[0]
    bs = lib_get_backup_storage_by_uuid(bs_one.backupStorageUuid)
    image_url = bs_one.installPath
    host = lib_get_backup_storage_host(bs.uuid)
    if hasattr(inventory, 'IMAGE_STORE_BACKUP_STORAGE_TYPE') and bs.type == inventory.IMAGE_STORE_BACKUP_STORAGE_TYPE:
        image_info = image_url.split('://')[1].split('/')
        image_url = '%s/registry/v1/repos/public/%s/manifests/revisions/%s' \
                % (bs.url, image_info[0], image_info[1])
	conditions = res_ops.gen_query_conditions('uuid', '=', image.uuid)
        _image = res_ops.query_resource(res_ops.IMAGE, conditions)
        if not _image:
            image_url += '/deleted'
            return not lib_check_file_exist(host, image_url)
        return lib_check_file_exist(host, image_url)

    elif bs.type == inventory.SFTP_BACKUP_STORAGE_TYPE:
        return lib_check_file_exist(host, image_url)

    test_util.test_logger('Did not find suiteable checker for bs: %s, whose type is: %s ' % (bs.uuid, bs.type))

def lib_check_sharedblock_file_exist(host, path):
    #cmd = "echo 11;lvdisplay | grep %s" % path
    cmd = "lvdisplay"
    result = lib_execute_ssh_cmd(host.managementIp, 'root', 'password', cmd)
    if path in result:
        return True
    else:
        return False

def lib_check_file_exist(host, file_path):
    command = 'ls -l %s' % file_path
    eout = ''
    try:
        if host.sshPort != None:
            (ret, out, eout) = ssh.execute(command, host.managementIp, host.username, host.password, port=int(host.sshPort))
	else:
            (ret, out, eout) = ssh.execute(command, host.managementIp, host.username, host.password)
        test_util.test_logger('[file:] %s was found in [host:] %s' % (file_path, host.managementIp))
        return True
    except:
        #traceback.print_exc(file=sys.stdout)
        test_util.test_logger('Fail to execute: ssh [host:] %s with [username:] %s and [password:] %s to check [file:] %s . This might be expected behavior.'% (host.managementIp, host.username, host.password, file_path))
        test_util.test_logger('ssh execution stderr output: %s' % eout)
        test_util.test_logger(linux.get_exception_stacktrace())
        return False

def lib_check_backup_storage_file_exist(backup_storage, file_path):
    command = 'ls -l %s' % file_path
    eout = ''
    try:
        if backup_storage.sshPort != None:
            (ret, out, eout) = ssh.execute(command, backup_storage.hostname, backup_storage.username, backup_storage.password, port=backup_storage.sshPort)
	else:
            (ret, out, eout) = ssh.execute(command, backup_storage.hostname, backup_storage.username, backup_storage.password)
        test_util.test_logger('[file:] %s was found in [host:] %s' % (file_path, backup_storage.hostname))
        return True
    except:
        #traceback.print_exc(file=sys.stdout)
        test_util.test_logger('Fail to execute: ssh [backup_storage:] %s with [username:] %s and [password:] %s to check [file:] %s . This might be expected behavior.'% (backup_storage.hostname, backup_storage.username, backup_storage.password, file_path))
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

def lib_get_ShareableVolume_Vm(volume_uuid):
    conditions = res_ops.gen_query_conditions('volumeUuid', '=', volume_uuid)
    vms = res_ops.query_resource(res_ops.SHARE_VOLUME, conditions)
    return vms

def lib_mkfs_for_volume(volume_uuid, vm_inv, mount_point=None):
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

    if volume.isShareable:
        vms = lib_get_ShareableVolume_Vm(volume.uuid)
        old_vms_uuid = []
        for vm in vms:
            old_vms_uuid.append(vm.vmInstanceUuid)
            lib_detach_volume(volume_uuid, vm.vmInstanceUuid)
    else:
        old_vms_uuid = None
        if volume.vmInstanceUuid:
            old_vms_uuid = volume.vmInstanceUuid
            lib_detach_volume(volume_uuid)
        old_vms_uuid=[old_vms_uuid]

    lib_attach_volume(volume_uuid, vm_inv.uuid)

    if not mount_point:
        mount_point = '/tmp/zstack/mnt'
    import tempfile
    script_file = tempfile.NamedTemporaryFile(delete=False)
    script_file.write('''
mkdir -p %s
device="/dev/`ls -ltr --file-type /dev | awk '$4~/disk/ {print $NF}' | grep -v '[[:digit:]]' | tail -1`"
mount ${device}1 %s
if [ $? -ne 0 ]; then
    fdisk $device <<EOF
n
p
1


w
EOF
    mkfs.vfat ${device}1
else
    umount %s
fi
''' % (mount_point, mount_point, mount_point))
    script_file.close()

    if not lib_execute_shell_script_in_vm(vm_inv, script_file.name):
        test_util.test_fail("make partition and make filesystem operation failed in [volume:] %s in [vm:] %s" % (volume_uuid, vm_inv.uuid))

        lib_detach_volume(volume_uuid, vm_inv.uuid)
        os.unlink(script_file.name)
        return False

    test_util.test_logger("Successfully make partition and make filesystem operation in [volume:] %s in [vm:] %s" % (volume_uuid, vm_inv.uuid))

    lib_detach_volume(volume_uuid,vm_inv.uuid)
    os.unlink(script_file.name)

    for old_vm_uuid in old_vms_uuid:
        lib_attach_volume(volume_uuid, old_vm_uuid)

    return True

#-----------Snapshot Operations-----------
def lib_get_volume_snapshot_tree(volume_uuid = None, tree_uuid = None, session_uuid = None):
    #if not volume_uuid and not tree_uuid:
    #    test_util.test_logger("volume_uuid and tree_uuid should not be None at the same time")
    #    return 

    #import apibinding.api_actions as api_actions
    #action = api_actions.GetVolumeSnapshotTreeAction()
    #action.volumeUuid = volume_uuid
    #action.treeUuid = tree_uuid
    #ret = acc_ops.execute_action_with_session(action, session_uuid).inventories
    #return ret

    if volume_uuid:
        cond = res_ops.gen_query_conditions('volumeUuid', '=', volume_uuid)
    elif tree_uuid:
        cond = res_ops.gen_query_conditions('uuid', '=', tree_uuid)
    else:
        test_util.test_logger("volume_uuid and tree_uuid should not be None at the same time")
        return

    result = res_ops.query_resource(res_ops.VOLUME_SNAPSHOT_TREE, cond, session_uuid)

    return result

def lib_get_volume_snapshot(snapshot_uuid = None, session_uuid = None):

    if snapshot_uuid:
        cond = res_ops.gen_query_conditions('uuid', '=', snapshot_uuid)
    else:
        test_util.test_logger("snapshot_uuid should not be None")
        return

    result = res_ops.query_resource(res_ops.VOLUME_SNAPSHOT, cond, session_uuid)

    return result

def lib_get_child_snapshots(snapshot):
    '''
    return child snapshots for a given snapshot
    '''

    import json
    import zstacklib.utils.jsonobject as jsonobject

    def _get_leaf_nodes(tree):
        if not tree:
            return 0

        leaf_nodes = []

        if not tree.has_key('children'):
            test_util.test_fail('Snapshot tree has invalid format, it does not has key for children.')

        if tree['children']:
            for child in tree['children']:
                leaf_node = _get_leaf_nodes(child)
                for i in leaf_node:
                    leaf_nodes.append(i)
        else:
            leaf_nodes.append(tree)

        return leaf_nodes


    snapshot_volume = snapshot.get_snapshot().volumeUuid
    vol_trees = lib_get_volume_snapshot_tree(snapshot_volume)
    child_snapshots = []

    if not vol_trees:
        test_util.test_logger("No snapshot tree found for %s" % (snapshot))
        return

    for vol_tree in vol_trees:
        tree = json.loads(jsonobject.dumps(vol_tree))['tree']

        for i in _get_leaf_nodes(tree):
            if i['inventory'].has_key('parentUuid'):
                if snapshot.get_snapshot().uuid == i['inventory']['parentUuid']:
                    test_util.test_logger("child snapshot %s found for %s" % (i, snapshot))
                    child_snapshots.append(i)
            else:
                test_util.test_logger("no parent node found for %s" % (i['inventory']['uuid']))

    if child_snapshots:
        return child_snapshots
    else:
        test_util.test_logger('No child found for %s' % (snapshot))
        return

def lib_get_diff_snapshots_with_zs(test_dict, volume_uuid):
    '''
    check if a snapshot is in a volume's snapshot tree
    '''

    import json
    import zstacklib.utils.jsonobject as jsonobject

    def _get_leaf_nodes(tree):
        if not tree:
            return 0

        leaf_nodes = []

        if not tree.has_key('children'):
            test_util.test_fail('Snapshot tree has invalid format, it does not has key for children.')

        if tree['children']:
            for child in tree['children']:
                leaf_node = _get_leaf_nodes(child)
                for i in leaf_node:
                    leaf_nodes.append(i)
        else:
            leaf_nodes.append(tree)

        return leaf_nodes


    vol_trees = lib_get_volume_snapshot_tree(volume_uuid)
    volume_snapshots = test_dict.get_volume_snapshot(volume_uuid)
    diff_snapshots = []

    if not vol_trees:
        test_util.test_logger("No snapshot tree found for %s" % (volume_uuid))
        return

    for vol_tree in vol_trees:
        tree = json.loads(jsonobject.dumps(vol_tree))['tree']

        for i in _get_leaf_nodes(tree):
            covered = 0
            for candidate_snapshot in volume_snapshots.get_primary_snapshots():
                if i['inventory']['uuid'] == candidate_snapshot.get_snapshot().uuid:
                    #test_util.test_logger("%s is found in volume snapshot tree %s" % (i['inventory']['uuid'], volume_uuid))
                    covered = 1
                    break
            if covered == 0:
                test_util.test_logger("check sp diff: %s is not found in volume snapshot tree %s, suppose it should be generated by auto" % (i['inventory']['uuid'], volume_uuid))
                diff_snapshots.append(i)

    return diff_snapshots
            
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
def lib_open_vm_listen_ports(vm, ports, l3_uuid=None, target_ip = None, target_ipv6 = None):
    target_ports = ' '.join(str(port) for port in ports)
    if not target_ipv6:
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
        flush_iptables_cmd = 'iptables -F; iptables -F -t nat'
        test_util.test_logger("Flush iptables rules")
        port_checking_cmd = 'result=""; for port in `echo %s`; do echo "hello" | nc -w1 %s $port >/dev/null 2>&1; if [ $? -eq 0 ]; then result="${result}0";else result="${result}1"; (nohup nc -k -l %s $port >/dev/null 2>&1 </dev/null &); fi ; done; echo $result' % (target_ports, target_ip, target_ip)
    else:
        flush_iptables_cmd = 'ip6tables -F; ip6tables -F -t nat'
        test_util.test_logger("Flush ip6tables rules")
        port_checking_cmd = 'result=""; for port in `echo %s`; do echo "hello" | nc -w1 %s $port >/dev/null 2>&1; if [ $? -eq 0 ]; then result="${result}0";else result="${result}1"; (nohup nc -k -l %s $port >/dev/null 2>&1 </dev/null &); fi ; done; echo $result' % (target_ports, target_ipv6, target_ipv6)
    test_result = lib_execute_command_in_vm(vm, flush_iptables_cmd, ipv6 = target_ipv6)

#    target_ports = ' '.join(str(port) for port in ports)

    test_util.test_logger("Doing opening vm port operations, might need 1 min")
    test_result = lib_execute_command_in_vm(vm, port_checking_cmd, ipv6 = target_ipv6)
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
    cmd = 'echo "quit" | telnet %s %s|grep "Escape character"' % (target_ip, port)
    #cmd = 'echo "hello"|nc -w 1 %s %s' % (target_ip, port)
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

def lib_check_vm_ports_in_a_command(src_vm, dst_vm, allowed_ports, denied_ports, target_ipv6 = None):
    '''
    Check VM a group of ports connectibility within 1 ssh command.
    1 means connection refused. 0 means connection success. 
    '''
    common_l3 = lib_find_vms_same_l3_uuid([src_vm, dst_vm])
    if target_ipv6:
        target_ip = target_ipv6
    else:
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
#    test_result = lib_execute_command_in_vm(src_vm, port_checking_cmd, l3_uuid)
    username = lib_get_vm_username(src_vm)
    password = lib_get_vm_password(src_vm)
    if lib_is_vm_vr(src_vm):
        src_vm_ip = lib_find_vr_mgmt_ip(src_vm)
    else:
        if not l3_uuid:
            src_vm_ip = src_vm.vmNics[0].ip
        else:
            src_vm_ip = lib_get_vm_nic_by_l3(src_vm, l3_uuid).ip
    test_util.test_logger("Do testing to ssh vm: %s, ip: %s, execute cmd: %s" % (src_vm.uuid, src_vm_ip, port_checking_cmd))
    test_result = lib_execute_ssh_cmd(src_vm_ip, username, password, port_checking_cmd, 240)

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

def lib_gen_sg_rule(port, protocol, type, addr, ipVersion = None):
    '''
    will return a rule object by giving parameters
    port: rule key, like Port.rule1_ports
    '''
    startPort, endPort = Port.get_start_end_ports(port)
    rule = inventory.SecurityGroupRuleAO()
    rule.endPort = endPort
    rule.startPort = startPort
    if ipVersion == 6:
        rule.ipVersion = ipVersion
        rule.allowedCidr = '%s/64' % addr
    else:
        rule.allowedCidr = '%s/32' % addr
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


    if vr.applianceVmType == 'vrouter' or vr.applianceVmType == 'vpcvrouter':
        check_string3 = '--dports %s:%s' % (pf_rule.vipPortStart, pf_rule.vipPortEnd)
        check_cmd = "sudo iptables-save| grep -Fe '%s'|grep -Fe '%s'|grep -Fe '%s'" % (check_string1, check_string2, check_string3)
    else:
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
            if os.environ.get('ZSTACK_SIMULATOR') != "yes":
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

def lib_get_vip_by_ip(ip):
    conditions = res_ops.gen_query_conditions('ip', '=', ip)
    vip = res_ops.query_resource(res_ops.VIP, conditions)
    return vip[0]

def lib_get_eip_by_uuid(eip_uuid):
    conditions = res_ops.gen_query_conditions('uuid', '=', eip_uuid)
    eip = res_ops.query_resource(res_ops.EIP, conditions)
    return eip[0]

#----------- Robot Library -------------
def lib_robot_cleanup(test_dict):
    for vm in test_dict.get_vm_list(vm_header.RUNNING):
        vm.clean()
        test_dict.mv_volumes(vm.vm.uuid, test_stage.free_volume)
    for vm in test_dict.get_vm_list(vm_header.STOPPED):
        vm.clean()
        test_dict.mv_volumes(vm.vm.uuid, test_stage.free_volume)
    for vm in test_dict.get_vm_list(vm_header.DESTROYED):
        vm.clean()
    for vl in test_dict.get_volume_list():
        vl.clean()
    for img in test_dict.get_image_list():
        img.clean()
    for img in test_dict.get_image_list(test_stage.deleted_image):
        img.clean()

    sg_vm = test_dict.get_sg_vm()
    for vm in sg_vm.get_all_stub_vm():
        if vm:
            vm.clean()
    for sg in sg_vm.get_all_sgs():
        sg_vm.delete_sg(sg)

    #Depricated
    #for sg_uuid in test_dict.get_sg_list():
    #    lib_delete_security_group(sg_uuid)
    for vip in test_dict.get_all_vip_list():
        vip.delete()

    for sp in test_dict.get_all_available_snapshots():
        sp.delete()

    for vm in test_dict.get_all_utility_vm():
        vm.clean()

    for account in test_dict.get_all_accounts():
        account.delete()

    for instance_offering in test_dict.get_all_instance_offerings():
        vm_ops.delete_instance_offering(instance_offering.uuid)

    for disk_offering in test_dict.get_all_disk_offerings():
        vol_ops.delete_disk_offering(disk_offering.uuid)

def lib_error_cleanup(test_dict):
    test_util.test_logger('- - - Error cleanup: running VM - - -')
    for vm in test_dict.get_vm_list(vm_header.RUNNING):
        try:
            vm.clean()
        except:
            pass

    test_util.test_logger('- - - Error cleanup: stopped VM - - -')
    for vm in test_dict.get_vm_list(vm_header.STOPPED):
        try:
            vm.clean()
        except:
            pass

    test_util.test_logger('- - - Error cleanup: destroyed VM - - -')
    for vm in test_dict.get_vm_list(vm_header.DESTROYED):
        try:
            vm.clean()
        except:
            pass

    test_util.test_logger('- - - Error cleanup: Delete ECS Instance - - -')
    if test_dict.hybrid_obj and test_dict.hybrid_obj.ecs_instance:
        try:
            test_dict.hybrid_obj.del_ecs_instance()
        except:
            pass

    test_util.test_logger('- - - Error cleanup: volume - - -')
    for vl in test_dict.get_all_volume_list():
        try:
            vl.clean()
        except:
            pass

    test_util.test_logger('- - - Error cleanup: image - - -')
    for img in test_dict.get_image_list():
        try:
            img.clean()
        except:
            pass

    for img in test_dict.get_image_list(test_stage.deleted_image):
        try:
            img.clean()
        except:
            pass

    test_util.test_logger('- - - Error cleanup: SG stub_vm - - -')
    sg_vm = test_dict.get_sg_vm()
    for vm in sg_vm.get_all_stub_vm():
        if vm:
            try:
                vm.clean()
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
    for sp in test_dict.get_all_available_snapshots():
        try:
            sp.delete()
        except:
            pass

    test_util.test_logger('- - - Error cleanup: utiltiy vm - - -')
    for vm in test_dict.get_all_utility_vm():
        try:
            vm.clean()
        except:
            pass

    test_util.test_logger('- - - Error cleanup: accounts - - -')
    for account in test_dict.get_all_accounts():
        try:
            account.delete()
        except:
            pass

    test_util.test_logger('- - - Error cleanup: instance offerings- - -')
    for instance_offering in test_dict.get_all_instance_offerings():
        try:
            vm_ops.delete_instance_offering(instance_offering.uuid)
        except:
            pass

    test_util.test_logger('- - - Error cleanup: disk offerings- - -')
    for disk_offering in test_dict.get_all_disk_offerings():
        try:
            vol_ops.delete_disk_offering(disk_offering.uuid)
        except:
            pass

def lib_robot_status_check(test_dict):
    test_util.test_logger("- - - Robot check skip - - -" )
    return
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
    volume_snapshots = test_dict.get_all_available_snapshots()
    for snapshots in volume_snapshots:
        snapshots.check()

    test_util.test_logger("- - - Robot check pass - - -" )

def lib_vm_random_operation(robot_test_obj):
    '''
        Random operations for robot testing
    '''

    for resource_uuid in dict(robot_test_obj.get_resource_action_history().items()+{None:None}.items()):
        test_dict = robot_test_obj.get_test_dict()
        print 'Try calculate possible path execution for resource %s' % resource_uuid
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
        candidate_resource_list = []
    
        #Firstly, choose a target VM state for operation. E.g. Running. 
        target_vm_list = None
        if resource_uuid != None:
            for candidate_vm in test_dict.get_all_vm_list():
                if candidate_vm.get_vm().uuid == resource_uuid:
                    target_vm_list = [ candidate_vm ]
                    target_vm_state = lib_get_vm_by_uuid(candidate_vm.get_vm().uuid).state
                    break
                for vm_volume in test_dict.get_volume_list(candidate_vm.get_vm().uuid):
                    if vm_volume.get_volume().uuid == resource_uuid:
                        target_vm_list = [ candidate_vm ]
                        target_vm_state = lib_get_vm_by_uuid(candidate_vm.get_vm().uuid).state
                        break
                if target_vm_list != None:
                    break

        if target_vm_list == None:
            if test_dict.get_vm_list(vm_header.STOPPED):
                if test_dict.get_vm_list(vm_header.DESTROYED):
                    target_vm_state = random.choice([vm_header.RUNNING, \
                            vm_header.STOPPED, vm_header.DESTROYED])
                else:
                    target_vm_state = random.choice([vm_header.RUNNING, \
                            vm_header.STOPPED])
            else:
                if test_dict.get_vm_list(vm_header.DESTROYED):
                    target_vm_state = random.choice([vm_header.RUNNING, \
                            vm_header.DESTROYED])
                else:
                    target_vm_state = vm_header.RUNNING 
        
            #Secondly, choose a target VM from target status. 
            target_vm_list = test_dict.get_vm_list(target_vm_state)
        if target_vm_list:
            target_vm = random.choice(target_vm_list)
    
            # vm state in db may become inconsistent due to VM may become paused for a short period and vm sync to ZStack
            retry_count = 0
            while retry_count < 120:
                vm = lib_get_vm_by_uuid(target_vm.get_vm().uuid)
                #vm state in db
                vm_current_state = vm.state
                if target_vm_state == vm_current_state:
                    break
                test_util.test_logger('[retry:] %s [vm:] %s current [state:] %s is not aligned with random test record [state:] \
    %s .' % (retry_count, target_vm.get_vm().uuid, vm_current_state, target_vm_state))
                time.sleep(2)
                retry_count += 1
            if target_vm_state != vm_current_state:
                test_util.test_fail('\
    [vm:] %s current [state:] %s is not aligned with random test record [state:] \
    %s .' % (target_vm.get_vm().uuid, vm_current_state, target_vm_state))
        
            test_stage_obj.set_vm_state(vm_current_state)
    
            test_util.test_logger('target vm is : %s' % target_vm.get_vm().uuid)
            test_util.test_logger('target test obj: %s' % test_dict)
            candidate_resource_list += [ target_vm.get_vm().uuid ]
    
            host_inv = lib_find_host_by_vm(vm)
            if host_inv:
                bs = lib_get_backup_storage_list_by_vm(vm)[0]
                
                if lib_check_live_snapshot_cap(host_inv) and bs.type == inventory.IMAGE_STORE_BACKUP_STORAGE_TYPE:
                    test_stage_obj.set_vm_live_template_cap(test_stage.template_live_creation)
                else:
                    test_stage_obj.set_vm_live_template_cap(test_stage.template_no_live_creation)
    
            #Thirdly, check VM's volume status. E.g. if could add a new volume.
            vm_volumes = test_dict.get_volume_list(target_vm.get_vm().uuid)
            if vm_volumes:
                vm_volume_number = len(vm_volumes)
            else:
    	        vm_volume_number = 0
    
            if vm_volume_number > 0 and vm_volume_number < 24:
                test_stage_obj.set_vm_volume_state(test_stage.vm_volume_att_not_full)
                attached_volume = random.choice(vm_volumes)
            elif vm_volume_number == 0:
                test_stage_obj.set_vm_volume_state(test_stage.vm_no_volume_att)
            else:
                test_stage_obj.set_vm_volume_state(test_stage.vm_volume_att_full)
                attached_volume = random.choice(vm_volumes)
        
            if lib_check_vm_live_migration_cap(vm):
                test_stage_obj.set_vm_live_migration_cap(test_stage.vm_live_migration)
            else:
                test_stage_obj.set_vm_live_migration_cap(test_stage.no_vm_live_migration)
        else:
            test_stage_obj.set_vm_state(test_stage.Any)
            test_stage_obj.set_vm_volume_state(test_stage.Any)
            test_stage_obj.set_vm_live_migration_cap(test_stage.Any)
    
        #Fourthly, choose a available volume for possibly attach or delete
        avail_volumes = None
        if resource_uuid != None:
            for candidate_volume in test_dict.get_all_volume_list():
                if candidate_volume.get_volume().uuid == resource_uuid:
                    avail_volumes = [ candidate_volume ]
                    break
        if avail_volumes == None:
            avail_volumes = list(test_dict.get_volume_list(test_stage.free_volume))
            avail_volumes.extend(test_dict.get_volume_list(test_stage.deleted_volume))
        if avail_volumes:
            ready_volume = random.choice(avail_volumes)
            if ready_volume.get_state() != vol_header.DELETED:
                test_stage_obj.set_volume_state(test_stage.free_volume)
                candidate_resource_list += [ ready_volume.get_volume().uuid ]
            else:
                test_stage_obj.set_volume_state(test_stage.deleted_volume)
        else:
            test_stage_obj.set_volume_state(test_stage.no_free_volume)
    
        #Fifthly, choose a volume for possible snasphot operation 
        all_volume_snapshots = None
        if resource_uuid != None:
            for candidate_snapshots in test_dict.get_all_available_snapshots():
                for candidate_snapshot in candidate_snapshots.get_primary_snapshots():
                    if candidate_snapshot.get_snapshot().uuid == resource_uuid:
                        all_volume_snapshots = [ candidate_snapshots ]
                        break
        target_volume_snapshots = None
        if all_volume_snapshots == None:
            all_volume_snapshots = test_dict.get_all_available_snapshots()
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
                # or we assume its hypervisor support live snapshot creation
                if snapshot_volume_obj.get_state() != vol_header.ATTACHED:
                    test_stage_obj.set_snapshot_live_cap(test_stage.snapshot_live_creation)
                    test_stage_obj.set_volume_vm_state(vm_header.STOPPED)
                elif snapshot_volume_obj.get_target_vm().get_state() == vm_header.DESTROYED:
                    test_stage_obj.set_snapshot_live_cap(test_stage.Any)
                    test_stage_obj.set_volume_vm_state(vm_header.DESTROYED)
                else:
                    volume_vm = snapshot_volume_obj.get_target_vm()
                    test_stage_obj.set_volume_vm_state(volume_vm.get_state())
                    target_vm_inv = volume_vm.get_vm()
                    host_inv = lib_find_host_by_vm(target_vm_inv)
                    if host_inv:
                        if lib_check_live_snapshot_cap(host_inv):
                            test_stage_obj.set_snapshot_live_cap(test_stage.snapshot_live_creation)
                        else:
                            test_stage_obj.set_snapshot_live_cap(test_stage.snapshot_no_live_creation)
    
                #random pick up an available snapshot. Firstly choose from primary snapshot.
                target_snapshot = None
    
                #If volume is expunged, there isn't snapshot in primary storage 
                if target_volume_snapshots.get_primary_snapshots() \
                        and snapshot_volume_obj.get_state() != vol_header.DELETED\
                        and snapshot_volume_obj.get_state() != vol_header.EXPUNGED:
                    if resource_uuid != None:
                        for candidate_snapshot in candidate_snapshots.get_primary_snapshots():
                            if candidate_snapshot.get_snapshot().uuid == resource_uuid:
                                target_snapshot = candidate_snapshot
                                break
                    if target_snapshot == None:
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
        if target_snapshot:
            if target_snapshot.get_target_volume().get_state() == vol_header.DELETED or target_snapshot.get_target_volume().get_state() == vol_header.EXPUNGED:
                test_stage_obj.set_snapshot_state(test_stage.no_volume_file)
            candidate_resource_list += [ target_snapshot.get_snapshot().uuid ]
        if target_volume_snapshots:
            if target_volume_snapshots.get_target_volume().get_state() == vol_header.DELETED or target_volume_snapshots.get_target_volume().get_state() == vol_header.EXPUNGED:
                test_stage_obj.set_snapshot_state(test_stage.no_volume_file)


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
        avail_images = list(test_dict.get_image_list(test_stage.new_template_image))
        avail_images.extend(test_dict.get_image_list(test_stage.deleted_image))
        if avail_images:
            target_image = random.choice(avail_images)
            if target_image.get_state() != image_header.DELETED:
                test_stage_obj.set_image_state(test_stage.new_template_image)
            else:
                test_stage_obj.set_image_state(test_stage.deleted_image)
            candidate_resource_list += [ target_image.get_image().uuid ]
        else:
            test_stage_obj.set_image_state(test_stage.Any)
    
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
        if avail_images and target_image != None and target_image.get_image().mediaType == 'RootVolumeTemplate':
            if excluded_actions_list == None:
                excluded_actions_list2 = [TestAction.create_data_volume_from_image]
            else:
                excluded_actions_list2 = excluded_actions_list + [TestAction.create_data_volume_from_image]
            action_list = ts_header.generate_action_list(test_stage_obj, \
                    excluded_actions_list2)
        else:
            action_list = ts_header.generate_action_list(test_stage_obj, \
                    excluded_actions_list)
    
        test_util.test_logger('action list: %s' % action_list)
    
        # Currently is randomly picking up.
        (next_action, path_execution) = lib_robot_pickup_action(robot_test_obj.get_required_path_list(), candidate_resource_list, action_list, \
                robot_test_obj.get_action_history(), robot_test_obj.get_resource_action_history(), priority_actions, random_type)
        if resource_uuid != None and not path_execution:
            continue
        robot_test_obj.add_action_history(next_action)

    if next_action == TestAction.create_vm:
        test_util.test_dsc('Robot Action: %s ' % next_action)
        new_vm = lib_create_vm(cre_vm_opt)
        robot_test_obj.add_resource_action_history(new_vm.get_vm().uuid, next_action)
        test_dict.add_vm(new_vm)

        test_util.test_dsc('Robot Action Result: %s; new VM: %s' % \
            (next_action, new_vm.get_vm().uuid))

        test_dict.create_empty_volume_list(new_vm.vm.uuid)

    elif next_action == TestAction.stop_vm:
        test_util.test_dsc('Robot Action: %s; on VM: %s' \
                % (next_action, target_vm.get_vm().uuid))
        robot_test_obj.add_resource_action_history(target_vm.get_vm().uuid, next_action)

        target_vm.stop()
        test_dict.mv_vm(target_vm, vm_header.RUNNING, vm_header.STOPPED)

    elif next_action == TestAction.start_vm :
        test_util.test_dsc('Robot Action: %s; on VM: %s' \
                % (next_action, target_vm.get_vm().uuid))
        robot_test_obj.add_resource_action_history(target_vm.get_vm().uuid, next_action)

        target_vm.start()
        test_dict.mv_vm(target_vm, vm_header.STOPPED, vm_header.RUNNING)

    elif next_action == TestAction.reboot_vm :
        test_util.test_dsc('Robot Action: %s; on VM: %s' \
                % (next_action, target_vm.get_vm().uuid))
        robot_test_obj.add_resource_action_history(target_vm.get_vm().uuid, next_action)

        target_vm.reboot()

    elif next_action == TestAction.destroy_vm :
        test_util.test_dsc('Robot Action: %s; on VM: %s' \
                % (next_action, target_vm.get_vm().uuid))
        robot_test_obj.add_resource_action_history(target_vm.get_vm().uuid, next_action)
        target_vm.destroy()
        test_dict.rm_vm(target_vm, vm_current_state)

    elif next_action == TestAction.expunge_vm :
        test_util.test_dsc('Robot Action: %s; on VM: %s' \
                % (next_action, target_vm.get_vm().uuid))
        robot_test_obj.add_resource_action_history(target_vm.get_vm().uuid, next_action)
        target_vm.expunge()
        test_dict.rm_vm(target_vm, vm_current_state)

    elif next_action == TestAction.migrate_vm :
        test_util.test_dsc('Robot Action: %s; on VM: %s' \
                % (next_action, target_vm.get_vm().uuid))
        robot_test_obj.add_resource_action_history(target_vm.get_vm().uuid, next_action)
        target_host = lib_find_random_host(target_vm.vm)
        if not target_host:
            test_util.test_logger('no avaiable host was found for doing vm migration')
        else:
            target_vm.migrate(target_host.uuid)

    elif next_action == TestAction.create_volume :
        test_util.test_dsc('Robot Action: %s ' % next_action)
        new_volume = lib_create_volume_from_offering()
        robot_test_obj.add_resource_action_history(new_volume.get_volume().uuid, next_action)
        test_dict.add_volume(new_volume)

        test_util.test_dsc('Robot Action Result: %s; new Volume: %s' % \
            (next_action, new_volume.get_volume().uuid))

    elif next_action == TestAction.create_scsi_volume :
        test_util.test_dsc('Robot Action: %s ' % next_action)
        volume_option = test_util.VolumeOption()
        volume_option.set_system_tags(["capability::virtio-scsi"])
        new_volume = lib_create_volume_from_offering(volume_option)
        robot_test_obj.add_resource_action_history(new_volume.get_volume().uuid, next_action)
        test_dict.add_volume(new_volume)

        test_util.test_dsc('Robot Action Result: %s; new Volume: %s' % \
            (next_action, new_volume.get_volume().uuid))

    elif next_action == TestAction.attach_volume :
        test_util.test_dsc('Robot Action: %s; on Volume: %s; on VM: %s' % \
            (next_action, ready_volume.get_volume().uuid, \
            target_vm.get_vm().uuid))

        root_volume = lib_get_root_volume(target_vm.get_vm())
        ps = lib_get_primary_storage_by_uuid(root_volume.primaryStorageUuid)
        if not lib_check_vm_live_migration_cap(target_vm.vm) or ps.type == inventory.LOCAL_STORAGE_TYPE:
            ls_ref = lib_get_local_storage_reference_information(ready_volume.get_volume().uuid)
            if ls_ref:
                volume_host_uuid = ls_ref[0].hostUuid
                vm_host_uuid = lib_get_vm_host(target_vm.vm).uuid
                if vm_host_uuid and volume_host_uuid != vm_host_uuid:
                    test_util.test_logger('need to migrate volume: %s to host: %s, before attach it to vm: %s' % (ready_volume.get_volume().uuid, vm_host_uuid, target_vm.vm.uuid))
                    ready_volume.migrate(vm_host_uuid)

        robot_test_obj.add_resource_action_history(ready_volume.get_volume().uuid, next_action)
        robot_test_obj.add_resource_action_history(target_vm.get_vm().uuid, next_action)
        ready_volume.attach(target_vm)
        test_dict.mv_volume(ready_volume, test_stage.free_volume, target_vm.vm.uuid)

    elif next_action == TestAction.detach_volume:
        test_util.test_dsc('Robot Action: %s; on Volume: %s' % \
            (next_action, attached_volume.get_volume().uuid))
        robot_test_obj.add_resource_action_history(attached_volume.get_volume().uuid, next_action)
        robot_test_obj.add_resource_action_history(target_vm.get_vm().uuid, next_action)

        attached_volume.detach()
        test_dict.mv_volume(attached_volume, target_vm.vm.uuid, test_stage.free_volume)

    elif next_action == TestAction.delete_volume:
        #if there is no free volume, but action is delete_volume. It means the 
        # the target volume is attached volume.
        if not ready_volume:
            ready_volume = attached_volume
            robot_test_obj.add_resource_action_history(target_vm.get_vm().uuid, next_action)

        robot_test_obj.add_resource_action_history(ready_volume.get_volume().uuid, next_action)
        test_util.test_dsc('Robot Action: %s; on Volume: %s' % \
            (next_action, ready_volume.get_volume().uuid))
        ready_volume.delete()
        test_dict.rm_volume(ready_volume)

    elif next_action == TestAction.expunge_volume:
        test_util.test_dsc('Robot Action: %s; on Volume: %s' % \
            (next_action, ready_volume.get_volume().uuid))
        robot_test_obj.add_resource_action_history(ready_volume.get_volume().uuid, next_action)
        ready_volume.expunge()
        test_dict.rm_volume(ready_volume)

    elif next_action == TestAction.migrate_volume :
        #TODO: add normal initialized data volume into migration target.
        root_volume_uuid = lib_get_root_volume(target_vm.get_vm()).uuid
        robot_test_obj.add_resource_action_history(root_volume_uuid, next_action)
        robot_test_obj.add_resource_action_history(target_vm.get_vm().uuid, next_action)
        test_util.test_dsc('Robot Action: %s; on Volume: %s; on VM: %s' \
                % (next_action, root_volume_uuid, target_vm.get_vm().uuid))
        target_host = lib_find_random_host_by_volume_uuid(root_volume_uuid)
        if not target_host:
            test_util.test_logger('no avaiable host was found for doing vm migration')
        else:
            import zstackwoodpecker.operations.volume_operations as vol_ops
            vol_ops.migrate_volume(root_volume_uuid, target_host.uuid)

    elif next_action == TestAction.idel :
        test_util.test_dsc('Robot Action: %s ' % next_action)
        lib_vm_random_idel_time(1, 5)

    elif next_action == TestAction.create_image_from_volume:
        root_volume_uuid = lib_get_root_volume(target_vm.vm).uuid

        test_util.test_dsc('Robot Action: %s; on Volume: %s; on VM: %s' % \
            (next_action, root_volume_uuid, target_vm.get_vm().uuid))
        robot_test_obj.add_resource_action_history(root_volume_uuid, next_action)

        new_image = lib_create_template_from_volume(root_volume_uuid)
        test_util.test_dsc('Robot Action Result: %s; new RootVolume Image: %s'\
                % (next_action, new_image.get_image().uuid))
        robot_test_obj.add_resource_action_history(new_image.get_image().uuid, next_action)
        test_dict.add_image(new_image)

    elif next_action == TestAction.create_data_vol_template_from_volume:
        vm_volumes = target_vm.get_vm().allVolumes
        vm_target_vol_candidates = []
        for vm_volume in vm_volumes:
            if vm_volume.status != 'Deleted':
                vm_target_vol_candidates.append(vm_volume)
        vm_target_vol = random.choice(vm_target_vol_candidates)
        test_util.test_dsc('Robot Action: %s; on Volume: %s; on VM: %s' % \
            (next_action, vm_target_vol.uuid, target_vm.get_vm().uuid))
        robot_test_obj.add_resource_action_history(vm_target_vol.uuid, next_action)
        robot_test_obj.add_resource_action_history(target_vm.get_vm().uuid, next_action)
        new_data_vol_temp = lib_create_data_vol_template_from_volume(target_vm, vm_target_vol)
        test_util.test_dsc('Robot Action Result: %s; new DataVolume Image: %s' \
                % (next_action, new_data_vol_temp.get_image().uuid))
        robot_test_obj.add_resource_action_history(new_data_vol_temp.get_image().uuid, next_action)
        test_dict.add_image(new_data_vol_temp)

    elif next_action == TestAction.create_data_volume_from_image:
        test_util.test_dsc('Robot Action: %s; on Image: %s' % \
            (next_action, target_image.get_image().uuid))

        robot_test_obj.add_resource_action_history(target_image.get_image().uuid, next_action)
        new_volume = lib_create_data_volume_from_image(target_image)
        robot_test_obj.add_resource_action_history(new_volume.get_volume().uuid, next_action)

        test_util.test_dsc('Robot Action Result: %s; new Volume: %s' % \
            (next_action, new_volume.get_volume().uuid))
        test_dict.add_volume(new_volume)

    elif next_action == TestAction.delete_image:
        test_util.test_dsc('Robot Action: %s; on Image: %s' % \
            (next_action, target_image.get_image().uuid))
        robot_test_obj.add_resource_action_history(target_image.get_image().uuid, next_action)

        target_image.delete()
        test_dict.rm_image(target_image)
        #image will be move to deleted state when call rm_image
        #test_dict.add_image(target_image, test_stage.deleted_image)

    elif next_action == TestAction.expunge_image:
        test_util.test_dsc('Robot Action: %s; on Image: %s' % \
            (next_action, target_image.get_image().uuid))
        robot_test_obj.add_resource_action_history(target_image.get_image().uuid, next_action)

        bss = target_image.get_image().backupStorageRefs
        bs_uuid_list = []
        for bs in bss:
            bs_uuid_list.append(bs.backupStorageUuid)
        target_image.expunge(bs_uuid_list)
        test_dict.rm_image(target_image)

    elif next_action == TestAction.create_sg:
        test_util.test_dsc('Robot Action: %s ' % next_action)
        sg_vm = test_dict.get_sg_vm()
        sg_creation_option = test_util.SecurityGroupOption()
        sg_creation_option.set_name('robot security group')
        new_sg = sg_vm.create_sg(sg_creation_option)
        robot_test_obj.add_resource_action_history(new_sg.get_security_group().uuid, next_action)
        test_util.test_dsc(\
            'Robot Action Result: %s; new SG: %s' % \
            (next_action, new_sg.get_security_group().uuid))

    elif next_action == TestAction.delete_sg:
        sg_vm = test_dict.get_sg_vm()
        target_sg = random.choice(sg_vm.get_all_sgs())
        test_util.test_dsc(\
            'Robot Action: %s; on SG: %s' % \
            (next_action, target_sg.get_security_group().uuid))
        robot_test_obj.add_resource_action_history(target_sg.get_security_group().uuid, next_action)

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
            robot_test_obj.add_resource_action_history(target_volume_inv.uuid, next_action)
            robot_test_obj.add_resource_action_history(target_volume_inv.vmInstanceUuid, next_action)
        else:
            test_util.test_dsc('Robot Action: %s; on Volume: %s' % \
                   (next_action, \
                    target_volume_inv.uuid))
            robot_test_obj.add_resource_action_history(target_volume_inv.uuid, next_action)

        new_snapshot = lib_create_volume_snapshot_from_volume(target_volume_snapshots, robot_test_obj, test_dict, cre_vm_opt)
        robot_test_obj.add_resource_action_history(new_snapshot.get_snapshot().uuid, next_action)

        test_util.test_dsc('Robot Action Result: %s; new SP: %s' % \
            (next_action, new_snapshot.get_snapshot().uuid))

    elif next_action == TestAction.delete_volume_snapshot:
        target_volume_snapshots.delete_snapshot(target_snapshot)
        test_util.test_dsc('Robot Action: %s; on Volume: %s; on SP: %s' % \
            (next_action, \
            target_volume_snapshots.get_target_volume().get_volume().uuid, \
            target_snapshot.get_snapshot().uuid))

        robot_test_obj.add_resource_action_history(target_snapshot.get_snapshot().uuid, next_action)
        robot_test_obj.add_resource_action_history(target_volume_snapshots.get_target_volume().get_volume().uuid, next_action)
        #If both volume and snapshots are deleted, volume_snapshot obj could be 
        # removed.
        if not target_volume_snapshots.get_backuped_snapshots():
            target_volume_obj = target_volume_snapshots.get_target_volume()
            if target_volume_obj.get_state() == vol_header.EXPUNGED \
                    or (target_volume_snapshots.get_volume_type() == \
                        vol_header.ROOT_VOLUME \
                        and target_volume_obj.get_target_vm().get_state() == \
                            vm_header.EXPUNGED):
                test_dict.rm_volume_snapshot(target_volume_snapshots)
    elif next_action == TestAction.batch_delete_volume_snapshot:
        target_volume_snapshots = None
        target_snapshot = None
        target_snapshot_name = None
        target_snapshot_uuid_list = []
        target_snapshot_list = []

        all_volume_snapshots = test_dict.get_all_available_snapshots()
        import zstackwoodpecker.operations.volume_operations as vol_ops
        for snapshot_name in constant_path_list[0][1]:
            cond = res_ops.gen_query_conditions('name','=',snapshot_name)
            target_snapshot = res_ops.query_resource(res_ops.VOLUME_SNAPSHOT, cond)
            if not target_snapshot:
                test_util.test_logger("Can not find target snapshot: %s" % snapshot_name)
            else:
                target_snapshot_uuid_list.append(target_snapshot[0].uuid)
                for candidate_snapshots in all_volume_snapshots:
                    for candidate_snapshot in candidate_snapshots.get_primary_snapshots():
                        if candidate_snapshot.get_snapshot().name == snapshot_name:
                            target_volume_snapshots = candidate_snapshots
                            target_snapshot_list.append(candidate_snapshot)
                            break
        target_volume_snapshots.delete_snapshots_dict_record(target_snapshot_list)
        vol_ops.batch_delete_snapshot(target_snapshot_uuid_list)

    elif next_action == TestAction.use_volume_snapshot:
        test_util.test_dsc('Robot Action: %s; on Volume: %s; on SP: %s' % \
            (next_action, \
            target_volume_snapshots.get_target_volume().get_volume().uuid, \
            target_snapshot.get_snapshot().uuid))
        robot_test_obj.add_resource_action_history(target_snapshot.get_snapshot().uuid, next_action)
        robot_test_obj.add_resource_action_history(target_volume_snapshots.get_target_volume().get_volume().uuid, next_action)

        target_volume_snapshots.use_snapshot(target_snapshot)

    elif next_action == TestAction.backup_volume_snapshot:
        test_util.test_dsc("Skip backup snapshot currently for debugging as this operation is"
                           "not exposed to users")
        #test_util.test_dsc('Robot Action: %s; on Volume: %s; on SP: %s' % \
        #    (next_action, \
        #    target_volume_snapshots.get_target_volume().get_volume().uuid, \
        #    target_snapshot.get_snapshot().uuid))

        #target_volume_snapshots.backup_snapshot(target_snapshot)

    elif next_action == TestAction.delete_backup_volume_snapshot:
        test_util.test_dsc("Skip backup snapshot currently for debugging as this operation is"
                           "not exposed to users")
        #test_util.test_dsc('Robot Action: %s; on Volume: %s; on SP: %s' % \
        #    (next_action, \
        #    target_volume_snapshots.get_target_volume().get_volume().uuid, \
        #    target_snapshot.get_snapshot().uuid))
        #
        #target_volume_snapshots.delete_backuped_snapshot(target_snapshot)

        #Both volume and snapshots are deleted, volume_snapshot obj could be 
        # removed.
        #if not target_volume_snapshots.get_backuped_snapshots():
        #    target_volume_obj = target_volume_snapshots.get_target_volume()
        #    if target_volume_obj.get_state() == vol_header.EXPUNGED \
        #            or (target_volume_snapshots.get_volume_type() == \
        #                vol_header.ROOT_VOLUME \
        #                and target_volume_obj.get_target_vm().get_state() == \
        #                    vm_header.EXPUNGED):
        #        test_dict.rm_volume_snapshot(target_volume_snapshots)

    elif next_action == TestAction.create_volume_from_snapshot:
        test_util.test_dsc('Robot Action: %s; on Volume: %s; on SP: %s' % \
            (next_action, \
            target_volume_snapshots.get_target_volume().get_volume().uuid, \
            target_snapshot.get_snapshot().uuid))
        robot_test_obj.add_resource_action_history(target_snapshot.get_snapshot().uuid, next_action)

        new_volume_obj = target_snapshot.create_data_volume()
        test_dict.add_volume(new_volume_obj)
        robot_test_obj.add_resource_action_history(new_volume_obj.get_volume().uuid, next_action)
        test_util.test_dsc('Robot Action Result: %s; new Volume: %s; on SP: %s'\
                % (next_action, new_volume_obj.get_volume().uuid,\
                target_snapshot.get_snapshot().uuid))

    elif next_action == TestAction.create_image_from_snapshot:
        test_util.test_dsc('Robot Action: %s; on Volume: %s; on SP: %s' % \
            (next_action, \
            target_volume_snapshots.get_target_volume().get_volume().uuid, \
            target_snapshot.get_snapshot().uuid))
        robot_test_obj.add_resource_action_history(target_snapshot.get_snapshot().uuid, next_action)

        new_image_obj = lib_create_image_from_snapshot(target_snapshot)
        robot_test_obj.add_resource_action_history(new_image_obj.get_image().uuid, next_action)

        test_dict.add_image(new_image_obj)
        test_util.test_dsc('Robot Action Result: %s; new Image: %s; on SP: %s'\
                % (next_action, new_image_obj.get_image().uuid,\
                target_snapshot.get_snapshot().uuid))

    required_path = robot_test_obj.get_required_path_list()
    resource_action_history = robot_test_obj.get_resource_action_history()
    for key in resource_action_history:
        if lib_evaluate_path_execution(required_path, resource_action_history[key]) == len(required_path):
            test_util.test_logger('Required path executed: %s' % required_path)
            robot_test_obj.set_required_path_list([])

    test_util.test_logger('Finsih action: %s execution' % next_action)

def lib_robot_update_configs(robot_test_obj, resource_type, resource):
    def _already_registered(uuid_dict, uuid):
        for key in uuid_dict:
            if uuid_dict[key] == uuid:
                return True
        return False

    for cd_key in robot_test_obj.configs_dict:
        for key in robot_test_obj.configs_dict[cd_key]:
            if robot_test_obj.configs_dict[cd_key][key] == None:
                if cd_key == "PS":
                    if resource_type == "VmInstance":
                        if not _already_registered(robot_test_obj.configs_dict[cd_key], resource.allVolumes[0].primaryStorageUuid):
                            robot_test_obj.configs_dict[cd_key][key] = resource.allVolumes[0].primaryStorageUuid
                    if resource_type == "Volume":
                        if not _already_registered(robot_test_obj.configs_dict[cd_key], resource.primaryStorageUuid):
                            robot_test_obj.configs_dict[cd_key][key] = resource.primaryStorageUuid
                if cd_key == "HOST":
                    if resource_type == "VmInstance":
                        if not _already_registered(robot_test_obj.configs_dict[cd_key], resource.hostUuid):
                            robot_test_obj.configs_dict[cd_key][key] = resource.hostUuid
          
def lib_robot_get_default_configs(robot_test_obj, resource_type):
    if robot_test_obj.configs_dict.has_key(resource_type):
        if not robot_test_obj.configs_dict[resource_type]:
            return None
        if not robot_test_obj.configs_dict[resource_type].has_key("default"):
            return None
        if not robot_test_obj.configs_dict[resource_type]["default"]:
            return None
        if not robot_test_obj.configs_dict[resource_type].has_key(robot_test_obj.configs_dict[resource_type]["default"]):
            return None
        return robot_test_obj.configs_dict[resource_type][robot_test_obj.configs_dict[resource_type]["default"]]
    return None

def lib_robot_import_resource_from_formation(robot_test_obj, resource_list):
    # import VM
    imported_resource = []
    test_dict = robot_test_obj.get_test_dict()
    for resource in resource_list:
        if resource.hasattr("VmInstance"):
            test_util.test_logger("debug VmInstance %s" % (resource["VmInstance"]["uuid"]))
            test_util.test_logger("debug VmInstance %s" % (resource["VmInstance"]["name"]))
            if resource["VmInstance"]["uuid"] in imported_resource:
                continue

            imported_resource.append(resource["VmInstance"]["uuid"])
            import zstackwoodpecker.zstack_test.zstack_test_vm as zstack_vm_header
            if resource["VmInstance"]["type"] == "ApplianceVm":
                continue
            new_vm = zstack_vm_header.ZstackTestVm()
            new_vm.create_from(resource["VmInstance"]["uuid"])
            # import Volume already attached
            volume_index = 1
            for volume in new_vm.get_vm().allVolumes:
                if volume.type != "Data":
                    continue
                if volume.uuid in imported_resource:
                    continue
                vol_ops.update_volume(volume.uuid, "%s-volume%s" % (resource["VmInstance"]["name"], volume_index),  None)
                imported_resource.append(volume.uuid)
                #import zstackwoodpecker.zstack_test.zstack_test_volume as zstack_volume_header
                #new_volume = zstack_volume_header.ZstackTestVolume()
                #new_volume.create_from(volume.uuid, new_vm)
                #test_dict.add_volume(new_volume)
                #test_dict.mv_volume_with_snapshots(new_volume, test_stage.free_volume, new_volume.get_volume().vmInstanceUuid)
                volume_index += 1
            new_vm.update()
            test_dict.add_vm(new_vm)
            lib_robot_update_configs(robot_test_obj, "VmInstance", new_vm.get_vm())

    # import Volume
    for resource in resource_list:
        if resource.hasattr("Volume"):
            test_util.test_logger("debug Volume list %s" % (resource["Volume"]["uuid"]))
            test_util.test_logger("debug Volume list %s" % (resource["Volume"]["name"]))
            if resource["Volume"]["uuid"] in imported_resource:
                continue

            imported_resource.append(resource["Volume"]["uuid"])
            import zstackwoodpecker.zstack_test.zstack_test_volume as zstack_volume_header
            new_volume = zstack_volume_header.ZstackTestVolume()
            new_volume.create_from(resource["Volume"]["uuid"])
            test_dict.add_volume(new_volume)
            if new_volume.get_volume().hasattr("vmInstanceUuid"):
                test_dict.mv_volume(new_volume, test_stage.free_volume, new_volume.get_volume().vmInstanceUuid)
            lib_robot_update_configs(robot_test_obj, "Volume", new_volume.get_volume())


    # import VIP

    # import EIP

    # import PF
    robot_test_obj.set_test_dict(test_dict)

def lib_robot_initial_formation_auto_parameter(robot_test_obj, template_uuid):
    if robot_test_obj.get_initial_formation_parameters():
        return

    import zstackwoodpecker.operations.stack_template as stack_template_ops
    import zstackwoodpecker.operations.resource_stack as resource_stack_ops
    para_invs = stack_template_ops.check_stack_template(template_uuid)
    instance_offering_dict = dict()
    image_dict = dict()
    pub_l3network_dict = dict()
    pri_l3network_dict = dict()
    disk_offering_dict = dict()
    for para_inv in para_invs.parameters:
        print para_inv
        if para_inv.resourceType == "InstanceOffering":
            if para_inv.paramName in instance_offering_dict:
                test_util.test_fail("duplicate parameter name found, should be a bug")
            cond = res_ops.gen_query_conditions('state', '=', 'Enabled')
            cond = res_ops.gen_query_conditions('type', '=', 'UserVm', cond)
            for paraname in instance_offering_dict:
                cond = res_ops.gen_query_conditions('uuid', '!=', instance_offering_dict[paraname], cond)
            instance_offerings = res_ops.query_resource(res_ops.INSTANCE_OFFERING, cond)  
            if not instance_offerings:
                test_util.test_fail("Not enough disinct resource for so many parameters")
            instance_offering_dict[para_inv.paramName] = instance_offerings[0].uuid
        elif para_inv.resourceType == "Image":
            if para_inv.paramName in image_dict:
                test_util.test_fail("duplicate parameter name found, should be a bug")

            cond = res_ops.gen_query_conditions('state', '=', 'Enabled')
            cond = res_ops.gen_query_conditions('status', '=', 'Ready', cond)
            if not image_dict:
                cond = res_ops.gen_query_conditions('name', '=', os.environ.get('imageName_net'), cond)
                images = res_ops.query_resource(res_ops.IMAGE, cond)
            else:
                for paraname in image_dict:
                    cond = res_ops.gen_query_conditions('uuid', '!=', image_dict[paraname], cond)
                images = res_ops.query_resource(res_ops.IMAGE, cond)
            if not images:
                test_util.test_fail("Not enough disinct resource for so many parameters")

            image_dict[para_inv.paramName] = images[0].uuid
        elif para_inv.resourceType == "L3Network":
            if "pub" in para_inv.paramName.lower():
                if para_inv.paramName in pub_l3network_dict:
                    test_util.test_fail("duplicate parameter name found, should be a bug")
                if not pub_l3network_dict:
                    public_l3 = lib_get_l3_by_name(os.environ.get('l3PublicNetworkName'))
                else:
                    test_util.test_fail("No more public l3")
                if not public_l3:
                    test_util.test_fail("Not enough disinct resource for so many parameters")

                pub_l3network_dict[para_inv.paramName] = public_l3.uuid
            else:
                if para_inv.paramName in pri_l3network_dict:
                    test_util.test_fail("duplicate parameter name found, should be a bug")
                
                public_l3 = lib_get_l3_by_name(os.environ.get('l3PublicNetworkName'))
                cond = res_ops.gen_query_conditions('state', '=', 'Enabled')
                cond = res_ops.gen_query_conditions('system', '=', 'false')
                cond = res_ops.gen_query_conditions('uuid', '!=', public_l3.uuid, cond)
                for paraname in pri_l3network_dict:
                    cond = res_ops.gen_query_conditions('uuid', '!=', pri_l3network_dict[paraname], cond)
                pri_l3s = res_ops.query_resource(res_ops.L3_NETWORK, cond)  
                if not pri_l3s:
                    test_util.test_fail("Not enough disinct resource for so many parameters")

                pri_l3network_dict[para_inv.paramName] = pri_l3s[0].uuid
        elif para_inv.resourceType == "DiskOffering":
            if para_inv.paramName in disk_offering_dict:
                test_util.test_fail("duplicate parameter name found, should be a bug")
 
            if not disk_offering_dict:
                cond = res_ops.gen_query_conditions('state', '=', 'Enabled')
                cond = res_ops.gen_query_conditions('name', '=', os.environ.get('smallDiskOfferingName'), cond)
	        disk_offerings = res_ops.query_resource(res_ops.DISK_OFFERING, cond)
            else:
                cond = res_ops.gen_query_conditions('state', '=', 'Enabled')
                for paraname in disk_offering_dict:
                    cond = res_ops.gen_query_conditions('uuid', '!=', disk_offering_dict[paraname], cond)
                disk_offerings = res_ops.query_resource(res_ops.DISK_OFFERING, cond)
            if not disk_offerings:
                test_util.test_fail("Not enough disinct resource for so many parameters")

            disk_offering_dict[para_inv.paramName] = disk_offerings[0].uuid
        all_dict = instance_offering_dict.copy()
        all_dict.update(image_dict)
        all_dict.update(pub_l3network_dict)
        all_dict.update(pri_l3network_dict)
        all_dict.update(disk_offering_dict)
        robot_test_obj.set_initial_formation_parameters(str(all_dict).replace("u'", "'"))

def lib_robot_create_utility_vm(robot_test_obj):
    '''
        Create utility vm for all ps for robot testing
    '''
    cond = res_ops.gen_query_conditions('state', '=', "Enabled")
    cond = res_ops.gen_query_conditions('status', '=', "Connected", cond)
    pss = res_ops.query_resource(res_ops.PRIMARY_STORAGE, cond)
    for ps in pss:
        utility_vm = None
        cond = res_ops.gen_query_conditions('name', '=', "utility_vm_for_robot_test")
        cond = res_ops.gen_query_conditions('state', '=', "Running", cond)
        vms = res_ops.query_resource(res_ops.VM_INSTANCE, cond)
        for vm in vms:
            ps_uuid = lib_get_root_volume(vm).primaryStorageUuid
            if ps_uuid == ps.uuid:
                utility_vm = vm
        if not utility_vm:
            utility_vm_image = None
            vm_create_option = test_util.VmOption()
            bs_uuids = lib_get_backup_storage_uuid_list_by_zone(ps.zoneUuid)
            cond = res_ops.gen_query_conditions('name', '=', 'image_for_robot_test')
            cond = res_ops.gen_query_conditions('state', '=', "Enabled", cond)
            cond = res_ops.gen_query_conditions('status', '=', "Ready", cond)
            images = res_ops.query_resource(res_ops.IMAGE, cond)
            for bs_uuid in bs_uuids:
                temp_list = lib_get_primary_storage_uuid_list_by_backup_storage(bs_uuid)
                if ps.uuid not in temp_list:
                    continue
                for image in images:
                    for bs_ref in image.backupStorageRefs:
                        if bs_ref.backupStorageUuid == bs_uuid:
                            utility_vm_image = image
                            break
            if not utility_vm_image:
                cond = res_ops.gen_query_conditions('name', '=', os.environ.get('imageName_net'))
                cond = res_ops.gen_query_conditions('state', '=', "Enabled", cond)
                cond = res_ops.gen_query_conditions('status', '=', "Ready", cond)
                images = res_ops.query_resource(res_ops.IMAGE, cond)
                for bs_uuid in bs_uuids:
                    temp_list = lib_get_primary_storage_uuid_list_by_backup_storage(bs_uuid)
                    if ps.uuid not in temp_list:
                        continue
                    for image in images:
                        for bs_ref in image.backupStorageRefs:
                            if bs_ref.backupStorageUuid == bs_uuid:
                                utility_vm_image = image
                                break
            if not utility_vm_image:
                image_option = test_util.ImageOption()
                image_option.set_format('qcow2')
                image_option.set_url(os.environ.get('imageUrl_net'))
                image_option.set_name('image_for_robot_test')
                for bs_uuid in bs_uuids:
                    temp_list = lib_get_primary_storage_uuid_list_by_backup_storage(bs_uuid)
                    if ps.uuid in temp_list:
                       target_bs_uuid = bs_uuid
                       break

                image_option.set_backup_storage_uuid_list([target_bs_uuid])
                image_option.set_timeout(7200000)
                image_option.set_mediaType("RootVolumeTemplate")
                import zstackwoodpecker.operations.image_operations as img_ops
                utility_vm_image = img_ops.add_image(image_option)

            utility_vm_create_option = test_util.VmOption()
            utility_vm_create_option.set_name('utility_vm_for_robot_test')
            utility_vm_create_option.set_image_uuid(utility_vm_image.uuid)
            utility_vm_create_option.set_ps_uuid(ps.uuid)
            l3_uuid = lib_get_l3_by_name(os.environ.get('l3VlanNetworkName1')).uuid
            utility_vm_create_option.set_l3_uuids([l3_uuid])
        
            utility_vm = lib_create_vm(utility_vm_create_option)
            #test_dict.add_utility_vm(utility_vm)
            if os.environ.get('ZSTACK_SIMULATOR') != "yes":
                utility_vm.check()
        else:
            import zstackwoodpecker.zstack_test.zstack_test_vm as zstack_vm_header
            utility_vm_uuid = utility_vm.uuid
            utility_vm = zstack_vm_header.ZstackTestVm()
            utility_vm.create_from(utility_vm_uuid)
              
        robot_test_obj.set_utility_vm(utility_vm)

dload_svr = "172.20.194.5"
def lib_dload_server_is_ready(dload_server_type):
    """
         Check and configure image download server.
    """
    global dload_svr
    if dload_server_type == "LOCAL":
        bs_cond = res_ops.gen_query_conditions("status", '=', "Connected")
        bss = res_ops.query_resource(res_ops.BACKUP_STORAGE, bs_cond)
        for bs in bss:
            host = lib_get_backup_storage_host(bs.uuid)
            cmd = "sshpass -p password scp root@%s:/image-pool/ttylinux.raw /tmp/" %(dload_svr)
            os.system(cmd)
            cmd = "sshpass -p password scp /tmp/ttylinux.raw root@%s:/tmp/ttylinux.raw" %(host.managementIp)
            os.system(cmd)
            cmd = "sshpass -p password scp root@%s:/image-pool/CentOS-x86_64-7.2-Minimal.iso /tmp/" %(dload_svr)
            os.system(cmd)
            cmd = "sshpass -p password scp /tmp/CentOS-x86_64-7.2-Minimal.iso root@%s:/tmp/CentOS-x86_64-7.2-Minimal.iso" %(host.managementIp)
            os.system(cmd)
        return True

    elif dload_server_type == "FTP":
        return True

    elif dload_server_type == "SFTP":
        return True

    elif dload_server_type == "HTTPS":
        if scenario_config != None and scenario_file != None and os.path.exists(scenario_file):
            host_ips = scenario_operations.dump_scenario_file_ips(scenario_file)
            for host in host_ips:
                cmd = "cat /etc/hosts|grep dload.zstack.com||sed -i '$a " + dload_svr + " dload.zstack.com' /etc/hosts"
                os.system('sshpass -p password ssh root@%s "%s"' %(host.managementIp_,cmd))
                os.system('sshpass -p password scp root@%s:/https-portal/dload.zstack.com/local/signed.crt /root/' %(dload_svr))
                os.system('sshpass -p password scp /root/signed.crt root@%s:/etc/pki/ca-trust/source/anchors/' %(host.managementIp_))
                os.system('sshpass -p password ssh root@%s update-ca-trust' %(host.managementIp_))
        else:
            cond = res_ops.gen_query_conditions("state", '=', "Enabled")
            cond = res_ops.gen_query_conditions("status", '=', "Connected")
            hosts = res_ops.query_resource(res_ops.HOST, cond)

            if not hosts:
                test_util.test_fail("No host available for adding imagestore for backup test")

            for host in hosts:
                cmd = "cat /etc/hosts|grep dload.zstack.com||sed -i '$a " + dload_svr + " dload.zstack.com' /etc/hosts"
                os.system('sshpass -p password ssh root@%s "%s"' %(host.managementIp,cmd))
                os.system('sshpass -p password scp root@%s:/https-portal/dload.zstack.com/local/signed.crt /root/' %(dload_svr))
                os.system('sshpass -p password scp /root/signed.crt root@%s:/etc/pki/ca-trust/source/anchors/' %(host.managementIp))
                os.system('sshpass -p password ssh root@%s update-ca-trust' %(host.managementIp))
            
        cmd = "wget -c https://%s/ttylinux.raw" %(dload_svr)
        if not os.system(cmd):
            return False

        return True


def lib_robot_create_initial_formation(robot_test_obj):
    '''
        Create initial zstack formation for robot testing
    '''

    stack_template_option = test_util.StackTemplateOption()
    stack_template_option.set_name("robot_test")
    stack_template_option.set_templateContent(robot_test_obj.get_initial_formation())
    import zstackwoodpecker.operations.stack_template as stack_template_ops
    import zstackwoodpecker.operations.resource_stack as resource_stack_ops

    stack_template = stack_template_ops.add_stack_template(stack_template_option)
    lib_robot_initial_formation_auto_parameter(robot_test_obj, stack_template.uuid)
    resource_stack_option = test_util.ResourceStackOption()
    resource_stack_option.set_template_uuid(stack_template.uuid)
    resource_stack_option.set_parameters(robot_test_obj.get_initial_formation_parameters())
    resource_stack = resource_stack_ops.create_resource_stack(resource_stack_option)

    # Import resources from zstack formation so checkers could work for them
    resource_list = resource_stack_ops.get_resource_from_resource_stack(resource_stack.uuid)
    lib_robot_import_resource_from_formation(robot_test_obj, resource_list)

def lib_get_backup_by_uuid(uuid):
    cond = res_ops.gen_query_conditions('uuid', '=', uuid)
    volume_backup = res_ops.query_resource(res_ops.VOLUME_BACKUP, cond)[0]
    return volume_backup


ROBOT = 0
default_snapshot_depth = "128"
def lib_robot_constant_path_operation(robot_test_obj, set_robot=True):
    '''
        Constant path operations for robot testing
    '''
    global default_snapshot_depth
    global ROBOT
    
    if set_robot:
        ROBOT = 1

    def _update_bs_for_robot_state(state):
        cond = res_ops.gen_query_conditions("type", '=', "ImageStoreBackupStorage")
        cond = res_ops.gen_query_conditions("name", '=', "only_for_robot_backup_test", cond)
        bss = res_ops.query_resource(res_ops.BACKUP_STORAGE, cond)
        for bs in bss:
            import zstackwoodpecker.operations.backupstorage_operations as bs_ops
            bs_ops.change_backup_storage_state(bs.uuid, state)

    def _parse_args(all_args):
        normal_args = []
        extra_args = []
        for aa in all_args:
            if not cmp(aa[0:1], "="):
                for a in aa[1:].split(','):
                    extra_args.append(a)
            else:
                normal_args.append(aa)
        return (normal_args, extra_args)

    #_update_bs_for_robot_state("disable")
    test_dict = robot_test_obj.get_test_dict()
    constant_path_list = robot_test_obj.get_constant_path_list()
    if len(constant_path_list) > 0:
        next_action = constant_path_list[0][0]
        if next_action == TestAction.change_global_config_sp_depth :
             test_depth = None
             if len(constant_path_list[0]) > 1:
                 test_depth = constant_path_list[0][1]
             if not test_depth:
                 test_util.test_fail("no snapshot depth available for next action: %s" % (next_action))
             default_snapshot_depth = conf_ops.change_global_config('volumeSnapshot', \
                                               'incrementalSnapshot.maxNum', test_depth)
        elif next_action == TestAction.recover_global_config_sp_depth :
             conf_ops.change_global_config('volumeSnapshot', \
                                   'incrementalSnapshot.maxNum', default_snapshot_depth)
        elif next_action == TestAction.idel :
            test_util.test_dsc('Robot Action: %s ' % next_action)
            lib_vm_random_idel_time(1, 5)
        elif next_action == TestAction.cleanup_imagecache_on_ps :
            import zstackwoodpecker.operations.primarystorage_operations as ps_ops
            target_vm = None
            if len(constant_path_list[0]) > 1:
                target_vm_name = constant_path_list[0][1]
                all_vm_list = test_dict.get_all_vm_list()
                for vm in all_vm_list:
                    if vm.get_vm().name == target_vm_name:
                        target_vm = vm
                        break
            if not target_vm:
                test_util.test_fail("no resource available for next action: %s" % (next_action))
            ps = lib_get_primary_storage_by_vm(target_vm.get_vm())
            ps_ops.cleanup_imagecache_on_primary_storage(ps.uuid)
        elif next_action == TestAction.migrate_vm :
            target_vm = None
            if len(constant_path_list[0]) > 1:
                target_vm_name = constant_path_list[0][1]
                all_vm_list = test_dict.get_all_vm_list()
                for vm in all_vm_list:
                    if vm.get_vm().name == target_vm_name:
                        target_vm = vm
                        break

            if not target_vm:
                test_util.test_fail("no resource available for next action: %s" % (next_action))

            test_util.test_dsc('Robot Action: %s; on VM: %s' \
                    % (next_action, target_vm.get_vm().uuid))
            target_host = lib_find_random_host(target_vm.vm)
            if not target_host:
                test_util.test_fail('no avaiable host was found for doing vm migration')
            else:
                target_vm.migrate(target_host.uuid)
        elif next_action == TestAction.create_image_from_volume:
            target_vm = None
            image_name = None
            target_snapshot = None
            target_snapshots = None
            if len(constant_path_list[0]) > 2:
                target_vm_name = constant_path_list[0][1]
                image_name = constant_path_list[0][2]
                all_vm_list = test_dict.get_all_vm_list()
                for vm in all_vm_list:
                    if vm.get_vm().name == target_vm_name:
                        target_vm = vm
                        break

            if not target_vm or not image_name:
                test_util.test_fail("no resource available for next action: %s" % (next_action))

            root_volume_uuid = lib_get_root_volume(target_vm.vm).uuid
            test_util.test_dsc('Robot Action: %s; on Volume: %s; on VM: %s' % \
                (next_action, root_volume_uuid, target_vm.get_vm().uuid))
   
            new_image = lib_create_template_from_volume(root_volume_uuid)
            import zstackwoodpecker.operations.image_operations as img_ops
            img_ops.update_image(new_image.get_image().uuid, image_name, None)
            test_util.test_dsc('Robot Action Result: %s; new RootVolume Image: %s'\
                    % (next_action, new_image.get_image().uuid))
            test_dict.add_image(new_image)

            snapshots = test_dict.get_volume_snapshot(root_volume_uuid)

            if test_dict.get_volume_snapshot(root_volume_uuid).get_current_snapshot():
                target_snapshots = lib_get_child_snapshots(test_dict.get_volume_snapshot(root_volume_uuid).get_current_snapshot())

                if target_snapshots:
                    for i in target_snapshots:
                        for sp in snapshots.get_primary_snapshots():
                            if i['inventory']['uuid'] == sp.get_snapshot().uuid:
                                test_util.test_logger('%s is already in snapshot list dict, no need to add it' % (i['inventory']['uuid']))
                                break
                            if sp == snapshots.get_primary_snapshots()[-1]:
                                test_util.test_logger('%s is not in snapshot list dict, suppose it should be the new snapshot generated by auto' % (i['inventory']['uuid']))
                                target_snapshot = i

            if not target_snapshots or not test_dict.get_volume_snapshot(root_volume_uuid).get_current_snapshot():
                if lib_get_diff_snapshots_with_zs(test_dict, root_volume_uuid):
                    # Suppose only one new snapshot generated by one action for each volume
                    target_snapshot = lib_get_diff_snapshots_with_zs(test_dict, root_volume_uuid)[0]
                    test_util.test_logger('%s is not in snapshot list dict, suppose it should be the new snapshot generated by auto' % (target_snapshot['inventory']['uuid']))

            if target_snapshot:
                cre_vm_opt = robot_test_obj.get_vm_creation_option()
                cre_vm_opt.set_name("utility_vm_for_robot_test")
                new_snapshot = lib_get_volume_snapshot_by_snapshot(snapshots, target_snapshot, robot_test_obj, test_dict, cre_vm_opt)

                target_volume = new_snapshot.get_target_volume()
                md5sum = target_volume.get_md5sum()
                new_snapshot.set_md5sum(md5sum)
            else:
                test_util.test_logger('No new snapshot found for volume %s, skip the snapshot tree update' % (root_volume_uuid))

        elif next_action == TestAction.create_data_vol_template_from_volume:
            target_volume = None
            image_name = None
            target_snapshot = None
            target_snapshots = None
            if len(constant_path_list[0]) > 2:
                target_volume_name = constant_path_list[0][1]
                image_name = constant_path_list[0][2]
                all_volume_list = test_dict.get_all_volume_list()
                for volume in all_volume_list:
                    if volume.get_volume().name == target_volume_name:
                        target_volume = volume
                        break

            if not target_volume:
                test_util.test_fail("no resource available for next action: %s" % (next_action))

            test_util.test_dsc('Robot Action: %s; on Volume: %s;' % \
                (next_action, target_volume.get_volume().uuid))
            new_data_vol_temp = lib_create_data_vol_template_from_volume(None, target_volume.get_volume())
            import zstackwoodpecker.operations.image_operations as img_ops
            img_ops.update_image(new_data_vol_temp.get_image().uuid, image_name, None)
            test_util.test_dsc('Robot Action Result: %s; new DataVolume Image: %s' \
                    % (next_action, new_data_vol_temp.get_image().uuid))
            robot_test_obj.add_resource_action_history(new_data_vol_temp.get_image().uuid, next_action)
            test_dict.add_image(new_data_vol_temp)

            snapshots = test_dict.get_volume_snapshot(target_volume.get_volume().uuid)

            if test_dict.get_volume_snapshot(target_volume.get_volume().uuid).get_current_snapshot():
                target_snapshots = lib_get_child_snapshots(test_dict.get_volume_snapshot(target_volume.get_volume().uuid).get_current_snapshot())

                if target_snapshots:
                    for i in target_snapshots:
                        for sp in snapshots.get_primary_snapshots():
                            if i['inventory']['uuid'] == sp.get_snapshot().uuid:
                                test_util.test_logger('%s is already in snapshot list dict, no need to add it' % (i['inventory']['uuid']))
                                break
                            if sp == snapshots.get_primary_snapshots()[-1]:
                                test_util.test_logger('%s is not in snapshot list dict, suppose it should be the new snapshot generated by auto' % (i['inventory']['uuid']))
                                target_snapshot = i

            if not target_snapshots or not test_dict.get_volume_snapshot(target_volume.get_volume().uuid).get_current_snapshot():
                if lib_get_diff_snapshots_with_zs(test_dict, target_volume.get_volume().uuid):
                    # Suppose only one new snapshot generated by one action for each volume
                    target_snapshot = lib_get_diff_snapshots_with_zs(test_dict, target_volume.get_volume().uuid)[0]
                    test_util.test_logger('%s is not in snapshot list dict, suppose it should be the new snapshot generated by auto' % (target_snapshot['inventory']['uuid']))


            if target_snapshot:
                cre_vm_opt = robot_test_obj.get_vm_creation_option()
                cre_vm_opt.set_name("utility_vm_for_robot_test")
                new_snapshot = lib_get_volume_snapshot_by_snapshot(snapshots, target_snapshot, robot_test_obj, test_dict, cre_vm_opt)

                target_volume = new_snapshot.get_target_volume()
                md5sum = target_volume.get_md5sum()
                new_snapshot.set_md5sum(md5sum)
            else:
                test_util.test_logger('No new snapshot found for volume %s, skip the snapshot tree update' % (target_volume.get_volume().uuid))

        elif next_action == TestAction.reinit_vm:
            target_vm = None
            target_snapshot = None
            target_snapshots = None
            if len(constant_path_list[0]) > 1:
                target_vm_name = constant_path_list[0][1]
                all_vm_list = test_dict.get_all_vm_list()
                for vm in all_vm_list:
                    if vm.get_vm().name == target_vm_name:
                        target_vm = vm
                        break
            if not target_vm:
                test_util.test_fail("no resource available for next action: %s" % (next_action))
            test_util.test_dsc('Robot Action: %s; on VM: %s' \
                    % (next_action, target_vm.get_vm().uuid))
            target_vm.reinit()

            root_volume_uuid = lib_get_root_volume(target_vm.vm).uuid
            snapshots = test_dict.get_volume_snapshot(root_volume_uuid)

            if test_dict.get_volume_snapshot(root_volume_uuid).get_current_snapshot():
                target_snapshots = lib_get_child_snapshots(test_dict.get_volume_snapshot(root_volume_uuid).get_current_snapshot())

                if target_snapshots:
                    for i in target_snapshots:
                        for sp in snapshots.get_primary_snapshots():
                            if i['inventory']['uuid'] == sp.get_snapshot().uuid:
                                test_util.test_logger('%s is already in snapshot list dict, no need to add it' % (i['inventory']['uuid']))
                                break
                            if sp == snapshots.get_primary_snapshots()[-1]:
                                test_util.test_logger('%s is not in snapshot list dict, suppose it should be the new snapshot generated by auto' % (i['inventory']['uuid']))
                                target_snapshot = i

            if not target_snapshots or not test_dict.get_volume_snapshot(root_volume_uuid).get_current_snapshot():
                if lib_get_diff_snapshots_with_zs(test_dict, root_volume_uuid):
                    # Suppose only one new snapshot generated by one action for each volume
                    target_snapshot = lib_get_diff_snapshots_with_zs(test_dict, root_volume_uuid)[0]
                    test_util.test_logger('%s is not in snapshot list dict, suppose it should be the new snapshot generated by auto' % (target_snapshot['inventory']['uuid']))

            if target_snapshot:
                cre_vm_opt = robot_test_obj.get_vm_creation_option()
                cre_vm_opt.set_name("utility_vm_for_robot_test")
                new_snapshot = lib_get_volume_snapshot_by_snapshot(snapshots, target_snapshot, robot_test_obj, test_dict, cre_vm_opt)

                target_volume = new_snapshot.get_target_volume()
                md5sum = target_volume.get_md5sum()
                new_snapshot.set_md5sum(md5sum)
            else:
                test_util.test_logger('No new snapshot found for volume %s, skip the snapshot tree update' % (root_volume_uuid))

        elif next_action == TestAction.stop_vm:
            target_vm = None
            if len(constant_path_list[0]) > 1:
                target_vm_name = constant_path_list[0][1]
                all_vm_list = test_dict.get_all_vm_list()
                for vm in all_vm_list:
                    if vm.get_vm().name == target_vm_name:
                        target_vm = vm
                        break
            if not target_vm:
                test_util.test_fail("no resource available for next action: %s" % (next_action))
            test_util.test_dsc('Robot Action: %s; on VM: %s' \
                    % (next_action, target_vm.get_vm().uuid))
            target_vm.stop()
            test_dict.mv_vm(target_vm, vm_header.RUNNING, vm_header.STOPPED)
        elif next_action == TestAction.reboot_vm:
            target_vm = None
            if len(constant_path_list[0]) > 1:
                target_vm_name = constant_path_list[0][1]
                all_vm_list = test_dict.get_all_vm_list()
                for vm in all_vm_list:
                    if vm.get_vm().name == target_vm_name:
                        target_vm = vm
                        break
            if not target_vm:
                test_util.test_fail("no resource available for next action: %s" % (next_action))
            test_util.test_dsc('Robot Action: %s; on VM: %s' \
                    % (next_action, target_vm.get_vm().uuid))
            target_vm.reboot()
        elif next_action == TestAction.start_vm:
            target_vm = None
            if len(constant_path_list[0]) > 1:
                target_vm_name = constant_path_list[0][1]
                all_vm_list = test_dict.get_all_vm_list()
                for vm in all_vm_list:
                    if vm.get_vm().name == target_vm_name:
                        target_vm = vm
                        break
            if not target_vm:
                test_util.test_fail("no resource available for next action: %s" % (next_action))

            test_util.test_dsc('Robot Action: %s; on VM: %s' \
                    % (next_action, target_vm.get_vm().uuid))

            target_vm.start()
            test_dict.mv_vm(target_vm, vm_header.STOPPED, vm_header.RUNNING)
        elif next_action == TestAction.suspend_vm:
            target_vm = None
            if len(constant_path_list[0]) > 1:
                target_vm_name = constant_path_list[0][1]
                all_vm_list = test_dict.get_all_vm_list()
                for vm in all_vm_list:
                    if vm.get_vm().name == target_vm_name:
                        target_vm = vm
                        break
            if not target_vm:
                test_util.test_fail("no resource available for next action: %s" % (next_action))

            test_util.test_dsc('Robot Action: %s; on VM: %s' \
                    % (next_action, target_vm.get_vm().uuid))

            target_vm.suspend()
            test_dict.mv_vm(target_vm, vm_header.RUNNING, vm_header.PAUSED)
        elif next_action == TestAction.resume_vm:
            target_vm = None
            if len(constant_path_list[0]) > 1:
                target_vm_name = constant_path_list[0][1]
                all_vm_list = test_dict.get_all_vm_list()
                for vm in all_vm_list:
                    if vm.get_vm().name == target_vm_name:
                        target_vm = vm
                        break
            if not target_vm:
                test_util.test_fail("no resource available for next action: %s" % (next_action))

            test_util.test_dsc('Robot Action: %s; on VM: %s' \
                    % (next_action, target_vm.get_vm().uuid))

            target_vm.resume()
            test_dict.mv_vm(target_vm, vm_header.PAUSED, vm_header.RUNNING)
            
        elif next_action == TestAction.destroy_vm:
            target_vm = None
            if len(constant_path_list[0]) > 1:
                target_vm_name = constant_path_list[0][1]
                all_vm_list = test_dict.get_all_vm_list()
                for vm in all_vm_list:
                    if vm.get_vm().name == target_vm_name:
                        target_vm = vm
                        break
            if not target_vm:
                test_util.test_fail("no resource available for next action: %s" % (next_action))
            test_util.test_dsc('Robot Action: %s; on VM: %s' \
                    % (next_action, target_vm.get_vm().uuid))

            target_vm.destroy()

            vm = lib_get_vm_by_uuid(target_vm.get_vm().uuid)
            vm_current_state = vm.state

            test_dict.rm_vm(target_vm, vm_current_state)
    
            
        elif next_action == TestAction.change_vm_image:
            target_vm = None
            target_image = None
            if len(constant_path_list[0]) > 2:
                target_vm_name = constant_path_list[0][1]
                image_name = constant_path_list[0][2]
                all_vm_list = test_dict.get_all_vm_list()
                for vm in all_vm_list:
                    if vm.get_vm().name == target_vm_name:
                        target_vm = vm
                        break
                target_image = lib_get_image_by_name(image_name)
            elif len(constant_path_list[0]) > 1:
                target_vm_name = constant_path_list[0][1]
                all_vm_list = test_dict.get_all_vm_list()
                for vm in all_vm_list:
                    if vm.get_vm().name == target_vm_name:
                        target_vm = vm
                        break
                vm_root_image_uuid = target_vm.get_vm().imageUuid
                ps_uuid = target_vm.get_vm().allVolumes[0].primaryStorageUuid
                cond = res_ops.gen_query_conditions('uuid', '!=', vm_root_image_uuid)
                cond = res_ops.gen_query_conditions('mediaType', '=', "RootVolumeTemplate", cond)
                cond = res_ops.gen_query_conditions('system', '=', "false", cond)
                target_images = res_ops.query_resource(res_ops.IMAGE, cond)
                for ti in target_images:
                    for tbs in ti.backupStorageRefs:
                        bs_inv = lib_get_backup_storage_by_uuid(tbs.backupStorageUuid)
                        ps_uuid_list = lib_get_primary_storage_uuid_list_by_backup_storage(bs_inv.uuid)
                        if ps_uuid not in ps_uuid_list:
                            continue
                        if bs_inv.name != "only_for_robot_backup_test":
                            target_image = ti
                            break

            if not target_vm or not target_image:
                test_util.test_fail("no resource available for next action: %s" % (next_action))

            test_util.test_dsc('Robot Action: %s; on VM: %s' \
                    % (next_action, target_vm.get_vm().uuid))

            target_vm.change_vm_image(target_image.uuid)
            target_vm.update()
        elif next_action == TestAction.attach_iso:
            target_vm = None
            target_volume = None
            if len(constant_path_list[0]) > 2:
                target_vm_name = constant_path_list[0][1]
                target_volume_name = constant_path_list[0][2]
                all_vm_list = test_dict.get_all_vm_list()
                for vm in all_vm_list:
                    if vm.get_vm().name == target_vm_name:
                        target_vm = vm
                        break

            if not target_vm:
                test_util.test_fail("no resource available for next action: %s" % (next_action))

            test_util.test_dsc('Robot Action: %s; on VM: %s' % \
                (next_action, target_vm.get_vm().uuid))

            cond = res_ops.gen_query_conditions("status", '=', "Connected")
            bs_uuid = res_ops.query_resource(res_ops.BACKUP_STORAGE, cond)[0].uuid
            img_option = test_util.ImageOption()
            img_option.set_name('iso')
            img_option.set_backup_storage_uuid_list([bs_uuid])
            mn_ip = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].hostName
            if os.system("sshpass -p password ssh %s 'ls  %s/apache-tomcat/webapps/zstack/static/zstack-repo/'" % (mn_ip, os.environ.get('zstackInstallPath'))) == 0:
                os.system("sshpass -p password ssh %s 'echo fake iso for test only >  %s/apache-tomcat/webapps/zstack/static/zstack-repo/7/x86_64/os/test.iso'" % (mn_ip, os.environ.get('zstackInstallPath')))
                img_option.set_url('http://%s:8080/zstack/static/zstack-repo/7/x86_64/os/test.iso' % (mn_ip))
            else:
                os.system("sshpass -p password ssh %s 'echo fake iso for test only >  %s/apache-tomcat/webapps/zstack/static/test.iso'" % (mn_ip, os.environ.get('zstackInstallPath')))
                img_option.set_url('http://%s:8080/zstack/static/test.iso' % (mn_ip))
            image_inv = img_ops.add_iso_template(img_option)
            image = test_image.ZstackTestImage()
            image.set_image(image_inv)
            image.set_creation_option(img_option)

            cond = res_ops.gen_query_conditions('name', '=', 'iso')
            iso_uuid = res_ops.query_resource(res_ops.IMAGE, cond)[0].uuid
            img_ops.attach_iso(iso_uuid, target_vm.vm.uuid)
            lib_wait_target_up(target_vm.get_vm().vmNics[0].ip, 22, 300)

        elif next_action == TestAction.detach_iso:
            target_vm = None
            target_volume = None
            if len(constant_path_list[0]) > 2:
                target_vm_name = constant_path_list[0][1]
                target_volume_name = constant_path_list[0][2]
                all_vm_list = test_dict.get_all_vm_list()
                for vm in all_vm_list:
                    if vm.get_vm().name == target_vm_name:
                        target_vm = vm
                        break

            if not target_vm:
                test_util.test_fail("no resource available for next action: %s" % (next_action))

            test_util.test_dsc('Robot Action: %s; on VM: %s' % \
                (next_action, \
                target_vm.get_vm().uuid))

            cond = res_ops.gen_query_conditions('name', '=', 'iso')
            iso_uuid = res_ops.query_resource(res_ops.IMAGE, cond)[0].uuid
            img_ops.detach_iso(target_vm.vm.uuid, iso_uuid)
            test_lib.lib_wait_target_up(target_vm.get_vm().vmNics[0].ip, 22, 300)

        elif next_action == TestAction.attach_volume:
            target_vm = None
            target_volume = None
            if len(constant_path_list[0]) > 2:
                target_vm_name = constant_path_list[0][1]
                target_volume_name = constant_path_list[0][2]
                all_vm_list = test_dict.get_all_vm_list()
                for vm in all_vm_list:
                    if vm.get_vm().name == target_vm_name:
                        target_vm = vm
                        break
                all_volume_list = test_dict.get_all_volume_list()
                for volume in all_volume_list:
                    if volume.get_volume().name == target_volume_name:
                        target_volume = volume
                        break

            if not target_vm or not target_volume:
                test_util.test_fail("no resource available for next action: %s" % (next_action))

            test_util.test_dsc('Robot Action: %s; on Volume: %s; on VM: %s' % \
                (next_action, target_volume.get_volume().uuid, \
                target_vm.get_vm().uuid))
    
            root_volume = lib_get_root_volume(target_vm.get_vm())
            ps = lib_get_primary_storage_by_uuid(root_volume.primaryStorageUuid)
            if not lib_check_vm_live_migration_cap(target_vm.vm) or ps.type == inventory.LOCAL_STORAGE_TYPE:
                ls_ref = lib_get_local_storage_reference_information(target_volume.get_volume().uuid)
                if ls_ref:
                    volume_host_uuid = ls_ref[0].hostUuid
                    vm_host_uuid = lib_get_vm_host(target_vm.vm).uuid
                    if vm_host_uuid and volume_host_uuid != vm_host_uuid:
                        test_util.test_logger('need to migrate volume: %s to host: %s, before attach it to vm: %s' % (target_volume.get_volume().uuid, vm_host_uuid, target_vm.vm.uuid))
                        target_volume.migrate(vm_host_uuid)
   
            target_volume.attach(target_vm)
            if target_volume.get_volume().isShareable:
                test_dict.add_volume_with_snapshots(target_volume, target_vm.vm.uuid)
            else:
                test_dict.mv_volume_with_snapshots(target_volume, test_stage.free_volume, target_vm.vm.uuid)
            all_volume_snapshots = test_dict.get_all_available_snapshots()

        elif next_action == TestAction.detach_volume:
            target_volume = None
            target_vm = None
            if len(constant_path_list[0]) > 2:
                target_volume_name = constant_path_list[0][1]
                target_vm_name = constant_path_list[0][2]
                all_volume_list = test_dict.get_all_volume_list()
                for volume in all_volume_list:
                    if volume.get_volume().name == target_volume_name:
                        target_volume = volume
                        break
                all_vm_list = test_dict.get_all_vm_list()
                for vm in all_vm_list:
                    if vm.get_vm().name == target_vm_name:
                        target_vm = vm
                        break
            elif len(constant_path_list[0]) > 1:
                target_volume_name = constant_path_list[0][1]
                all_volume_list = test_dict.get_all_volume_list()
                for volume in all_volume_list:
                    if volume.get_volume().name == target_volume_name:
                        target_volume = volume
                        break

            if not target_volume:
                test_util.test_fail("no resource available for next action: %s" % (next_action))
            if target_volume.get_volume().isShareable and not target_vm:
                test_util.test_fail("no resource available for next action: %s" % (next_action))

            test_util.test_dsc('Robot Action: %s; on Volume: %s' % \
                (next_action, target_volume.get_volume().uuid))
            all_volume_snapshots = test_dict.get_all_available_snapshots()

            target_vm_uuid = target_volume.get_volume().vmInstanceUuid
            if target_volume.get_volume().isShareable:
                target_vm_uuid = target_vm.get_vm().uuid
                target_volume.detach(target_vm_uuid)
                test_dict.rm_volume_with_snapshots(target_volume, target_vm.get_vm().uuid)
            else:
                target_volume.detach()
                test_dict.mv_volume_with_snapshots(target_volume, target_vm_uuid, test_stage.free_volume)
            all_volume_snapshots = test_dict.get_all_available_snapshots()

        elif next_action == TestAction.delete_volume:
            target_volume = None
            if len(constant_path_list[0]) > 1:
                target_volume_name = constant_path_list[0][1]
                all_volume_list = test_dict.get_all_volume_list()
                for volume in all_volume_list:
                    if volume.get_volume().name == target_volume_name:
                        target_volume = volume
                        break

            if not target_volume:
                test_util.test_fail("no resource available for next action: %s" % (next_action))
   
            test_util.test_dsc('Robot Action: %s; on Volume: %s' % \
                (next_action, target_volume.get_volume().uuid))

            target_volume.delete()
            test_dict.rm_volume(target_volume)

        elif next_action == TestAction.resize_volume:
            target_vm = None
            target_snapshot = None
            target_snapshots = None

            if len(constant_path_list[0]) > 2:
                target_vm_name = constant_path_list[0][1]
                delta = constant_path_list[0][2]
                all_vm_list = test_dict.get_all_vm_list()
                for vm in all_vm_list:
                    if vm.get_vm().name == target_vm_name:
                        target_vm = vm
                        break
            if not target_vm:
                test_util.test_fail("no resource available for next action: %s" % (next_action))

            root_volume_uuid = lib_get_root_volume(target_vm.vm).uuid
            current_size = lib_get_root_volume(target_vm.vm).size
            new_size = current_size + int(delta)
            import zstackwoodpecker.operations.volume_operations as vol_ops
            vol_ops.resize_volume(root_volume_uuid, new_size)

            snapshots = test_dict.get_volume_snapshot(root_volume_uuid)

            if test_dict.get_volume_snapshot(root_volume_uuid).get_current_snapshot():
                target_snapshots = lib_get_child_snapshots(test_dict.get_volume_snapshot(root_volume_uuid).get_current_snapshot())

                if target_snapshots:
                    for i in target_snapshots:
                        for sp in snapshots.get_primary_snapshots():
                            if i['inventory']['uuid'] == sp.get_snapshot().uuid:
                                test_util.test_logger('%s is already in snapshot list dict, no need to add it' % (i['inventory']['uuid']))
                                break
                            if sp == snapshots.get_primary_snapshots()[-1]:
                                test_util.test_logger('%s is not in snapshot list dict, suppose it should be the new snapshot generated by auto' % (i['inventory']['uuid']))
                                target_snapshot = i

            if not target_snapshots or not test_dict.get_volume_snapshot(root_volume_uuid).get_current_snapshot():
                if lib_get_diff_snapshots_with_zs(test_dict, root_volume_uuid):
                    # Suppose only one new snapshot generated by one action for each volume
                    target_snapshot = lib_get_diff_snapshots_with_zs(test_dict, root_volume_uuid)[0]
                    test_util.test_logger('%s is not in snapshot list dict, suppose it should be the new snapshot generated by auto' % (target_snapshot['inventory']['uuid']))

            if target_snapshot:
                cre_vm_opt = robot_test_obj.get_vm_creation_option()
                cre_vm_opt.set_name("utility_vm_for_robot_test")
                new_snapshot = lib_get_volume_snapshot_by_snapshot(snapshots, target_snapshot, robot_test_obj, test_dict, cre_vm_opt)

                target_volume = new_snapshot.get_target_volume()
                md5sum = target_volume.get_md5sum()
                new_snapshot.set_md5sum(md5sum)
            else:
                test_util.test_logger('No new snapshot found for volume %s, skip the snapshot tree update' % (root_volume_uuid))

        elif next_action == TestAction.resize_data_volume:
            target_volume = None
            target_snapshot = None
            target_snapshots = None

            if len(constant_path_list[0]) > 2:
                target_volume_name = constant_path_list[0][1]
                delta = constant_path_list[0][2]
                all_volume_list = test_dict.get_all_volume_list()
                for volume in all_volume_list:
                    if volume.get_volume().name == target_volume_name:
                        target_volume = volume
                        break

            if not target_volume:
                test_util.test_fail("no resource available for next action: %s" % (next_action))

            test_util.test_dsc('Robot Action: %s; on Volume: %s' % \
                (next_action, target_volume.get_volume().uuid))
            current_size = target_volume.get_volume().size
            new_size = current_size + int(delta)
            target_volume.resize(new_size)
            target_volume.update()
            target_volume.update_volume()

            snapshots = test_dict.get_volume_snapshot(target_volume.get_volume().uuid)

            if test_dict.get_volume_snapshot(target_volume.get_volume().uuid).get_current_snapshot():
                target_snapshots = lib_get_child_snapshots(test_dict.get_volume_snapshot(target_volume.get_volume().uuid).get_current_snapshot())

                if target_snapshots:
                    for i in target_snapshots:
                        for sp in snapshots.get_primary_snapshots():
                            if i['inventory']['uuid'] == sp.get_snapshot().uuid:
                                test_util.test_logger('%s is already in snapshot list dict, no need to add it' % (i['inventory']['uuid']))
                                break
                            if sp == snapshots.get_primary_snapshots()[-1]:
                                test_util.test_logger('%s is not in snapshot list dict, suppose it should be the new snapshot generated by auto' % (i['inventory']['uuid']))
                                target_snapshot = i

            if not target_snapshots or not test_dict.get_volume_snapshot(target_volume.get_volume().uuid).get_current_snapshot():
                if lib_get_diff_snapshots_with_zs(test_dict, target_volume.get_volume().uuid):
                    # Suppose only one new snapshot generated by one action for each volume
                    target_snapshot = lib_get_diff_snapshots_with_zs(test_dict, target_volume.get_volume().uuid)[0]
                    test_util.test_logger('%s is not in snapshot list dict, suppose it should be the new snapshot generated by auto' % (target_snapshot['inventory']['uuid']))


            if target_snapshot:
                cre_vm_opt = robot_test_obj.get_vm_creation_option()
                cre_vm_opt.set_name("utility_vm_for_robot_test")
                new_snapshot = lib_get_volume_snapshot_by_snapshot(snapshots, target_snapshot, robot_test_obj, test_dict, cre_vm_opt)

                target_volume = new_snapshot.get_target_volume()
                md5sum = target_volume.get_md5sum()
                new_snapshot.set_md5sum(md5sum)
            else:
                test_util.test_logger('No new snapshot found for volume %s, skip the snapshot tree update' % (target_volume.get_volume().uuid))

        elif next_action == TestAction.create_data_volume_from_image:
            target_images = None
            target_image_name = None
            (normal_args, extra_args) = _parse_args(constant_path_list[0])
            if len(normal_args) > 2:
                target_volume_name = normal_args[1]
                target_image_name = normal_args[2]
                cond = res_ops.gen_query_conditions('name', '=', target_image_name)
                cond = res_ops.gen_query_conditions('mediaType', '=', "DataVolumeTemplate", cond)
                target_images = res_ops.query_resource(res_ops.IMAGE, cond)
            elif len(normal_args) > 1:
                target_volume_name = normal_args[1]
                cond = res_ops.gen_query_conditions('mediaType', '=', "DataVolumeTemplate")
                target_images = res_ops.query_resource(res_ops.IMAGE, cond)
            if not target_images:
                if not target_image_name:
                    ps_uuid = lib_robot_get_default_configs(robot_test_obj, "PS")
                    
                    image_option = test_util.ImageOption()
                    image_option.set_format('qcow2')
                    image_option.set_name('data_volume_image')
                    bs_cond = res_ops.gen_query_conditions("status", '=', "Connected")
                    bss = res_ops.query_resource(res_ops.BACKUP_STORAGE, bs_cond)
                    filtered_bss = []
                    for bs in bss:
                        ps_uuid_list = lib_get_primary_storage_uuid_list_by_backup_storage(bs.uuid)
                        if ps_uuid in ps_uuid_list:
                            filtered_bss.append(bs)
                        
                    if not filtered_bss:
                        test_util.test_fail("not find available backup storage. Skip test")

                    image_option.set_url(os.environ.get('emptyimageUrl'))
                    image_option.set_backup_storage_uuid_list([filtered_bss[0].uuid])
                    image_option.set_timeout(120000)
                    image_option.set_mediaType("DataVolumeTemplate")
                    import zstackwoodpecker.operations.image_operations as img_ops
                    image = img_ops.add_image(image_option)
                
                    import zstackwoodpecker.zstack_test.zstack_test_image as zstack_image_header
                    new_image = zstack_image_header.ZstackTestImage()
                    new_image.set_creation_option(image_option)
                    new_image.set_image(image)
                    test_dict.add_image(new_image)
                    target_images = [image]
                else:
                    test_util.test_fail("no resource available for next action: %s" % (next_action))
            systemtags = []
            for ea in extra_args:
                if ea == "shareable":
                    systemtags.append("ephemeral::shareable")
                if ea == "scsi":
                    systemtags.append("capability::virtio-scsi")


            test_util.test_dsc('Robot Action: %s; on Image: %s' % \
                (next_action, target_images[0]['uuid']))
            target_image = lib_get_image_by_uuid(target_images[0]['uuid'])
            bs_uuid = target_image.backupStorageRefs[0].backupStorageUuid
            ps_uuid_list = lib_get_primary_storage_uuid_list_by_backup_storage(bs_uuid)
            ps_uuid = random.choice(ps_uuid_list)
            ps = lib_get_primary_storage_by_uuid(ps_uuid)
            host_uuid = None
            if ps.type == inventory.LOCAL_STORAGE_TYPE:
                host_uuid = lib_robot_get_default_configs(robot_test_obj, "HOST")

            import zstackwoodpecker.operations.volume_operations as vol_ops
            import zstackwoodpecker.zstack_test.zstack_test_volume as zstack_volume_header
            volume_inv = vol_ops.create_volume_from_template(target_images[0]['uuid'], ps_uuid, target_volume_name, host_uuid, systemtags)
            new_volume = zstack_volume_header.ZstackTestVolume()
            new_volume.create_from(volume_inv.uuid, None)
            test_dict.add_volume(new_volume)
    
            test_util.test_dsc('Robot Action Result: %s; new Volume: %s' % \
                (next_action, new_volume.get_volume().uuid))
        elif next_action == TestAction.ps_migrate_volume:
            target_volume = None
            target_vm = None
            target_volume_uuid = None
            if len(constant_path_list[0]) > 1:
                target_volume_name = constant_path_list[0][1]
                all_volume_list = test_dict.get_all_volume_list()
                for volume in all_volume_list:
                    if volume.get_volume().name == target_volume_name:
                        target_volume = volume
                        target_volume_uuid = volume.get_volume().uuid
                        break
                if not target_volume_uuid:
                    all_vm_list = test_dict.get_all_vm_list()
                    for vm in all_vm_list:
                        if "%s-root" % vm.get_vm().name == target_volume_name:
                            target_vm = target_vm
                            target_volume_uuid = lib_get_root_volume(vm.get_vm()).uuid
                            break

            if not target_volume_uuid:
                test_util.test_fail("no resource available for next action: %s" % (next_action))

            target_snapshots = test_dict.get_volume_snapshot(target_volume_uuid)

            test_util.test_dsc('Robot Action: %s; on Volume: %s' % \
                (next_action, target_volume_uuid))
            import zstackwoodpecker.operations.datamigrate_operations as datamigr_ops
            target_pss = datamigr_ops.get_ps_candidate_for_vol_migration(target_volume_uuid)
            if not target_pss:
                test_util.test_fail("no resource available for next action: %s" % (next_action))
            datamigr_ops.ps_migrage_volume(target_pss[0].uuid, target_volume_uuid)
            if target_vm:
                target_vm.update()
            if target_volume:
                target_volume.update_volume()
            if target_snapshots:
                target_snapshots.update()

        elif next_action == TestAction.create_volume :
            ps_uuid = lib_robot_get_default_configs(robot_test_obj, "PS")
            target_volume_name = None
            (normal_args, extra_args) = _parse_args(constant_path_list[0])
            if len(normal_args) > 1:
                target_volume_name = normal_args[1]
            if not target_volume_name:
                test_util.test_fail("no resource available for next action: %s" % (next_action))

            test_util.test_dsc('Robot Action: %s ' % next_action)
            volume_creation_option = test_util.VolumeOption()
            volume_creation_option.set_name(target_volume_name)
            volume_creation_option.set_primary_storage_uuid(ps_uuid)
            systemtags = []
            for ea in extra_args:
                if ea == "shareable":
                    systemtags.append("ephemeral::shareable")
                if ea == "scsi":
                    systemtags.append("capability::virtio-scsi")

            if ps_uuid:
                ps = lib_get_primary_storage_by_uuid(ps_uuid)
                if ps.type == inventory.LOCAL_STORAGE_TYPE:
                    host_uuid = lib_robot_get_default_configs(robot_test_obj, "HOST")
                    systemtags.append("localStorage::hostUuid::%s" % (host_uuid))
            if systemtags:
                volume_creation_option.set_system_tags(systemtags)
            new_volume = lib_create_volume_from_offering(volume_creation_option)
            test_dict.add_volume(new_volume)
    
            test_util.test_dsc('Robot Action Result: %s; new Volume: %s' % \
                (next_action, new_volume.get_volume().uuid))
        elif next_action == TestAction.cleanup_ps_cache:
            import zstackwoodpecker.operations.primarystorage_operations as ps_ops
            cond = res_ops.gen_query_conditions('state', '=', 'Enabled')
            cond = res_ops.gen_query_conditions('status', '=', 'Connected')
            pss = res_ops.query_resource_fields(res_ops.PRIMARY_STORAGE, cond, \
                None, ['uuid'])

            for ps in pss:
                ps_ops.cleanup_imagecache_on_primary_storage(ps.uuid)
        elif next_action == TestAction.create_volume_snapshot:
            target_volume_uuid = None
            target_snapshot_name = None
            if len(constant_path_list[0]) > 2:
                target_volume_name = constant_path_list[0][1]
                target_snapshot_name = constant_path_list[0][2]
                all_volume_list = test_dict.get_all_volume_list()
                for volume in all_volume_list:
                    if volume.get_volume().name == target_volume_name:
                        target_volume_uuid = volume.get_volume().uuid
                        ps_uuid = volume.get_volume().primaryStorageUuid
                        break
                if not target_volume_uuid:
                    all_vm_list = test_dict.get_all_vm_list()
                    for vm in all_vm_list:
                        if "%s-root" % vm.get_vm().name == target_volume_name:
                            target_volume = lib_get_root_volume(vm.get_vm())
                            target_volume_uuid = target_volume.uuid
                            ps_uuid = target_volume.primaryStorageUuid
                            break

            if not target_volume_uuid:
                test_util.test_fail("no resource available for next action: %s" % (next_action))

            test_util.test_dsc('Robot Action: %s; on Volume: %s' % (next_action, target_volume_uuid))

            snapshots = test_dict.get_volume_snapshot(target_volume_uuid)
            cre_vm_opt = robot_test_obj.get_vm_creation_option()
            cre_vm_opt.set_name("utility_vm_for_robot_test")
            new_snapshot = lib_create_volume_snapshot_from_volume(snapshots, robot_test_obj, test_dict, cre_vm_opt, target_snapshot_name)
 
            target_volume = new_snapshot.get_target_volume()
            md5sum = target_volume.get_md5sum()
            new_snapshot.set_md5sum(md5sum)
    
            test_util.test_dsc('Robot Action Result: %s; new SP: %s' % \
                (next_action, new_snapshot.get_snapshot().uuid))
        elif next_action == TestAction.delete_volume_snapshot:
            target_volume_snapshots = None
            target_snapshot = None
            target_snapshot_name = None
            if len(constant_path_list[0]) > 1:
                target_snapshot_name = constant_path_list[0][1]
           
                all_volume_snapshots = test_dict.get_all_available_snapshots()
                for candidate_snapshots in all_volume_snapshots:
                    for candidate_snapshot in candidate_snapshots.get_primary_snapshots():
                        if candidate_snapshot.get_snapshot().name == target_snapshot_name:
                            target_volume_snapshots = candidate_snapshots
                            target_snapshot = candidate_snapshot
                            break

            if not target_snapshot:
                test_util.test_fail("no resource available for next action: %s" % (next_action))

            target_volume_snapshots.delete_snapshot(target_snapshot)
            test_util.test_dsc('Robot Action: %s; on Volume: %s; on SP: %s' % \
                (next_action, \
                target_volume_snapshots.get_target_volume().get_volume().uuid, \
                target_snapshot.get_snapshot().uuid))

            robot_test_obj.add_resource_action_history(target_snapshot.get_snapshot().uuid, next_action)
            robot_test_obj.add_resource_action_history(target_volume_snapshots.get_target_volume().get_volume().uuid, next_action)
            #If both volume and snapshots are deleted, volume_snapshot obj could be 
            # removed.
            #if not target_volume_snapshots.get_backuped_snapshots():
            #    target_volume_obj = target_volume_snapshots.get_target_volume()
            #    if target_volume_obj.get_state() == vol_header.EXPUNGED \
            #            or (target_volume_snapshots.get_volume_type() == \
            #                vol_header.ROOT_VOLUME \
            #                and target_volume_obj.get_target_vm().get_state() == \
            #                    vm_header.EXPUNGED):
            #        test_dict.rm_volume_snapshot(target_volume_snapshots)
        elif next_action == TestAction.batch_delete_volume_snapshot:
            target_volume_snapshots = None
            target_snapshot = None
            target_snapshot_name = None
            target_snapshot_uuid_list = []
            target_snapshot_list = []

            all_volume_snapshots = test_dict.get_all_available_snapshots()
            import zstackwoodpecker.operations.volume_operations as vol_ops
            for snapshot_name in constant_path_list[0][1]:
                cond = res_ops.gen_query_conditions('name','=',snapshot_name)
                target_snapshot = res_ops.query_resource(res_ops.VOLUME_SNAPSHOT, cond)
                if not target_snapshot:
                    test_util.test_logger("Can not find target snapshot: %s" % snapshot_name)
                else:
                    target_snapshot_uuid_list.append(target_snapshot[0].uuid)
                    for candidate_snapshots in all_volume_snapshots:
                        for candidate_snapshot in candidate_snapshots.get_primary_snapshots():
                            if candidate_snapshot.get_snapshot().name == snapshot_name:
                                target_volume_snapshots = candidate_snapshots
                                target_snapshot_list.append(candidate_snapshot)
                                break
            target_volume_snapshots.delete_snapshots_dict_record(target_snapshot_list)
            vol_ops.batch_delete_snapshot(target_snapshot_uuid_list)
            test_util.test_dsc(test_dict)

        elif next_action == TestAction.use_volume_snapshot:
            target_volume_snapshots = None
            target_snapshot = None
            target_snapshot_name = None
            if len(constant_path_list[0]) > 1:
                target_snapshot_name = constant_path_list[0][1]
           
                all_volume_snapshots = test_dict.get_all_available_snapshots()
                for candidate_snapshots in all_volume_snapshots:
                    for candidate_snapshot in candidate_snapshots.get_primary_snapshots():
                        if candidate_snapshot.get_snapshot().name == target_snapshot_name:
                            target_volume_snapshots = candidate_snapshots
                            target_snapshot = candidate_snapshot
                            break

            if not target_snapshot:
                test_util.test_fail("no resource available for next action: %s" % (next_action))

            test_util.test_dsc('Robot Action: %s; on Volume: %s; on SP: %s' % \
                (next_action, \
                target_snapshot.get_target_volume().get_volume().uuid, \
                target_snapshot.get_snapshot().uuid))
            md5sum = target_snapshot.get_md5sum()
            target_volume_snapshots.use_snapshot(target_snapshot)
            target_snapshot.get_target_volume().set_md5sum(md5sum)
            
        elif next_action == TestAction.create_volume_backup:
            backup_name = None
            target_volume_uuid = None
            if len(constant_path_list[0]) > 2:
                target_volume_name = constant_path_list[0][1]
                backup_name = constant_path_list[0][2]
                all_volume_list = test_dict.get_all_volume_list()
                for volume in all_volume_list:
                    if volume.get_volume().name == target_volume_name:
                        target_volume_uuid = volume.get_volume().uuid
                        ps_uuid = volume.get_volume().primaryStorageUuid
                        md5sum = volume.get_md5sum()
                        break
                if not target_volume_uuid:
                    all_vm_list = test_dict.get_all_vm_list()
                    for vm in all_vm_list:
                        if "%s-root" % vm.get_vm().name == target_volume_name:
                            target_volume = lib_get_root_volume(vm.get_vm())
                            target_volume_uuid = target_volume.uuid
                            ps_uuid = target_volume.primaryStorageUuid
                            break


            if not target_volume_uuid or not backup_name:
                test_util.test_fail("no resource available for next action: %s" % (next_action))

            cond = res_ops.gen_query_conditions("type", '=', "ImageStoreBackupStorage")
            cond = res_ops.gen_query_conditions("name", '=', "only_for_robot_backup_test", cond)
            bss = res_ops.query_resource(res_ops.BACKUP_STORAGE, cond)
            if not bss:
                cond = res_ops.gen_query_conditions("type", '=', "ImageStoreBackupStorage")
                bss = res_ops.query_resource(res_ops.BACKUP_STORAGE, cond)
                if not bss:
                    cond = res_ops.gen_query_conditions("state", '=', "Enabled")
                    cond = res_ops.gen_query_conditions("status", '=', "Connected")
                    hosts = res_ops.query_resource(res_ops.HOST, cond)
                    if not hosts:
                        test_util.test_fail("No host available for adding imagestore for backup test")
                    host = hosts[0]
                    import zstackwoodpecker.operations.backupstorage_operations as bs_ops
                    bs_option = test_util.ImageStoreBackupStorageOption()
                    bs_option.set_name("only_for_robot_backup_test")
                    bs_option.set_url("/home/sftpBackupStorage")
                    bs_option.set_hostname(host.managementIp)
                    bs_option.set_password('password')
                    bs_option.set_sshPort(host.sshPort)
                    bs_option.set_username(host.username)
                    bs_inv = bs_ops.create_image_store_backup_storage(bs_option)
                
                    bs_ops.attach_backup_storage(bs_inv.uuid, host.zoneUuid)
                    bss = [bs_inv]
            bs = bss[0]
               
            backup_option = test_util.BackupOption()
            backup_option.set_name(backup_name)
            backup_option.set_volume_uuid(target_volume_uuid)
            backup_option.set_backupStorage_uuid(bs.uuid)
            import zstackwoodpecker.operations.volume_operations as vol_ops
            test_util.test_dsc('Robot Action: %s; on Volume: %s' % \
                (next_action, target_volume_uuid))

            #_update_bs_for_robot_state("enable")
            backup = vol_ops.create_backup(backup_option)
            #_update_bs_for_robot_state("disable")
            test_dict.add_backup(backup.uuid)
            test_dict.add_backup_md5sum(backup.uuid, md5sum)
        elif next_action == TestAction.use_volume_backup:
            target_backup = None
            backup_name = None
            if len(constant_path_list[0]) > 1:
                backup_name = constant_path_list[0][1]
                backup_list = test_dict.get_backup_list()
                for backup_uuid in backup_list:
                    backup = lib_get_backup_by_uuid(backup_uuid)
                    if backup.name == backup_name:
                        target_backup = backup
                        break

            if not target_backup or not backup_name:
                test_util.test_fail("no resource available for next action: %s" % (next_action))
            import zstackwoodpecker.operations.volume_operations as vol_ops
            test_util.test_dsc('Robot Action: %s; on Backup: %s' % \
                (next_action, target_backup.uuid))

            #_update_bs_for_robot_state("enable")
            backup = vol_ops.revert_volume_from_backup(target_backup.uuid)
            #_update_bs_for_robot_state("disable")
            for volume in test_dict.get_all_volume_list():
                if volume.get_volume().uuid == target_backup.volumeUuid:
                    volume.update()
                    volume.update_volume()
                    md5sum = test_dict.get_backup_md5sum(target_backup.uuid)
                    volume.set_md5sum(md5sum)
                    break
        elif next_action == TestAction.create_data_template_from_backup:
            target_backup = None
            backup_name = None
            image_name = None
            if len(constant_path_list[0]) > 2:
                backup_name = constant_path_list[0][1]
                image_name = constant_path_list[0][2]
                backup_list = test_dict.get_backup_list()
                for backup_uuid in backup_list:
                    backup = lib_get_backup_by_uuid(backup_uuid)
                    if backup.name == backup_name:
                        target_backup = backup
                        break
            if not target_backup or not image_name:
                test_util.test_fail("no resource available for next action: %s" % (next_action))
            test_util.test_dsc('Robot Action: %s; on Backup: %s' % \
                (next_action, target_backup.uuid))

            ps_uuid = lib_robot_get_default_configs(robot_test_obj, "PS")
            
            bs_cond = res_ops.gen_query_conditions("status", '=', "Connected")
            bss = res_ops.query_resource(res_ops.BACKUP_STORAGE, bs_cond)
            filtered_bss = []
            for bs in bss:
                ps_uuid_list = lib_get_primary_storage_uuid_list_by_backup_storage(bs.uuid)
                if ps_uuid in ps_uuid_list:
                    filtered_bss.append(bs)
                
            if not filtered_bss:
                test_util.test_fail("not find available backup storage. Skip test")

            import zstackwoodpecker.operations.image_operations as img_ops
            img_ops.create_data_template_from_backup(filtered_bss[0].uuid, target_backup.uuid, image_name)
        elif next_action == TestAction.add_image:
            backup_name = None
            image_name = None
            image_format = None
            image_url = None
            image_type = None
            dload_server_type = None
            
            global dload_svr
            def _get_image_name(dload_server_type, image_format):
                if dload_server_type == "LOCAL" and image_format == "raw":
                    return "file:///tmp/ttylinux.raw"
                elif dload_server_type == "LOCAL" and image_format == "iso":
                    return "file:///tmp/CentOS-x86_64-7.2-Minimal.iso"
                elif dload_server_type == "FTP" and image_format == "raw":
                    return "ftp://test:password@" + dload_svr + ":21/ttylinux.raw"
                elif dload_server_type == "FTP" and image_format == "iso":
                    return "ftp://test:password@" + dload_svr + ":21/CentOS-x86_64-7.2-Minimal.iso"
                elif dload_server_type == "SFTP" and image_format == "raw":
                    return "sftp://test:password@" + dload_svr + ":2294/ttylinux.raw"
                elif dload_server_type == "SFTP" and image_format == "iso":
                    return "sftp://test:password@" + dload_svr + ":2294/CentOS-x86_64-7.2-Minimal.iso"
                elif dload_server_type == "HTTPS" and image_format == "raw":
                    return "https://dload.zstack.com/ttylinux.raw"
                elif dload_server_type == "HTTPS" and image_format == "iso":
                    return "https://dload.zstack.com/CentOS-x86_64-7.2-Minimal.iso"
                else:
                    test_util.test_logger("dload_server_type=" + dload_server_type)
                    test_util.test_logger("image_format=" + image_format)
                    test_util.test_fail("not found matched image")
                    return 

            if len(constant_path_list[0]) > 4:
                bs_type = constant_path_list[0][1]
                image_name = constant_path_list[0][2]
                image_format = constant_path_list[0][3]
                image_type = constant_path_list[0][4]
                dload_server_type = constant_path_list[0][5]
                #image_list = test_dict.get_image_list()
                #for image in image_list:
                #    if image.name == image_name:
                #        image_uuid = image.get_image().uuid
                #        break
                #else:
                #    test_util.test_fail("not find candidate image.")
            else:
                test_util.test_fail("candidate argument number is less than 4.")

            test_util.test_dsc('Robot Action: %s;' %(next_action))

            #ps_uuid = lib_robot_get_default_configs(robot_test_obj, "PS")
            if not lib_dload_server_is_ready(dload_server_type):
                test_util.test_fail("download server is not ready yet, please check type=%s" %(str(dload_server_type)))

            bs_cond = res_ops.gen_query_conditions("status", '=', "Connected")
            bss = res_ops.query_resource(res_ops.BACKUP_STORAGE, bs_cond)
            bs_uuid = None
            for bs in bss:
                test_util.test_logger("DEBUG>>>bs.type=(%s) vs. bs_type=(%s)" %(bs.type, bs_type))
                if bs.type.strip() == bs_type.strip():
                    bs_uuid = bs.uuid
                    break
            else:
                test_util.test_skip("not find bs with assigned name")
                
            image_option = test_util.ImageOption()
            #image_option.set_uuid(image_uuid)
            image_option.set_name(image_name)
            image_option.set_description('Description->'+ image_name)
            image_option.set_format(image_format)

            if image_type == "RootVolumeTemplate":
                image_option.set_mediaType('RootVolumeTemplate')
            elif image_type == "DataVolumeTemplate":
                image_option.set_mediaType('DataVolumeTemplate')
            else:
                test_util.test_fail("imageMediaType is not in RootVolumeTemplate|DataVolumeTemplate, actual is [%s]" %(image_type))

            image_option.set_backup_storage_uuid_list([bs_uuid])
            image_option.url = _get_image_name(dload_server_type, image_format)
            image_option.set_timeout(24*60*60*1000)
            import zstackwoodpecker.operations.image_operations as img_ops
            image = img_ops.add_image(image_option)

            import zstackwoodpecker.zstack_test.zstack_test_image as zstack_image_header
            new_image = zstack_image_header.ZstackTestImage()
            new_image.set_creation_option(image_option)
            new_image.set_image(image)
            test_dict.add_image(new_image)

        elif next_action == TestAction.export_image:
            target_image = None
            if len(constant_path_list[0]) > 1:
                target_image_name = constant_path_list[0][1]
                image_list = test_dict.get_image_list()
                for image in image_list:
                    if image.get_image().name == target_image_name:
                        target_image = image
                        break

            if not target_image:
                test_util.test_fail("no resource available for next action: %s" % (next_action))

            target_image.export()

        elif next_action == TestAction.delete_image:
            target_image = None
            if len(constant_path_list[0]) > 1:
                target_image_name = constant_path_list[0][1]
                image_list = test_dict.get_image_list()
                for image in image_list:
                    if image.get_image().name == target_image_name:
                        target_image = image
                        break

            if not target_image:
                test_util.test_fail("no resource available for next action: %s" % (next_action))

            target_image.delete()
            test_dict.rm_image(target_image)

        elif next_action == TestAction.expunge_image:
            target_image = None
            if len(constant_path_list[0]) > 1:
                target_image_name = constant_path_list[0][1]
                image_list = test_dict.get_image_list()
                for image in image_list:
                    if image.get_image().name == target_image_name:
                        target_image = image
                        break

            if not target_image:
                test_util.test_fail("no resource available for next action: %s" % (next_action))
            bss = target_image.get_image().backupStorageRefs
            bs_uuid_list = []
            for bs in bss:
                bs_uuid_list.append(bs.backupStorageUuid)
            target_image.expunge(bs_uuid_list)
            test_dict.rm_image(target_image)

        elif next_action == TestAction.reclaim_space_from_bs:
            cond = res_ops.gen_query_conditions("status", '=', "Connected")
            cond = res_ops.gen_query_conditions("type", '=', "ImageStoreBackupStorage", cond)
            bss = res_ops.query_resource(res_ops.BACKUP_STORAGE, cond)
            import zstackwoodpecker.operations.backupstorage_operations as bs_ops
            if not bss:
                test_util.test_logger("not found enabled and imagestore bss")
            else:
                for bs in bss:
                    bs_ops.reclaim_space_from_bs(bs.uuid)

        elif next_action == TestAction.reconnect_bs:
            cond = res_ops.gen_query_conditions("status", '=', "Connected")
            bss = res_ops.query_resource(res_ops.BACKUP_STORAGE, cond)
            import zstackwoodpecker.operations.backupstorage_operations as bs_ops
            if not bss:
                test_util.test_fail("not found enabled bs")

            for bs in bss:
                bs_ops.reconnect_backup_storage(bs.uuid)

        elif next_action == TestAction.ps_migrage_vm:
            import zstackwoodpecker.operations.datamigrate_operations as datamigr_ops
            def _get_vm_ps_candidate(vm_uuid):
                ps_to_migrate = random.choice(datamigr_ops.get_ps_candidate_for_vm_migration(vm_uuid))
                return ps_to_migrate

            target_vm = None
            if len(constant_path_list[0]) > 1:
                target_vm_name = constant_path_list[0][1]
                all_vm_list = test_dict.get_all_vm_list()
                for vm in all_vm_list:
                    if vm.get_vm().name == target_vm_name:
                        target_vm = vm
                        break

            if not target_vm:
                test_util.test_fail("no resource available for next action: %s" % (next_action))

            target_vm_uuid = target_vm.get_vm().uuid
            ps_uuid_to_migrate = _get_vm_ps_candidate(target_vm_uuid).uuid
            datamigr_ops.ps_migrage_vm(ps_uuid_to_migrate, target_vm_uuid)

        elif next_action == TestAction.sync_image_from_imagestore:
            target_image = None
            if len(constant_path_list[0]) > 1:
                target_image_name = constant_path_list[0][1]
                image_list = test_dict.get_image_list()
                for image in image_list:
                    if image.get_image().name == target_image_name:
                        target_image = image
                        break

            if not target_image:
                test_util.test_fail("no resource available for next action: %s" % (next_action))

            image_uuid_local = target_image.get_image().uuid 
            local_bs_uuid = target_image.get_image().backupStorageRefs[0].backupStorageUuid
            disaster_bs_uuid = lib_get_another_imagestore_by_uuid(local_bs_uuid)
            import zstackwoodpecker.operations.image_operations as img_ops
            image_uuid = img_ops.sync_image_from_image_store_backup_storage(disaster_bs_uuid, local_bs_uuid, image_uuid_local)

        elif next_action == TestAction.create_vm_by_image:
            vm_name = None
            image_format = None
            target_image = None
            if len(constant_path_list[0]) > 3:
                target_image_name = constant_path_list[0][1]
                image_format = constant_path_list[0][2]
                vm_name = constant_path_list[0][3]
                image_list = test_dict.get_image_list()
                for image in image_list:
                    if image.get_image().name == target_image_name:
                        target_image = image
                        break

            if not target_image or not vm_name:
                test_util.test_fail("no resource available for next action: %s" % (next_action))

            vm_creation_option = test_util.VmOption()

            if image_format == "iso":
                root_disk_uuid = lib_get_disk_offering_by_name(os.environ.get('rootDiskOfferingName')).uuid
                vm_creation_option.set_instance_offering_uuid(root_disk_uuid)

            vm_creation_option.set_image_uuid(target_image.get_image().uuid)

            conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
            instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid
            vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)

            vm = lib_create_vm(vm_creation_option)
            test_dict.add_vm(vm)

        elif next_action == TestAction.create_vm_backup:
            backup_name = None
            target_vm = None
            if len(constant_path_list[0]) > 2:
                target_vm_name = constant_path_list[0][1]
                backup_name = constant_path_list[0][2]
                all_vm_list = test_dict.get_all_vm_list()
                for vm in all_vm_list:
                    if vm.get_vm().name == target_vm_name:
                        target_vm = vm
                        break

            if not target_vm or not backup_name:
                test_util.test_fail("no resource available for next action: %s" % (next_action))

            cond = res_ops.gen_query_conditions("type", '=', "ImageStoreBackupStorage")
            cond = res_ops.gen_query_conditions("name", '=', "only_for_robot_backup_test", cond)
            bss = res_ops.query_resource(res_ops.BACKUP_STORAGE, cond)
            if not bss:
                cond = res_ops.gen_query_conditions("type", '=', "ImageStoreBackupStorage")
                bss = res_ops.query_resource(res_ops.BACKUP_STORAGE, cond)
                if not bss:
                    cond = res_ops.gen_query_conditions("state", '=', "Enabled")
                    cond = res_ops.gen_query_conditions("status", '=', "Connected")
                    hosts = res_ops.query_resource(res_ops.HOST, cond)
                    if not hosts:
                        test_util.test_fail("No host available for adding imagestore for backup test")
                    host = hosts[0]
                    import zstackwoodpecker.operations.backupstorage_operations as bs_ops
                    bs_option = test_util.ImageStoreBackupStorageOption()
                    bs_option.set_name("only_for_robot_backup_test")
                    bs_option.set_url("/home/sftpBackupStorage")
                    bs_option.set_hostname(host.managementIp)
                    bs_option.set_password('password')
                    bs_option.set_sshPort(host.sshPort)
                    bs_option.set_username(host.username)
                    bs_inv = bs_ops.create_image_store_backup_storage(bs_option)
                
                    bs_ops.attach_backup_storage(bs_inv.uuid, host.zoneUuid)
                    bss = [bs_inv]
            bs = bss[0]
               
            backup_option = test_util.BackupOption()
            backup_option.set_name(backup_name)
            backup_option.set_volume_uuid(lib_get_root_volume(vm.get_vm()).uuid)
            backup_option.set_backupStorage_uuid(bs.uuid)
            test_util.test_dsc('Robot Action: %s; on Volume: %s' % \
                (next_action, target_vm.get_vm().uuid))

            backups = vm_ops.create_vm_backup(backup_option)
            for backup in backups:
                test_dict.add_backup(backup.uuid)
                for volume in test_dict.get_all_volume_list():
                    if backup.volumeUuid == volume.get_volume().uuid:
                        md5sum = volume.get_md5sum()
                        test_dict.add_backup_md5sum(backup.uuid, md5sum)

        elif next_action == TestAction.use_vm_backup:
            target_backup = None
            backup_name = None
            if len(constant_path_list[0]) > 1:
                backup_name = constant_path_list[0][1]
                backup_list = test_dict.get_backup_list()
                for backup_uuid in backup_list:
                    backup = lib_get_backup_by_uuid(backup_uuid)
                    if backup.name == backup_name:
                        target_backup = backup
                        break

            if not target_backup or not backup_name:
                test_util.test_fail("no resource available for next action: %s" % (next_action))
            import zstackwoodpecker.operations.volume_operations as vol_ops
            test_util.test_dsc('Robot Action: %s; on Backup: %s' % \
                (next_action, target_backup.uuid))

            #_update_bs_for_robot_state("enable")
            vol_ops.revert_vm_from_backup(target_backup.groupUuid)
            cond = res_ops.gen_query_conditions("groupUuid", '=', target_backup.groupUuid)
            backups = res_ops.query_resource(res_ops.VOLUME_BACKUP, cond)
            #_update_bs_for_robot_state("disable")
            for backup in backups:
                for volume in test_dict.get_all_volume_list():
                    volume.update()
                    volume.update_volume()
                    if backup.volumeUuid == volume.get_volume().uuid:
                        md5sum = test_dict.get_backup_md5sum(backup.uuid)
                        volume.set_md5sum(md5sum)

        elif next_action == TestAction.clone_vm:
            target_vm = None
            vm_name = None
            full = False
            target_snapshots = None
            (normal_args, extra_args) = _parse_args(constant_path_list[0])
            if len(normal_args) > 2:
                target_vm_name = normal_args[1]
                vm_name = normal_args[2]
                all_vm_list = test_dict.get_all_vm_list()
                for vm in all_vm_list:
                    if vm.get_vm().name == target_vm_name:
                        target_vm = vm
                        break

            if not target_vm or not vm_name:
                test_util.test_fail("no resource available for next action: %s" % (next_action))

            test_util.test_dsc('Robot Action: %s; on VM: %s' % \
                (next_action, target_vm.get_vm().uuid))
            for ea in extra_args:
                if ea == "full":
                    full = True

            new_vm = target_vm.clone([vm_name], full=full)[0]
            test_util.test_dsc('Robot Action Result: %s; new VM: %s'\
                    % (next_action, new_vm.get_vm().uuid))
            test_dict.add_vm(new_vm)
            for volume in test_dict.get_all_volume_list():
                volume.update()
                volume.update_volume()

            if full:
                target_volumes = target_vm.get_vm().allVolumes
            elif not full:
                target_volumes = [lib_get_root_volume(target_vm.get_vm())]

            for target_volume in target_volumes:
                snapshots = test_dict.get_volume_snapshot(target_volume.uuid)

                if test_dict.get_volume_snapshot(target_volume.uuid).get_current_snapshot():
                    target_snapshots = lib_get_child_snapshots(test_dict.get_volume_snapshot(target_volume.uuid).get_current_snapshot())

                    if target_snapshots:
                        for i in target_snapshots:
                            for sp in snapshots.get_primary_snapshots():
                                if i['inventory']['uuid'] == sp.get_snapshot().uuid:
                                    test_util.test_logger('%s is already in snapshot list dict, no need to add it' % (i['inventory']['uuid']))
                                    break
                                if sp == snapshots.get_primary_snapshots()[-1]:
                                    test_util.test_logger('%s is not in snapshot list dict, suppose it should be the new snapshot generated by auto' % (i['inventory']['uuid']))
                                    target_snapshot = i

                if not target_snapshots or not test_dict.get_volume_snapshot(target_volume.uuid).get_current_snapshot():
                    if lib_get_diff_snapshots_with_zs(test_dict, target_volume.uuid):
                        # Suppose only one new snapshot generated by one action for each volume
                        target_snapshot = lib_get_diff_snapshots_with_zs(test_dict, target_volume.uuid)[0]
                        test_util.test_logger('%s is not in snapshot list dict, suppose it should be the new snapshot generated by auto' % (target_snapshot['inventory']['uuid']))

                if not target_snapshot:
                    test_util.test_logger('No new snapshot found for volume %s, skip the snapshot tree update' % (target_volume.uuid))

                if target_snapshot:
                    cre_vm_opt = robot_test_obj.get_vm_creation_option()
                    cre_vm_opt.set_name("utility_vm_for_robot_test")
                    new_snapshot = lib_get_volume_snapshot_by_snapshot(snapshots, target_snapshot, robot_test_obj, test_dict, cre_vm_opt)

                    target_volume = new_snapshot.get_target_volume()
                    md5sum = target_volume.get_md5sum()
                    new_snapshot.set_md5sum(md5sum)

        else:
            test_util.test_fail("Robot action: <%s> not supported" %(next_action))

        constant_path_list.pop(0)
        robot_test_obj.set_constant_path_list(constant_path_list)


def lib_evaluate_path_execution(required_path, action_history):
    if not required_path or not action_history:
        return 0
    required_path_reverse = list(required_path)
    required_path_reverse.reverse()
    action_history_reverse = list(action_history)
    action_history_reverse.reverse()
    for offset in range(0, len(required_path)):
        if len(required_path)-offset > len(action_history):
            continue
        mismatch = False
        for index in range(0, len(required_path)-offset):
            if required_path_reverse[offset+index] != action_history_reverse[index]:
                mismatch = True
                break
        if mismatch:
            continue
        return len(required_path)-offset
            
    return 0


#TODO: add more action pickup strategy
def lib_robot_pickup_action(required_path, resource_list, action_list, pre_robot_actions, pre_resource_robot_actions, \
        priority_actions, selector_type):

    def _next_action_for_required_path(required_path, exec_len):
        return required_path[exec_len]

    test_util.test_logger('Action history: %s' % pre_robot_actions)
    test_util.test_logger('Resource Action history: %s' % pre_resource_robot_actions)
    test_util.test_logger('Required path: %s' % required_path)
    for key in pre_resource_robot_actions:
        test_util.test_logger('Required path exec len (%s): %s' % (key, lib_evaluate_path_execution(required_path, pre_resource_robot_actions[key])))

    if not selector_type:
        selector_type = action_select.default_strategy

    test_util.test_logger('resource_list: %s' % resource_list)
    action_selector = action_select.action_selector_table[selector_type]
    if selector_type == action_select.resource_path_strategy and pre_resource_robot_actions:
        history_len_dict = dict()
        required_path_exec_len_dict = dict()
        # default to select least resource history action
        for key in pre_resource_robot_actions:
            for res in resource_list:
                if key == res:
                    if required_path:
                        required_path_exec_len = lib_evaluate_path_execution(required_path, pre_resource_robot_actions[key])
                        next_action = _next_action_for_required_path(required_path, required_path_exec_len)
                        if next_action in action_list:
                            if required_path_exec_len_dict.has_key(required_path_exec_len):
                                required_path_exec_len_dict[required_path_exec_len] += key
                            else:
                                required_path_exec_len_dict[required_path_exec_len] = [ key ]
                    next_action = action_selector(action_list, pre_resource_robot_actions[key], priority_actions).select()
                    history_len = len(pre_resource_robot_actions[key])
                    if history_len_dict.has_key(history_len):
                        history_len_dict[history_len] += next_action
                    else:
                        history_len_dict[history_len] = [ next_action ]
        test_util.test_logger('Required path exec len dict: %s' % (required_path_exec_len_dict))
        if required_path_exec_len_dict:
            all_exec_len = required_path_exec_len_dict.keys()
            all_exec_len.sort(reverse=True)
            res = random.choice(required_path_exec_len_dict[all_exec_len[0]])
            next_action = _next_action_for_required_path(required_path, all_exec_len[0])
            return (next_action, True)
        if history_len_dict:
            all_history_len = history_len_dict.keys()
            all_history_len.sort()
            next_action = random.choice(history_len_dict[all_history_len[0]])
            return (next_action, False)
        else:
            return (action_selector(action_list, pre_robot_actions, \
                priority_actions).select(), False)
    else:
        return (action_selector(action_list, pre_robot_actions, \
            priority_actions).select(), False)

def lib_get_test_stub(suite_name=None):
    '''test_stub lib is not global test library. It is test suite level common
    lib. Test cases might be in different sub folders under test suite folder. 
    This function will help test case to find and load test_stub.py.'''
    import inspect
    import zstacklib.utils.component_loader as component_loader
    caller_info_list = inspect.getouterframes(inspect.currentframe())[1]
    caller_path = os.path.realpath(caller_info_list[1])
    curr_dir = os.path.dirname(caller_path)
    if suite_name:
        suite_path = '/'.join([os.path.dirname(curr_dir), suite_name])
    else:
        suite_path = curr_dir
    test_stub_cl = component_loader.ComponentLoader('test_stub', suite_path, 4)
    test_stub_cl.load()
    return test_stub_cl.module

#---------------------------------------------------------------
#Robot actions.
def lib_create_data_vol_template_from_volume(target_vm=None, vm_target_vol=None):
    import zstackwoodpecker.zstack_test.zstack_test_image as zstack_image_header
    if target_vm:
        vm_inv = target_vm.get_vm()

        backup_storage_uuid_list = lib_get_backup_storage_uuid_list_by_zone(vm_inv.zoneUuid)
        ps_uuid = lib_get_primary_storage_by_vm(vm_inv).uuid
    else:
        ps_uuid = vm_target_vol.primaryStorageUuid
        backup_storage_uuid_list = lib_get_backup_storage_uuid_list_by_zone(lib_get_primary_storage_by_uuid(ps_uuid).zoneUuid)

    bs_list = []
    for bsu in backup_storage_uuid_list:
        bs = lib_get_backup_storage_by_uuid(bsu)
        if bs.type == "Ceph":
            ps_list = lib_get_primary_storage_uuid_list_by_backup_storage(bsu)
            ps = lib_get_primary_storage_by_uuid(ps_uuid)
            if ps.uuid not in ps_list:
                continue
        bs_list.append(bsu)

    new_data_vol_inv = vol_ops.create_volume_template(vm_target_vol.uuid, \
            bs_list, \
            'vol_temp_for_volume_%s' % vm_target_vol.uuid)
    new_data_vol_temp = zstack_image_header.ZstackTestImage()
    new_data_vol_temp.set_image(new_data_vol_inv)
    new_data_vol_temp.set_state(image_header.CREATED)
    return new_data_vol_temp

def lib_create_volume_snapshot_from_volume(target_volume_snapshots, robot_test_obj, test_dict, cre_vm_opt=None, snapshot_name=None):
    vol_utiltiy_vm = None
    target_volume_inv = \
            target_volume_snapshots.get_target_volume().get_volume()
    ps_uuid = target_volume_inv.primaryStorageUuid
    ps = lib_get_primary_storage_by_uuid(ps_uuid)
    if target_volume_snapshots.get_utility_vm():
        vol_utiltiy_vm = target_volume_snapshots.get_utility_vm()
        if ps.type == inventory.LOCAL_STORAGE_TYPE:
            if vol_utiltiy_vm.get_vm().hostUuid != lib_get_local_storage_volume_host(target_volume_inv.uuid).uuid:
                vol_utiltiy_vm = None

    if not vol_utiltiy_vm:
        vol_utiltiy_vm = robot_test_obj.get_utility_vm(ps_uuid)
        if ps.type == inventory.LOCAL_STORAGE_TYPE:
            if vol_utiltiy_vm.get_vm().hostUuid != lib_get_local_storage_volume_host(target_volume_inv.uuid).uuid:
                vol_utiltiy_vm = None

    if not vol_utiltiy_vm:
        cond = res_ops.gen_query_conditions('name', '=', "utility_vm_for_robot_test")
        cond = res_ops.gen_query_conditions('state', '=', "Running", cond)
        vms = res_ops.query_resource(res_ops.VM_INSTANCE, cond)
        for vm in vms:
            if ps.type == inventory.LOCAL_STORAGE_TYPE:
                if ps_uuid == ps.uuid and vm.hostUuid == lib_get_local_storage_volume_host(target_volume_inv.uuid).uuid:
                    vol_utility_vm = vm
            else:
                if ps_uuid == ps.uuid:
                    vol_utility_vm = vm

    if not vol_utiltiy_vm:
        #create utiltiy_vm on given primary storage.
        util_vm_opt = test_util.VmOption(cre_vm_opt)
        instance_offering_uuid = util_vm_opt.get_instance_offering_uuid()
        if not instance_offering_uuid:
            instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING)[0].uuid
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
        util_vm_opt.set_ps_uuid(ps_uuid)
        #need to set host_uuid == target_volume host uuid if local ps,
        #  as there will attach testing for snapshot creation
        if lib_get_primary_storage_by_uuid(ps_uuid).type == inventory.LOCAL_STORAGE_TYPE:
            util_vm_opt.set_host_uuid(lib_get_local_storage_volume_host(target_volume_inv.uuid).uuid)

        vol_utiltiy_vm  = lib_create_vm(util_vm_opt)
        robot_test_obj.set_utility_vm(vol_utiltiy_vm)
        test_dict.add_utility_vm(vol_utiltiy_vm)
        vol_utiltiy_vm.check()
            
    target_volume_snapshots.set_utility_vm(vol_utiltiy_vm)

    return target_volume_snapshots.create_snapshot(snapshot_name)

def lib_get_volume_snapshot_by_snapshot(target_volume_snapshots, target_snapshot, robot_test_obj, test_dict, cre_vm_opt=None):
    vol_utiltiy_vm = None
    snapshot_name = None
    snapshot_uuid = None
    target_volume_inv = \
            target_volume_snapshots.get_target_volume().get_volume()
    ps_uuid = target_volume_inv.primaryStorageUuid
    ps = lib_get_primary_storage_by_uuid(ps_uuid)
    if target_volume_snapshots.get_utility_vm():
        vol_utiltiy_vm = target_volume_snapshots.get_utility_vm()
        if ps.type == inventory.LOCAL_STORAGE_TYPE:
            if vol_utiltiy_vm.get_vm().hostUuid != lib_get_local_storage_volume_host(target_volume_inv.uuid).uuid:
                vol_utiltiy_vm = None

    if not vol_utiltiy_vm:
        vol_utiltiy_vm = robot_test_obj.get_utility_vm(ps_uuid)
        if ps.type == inventory.LOCAL_STORAGE_TYPE:
            if vol_utiltiy_vm.get_vm().hostUuid != lib_get_local_storage_volume_host(target_volume_inv.uuid).uuid:
                vol_utiltiy_vm = None

    if not vol_utiltiy_vm:
        cond = res_ops.gen_query_conditions('name', '=', "utility_vm_for_robot_test")
        cond = res_ops.gen_query_conditions('state', '=', "Running", cond)
        vms = res_ops.query_resource(res_ops.VM_INSTANCE, cond)
        for vm in vms:
            if ps.type == inventory.LOCAL_STORAGE_TYPE:
                if ps_uuid == ps.uuid and vm.hostUuid == lib_get_local_storage_volume_host(target_volume_inv.uuid).uuid:
                    vol_utility_vm = vm
            else:
                if ps_uuid == ps.uuid:
                    vol_utility_vm = vm

    if not vol_utiltiy_vm:
        #create utiltiy_vm on given primary storage.
        util_vm_opt = test_util.VmOption(cre_vm_opt)
        instance_offering_uuid = util_vm_opt.get_instance_offering_uuid()
        if not instance_offering_uuid:
            instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING)[0].uuid
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
        util_vm_opt.set_ps_uuid(ps_uuid)
        #need to set host_uuid == target_volume host uuid if local ps,
        #  as there will attach testing for snapshot creation
        if lib_get_primary_storage_by_uuid(ps_uuid).type == inventory.LOCAL_STORAGE_TYPE:
            util_vm_opt.set_host_uuid(lib_get_local_storage_volume_host(target_volume_inv.uuid).uuid)

        vol_utiltiy_vm  = lib_create_vm(util_vm_opt)
        robot_test_obj.set_utility_vm(vol_utiltiy_vm)
        test_dict.add_utility_vm(vol_utiltiy_vm)
        vol_utiltiy_vm.check()
            
    target_volume_snapshots.set_utility_vm(vol_utiltiy_vm)

    snapshot_name = target_snapshot['inventory']['name']
    snapshot_uuid = target_snapshot['inventory']['uuid']
    return target_volume_snapshots.create_snapshot(name = snapshot_name, target_snapshot_uuid = snapshot_uuid)

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
    target_host_uuid = None
    #TODO: need to consider multiple local storage condition, since zs 1.0 only
    # support 1 local storage per host.
    ps_uuid = random.choice(ps_uuid_list)
    ps_inv = lib_get_primary_storage_by_uuid(ps_uuid)
    if ps_inv.type == inventory.LOCAL_STORAGE_TYPE:
        #local storage, need to assigne a host
        target_host_uuid = \
                random.choice(lib_find_hosts_by_ps_uuid(ps_uuid)).uuid

    new_volume = target_image.create_data_volume(ps_uuid, \
            'new_volume_from_template_%s' % target_image.get_image().uuid, \
            host_uuid = target_host_uuid)
    return new_volume 

#------- load balance related function
def lib_create_lb_listener_option(lbl_name = 'lb ssh test',\
        lbl_protocol = 'tcp', lbl_port = 22, lbi_port = 22, lb_uuid = None):
    '''
    Create common load balancer listener option. 
    '''
    lb_creation_option = test_util.LoadBalancerListenerOption()
    lb_creation_option.set_name(lbl_name)
    lb_creation_option.set_protocol(lbl_protocol)
    lb_creation_option.set_load_balancer_port(lbl_port)
    lb_creation_option.set_instance_port(lbi_port)
    lb_creation_option.set_load_balancer_uuid(lb_uuid)
    return lb_creation_option

#------- over provision function --------
def lib_set_provision_memory_rate(rate):
    return conf_ops.change_global_config('mevoco', 'overProvisioning.memory', rate)

def lib_get_provision_memory_rate():
    return conf_ops.get_global_config_value('mevoco', 'overProvisioning.memory')

def lib_set_provision_storage_rate(rate):
    return conf_ops.change_global_config('mevoco', 'overProvisioning.primaryStorage', rate)

#--------QOS related function ---------
def lib_limit_volume_total_iops(instance_offering_uuid, iops, \
        session_uuid = None):
    return tag_ops.create_system_tag('InstanceOfferingVO', \
            instance_offering_uuid, \
            '%s::%d' % (vm_header.VOLUME_IOPS, iops),\
            session_uuid)

def lib_limit_volume_bandwidth(instance_offering_uuid, bandwidth, \
        session_uuid = None):
    return tag_ops.create_system_tag('InstanceOfferingVO', \
            instance_offering_uuid, \
            '%s::%d' % (vm_header.VOLUME_BANDWIDTH, bandwidth),\
            session_uuid)

def lib_limit_read_bandwidth(instance_offering_uuid, bandwidth, \
        session_uuid = None):
    return tag_ops.create_system_tag('InstanceOfferingVO', \
            instance_offering_uuid, \
            '%s::%d' % (vm_header.READ_BANDWIDTH, bandwidth),\
            session_uuid)

def lib_limit_write_bandwidth(instance_offering_uuid, bandwidth, \
        session_uuid = None):
    return tag_ops.create_system_tag('InstanceOfferingVO', \
            instance_offering_uuid, \
            '%s::%d' % (vm_header.WRITE_BANDWIDTH, bandwidth),\
            session_uuid)

def lib_limit_volume_read_bandwidth(instance_offering_uuid, bandwidth, \
        session_uuid = None):
    return tag_ops.create_system_tag('DiskOfferingVO', \
            instance_offering_uuid, \
            '%s::%d' % (vm_header.READ_BANDWIDTH, bandwidth),\
            session_uuid)

def lib_limit_volume_write_bandwidth(instance_offering_uuid, bandwidth, \
        session_uuid = None):
    return tag_ops.create_system_tag('DiskOfferingVO', \
            instance_offering_uuid, \
            '%s::%d' % (vm_header.WRITE_BANDWIDTH, bandwidth),\
            session_uuid)

def lib_limit_vm_network_bandwidth(instance_offering_uuid, bandwidth, \
        outbound = True, session_uuid = None):
    if outbound:
        return tag_ops.create_system_tag('InstanceOfferingVO', \
                instance_offering_uuid, \
                '%s::%d' % (vm_header.NETWORK_OUTBOUND_BANDWIDTH, bandwidth),\
                session_uuid)
    else:
        return tag_ops.create_system_tag('InstanceOfferingVO', \
                instance_offering_uuid, \
                '%s::%d' % (vm_header.NETWORK_INBOUND_BANDWIDTH, bandwidth),\
                session_uuid)

#--------disk offering--------
def lib_limit_disk_bandwidth(disk_offering_uuid, bandwidth, \
        session_uuid = None):
    return tag_ops.create_system_tag('DiskOfferingVO', \
            disk_offering_uuid, \
            '%s::%d' % (vm_header.VOLUME_BANDWIDTH, bandwidth),\
            session_uuid)

def lib_create_disk_offering(diskSize = 1073741824, \
        name = 'new_disk_offering', volume_bandwidth = None,\
        read_bandwidth=None, write_bandwidth=None):
    new_offering_option = test_util.DiskOfferingOption()
    new_offering_option.set_diskSize(diskSize)
    new_offering_option.set_name(name)
    new_offering = vol_ops.create_volume_offering(new_offering_option)
    if volume_bandwidth:
        lib_limit_disk_bandwidth(new_offering.uuid, volume_bandwidth)
    if read_bandwidth:
        lib_limit_volume_read_bandwidth(new_offering.uuid, read_bandwidth)
    if write_bandwidth:
        lib_limit_volume_write_bandwidth(new_offering.uuid, write_bandwidth)
    return new_offering


#--------instance offering--------
#def lib_create_instance_offering(cpuNum = 1, cpuSpeed = 16, \
def lib_create_instance_offering(cpuNum = 1, \
        memorySize = 536870912, name = 'new_instance', \
        volume_iops = None, volume_bandwidth = None, read_bandwidth=None, write_bandwidth=None, \
        net_outbound_bandwidth = None, net_inbound_bandwidth = None):
    new_offering_option = test_util.InstanceOfferingOption()
    new_offering_option.set_cpuNum(cpuNum)
    #new_offering_option.set_cpuSpeed(cpuSpeed)
    new_offering_option.set_memorySize(memorySize)
    new_offering_option.set_name(name)
    new_offering = vm_ops.create_instance_offering(new_offering_option)
    if volume_iops:
        lib_limit_volume_total_iops(new_offering.uuid, volume_iops)
    if volume_bandwidth:
        lib_limit_volume_bandwidth(new_offering.uuid, volume_bandwidth)
    if read_bandwidth:
        lib_limit_read_bandwidth(new_offering.uuid, read_bandwidth)
    if write_bandwidth:
        lib_limit_write_bandwidth(new_offering.uuid, write_bandwidth)
    if net_outbound_bandwidth:
        lib_limit_vm_network_bandwidth(new_offering.uuid, net_outbound_bandwidth, outbound = True)
    if net_inbound_bandwidth:
        lib_limit_vm_network_bandwidth(new_offering.uuid, net_inbound_bandwidth, outbound = False)
    return new_offering

def lib_get_reserved_memory():
    return conf_ops.get_global_config_value('kvm', 'reservedMemory')

def lib_set_reserved_memory(value):
    return conf_ops.change_global_config('kvm', 'reservedMemory', value)

def lib_get_active_host_number():
    cond = res_ops.gen_query_conditions('state', '=', 'Enabled')
    cond = res_ops.gen_query_conditions('status', '=', 'Connected', cond)
    result = res_ops.query_resource_count(res_ops.HOST, cond)
    return result

def lib_get_delete_policy(category = 'vm'):
    '''
    category could be vm, volume, image.
    '''
    return conf_ops.get_global_config_value(category, 'deletionPolicy')

def lib_get_vm_delete_policy():
    return lib_get_delete_policy()

def lib_get_volume_delete_policy():
    return lib_get_delete_policy('volume')

def lib_get_image_delete_policy():
    return lib_get_delete_policy('image')

def lib_set_delete_policy(category = 'vm', value = 'Direct'):
    '''
    value could be Direct, Delay, Never
    category could be vm, image, volume
    '''
    return conf_ops.change_global_config(category, 'deletionPolicy', value)

def lib_set_expunge_time(category = 'vm', value = 1):
    '''
    value could be 1~N
    category could be vm, image, volume
    '''
    return conf_ops.change_global_config(category, 'expungePeriod', value)

def lib_get_expunge_time(category = 'vm'):
    '''
    category could be vm, volume, image.
    '''
    return conf_ops.get_global_config_value(category, 'expungePeriod')

def lib_update_test_state_object_delete_policy(category, policy, \
        test_state_object):
    '''
    category could be vm, volume, image.
    policy could be DIRECT, DELAY, NEVER
    test_state_object is test_state.TestStageDict
    '''
    lib_set_delete_policy(category = category, value = policy)
    if category == 'vm':
        test_state_object.update_vm_delete_policy(policy)
    elif category == 'volume':
        test_stage_object.update_volume_delete_policy(policy)
    elif category == 'image':
        test_stage_object.update_image_delete_policy(policy)
    else:
        test_util.test_fail('Category can only be vm, volume or image. But your input is: %s'% category)
    test_util.test_logger('%s delete policy has been changed to %s' % \
            (category, policy))

def lib_update_test_state_object_delete_delay_time(category, \
        delay_time, test_state_object):
    '''
    category could be vm, volume, image.
    delete_delay_time is an int value for seconds.
    test_state_object is test_state.TestStageDict
    '''
    lib_set_expunge_time(category = category, value = delay_time)
    if category == 'vm':
        test_state_object.update_vm_delete_delay_time(delay_time)
    elif category == 'volume':
        test_state_object.update_volume_delete_delay_time(delay_time)
    elif category == 'image':
        test_state_object.update_image_delete_delay_time(delay_time)
    else:
        test_util.test_fail('Category can only be vm, volume or image. But your input is: %s'% category)
    test_util.test_logger('%s delete delay time has been changed to \
%s' % (category, policy))

def lib_get_local_storage_reference_information(volume_uuid):
    cond = res_ops.gen_query_conditions('volume.uuid', '=', volume_uuid)
    ls_ref = res_ops.query_resource(res_ops.LOCAL_STORAGE_RESOURCE_REF, cond)
    return ls_ref

def lib_get_local_storage_volume_host(volume_uuid):
    ls_ref = lib_get_local_storage_reference_information(volume_uuid)
    if ls_ref:
        host_uuid = ls_ref[0].hostUuid
        cond = res_ops.gen_query_conditions('uuid', '=', host_uuid)
        return res_ops.query_resource(res_ops.HOST, cond)[0]

def lib_get_image_store_backup_storage():
    for zone in res_ops.query_resource(res_ops.ZONE):
        for bs_uuid in lib_get_backup_storage_uuid_list_by_zone(zone.uuid):
            bs = lib_get_backup_storage_by_uuid(bs_uuid)
            if bs.type == inventory.IMAGE_STORE_BACKUP_STORAGE_TYPE:
                return bs

def lib_request_console_access(vm_uuid, session_uuid=None):
    return cons_ops.request_console_access(vm_uuid, session_uuid)

def lib_get_vm_console_address(vm_uuid, session_uuid=None):
    return cons_ops.get_vm_console_address(vm_uuid, session_uuid)

def lib_set_vm_console_password(vm_uuid, console_password, session_uuid=None):
    return cons_ops.set_vm_console_password(vm_uuid, console_password, session_uuid)

def lib_delete_vm_console_password(vm_uuid, session_uuid=None):
    return cons_ops.delete_vm_console_password(vm_uuid, session_uuid)

def lib_get_vm_console_password(vm_uuid, session_uuid=None):
    return cons_ops.get_vm_console_password(vm_uuid, session_uuid)

def lib_get_ha_enable():
    return conf_ops.get_global_config_value('ha', 'enable')

def lib_set_ha_enable(value):
    return conf_ops.change_global_config('ha', 'enable', value)

def lib_get_ha_selffencer_maxattempts():
    return conf_ops.get_global_config_value('ha', 'host.selfFencer.maxAttempts')

def lib_set_ha_selffencer_maxattempts(value):
    return conf_ops.change_global_config('ha', 'host.selfFencer.maxAttempts', value)

def lib_get_ha_selffencer_storagechecker_timeout():
    return conf_ops.get_global_config_value('ha', 'host.selfFencer.storageChecker.timeout')

def lib_set_ha_selffencer_storagechecker_timeout(value):
    return conf_ops.change_global_config('ha', 'host.selfFencer.storageChecker.timeout', value)

def lib_get_reserved_primary_storage():
    return conf_ops.get_global_config_value('primaryStrorage', 'reservedCapacity')

def lib_set_primary_storage_imagecache_gc_interval(value):
    return conf_ops.change_global_config('primaryStorage', 'imageCache.garbageCollector.interval', value)

def lib_set_allow_live_migration_local_storage(value):
    return conf_ops.change_global_config('localStoragePrimaryStorage', 'liveMigrationWithStorage.allow', value)

def lib_add_vm_sshkey(vm_uuid, sshkey, session_uuid = None):
    return tag_ops.create_system_tag('VmInstanceVO', \
            vm_uuid, \
            '%s::%s' % (vm_header.SSHKEY, sshkey),\
            session_uuid)

def lib_get_local_management_server_log_path():
    return shell.call('zstack-ctl status | grep "log file:" | awk \'{print $3}\'')

def lib_get_remote_management_server_log_path(node_ip, node_username, node_password):
    cmd = 'zstack-ctl status | grep "log file:" | awk \'{print $3}\''
    return lib_execute_ssh_cmd(node_ip, node_username, node_password, cmd, 180)

def lib_get_local_management_server_log():
    return shell.call('cat %s' % (lib_get_local_management_server_log_path()))

def lib_set_vm_numa(value):
    return conf_ops.change_global_config('vm', 'numa', value)

def lib_get_vm_numa():
    return conf_ops.get_global_config_value('vm', 'numa')

def lib_find_in_local_management_server_log(timestamp, *keywords):
    datetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
    cmd = 'grep "%s" %s' % (datetime, lib_get_local_management_server_log_path().strip())
    try:
        out = shell.call(cmd)
    except:
        return False

    for line in out.splitlines():
        line_match = True
        for keyword in keywords:
            if line.find(keyword) < 0:
                line_match = False
                break
        if line_match:
            return True
        
    return False

def lib_count_in_local_management_server_log(timestamp, *keywords):
    datetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
    cmd = 'grep "%s" %s' % (datetime, lib_get_local_management_server_log_path().strip())
    try:
        out = shell.call(cmd)
    except:
        return 0
    match = 0
    for line in out.splitlines():
        line_match = True
        for keyword in keywords:
            if line.find(keyword) < 0:
                line_match = False
                break
        if line_match:
            match += 1
        
    return match

def lib_find_in_remote_management_server_log(node_ip, node_username, node_password, timestamp, *keywords):
    datetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
    if lib_get_remote_management_server_log_path(node_ip, node_username, node_password) == False:
        return False
    else:
        cmd = 'grep "%s" %s | cat' % (datetime, lib_get_remote_management_server_log_path(node_ip, node_username, node_password).strip())
    try:
        out = lib_execute_ssh_cmd(node_ip, node_username, node_password, cmd, 180)
    except:
        return False

    for line in out.splitlines():
        line_match = True
        for keyword in keywords:
            if line.find(keyword) < 0:
                line_match = False
                break
        if line_match:
            return True
        
    return False

#def lib_update_instance_offering(offering_uuid, cpuNum = None, cpuSpeed = None, \
def lib_update_instance_offering(offering_uuid, cpuNum = None, \
        memorySize = None, name = None, \
        volume_iops = None, volume_bandwidth = None, \
        net_outbound_bandwidth = None, net_inbound_bandwidth = None):

    systemTags = None
    updated_offering_option = test_util.InstanceOfferingOption()
    if cpuNum:
        updated_offering_option.set_cpuNum(cpuNum)
    #if cpuSpeed:
    #    updated_offering_option.set_cpuSpeed(cpuSpeed)
    if memorySize:
        updated_offering_option.set_memorySize(memorySize)
    if name:
        updated_offering_option.set_name(name)
    if volume_iops:
        systemTags += "volumeTotalIops::%d," %(volume_iops)
    if volume_bandwidth:
        systemTags += "volumeTotalIops::%d," %(volume_bandwidth)
    if net_outbound_bandwidth:
        systemTags += "volumeTotalIops::%d," %(net_outbound_bandwidth)
    if net_inbound_bandwidth:
        systemTags += "volumeTotalIops::%d," %(net_inbound_bandwidth)

    if systemTags:
        systemTags = systemTags.rstrip(',')

    return vm_ops.update_instance_offering(updated_offering_option, offering_uuid, systemTags)

version_is_mevoco = None
def lib_check_version_is_mevoco():
    global version_is_mevoco
    if version_is_mevoco != None:
        return version_is_mevoco

    try:
        lic_ops.get_license_info()
	version_is_mevoco = True
    except:
        version_is_mevoco = False
    return version_is_mevoco

version_is_mevoco_1_8 = None
def lib_check_version_is_mevoco_1_8():
    global version_is_mevoco_1_8
    if version_is_mevoco_1_8 != None:
        return version_is_mevoco_1_8

    if shell.call('zstack-ctl status').find('version: 1.8') >= 0:
	version_is_mevoco_1_8 = True
    else:
        version_is_mevoco_1_8 = False
    return version_is_mevoco_1_8


def lib_get_host_cpu_prometheus_data(mn_ip, end_time, interval, host_uuid):
    cmd = '/usr/bin/zstack-cli LogInByAccount accountName=admin password=password'
    if not lib_execute_ssh_cmd(mn_ip, 'root', 'password', cmd):
        test_util.test_fail('zstack-cli login failed')

    cmd = """/usr/bin/zstack-cli PrometheusQueryPassThrough endTime=%s relativeTime=%s expression='collectd:collectd_cpu_percent{hostUuid=\\"%s\\",type=\\"user\\"}'""" % (end_time, interval, host_uuid)
    rsp = lib_execute_ssh_cmd(mn_ip, 'root', 'password', cmd)
    if not rsp:
        test_util.test_fail('%s failed' % (cmd))
    return rsp

def lib_get_file_size(host, file_path):
    command = "du -sb %s | awk '{print $1}'" % file_path
    eout = ''
    try:
        if host.sshPort != None:
            (ret, out, eout) = ssh.execute(command, host.managementIp, host.username, host.password, port=int(host.sshPort))
	else:
            (ret, out, eout) = ssh.execute(command, host.managementIp, host.username, host.password)
        test_util.test_logger('[file:] %s was found in [host:] %s' % (file_path, host.managementIp))
        return out
    except:
        #traceback.print_exc(file=sys.stdout)
        test_util.test_logger('Fail to execute: ssh [host:] %s with [username:] %s and [password:] %s to get size of [file:] %s . This might be expected behavior.'% (host.managementIp, host.username, host.password, file_path))
        test_util.test_logger('ssh execution stderr output: %s' % eout)
        test_util.test_logger(linux.get_exception_stacktrace())
        return 0

def ip2num(ip):
    ip=[int(x) for x in ip.split('.')]
    return ip[0] <<24 | ip[1]<<16 | ip[2]<<8 |ip[3]

def num2ip(num):
    return '%s.%s.%s.%s' %( (num & 0xff000000) >>24,
                            (num & 0x00ff0000) >>16,
                            (num & 0x0000ff00) >>8,
                            num & 0x000000ff )

def get_ip(start_ip, end_ip):
    start = ip2num(start_ip)
    end = ip2num(end_ip)
    return [ num2ip(num) for num in range(start, end+1) if num & 0xff ]


def skip_test_when_ps_include_local():
    ps_list = res_ops.query_resource(res_ops.PRIMARY_STORAGE)
    for ps in ps_list:
        if ps.type == inventory.LOCAL_STORAGE_TYPE:
            test_util.test_skip("The test is not support local storage.")

def skip_test_when_ps_type_not_in_list(allow_ps_list):
    ps_list = res_ops.query_resource(res_ops.PRIMARY_STORAGE)
    for ps in ps_list:
        if ps.type not in allow_ps_list:
            test_util.test_skip("%s is not in %s." %(ps.type, allow_ps_list))

def skip_test_when_bs_type_not_in_list(allow_bs_list):
    bs_list = res_ops.query_resource(res_ops.BACKUP_STORAGE)
    for bs in bs_list:
        if bs.type not in allow_bs_list:
            test_util.test_skip("%s is not in %s." %(bs.type, allow_bs_list))

def skip_test_if_any_ps_not_deployed(must_ps_list):
    ps_type_list = res_ops.query_resource_fields(res_ops.PRIMARY_STORAGE, [], None, ['type'])
    ps_list = []
    for ps in ps_type_list:
        ps_list.append(ps.type)

    for ps in must_ps_list:
        if ps in ps_list:
            continue
        else:
            test_util.test_skip("%s has not been deployed." %(ps))

def clean_up_all_vr():
    cond = res_ops.gen_query_conditions('type', '=', 'ApplianceVm')
    vr_list = res_ops.query_resource_fields(res_ops.VM_INSTANCE, cond, None, ['uuid'])
    for vr in vr_list:
        vm_ops.destroy_vm(vr.uuid)

def ensure_recover_script_l2_correct():
    if scenario_config_path != None and scenario_file_path != None and os.path.exists(scenario_file_path):
        host_recover_script = os.environ.get('hostRecoverScript')
        os.system("sed -i 's/eth/zsn/g' %s" % (host_recover_script))

def ver_ge_zstack_2_0(mn_ip):
    if int(os.system("sshpass -p password ssh root@%s \"zstack-ctl status|tail -n 1|grep '2.'\"" %(mn_ip))) == 0:
        return True
    else:
        return False

def lib_is_storage_network_separate():
    if all_scenario_config == None or scenario_file == None or not os.path.exists(scenario_file):
        test_util.test_logger("Not found scenario config or scenario file is not named or not generated")
        return False
    for host in xmlobject.safe_list(all_scenario_config.deployerConfig.hosts.host):
        for vm in xmlobject.safe_list(host.vms.vm):
            for l3Network in xmlobject.safe_list(vm.l3Networks.l3Network):
                if xmlobject.has_element(l3Network, 'primaryStorageRef'): 
                    return True
    return False

def lib_cur_env_is_not_scenario():
    if all_scenario_config == None or scenario_file == None or not os.path.exists(scenario_file):
        test_util.test_skip("Not found scenario config or scenario file is not named or not generated")

def lib_skip_if_ps_num_is_not_eq_number(number):
    ps_list = res_ops.query_resource(res_ops.PRIMARY_STORAGE)
    if len(ps_list) != number:
        test_util.test_skip("The expected ps number is %s VS. actual is %s." %(str(number), str(len(ps_list))))


def lib_cur_cfg_is_a_and_b(tst_cfg_lst, sce_xml_lst):
    '''
        This function helps to filter out the current test config and scenario config
        is one of the combination.
        @tst_cfg_lst: list type, test configure list, like a
        @sce_xml_lst: list tyoe, scenario configure list, like b
    '''
    for tst_cfg in tst_cfg_lst:
        if tst_cfg == os.path.basename(os.environ.get('WOODPECKER_TEST_CONFIG_FILE')).strip():
            for sce_xml in sce_xml_lst:
                if sce_xml == os.path.basename(os.environ.get('WOODPECKER_SCENARIO_CONFIG_FILE')).strip():
                    return True
    return False


@contextmanager
def ignored(*exceptions):
    try:
        yield
    except exceptions:
        pass


@contextmanager
def expected_failure(msg, *exceptions):
    try:
        yield
    except exceptions:
        test_util.test_logger("Expected failure: {}".format(msg))
    else:
        test_util.test_fail("CRITICAL ERROR: {} succeed!".format(msg))


def pre_execution_action(func):
    def decorator(test_method):
        @functools.wraps(test_method)
        def wrapper():
            with ignored(Exception):
                func()
            return test_method()
        return wrapper
    return decorator


def deprecated_case(test_method):
    @functools.wraps(test_method)
    def wrapper():
        test_util.test_skip("deprecated case, Skip execution,"
                            "Will be removed in some day")
    return wrapper


def skip_if(condition):
    assert isinstance(condition, bool)

    def decorator(test_method):
        @functools.wraps(test_method)
        def wrapper():
            if condition:
                test_util.test_skip('Skip test excution as meet some criterias')
            return test_method()
        return wrapper
    return decorator


def disable_checker(self):
    '''
    disable checker to Skip checker if meet some user defined criteria
    to debug or speed up test running
    '''
    try:
        getattr(self, "check")
    except AttributeError:
        test_util.test_warn("Fail to get check attribute")
        return self
    self.check = do_nothing
    return self


def do_nothing():
    pass


class DefaultFalseDict(defaultdict):
    def __init__(self, **kwargs):
        super(DefaultFalseDict, self).__init__(lambda:False, **kwargs)

def check_vcenter_host(ip):
    test = 0
    old_url, new_url = '', ''
    result = lib_execute_ssh_cmd(ip,"root","password","ls vmfs/volumes")
    '''for example:
	5a609b8c-9ec41a7c-2b90-fa3c0c711b00
	5a609b96-cd1e9698-8316-fa3c0c711b00 
	5aefdca7-51326905-a5a5-fa80a82b9900 (datastore url)  
	627adf75-dfb4ef0f-0649-19b4b53f5af3  
	a0b9e87d-eb910865-4905-b555b6619b12
	newdatastore
    '''
    if result != False: old_url = result.split('\n')[2]
    while test < 5:
        command = "source etc/rc.local.d/local.sh"
        _result = lib_execute_ssh_cmd(ip,"root","password", command)
        test += 1
        time.sleep(1)
        lib_execute_ssh_cmd(ip,"root","password","esxcli storage filesystem rescan")
        result = lib_execute_ssh_cmd(ip,"root","password","ls vmfs/volumes")
        if result != False: new_url = result.split('\n')[2]
        if old_url != new_url:
            command = "sed -i '/newdatastore/d' etc/rc.local.d/local.sh"
	    _result = lib_execute_ssh_cmd(ip,"root","password", command)
            return
    test_util.test_logger("The esxi host: %s checks faild" % ip)

def lib_check_pid(pid_name):
    '''
    Check if process is alive.
    '''

    try:
        out = shell.call('ps -ef | grep -v "grep" | grep %s' % pid_name)
    except:
        test_util.test_logger('no process %s found' % pid_name)
        return False

    if out.find(pid_name) >= 0:
        test_util.test_logger('process %s is up' % pid_name)
        return True
    else:
        test_util.test_logger('process %s is not up' % pid_name)
        return False
