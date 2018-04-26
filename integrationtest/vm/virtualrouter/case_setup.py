'''
This is a per test case setup that do setup work before test case execution
@author: Quarkonics
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.deploy_operations as deploy_operations
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.zone_operations as zone_operations
import zstackwoodpecker.operations.backupstorage_operations as bs_ops
import zstackwoodpecker.operations.primarystorage_operations as ps_ops
import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import os
import time

def check_resource():

    hosts = res_ops.query_resource(res_ops.HOST, [], None)
    for host in hosts:
        if host.status != "Connected":
            host_ops.reconnect_host(host.uuid) 
            return False

    pss = res_ops.query_resource(res_ops.PRIMARY_STORAGE, [], None)
    for ps in pss:
        if ps.status != "Connected":
            ps_ops.reconnect_primary_storage(ps.uuid)
            return False

    bss = res_ops.query_resource(res_ops.BACKUP_STORAGE, [], None)
    for bs in bss:
        if bs.status != "Connected":
            bs_ops.reconnect_backup_storage(bs.uuid)
            return False

    if os.environ.get('WOODPECKER_PARALLEL') != None and os.environ.get('WOODPECKER_PARALLEL') == '0':
        vms = res_ops.query_resource(res_ops.VM_INSTANCE, [], None)
        for vm in vms:
            if vm.type == 'UserVm':
                try:
                    vm_ops.destroy_vm(vm.uuid)
                except:
                    test_util.test_logger('ignore exception try to destroy vm')
                try:
                    vm_ops.expunge_vm(vm.uuid)
                except:
                    test_util.test_logger('ignore exception try to expunge vm')

    vrs = res_ops.query_resource(res_ops.APPLIANCE_VM, [], None)
    for vr in vrs:
        if vr.status != "Connected" or vr.state != "Running":
            if vr.applianceVmType != "vrouter":
		try:
                    vm_ops.stop_vm(vr.uuid, force='cold')
                    vm_ops.start_vm(vr.uuid)
                except:
                    test_util.test_logger('Exception when reboot vr vm')
            else:
                try:
                    vm_ops.stop_vm(vr.uuid, force='cold')
                except:
                    test_util.test_logger('Exception when reboot vr vm')
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
