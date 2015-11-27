'''
zstack image test class

@author: Youyk
'''
import zstackwoodpecker.header.image as image_header
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstackwoodpecker.test_util as test_util

class ZstackTestImage(image_header.TestImage):

    def __init__(self):
        self.image_creation_option = test_util.ImageOption()
        self.original_checking_points = []
        super(ZstackTestImage, self).__init__()

    def create(self):
        '''
        Create image template from Root Volume
        '''
        self.image = \
                img_ops.create_root_volume_template(self.image_creation_option)
        super(ZstackTestImage, self).create()

    def delete(self):
        img_ops.delete_image(self.image.uuid)
        super(ZstackTestImage, self).delete()

    def expunge(self):
        img_ops.expunge_image(self.image.uuid)
        super(ZstackTestImage, self).expunge()

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

    def set_original_checking_points(self, original_checking_points):
        '''
        If the tmpt is created from a snapshot, it should inherit snapshot's 
        checking points. Otherwise the previous checking points will lost, when
        create a new snapshot from the volume created from current template.
        '''
        self.original_checking_points = original_checking_points

    def get_original_checking_points(self):
        return self.original_checking_points
