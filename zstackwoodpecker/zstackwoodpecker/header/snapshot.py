import zstackwoodpecker.header.header as zstack_header
import zstackwoodpecker.header.volume as volume_header
CREATED = 'created' #just created and only in primary storage
BACKUPED ='backuped'    #in both primary and backup storage
DELETED = 'deleted'     #neither in primary storage nor backup storage
PS_DELETED = 'deleted_from_primary_storage' #only in backup storage 
md5sum = ''

class TestSnapshot(zstack_header.ZstackObject):

    def __init__(self):
        self.snapshot = None
        self.state = None
        self.in_use = False
        self.target_volume = None
        #snapshot has to define volume type. It is because when target_volume
        # is deleted, then target_volume.volume() will be set to None. So we can
        # not get volume's type from target_volume.volume().type
        self.volume_type = None #volume.ROOT_VOLUME or volume.DATA_VOLUME

    def __repr__(self):
        if self.snapshot:
            return '%s-%s' % (self.__class__.__name__, self.snapshot.uuid)
        return '%s-None' % self.__class__.__name__

    def create(self):
        self.state = CREATED

    def backup(self):
        self.state = BACKUPED

    def use(self):
        self.in_use = True

    def drop(self):
        self.in_use = False

    def delete_from_primary_storage(self):
        if self.state == CREATED:
            self.state = DELETED
            self.set_target_volume(None)
        elif self.state == BACKUPED:
            self.state = PS_DELETED

    def delete_from_backup_storage(self):
        if self.state == BACKUPED:
            self.state = CREATED
        elif self.state == PS_DELETED:
            self.state = DELETED
            self.set_target_volume(None)

    def delete(self):
        self.state = DELETED

    def create_data_volume(self):
        pass

    def create_image_template(self):
        pass

    def check(self):
        pass

    def get_snapshot(self):
        return self.snapshot

    def get_state(self):
        return self.state

    def is_in_use(self):
        return self.in_use

    def set_target_volume(self, target_volume):
        self.target_volume = target_volume
        if target_volume.get_volume().type == volume_header.ROOT_VOLUME:
            self.set_volume_type(volume_header.ROOT_VOLUME)
        else:
            self.set_volume_type(volume_header.DATA_VOLUME)

    def get_target_volume(self):
        return self.target_volume

    def set_volume_type(self, volume_type):
        self.volume_type = volume_type

    def get_volume_type(self):
        return self.volume_type

    def set_md5sum(self, md5sum):
        self.md5sum = md5sum

    def get_md5sum(self):
        return self.md5sum
