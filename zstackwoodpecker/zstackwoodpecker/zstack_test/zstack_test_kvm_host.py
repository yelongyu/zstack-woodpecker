'''
zstack KVM Host class

@author: Youyk
'''
import zstackwoodpecker.header.host as host_header
import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_util as test_util

MAINTAIN_EVENT = 'maintain'
ENABLE_EVENT = 'enable'
DISABLE_EVENT = 'disable'
PREMAINTAIN_EVENT = 'preMaintain'

state_event_dict = {MAINTAIN_EVENT: host_header.MAINTENANCE,
        ENABLE_EVENT: host_header.ENABLED,
        DISABLE_EVENT: host_header.DISABLED}

class ZstackTestKvmHost(host_header.TestHost):
    def __init__(self):
        self.host_creation_option = test_util.HostOption()
        super(ZstackTestKvmHost, self).__init__()

    def add(self):
        self.host = host_ops.add_kvm_host(self.host_creation_option)
        super(ZstackTestKvmHost, self).create()

    def set_host(self, host_inv):
        self.host = host_inv
        self.state = host_inv.state
        self.connection_state = host_inv.status

    def delete(self):
        host_ops.delete_host(self.host.uuid)
        super(ZstackTestKvmHost, self).delete()

    def check(self):
        import zstackwoodpecker.zstack_test.checker_factory as checker_factory
        checker = checker_factory.CheckerFactory().create_checker(self)
        checker.check()
        super(ZstackTestKvmHost, self).check()

    def set_creation_option(self, host_creation_option):
        self.host_creation_option = host_creation_option

    def get_creation_option(self):
        return self.host_creation_option

    def change_state(self, state):
        host_ops.change_host_state(self.host.uuid, state)
        self.state = state_event_dict[state]

    def maintain(self):
        self.change_state(MAINTAIN_EVENT)

    def enable(self):
        self.change_state(ENABLE_EVENT)

    def disable(self):
        self.change_state(DISABLE_EVENT)

    def reconnect(self):
        host_ops.reconnect_host(self.host.uuid)

    def update(self):
        cond =  res_ops.gen_query_conditions("uuid", "=", self.host.uuid)
        host_inv = res_ops.query_resource(res_ops.HOST, cond)[0]
        self.host = host_inv
        self.state = host_inv.state

