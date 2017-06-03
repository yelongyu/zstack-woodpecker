'''

New Integration test for checking logs

@author: SyZhao
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.header.host as host_header
import zstacklib.utils.ssh as ssh
import os
import os.path
import re

_config_ = {
        'timeout' : 600,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
TEMPT_FOLDER = "/tmp/"
#MEVOCO_LOG_FOLDER = r"collect-log-mevoco*"
#MEVOCO_LOG_FOLDER_PATTERN = "collect-log-mevoco"
MEVOCO_LOG_FOLDER = r"collect-log-zstack*"
MEVOCO_LOG_FOLDER_PATTERN = "collect-log-zstack"
MEVOCO_LOG_FOLDER_MASK = ".gz"
MEVOCO_LOG_PATH = None


def find_mevoco_log_folder_name():
    global MEVOCO_LOG_FOLDER, MEVOCO_LOG_PATH, MEVOCO_LOG_FOLDER_PATTERN
    #if not test_lib.lib_check_version_is_mevoco():
    #    MEVOCO_LOG_FOLDER = r"collect-log-zstack*"
    #	MEVOCO_LOG_FOLDER_PATTERN = "collect-log-zstack"
    temptNameList = os.listdir(TEMPT_FOLDER)
    for folderName in temptNameList:
        print "Start"
        print "folderName=%s" %(folderName)
        print "MEVOCO_LOG_FOLDER_PATTERN=%s" %(MEVOCO_LOG_FOLDER_PATTERN)
        print "MEVOCO_LOG_FOLDER_MASK=%s" %(MEVOCO_LOG_FOLDER_MASK)
        if MEVOCO_LOG_FOLDER_PATTERN in folderName and not MEVOCO_LOG_FOLDER_MASK in folderName:
            MEVOCO_LOG_FOLDER = folderName
            MEVOCO_LOG_PATH = TEMPT_FOLDER + MEVOCO_LOG_FOLDER + "/"
            print "MEVOCO_LOG_PATH=%s" %(MEVOCO_LOG_PATH)

def test():
    #str = str(os.listdir('/home'))
    #if 'scenario' in str:
    #    test_util.test_skip('Not available environment to run this case')

    path = "/home"
    pathlist = os.listdir(path)
    for path in pathlist:
        if re.findall(r'\d+.\d+.\d+.\d+', path):
            target_path = path

    if os.path.exists('/home/' + target_path + '/scenario-file.xml'):
        test_util.test_skip('Not available environment to run this case')

    global MEVOCO_LOG_FOLDER, MEVOCO_LOG_PATH, MEVOCO_LOG_FOLDER_PATTERN
    #if not test_lib.lib_check_version_is_mevoco():
    #    MEVOCO_LOG_FOLDER = r"collect-log-zstack*"
    #	MEVOCO_LOG_FOLDER_PATTERN = "collect-log-zstack"

    #Step1: clean env below TEMPT_FOLDER and run collect log
    retVal = os.system(" cd " + TEMPT_FOLDER  + "; rm -rf " + MEVOCO_LOG_FOLDER + "; zstack-ctl collect_log")

    if retVal != 0:
        test_util.test_logger("os.system return value: %d" % (retVal))
        test_util.test_fail('run zstack-ctl collect_log failed.')


    #Step2: refresh MEVOCO_LOG_FOLDER value to real one below TEMPT_FOLDER
    find_mevoco_log_folder_name()


    #Step3: verify sftpbackupstorage logs are saved
    bs_cond = res_ops.gen_query_conditions("status", '=', "Connected")
    bss = res_ops.query_resource_fields(res_ops.BACKUP_STORAGE, bs_cond, \
            None, fields=['uuid', 'type'])
    if not bss:
        test_util.test_skip("not find available backup storage. Skip test")


    for bs in bss:
        #test_util.test_logger(bs.dump())
        if bs.type == "SftpBackupStorage":
            #bs_sftp_cond = res_ops.gen_query_conditions("type", "=", "SftpBackupStorage")
            #hostIP = res_ops.query_resource_fields(res_ops.BACKUP_STORAGE, bs_sftp_cond, None, fields=["hostname"])
            hostIP = test_lib.lib_get_backup_storage_host(bs.uuid) 

            sftpLogFolderName = "sftp_bs-" + hostIP.managementIp 
            print "logPath=%s" %(MEVOCO_LOG_PATH)
            print "sftpLogFolderName=%s" %(sftpLogFolderName)
            dmesgFilePath             = MEVOCO_LOG_PATH + sftpLogFolderName + "/dmesg"
            hostInfoFilePath          = MEVOCO_LOG_PATH + sftpLogFolderName + "/host_info"
            messagesFilePath          = MEVOCO_LOG_PATH + sftpLogFolderName + "/messages"
            sftpbackupstorageFilePath = MEVOCO_LOG_PATH + sftpLogFolderName + "/zstack-sftpbackupstorage.log"

            if not os.path.exists(dmesgFilePath):
                test_util.test_fail( dmesgFilePath             + ' is not exist.')
            if not os.path.exists(hostInfoFilePath):
                test_util.test_fail( hostInfoFilePath          + ' is not exist.')
            if not os.path.exists(messagesFilePath):
                test_util.test_fail( messagesFilePath          + ' is not exist.')
            if not os.path.exists(sftpbackupstorageFilePath):
                test_util.test_fail( sftpbackupstorageFilePath + ' is not exist.')
        #elif bs.type == "ImageStoreBackupStorage":
        #    pass
        else:
            test_util.test_skip("backup storage is not sftp, skip")


    #Step4: verify hosts logs are saved
    #conditions = res_ops.gen_query_conditions('state', '=', host_header.ENABLED)
    #conditions = res_ops.gen_query_conditions('status', '=', host_header.CONNECTED, conditions)
    #all_hosts = res_ops.query_resource(res_ops.HOST, conditions)
    #if len(all_hosts) < 1:
    #    test_util.test_skip('Not available host to check')

    #for host in all_hosts:
    #    hostFolderName = host.managementIp
    #    dmesgFilePath    = MEVOCO_LOG_PATH + hostFolderName + "/dmesg"
    #    hostInfoFilePath = MEVOCO_LOG_PATH + hostFolderName + "/host_info"
    #    messagesFilePath = MEVOCO_LOG_PATH + hostFolderName + "/messages"
    #    kvmagentFilePath = MEVOCO_LOG_PATH + hostFolderName + "/zstack-kvmagent.log"
    #    zstackFilePath   = MEVOCO_LOG_PATH + hostFolderName + "/zstack.log"

    #    if not os.path.exists(dmesgFilePath):
    #        test_util.test_fail( dmesgFilePath    + ' is not exist.')
    #    if not os.path.exists(hostInfoFilePath):
    #        test_util.test_fail( hostInfoFilePath + ' is not exist.')
    #    if not os.path.exists(messagesFilePath):
    #        test_util.test_fail( messagesFilePath + ' is not exist.')
    #    if not os.path.exists(kvmagentFilePath):
    #        test_util.test_fail( kvmagentFilePath + ' is not exist.')
    #    if not os.path.exists(zstackFilePath):
    #        test_util.test_fail( zstackFilePath   + 'is not exist.')


    #Step5: verify management node logs are saved
    #conditions = res_ops.gen_query_conditions("status", '=', "Connected")
    all_mn = res_ops.query_resource(res_ops.MANAGEMENT_NODE)
    if len(all_mn) < 1:
        test_util.test_skip('Not available mn to check')

    for mn in all_mn:
        mnHostIP = mn.hostName
        mnFolderName = "management-node-" + mnHostIP
        dmesgFilePath    = MEVOCO_LOG_PATH + mnFolderName + "/dmesg"
        hostInfoFilePath = MEVOCO_LOG_PATH + mnFolderName + "/host_info"
        messagesFilePath = MEVOCO_LOG_PATH + mnFolderName + "/messages"
        manageServerPath = MEVOCO_LOG_PATH + mnFolderName + "/management-server.log"

        if not os.path.exists(dmesgFilePath):
            test_util.test_fail( dmesgFilePath    + ' is not exist.')
        if not os.path.exists(hostInfoFilePath):
            test_util.test_fail( hostInfoFilePath + ' is not exist.')
        if not os.path.exists(messagesFilePath):
            test_util.test_fail( messagesFilePath + ' is not exist.')
        if not os.path.exists(manageServerPath):
            test_util.test_fail( manageServerPath + ' is not exist.')


#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
