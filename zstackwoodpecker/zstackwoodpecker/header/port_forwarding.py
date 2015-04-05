import zstackwoodpecker.header.header as zstack_header
ATTACHED = 'PF_ATTACHED'
DETACHED = 'PF_DETACHED'
DELETED = 'DELETED'
SERVICE = 'PortForwarding'

class TestPortForwarding(zstack_header.ZstackObject):
    def __init__(self):
        self.port_forwarding = None
        self.state = None 

    def __repr__(self):
        if self.port_forwarding:
            return '%s-%s' % (self.__class__.__name__, self.port_forwarding.uuid)
        return '%s-None' % self.__class__.__name__

    def create(self):
        #create state is decided by if there is vm_nic assigned.
        pass

    def delete(self):
        self.state = DELETED

    def detach(self):
        self.state = DETACHED

    def attach(self, nic):
        self.state = ATTACHED

    def check(self):
        pass

    def get_port_forwarding(self):
        return self.port_forwarding

    def get_state(self):
        return self.state
