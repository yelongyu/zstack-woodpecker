import sys
import traceback

import zstackwoodpecker.header.checker as checker_header
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstacklib.utils.http as http
import zstacklib.utils.jsonobject as jsonobject
import zstacktestagent.plugins.vm as vm_plugin
import zstacktestagent.plugins.host as host_plugin
import zstacktestagent.testagent as testagent
import apibinding.inventory as inventory

class zstack_kvm_image_file_checker(checker_header.TestChecker):
    '''check kvm image file existencex . If it is in backup storage, 
        return self.judge(True). If not, return self.judge(False)'''
    def check(self):
        super(zstack_kvm_image_file_checker, self).check()
        image = self.test_obj.image
        backupStorages = image.backupStorageRefs
        bs_one = backupStorages[0]
        bs = test_lib.lib_get_backup_storage_by_uuid(bs_one.backupStorageUuid)
        if bs.type == inventory.SFTP_BACKUP_STORAGE_TYPE:
            host = test_lib.lib_get_backup_storage_host(bs_one.backupStorageUuid)
            image_url = backupStorages[0].installPath
            self.judge(test_lib.lib_check_file_exist(host, image_url))
        elif bs.type == inventory.CEPH_BACKUP_STORAGE_TYPE:
            ceph_host, username, password = test_lib.lib_get_ceph_info(os.environ.get('cephBackupStorageMonUrls'))
            image_installPath = bs_one.installPath.split('ceph://')[1]

            command = 'rbd info %s' % image_installPath
            if not test_lib.lib_execute_ssh_cmd(ceph_host, username, password, command, 10):
                test_util.test_logger('Check result: [image:] %s [file:] %s exist on ceph [host name:] %s .' % (image.uuid, image_installPath, ceph_host))
                return self.judge(True)
            else:
                test_util.test_logger('Check result: [image:] %s [file:] %s does not exist on ceph [host name:] %s .' % (image.uuid, image_installPath, ceph_host))
                return self.judge(False)


