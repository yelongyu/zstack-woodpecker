# coding=utf-8
import importlib
import os
import subprocess
import sys
import time
import uuid
import xml.dom.minidom as xmldom

import zstacklib.utils.ssh as ssh
import zstackwoodpecker.test_util as test_util

# -------------------------------------------------------------------------------------
zstack_management_ip = os.environ.get('zstackManagementIp')
data_image_name = os.environ.get('data_volume_template')
tmp_file = '/tmp/%s' % uuid.uuid1().get_hex()
mount_point = "/tmp/%s" % uuid.uuid1().get_hex()

path = os.path.dirname(__file__)
sys.path.append(path)
feature_cases = os.path.join(os.path.dirname(__file__), "feature_cases.xml")
VERSION = ["2.6.0",
           "3.0.0", "3.0.1",
           "3.1.0", "3.1.1",
           "3.2.0",
           "3.3.0",
           "3.4.0",
           "3.4.1",
           "3.5.0",
           "3.5.2",
           "3.6.0"
           ]
ver = {}
for v in VERSION:
    ver[v] = len(ver) + 1

ver["latest"] = 100000


def _version():
    print "ALL VERSION %s need to upgrade" % VERSION
    for i in VERSION:
        yield i
        print "\nVERSION List %s need to upgrade" % VERSION


class Case(object):
    def __init__(self, start_version, end_version, case_name):
        self.start_version = start_version
        self.end_version = end_version
        self.case_name = case_name
        self.case = None
        self.result = None

    def init(self):
        pkg_path = path
        if "/" in self.case_name:
            full_name = self.case_name
            dir_name = full_name.split('/')[0]
            self.case_name = full_name.split("/")[-1]
            pkg_path = os.path.join(path, dir_name)
            sys.path.append(pkg_path)
        self.case = importlib.import_module(self.case_name, pkg_path)

    def run(self):
        self.case.test()

    def error_cleanup(self):
        try:
            self.case.error_cleanup()
        except Exception as e:
            print e

    def recover_env(self):
        try:
            self.case.recover_env()
        except Exception as e:
            print e


def import_xml_to_cases():
    all_cases = []
    xml_path = os.path.abspath(feature_cases)
    domobj = xmldom.parse(xml_path)

    subElementObj = domobj.getElementsByTagName("cases")[0]
    default_version = subElementObj.getAttribute("default_version")

    cases_obj = subElementObj.getElementsByTagName("case")

    for case_obj in cases_obj:
        start = case_obj.getAttribute("start_version") if case_obj.hasAttribute("start_version") else default_version
        end = case_obj.getAttribute("end_version") if case_obj.hasAttribute("end_version") else "latest"
        name = case_obj.firstChild.data
        case = Case(ver[start], ver[end], name)
        case.init()
        all_cases.append(case)
    return all_cases


def find_cases(all_cases, current_version):
    need_execute_cases_list = []
    not_execute_cases_anymore = []
    for case in all_cases:
        if case.start_version <= ver[current_version]:
            if case.end_version >= ver[current_version]:
                need_execute_cases_list.append(case)
            else:
                not_execute_cases_anymore.append(case)

    for case in not_execute_cases_anymore:
        all_cases.remove(case)

    return need_execute_cases_list, all_cases


# -------------------------------------------------------------------------------------

def initial(management_ip):
    # todo: zsha2_vip

    make_ssh_no_password(management_ip, tmp_file)
    update_old_repo(management_ip, tmp_file)


def update_repo(management_ip, tmp_file):
    ssh_cmd = 'ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % management_ip
    cmd = '''%s 'sed -i "1a 172.20.198.8 rsync.repo.zstack.io" /etc/hosts' ''' % ssh_cmd
    process_result = execute_shell_in_process(cmd, tmp_file)


def update_old_repo(management_ip, tmp_file):
    ssh_cmd = 'ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % management_ip
    cmd = '''%s 'echo "172.20.198.8 repo.zstack.io" >> /etc/hosts' ''' % ssh_cmd
    process_result = execute_shell_in_process(cmd, tmp_file)


def upgrade_zstack(vm_ip, target_file, tmp_file):
    ssh_cmd = 'ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % vm_ip
    vm_username = os.environ['imageUsername']
    vm_password = os.environ['imagePassword']
    ssh.scp_file(target_file, '/opt/zstack_installer', vm_ip, vm_username, vm_password)

    env_var = "WEBSITE='%s'" % 'localhost'
    cmd = '%s "%s bash %s -u"' % (ssh_cmd, env_var, '/opt/zstack_installer')
    process_result = execute_shell_in_process(cmd, tmp_file)

    if process_result != 0:
        test_util.test_fail('zstack upgrade failed')
    else:
        test_util.test_logger('upgrade zstack success')


def start_mn(management_ip):
    ssh_cmd = 'ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % management_ip
    cmd = '%s "zstack-ctl start"' % ssh_cmd
    process_result = execute_shell_in_process(cmd, tmp_file)


def start_node(management_ip):
    ssh_cmd = 'ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % management_ip
    cmd = '%s "zstack-ctl start_node --timeout 600"' % ssh_cmd
    process_result = execute_shell_in_process(cmd, tmp_file)


def stop_mn(management_ip):
    ssh_cmd = 'ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % management_ip
    cmd = '%s "zstack-ctl stop"' % ssh_cmd
    process_result = execute_shell_in_process(cmd, tmp_file)


def stop_node(management_ip):
    ssh_cmd = 'ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % management_ip
    cmd = '%s "zstack-ctl stop_node"' % ssh_cmd
    process_result = execute_shell_in_process(cmd, tmp_file)


def check_mn_running(management_ip):
    ssh_cmd = 'ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % management_ip
    cmd = '%s "zstack-ctl status|grep Stopped"' % ssh_cmd
    process_result = execute_shell_in_process(cmd, tmp_file)
    if process_result != 1:
        test_util.test_fail('zstack upgrade failed ')
    else:
        test_util.test_logger('zstack-ctl status are all running')


# -------------------------------------------------------------------------------------

def make_ssh_no_password(management_ip, tmp_file):
    ssh_cmd = 'ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s' % management_ip
    ssh.make_ssh_no_password(management_ip, os.environ['imageUsername'], os.environ['imagePassword'])
    copy_id_dsa(management_ip, ssh_cmd, tmp_file)
    copy_id_dsa_pub(management_ip)


def copy_id_dsa(management_ip, ssh_cmd, tmp_file):
    src_file = '/root/.ssh/id_dsa'
    target_file = '/root/.ssh/id_dsa'
    if not os.path.exists(src_file):
        os.system("ssh-keygen -t dsa -N '' -f %s" % src_file)

    scp_file_to_vm(management_ip, src_file, target_file)
    cmd = '%s "chmod 600 /root/.ssh/id_dsa"' % ssh_cmd
    process_result = execute_shell_in_process(cmd, tmp_file)


def copy_id_dsa_pub(management_ip):
    src_file = '/root/.ssh/id_dsa.pub'
    target_file = '/root/.ssh/authorized_keys'
    if not os.path.exists(src_file):
        os.system("ssh-keygen -t dsa -N '' -f %s" % src_file)
    scp_file_to_vm(management_ip, src_file, target_file)


def scp_file_to_vm(management_ip, src_file, target_file):
    vm_username = os.environ['imageUsername']
    vm_password = os.environ['imagePassword']
    ssh.scp_file(src_file, target_file, management_ip, vm_username, vm_password)


def execute_shell_in_process(cmd, tmp_file, timeout=3600, no_timeout_excep=False):
    logfd = open(tmp_file, 'w', 0)
    process = subprocess.Popen(cmd, executable='/bin/sh', shell=True, stdout=logfd, stderr=logfd,
                               universal_newlines=True)

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
        if test_time % 10 == 0:
            print('shell script used: %ds' % int(test_time))
        time.sleep(1)
    logfd.close()
    logfd = open(tmp_file, 'r')
    test_util.test_logger('[shell:] %s [logs]: %s' % (cmd, '\n'.join(logfd.readlines())))
    logfd.close()
    return process.returncode
# -------------------------------------------------------------------------------------