import zstackwoodpecker.header.header as zstack_header
CREATED = 'created'
ATTACHED = 'attached'
DETACHED = 'detached'
DELETED = 'deleted'

class TestSecurityGroup(zstack_header.ZstackObject):

    def __init__(self):
        self.security_group = None
        self.state = None

    def __repr__(self):
        if self.security_group:
            return '%s-%s' % (self.__class__.__name__, self.security_group.uuid)
        return '%s-None' % self.__class__.__name__

    def create(self):
        self.state = CREATED

    def attach(self, target_nic_uuids):
        self.state = ATTACHED

    def detach(self, target_nic_uuids):
        self.state = DETACHED

    def delete(self):
        self.state = DELETED

    def add_rule(self, target_rules):
        pass

    def delete_rule(self, target_rules):
        pass

    def check(self):
        pass

    def get_security_group(self):
        return self.security_group

    def get_state(self):
        return self.state

class TestSecurityGroupVm(object):
    def attach(self, sg, vm_nic):
        pass

    def detach(self, sg, vm_nic):
        pass

    def check(self):
        pass
