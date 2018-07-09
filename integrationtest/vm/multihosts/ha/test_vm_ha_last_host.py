'''

New Integration Test for KVM VM ha never stop mode.

@author: Mirabel
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
import apibinding.inventory as inventory
import time
import os

vm = None
host_uuid = None
host_ip = None
max_attempts = None
storagechecker_timeout = None
test_stub = test_lib.lib_get_test_stub()

def test():
    global vm
    global host_uuid
    global host_ip
    global max_attempts
    global storagechecker_timeout

    allow_ps_list = [inventory.CEPH_PRIMARY_STORAGE_TYPE, inventory.NFS_PRIMARY_STORAGE_TYPE, 'SharedMountPoint', 'AliyunNAS']
    test_lib.skip_test_when_ps_type_not_in_list(allow_ps_list)

    if test_lib.lib_get_ha_enable() != 'true':
        test_util.test_skip("vm ha not enabled. Skip test")


    vm_creation_option = test_util.VmOption()
    image_name = os.environ.get('imageName_net')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    #l3_name = os.environ.get('l3NoVlanNetworkName1')
    l3_name = os.environ.get('l3VlanNetworkName1')
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    test_lib.clean_up_all_vr()
    #vrs = test_lib.lib_find_vr_by_l3_uuid(l3_net_uuid)
    #vr_host_ips = []
    #for vr in vrs:
    #    vr_host_ips.append(test_lib.lib_find_host_by_vr(vr).managementIp)
    #    if test_lib.lib_is_vm_running(vr) != True:
    #        vm_ops.start_vm(vr.uuid)
    #time.sleep(60)

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

    vr_hosts = test_stub.get_host_has_vr()
    mn_hosts = test_stub.get_host_has_mn()
    nfs_hosts = test_stub.get_host_has_nfs()
    test_util.test_logger('vr_hosts = %s' % vr_hosts)
    test_util.test_logger('mn_hosts = %s' % mn_hosts)
    test_util.test_logger('nfs_hosts = %s' % nfs_hosts)
    #test_stub.test_skip('debug')
    if not test_stub.ensure_vm_not_on(vm.get_vm().uuid, vm.get_vm().hostUuid, vr_hosts+mn_hosts+nfs_hosts):
        test_util.test_fail("Not find out a suitable host")

    vm.update()
    #vm.check()
    host_ip = test_lib.lib_find_host_by_vm(vm.get_vm()).managementIp
    host_port = test_lib.lib_get_host_port(host_ip)
    test_util.test_logger("host %s is disconnecting" %(host_ip))
    host_uuid = test_lib.lib_find_host_by_vm(vm.get_vm()).uuid
    ha_ops.set_vm_instance_ha_level(vm.get_vm().uuid, "NeverStop")
    test_util.test_logger("force stop host: %s" % (host_ip))
    os.system('bash -ex %s %s' % (os.environ.get('hostForceStopScript'), host_ip))
    test_util.test_logger("host is expected to shutdown for a while")

    test_util.test_logger("wait for 360 seconds")
    time.sleep(360)
    vm.update()
    if test_lib.lib_find_host_by_vm(vm.get_vm()).managementIp == host_ip:
	test_util.test_fail("VM is expected to start running on another host")
    vm.set_state(vm_header.RUNNING)
    vm.check()

    if test_lib.lib_get_vm_last_host(vm.get_vm()).managementIp != host_ip:
        test_util.test_fail("Migrated VM's last host is expected to be the last host[ip:%s]" % (host_ip))

    vm.destroy()

    os.system('bash -ex %s %s' % (os.environ.get('hostRecoverScript'), host_ip))
    host_ops.reconnect_host(host_uuid)
    test_util.test_pass('Test VM ha on host failure Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    global host_uuid
    global host_ip
    global max_attempts
    global storagechecker_timeout

    if vm:
        try:
            vm.destroy()
        except:
            pass


    os.system('bash -ex %s %s' % (os.environ.get('hostRecoverScript'), host_ip))
    host_ops.reconnect_host(host_uuid)
