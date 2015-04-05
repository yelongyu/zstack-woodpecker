import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.header.eip as eip_header
import zstackwoodpecker.header.vm as vm_header
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib

class ZstackTestEip(eip_header.TestEIP):
    def __init__(self):
        self.eip_creation_option = test_util.EipOption()
        self.target_vm = None #ZstackTestVm()
        self.vip = None
        super(ZstackTestEip, self).__init__()

    def create(self, target_vm=None):
        '''
        @param: target_vm: ZstackTestVm(). Target_vm is important. It is for
        eip testing. If target_vm is none, it means this eip is not attached 
        for any vm.
        '''
        self.eip = net_ops.create_eip(self.eip_creation_option)
        vm_nic_uuid = self.eip_creation_option.get_vm_nic_uuid()
        self.target_vm = target_vm
        vip_uuid = self.eip_creation_option.get_vip_uuid()
        self.vip = test_lib.lib_get_vip_by_uuid(vip_uuid)
        if vm_nic_uuid:
            self.state = eip_header.ATTACHED
        else:
            self.state = eip_header.DETACHED

        super(ZstackTestEip, self).create()

    def attach(self, vm_nic_uuid, target_vm):
        '''
        @param: test_vm: ZstackTestVm()
        '''
        self.eip = net_ops.attach_eip(self.eip.uuid, vm_nic_uuid)
        self.target_vm = target_vm
        super(ZstackTestEip, self).attach(vm_nic_uuid)

    def detach(self):
        self.eip = net_ops.detach_eip(self.eip.uuid)
        self.target_vm = None
        super(ZstackTestEip, self).detach()

    def delete(self):
        net_ops.delete_eip(self.eip.uuid)
        self.target_vm = None
        super(ZstackTestEip, self).delete()

    def check(self):
        self.update()
        import zstackwoodpecker.zstack_test.checker_factory as checker_factory
        checker = checker_factory.CheckerFactory().create_checker(self)
        checker.check()
        super(ZstackTestEip, self).check()

    def update(self):
        if self.target_vm:
            if self.target_vm.state == vm_header.DESTROYED and self.state == eip_header.ATTACHED:
                self.state = eip_header.DETACHED

    def set_creation_option(self, eip_creation_option):
        self.eip_creation_option = eip_creation_option

    def get_creation_option(self):
        return self.eip_creation_option

    def get_target_vm(self):
        return self.target_vm
