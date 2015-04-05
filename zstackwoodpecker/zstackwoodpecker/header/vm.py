import apibinding.inventory as inventory
import zstackwoodpecker.header.header as zstack_header

RUNNING = inventory.RUNNING
STOPPED = inventory.STOPPED
DESTROYED = inventory.DESTROYED

class TestVm(zstack_header.ZstackObject):

    def __init__(self):
        self.vm = None
        self.state = None

    def __repr__(self):
        if self.vm:
            return '%s-%s' % (self.__class__.__name__, self.vm.uuid)
        return '%s-None' % self.__class__.__name__

    def create(self):
        self.state = RUNNING

    def destroy(self):
        self.state = DESTROYED

    def start(self):
        self.state = RUNNING

    def stop(self):
        self.state = STOPPED

    def reboot(self):
        self.state = RUNNING

    def migrate(self, target_host):
        pass

    def check(self):
        pass

    def get_vm(self):
        return self.vm

    def get_state(self):
        return self.state

    def set_state(self, state):
        self.state = state

    def update(self):
        pass
