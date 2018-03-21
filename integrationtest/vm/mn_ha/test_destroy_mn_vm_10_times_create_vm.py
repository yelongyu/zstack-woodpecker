'''

Integration Test for creating KVM VM in MN HA mode after destroying MN VM.

@author: Mirabel
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.node_operations as node_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import test_stub
import time
import os

vm = None
mn_host = None

def test():
    global vm
    global mn_host
    for i in range(0, 10):
        test_util.test_logger("destroy mn vm round %s" % (i))

        mn_host = test_stub.get_host_by_mn_vm(test_lib.all_scenario_config, test_lib.scenario_file)
        if len(mn_host) != 1:
            test_util.test_fail('MN VM is running on %d host(s)' % len(mn_host))
        test_util.test_logger("destroy mn vm on host [%s]" % mn_host[0].ip_)
        test_stub.destroy_mn_vm(mn_host[0], test_lib.all_scenario_config)
        new_mn_host = test_stub.get_host_by_mn_vm(test_lib.all_scenario_config, test_lib.scenario_file)
        if len(new_mn_host) == 0:
            test_util.test_logger("mn vm was destroyed successfully")
        else:
            test_util.test_fail("mn vm was not destroyed successfully")
            
        test_util.test_logger("wait for 20 seconds to see if management node VM starts on one host")
        time.sleep(20)
    
        new_mn_host_ip = test_stub.get_host_by_consul_leader(test_lib.all_scenario_config, test_lib.scenario_file)
        if new_mn_host_ip == "" or new_mn_host_ip != mn_host[0].ip_:
            test_util.test_fail("management node VM not run correctly on [%s] after its former host [%s] down for 20s" % (new_mn_host_ip, mn_host[0].ip_))
    
        count = 60
        while count > 0:
            new_mn_host = test_stub.get_host_by_mn_vm(test_lib.all_scenario_config, test_lib.scenario_file)
            if len(new_mn_host) == 1:
                test_util.test_logger("management node VM run after its former host down for 30s")
                break
            elif len(new_mn_host) > 1:
                test_util.test_fail("management node VM runs on more than one host after its former host down")
            time.sleep(5)
            count -= 1
    
        if len(new_mn_host) == 0:
            test_util.test_fail("management node VM does not run after its former host down for 30s")
        elif len(new_mn_host) > 1:
            test_util.test_fail("management node VM runs on more than one host after its former host down")

        test_util.test_logger("wait for 5 minutes to see if management node starts again")
        #node_ops.wait_for_management_server_start(300)
        test_stub.wrapper_of_wait_for_management_server_start(600)
    
        test_stub.ensure_hosts_connected()
        test_stub.ensure_pss_connected()
        test_stub.ensure_bss_connected()

        test_stub.return_pass_ahead_if_3sites("TEST PASS") 
        if os.path.basename(os.environ.get('WOODPECKER_SCENARIO_CONFIG_FILE')).strip() == "scenario-config-vpc-ceph-3-sites.xml":
            pass
        else:
            vm = test_stub.create_basic_vm()
            vm.check()
            vm.destroy()

    test_util.test_pass('Create VM Test Success')

#Will be called what ever test result is
def env_recover():
    test_stub.wait_for_mn_ha_ready(test_lib.all_scenario_config, test_lib.scenario_file)

#Will be called only if exception happens in test().
def error_cleanup():
    global vm
    if vm:
        try:
            vm.destroy()
        except:
            pass
