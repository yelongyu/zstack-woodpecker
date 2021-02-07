'''
zstack image test class

@author: Youyk
'''
import apibinding.inventory as inventory 
import zstackwoodpecker.header.header as zstack_header
import zstackwoodpecker.header.image as image_header
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import random

class ZstackTestImage(image_header.TestImage):

    def __init__(self):
        super(ZstackTestImage, self).__init__()
        self.image_creation_option = test_util.ImageOption()
        self.original_checking_points = []
        self.delete_policy = test_lib.lib_get_delete_policy('image')
        self.delete_delay_time = test_lib.lib_get_expunge_time('image')

    def create(self, apiid=None, root=True):
        '''
        Create image template from Root Volume using CreateRootVolumeTemplateFromRootVolume
        '''
        if test_lib.lib_check_version_is_mevoco_1_8():
            if test_lib.lib_check_version_is_mevoco():
                self.image = img_ops.commit_volume_as_image_apiid(self.image_creation_option, apiid)
            else:
                self.image = img_ops.create_root_volume_template_apiid(self.image_creation_option, apiid)
        else:
            if root:
                self.image = img_ops.create_root_volume_template_apiid(self.image_creation_option, apiid)
            else:
                self.image = img_ops.create_data_volume_template(self.image_creation_option)
        super(ZstackTestImage, self).create()

    def delete(self):
        img_ops.delete_image(self.image.uuid)
        super(ZstackTestImage, self).delete()

    def recover(self):
        img_ops.recover_image(self.image.uuid)
        super(ZstackTestImage, self).recover()

    def expunge(self, bs_uuid_list = None):
        img_ops.expunge_image(self.image.uuid, bs_uuid_list)
        super(ZstackTestImage, self).expunge()

    def update(self):
        if self.get_state() != image_header.EXPUNGED:
            updated_image = test_lib.lib_get_image_by_uuid(self.image.uuid)
            if updated_image:
                self.image = updated_image
            else:
                self.set_state(image_header.EXPUNGED)
        return self.image

    def clean(self):
        if self.delete_policy != zstack_header.DELETE_DIRECT:
            if self.get_state() == image_header.DELETED:
                self.expunge()
            elif self.get_state() == image_header.EXPUNGED:
                pass
            else:
                self.delete()
                self.expunge()
        else:
            self.delete()

    def export(self):
        bs_uuid = self.image_creation_option.get_backup_storage_uuid_list()[0]
        return img_ops.export_image_from_backup_storage(self.image.uuid, bs_uuid)

    def delete_exported_image(self):
        bs_uuid = self.image_creation_option.get_backup_storage_uuid_list()[0]
        return img_ops.delete_exported_image_from_backup_storage(self.image.uuid, bs_uuid)

    def check(self):
        import zstackwoodpecker.zstack_test.checker_factory as checker_factory
        checker = checker_factory.CheckerFactory().create_checker(self)
        checker.check()
        super(ZstackTestImage, self).check()

    def set_creation_option(self, image_creation_option):
        self.image_creation_option = image_creation_option

    def get_creation_option(self):
        return self.image_creation_option

    def create_data_volume(self, ps_uuid, name = None, host_uuid = None):
        import zstackwoodpecker.header.volume as volume_header
        import zstackwoodpecker.zstack_test.zstack_test_volume \
                as zstack_volume_header
        volume_inv = vol_ops.create_volume_from_template(self.get_image().uuid,\
                ps_uuid, name, host_uuid)
        volume = zstack_volume_header.ZstackTestVolume()
        volume.set_volume(volume_inv)
        volume.set_state(volume_header.DETACHED)
        volume.set_original_checking_points(self.get_original_checking_points())
        super(ZstackTestImage, self).create_data_volume()
        return volume

    def add_data_volume_template(self):
        self.set_image(img_ops.add_data_volume_template(self.get_creation_option))
        return self

    def add_root_volume_template(self):
        self.set_image(img_ops.add_root_volume_template(self.get_creation_option()))
        return self

    def add_root_volume_template_apiid(self, apiid):
        self.set_image(img_ops.add_root_volume_template_apiid(self.get_creation_option(), apiid))
        return self

    def set_original_checking_points(self, original_checking_points):
        '''
        If the tmpt is created from a snapshot, it should inherit snapshot's 
        checking points. Otherwise the previous checking points will lost, when
        create a new snapshot from the volume created from current template.
        '''
        self.original_checking_points = original_checking_points

    def get_original_checking_points(self):
        return self.original_checking_points

    def set_delete_policy(self, policy):
        test_lib.lib_set_delete_policy(category = 'image', value = policy)
        super(ZstackTestImage, self).set_delete_policy(policy)

    def set_delete_delay_time(self, delay_time):
        test_lib.lib_set_expunge_time(category = 'image', value = delay_time)
        super(ZstackTestImage, self).set_delete_delay_time(delay_time)

