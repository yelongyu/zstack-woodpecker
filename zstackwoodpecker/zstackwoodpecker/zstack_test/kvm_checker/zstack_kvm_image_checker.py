import zstackwoodpecker.header.checker as checker_header
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstacklib.utils.http as http
import zstacklib.utils.jsonobject as jsonobject
import zstacktestagent.plugins.vm as vm_plugin
import zstacktestagent.plugins.host as host_plugin
import zstacktestagent.testagent as testagent

import sys
import traceback

class zstack_kvm_image_file_checker(checker_header.TestChecker):
    '''check kvm image file existencex . If it is in backup storage, 
        return self.judge(True). If not, return self.judge(False)'''
    def check(self):
        super(zstack_kvm_image_file_checker, self).check()
        image = self.test_obj.image
        backupStorages = image.backupStorageRefs
        image_url = backupStorages[0].installPath
        host = test_lib.lib_get_backup_storage_host(image.backupStorageUuid)
        self.judge(test_lib.lib_check_file_exist(host, image_url))

