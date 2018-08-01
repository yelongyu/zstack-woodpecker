'''

New Integration test for testing stopped vm migration after change the password "password*()"between hosts.

@author: yetian
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.account_operations as account_ops
import apibinding.inventory as inventory
import apibinding.api_actions as api_actions
import zstacklib.utils.ssh as ssh


vm = None
test_stub = test_lib.lib_get_test_stub()

def test():
    global vm, kvm_host 

    ps = res_ops.query_resource(res_ops.PRIMARY_STORAGE)
    for i in ps:
        if i.type == inventory.LOCAL_STORAGE_TYPE:
 	    break
    else:
        test_util.test_skip('Skip test on non-localstoreate PS')

    #ps = res_ops.query_resource(res_ops.PRIMARY_STORAGE)[0]
    #if ps.type != inventory.LOCAL_STORAGE_TYPE:
    #    test_util.test_skip('Skip test on non-localstorage')
    #if "test-config-local-ps.xml" != os.path.basename(os.environ.get('WOODPECKER_TEST_CONFIG_FILE')).strip():
	# test_util.test_skip('Skip test on non-localstoreage')
#query all hosts and change password
    conditions = res_ops.gen_query_conditions('state', '=', 'Enabled')
    if res_ops.query_resource(res_ops.HOST, conditions):
        kvm_host = res_ops.query_resource(res_ops.HOST, conditions)
        for i in kvm_host:
        	host_ops.update_kvm_host(i.uuid, 'password', 'password*()')
 		cmd = 'echo "password*()"| passwd --stdin root'
    		test_lib.lib_execute_ssh_cmd(i.managementIp,"root","password",cmd)
    		host_ops.reconnect_host(i.uuid)
    else:
        test_util.test_skip("There is no host. Skip test")

    test_util.test_dsc('Test KVM Host Infomation: password')

#create vm and stop and migrate
    vm = test_stub.create_vr_vm('migrate_stopped_vm', 'imageName_s', 'l3VlanNetwork2')
    vm.check()
    target_host = test_lib.lib_find_random_host(vm.vm)
    vm.stop()
    vol_ops.migrate_volume(vm.get_vm().allVolumes[0].uuid, target_host.uuid)
    vm.check()
    vm.start()
    vm.check()
    vm.destroy()
    vm.expunge()
################################# recover KVM HOST Password #################################
    conditions = res_ops.gen_query_conditions('state', '=', 'Enabled')
    if res_ops.query_resource(res_ops.HOST, conditions):
        kvm_host = res_ops.query_resource(res_ops.HOST, conditions)
        for i in kvm_host:
                host_ops.update_kvm_host(i.uuid, 'password', 'password')
                cmd = 'echo "password"| passwd --stdin root'
                test_lib.lib_execute_ssh_cmd(i.managementIp,"root","password*()",cmd)
                host_ops.reconnect_host(i.uuid)
    else:
        test_util.test_skip("There is no host. Skip test")

    test_util.test_dsc('Test KVM Host Infomation: password')

    test_util.test_pass('Migrate Stopped VM with special_password Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global vm

    #conditions = res_ops.gen_query_conditions('state', '=', 'Enabled')
    #if res_ops.query_resource(res_ops.HOST, conditions):
    #    kvm_host = res_ops.query_resource(res_ops.HOST, conditions)
    #    for i in kvm_host:
    #            host_ops.update_kvm_host(i.uuid, 'password', 'password')
    #            cmd = 'echo "password"| passwd --stdin root'
    #            test_lib.lib_execute_ssh_cmd(i.managementIp,"root","password*()",cmd)
    #            host_ops.reconnect_host(i.uuid)
    #else:
    #    test_util.test_skip("There is no host. Skip test")

    #test_util.test_dsc('Test KVM Host Infomation: password')

    if vm:
        try:
            vm.destroy()
        except:
            pass

