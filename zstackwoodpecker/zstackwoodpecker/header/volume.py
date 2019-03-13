import zstackwoodpecker.header.header as zstack_header
CREATED = 'created'
ATTACHED = 'attached' #in primary storage
DETACHED = 'detached' #in primary storage
DELETED = 'deleted'
EXPUNGED = 'expunged'

ROOT_VOLUME = 'Root'
DATA_VOLUME = 'Data'

class TestVolume(zstack_header.ZstackObject):

    def __init__(self):
        self.volume = None
        self.state = None
        self.storage_state = None
        self.target_vm = None
        self.delete_policy = None
        self.delete_delay_time = None
        self.md5sum = ''

    def __repr__(self):
        if self.volume:
            return '%s-%s' % (self.__class__.__name__, self.volume.uuid)
        return '%s-None' % self.__class__.__name__

    def create(self):
        '''
        Create a new volume from a volume offering
        '''
        self.state = CREATED

    def create_template(self):
        '''
        Create a volume template from a data or root volume
        '''
        pass

    def attach(self, target_vm):
        self.state = ATTACHED
        self.target_vm = target_vm
        self.target_vm.update()

    def detach(self):
        self.state = DETACHED
        self.target_vm.update()
        self.target_vm = None

    def delete(self):
        if self.state == ATTACHED:
            self.target_vm.update()
            self.target_vm = None

        if self.delete_policy != zstack_header.DELETE_DIRECT:
            self.state = DELETED
        else:
            self.state = EXPUNGED

    def expunge(self):
        if self.state == ATTACHED:
            self.target_vm.update()
            self.target_vm = None

        self.state = EXPUNGED

    def check(self):
        pass

    def set_volume(self, volume):
        '''
        Used for volume created by none volume operations, like snapshot
        '''
        self.volume = volume

    def set_state(self, state):
        self.state = state

    def set_target_vm(self, target_vm):
        self.target_vm = target_vm

    def get_volume(self):
        return self.volume

    def get_state(self):
        return self.state

    def get_storage_sate(self):
        return self.storage_state

    def get_target_vm(self):
        return self.target_vm

    def set_delete_policy(self, policy):
        self.delete_policy = policy

    def get_delete_policy(self):
        return self.delete_policy

    def set_delete_delay_time(self, time):
        self.delete_delay_time = time

    def get_md5sum(self):
        return self.md5sum

    def set_md5sum(self, md5sum):
        self.md5sum = md5sum

    def get_delete_delay_time(self):
        return self.delete_delay_time
