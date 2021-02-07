'''

New Integration test for image replication.
1. Add image with BS-1 off
2. Recover BS-1
3. Create VM with BS-2 off

@author: Legion
'''

import os
import time
import random
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops


image_name = 'image-replication-test-' + time.strftime('%y%m%d%H%M%S', time.localtime())
test_stub = test_lib.lib_get_test_stub()
img_repl = test_stub.ImageReplication()


def test():
    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = os.getenv('zstackHaVip')
    cluster_num = len(res_ops.query_resource(res_ops.CLUSTER))
    if cluster_num == 1:
        test_util.test_skip('Skip for 1 mini-cluster')
    bs_list = img_repl.get_bs_list()
    bs = random.choice(bs_list)
    bs_list.remove(bs)
    bs2 = bs_list[0]
    host_vm1 = test_stub.get_host_by_index_in_scenario_file(test_lib.all_scenario_config, test_lib.scenario_file, ip=bs.hostname)
    host_vm2 = test_stub.get_host_by_index_in_scenario_file(test_lib.all_scenario_config, test_lib.scenario_file, ip=bs2.hostname)

    test_stub.stop_host(host_vm2, test_lib.all_scenario_config, 'cold')

    img_repl.add_image(image_name, bs_uuid=bs.uuid, url=os.getenv('imageUrl_raw'))

    time.sleep(300)
    test_stub.start_host(host_vm2, test_lib.all_scenario_config)
    test_stub.recover_vlan_in_host(bs2.hostname, test_lib.all_scenario_config, test_lib.deploy_config)

    img_repl.wait_for_bs_status_change('Connected')
    img_repl.wait_for_image_replicated(image_name)

    test_stub.stop_host(host_vm1, test_lib.all_scenario_config, 'cold')

    img_repl.create_vm(image_name)

    test_stub.start_host(host_vm1, test_lib.all_scenario_config)
    test_stub.recover_vlan_in_host(bs.hostname, test_lib.all_scenario_config, test_lib.deploy_config)

    test_util.test_pass('Image Replication After Host Recovering Test Success')
    img_repl.clean_on_expunge()


def env_recover():
    img_repl.delete_image()
    img_repl.expunge_image()
    img_repl.reclaim_space_from_bs()
    try:
        img_repl.vm.destroy()
    except:
        pass


#Will be called only if exception happens in test().
def error_cleanup():
    try:
        img_repl.delete_image()
        img_repl.expunge_image()
        img_repl.reclaim_space_from_bs()
        img_repl.vm.destroy()
    except:
        pass
