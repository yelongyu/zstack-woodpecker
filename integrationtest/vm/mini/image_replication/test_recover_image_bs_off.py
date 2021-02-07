'''

New Integration test for image replication.

@author: Legion
'''

import os
import time
import random
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.config_operations as conf_ops

image_name = 'image-replication-test-' + time.strftime('%y%m%d%H%M%S', time.localtime())
test_stub = test_lib.lib_get_test_stub()
img_repl = test_stub.ImageReplication()


def test():
    os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'] = os.getenv('zstackHaVip')
    conf_ops.change_global_config('imagestore', 'cleanOnExpunge', 'true')
    bs_list = img_repl.get_bs_list()
    bs = random.choice(bs_list)
    host_vm = test_stub.get_host_by_index_in_scenario_file(test_lib.all_scenario_config, test_lib.scenario_file, ip=bs.hostname)

    img_repl.add_image(image_name, bs_uuid=bs.uuid, url=os.getenv('imageUrl_vdbench'))
    img_repl.delete_image()

    test_stub.stop_host(host_vm, test_lib.all_scenario_config, 'grace')
    img_repl.recover_image()

    test_stub.start_host(host_vm, test_lib.all_scenario_config)
    time.sleep(300)
    img_repl.wait_for_image_replicated(image_name)
    img_repl.check_image_data(image_name)

    img_repl.create_vm(image_name)
    test_util.test_pass('Recovered Image Create VM Test Success')
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