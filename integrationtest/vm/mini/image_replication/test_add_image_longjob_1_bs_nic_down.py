'''

New Integration test for image replication.

@author: Legion
'''

import os
import time
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib


image_name = 'image-replication-test-' + time.strftime('%y%m%d%H%M%S', time.localtime())
test_stub_vr = test_lib.lib_get_test_stub('virtualrouter')
longjob = test_stub_vr.Longjob(name=image_name, url=os.getenv('imageUrl_vdbench'))
test_stub = test_lib.lib_get_test_stub()
img_repl = test_stub.ImageReplication()


def test():
    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = os.getenv('zstackHaVip')
    host_vm0 = test_stub.get_host_by_index_in_scenario_file(test_lib.all_scenario_config, test_lib.scenario_file, 0)
    test_stub.down_host_network(host_vm0.ip_, test_lib.all_scenario_config, "managment_net")

    img_repl.wait_for_bs_status_change('Disconnected')
    longjob.add_image()

    test_stub.up_host_network(host_vm0.ip_, test_lib.all_scenario_config, "managment_net")
    test_stub.recover_vlan_in_host(host_vm0.ip_, test_lib.all_scenario_config, test_lib.deploy_config)

    img_repl.wait_for_bs_status_change('Connected')
    img_repl.wait_for_image_replicated(image_name)

    img_repl.check_image_data(image_name)
    img_repl.reconnect_host()

    img_repl.create_vm(image_name)
    test_util.test_pass('Image Replication After NIC Recovering Test Success')


def env_recover():
    longjob.delete_image()
    longjob.expunge_image()
    img_repl.reclaim_space_from_bs()
    try:
        img_repl.vm.destroy()
    except:
        pass


#Will be called only if exception happens in test().
def error_cleanup():
    longjob.delete_image()
    longjob.expunge_image()
    img_repl.reclaim_space_from_bs()
    try:
        img_repl.vm.destroy()
    except:
        pass

