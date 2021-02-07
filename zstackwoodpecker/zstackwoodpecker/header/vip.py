import zstackwoodpecker.header.header as zstack_header
CREATED = 'created'
ATTACHED = 'attached'
DETACHED = 'detached'
DELETED = 'deleted'
Eip = 'Eip'
PortForwarding = 'PortForwarding'
LoadBalancer = 'LoadBalancer'

class TestVip(zstack_header.ZstackObject):
    def __init__(self):
        self.vip = None
        self.use_for = []
        self.state = None

    def __repr__(self):
        if self.vip:
            return '%s-%s' % (self.__class__.__name__, self.vip.uuid)
        return '%s-None' % self.__class__.__name__

    def create(self):
        self.state = CREATED

    def delete(self):
        self.vip = DELETED
        self.state = DELETED

    def set_use_for(self, service_type=None):
        self.use_for.append(service_type)

    def get_use_for(self):
        return self.use_for

    def get_state(self):
        return self.state

    def get_vip(self):
        return self.vip

    def check(self):
        pass

