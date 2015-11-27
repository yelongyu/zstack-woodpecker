import zstackwoodpecker.header.header as zstack_header
CREATED = 'created'
DELETED = 'deleted'
EXPUNGED = 'expunged'

class TestImage(zstack_header.ZstackObject):
    def __init__(self):
        self.image = None
        self.state = None

    def __repr__(self):
        if self.image:
            return '%s-%s' % (self.__class__.__name__, self.image.uuid)
        return '%s-None' % self.__class__.__name__

    def create(self):
        self.state = CREATED

    def create_data_volume(self):
        '''
        Create Data Volume from Image Template
        '''
        pass

    def add_root_volume_template(self):
        pass

    def add_data_volume_template(self):
        pass

    def delete(self):
        self.state = DELETED

    def expunge(self):
        #self.state = EXPUNGED
        pass

    def check(self):
        pass

    def get_image(self):
        return self.image

    def get_state(self):
        return self.state

    def set_image(self, image):
        '''
        Used for image created by none image operations, like snapshot
        '''
        self.image = image

    def set_state(self, state):
        self.state = state
