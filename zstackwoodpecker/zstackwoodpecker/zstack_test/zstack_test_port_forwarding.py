'''
zstack port forwarding test class

@author: Youyk
'''
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.header.vm as vm_header
import zstackwoodpecker.header.security_group as sg_header
import zstackwoodpecker.header.port_forwarding as pf_header
import zstackwoodpecker.zstack_test.checker_factory as checker_factory

class ZstackTestPortForwarding(pf_header.TestPortForwarding):
    def __init__(self):
        self.target_vm = None
        self.pf_creation_option = None
        super(ZstackTestPortForwarding, self).__init__()

    def __hash__(self):
        return hash(self.port_forwarding.uuid)

    def __eq__(self, other):
        return self.port_forwarding.uuid == other.port_forwarding.uuid

    def set_creation_option(self, pf_creation_option):
        '''
            @param: pf_creation_opt: test_util.PortForwardingRuleOption()
        '''
        self.pf_creation_option = pf_creation_option

    def get_creation_option(self):
        return self.pf_creation_option

    def create(self, target_vm=None):
        if not self.pf_creation_option.get_vm_nic_uuid():
            self.state = pf_header.DETACHED
        else:
            if not self.pf_creation_option.get_vip_uuid():
                l3_uuid = test_lib.lib_get_l3_uuid_by_nic(self.pf_creation_option.get_vm_nic_uuid())
                if not 'PortForwarding' in test_lib.lib_get_l3_service_type(l3_uuid):
                    test_util.test_fail('[l3:] %s is not available PortForwarding network for [vm:] %s' % (l3_uuid, target_vm.get_vm().uuid))
                vr = test_lib.lib_find_vr_by_l3_uuid(l3_uuid)[0]
                vr_pub_nic = test_lib.lib_find_vr_pub_nic(vr)
                vip = net_ops.create_vip(vr_pub_nic.l3NetworkUuid)
                self.pf_creation_option.set_vip_uuid(vip.uuid)
            self.state = pf_header.ATTACHED
            if not target_vm:
                test_util.test_fail('You forget to add target_vm object when calling pf.create(target_vm). ')
                    
        self.port_forwarding = net_ops.create_port_forwarding(self.pf_creation_option)
        self.target_vm = target_vm
        super(ZstackTestPortForwarding, self).create()

        return self.port_forwarding

    def delete(self):
        net_ops.delete_port_forwarding(self.get_port_forwarding().uuid)
        self.target_vm = None
        super(ZstackTestPortForwarding, self).delete()

    def detach(self):
        self.target_vm = None
        self.port_forwarding = net_ops.detach_port_forwarding(self.get_port_forwarding().uuid)
        super(ZstackTestPortForwarding, self).detach()

    def attach(self, vm_nic_uuid, target_vm):
        self.pf_creation_option.set_vm_nic_uuid(vm_nic_uuid)
        self.target_vm = target_vm
        self.port_forwarding = net_ops.attach_port_forwarding(self.get_port_forwarding().uuid, vm_nic_uuid)
        super(ZstackTestPortForwarding, self).attach(vm_nic_uuid)

    def check(self):
        '''
        This function is deprecated. The standard Test case steps should be:
            1. vip.create()
            2. pf.create()
            3. vip.attach_pf(pf)
            4. vip.check()
        This change is due to same vip might be used by different pfs. So the 
        network connection testing should consider all pf rules belongs to same
        vip. 
        '''
        self.update()
        checker = checker_factory.CheckerFactory().create_checker(self)
        checker.check()
        super(ZstackTestPortForwarding, self).check()

    def update(self):
        if self.state == pf_header.ATTACHED \
                and (self.target_vm.state == vm_header.DESTROYED \
                or self.target_vm.state == vm_header.EXPUNGED):
            self.state = pf_header.DETACHED
            self.target_vm = None

    def get_target_vm(self):
        return self.target_vm
