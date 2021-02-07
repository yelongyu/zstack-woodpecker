'''
Test for auto reconnect ceph bs

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

case_flavor = dict(kill_bs=             DefaultFalseDict(bs=True, kill=True),
                   stop_bs=             DefaultFalseDict(bs=True, kill=False),
                   kill_ps=             DefaultFalseDict(bs=False, kill=True),
                   stop_ps=             DefaultFalseDict(bs=False, kill=False),
                   )


def test():
    flavor = case_flavor[os.environ.get('CASE_FLAVOR')]
    test_util.test_dsc('ceph auto reconnection check test')

    conditions = res_ops.gen_query_conditions('type', '=', 'Ceph')
    if flavor['bs']:
        resource_type = res_ops.BACKUP_STORAGE
    else:
        resource_type = res_ops.PRIMARY_STORAGE
    bpss = res_ops.query_resource(resource_type, conditions)
    if len(bpss) == 0:
        test_util.test_skip('Skip due to no ceph storage available')
    if len(bpss[0].mons) == 1:
        test_util.test_skip('Skip due to only one mon in ceph storage')

    ceph_mon = bpss[0].mons[0]
    test_util.test_logger("kill ceph agent on one mon of ceph storage %s" % (bpss[0].uuid))
    if flavor['bs']:
        if flavor['kill']:
            cmd = "pkill -9 -f 'from cephbackupstorage import cdaemon'"
        else:
            cmd = "service zstack-ceph-backupstorage stop"
    else:
        if flavor['kill']:
            cmd = "pkill -9 -f 'from cephprimarystorage import cdaemon'"
        else:
            cmd = "service zstack-ceph-primarystorage stop"
    if test_lib.lib_execute_ssh_cmd(ceph_mon.hostname, ceph_mon.sshUsername, ceph_mon.sshPassword, cmd,  timeout = 120) == False:
        test_util.test_fail("CMD:%s execute failed on %s" %(cmd, ceph_mon.hostname))

    test_util.test_logger("ceph mon of %s is expected to disconnect and start reconnect automatically" % (bpss[0].uuid))
    conditions = res_ops.gen_query_conditions('uuid', '=', bpss[0].uuid)
    count = 0
    while count < 24:
        bps = res_ops.query_resource(resource_type, conditions)[0]
        if bps.status != "Connected":
            test_util.test_fail("ceph storage is not expected to disconnect for only one mon disconnected")

        for mon in bps.mons:
            if mon.monUuid == bpss[0].mons[0].monUuid:
                mon_status = mon.status

        if mon_status == "Connecting":
            break

        time.sleep(5)
        count += 1

    if mon_status != "Connecting":
        test_util.test_fail("ceph storage %s mon is not disconnect and start reconnect automatically in 120 seconds" % (bpss[0].uuid))

    test_util.test_logger("ceph mon of storage %s is expected to reconnect success automatically" % (bpss[0].uuid))
    count = 0
    while count < 24:
        bps = res_ops.query_resource(resource_type, conditions)[0]
        if bps.status != "Connected":
            test_util.test_fail("ceph storage is not expected to disconnect for only one mon disconnected")

        for mon in bps.mons:
            if mon.monUuid == bpss[0].mons[0].monUuid:
                mon_status = mon.status

        if mon_status == "Connected":
            break

        time.sleep(5)
        count += 1

    if mon_status != "Connected":
        test_util.test_fail("ceph storage %s mon not reconnect success automatically in 120 seconds" % (bpss[0].uuid))
       
    test_util.test_logger("kill ceph storage agent on all mon of ceph storage %s" % (bpss[0].uuid))
    for ceph_mon in bpss[0].mons:
        if test_lib.lib_execute_ssh_cmd(ceph_mon.hostname, ceph_mon.sshUsername, ceph_mon.sshPassword, cmd,  timeout = 120) == False:
            test_util.test_fail("CMD:%s execute failed on %s" %(cmd, ceph_mon.hostname))

    test_util.test_logger("ceph mon of storage %s is expected to disconnect and start reconnect automatically" % (bpss[0].uuid))
    conditions = res_ops.gen_query_conditions('uuid', '=', bpss[0].uuid)
    count = 0
    while count < 48:
        bps = res_ops.query_resource(resource_type, conditions)[0]
        if bps.status == "Connecting":
            break

        time.sleep(5)
        count += 1

    if bps.status != "Connecting":
        test_util.test_fail("ceph storage %s is not disconnect and start reconnect automatically in 240 seconds" % (bpss[0].uuid))

    test_util.test_logger("ceph storage %s is expected to reconnect success automatically" % (bpss[0].uuid))
    count = 0
    while count < 24:
        bps = res_ops.query_resource(resource_type, conditions)[0]
        if bps.status == "Connected":
            break

        time.sleep(5)
        count += 1

    if bps.status != "Connected":
	test_util.test_fail("ceph storage %s not reconnect success automatically in 120 seconds" % (bpss[0].uuid))

    test_util.test_pass("Auto reconnect ceph storage pass")
