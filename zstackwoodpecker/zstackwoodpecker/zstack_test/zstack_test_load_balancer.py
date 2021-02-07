'''
The union test class for load balancer test

@author: Youyk

'''
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.header.vm as vm_header
import zstackwoodpecker.header.port_forwarding as pf_header
import zstackwoodpecker.header.load_balancer as lb_header
import zstackwoodpecker.header.vip as vip_header
import zstackwoodpecker.zstack_test.checker_factory as checker_factory

class ZstackTestLoadBalancer(lb_header.TestLoadBalancer):
    def __init__(self):
        self.load_balancer_listeners = {}
        self.separated_vr = False
        self.isVcenter = False
        super(ZstackTestLoadBalancer, self).__init__()

    def __hash__(self):
        return hash(self.get_load_balancer().uuid)

    def __eq__(self, other):
        return self.get_load_balancer().uuid == other.get_load_balancer().uuid

    def get_load_balancer_listeners(self):
        return self.load_balancer_listeners

    def add_load_balancer_listener(self, lbl):
        if not lbl.get_load_balancer_listener().uuid \
                in self.get_load_balancer_listeners().keys():
            self.load_balancer_listeners[lbl.get_load_balancer_listener().uuid]\
                    = lbl

    def remove_load_balancer_listener(self, lbl_uuid):
        if lbl_uuid in self.get_load_balancer_listeners().keys():
            self.load_balancer_listeners.pop(lbl_uuid)

    def create(self, name, vip_uuid, session_uuid = None):
        self.load_balancer = \
                net_ops.create_load_balancer(vip_uuid, name, \
                self.separated_vr, session_uuid)
        super(ZstackTestLoadBalancer, self).create()
        return self.get_load_balancer()

    def is_separated_vr(self):
        return self.separated_vr

    def set_separated_vr(self):
        self.separated_vr = True

    def delete(self):
        net_ops.delete_load_balancer(self.get_load_balancer().uuid)
        super(ZstackTestLoadBalancer, self).delete()

    def check(self):
        import zstackwoodpecker.zstack_test.checker_factory as checker_factory
        checker = checker_factory.CheckerFactory().create_checker(self)
        checker.check()
        super(ZstackTestLoadBalancer, self).check()
        pass

    def create_listener(self, lbl_creation_option):
        listener = ZstackTestLoadBalancerListener()
        lbl_creation_option.set_load_balancer_uuid(self.get_load_balancer().uuid)
        listener.set_creation_option(lbl_creation_option)
        listener.create()
        self.add_load_balancer_listener(listener)
        return listener

    def delete_listener(self, lbl_uuid):
        self.get_load_balancer_listeners()[lbl_uuid].delete()

class ZstackTestLoadBalancerListener(lb_header.TestLoadBalancerListener):
    def __init__(self):
        self.creation_option = None
        self.vm_nics_uuid_list = []
        super(ZstackTestLoadBalancerListener, self).__init__()

    def set_creation_option(self, lb_creation_option):
        self.creation_option = lb_creation_option

    def get_creation_option(self):
        return self.creation_option

    def _rm_system_tag(self, system_tag_key):
        pre_tag = self.get_creation_option().get_system_tags()
        if not pre_tag:
            return

        new_tag = []
        for tag in pre_tag:
            if not tag.startswith(system_tag_key):
                new_tag.append(tag)

        self.get_creation_option().set_system_tags(new_tag)

    def _add_system_tag(self, tag):
        pre_tag = self.get_creation_option().get_system_tags()
        if not pre_tag:
            pre_tag = []

        pre_tag.append(tag)
        self.get_creation_option().set_system_tags(pre_tag)

    def set_algorithm(self, algorithm):
        self._rm_system_tag('balancerAlgorithm')
        self._add_system_tag('balancerAlgorithm::%s' % algorithm)
        super(ZstackTestLoadBalancerListener, self).set_algorithm(algorithm)

    def create(self):
        self.load_balancer_listener = net_ops.create_load_balancer_listener(self.get_creation_option())
        super(ZstackTestLoadBalancerListener, self).create()
        return self.get_load_balancer_listener()

    def delete(self):
        net_ops.delete_load_balancer_listener(self.get_load_balancer_listener().uuid)
        super(ZstackTestLoadBalancerListener, self).delete()

    def add_nics(self, vm_nics_uuid_list, session_uuid = None):
        self.load_balancer = \
                net_ops.add_nic_to_load_balancer(\
                self.get_load_balancer_listener().uuid,\
                vm_nics_uuid_list,\
                session_uuid)
        
        for vm_nic_uuid in vm_nics_uuid_list:
            if not vm_nic_uuid in self.vm_nics_uuid_list:
                self.vm_nics_uuid_list.append(vm_nic_uuid)

    def get_vm_nics_uuid(self):
        return self.vm_nics_uuid_list
    
    def remove_nics(self, vm_nics_uuid_list, session_uuid = None):
        self.load_balancer = \
                net_ops.remove_nic_from_load_balancer(\
                self.get_load_balancer_listener().uuid,\
                vm_nics_uuid_list, \
                session_uuid)

        for vm_nic_uuid in vm_nics_uuid_list:
            if vm_nic_uuid in self.vm_nics_uuid_list:
                self.vm_nics_uuid_list.remove(vm_nic_uuid)

