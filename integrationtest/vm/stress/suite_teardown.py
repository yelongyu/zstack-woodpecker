'''

Integration Test Teardown case

@author: Youyk
'''

import zstackwoodpecker.setup_actions as setup_actions
from zstackwoodpecker import test_util
from zstackwoodpecker import clean_util
from zstacklib.utils import linux
from zstacklib.utils import http
import zstackwoodpecker.test_lib as test_lib
from zstacktestagent.plugins import host as host_plugin
from zstacktestagent import testagent

def test():
    clean_util.cleanup_all_vms_violently()
    clean_util.cleanup_none_vm_volumes_violently()
    clean_util.umount_all_primary_storages_violently()
    test_lib.setup_plan.stop_node()

    test_lib.lib_cleanup_host_ip_dict()
    test_util.test_pass('ZStack POC Test Teardown Success')
