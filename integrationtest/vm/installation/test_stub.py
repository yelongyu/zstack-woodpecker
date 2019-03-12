import os
import subprocess
import time

import zstacklib.utils.ssh as ssh
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as zstack_vm_header
import zstackwoodpecker.operations.scenario_operations as scen_ops
import zstackwoodpecker.operations.license_operations as lic_ops
import zstackwoodpecker.zstack_test.zstack_test_volume as zstack_volume_header
import zstackwoodpecker.test_state as test_state
import commands
from lib2to3.pgen2.token import STAR
from zstacklib.utils import shell
from collections import OrderedDict

zstack_management_ip = os.environ.get('zstackManagementIp')

def create_vlan_vm(image_name, l3_name=None, disk_offering_uuids=None):
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    if not l3_name:
        l3_name = os.environ.get('l3PublicNetworkName')

    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    return create_vm([l3_net_uuid], image_uuid, 'zs_install_%s' % image_name, \
            disk_offering_uuids)

def create_vm(l3_uuid_list, image_uuid, vm_name = None, \
        disk_offering_uuids = None, default_l3_uuid = None):
    vm_creation_option = test_util.VmOption()
    conditions = res_ops.gen_query_conditions('name', '=', os.environ.get('instanceOfferingName_m'))
    instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_l3_uuids(l3_uuid_list)
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_name(vm_name)
    vm_creation_option.set_data_disk_uuids(disk_offering_uuids)
    vm_creation_option.set_default_l3_uuid(default_l3_uuid)
    vm = zstack_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    return vm

#def create_vm_scenario(image_name, vm_name = None, host_name = None):
def create_vm_scenario(image_name, vm_name = None):
    #zstack_management_ip = test_lib.all_scenario_config.basicConfig.zstackManagementIp.text_
    vm_creation_option = test_util.VmOption()
    conditions = res_ops.gen_query_conditions('name', '=', os.environ.get('instanceOfferingName_m'))
    instance_offering_uuid = scen_ops.query_resource(zstack_management_ip, res_ops.INSTANCE_OFFERING, conditions).inventories[0].uuid
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    conditions = res_ops.gen_query_conditions('name', '=', 'public network')
    l3_uuid = scen_ops.query_resource(zstack_management_ip, res_ops.L3_NETWORK, conditions).inventories[0].uuid
    vm_creation_option.set_l3_uuids([l3_uuid])
    vm_creation_option.set_default_l3_uuid(l3_uuid)
    conditions = res_ops.gen_query_conditions('name', '=', image_name)
    image_uuid = scen_ops.query_resource(zstack_management_ip, res_ops.IMAGE, conditions).inventories[0].uuid
    #conditions = res_ops.gen_query_conditions('name', '=', host_name)
    #host_uuid = scen_ops.query_resource(zstack_management_ip, res_ops.HOST, conditions).inventories[0].uuid
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_name(vm_name)
    #vm_creation_option.set_host_uuid(host_name)
    return scen_ops.create_vm(zstack_management_ip, vm_creation_option)

def destroy_vm_scenario(vm_uuid):
    #zstack_management_ip = test_lib.all_scenario_config.basicConfig.zstackManagementIp.text_
    scen_ops.destroy_vm(zstack_management_ip, vm_uuid)

def create_instance_vm(image_name, instance_offering_uuid, l3_name=None, disk_offering_uuids = None, default_l3_uuid = None):
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    if not l3_name:
        l3_name = os.environ.get('l3PublicNetworkName')

    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    vm_name = 'zs_install_%s' % image_name

    vm_creation_option = test_util.VmOption()
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_l3_uuids([l3_net_uuid])
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_name(vm_name)
    vm_creation_option.set_data_disk_uuids(disk_offering_uuids)
    vm_creation_option.set_default_l3_uuid(default_l3_uuid)
    vm = zstack_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    return vm

def check_str(string):
    if string == None:
        return ""
    return string

def execute_shell_in_process(cmd, tmp_file, timeout = 3600, no_timeout_excep = False):
    logfd = open(tmp_file, 'w', 0)
    process = subprocess.Popen(cmd, executable='/bin/sh', shell=True, stdout=logfd, stderr=logfd, universal_newlines=True)

    start_time = time.time()
    while process.poll() is None:
        curr_time = time.time()
        test_time = curr_time - start_time
        if test_time > timeout:
            process.kill()
            logfd.close()
            logfd = open(tmp_file, 'r')
            test_util.test_logger('[shell:] %s [timeout logs:] %s' % (cmd, '\n'.join(logfd.readlines())))
            logfd.close()
            if no_timeout_excep:
                test_util.test_logger('[shell:] %s timeout, after %d seconds' % (cmd, test_time))
                return 1
            else:
                os.system('rm -f %s' % tmp_file)
                test_util.test_fail('[shell:] %s timeout, after %d seconds' % (cmd, timeout))
        if test_time%10 == 0:
            print('shell script used: %ds' % int(test_time))
        time.sleep(1)
    logfd.close()
    logfd = open(tmp_file, 'r')
    test_util.test_logger('[shell:] %s [logs]: %s' % (cmd, '\n'.join(logfd.readlines())))
    logfd.close()
    return process.returncode

def execute_shell_in_process_stdout(cmd, tmp_file, timeout = 3600, no_timeout_excep = False):
    logfd = open(tmp_file, 'w', 0)
    process = subprocess.Popen(cmd, executable='/bin/sh', shell=True, stdout=logfd, universal_newlines=True)

    start_time = time.time()
    while process.poll() is None:
        curr_time = time.time()
        test_time = curr_time - start_time
        if test_time > timeout:
            process.kill()
            logfd.close()
            logfd = open(tmp_file, 'r')
            test_util.test_logger('[shell:] %s [timeout logs:] %s' % (cmd, '\n'.join(logfd.readlines())))
            logfd.close()
            if no_timeout_excep:
                test_util.test_logger('[shell:] %s timeout, after %d seconds' % (cmd, test_time))
                return 1
            else:
                os.system('rm -f %s' % tmp_file)
                test_util.test_fail('[shell:] %s timeout, after %d seconds' % (cmd, timeout))
        if test_time%10 == 0:
            print('shell script used: %ds' % int(test_time))
        time.sleep(1)
    logfd.close()
    logfd = open(tmp_file, 'r')
    stdout = '\n'.join(logfd.readlines())
    logfd.close()
    test_util.test_logger('[shell:] %s [logs]: %s' % (cmd, stdout))
    return (process.returncode, stdout)

def scp_file_to_vm(vm_ip, src_file, target_file):
    vm_username = os.environ['imageUsername']
    vm_password = os.environ['imagePassword']
    ssh.scp_file(src_file, target_file, vm_ip, vm_username, vm_password)

def copy_id_dsa(vm_ip, ssh_cmd, tmp_file):
    src_file = '/root/.ssh/id_dsa'
    target_file = '/root/.ssh/id_dsa'
    if not os.path.exists(src_file):
        os.system("ssh-keygen -t dsa -N '' -f %s" % src_file)

    scp_file_to_vm(vm_ip, src_file, target_file)
    cmd = '%s "chmod 600 /root/.ssh/id_dsa"' % ssh_cmd
    process_result = execute_shell_in_process(cmd, tmp_file)

def copy_id_dsa_pub(vm_ip):
    src_file = '/root/.ssh/id_dsa.pub'
    target_file = '/root/.ssh/authorized_keys'
    if not os.path.exists(src_file):
        os.system("ssh-keygen -t dsa -N '' -f %s" % src_file)
    scp_file_to_vm(vm_ip, src_file, target_file)

def make_ssh_no_password(vm_ip, tmp_file):
    ssh_cmd = 'ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm_ip
    ssh.make_ssh_no_password(vm_ip, os.environ['imageUsername'], os.environ['imagePassword'])
    copy_id_dsa(vm_ip, ssh_cmd, tmp_file)
    copy_id_dsa_pub(vm_ip)
def update_mn_hostname(vm_ip, tmp_file):
    ssh_cmd = 'ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm_ip
    cmd = '%s "hostnamectl set-hostname zs-test" ' % ssh_cmd
    process_result = execute_shell_in_process(cmd, tmp_file)

def update_console_ip(vm_ip, tmp_file):
    ssh_cmd = 'ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm_ip
    cmd = '%s "zstack-ctl configure consoleProxyOverriddenIp=%s" ' % (ssh_cmd, vm_ip)
    process_result = execute_shell_in_process(cmd, tmp_file)

def change_root_mysql_password(vm_ip, tmp_file):
    ssh_cmd = 'ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm_ip
    cmd = '%s " zstack-ctl change_mysql_password --user-name root --new-password  zstack.123 --root-password zstack.mysql.password" ' % ssh_cmd
    process_result = execute_shell_in_process(cmd, tmp_file)

def change_mysql_password(vm_ip, tmp_file):
    ssh_cmd = 'ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm_ip
    cmd = '%s " zstack-ctl change_mysql_password --user-name zstack --new-password  zstack.123 --root-password zstack.mysql.password" ' % ssh_cmd
    process_result = execute_shell_in_process(cmd, tmp_file)

def update_zstack_mysql_password(vm_ip, tmp_file):
    ssh_cmd = 'ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm_ip
    cmd = '''%s 'sed -i "s/zstack.password/zstack.123/g" /usr/local/zstack/apache-tomcat/webapps/zstack/WEB-INF/classes/zstack.properties' ''' % ssh_cmd 
    process_result = execute_shell_in_process(cmd, tmp_file)
    if process_result != 0:
        test_util.test_fail('update zstack mysql password failed')
    else:
        test_util.test_logger('update zstack mysql password success')

def reload_default_license(vm_ip, tmp_file):

    ssh_cmd = 'ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm_ip
    cmd = '''%s 'rm -rf /var/lib/zstack/license/license*' ''' % ssh_cmd
    process_result = execute_shell_in_process(cmd, tmp_file)
    lic_ops.reload_license()

def update_repo(vm_ip, tmp_file):
    ssh_cmd = 'ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm_ip
    cmd = '''%s 'sed -i "1a 172.20.198.8 rsync.repo.zstack.io" /etc/hosts' ''' % ssh_cmd
    process_result = execute_shell_in_process(cmd, tmp_file)

def update_old_repo(vm_ip, tmp_file):
    ssh_cmd = 'ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm_ip
    cmd = '''%s 'echo "172.20.198.8 repo.zstack.io" >> /etc/hosts' ''' % ssh_cmd
    process_result = execute_shell_in_process(cmd, tmp_file)

def update_hosts(vm_ip, tmp_file):
    ssh_cmd = 'ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm_ip
    cmd = '''%s 'echo "%s zs-test" >> /etc/hosts' ''' % (ssh_cmd, vm_ip)
    process_result = execute_shell_in_process(cmd, tmp_file)

def update_mn_ip(vm_ip, tmp_file):
    ssh_cmd = 'ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm_ip
    cmd = '%s "zstack-ctl change_ip --ip="%s ' % (ssh_cmd, vm_ip)
    process_result = execute_shell_in_process(cmd, tmp_file)

def reset_rabbitmq_for_13(vm_ip, tmp_file):
    ssh_cmd = 'ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm_ip
    cmd = '''%s 'systemctl restart  rabbitmq-server.service' ''' % ssh_cmd
    process_result = execute_shell_in_process(cmd, tmp_file)
    cmd = '''%s 'rabbitmqctl add_user zstack zstack.password' ''' % ssh_cmd
    process_result = execute_shell_in_process(cmd, tmp_file)
    cmd = '%s "rabbitmqctl set_user_tags zstack administrator" ' % ssh_cmd
    process_result = execute_shell_in_process(cmd, tmp_file)
    cmd = '''%s 'rabbitmqctl set_permissions -p / zstack ".*" ".*" ".*" ' ''' % ssh_cmd
    process_result = execute_shell_in_process(cmd, tmp_file)

def reset_rabbitmq(vm_ip, tmp_file):
    ssh_cmd = 'ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm_ip
    cmd = '%s "zstack-ctl reset_rabbitmq" ' % ssh_cmd
    process_result = execute_shell_in_process(cmd, tmp_file)

def start_mn(vm_ip, tmp_file):
    ssh_cmd = 'ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm_ip
    cmd = '%s "zstack-ctl start"' % ssh_cmd
    process_result = execute_shell_in_process(cmd, tmp_file)
    time.sleep(40)

def start_node(vm_ip, tmp_file):
    ssh_cmd = 'ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm_ip
    cmd = '%s "zstack-ctl start_node --timeout 600"' % ssh_cmd
    process_result = execute_shell_in_process(cmd, tmp_file)
    time.sleep(40)

def stop_mn(vm_ip, tmp_file):
    ssh_cmd = 'ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm_ip
    cmd = '%s "zstack-ctl stop"' % ssh_cmd
    process_result = execute_shell_in_process(cmd, tmp_file)
    time.sleep(20)

def stop_node(vm_ip, tmp_file):
    ssh_cmd = 'ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm_ip
    cmd = '%s "zstack-ctl stop_node"' % ssh_cmd
    process_result = execute_shell_in_process(cmd, tmp_file)
    time.sleep(20)

def check_mn_running(vm_ip, tmp_file):
    ssh_cmd = 'ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm_ip
    cmd = '%s "zstack-ctl status|grep Stopped"' % ssh_cmd
    process_result = execute_shell_in_process(cmd, tmp_file)
    if process_result != 1:
        test_util.test_fail('zstack upgrade failed ')
    else:
        test_util.test_logger('zstack-ctl status are all running')
    #cmd = '%s "zstack-ctl status|grep Running "' % ssh_cmd
    #process_result1 = execute_shell_in_process(cmd, tmp_file)
    #test_util.test_logger('zstack-ctl status  %s' % process_result)   
    time.sleep(5)

def rm_old_zstack(vm_ip, zstack_home, tmp_file):
    ssh_cmd = 'ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm_ip
    cmd = '%s "rm -rf %s" ' % (ssh_cmd, zstack_home)
    process_result = execute_shell_in_process(cmd, tmp_file)

def update_iso(vm_ip, tmp_file, iso_path, upgrade_script_path):
    ssh_cmd = 'ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm_ip
    vm_username = os.environ['imageUsername']
    vm_password = os.environ['imagePassword']
    cmd = '%s "rm -f /opt/zstack.iso"' % ssh_cmd
    process_result = execute_shell_in_process(cmd, tmp_file)
    ssh.scp_file(iso_path, '/opt/zstack.iso', vm_ip, vm_username, vm_password)
    ssh.scp_file(upgrade_script_path, '/opt/zstack-upgrade', vm_ip, vm_username, vm_password)
    cmd = '%s "mkdir -p /opt/zstack-dvd"' % ssh_cmd
    process_result = execute_shell_in_process(cmd, tmp_file)
    cmd = '%s "bash /opt/zstack-upgrade -r /opt/zstack.iso"' % ssh_cmd
    process_result = execute_shell_in_process(cmd, tmp_file)
    #cmd = '%s "zstack-ctl stop"' % ssh_cmd
    #process_result = execute_shell_in_process(cmd, tmp_file)
    #cmd = '%s "yum -y --disablerepo=* --enablerepo=zstack-local,qemu-kvm-ev clean all"' % ssh_cmd
    #process_result = execute_shell_in_process(cmd, tmp_file)
    #cmd = '%s "yum -y clean all"' % ssh_cmd
    #process_result = execute_shell_in_process(cmd, tmp_file)
    #cmd = '%s "yum -y --disablerepo=* --enablerepo=zstack-local,qemu-kvm-ev update"' % ssh_cmd
    #process_result = execute_shell_in_process(cmd, tmp_file)
    if process_result != 0:
        test_util.test_fail('zstack upgrade iso failed')
    else:
        test_util.test_logger('update the iso success')

def update_c74_iso(vm_ip, tmp_file, c74_iso_path, upgrade_script_path):
    ssh_cmd = 'ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm_ip
    vm_username = os.environ['imageUsername']
    vm_password = os.environ['imagePassword']
    cmd = '%s "rm -f /opt/zstack.iso"' % ssh_cmd
    process_result = execute_shell_in_process(cmd, tmp_file)
    ssh.scp_file(c74_iso_path, '/opt/zstack-c74.iso', vm_ip, vm_username, vm_password)
    ssh.scp_file(upgrade_script_path, '/opt/zstack-upgrade', vm_ip, vm_username, vm_password)
    cmd = '%s "rm -rf /opt/zstack-dvd"' % ssh_cmd
    process_result = execute_shell_in_process(cmd, tmp_file)
    cmd = '%s "bash /opt/zstack-upgrade -r -f /opt/zstack-c74.iso"' % ssh_cmd
    process_result = execute_shell_in_process(cmd, tmp_file)
    if process_result != 0:
        test_util.test_fail('zstack upgrade iso failed')
    else:
        test_util.test_logger('update the iso success')

def upgrade_by_iso(vm_ip, tmp_file, iso_path, upgrade_script_path):
    ssh_cmd = 'ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm_ip
    vm_username = os.environ['imageUsername']
    vm_password = os.environ['imagePassword']
    cmd = '%s "rm -f /opt/zstack.iso"' % ssh_cmd
    process_result = execute_shell_in_process(cmd, tmp_file)
    ssh.scp_file(iso_path, '/opt/zstack.iso', vm_ip, vm_username, vm_password)
    ssh.scp_file(upgrade_script_path, '/opt/zstack-upgrade', vm_ip, vm_username, vm_password)
    cmd = '%s "mkdir -p /opt/zstack-dvd"' % ssh_cmd
    process_result = execute_shell_in_process(cmd, tmp_file)
    cmd = '%s "bash /opt/zstack-upgrade /opt/zstack.iso"' % ssh_cmd
    process_result = execute_shell_in_process(cmd, tmp_file)
    if process_result != 0:
        test_util.test_fail('zstack upgrade iso failed')
    else:
        test_util.test_logger('upgrade iso success')

def update_19_iso(vm_ip, tmp_file, iso_19_path, upgrade_script_path):
    ssh_cmd = 'ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm_ip
    vm_username = os.environ['imageUsername']
    vm_password = os.environ['imagePassword']
    #cmd = '%s "rm -f /opt/zstack_19.iso"' % ssh_cmd
    #process_result = execute_shell_in_process(cmd, tmp_file)
    ssh.scp_file(iso_19_path, '/opt/zstack_19.iso', vm_ip, vm_username, vm_password)
    ssh.scp_file(upgrade_script_path, '/opt/zstack-upgrade', vm_ip, vm_username, vm_password)
    cmd = '%s "mkdir -p /opt/zstack-dvd"' % ssh_cmd
    process_result = execute_shell_in_process(cmd, tmp_file)
    cmd = '%s "bash /opt/zstack-upgrade -r /opt/zstack_19.iso"' % ssh_cmd
    process_result = execute_shell_in_process(cmd, tmp_file)
    #cmd = '%s "zstack-ctl stop"' % ssh_cmd
    #process_result = execute_shell_in_process(cmd, tmp_file)
    #cmd = '%s "yum -y --disablerepo=* --enablerepo=zstack-local,qemu-kvm-ev clean all"' % ssh_cmd
    #process_result = execute_shell_in_process(cmd, tmp_file)
    #cmd = '%s "yum -y clean all"' % ssh_cmd
    #process_result = execute_shell_in_process(cmd, tmp_file)
    #cmd = '%s "yum -y --disablerepo=* --enablerepo=zstack-local,qemu-kvm-ev update"' % ssh_cmd
    #process_result = execute_shell_in_process(cmd, tmp_file)
    if process_result != 0:
         test_util.test_fail('zstack upgrade iso failed')
    else:
       test_util.test_logger('update the 1.9 iso success')

def update_10_iso(vm_ip, tmp_file, iso_10_path, upgrade_script_path):
    ssh_cmd = 'ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm_ip
    vm_username = os.environ['imageUsername']
    vm_password = os.environ['imagePassword']
    #cmd = '%s "rm -f /opt/zstack_10.iso"' % ssh_cmd
    #process_result = execute_shell_in_process(cmd, tmp_file)
    ssh.scp_file(iso_10_path, '/opt/zstack_10.iso', vm_ip, vm_username, vm_password)
    ssh.scp_file(upgrade_script_path, '/opt/zstack-upgrade', vm_ip, vm_username, vm_password)
    cmd = '%s "mkdir -p /opt/zstack-dvd"' % ssh_cmd
    process_result = execute_shell_in_process(cmd, tmp_file)
    cmd = '%s "bash /opt/zstack-upgrade -r /opt/zstack_10.iso"' % ssh_cmd
    process_result = execute_shell_in_process(cmd, tmp_file)
    #cmd = '%s "zstack-ctl stop"' % ssh_cmd
    #process_result = execute_shell_in_process(cmd, tmp_file)
    #cmd = '%s "yum -y --disablerepo=* --enablerepo=zstack-local,qemu-kvm-ev clean all"' % ssh_cmd
    #process_result = execute_shell_in_process(cmd, tmp_file)
    #cmd = '%s "yum -y clean all"' % ssh_cmd
    #process_result = execute_shell_in_process(cmd, tmp_file)
    #cmd = '%s "yum -y --disablerepo=* --enablerepo=zstack-local,qemu-kvm-ev update"' % ssh_cmd
    #process_result = execute_shell_in_process(cmd, tmp_file)
    if process_result != 0:
         test_util.test_fail('zstack upgrade iso failed')
    else:
       test_util.test_logger('update the 1.10 iso success')

def update_20_iso(vm_ip, tmp_file, iso_20_path, upgrade_script_path):
    ssh_cmd = 'ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm_ip
    vm_username = os.environ['imageUsername']
    vm_password = os.environ['imagePassword']
    #cmd = '%s "rm -f /opt/zstack_20.iso"' % ssh_cmd
    #process_result = execute_shell_in_process(cmd, tmp_file)
    ssh.scp_file(iso_20_path, '/opt/zstack_20.iso', vm_ip, vm_username, vm_password)
    ssh.scp_file(upgrade_script_path, '/opt/zstack-upgrade', vm_ip, vm_username, vm_password)
    cmd = '%s "mkdir -p /opt/zstack-dvd"' % ssh_cmd
    process_result = execute_shell_in_process(cmd, tmp_file)
    cmd = '%s "bash /opt/zstack-upgrade -r /opt/zstack_20.iso"' % ssh_cmd
    process_result = execute_shell_in_process(cmd, tmp_file)
    #cmd = '%s "zstack-ctl stop"' % ssh_cmd
    #process_result = execute_shell_in_process(cmd, tmp_file)
    cmd = '%s "yum -y --disablerepo=* --enablerepo=zstack-local,qemu-kvm-ev clean all"' % ssh_cmd
    process_result = execute_shell_in_process(cmd, tmp_file)
    cmd = '%s "yum -y clean all"' % ssh_cmd
    process_result = execute_shell_in_process(cmd, tmp_file)
    #cmd = '%s "yum -y --disablerepo=* --enablerepo=zstack-local,qemu-kvm-ev update"' % ssh_cmd
    #process_result = execute_shell_in_process(cmd, tmp_file)
    if process_result != 0:
         test_util.test_fail('zstack upgrade iso failed')
    else:
       test_util.test_logger('update the 2.0 iso success')

def update_21_iso(vm_ip, tmp_file, iso_21_path, upgrade_script_path):
    ssh_cmd = 'ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm_ip
    vm_username = os.environ['imageUsername']
    vm_password = os.environ['imagePassword']
    #cmd = '%s "rm -f /opt/zstack_20.iso"' % ssh_cmd
    #process_result = execute_shell_in_process(cmd, tmp_file)
    ssh.scp_file(iso_21_path, '/opt/zstack_21.iso', vm_ip, vm_username, vm_password)
    ssh.scp_file(upgrade_script_path, '/opt/zstack-upgrade', vm_ip, vm_username, vm_password)
    cmd = '%s "mkdir -p /opt/zstack-dvd"' % ssh_cmd
    process_result = execute_shell_in_process(cmd, tmp_file)
    cmd = '%s "bash /opt/zstack-upgrade -r /opt/zstack_21.iso"' % ssh_cmd
    process_result = execute_shell_in_process(cmd, tmp_file)
    #cmd = '%s "zstack-ctl stop"' % ssh_cmd
    #process_result = execute_shell_in_process(cmd, tmp_file)
    #cmd = '%s "yum -y --disablerepo=* --enablerepo=zstack-local,qemu-kvm-ev clean all"' % ssh_cmd
    #process_result = execute_shell_in_process(cmd, tmp_file)
    #cmd = '%s "yum -y clean all"' % ssh_cmd
    #process_result = execute_shell_in_process(cmd, tmp_file)
    #cmd = '%s "yum -y --disablerepo=* --enablerepo=zstack-local,qemu-kvm-ev update"' % ssh_cmd
    #process_result = execute_shell_in_process(cmd, tmp_file)
    if process_result != 0:
         test_util.test_fail('zstack upgrade iso failed')
    else:
       test_util.test_logger('update the 2.10 iso success')

def update_230_iso(vm_ip, tmp_file, iso_230_path, upgrade_script_path):
    ssh_cmd = 'ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm_ip
    vm_username = os.environ['imageUsername']
    vm_password = os.environ['imagePassword']
    #cmd = '%s "rm -f /opt/zstack_20.iso"' % ssh_cmd
    #process_result = execute_shell_in_process(cmd, tmp_file)
    ssh.scp_file(iso_230_path, '/opt/zstack_230.iso', vm_ip, vm_username, vm_password)
    ssh.scp_file(upgrade_script_path, '/opt/zstack-upgrade', vm_ip, vm_username, vm_password)
    cmd = '%s "mkdir -p /opt/zstack-dvd"' % ssh_cmd
    process_result = execute_shell_in_process(cmd, tmp_file)
    cmd = '%s "bash /opt/zstack-upgrade -r /opt/zstack_230.iso"' % ssh_cmd
    process_result = execute_shell_in_process(cmd, tmp_file)
    if process_result != 0:
         test_util.test_fail('zstack upgrade iso failed')
    else:
       test_util.test_logger('update the 2.3.0 iso success')

def update_232_iso(vm_ip, tmp_file, iso_232_path, upgrade_script_path):
    ssh_cmd = 'ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm_ip
    vm_username = os.environ['imageUsername']
    vm_password = os.environ['imagePassword']
    #cmd = '%s "rm -f /opt/zstack_20.iso"' % ssh_cmd
    #process_result = execute_shell_in_process(cmd, tmp_file)
    ssh.scp_file(iso_232_path, '/opt/zstack_232.iso', vm_ip, vm_username, vm_password)
    ssh.scp_file(upgrade_script_path, '/opt/zstack-upgrade', vm_ip, vm_username, vm_password)
    cmd = '%s "mkdir -p /opt/zstack-dvd"' % ssh_cmd
    process_result = execute_shell_in_process(cmd, tmp_file)
    cmd = '%s "bash /opt/zstack-upgrade -r /opt/zstack_232.iso"' % ssh_cmd
    process_result = execute_shell_in_process(cmd, tmp_file)
    if process_result != 0:
         test_util.test_fail('zstack upgrade iso failed')
    else:
       test_util.test_logger('update the 2.3.2 iso success')

def update_240_iso(vm_ip, tmp_file, iso_240_path, upgrade_script_path):
    ssh_cmd = 'ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm_ip
    vm_username = os.environ['imageUsername']
    vm_password = os.environ['imagePassword']
    #cmd = '%s "rm -f /opt/zstack_20.iso"' % ssh_cmd
    #process_result = execute_shell_in_process(cmd, tmp_file)
    ssh.scp_file(iso_240_path, '/opt/zstack_240.iso', vm_ip, vm_username, vm_password)
    ssh.scp_file(upgrade_script_path, '/opt/zstack-upgrade', vm_ip, vm_username, vm_password)
    cmd = '%s "mkdir -p /opt/zstack-dvd"' % ssh_cmd
    process_result = execute_shell_in_process(cmd, tmp_file)
    cmd = '%s "bash /opt/zstack-upgrade -r /opt/zstack_240.iso"' % ssh_cmd
    process_result = execute_shell_in_process(cmd, tmp_file)
    if process_result != 0:
         test_util.test_fail('zstack upgrade iso failed')
    else:
       test_util.test_logger('update the 2.4.0 iso success')

def update_local_iso(vm_ip, tmp_file, local_iso_path, upgrade_script_path):
    ssh_cmd = 'ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm_ip
    vm_username = os.environ['imageUsername']
    vm_password = os.environ['imagePassword']
    #ssh.scp_file(iso_240_path, '/opt/zstack_240.iso', vm_ip, vm_username, vm_password)
    ssh.scp_file(upgrade_script_path, '/opt/zstack-upgrade', vm_ip, vm_username, vm_password)
    #cmd = '%s "mkdir -p /opt/zstack-dvd"' % ssh_cmd
    #process_result = execute_shell_in_process(cmd, tmp_file)
    cmd = '%s "bash /opt/zstack-upgrade -r %s"' % (ssh_cmd,local_iso_path)
    process_result = execute_shell_in_process(cmd, tmp_file)
    if process_result != 0:
         test_util.test_fail('zstack upgrade iso failed')
    else:
       test_util.test_logger('update the 2.4.0 iso success')

def prepare_mevoco_test_env(vm_inv):
    all_in_one_pkg = os.environ['zstackPkg']
    scp_file_to_vm(vm_ip, all_in_one_pkg, '/root/zizhu.bin')

    vm_ip = vm_inv.vmNics[0].ip
    ssh.make_ssh_no_password(vm_ip, test_lib.lib_get_vm_username(vm_inv), \
            test_lib.lib_get_vm_password(vm_inv))

def prepare_test_env(vm_inv, aio_target):
    zstack_install_script = os.environ['zstackInstallScript']
    target_file = '/root/zstack_installer.sh'
    vm_ip = vm_inv.vmNics[0].ip
    vm_username = test_lib.lib_get_vm_username(vm_inv)
    vm_password = test_lib.lib_get_vm_password(vm_inv)
    scp_file_to_vm(vm_ip, zstack_install_script, target_file)

    all_in_one_pkg = os.environ['zstackPkg']
    scp_file_to_vm(vm_ip, all_in_one_pkg, aio_target)

    ssh.make_ssh_no_password(vm_ip, vm_username, vm_password)

def prepare_upgrade_test_env(vm_inv, aio_target, upgrade_pkg):
    zstack_install_script = os.environ['zstackInstallScript']
    target_file = '/root/zstack_installer.sh'
    vm_ip = vm_inv.vmNics[0].ip
    vm_username = test_lib.lib_get_vm_username(vm_inv)
    vm_password = test_lib.lib_get_vm_password(vm_inv)
    scp_file_to_vm(vm_ip, zstack_install_script, target_file)

    scp_file_to_vm(vm_ip, upgrade_pkg, aio_target)

    ssh.make_ssh_no_password(vm_ip, vm_username, vm_password)

def prepare_yum_repo(vm_inv):
    origin_file = '/etc/yum.repos.d/epel.repo'
    target_file = '/etc/yum.repos.d/epel.repo'
    vm_ip = vm_inv.vmNics[0].ip
    vm_username = test_lib.lib_get_vm_username(vm_inv)
    vm_password = test_lib.lib_get_vm_password(vm_inv)
    scp_file_to_vm(vm_ip, origin_file, target_file)

    ssh.make_ssh_no_password(vm_ip, vm_username, vm_password)

def upgrade_zstack(vm_ip, target_file, tmp_file):
    ssh_cmd = 'ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm_ip
    vm_username = os.environ['imageUsername']
    vm_password = os.environ['imagePassword']
    ssh.scp_file(target_file, '/opt/zstack_installer', vm_ip, vm_username, vm_password)

    env_var = "WEBSITE='%s'" % 'localhost'

#    cmd = '%s "%s bash %s -u -R aliyun"' % (ssh_cmd, env_var, target_file)
    #cmd = '%s "%s bash %s -u -o"' % (ssh_cmd, env_var, '/opt/zstack_installer')
    cmd = '%s "%s bash %s -u"' % (ssh_cmd, env_var, '/opt/zstack_installer')

    process_result = execute_shell_in_process(cmd, tmp_file)

    if process_result != 0:
         test_util.test_fail('zstack upgrade failed')
    else:
       test_util.test_logger('upgrade zstack success')
       # cmd = '%s "cat /tmp/zstack_installation.log"' % ssh_cmd
       # execute_shell_in_process(cmd, tmp_file)
       # if 'no management-node-ready message received within' in open(tmp_file).read():
       #     times = 30
       #     cmd = '%s "zstack-ctl status"' % ssh_cmd
       #     while (times > 0):
       #         time.sleep(10)
       #         process_result = execute_shell_in_process(cmd, tmp_file, 10, True)
       #         times -= 0
       #         if process_result == 0:
       #             test_util.test_logger("management node start after extra %d seconds" % (30 - times + 1) * 10 )
       #             return 0
       #         test_util.test_logger("mn node is still not started up, wait for another 10 seconds...")
       #     else:
       #         test_util.test_fail('zstack upgrade failed')

def upgrade_zstack_with_root_mysql_password(vm_ip, target_file, tmp_file):
    ssh_cmd = 'ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm_ip
    vm_username = os.environ['imageUsername']
    vm_password = os.environ['imagePassword']
    ssh.scp_file(target_file, '/opt/zstack_installer', vm_ip, vm_username, vm_password)
    env_var = "WEBSITE='%s'" % 'localhost'
    cmd = '%s "%s bash %s -u -P zstack.123"' % (ssh_cmd, env_var, '/opt/zstack_installer')
    process_result = execute_shell_in_process(cmd, tmp_file)

    if process_result != 0:
         test_util.test_fail('zstack upgrade failed')
    else:
       test_util.test_logger('upgrade zstack success')

def execute_mevoco_aliyun_install(ssh_cmd, tmp_file):
    target_file = '/root/zizhu.bin'
    env_var = "ZSTACK_ALL_IN_ONE='%s' WEBSITE='%s'" % \
            (target_file, 'localhost')

    cmd = '%s "%s bash /root/zizhu.bin -R aliyun -m"' % (ssh_cmd, env_var)

    process_result = execute_shell_in_process(cmd, tmp_file)

    if process_result != 0:
        cmd = '%s "cat /tmp/zstack_installation.log"' % ssh_cmd
        execute_shell_in_process(cmd, tmp_file)
        if 'no management-node-ready message received within' in open(tmp_file).read():
            times = 30
            cmd = '%s "zstack-ctl status"' % ssh_cmd
            while (times > 0):
                time.sleep(10)
                process_result = execute_shell_in_process(cmd, tmp_file, 10, True)
                times -= 0
                if process_result == 0:
                    test_util.test_logger("management node start after extra %d seconds" % (30 - times + 1) * 10 )
                    return 0
                test_util.test_logger("mn node is still not started up, wait for another 10 seconds...")
            else:
                test_util.test_fail('zstack installation failed')

def execute_mevoco_online_install(ssh_cmd, tmp_file):
    target_file = '/root/zizhu.bin'
    env_var = "ZSTACK_ALL_IN_ONE='%s' WEBSITE='%s'" % \
            (target_file, 'localhost')

    cmd = '%s "%s bash /root/zizhu.bin -m"' % (ssh_cmd, env_var)

    process_result = execute_shell_in_process(cmd, tmp_file)

    if process_result != 0:
        cmd = '%s "cat /tmp/zstack_installation.log"' % ssh_cmd
        execute_shell_in_process(cmd, tmp_file)
        if 'no management-node-ready message received within' in open(tmp_file).read():
            times = 30
            cmd = '%s "zstack-ctl status"' % ssh_cmd
            while (times > 0):
                time.sleep(10)
                process_result = execute_shell_in_process(cmd, tmp_file, 10, True)
                times -= 0
                if process_result == 0:
                    test_util.test_logger("management node start after extra %d seconds" % (30 - times + 1) * 10 )
                    return 0
                test_util.test_logger("mn node is still not started up, wait for another 10 seconds...")
            else:
                test_util.test_fail('zstack installation failed')

def execute_install_with_args(ssh_cmd, args, target_file, tmp_file):
    env_var = " WEBSITE='%s'" % ('localhost')

    cmd = '%s "%s bash %s %s"' % (ssh_cmd, env_var, target_file, args)

    process_result = execute_shell_in_process(cmd, tmp_file, 2400)

    if process_result != 0:
        cmd = '%s "cat /tmp/zstack_installation.log"' % ssh_cmd
        execute_shell_in_process(cmd, tmp_file)
        if 'no management-node-ready message received within' in open(tmp_file).read():
            times = 30
            cmd = '%s "zstack-ctl status"' % ssh_cmd
            while (times > 0):
                time.sleep(10)
                process_result = execute_shell_in_process(cmd, tmp_file, 10, True)
                times -= 0
                if process_result == 0:
                    test_util.test_logger("management node start after extra %d seconds" % (30 - times + 1) * 10 )
                    return 0
                test_util.test_logger("mn node is still not started up, wait for another 10 seconds...")
            else:
                test_util.test_fail('zstack installation failed')

def execute_all_install(ssh_cmd, target_file, tmp_file):
    env_var = " WEBSITE='%s'" % ('localhost')

#    cmd = '%s "%s bash %s -R aliyun"' % (ssh_cmd, env_var, target_file)
    cmd = '%s "%s bash %s -o"' % (ssh_cmd, env_var, target_file)

    process_result = execute_shell_in_process(cmd, tmp_file, 2400)

    if process_result != 0:
        cmd = '%s "cat /tmp/zstack_installation.log"' % ssh_cmd
        execute_shell_in_process(cmd, tmp_file)
        if 'no management-node-ready message received within' in open(tmp_file).read():
            times = 30
            cmd = '%s "zstack-ctl status"' % ssh_cmd
            while (times > 0):
                time.sleep(10)
                process_result = execute_shell_in_process(cmd, tmp_file, 10, True)
                times -= 0
                if process_result == 0:
                    test_util.test_logger("management node start after extra %d seconds" % (30 - times + 1) * 10 )
                    return 0
                test_util.test_logger("mn node is still not started up, wait for another 10 seconds...")
            else:
                test_util.test_fail('zstack installation failed')

def only_install_zstack(ssh_cmd, target_file, tmp_file):
    env_var = "WEBSITE='%s'" % 'localhost'

    cmd = '%s "%s bash %s -d -i"' % (ssh_cmd, env_var, target_file)

    process_result = execute_shell_in_process(cmd, tmp_file)

    if process_result != 0:
        cmd = '%s "cat /tmp/zstack_installation.log"' % ssh_cmd
        execute_shell_in_process(cmd, tmp_file)
        test_util.test_fail('zstack installation failed')

def check_installation(vm_ip, tmp_file):
#    cmd = '%s "/usr/bin/zstack-cli LogInByAccount accountName=admin password=password"' % ssh_cmd
#    process_result = execute_shell_in_process(cmd, tmp_file)
#    if process_result != 0:
#        test_util.test_fail('zstack-cli login failed')
    vm_username = os.environ['imageUsername']
    vm_password = os.environ['imagePassword']

    bs_option = test_util.BackupStorageOption()
    bs_option.name = 'bs1'
    bs_option.description = 'bs'
    bs_option.hostname = vm_ip
    bs_option.url = '/home/bs'
    bs_option.username = vm_username
    bs_option.password = vm_password
    bs_option.sshPort = '22'
    bs = scen_ops.create_sftp_backup_storage(vm_ip, bs_option)
    scen_ops.delete_backup_storage(vm_ip, bs.uuid)
#    vm_passwd = test_lib.lib_get_vm_password(vm_inv)
#    vm_ip = vm_ip = vm_inv.vmNics[0].ip
#    cmd = '%s "/usr/bin/zstack-cli AddSftpBackupStorage name=bs1 description=bs hostname=%s username=root password=%s url=/home/bs"' % (ssh_cmd, vm_ip, vm_passwd)
#    process_result = execute_shell_in_process(cmd, tmp_file)
#    if process_result != 0:
#        test_util.test_fail('zstack-cli create Backup Storage failed')
#
#    cmd = '%s "/usr/bin/zstack-cli QuerySftpBackupStorage name=bs1"' % ssh_cmd
#    process_result = execute_shell_in_process(cmd, tmp_file)
#    if process_result != 0:
#        test_util.test_fail('zstack-cli Query Backup Storage failed')
#    cmd = '%s "/usr/bin/zstack-cli QuerySftpBackupStorage name=bs1 fields=uuid" | grep uuid | awk \'{print $2}\'' % ssh_cmd
#    (process_result, bs_uuid) = execute_shell_in_process_stdout(cmd, tmp_file)
#    if process_result != 0:
#        test_util.test_fail('zstack-cli Query Backup Storage failed')
#
#    cmd = '%s "/usr/bin/zstack-cli DeleteBackupStorage uuid=%s"' % (ssh_cmd, bs_uuid.split('"')[1])
#    process_result = execute_shell_in_process(cmd, tmp_file)
#    if process_result != 0:
#        test_util.test_fail('zstack-cli Delete Backup Storage failed')

# check zone
#    zone = scen_ops.create_zone(zstack_management_ip, zone_option)
#    cmd = '%s "/usr/bin/zstack-cli CreateZone name=ZONE1"' % ssh_cmd
#    process_result = execute_shell_in_process(cmd, tmp_file)
#    if process_result != 0:
#        test_util.test_fail('zstack-cli Create Zone failed')
#
#    cmd = '%s "/usr/bin/zstack-cli QueryZone name=ZONE1"' % ssh_cmd
#    process_result = execute_shell_in_process(cmd, tmp_file)
#    if process_result != 0:
#        test_util.test_fail('zstack-cli Query Zone failed')
#    cmd = '%s "/usr/bin/zstack-cli QueryZone name=ZONE1 fields=uuid" | grep uuid | awk \'{print $2}\'' % ssh_cmd
#    (process_result, zone_uuid) = execute_shell_in_process_stdout(cmd, tmp_file)
#    if process_result != 0:
#        test_util.test_fail('zstack-cli Query Zone failed')
#
#    cmd = '%s "/usr/bin/zstack-cli DeleteZone uuid=%s"' % (ssh_cmd, zone_uuid.split('"')[1])
#    process_result = execute_shell_in_process(cmd, tmp_file)
#    if process_result != 0:
#        test_util.test_fail('zstack-cli Delete Zone failed')

# check item
#    cmd = '%s "/usr/bin/zstack-ctl status" | grep \'^version\' | awk \'{print $2}\'' % ssh_cmd
#    (process_result, version_info) = execute_shell_in_process_stdout(cmd, tmp_file)
#    if process_result != 0:
#        test_util.test_fail('zstack-ctl get version failed')
#    if '1.3' in version_info or '1.2' in version_info:
#        cmd = '%s "/usr/bin/zstack-ctl status" | grep \'^status\' | awk \'{print $2}\'' % ssh_cmd
#        (process_result, status_info) = execute_shell_in_process_stdout(cmd, tmp_file)
#        if process_result != 0:
#            test_util.test_fail('zstack-ctl get status failed')
#        if not 'Running' in status_info:
#            test_util.test_dsc('zstack is not running, try to start zstack')
#            cmd = '%s "/usr/bin/zstack-ctl start"' % ssh_cmd
#            process_result = process_result = execute_shell_in_process(cmd, tmp_file)
#            if process_result != 0:
#                test_util.test_fail('zstack-ctl start failed')
#            time.sleep(5)
#            cmd = '%s "/usr/bin/zstack-ctl status" | grep \'^status\' | awk \'{print $2}\'' % ssh_cmd
#            (process_result, status_info) = execute_shell_in_process_stdout(cmd, tmp_file)
#            if process_result != 0:
#                test_util.test_fail('zstack-ctl get status failed')
#            if not 'Running' in status_info:
#                test_util.test_fail('zstack is not running, start zstack failed')
#        test_util.test_dsc('check zstack status, zstack is running')
#    else:
#        cmd = '%s "/usr/bin/zstack-ctl status" | grep \'^MN status\' | awk \'{print $3}\'' % ssh_cmd
#        (process_result, mn_status) = execute_shell_in_process_stdout(cmd, tmp_file)
#        if process_result != 0:
#            test_util.test_fail('zstack-ctl get MN status failed')
#        if not 'Running' in mn_status:
#            test_util.test_dsc('management node is not running, try to start management node')
#            cmd = '%s "/usr/bin/zstack-ctl start_node"' % ssh_cmd
#            process_result = process_result = execute_shell_in_process(cmd, tmp_file)
#            if process_result != 0:
#                test_util.test_fail('zstack-ctl start_node failed')
#            time.sleep(5)
#            cmd = '%s "/usr/bin/zstack-ctl status" | grep \'^MN status\' | awk \'{print $3}\'' % ssh_cmd
#            (process_result, mn_status) = execute_shell_in_process_stdout(cmd, tmp_file)
#            if process_result != 0:
#                test_util.test_fail('zstack-ctl get MN status failed')
#            if not 'Running' in mn_status:
#                test_util.test_fail('management node is not running, start management node failed')
#        test_util.test_dsc('check MN, MN is running')
#        cmd = '%s "/usr/bin/zstack-ctl status" | grep \'^UI status\' | awk \'{print $3}\'' % ssh_cmd
#        (process_result, ui_status) = execute_shell_in_process_stdout(cmd, tmp_file)
#        if process_result != 0:
#            test_util.test_fail('zstack-ctl get UI status failed')
#        if not 'Running' in ui_status:
#            test_util.test_dsc('UI is not running, try to start UI')
#            cmd = '%s "/usr/bin/zstack-ctl start_ui"' % ssh_cmd
#            process_result = process_result = execute_shell_in_process(cmd, tmp_file)
#            if process_result != 0:
#                test_util.test_fail('zstack-ctl start_ui failed')
#            time.sleep(5)
#            cmd = '%s "/usr/bin/zstack-ctl status" | grep \'^MN status\' | awk \'{print $3}\'' % ssh_cmd
#            (process_result, mn_status) = execute_shell_in_process_stdout(cmd, tmp_file)
#            if process_result != 0:
#                test_util.test_fail('zstack-ctl get MN status failed')
#            if not 'Running' in mn_status:
#                test_util.test_fail('UI is not running, start UI failed')
#        test_util.test_dsc('check UI, UI is running')
#
#    cmd = '%s "/usr/bin/zstack-ctl status" | grep ^ZSTACK_HOME | awk \'{print $2}\'' % ssh_cmd
#    (process_result, zstack_home) = execute_shell_in_process_stdout(cmd, tmp_file)
#    if process_result != 0:
#        test_util.test_fail('zstack-ctl status get ZSTACK_HOME failed')
#    zstack_home = zstack_home[:-1]
#    cmd = '%s "[ -d " %s " ] && echo yes || echo no" ' % (ssh_cmd, zstack_home)
#    (process_result, dir_exist) = execute_shell_in_process_stdout(cmd, tmp_file)
#    if process_result != 0:
#        test_util.test_fail('check ZSTACK_HOME failed')
#    dir_exist = dir_exist[:-1]
#    if dir_exist == 'no':
#        test_util.test_fail('there is no ZSTACK_HOME')
#
#    cmd = '%s "/usr/bin/zstack-ctl status" | grep ^zstack.properties | awk \'{print $2}\'' % ssh_cmd
#    (process_result, properties_file) = execute_shell_in_process_stdout(cmd, tmp_file)
#    if process_result != 0:
#        test_util.test_fail('zstack-ctl status get zstack.properties failed')
#    properties_file = properties_file[:-1]
#    cmd = '%s "[ -f " %s " ] && echo yes || echo no" ' % (ssh_cmd, properties_file)
#    (process_result, file_exist) = execute_shell_in_process_stdout(cmd, tmp_file)
#    if process_result != 0:
#        test_util.test_fail('check zstack.properties failed')
#    file_exist = file_exist[:-1]
#    if file_exist == 'no':
#        test_util.test_fail('there is no zstack.properties')
#
#    cmd = '%s "/usr/bin/zstack-ctl status" | grep ^log4j2.xml | awk \'{print $2}\'' % ssh_cmd
#    (process_result, properties_file) = execute_shell_in_process_stdout(cmd, tmp_file)
#    if process_result != 0:
#        test_util.test_fail('zstack-ctl status get log4j2.xml failed')
#    properties_file = properties_file[:-1]
#    cmd = '%s "[ -f " %s " ] && echo yes || echo no" ' % (ssh_cmd, properties_file)
#    (process_result, file_exist) = execute_shell_in_process_stdout(cmd, tmp_file)
#    if process_result != 0:
#        test_util.test_fail('check log4j2.xml failed')
#    file_exist = file_exist[:-1]
#    if file_exist == 'no':
#        test_util.test_fail('there is no log4j2.xml')
#
#    cmd = '%s "/usr/bin/zstack-ctl status" | grep ^\'PID file\' | awk \'{print $3}\'' % ssh_cmd
#    (process_result, properties_file) = execute_shell_in_process_stdout(cmd, tmp_file)
#    if process_result != 0:
#        test_util.test_fail('zstack-ctl status get PID file failed')
#    properties_file = properties_file[:-1]
#    cmd = '%s "[ -f " %s " ] && echo yes || echo no" ' % (ssh_cmd, properties_file)
#    (process_result, file_exist) = execute_shell_in_process_stdout(cmd, tmp_file)
#    if process_result != 0:
#        test_util.test_fail('check PID file failed')
#    file_exist = file_exist[:-1]
#    if file_exist == 'no':
#        test_util.test_fail('there is no PID file')
#
#    cmd = '%s "/usr/bin/zstack-ctl status" | grep ^\'log file\' | awk \'{print $3}\'' % ssh_cmd
#    (process_result, properties_file) = execute_shell_in_process_stdout(cmd, tmp_file)
#    if process_result != 0:
#        test_util.test_fail('zstack-ctl status get log file failed')
#    properties_file = properties_file[:-1]
#    cmd = '%s "[ -f " %s " ] && echo yes || echo no" ' % (ssh_cmd, properties_file)
#    (process_result, file_exist) = execute_shell_in_process_stdout(cmd, tmp_file)
#    if process_result != 0:
#        test_util.test_fail('check log file failed')
#    file_exist = file_exist[:-1]
#    if file_exist == 'no':
#        test_util.test_fail('there is no log file')

def reconnect_backup_storage(vm_ip, tmp_file):
	
    bs = scen_ops.query_backup_storage(vm_ip, tmp_file)
    scen_ops.reconnect_backup_storage(vm_ip, bs.uuid)

def delete_backup_storage(vm_ip, tmp_file):
    bs = scen_ops.query_backup_storage(vm_ip, tmp_file)
    scen_ops.delete_backup_storage(vm_ip, bs.uuid)

def check_zstack_version(vm_ip, tmp_file, pkg_version):
    ssh_cmd = 'ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm_ip
    cmd = '%s "/usr/bin/zstack-ctl status" | grep ^version | awk \'{print $2}\'' % ssh_cmd
    (process_result, version) = execute_shell_in_process_stdout(cmd, tmp_file)
    if process_result != 0:
        test_util.test_fail('zstack-ctl get version failed')
    version = version[:-1]
    test_util.test_dsc("current version number: %s" % version)
    if version != pkg_version:
        test_util.test_fail('try to install zstack-%s, but current version is zstack-%s' % (pkg_version, version))

def check_zstack_or_mevoco(vm_ip, tmp_file, zom):
    ssh_cmd = 'ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm_ip
    cmd = '%s "/usr/bin/zstack-ctl status" | grep ^version | awk \'{print $3}\'' % ssh_cmd
    (process_result, version) = execute_shell_in_process_stdout(cmd, tmp_file)
    if process_result != 0:
        test_util.test_fail('zstack-ctl get version failed')
    version = version[1:-1]
    test_util.test_dsc("current version: %s" % version)
    if version != zom:
        test_util.test_fail('try to install %s, but current version is %s' % (zom, version))

def create_zone1(vm_ip, tmp_file):
    zone_option = test_util.ZoneOption()
    zone_option.name = 'Zone1'
    zone_option.description = 'Zone1'
    zone_inv = scen_ops.create_zone(vm_ip, zone_option)

    return zone_inv

def create_cluster1(vm_ip, cluster_name, zone_uuid, tmp_file):
    cluster_option = test_util.ClusterOption()
    cluster_option.name = cluster_name
    cluster_option.description = 'Cluster'
    cluster_option.hypervisor_type = 'KVM'
    cluster_option.zone_uuid = zone_uuid
    cluster_inv = scen_ops.create_cluster(vm_ip, cluster_option)

    return cluster_inv

def add_kvm_host1(vm_ip, host_ip, host_name, cluster_uuid, tmp_file):
    
    vm_username = os.environ['imageUsername']
    vm_password = os.environ['imagePassword']

    host_option = test_util.HostOption()
    host_option.clusterUuid = cluster_uuid
    host_option.username = vm_username
    host_option.password = vm_password
    host_option.managementIp = host_ip
    host_option.sshPort = '22'
    host_option.name = host_name
    host_inv = scen_ops.add_kvm_host(vm_ip, host_option)

    return host_inv

def create_local_ps(vm_ip, zone_uuid, tmp_file):
    ps_option = test_util.PrimaryStorageOption()
    ps_option.name = 'PS1'
    ps_option.url = '/zstack_ps1'
    ps_option.zone_uuid = zone_uuid
    ps_inv = scen_ops.create_local_primary_storage(vm_ip, ps_option)

    return ps_inv

def create_sftp_backup_storage(vm_ip, tmp_file):
    vm_username = os.environ['imageUsername']
    vm_password = os.environ['imagePassword']

    bs_option = test_util.BackupStorageOption()
    bs_option.name = 'bs1'
    bs_option.description = 'bs'
    bs_option.hostname = vm_ip
    bs_option.url = '/home/bs'
    bs_option.username = vm_username
    bs_option.password = vm_password
    bs_option.sshPort = '22'
    bs_inv = scen_ops.create_sftp_backup_storage(vm_ip, bs_option)
    scen_ops.reconnect_backup_storage(vm_ip, bs_inv.uuid)
    
    return bs_inv

def attach_ps(vm_ip, ps_uuid, cluster_uuid, tmp_file):

    scen_ops.attach_ps_to_cluster(vm_ip, ps_uuid, cluster_uuid)

def attach_bs(vm_ip, bs_uuid, zone_uuid, tmp_file):

    scen_ops.attach_bs_to_zone(vm_ip, bs_uuid, zone_uuid)

def add_image_local(vm_ip, bs_uuid, tmp_file):

    image_option = test_util.ImageOption()
    image_option.name = 'image1.4'
    image_option.format = 'qcow2'
    image_option.platform = 'Linux'
    image_option.backup_storage_uuid_list = [bs_uuid]
    image_option.url = 'file:///opt/zstack-dvd/zstack-image-1.4.qcow2'
    image_inv = scen_ops.add_image1(vm_ip, image_option)

    return image_inv

def create_vm_offering(vm_ip, tmp_file):
    vmoffering_option = test_util.InstanceOfferingOption()
    vmoffering_option.name = '1-1G'
    vmoffering_option.cpuNum = '1'
    vmoffering_option.memorySize = '1073741824'
    vmoffering_option.type = 'UserVm'
    vmoffering_inv = scen_ops.create_instance_offering1(vm_ip, vmoffering_option)

    return vmoffering_inv

def attach_mount_volume(volume, vm, mount_point):
    volume.attach(vm)
    import tempfile
    script_file = tempfile.NamedTemporaryFile(delete=False)
    script_file.write('''
mkdir -p %s
device="/dev/`ls -ltr --file-type /dev | awk '$4~/disk/ {print $NF}' | grep -v '[[:digit:]]' | tail -1`"
mount ${device}1 %s
''' % (mount_point, mount_point))
    script_file.close()

    vm_inv = vm.get_vm()
    if not test_lib.lib_execute_shell_script_in_vm(vm_inv, script_file.name):
        test_util.test_fail("mount operation failed in [volume:] %s in [vm:] %s" % (volume.get_volume().uuid, vm_inv.uuid))
        os.unlink(script_file.name)

def mount_volume(vm_ip, mount_point, tmp_file):

    ssh_cmd = 'ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm_ip
    cmd = '%s " mkdir -p  %s && mount /dev/vdb1  %s" ' % (ssh_cmd, mount_point, mount_point)
    process_result = execute_shell_in_process(cmd, tmp_file)

def upgrade_old_zstack(vm_ip, old_bin, tmp_file):
    ssh_cmd = 'ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm_ip
    env_var = "WEBSITE='%s'" % 'localhost'
    cmd = '%s "%s bash %s -u"' % (ssh_cmd, env_var, old_bin)

    process_result = execute_shell_in_process(cmd, tmp_file)

    if process_result != 0:
         test_util.test_fail('zstack upgrade failed')
    else:
       test_util.test_logger('upgrade zstack success')

