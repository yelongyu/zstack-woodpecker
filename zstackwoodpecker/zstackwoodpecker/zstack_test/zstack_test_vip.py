'''
The union test class for test multi pf rules with same vip 

@author: Youyk

'''
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.header.vm as vm_header
import zstackwoodpecker.header.port_forwarding as pf_header
import zstackwoodpecker.header.eip as eip_header
import zstackwoodpecker.header.vip as vip_header
import zstackwoodpecker.zstack_test.checker_factory as checker_factory
import zstackwoodpecker.zstack_test.zstack_test_eip as zstack_eip_header
import zstackwoodpecker.zstack_test.zstack_test_port_forwarding as zstack_pf_header

class ZstackTestVip(vip_header.TestVip):
    def __init__(self):
        #a list including all TestPortForwarding using same vip
        self.pf_list = []
        self.pf_dict = {vm_header.RUNNING:[], vm_header.STOPPED:[], pf_header.DETACHED:[]}
        self.eip = None
        self.lb = None
        self.isVcenter = False
        #not used currently
        self.creation_option = None
        super(ZstackTestVip, self).__init__()

    def __hash__(self):
        return hash(self.get_vip().uuid)

    def __eq__(self, other):
        return self.get_vip().uuid == other.get_vip().uuid

    #not used currently
    def set_creation_option(self, vip_creation_option):
        self.creation_option = vip_creation_option

    #not used currently
    def get_creation_option(self):
        return self.creation_option

    def create(self):
        self.vip = net_ops.create_vip(self.get_creation_option())
        super(ZstackTestVip, self).create()
        return self.vip

    def get_snat_ip_as_vip(self, snat_ip):
        self.vip = net_ops.get_snat_ip_as_vip(snat_ip)
        super(ZstackTestVip, self).create()
        return self.vip

    def delete(self):
        net_ops.delete_vip(self.get_vip().uuid)
        #delete vip will release all services belong to vip. So needs to update
        #pf and eip.
        for pf in self.get_pf_list():
            pf.state = pf_header.DELETED

        if self.eip:
            self.eip.state = eip_header.DELETED

        super(ZstackTestVip, self).delete()

    def attach_pf(self, pf):
        '''
        Be called after pf is created. 
        @param: pf: ZstackTestPortForwarding()
        '''
        if not pf in self.pf_list:
            self.pf_list.append(pf)

        self.state = vip_header.ATTACHED
        self.set_use_for(vip_header.PortForwarding)

    def attach_eip(self, eip):
        '''
        Be called after eip is created. 
        @param: pf: ZstackTestEip()
        '''
        self.eip = eip
        self.state = vip_header.ATTACHED
        self.set_use_for(vip_header.Eip)

    def attach_lb(self, lb):
        self.lb = lb
        self.state = vip_header.ATTACHED
        self.set_use_for(vip_header.LoadBalancer)

    def _detach_lb(self):
        self.lb = None

    def _detach_pf(self, pf):
        self.pf_list.remove(pf)

    def _detach_eip(self):
        self.eip = None

    def check(self):
        self.update()
        checker = checker_factory.CheckerFactory().create_checker(self)
        checker.check()
        super(ZstackTestVip, self).check()

    def update(self):
        #PF EIP detach operations might change VIP inventory
        import zstackwoodpecker.operations.resource_operations as res_ops
        vip_uuid = self.vip.uuid
        condition = res_ops.gen_query_conditions('uuid', '=', vip_uuid)
        vip = res_ops.query_resource(res_ops.VIP, condition)[0]

        temp_pf_list = list(self.pf_list)
        for pf in temp_pf_list:
            pf.update()
            if pf.state == pf_header.DELETED:
                self._detach_pf(pf)

        if self.eip:
            self.eip.update()
            if self.eip.state == eip_header.DELETED:
                self._detach_eip()

        #When vip is not used for PF or EIP, the VIP is detached status
        if not self.pf_list and not self.eip and not self.lb:
            if self.get_use_for():
                self.set_use_for()
            if self.state == vip_header.ATTACHED:
                self.state = vip_header.DETACHED
            return

        #otherwise it is in attached status.
        if self.state == vip_header.CREATED:
            self.state = vip_header.ATTACHED

        self.analyze_pf_rules()

    def analyze_pf_rules(self):
        '''
        sort and make pf rules into different groups. 
        1. pf rules attached to living vms.
        2. pf rules attached to the stopped vms.
        2. pf rules is not attached to any vms.
        '''
        self.pf_dict = {vm_header.RUNNING:[], vm_header.STOPPED:[], pf_header.DETACHED:[]}
        for pf in self.pf_list:
            if pf.state == pf_header.ATTACHED and \
                    pf.target_vm.state == vm_header.RUNNING:
                self.pf_dict[vm_header.RUNNING].append(pf)
                continue
            if pf.state == pf_header.ATTACHED and \
                    pf.target_vm.state == vm_header.STOPPED:
                self.pf_dict[vm_header.STOPPED].append(pf)
                continue
            if pf.state == pf_header.DETACHED:
                self.pf_dict[pf_header.DETACHED].append(pf)
                continue

    def get_pf_list(self):
        return self.pf_list

    def get_pf_list_for_running_vm(self):
        return self.pf_dict[vm_header.RUNNING]

    def get_pf_list_for_stopped_vm(self):
        return self.pf_dict[vm_header.STOPPED]

    def get_detached_pf_list(self):
        return self.pf_dict[pf_header.DETACHED]

    def get_eip(self):
        return self.eip

    def create_eip(self, eip_creation_option, target_vm):
        '''
        combine eip.create() + vip.attach_eip()
        '''
        eip = zstack_eip_header.ZstackTestEip()
        eip.set_creation_option(eip_creation_option)
        eip.create(target_vm)
        self.attach_eip(eip)
        return eip

    def create_pf(self, pf_creation_option, target_vm):
        '''
        combine pf.create() + vip.attach_pf()
        '''
        pf = zstack_pf_header.ZstackTestPortForwarding()
        pf.set_creation_option(pf_creation_option)
        pf.create(target_vm)
        self.attach_pf(pf)
        return pf

