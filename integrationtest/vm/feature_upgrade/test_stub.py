# coding=utf-8
import os
import subprocess
import sys
import time
import uuid
import xml.dom.minidom as xmldom

import importlib
import zstacklib.utils.ssh as ssh
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.scenario_operations as sce_ops
import zstackwoodpecker.test_lib as test_lib
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
        # need_execute_cases_list.append(case)

    for case in not_execute_cases_anymore:
        all_cases.remove(case)

    return need_execute_cases_list, all_cases


# -------------------------------------------------------------------------------------
iso_dict = {
    "2.3.0": "%s/iso/zstack_230.iso",
    "2.3.1": '%s/iso/zstack_230.iso',
    "2.3.2": "%s/iso/zstack_230.iso",
    "2.4.0": '%s/iso/zstack_240.iso',
    "2.5.0": '%s/iso/zstack_250.iso',
    "2.6.0": '%s/iso/zstack_260.iso',
    "3.0.0": '%s/iso/zstack_260.iso',
    "3.0.1": '%s/iso/zstack_301.iso',
    "3.1.0": '%s/iso/zstack_310.iso',
    "3.1.3": '%s/iso/zstack_310.iso',
    "3.2.0": '%s/iso/zstack_320.iso',
    "3.3.0": '%s/iso/zstack_330.iso',
    # "3.4.0"
    # "3.5.0"
    # "3.5.1"
    # "3.5.2"
}

bin_path = '%s/installation-package/zstack-installer-%s.bin'


def initial(management_ip):
    # todo: zsha2_vip

    make_ssh_no_password(management_ip, tmp_file)
    update_old_repo(management_ip, tmp_file)

    # vm_cond = res_ops.gen_query_conditions('vmNics.ip', '=', management_ip)
    # vm = sce_ops.query_resource(zstack_management_ip, res_ops.VM_INSTANCE, vm_cond).inventories[0]
    #
    # volume_image_cond = res_ops.gen_query_conditions("name", "=", data_image_name)
    # volume_image = sce_ops.query_resource(zstack_management_ip, res_ops.IMAGE, volume_image_cond).inventories[0]
    #
    # data_volume_name = 'Test_feature__data_volume_for_nightly'
    # ps_uuid = vm.allVolumes[0].primaryStorageUuid
    # data_volume = sce_ops.create_volume_from_template(zstack_management_ip, volume_image.uuid, ps_uuid,
    #                                                   data_volume_name, vm.hostUuid,
    #                                                   systemtags=['capability::virtio-scsi'])
    #
    # test_util.test_dsc('attach the data volume to vm')
    # sce_ops.attach_volume(zstack_management_ip, data_volume.uuid, vm.uuid)
    #
    # tag_cond = res_ops.gen_query_conditions("resourceUuid", "=", data_volume.uuid)
    # tags = sce_ops.query_resource(zstack_management_ip, res_ops.SYSTEM_TAG, tag_cond).inventories
    # for tag in tags:
    #     if "kvm::volume" in tag.tag:
    #         wwn = tag.tag.split("::")[2]
    #         break
    # # mount
    # mount_volume(management_ip, wwn)


def mount_volume(management_ip, wwn):
    ssh_cmd = "ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s" % management_ip
    test_util.test_logger("MN Mount Volume")

    cmd = "touch /root/mount_volume.sh & chmod a+x /root/mount_volume.sh"
    test_lib.lib_execute_ssh_cmd(management_ip, "root", "password", cmd)
    shell_script = '''
    mkdir -p %s
    device="/dev/`ls -l /dev/disk/by-id | grep %s | awk \'{print \$11}\' | awk -F/ \'{print \$3}\' | tail -n1`"
    mount ${device} %s
    ''' % (mount_point, wwn, mount_point)
    with open("/root/mount_volume.sh", "w+") as f:
        f.write(shell_script)

    scp_file_to_vm(management_ip, "/root/mount_volume.sh", "/root/mount_volume.sh")
    cmd = "%s bash /root/mount_volume.sh" % ssh_cmd
    if test_lib.lib_execute_ssh_cmd(management_ip, "root", "password", cmd):
        test_util.test_logger("Mount Volume success")
    else:
        test_util.test_fail("Mount Volume faild")


def upgrade_mn(management_ip, current_version, next_version):
    print "\nUpgrade MN: %s ----> %s" % (current_version, next_version)
    # # upgrade_iso
    # if iso_dict[current_version] != iso_dict[next_version]:
    #     test_util.test_logger("upgrade iso %s --> %s" % (iso_dict[current_version], iso_dict[next_version]))
    #     upgrade_iso(management_ip, iso_dict[next_version] % mount_point)
    #
    # # upgrade_bin
    # test_util.test_logger("upgrade bin %s --> %s" % (current_version, next_version))
    # next_version_bin = "%s/installation-package/zstack-installer-%s.bin" % (mount_point, next_version)
    # upgrade_bin(management_ip, next_version_bin)
    # # check mn

    test_util.test_logger('Upgrade zstack to %s' % next_version)
    upgrade_pkg = os.environ.get('zstackPkg_%s' % next_version)
    upgrade_zstack(management_ip, upgrade_pkg, tmp_file)
    start_mn(management_ip)

    # todo check resource status


def upgrade_iso(management_ip, iso_path):
    ssh_cmd = "ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s" % management_ip
    iso_mount_point = "/tmp/%s" % uuid.uuid1().get_hex()
    test_lib.lib_execute_ssh_cmd(management_ip, "root", "password", "mkdir %s" % iso_mount_point)
    zstack_upgrade_path = "%s/scripts/zstack-upgrade" % iso_mount_point

    mount_cmd = "mount %s %s" % (iso_path, iso_mount_point)
    cmd = "%s %s" % (ssh_cmd, mount_cmd)
    process_result = execute_shell_in_process(cmd, tmp_file)

    if process_result != 0:
        test_util.test_fail('mount iso faild')
    else:
        test_util.test_logger('mount iso success')

    cp_cmd = "echo 'y' | cp %s /opt/; umount %s;" % (zstack_upgrade_path, iso_mount_point)
    test_lib.lib_execute_ssh_cmd(management_ip, "root", "password", cp_cmd)
    upgrade_cmd = "/opt/zstack-upgrade -r ../../../%s" % iso_path
    cmd = "%s %s" % (ssh_cmd, upgrade_cmd)
    process_result = execute_shell_in_process(cmd, tmp_file)

    if process_result != 0:
        test_util.test_fail('upgrade iso faild')
    else:
        test_util.test_logger('upgrade iso success')


def upgrade_bin(management_ip, bin_path):
    ssh_cmd = "ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null %s" % management_ip
    upgrade_cmd = "WEBSITE='%s' bash %s -u" % ('localhost', bin_path)
    cmd = "%s %s" % (ssh_cmd, upgrade_cmd)

    process_result = execute_shell_in_process(cmd, tmp_file)

    if process_result != 0:
        test_util.test_fail('upgrade_zstack faild')
    else:
        test_util.test_logger('upgrade_zstack success')


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
