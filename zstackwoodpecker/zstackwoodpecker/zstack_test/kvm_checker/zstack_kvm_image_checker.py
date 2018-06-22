import os
import sys
import traceback

import zstackwoodpecker.header.checker as checker_header
import zstackwoodpecker.header.image as image_header
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
            self.judge(test_lib.lib_check_backup_storage_image_file(image))

        elif hasattr(inventory, 'IMAGE_STORE_BACKUP_STORAGE_TYPE') and bs.type == inventory.IMAGE_STORE_BACKUP_STORAGE_TYPE:
            if self.test_obj.state == image_header.DELETED:
                test_util.test_logger("skip image store image delete check, since the image won't be deleted until no vms refer to it.")
                return self.judge(self.exp_result)
            self.judge(test_lib.lib_check_backup_storage_image_file(image))

        elif bs.type == inventory.CEPH_BACKUP_STORAGE_TYPE:
            if self.test_obj.state == image_header.DELETED:
                #https://github.com/zstackorg/zstack/issues/93#issuecomment-130935998
                test_util.test_logger("skip ceph image delete check, since the image won't be deleted until no vms refer to it.")
                return self.judge(self.exp_result)

            if test_lib.scenario_config != None and test_lib.scenario_file != None and os.path.exists(test_lib.scenario_file):
                import zstackwoodpecker.operations.scenario_operations as sce_ops
                sce_ops.replace_env_params_if_scenario()

            ceph_host, username, password = test_lib.lib_get_ceph_info(os.environ.get('cephBackupStorageMonUrls'))
            image_installPath = bs_one.installPath.split('ceph://')[1]

            command = 'rbd info %s' % image_installPath
            if test_lib.lib_execute_ssh_cmd(ceph_host, username, password, command, 10):
                test_util.test_logger('Check result: [image:] %s [file:] %s exist on ceph [host name:] %s .' % (image.uuid, image_installPath, ceph_host))
                return self.judge(True)
            else:
                test_util.test_logger('Check result: [image:] %s [file:] %s does not exist on ceph [host name:] %s .' % (image.uuid, image_installPath, ceph_host))
                return self.judge(False)


