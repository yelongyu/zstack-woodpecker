import zstackwoodpecker.header.header as zstack_header
CONNECTED = 'Connected'
CONNECTING = 'Connecting'
DISCONNECTED = 'Disconnected'
ENABLED = 'Enabled'
DISABLED = 'Disabled'
PREMAINTENANCE = 'PreMaintenance'
MAINTENANCE = 'Maintenance'

class TestHost(zstack_header.ZstackObject):
    def __init__(self):
        self.host = None
        self.connection_state = None
        self.state = None

    def __repr__(self):
        if self.host:
            return '%s-%s' % (self.__class__.__name__, self.host.uuid)
        return '%s-None' % self.__class__.__name__

    def add(self):
        self.connection_state = CONNECTED
        self.state = ENABLED

    def delete(self):
        self.state = None
        self.connection_state = None

    def maintain(self):
        self.connection_state = DISCONNECTED
        self.state = MAINTENANCE

    def reconnect(self):
        self.connection_state = CONNECTED
        self.state = ENABLED

    def disable(self):
        self.state = DISABLED
        self.connection_state = DISCONNECTED

    def enable(self):
        self.state = ENABLED

    def check(self):
        pass

    def get_host(self):
        return self.host

    def get_state(self):
        return self.state

    def get_connection_state(self):
        return self.connection_state
