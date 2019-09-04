'''
cover ZSTAC-10469
Disable MN host 
1.check if /usr/local/zstack/imagestore exist in hosts;
2.remove /usr/local/zstack/imagestore, reconnect hosts, clean up ps image cache then create vm on nfs primary storage;
3.check if the exception including 'reconnect hosts';
4.remove /var/lib/zstack/imagestorebackupstorage/package/zstack-store.bin, reconnect host;
5.check if /usr/local/zstack/imagestore exist in hosts;
6.create vm on nfs primary storage
@author: Zhaohao
'''
import zstackwoodpecker.action_select as action_select
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.header.vm as vm_header
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.primarystorage_operations as ps_ops
import traceback
import os
import time

test_stub = test_lib.lib_get_test_stub()
test_dict = test_state.TestStateDict()
img_store_path = '/usr/local/zstack/imagestore'
zs_store_bin_path = '/var/lib/zstack/imagestorebackupstorage/package/zstack-store.bin'
err_check_flag = 'Please reconnect all hosts'
hosts = None

def img_store_check(hosts):
    check_cmd = 'test -e %s && echo "exist" || echo "Not exist"' % img_store_path
    for host in hosts:
        host_ip = host.managementIp
        check_result = test_lib.lib_execute_ssh_cmd(host_ip, 'root', 'password', check_cmd)
        test_util.test_logger("Check_result: %s" % check_result)
        if 'Not exist' in check_result:
            test_util.test_fail('Host %s file %s check failed!\n check_result: %s' % (host_ip, img_store_path, check_result))

def rm_file_in_hosts(rm_cmd, hosts):
    for host in hosts:
        host_ip = host.managementIp
        host_uuid = host.uuid
        rm_result = test_lib.lib_execute_ssh_cmd(host_ip, 'root', 'password', rm_cmd)
        time.sleep(5)
        host_ops.reconnect_host(host_uuid)

def test():
    global test_dict
    global hosts
    MN_IP = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].hostName
    mn_cond = res_ops.gen_query_conditions('managementIp', '=', MN_IP)
    mn_host = res_ops.query_resource(res_ops.HOST, mn_cond)
    if len(mn_host):
        #Disable MN Host
        mn_host_uuid = mn_host[0].uuid
        host_ops.change_host_state(mn_host_uuid, 'disable')
    nfs_cond = res_ops.gen_query_conditions('type', '=', 'NFS') 
    nfs_ps = res_ops.query_resource(res_ops.PRIMARY_STORAGE, nfs_cond)
    if not len(nfs_ps):
        test_util.test_skip("No nfs ps, test skip")
    nfs_ps_uuid = nfs_ps[0].uuid
    test_util.test_logger("@@nfs: %s" % nfs_ps_uuid)
    image_name = 'image_for_sg_test' 
    image_cond = res_ops.gen_query_conditions('name', '=', image_name)
    image_uuid = res_ops.query_resource(res_ops.IMAGE, image_cond)[0].uuid 
    l3_cond = res_ops.gen_query_conditions('category', '=', 'Private')
    l3_uuid = res_ops.query_resource(res_ops.L3_NETWORK, l3_cond)[0].uuid
    offering_cond = res_ops.gen_query_conditions('type', '=', 'UserVm')
    instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, offering_cond)[0].uuid
    vm_create_option = test_util.VmOption()
    vm_create_option.set_l3_uuids([l3_uuid])
    vm_create_option.set_image_uuid(image_uuid)
    vm_create_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_create_option.set_ps_uuid(nfs_ps_uuid)
    host_cond = res_ops.gen_query_conditions('managementIp', '!=', MN_IP)
    hosts = res_ops.query_resource(res_ops.HOST, host_cond)
    #1.check if /usr/local/zstack/imagestore exist in hosts
    img_store_check(hosts)
    test_util.test_logger('All host file check pass!')
    #2.remove /usr/local/zstack/imagestore, reconnect hosts;
    rm_cmd = 'rm -rf %s' % img_store_path
    rm_file_in_hosts(rm_cmd, hosts) 
    #3.create vm on nfs primary storage, check if the exception including 'reconnect hosts';
    #Clean up ps image cache
    ps_list = res_ops.query_resource(res_ops.PRIMARY_STORAGE)
    exc = None
    for i in range(3):
        for ps in ps_list:
            ps_ops.cleanup_imagecache_on_primary_storage(ps.uuid) 
        time.sleep(10)
        vm_create_option.set_name('Fail%s' % i)
        try:
            vm = vm_ops.create_vm(vm_create_option)
        except Exception:
            exc = traceback.format_exc()
            if err_check_flag not in exc:
                test_util.test_fail('Error msg check failed!\n Error msg:%s' % exc)
            break
    if not exc:
        test_util.test_fail('Create VM successed, please check %s' % img_store_path)
    test_util.test_logger('Error msg check pass!')
    #4.remove /var/lib/zstack/imagestorebackupstorage/package/zstack-store.bin, reconnect host;
    rm_cmd = 'rm -rf %s' % zs_store_bin_path
    rm_file_in_hosts(rm_cmd, hosts)
    #5.check if /usr/local/zstack/imagestore exist in hosts;
    img_store_check(hosts)
    test_util.test_logger('All host file check pass!')
    #6.create vm on nfs primary storage    
    vm_create_option.set_name('Success')
    vm_2 = vm_ops.create_vm(vm_create_option)
    test_util.test_pass('Create VM successed!')

def env_recover():
    global test_dict
    global hosts
    test_lib.lib_robot_cleanup(test_dict)
    MN_IP = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].hostName
    mn_cond = res_ops.gen_query_conditions('managementIp', '=', MN_IP)
    mn_host_uuid = res_ops.query_resource(res_ops.HOST, mn_cond)[0].uuid
    rm_cmd = 'rm -rf %s' % zs_store_bin_path
    rm_file_in_hosts(rm_cmd, hosts)
    host_ops.change_host_state(mn_host_uuid, 'enable')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_dict
    global hosts
    test_lib.lib_robot_cleanup(test_dict)
    MN_IP = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].hostName
    mn_cond = res_ops.gen_query_conditions('managementIp', '=', MN_IP)
    mn_host_uuid = res_ops.query_resource(res_ops.HOST, mn_cond)[0].uuid
    rm_cmd = 'rm -rf %s' % zs_store_bin_path
    rm_file_in_hosts(rm_cmd, hosts)
    host_ops.change_host_state(mn_host_uuid, 'enable')
