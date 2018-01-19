'''
Test for auto reconnect sftp/imagestore bs

@author: quarkonics
'''

import os
import time
import commands
#import sys

import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.primarystorage_operations as ps_ops
DefaultFalseDict = test_lib.DefaultFalseDict

_config_ = {
        'timeout' : 360,
        'noparallel' : True
        }

case_flavor = dict(stop_sftp=             DefaultFalseDict(sftp=True, imagestore=False, kill=False),
                   kill_sftp=             DefaultFalseDict(sftp=True, imagestore=False, kill=True),
                   stop_imagestore=             DefaultFalseDict(sftp=False, imagestore=True, kill=False),
                   kill_imagestore=             DefaultFalseDict(sftp=False, imagestore=True, kill=True),
                   )


def test():
    flavor = case_flavor[os.environ.get('CASE_FLAVOR')]
    test_util.test_dsc('bs auto reconnection check test')
    if flavor['sftp']:
        conditions = res_ops.gen_query_conditions('type', '=', 'SftpBackupStorage')
    if flavor['imagestore']:
        conditions = res_ops.gen_query_conditions('type', '=', 'ImageStoreBackupStorage')

    resource_type = res_ops.BACKUP_STORAGE
    bss = res_ops.query_resource(resource_type, conditions)
    if len(bss) == 0:
        test_util.test_skip('Skip due to no backup storage available')

    test_util.test_logger("kill bs agent on storage %s" % (bss[0].uuid))
    if flavor['sftp']:
        if flavor['kill']:
            cmd = "pkill -9 -f 'from sftpbackupstorage import sftpbackupstoragedaemon'"
        else:
            cmd = "service zstack-sftpbackupstorage stop"
    elif flavor['imagestore']:
        if flavor['kill']:
            cmd = "pkill -9 -f '/usr/local/zstack/imagestore/bin/zstore -conf'"
        else:
            cmd = "service zstack-imagestorebackupstorage stop"

    bs_host = test_lib.lib_get_backup_storage_host(bss[0].uuid)
    if bs_host.username != 'root':
        cmd = "sudo %s" % (cmd)
    if not bs_host.sshPort:
        bs_host.sshPort = 22
    if test_lib.lib_execute_ssh_cmd(bs_host.managementIp, bs_host.username, bs_host.password, cmd,  timeout = 120, port = int(bs_host.sshPort)) == False:
        test_util.test_fail("CMD:%s execute failed on %s" %(cmd, bs_host.managementIp))

    test_util.test_logger("bs %s is expected to disconnect and start reconnect automatically" % (bss[0].uuid))
    conditions = res_ops.gen_query_conditions('uuid', '=', bss[0].uuid)
    count = 0
    while count < 24:
        bs = res_ops.query_resource(resource_type, conditions)[0]
        if bs.status == "Connecting":
            break

        time.sleep(5)
        count += 1

    if bs.status != "Connecting":
        test_util.test_fail("bs %s is not disconnect and start reconnect automatically in 120 seconds" % (bss[0].uuid))

    test_util.test_logger("bs %s is expected to reconnect success automatically" % (bss[0].uuid))
    count = 0
    while count < 24:
        bs = res_ops.query_resource(resource_type, conditions)[0]
        if bs.status == "Connected":
            break

        time.sleep(5)
        count += 1

    if bs.status != "Connected":
        test_util.test_fail("bs %s not reconnect success automatically in 120 seconds" % (bss[0].uuid))

    test_util.test_pass("Auto reconnect backup storage pass")
