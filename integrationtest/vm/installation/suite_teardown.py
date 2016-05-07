'''
Integration Test Teardown case

@author: Youyk
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.clean_util as clean_util
import zstackwoodpecker.test_lib as test_lib
import os

def test():
    if os.environ.get('zstackManagementIp') == None:
        clean_util.cleanup_all_vms_violently()
        clean_util.cleanup_none_vm_volumes_violently()
        clean_util.umount_all_primary_storages_violently()
        clean_util.cleanup_backup_storage()
        test_lib.setup_plan.stop_node()
    
        test_lib.lib_cleanup_host_ip_dict()
    test_util.test_pass('ZStack Installation Teardown Success')
