import zstackwoodpecker.header.header as zstack_header
CREATED = 'Created'
DELETED = 'Deleted'
ENABLED = 'Enabled'
DISABLED = 'Disabled'

class TestUser(zstack_header.ZstackObject):
    def __init__(self):
        self.user = None
        self.state = None

    def __repr__(self):
        if self.user:
            return '%s-%s' % (self.__class__.__name__, self.host.uuid)
        return '%s-None' % self.__class__.__name__

    def create(self):
        self.state = CREATED

    def delete(self):
        self.state = DELETED

    def disable(self):
        self.state = DISABLED

    def enable(self):
        self.state = ENABLED

    def check(self):
        pass

    def get_user(self):
        return self.user

    def set_user(self, user):
        self.user = user
        return self.user

    def get_state(self):
        return self.state
