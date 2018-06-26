import zstackwoodpecker.header.header as zstack_header
CREATED = 'Created'
DELETED = 'Deleted'
ENABLED = 'Enabled'
DISABLED = 'Disabled'

class TestVid(zstack_header.ZstackObject):
    def __init__(self):
        self.vid = None
        self.state = None
        self.attributes = []
        self.statements = []

    def __repr__(self):
        if self.vid:
            return '%s-%s' % (self.__class__.__name__, self.vid.uuid)
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

    def get_vid(self):
        return self.vid

    def set_vid(self, vid):
        self.vid = vid

    def get_state(self):
        return self.state

    def set_vid_attributes(self, attributes):
        if not isinstance(attributes, list):
            raise TestError('attributes is not a list.')
        self.attributes = attributes
    def get_vid_attributes(self):
        return self.attributes

    def set_vid_statements(self, statements):
        if not isinstance(statements, list):
            raise TestError('statements is not a list.')
        self.statements = statements
    def get_vid_statements(self):
        return self.statements
