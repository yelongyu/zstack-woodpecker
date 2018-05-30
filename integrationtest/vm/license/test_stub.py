'''

Create an unified test_stub to share test operations

@author: Quarkonics
'''

import os
import subprocess
import time
import datetime
import uuid

import apibinding.api_actions as api_actions
import apibinding.inventory as inventory

import zstacklib.utils.ssh as ssh
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.license_operations as lic_ops
import zstackwoodpecker.operations.account_operations as acc_ops

TEST_TIME = 120

lic_issued_date = None
lic_expired_date = None
def get_license_info():
    global lic_issued_date
    global lic_expired_date
    lic_info = lic_ops.get_license_info().inventory
    if lic_issued_date == None or lic_expired_date != None:
        lic_issued_date = lic_info.issuedDate
    lic_expired_date = lic_info.expiredDate
    return lic_info

def get_license_addons_info():
    global lic_issued_date
    global lic_expired_date
    lic_info = lic_ops.get_license_addons_info().inventory
    if lic_issued_date == None or lic_expired_date != None:
        lic_issued_date = lic_info.issuedDate
    lic_expired_date = lic_info.expiredDate
    return lic_info

def get_license_issued_date():
    global lic_issued_date
    if lic_issued_date == None or lic_expired_date == None:
        get_license_info()
    return lic_issued_date

def get_license_addons_issued_date():
    global lic_issued_date
    if lic_issued_date == None or lic_expired_date == None:
        get_license_addons_info()
    return lic_issued_date

def get_license_expired_date():
    global lic_expired_date
    if lic_expired_date == None:
        get_license_info()
    return lic_expired_date

def get_license_addons_expired_date():
    global lic_expired_date
    if lic_expired_date == None:
        get_license_addons_info()
    return lic_expired_date

def execute_shell_in_process(cmd, timeout=10, logfd=None):
    if not logfd:
        process = subprocess.Popen(cmd, executable='/bin/sh', shell=True, universal_newlines=True)
    else:
        process = subprocess.Popen(cmd, executable='/bin/sh', shell=True, stdout=logfd, stderr=logfd, universal_newlines=True)

    start_time = time.time()
    while process.poll() is None:
        curr_time = time.time()
        TEST_TIME = curr_time - start_time
        if TEST_TIME > timeout:
            process.kill()
            test_util.test_logger('[shell:] %s timeout ' % cmd)
            return False
        time.sleep(1)

    test_util.test_logger('[shell:] %s is finished.' % cmd)
    return process.returncode

def execute_shell_in_process_stdout(cmd, tmp_file, timeout = 1200, no_timeout_excep = False):
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

def reload_default_license():
    execute_shell_in_process('rm -rf /var/lib/zstack/license/license.txt')
    result = lic_ops.reload_license()

def gen_license(customer_name, user_name, duration, lic_type, cpu_num, host_num):
    tmp_file = '/tmp/%s' % uuid.uuid1().get_hex()
    license_script = os.environ.get('licenseGenScript') 
    lic_info = lic_ops.get_license_info()
    test_util.test_logger("bash '%s' '%s' '%s' '%s' '%s' '%s' '%s' '%s'" % (license_script, customer_name, user_name, duration, lic_type, cpu_num, host_num, lic_info.inventory.licenseRequest))
    (ret, file_path) = execute_shell_in_process_stdout("bash '%s' '%s' '%s' '%s' '%s' '%s' '%s' '%s'" % (license_script, customer_name, user_name, duration, lic_type, cpu_num, host_num, lic_info.inventory.licenseRequest), tmp_file)
    return file_path

def gen_other_license(customer_name, user_name, duration, lic_type, cpu_num, host_num):
    tmp_file = '/tmp/%s' % uuid.uuid1().get_hex()
    license_script = os.environ.get('licenseGenScript') 
    request_key1 = os.environ.get('licenseRequestKey') 
    with open(request_key1.strip('\n'), 'r') as request_key2:
        request_key = request_key2.read()
    #lic_info = lic_ops.get_license_info()
    test_util.test_logger("bash '%s' '%s' '%s' '%s' '%s' '%s' '%s' '%s'" % (license_script, customer_name, user_name, duration, lic_type, cpu_num, host_num, request_key))
    (ret, file_path) = execute_shell_in_process_stdout("bash '%s' '%s' '%s' '%s' '%s' '%s' '%s' '%s'" % (license_script, customer_name, user_name, duration, lic_type, cpu_num, host_num, request_key), tmp_file)
    return file_path

def gen_addons_license(customer_name, user_name, duration, lic_type, cpu_num, host_num, pro_mode):
    tmp_file = '/tmp/%s' % uuid.uuid1().get_hex()
    license_script = os.environ.get('licenseGenScript') 
    lic_info = lic_ops.get_license_addons_info()
    test_util.test_logger("bash '%s' '%s' '%s' '%s' '%s' '%s' '%s' '%s' '%s'" % (license_script, customer_name, user_name, duration, lic_type, cpu_num, host_num, lic_info.inventory.licenseRequest, pro_mode))
    (ret, file_path) = execute_shell_in_process_stdout("bash '%s' '%s' '%s' '%s' '%s' '%s' '%s' '%s' '%s'" % (license_script, customer_name, user_name, duration, lic_type, cpu_num, host_num, lic_info.inventory.licenseRequest, pro_mode), tmp_file)
    return file_path

def load_license(file_path):
    execute_shell_in_process('zstack-ctl install_license --license %s' % file_path)
    result = lic_ops.reload_license()

def check_license(user_name, cpu_num, host_num, expired, lic_type, issued_date=None, expired_date=None):
    if issued_date == None:
        issued_date = get_license_issued_date()
    if expired_date == None:
        expired_date = get_license_expired_date()
    lic_info = lic_ops.get_license_info().inventory
    if lic_info.user != user_name:
        test_util.test_fail("License user info not correct")
    if lic_info.cpuNum != cpu_num:
        test_util.test_fail("License cpu info not correct")
    if lic_info.hostNum != host_num:
        test_util.test_fail("License host info not correct")
    if lic_info.expired != expired:
        test_util.test_fail("License expire info not correct")
    if lic_info.licenseType != lic_type:
        test_util.test_fail("License type info not correct")
    if lic_info.issuedDate != issued_date:
        test_util.test_fail("License issue date info not correct")
    if lic_info.expiredDate != expired_date:
        test_util.test_fail("License expire date info not correct")

def check_license_addons(expired, lic_type, issued_date=None, expired_date=None):
    if issued_date == None:
        issued_date = get_license_addons_issued_date()
    if expired_date == None:
        expired_date = get_license_addons_expired_date()
    lic_info = lic_ops.get_license_addons_info().inventory
    if lic_info.expired != expired:
        test_util.test_fail("License expire info not correct")
    if lic_info.licenseType != lic_type:
        test_util.test_fail("License type info not correct")
    if lic_info.issuedDate != issued_date:
        test_util.test_fail("License issue date info not correct")
    if lic_info.expiredDate != expired_date:
        test_util.test_fail("License expire date info not correct")

def license_date_cal(issued_date, duration):
    try:
        issued_time = time.mktime(time.strptime(issued_date, '%Y-%m-%d %H:%M:%S.0'))
        expired_time = issued_time + duration
        expired_date = datetime.datetime.fromtimestamp(expired_time).strftime('%Y-%m-%d %H:%M:%S.0')
    except:
        issued_time = time.mktime(time.strptime(issued_date, '%Y-%m-%dT%H:%M:%S.000+08:00'))
        expired_time = issued_time + duration
        expired_date = datetime.datetime.fromtimestamp(expired_time).strftime('%Y-%m-%dT%H:%M:%S.000+08:00')
    return expired_date

def create_zone(zone_name='ZONE1', session_uuid=None):
    action = api_actions.CreateZoneAction()
    action.name = zone_name
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    test_util.action_logger('Add Zone [uuid:] %s [name:] %s' % \
            (evt.uuid, action.name))
    return evt.inventory

def create_image_store_backup_storage(bs_name, bs_hostname, bs_username, bs_password, bs_url, bs_sshport, session_uuid=None):
    action = api_actions.AddImageStoreBackupStorageAction()
    action.name = bs_name
    action.url = bs_url
    action.hostname = bs_hostname
    action.username = bs_username
    action.password = bs_password
    action.sshPort = bs_sshport
    evt = acc_ops.execute_action_with_session(action, session_uuid)
    test_util.action_logger('Create Sftp Backup Storage [uuid:] %s [name:] %s' % \
            (evt.inventory.uuid, action.name))
    return evt.inventory

