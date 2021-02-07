'''

@author: MengLai
'''
import os
import tempfile
import uuid
import time

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.console_operations as cons_ops
import zstackwoodpecker.operations.scenario_operations as sce_ops
import zstacklib.utils.ssh as ssh

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
tmp_file = '/tmp/%s' % uuid.uuid1().get_hex()
zstack_management_ip = os.environ.get('zstackManagementIp')
vm_inv = None

#def create_vm(image):
#    l3_name = os.environ.get('l3PublicNetworkName')
#    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
#    image_uuid = image.uuid
#    #vm_name = 'zs_install_%s' % image.name
#    vm_name = os.environ.get('vmName')
#    vm_instrance_offering_uuid = os.environ.get('instanceOfferingUuid')
#
#    vm_creation_option = test_util.VmOption()
#    vm_creation_option.set_instance_offering_uuid(vm_instrance_offering_uuid)
#    vm_creation_option.set_l3_uuids([l3_net_uuid])
#    vm_creation_option.set_image_uuid(image_uuid)
#    vm_creation_option.set_name(vm_name)
#    vm_inv = sce_ops.create_vm(zstack_management_ip, vm_creation_option)
#
#    return vm_inv

def check_installtion_path(ssh_cmd, ins_path):
    cmd = '%s "/usr/bin/zstack-ctl status" | grep ^ZSTACK_HOME | awk \'{print $2}\'' % ssh_cmd
    (process_result, zstack_home) = test_stub.execute_shell_in_process_stdout(cmd, tmp_file)
    if process_result != 0:
        test_util.test_fail('zstack-ctl status get ZSTACK_HOME failed')
    zstack_home = zstack_home[:-1]
    expect_path = "%s/apache-tomcat/webapps/zstack" % ins_path
    if zstack_home != expect_path:
        test_util.test_fail('Expected ZSTACK_HOME:%s, but actual ZSTACK_HOME: %s' % (expect_path, zstack_home))

    cmd = '%s "/usr/bin/zstack-ctl status" | grep ^zstack.properties | awk \'{print $2}\'' % ssh_cmd
    (process_result, properties_file) = test_stub.execute_shell_in_process_stdout(cmd, tmp_file)
    if process_result != 0:
        test_util.test_fail('zstack-ctl status get zstack.properties failed')
    properties_file = properties_file[:-1]
    expect_path = "%s/apache-tomcat/webapps/zstack/WEB-INF/classes/zstack.properties" % ins_path
    if properties_file != expect_path:
        test_util.test_fail('Expected zstack.properties path:%s, but actual zstack.properties path: %s' % (expect_path, properties_file))

    cmd = '%s "/usr/bin/zstack-ctl status" | grep ^log4j2.xml | awk \'{print $2}\'' % ssh_cmd
    (process_result, log4j2_file) = test_stub.execute_shell_in_process_stdout(cmd, tmp_file)
    if process_result != 0:
        test_util.test_fail('zstack-ctl status get log4j2.xml failed')
    log4j2_file = log4j2_file[:-1]
    expect_path = "%s/apache-tomcat/webapps/zstack/WEB-INF/classes/log4j2.xml" % ins_path
    if log4j2_file != expect_path:
        test_util.test_fail('Expected log4j2.xml path:%s, but actual log4j2.xml path: %s' % (expect_path, log4j2_file))

    cmd = '%s "/usr/bin/zstack-ctl status" | grep ^\'PID file\' | awk \'{print $3}\'' % ssh_cmd
    (process_result, pid_file) = test_stub.execute_shell_in_process_stdout(cmd, tmp_file)
    if process_result != 0:
        test_util.test_fail('zstack-ctl status get PID file failed')
    pid_file = pid_file[:-1]
    expect_path = "%s/management-server.pid" % ins_path
    if pid_file != expect_path:
        test_util.test_fail('Expected PID file path:%s, but actual PID file path: %s' % (expect_path, pid_file))

    cmd = '%s "/usr/bin/zstack-ctl status" | grep ^\'log file\' | awk \'{print $3}\'' % ssh_cmd
    (process_result, log_file) = test_stub.execute_shell_in_process_stdout(cmd, tmp_file)
    if process_result != 0:
        test_util.test_fail('zstack-ctl status get log file failed')
    log_file = log_file[:-1]
    expect_path = "%s/apache-tomcat/logs/management-server.log"  % ins_path 
    if log_file != expect_path:
        test_util.test_fail('Expected log file path:%s, but actual log file path: %s' % (expect_path, log_file))

def test():
    global vm_inv
    test_util.test_dsc('Create test vm to test zstack upgrade and re-install with -r.')

    #conditions = res_ops.gen_query_conditions('name', '=', os.environ.get('imageNameBase_10'))
    ##image = res_ops.query_resource(res_ops.IMAGE, conditions)[0]
    #image = sce_ops.query_resource(zstack_management_ip, res_ops.IMAGE, conditions)[0] 
    #vm_inv = create_vm(image)
    #time.sleep(60)
    #iso_path = os.environ.get('iso_path')
    #upgrade_script_path = os.environ.get('upgradeScript')


    image_name = os.environ.get('imageNameBase_10')
    iso_path = os.environ.get('iso_path')
    #iso_21_path = os.environ.get('iso_21_path')
    zstack_latest_version = os.environ.get('zstackLatestVersion')
    zstack_latest_path = os.environ.get('zstackLatestInstaller')
    vm_name = os.environ.get('vmName')
    upgrade_script_path = os.environ.get('upgradeScript')

    vm_inv = test_stub.create_vm_scenario(image_name, vm_name)
    time.sleep(100)
    #test_lib.lib_wait_target_up(vm_ip, 22)

    test_util.test_dsc('Install zstack with -o -r -I')
    vm_ip = vm_inv.vmNics[0].ip
    test_stub.make_ssh_no_password(vm_ip, tmp_file)
    test_util.test_dsc('Upgrade master iso')   
    test_stub.update_iso(vm_ip, tmp_file, iso_path, upgrade_script_path)

    target_file = '/root/zstack-all-in-one.bin'
    test_stub.prepare_test_env(vm_inv, target_file)
    ssh_cmd = 'ssh  -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm_ip
    args = "-o -r /home/zstack-test -I eth0"
    test_stub.execute_install_with_args(ssh_cmd, args, target_file, tmp_file)
    ins_path = "/home/zstack-test"
    check_installtion_path(ssh_cmd, ins_path)
    test_stub.check_installation(vm_ip, tmp_file)
    test_stub.stop_mn(vm_ip, tmp_file)
     
    #test_util.test_dsc('Upgrade zstack to latest') 
    #upgrade_target_file = '/root/zstack-upgrade-all-in-one.tgz' 
    #test_stub.prepare_test_env(vm_inv, upgrade_target_file)
    #test_stub.upgrade_zstack(vm_ip, upgrade_target_file, tmp_file) 
    ##check_installtion_path(ssh_cmd, ins_path)
    #test_stub.check_installation(vm_ip, tmp_file)

    test_util.test_dsc('Install zstack with default path')
    cmd= '%s "[ -e /usr/local/zstack ] && echo yes || echo no"' % ssh_cmd
    (process_result, cmd_stdout) = test_stub.execute_shell_in_process_stdout(cmd, tmp_file)
    if process_result != 0:
        test_util.test_fail('check /usr/local/zstack fail, cmd_stdout:%s' % cmd_stdout)
    cmd_stdout = cmd_stdout[:-1]   
    if cmd_stdout == "yes":
        cmd = '%s "rm -rf /usr/local/zstack"' % ssh_cmd
        (process_result, cmd_stdout) = test_stub.execute_shell_in_process_stdout(cmd, tmp_file)
        if process_result != 0:
            test_util.test_fail('delete /usr/local/zstack fail')
    args = "-D"
    test_stub.execute_install_with_args(ssh_cmd, args, target_file, tmp_file)
    ins_path = "/usr/local/zstack"
    check_installtion_path(ssh_cmd, ins_path)
    test_stub.check_installation(vm_ip, tmp_file)

    os.system('rm -f %s' % tmp_file)
    sce_ops.destroy_vm(zstack_management_ip, vm_inv.uuid)
    test_util.test_pass('Install ZStack with -R aliyun -r -I Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm_inv

    os.system('rm -f %s' % tmp_file)
    sce_ops.destroy_vm(zstack_management_ip, vm_inv.uuid)
    test_lib.lib_error_cleanup(test_obj_dict)
