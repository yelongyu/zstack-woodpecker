import zstackwoodpecker.header.header as zstack_header
CREATED = 'Created'
DELETED = 'Deleted'
ENABLED = 'Enabled'
DISABLED = 'Disabled'

class TestAccount(zstack_header.ZstackObject):
    def __init__(self):
        self.account = None
        self.state = None

    def __repr__(self):
        if self.account:
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

    def get_account(self):
        return self.account

    def set_account(self, account):
        self.account = account
        return self.account

    def get_state(self):
        return self.state
