'''

Clean up test case remnants

@author: Youyk
'''
import threading
import time
import sys
import os
import errno
import traceback

import apibinding.api as api
import apibinding.inventory as inventory
import apibinding.api_actions as api_actions
import zstacklib.utils.http as http
import zstacklib.utils.jsonobject as jsonobject
import zstacklib.utils.log as log
import zstacklib.utils.linux as linux
import zstacklib.utils.ssh as ssh
import zstacktestagent.plugins.vm as vm_plugin
import zstacktestagent.plugins.host as host_plugin
import zstacktestagent.testagent as testagent
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.header.host as host_header
import zstackwoodpecker.operations.config_operations as con_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.operations.account_operations as acc_ops

#logger = log.get_logger(__name__)

def _get_host_ip(vm_inv, session_uuid):
    if not vm_inv.hostUuid:
        host_uuid = vm_inv.lastHostUuid
    else:
        host_uuid = vm_inv.hostUuid
    if not host_uuid:
        test_util.test_logger("Host UUID is None. Can't get Host IP address")
        return None
    ret = res_ops.get_resource(res_ops.HOST, session_uuid, uuid=host_uuid)[0]
    return ret.managementIp

def _delete_file(host_ip, path):
    cmd = host_plugin.HostShellCmd()
    cmd.command = "rm -rf %s" % path 
    test_util.test_logger("Delete file: %s in Host: %s" % (path, host_ip))
    http.json_dump_post(testagent.build_http_path(host_ip, host_plugin.HOST_SHELL_CMD_PATH), cmd)

def _delete_files(host_ip, path):
    cmd = host_plugin.HostShellCmd()
    cmd.command = "rm -rf %s*" % path 
    test_util.test_logger("Delete files: %s in Host: %s" % (path, host_ip))
    http.json_dump_post(testagent.build_http_path(host_ip, host_plugin.HOST_SHELL_CMD_PATH), cmd)

def _rm_folder_contents_violently(host_ip, path):
    cmd = host_plugin.HostShellCmd()
    cmd.command = "rm -rf %s/*" % path 
    try:
        http.json_dump_post(testagent.build_http_path(host_ip, host_plugin.HOST_SHELL_CMD_PATH), cmd)
    except Exception as e:
        err = linux.get_exception_stacktrace()
        test_util.test_logger("Fail to delete contents in folder: %s in Host: %s" % (path, host_ip))
        test_util.test_logger(err)

    test_util.test_logger("Successfully delete contents in folder: %s in Host: %s" % (path, host_ip))

def _umount_folder_violently(host_ip, path):
    cmd = host_plugin.HostShellCmd()
    cmd.command = "umount %s" % path 
    try:
        http.json_dump_post(testagent.build_http_path(host_ip, host_plugin.HOST_SHELL_CMD_PATH), cmd)
    except Exception as e:
        err = linux.get_exception_stacktrace()
        test_util.test_logger("Fail to umount folder: %s in Host: %s" % (path, host_ip))
        test_util.test_logger(err)

    test_util.test_logger("Umount folder: %s in Host: %s" % (path, host_ip))
    
def _destroy_vm_violently(host_ip, uuid):
    cmd = vm_plugin.DeleteVmCmd()
    cmd.vm_uuids = [uuid]
    http.json_dump_post(testagent.build_http_path(host_ip, vm_plugin.DELETE_VM_PATH), cmd)

def _async_api_call(action):
    api_client = api.Api()
    session_uuid = api_client.login_as_admin()
    api_client.set_session_to_api_message(action, session_uuid)
    return api_client.async_call_wait_for_complete(action)

def _sync_api_call(action):
    api_client = api.Api()
    session_uuid = api_client.login_as_admin()
    api_client.set_session_to_api_message(action, session_uuid)
    return api_client.sync_call(action)

def _clean_image_violently(backup_storage_uuid, account_uuid, zone_uuid, host_ip, session_uuid):
    result = res_ops.get_resource(res_ops.IMAGE, session_uuid) 
    image_path = None
    for image in result:
        for backup_storage in image.backupStorageRefs:
            if backup_storage.uuid == backup_storage_uuid:
                image_path = os.path.dirname(backup_storage.installPath)

    #Delete Backup Storage Files
    if image_path:
        _delete_file(host_ip, image_path)

def _clean_volume_violently(vm_all_volumes, backup_storage_uuid, account_uuid, zone_uuid, host_ip, session_uuid):
    volume_path = None
    for volume in vm_all_volumes:
        if not volume.installPath:
            continue
        volume_path = os.path.dirname(volume.installPath)
        #Delete Root Volume Files
        if volume_path:
            _delete_file(host_ip, volume_path)

    result = res_ops.get_resource(res_ops.PRIMARY_STORAGE, session_uuid) 
    image_cache_path = None

    for pri_storage in result:
        if pri_storage.zoneUuid == zone_uuid:
            image_cache_path = "%s/imagecache/template/%s" % (pri_storage.mountPath, backup_storage_uuid)
    
    #Delete Primary Storage Cache files
    if image_cache_path:
        _delete_file(host_ip, image_cache_path)

def umount_primary_storage_violently(host_ip, storage_mount_path):
    if storage_mount_path:
        _rm_folder_contents_violently(host_ip, storage_mount_path)
        _umount_folder_violently(host_ip, storage_mount_path)
        try:
            os.rmdir(storage_mount_path)
        except OSError as ex:
            if ex.errno == errno.ENOTEMPTY:
                test_util.test_logger("Folder %s is not safely umounted" % storage_mount_path)

def destroy_vm_and_storage_violently(vm, session_uuid):
    destroy_all_vm_and_vips()
    vm_inv = inventory.VmInstanceInventory()
    vm_inv.evaluate(vm)
    vm_uuid = vm_inv.uuid
    vm_all_volumes = vm_inv.allVolumes
    backup_storage_uuid = vm_inv.imageUuid
    account_uuid = None
    zone_uuid = vm_inv.zoneUuid
    host_ip = _get_host_ip(vm_inv, session_uuid)

    if not host_ip:
        test_util.test_logger("Can't find Host for VM: %s" % vm_uuid)
        return

    _destroy_vm_violently(host_ip, vm_uuid)
    
    _clean_volume_violently(vm_all_volumes, backup_storage_uuid, account_uuid, zone_uuid, host_ip, session_uuid)
    _clean_image_violently(backup_storage_uuid, account_uuid, zone_uuid, host_ip, session_uuid)

def cleanup_all_vms_violently():
    destroy_all_vm_and_vips()
    session_uuid = acc_ops.login_as_admin()
    result = res_ops.get_resource(res_ops.VM_INSTANCE, session_uuid)
    for vm in result:
        thread = threading.Thread(target = destroy_vm_and_storage_violently\
                , args = (vm, session_uuid, ))
        thread.start()

    while threading.active_count() > 1:
        time.sleep(0.1)

    acc_ops.logout(session_uuid)

#Find a vm, whose zone use primary_storage. 
def _get_host_from_primary_storage(primary_storage_uuid, session_uuid):
    result = res_ops.get_resource(res_ops.PRIMARY_STORAGE, session_uuid, uuid=primary_storage_uuid)[0]
    hosts = res_ops.get_resource(res_ops.HOST, session_uuid)
    for host in hosts:
        if host.zoneUuid == result.zoneUuid:
            return host

def cleanup_none_vm_volumes_violently():
    session_uuid = acc_ops.login_as_admin()
    try:
        priSto_host_list = {}
        result = res_ops.get_resource(res_ops.VOLUME, session_uuid)
        for volume in result:
            if not volume.installPath:
                continue
            volume_path = os.path.dirname(volume.installPath)
            #VM volume has been cleanup in destroy_vm_and_storage_violently()
            if not volume.hasattr('vmInstanceUuid'):
                pri_sto_uuid = volume.primaryStorageUuid
                if priSto_host_list.has_key(pri_sto_uuid):
                    host_ip = priSto_host_list[pri_sto_uuid]
                else:
                    #TODO: need to add multi hosts, if primary storage is local storage.
                    host = _get_host_from_primary_storage(pri_sto_uuid, session_uuid)
                    host_ip = host.managementIp
                    priSto_host_list[pri_sto_uuid] = host_ip
                thread = threading.Thread(target = _delete_file, \
                        args = (host_ip, volume_path))
                thread.start()

        while threading.active_count() > 1:
            time.sleep(0.1)

    except Exception as e:
        test_util.test_logger("cleanup volumes violently meet exception")
        traceback.print_exc(file=sys.stdout)
        raise e
    finally:
        acc_ops.logout(session_uuid)

def umount_all_primary_storages_violently():
    session_uuid = acc_ops.login_as_admin()
    zones = res_ops.query_resource(res_ops.ZONE)
    for zone in zones:
        conditions = res_ops.gen_query_conditions('zoneUuid', '=', zone.uuid)
        conditions = res_ops.gen_query_conditions('state', '=', 'Enabled', conditions)
        pss = res_ops.query_resource(res_ops.PRIMARY_STORAGE, conditions, session_uuid)
        conditions = res_ops.gen_query_conditions('zoneUuid', '=', zone.uuid)
        conditions = res_ops.gen_query_conditions('state', '=', host_header.ENABLED, conditions)
        conditions = res_ops.gen_query_conditions('status', '=', host_header.CONNECTED, conditions)
        conditions = res_ops.gen_query_conditions('hypervisorType', '=', inventory.KVM_HYPERVISOR_TYPE, conditions)
        all_hosts = res_ops.query_resource(res_ops.HOST, conditions, session_uuid)
        for host in all_hosts:
            for ps in pss:
                ps_url = ps.mountPath
                thread = threading.Thread(\
                        target = umount_primary_storage_violently, \
                        args = (host.managementIp, ps_url))
                thread.start()

    while threading.active_count() > 1:
        time.sleep(0.1)

    acc_ops.logout(session_uuid)

def cleanup_backup_storage():
    cleanup_sftp_backup_storage()

def cleanup_sftp_backup_storage():
    backup_obj = test_lib.deploy_config.backupStorages
    sftp_backupstorages = backup_obj.get_child_node_as_list('sftpBackupStorage')
    for storage in sftp_backupstorages:
        cmd = 'rm -rf %s/rootVolumeTemplates/*' % storage.url_
        ssh.execute(cmd, storage.hostname_, storage.username_, storage.password_)
        cmd = 'rm -rf %s/dataVolumeTemplates/*' % storage.url_
        ssh.execute(cmd, storage.hostname_, storage.username_, storage.password_)


def do_destroy_vips(vips, thread_threshold = 1000):
    for vip in vips:
        thread = threading.Thread(target=net_ops.delete_vip, args=(vip.uuid,))
        while threading.active_count() > thread_threshold:
            time.sleep(0.5)
        exc = sys.exc_info()
        if exc[0]:
            raise info1, None, info2
        thread.start()

    while threading.activeCount() > 1:
        exc = sys.exc_info()
        if exc[0]:
            raise info1, None, info2
        time.sleep(0.1)

def do_destroy_vms(vms, thread_threshold = 1000):
    for vm in vms:
        thread = threading.Thread(target=vm_ops.destroy_vm, args=(vm.uuid,))
        while threading.active_count() > thread_threshold:
            time.sleep(0.5)
        exc = sys.exc_info()
        if exc[0]:
            raise info1, None, info2
        thread.start()

    while threading.activeCount() > 1:
        exc = sys.exc_info()
        if exc[0]:
            raise info1, None, info2
        time.sleep(0.1)

def delete_accounts(thread_threshold = 1000):
    def do_delete_accounts(accounts, session_uuid):
        for account in accounts:
            thread = threading.Thread(target=acc_ops.delete_account, \
                    args=(account.uuid, session_uuid))
            while threading.active_count() > thread_threshold:
                time.sleep(0.5)
            exc = sys.exc_info()
            if exc[0]:
                raise info1, None, info2
            thread.start()

        while threading.activeCount() > 1:
            exc = sys.exc_info()
            if exc[0]:
                raise info1, None, info2
            time.sleep(0.1)

    session_uuid = acc_ops.login_as_admin()
    session_to = con_ops.change_global_config('identity', 'session.timeout', '720000')
    session_mc = con_ops.change_global_config('identity', 'session.maxConcurrent', '10000')
    cond = []
    cond = res_ops.gen_query_conditions('name', '!=', 'admin', cond)
    num = res_ops.query_resource_count(res_ops.ACCOUNT, cond)
    if num <= thread_threshold:
        accounts = res_ops.query_resource(res_ops.ACCOUNT, cond)
        do_delete_accounts(accounts, session_uuid)
    else:
        start = 0
        limit = thread_threshold - 1
        curr_num = start
        accs = []
        while curr_num < num:
            acc_tmp= res_ops.query_resource_fields(res_ops.ACCOUNT, \
                    [], session_uuid, ['uuid'], start, limit)
            accs.extend(acc_temp)
            curr_num += limit
            start += limit
        do_delete_accounts(accs, thread_threshold)

def destroy_all_vm_and_vips(thread_threshold = 1000):
    session_uuid = acc_ops.login_as_admin()
    session_to = con_ops.change_global_config('identity', 'session.timeout', '720000')
    session_mc = con_ops.change_global_config('identity', 'session.maxConcurrent', '10000')
    cond = []
    num = res_ops.query_resource_count(res_ops.VM_INSTANCE, cond)

    if num <= thread_threshold:
        vms = res_ops.query_resource(res_ops.VM_INSTANCE, cond)
        do_destroy_vms(vms, thread_threshold)
    else:
        start = 0
        limit = thread_threshold - 1
        curr_num = start
        vms = []
        while curr_num < num:
            vms_temp = res_ops.query_resource_fields(res_ops.VM_INSTANCE, \
                    cond, None, ['uuid'], start, limit)
            vms.extend(vms_temp)
            curr_num += limit
            start += limit
        do_destroy_vms(vms, thread_threshold)

    vip_num = res_ops.query_resource_count(res_ops.VIP, [], session_uuid)

    if vip_num <= thread_threshold:
        vips = res_ops.query_resource(res_ops.VIP, [], session_uuid)
        do_destroy_vips(vips, thread_threshold)
    else:
        start = 0
        limit = thread_threshold - 1
        curr_num = start
        vms = []
        while curr_num < vip_num:
            vips_temp = res_ops.query_resource_fields(res_ops.VIP, \
                    [], session_uuid, ['uuid'], start, limit)
            vips.extend(vips_temp)
            curr_num += limit
            start += limit
        do_destroy_vips(vips, thread_threshold)

    test_util.test_logger('vms destroy Success. Destroy %d VMs.' % num)
