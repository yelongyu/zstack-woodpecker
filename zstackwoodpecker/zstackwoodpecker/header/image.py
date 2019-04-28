import zstackwoodpecker.header.header as zstack_header
CREATED = 'created'
DELETED = 'deleted'
EXPUNGED = 'expunged'

class TestImage(zstack_header.ZstackObject):
    def __init__(self):
        self.image = None
        self.state = None
        self.delete_policy = None
        self.delete_delay_time = None

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
        if self.delete_policy != zstack_header.DELETE_DIRECT:
            self.state = DELETED
        else:
            self.state = EXPUNGED

    def expunge(self):
        self.state = EXPUNGED

    def recover(self):
        self.state = CREATED

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

    def set_delete_policy(self, policy):
        self.delete_policy = policy

    def get_delete_policy(self):
        return self.delete_policy

    def set_delete_delay_time(self, time):
        self.delete_delay_time = time

    def get_delete_delay_time(self):
        return self.delete_delay_time
