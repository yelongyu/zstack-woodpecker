import zstackwoodpecker.header.header as zstack_header
ATTACHED = 'eip_attached'
DETACHED = 'eip_detached'
DELETED = 'deleted'
SERVICE = 'Eip'

class TestEIP(zstack_header.ZstackObject):
    def __init__(self):
        self.eip = None
        self.state = None

    def __repr__(self):
        if self.eip:
            return '%s-%s' % (self.__class__.__name__, self.eip.uuid)
        return '%s-None' % self.__class__.__name__

    def attach(self, nic):
        self.state = ATTACHED

    def detach(self):
        self.state = DETACHED

    def delete(self):
        self.state = DELETED

    def create(self):
        pass

    def check(self):
        pass

    def get_eip(self):
        return self.eip

    def get_state(self):
        return self.state
