'''
This is a per test case setup that do setup work before test case execution
@author: Quarkonics
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.deploy_operations as deploy_operations
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.zone_operations as zone_operations
import zstackwoodpecker.operations.backupstorage_operations as bs_operations
import os
import time

def check_resource():
    vrs = res_ops.query_resource(res_ops.APPLIANCE_VM, [], None)
    for vr in vrs:
        if vr.status != "Connected":
            return False
    hosts = res_ops.query_resource(res_ops.HOST, [], None)
    for host in hosts:
        if host.status != "Connected":
            return False

    pss = res_ops.query_resource(res_ops.PRIMARY_STORAGE, [], None)
    for ps in pss:
        if ps.status != "Connected":
            return False

    bss = res_ops.query_resource(res_ops.BACKUP_STORAGE, [], None)
    for bs in bss:
        if bs.status != "Connected":
            return False

    return True


def test():
    test_util.test_logger('Check test environment before test case execution')
    checker_count = 0
    while True:
        if check_resource():
            test_util.test_logger('Check test environment before test case execution success')
            return
        time.sleep(1)
        checker_count += 1
        if checker_count > 120:
            test_util.test_fail('Test resource not ready for test')
