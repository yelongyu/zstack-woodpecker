'''

Integration Test Teardown case

@author: Youyk
'''

import zstackwoodpecker.setup_actions as setup_actions
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.clean_util as clean_util
import zstackwoodpecker.test_lib as test_lib
from zstacklib.utils import linux
from zstacklib.utils import http
import os.path
from zstacktestagent.plugins import host as host_plugin
from zstacktestagent import testagent

def test():
    clean_util.cleanup_all_vms_violently()
    clean_util.cleanup_none_vm_volumes_violently()
    clean_util.umount_all_primary_storages_violently()
    clean_util.cleanup_backup_storage()
    test_lib.setup_plan.stop_node()
    test_util.test_pass('VCenter Teardown Success')
