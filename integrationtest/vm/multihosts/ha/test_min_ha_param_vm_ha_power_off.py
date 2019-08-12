'''
Test for graceful stop host vm ha located by quick ha setting and check vm ha
@author: SyZhao
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import zstackwoodpecker.header.vm as vm_header
import zstackwoodpecker.operations.ha_operations as ha_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.config_operations as conf_ops
import apibinding.inventory as inventory
import time
import os
import zstacklib.utils.ssh as ssh

vm = None
host_uuid = None
host_ip = None
max_attempts = None
storagechecker_timeout = None
test_stub = test_lib.lib_get_test_stub()
test_host = None

pre1 = None
pre2 = None
pre3 = None
pre4 = None
pre5 = None
pre6 = None

def set_quick_ha_params():
    global pre1,pre2,pre3,pre4,pre5,pre6
    pre1 = conf_ops.change_global_config('ha', 'host.selfFencer.storageChecker.timeout', 5)
    pre2 = conf_ops.change_global_config('ha', 'neverStopVm.retry.delay', 5)
    pre3 = conf_ops.change_global_config('ha', 'host.selfFencer.maxAttempts', 10)
    pre4 = conf_ops.change_global_config('ha', 'host.selfFencer.interval', 1)
    pre5 = conf_ops.change_global_config('ha', 'host.check.interval', 1)
    pre6 = conf_ops.change_global_config('primaryStorage', 'ping.interval', 2)
    global ps_uuid

def set_org_ha_params():
    global pre1,pre2,pre3,pre4,pre5,pre6
    if pre1:
        conf_ops.change_global_config('ha', 'host.selfFencer.storageChecker.timeout', pre1)
    if pre2:
        conf_ops.change_global_config('ha', 'neverStopVm.retry.delay', pre2)
    if pre3:
        conf_ops.change_global_config('ha', 'host.selfFencer.maxAttempts', pre3)
    if pre4:
        conf_ops.change_global_config('ha', 'host.selfFencer.interval', pre4)
    if pre5:
        conf_ops.change_global_config('ha', 'host.check.interval', pre5)
    if pre6:
        conf_ops.change_global_config('primaryStorage', 'ping.interval', pre6)

def set_quick_ha_properties():
    host_username = os.environ.get('hostUsername')
    host_password = os.environ.get('hostPassword')
    mn_ip = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].hostName
    cmd = 'zstack-ctl status|grep properties|cut -d: -f2'
    ret, properties_file, stderr = ssh.execute(cmd, mn_ip, host_username, host_password, False, 22)

    cmd = "zstack-ctl stop"
    if test_lib.lib_execute_ssh_cmd(mn_ip, host_username, host_password, cmd,  timeout = 120) == False:
        test_util.test_fail("CMD:%s execute failed on %s" %(cmd, mn_ip))

    cmd = "sed 's/RESTFacade.connectTimeout.*$//g' -i " + properties_file
    if test_lib.lib_execute_ssh_cmd(mn_ip, host_username, host_password, cmd,  timeout = 10) == False:
        test_util.test_fail("CMD:%s execute failed on %s" %(cmd, mn_ip))

    cmd = "sed 's/RESTFacade.readTimeout.*$//g' -i " + properties_file
    if test_lib.lib_execute_ssh_cmd(mn_ip, host_username, host_password, cmd,  timeout = 10) == False:
        test_util.test_fail("CMD:%s execute failed on %s" %(cmd, mn_ip))

    cmd = "echo \"RESTFacade.readTimeout = 10000\" >>" + properties_file
    if test_lib.lib_execute_ssh_cmd(mn_ip, host_username, host_password, cmd,  timeout = 10) == False:
        test_util.test_fail("CMD:%s execute failed on %s" %(cmd, mn_ip))

    cmd = "echo \"RESTFacade.connectTimeout = 5000\" >>" + properties_file
    if test_lib.lib_execute_ssh_cmd(mn_ip, host_username, host_password, cmd,  timeout = 10) == False:
        test_util.test_fail("CMD:%s execute failed on %s" %(cmd, mn_ip))

    cmd = "nohup zstack-ctl start &"
    if test_lib.lib_execute_ssh_cmd(mn_ip, host_username, host_password, cmd,  timeout = 180) == False:
        test_util.test_fail("CMD:%s execute failed on %s" %(cmd, mn_ip))

    time.sleep(60)


def test():
    global vm
    global host_uuid
    global host_ip
    global max_attempts
    global storagechecker_timeout

    allow_ps_list = [inventory.CEPH_PRIMARY_STORAGE_TYPE]
    test_lib.skip_test_when_ps_type_not_in_list(allow_ps_list)

    if test_lib.lib_get_ha_enable() != 'true':
        test_util.test_skip("vm ha not enabled. Skip test")

    set_quick_ha_properties()
    set_quick_ha_params()

    bs = res_ops.query_resource(res_ops.BACKUP_STORAGE, [], None)[0]
    test_stub.ensure_bss_connected()
    vm_creation_option = test_util.VmOption()
    image_name = os.environ.get('imageName_net')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    l3_name = os.environ.get('l3VlanNetworkName1')
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    test_lib.clean_up_all_vr()
    #vrs = test_lib.lib_find_vr_by_l3_uuid(l3_net_uuid)
    #vr_host_ips = []
    #for vr in vrs:
    #    vr_host_ips.append(test_lib.lib_find_host_by_vr(vr).managementIp)
    #    if test_lib.lib_is_vm_running(vr) != True:
    #        vm_ops.start_vm(vr.uuid)
    #        time.sleep(60)

    mn_ip = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].hostName
    conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
    instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid
    conditions = res_ops.gen_query_conditions('state', '=', 'Enabled')
    conditions = res_ops.gen_query_conditions('status', '=', 'Connected', conditions)
    conditions = res_ops.gen_query_conditions('managementIp', '!=', mn_ip, conditions)
    #for vr_host_ip in vr_host_ips:
    #    conditions = res_ops.gen_query_conditions('managementIp', '!=', vr_host_ip, conditions)
    host_uuid = res_ops.query_resource(res_ops.HOST, conditions)[0].uuid
    vm_creation_option.set_host_uuid(host_uuid)
    vm_creation_option.set_l3_uuids([l3_net_uuid])
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_name('multihost_basic_vm')
    vm = test_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    vm.check()

    test_stub.ensure_host_has_no_vr(host_uuid)

    host_ip = test_lib.lib_find_host_by_vm(vm.get_vm()).managementIp
    host_port = test_lib.lib_get_host_port(host_ip)
    test_util.test_logger("host %s is disconnecting" %(host_ip))
    ha_ops.set_vm_instance_ha_level(vm.get_vm().uuid, "NeverStop")

    host_list = test_stub.get_sce_hosts(test_lib.all_scenario_config, test_lib.scenario_file)
    for host in host_list:
        if host.ip_ == host_ip:
            test_host = host
            break
    if not test_host:
        test_util.test_fail('there is no host with ip %s in scenario file.' %(host_ip))

    test_stub.stop_host(test_host, test_lib.all_scenario_config)

    test_util.test_logger("wait for 120 seconds")
    time.sleep(120)

    test_stub.start_host(test_host, test_lib.all_scenario_config)
    test_stub.recover_host_vlan(test_host, test_lib.all_scenario_config, test_lib.deploy_config)

    vm.set_state(vm_header.RUNNING)
    vm.check()

    vm.update()
    if test_lib.lib_find_host_by_vm(vm.get_vm()).managementIp == host_ip:
        test_util.test_fail("VM is expected to start running on another host")

    vm.destroy()

    test_util.test_pass('Test checking vm status after graceful stop and start success')


#Will be called only if exception happens in test().
def error_cleanup():
    global vm

    if vm:
        try:
            vm.destroy()
        except:
            pass



def env_recover():
    set_org_ha_params()
    test_util.test_logger("recover host: %s" % (test_host.ip_))
    test_stub.recover_host(test_host, test_lib.all_scenario_config, test_lib.deploy_config)
    #host_ops.reconnect_host(host_uuid)
