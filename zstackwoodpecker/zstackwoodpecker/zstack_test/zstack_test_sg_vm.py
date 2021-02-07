'''
zstack security group and vm mediator class

It will record all sg and vm relationship and do the real check.


@author: Youyk
'''

import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.header.vm as vm_header
import zstackwoodpecker.header.security_group as sg_header

TCP_INGRESS = 'tcp_ingress'
TCP_EGRESS = 'tcp_egress'
UDP_INGRESS = 'udp_ingress'
UDP_EGRESS = 'udp_egress'
ICMP_INGRESS = 'icmp_ingress'
ICMP_EGRESS = 'icmp_egress'


class ZstackTestSgVm(sg_header.TestSecurityGroupVm):
    def __init__(self):
        #{test_sg_obj:[nic_obj]}
        self.sg_nic_dict = {}
        #{nic_uuid:[test_sg_obj]}
        self.nic_sg_dict = {}
        #each l3 will have one test vm. {l3_uuid: test_stub_vm_obj}
        self.stub_vm_dict = {}
        #{test_vm_obj: [nic_uuid]}
        self.vm_nic_dict = {}
        #{nic_uuid:{'tcp_ingress':{allowedCidr1:[rule1, rule2], allowedCidr2:[]}, 'tcp_egress':{}, } nic_uuid2:{}}
        self.nic_rule_dict = {}
        #[test_vm_obj]
        self.detached_vm_list = []

    def __repr__(self):
        return self.__class__.__name__

    def get_all_nics(self):
        return self.nic_sg_dict.keys()

    def get_detached_vm(self):
        return self.detached_vm_list

    def get_all_sgs(self):
        return self.sg_nic_dict.keys()

    def get_nic_list_by_sg(self, test_sg):
        if self.sg_nic_dict.has_key(test_sg):
            return self.sg_nic_dict[test_sg]

    def get_sg_list_by_nic(self, nic_uuid):
        if self.nic_sg_dict.has_key(nic_uuid):
            return self.nic_sg_dict[nic_uuid]

    def get_vm_by_nic(self, nic_uuid):
        for key, values in self.vm_nic_dict.items():
            if nic_uuid in values:
                return key

    def get_nic_list_by_vm(self, vm):
        if self.vm_nic_dict.has_key(vm):
            return self.vm_nic_dict[vm]

    def _add_sg_nic_dict(self, sg, target_nic):
        if self.sg_nic_dict.has_key(sg):
            nic_uuids = []
            for nic in self.get_nic_list_by_sg(sg):
                nic_uuids.append(nic.uuid)
            if not target_nic.uuid in nic_uuids:
                self.sg_nic_dict[sg].append(target_nic)
        else:
            self.sg_nic_dict[sg] = [target_nic]

    def _add_nic_sg_dict(self, nic_uuid, sg):
        if self.nic_sg_dict.has_key(nic_uuid):
            if not sg in self.get_sg_list_by_nic(nic_uuid):
                self.nic_sg_dict[nic_uuid].append(sg)
        else:
            self.nic_sg_dict[nic_uuid] = [sg]

    #when calling remove nic function, the nic might be not existed in db. So can't get full nic obj from nic_uuid
    def _remove_nic_from_sg_nic_dict(self, sg, nic_uuid):
        if self.sg_nic_dict.has_key(sg):
            nic_list = self.get_nic_list_by_sg(sg)
            for nic in nic_list:
                if nic.uuid == nic_uuid:
                    self.sg_nic_dict[sg].remove(nic)

    #detach nic from sg.
    def _detach(self, test_sg, nic_uuid):
        self._remove_nic_from_sg_nic_dict(test_sg, nic_uuid)

        if self.nic_sg_dict.has_key(nic_uuid):
            if test_sg in self.get_sg_list_by_nic(nic_uuid):
                self.nic_sg_dict[nic_uuid].remove(test_sg)
            if not self.get_sg_list_by_nic(nic_uuid):
                self.nic_sg_dict.pop(nic_uuid)
                self._rm_nic_vm_map(nic_uuid)

    #detach sg from l3. It means all nic on the l3 will be detached from sg.
    def _detach_l3(self, test_sg, l3_uuid):
        for nic_uuid in test_sg.get_attached_nics_by_l3(l3_uuid):
            self._detach(test_sg, nic_uuid)

    #delete sg.
    def _remove_sg(self, test_sg):
        if self.sg_nic_dict.has_key(test_sg):
            nic_list = self.sg_nic_dict.pop(test_sg)
            for nic in nic_list:
                self.nic_sg_dict[nic.uuid].remove(test_sg)
                if not self.nic_sg_dict[nic.uuid]:
                    self.nic_sg_dict.pop(nic.uuid)
                    self._rm_nic_vm_map(nic.uuid)

    #delete nic, e.g. VM destroy
    def _remove_nic_from_sg(self, nic_uuid):
        if self.nic_sg_dict.has_key(nic_uuid):
            sg_list = self.nic_sg_dict.pop(nic_uuid)
            for sg in sg_list:
                self._remove_nic_from_sg_nic_dict(sg, nic_uuid)

    #add vm and nic mapping, when VM's NIC is attached to SG.
    def _map_nic_vm(self, nic_uuid, test_vm):
        if not self.vm_nic_dict.has_key(test_vm):
            self.vm_nic_dict[test_vm] = [nic_uuid]
        else:
            if not nic_uuid in self.vm_nic_dict[test_vm]:
                self.vm_nic_dict[test_vm].append(nic_uuid)

        if test_vm in self.detached_vm_list:
            self.detached_vm_list.remove(test_vm)

    #Remove VM and NIC mapping, when detach VM's nic or VM's NICs lost all attached SG. 
    def _rm_nic_vm_map(self, nic_uuid):
        test_vm = self.get_vm_by_nic(nic_uuid)
        if not test_vm:
            return
        self.vm_nic_dict[test_vm].remove(nic_uuid)

        #no other attached NICs for this VM.
        if not self.vm_nic_dict[test_vm]:
            #still keep test_vm object in dict, until test_vm is destroyed.
            #self.vm_nic_dict.pop(test_vm)
            self.detached_vm_list.append(test_vm)

    def attach(self, test_sg, nic_vm_list, ipv6 = None):
        '''
        nic_vm_list = [(nic_uuid, test_vm), (nic_uuid2, test_vm2)] record the test_vm's nic_uuid for attaching to SG.
        test_vm is ZstackTestVm()

        SG test case should call this API to attach nic to SG. 
        '''
        nic_list = []
        for nic_vm in nic_vm_list:
            nic_uuid = nic_vm[0]
            test_vm = nic_vm[1]
            nic_list.append(nic_uuid)
            nic = test_lib.lib_get_nic_by_uuid(nic_uuid)
            self._add_nic_sg_dict(nic_uuid, test_sg)
            self._add_sg_nic_dict(test_sg, nic)
            self._map_nic_vm(nic_uuid, test_vm)

        if not ipv6:
            test_sg.attach(nic_list)
        else:
            test_sg.attach(nic_list, ipv6 = ipv6)

    #SG test case should call this API to detach nic from SG. 
    def detach(self, test_sg, nic_uuid):
        self._detach(test_sg, nic_uuid)
        test_sg.detach(nic_uuid)

    #SG detach sg from l3.
    def detach_l3(self, test_sg, l3_uuid):
        self._detach_l3(test_sg, l3_uuid)
        test_sg.detach_l3(l3_uuid)

    def create_sg(self, sg_creation_option):
        import zstackwoodpecker.zstack_test.zstack_test_security_group as zstack_sg_header
        sg = zstack_sg_header.ZstackTestSecurityGroup()
        sg.set_creation_option(sg_creation_option)
        sg.create()
        self.sg_nic_dict[sg] = []
        return sg
        
    #SG test case should call this API to delete SG. 
    def delete_sg(self, test_sg):
        self._remove_sg(test_sg)
        test_sg.delete()

    def delete_vm(self, test_vm):
        #test_vm was not attached to any SG.
        if test_vm in self.detached_vm_list:
            self.detached_vm_list.remove(test_vm)
            return

        #test_vm has some attached SG.
        for nic_uuid in self.vm_nic_dict[test_vm]:
            self._remove_nic_from_sg(nic_uuid)

        self.vm_nic_dict.pop(test_vm)

    def add_stub_vm(self, l3_uuid, stub_vm):
        self.stub_vm_dict[l3_uuid] = stub_vm

    def delete_stub_vm(self, l3_uuid):
        if self.stub_vm_dict.has_key(l3_uuid):
            del self.stub_vm_dict[l3_uuid]

    def get_stub_vm(self, l3_uuid):
        if self.stub_vm_dict.has_key(l3_uuid):
            return self.stub_vm_dict[l3_uuid]

    def get_all_stub_vm(self):
        stub_vm_list = []
        for value in self.stub_vm_dict.values():
            if not value in stub_vm_list:
                stub_vm_list.append(value)

        return stub_vm_list

    def _check_vm_destroyed(self):
        for vm in self.vm_nic_dict.keys():
            if vm.state == vm_header.DESTROYED \
                    or vm.state == vm_header.EXPUNGED:
                nic_list = self.get_nic_list_by_vm(vm)
                for nic in nic_list:
                    sg_list = self.get_sg_list_by_nic(nic)
                    for sg in sg_list:
                        sg.delete_vm(vm)

                self.delete_vm(vm)

    def _check_sg_destroyed(self):
        for sg in self.sg_nic_dict.keys():
            if sg.state == sg_header.DELETED:
                self._remove_sg(sg)
                test_util.test_warn("Catch undeleted SG. It might be because SG deletion is not called by delete_sg() API.")

    def get_nic_tcp_ingress_all_addr(self, nic_uuid):
        if self.nic_rule_dict.has_key(nic_uuid):
            return self.nic_rule_dict[nic_uuid][TCP_INGRESS].keys()
        else:
            return []

    def get_nic_tcp_ingress_rule_by_addr(self, nic_uuid, allowedCidr):
        if self.nic_rule_dict.has_key(nic_uuid) and self.nic_rule_dict[nic_uuid][TCP_INGRESS].has_key(allowedCidr):
            return self.nic_rule_dict[nic_uuid][TCP_INGRESS][allowedCidr]
        else:
            return []

    def get_nic_tcp_ingress_rules(self, nic_uuid):
        tcp_ingress_rules = []
        if self.nic_rule_dict.has_key(nic_uuid):
            for rules in self.nic_rule_dict[nic_uuid][TCP_INGRESS].values():
                tcp_ingress_rules.extend(rules)
        return tcp_ingress_rules

    def get_nic_tcp_egress_all_addr(self, nic_uuid):
        if self.nic_rule_dict.has_key(nic_uuid):
            return self.nic_rule_dict[nic_uuid][TCP_EGRESS].keys()
        else:
            return []

    def get_nic_tcp_egress_rule_by_addr(self, nic_uuid, allowedCidr):
        if self.nic_rule_dict.has_key(nic_uuid) and self.nic_rule_dict[nic_uuid][TCP_EGRESS].has_key(allowedCidr):
            return self.nic_rule_dict[nic_uuid][TCP_EGRESS][allowedCidr]
        else:
            return []

    def get_nic_tcp_egress_rules(self, nic_uuid):
        tcp_egress_rules = []
        if self.nic_rule_dict.has_key(nic_uuid):
            for rules in self.nic_rule_dict[nic_uuid][TCP_EGRESS].values():
                tcp_egress_rules.extend(rules)
        return tcp_egress_rules

    def get_nic_udp_ingress_all_addr(self, nic_uuid):
        if self.nic_rule_dict.has_key(nic_uuid):
            return self.nic_rule_dict[nic_uuid][UDP_INGRESS].keys()
        else:
            return []

    def get_nic_udp_ingress_rule_by_addr(self, nic_uuid, allowedCidr):
        if self.nic_rule_dict.has_key(nic_uuid) and self.nic_rule_dict[nic_uuid][UDP_INGRESS].has_key(allowedCidr):
            return self.nic_rule_dict[nic_uuid][UDP_INGRESS][allowedCidr]
        else:
            return []

    def get_nic_udp_ingress_rules(self, nic_uuid):
        udp_ingress_rules = []
        if self.nic_rule_dict.has_key(nic_uuid):
            for rules in self.nic_rule_dict[nic_uuid][UDP_INGRESS].values():
                udp_ingress_rules.extend(rules)
        return udp_ingress_rules

    def get_nic_udp_egress_all_addr(self, nic_uuid):
        if self.nic_rule_dict.has_key(nic_uuid):
            return self.nic_rule_dict[nic_uuid][UDP_EGRESS].keys()
        else:
            return []

    def get_nic_udp_egress_rule_by_addr(self, nic_uuid, allowedCidr):
        if self.nic_rule_dict.has_key(nic_uuid) and self.nic_rule_dict[nic_uuid][UDP_EGRESS].has_key(allowedCidr):
            return self.nic_rule_dict[nic_uuid][UDP_EGRESS][allowedCidr]
        else:
            return []

    def get_nic_udp_egress_rules(self, nic_uuid):
        udp_egress_rules = []
        if self.nic_rule_dict.has_key(nic_uuid):
            for rules in self.nic_rule_dict[nic_uuid][UDP_EGRESS].values():
                udp_egress_rules.extend(rules)
        return udp_egress_rules

    def get_nic_icmp_ingress_all_addr(self, nic_uuid):
        if self.nic_rule_dict.has_key(nic_uuid):
            return self.nic_rule_dict[nic_uuid][ICMP_INGRESS].keys()
        else:
            return []

    def get_nic_icmp_ingress_rule_by_addr(self, nic_uuid, allowedCidr):
        if self.nic_rule_dict.has_key(nic_uuid) and self.nic_rule_dict[nic_uuid][ICMP_INGRESS].has_key(allowedCidr):
            return self.nic_rule_dict[nic_uuid][ICMP_INGRESS][allowedCidr]
        else:
            return []

    def get_nic_icmp_ingress_rules(self, nic_uuid):
        icmp_ingress_rules = []
        if self.nic_rule_dict.has_key(nic_uuid):
            for rules in self.nic_rule_dict[nic_uuid][ICMP_INGRESS].values():
                icmp_ingress_rules.extend(rules)
        return icmp_ingress_rules

    def get_nic_icmp_egress_all_addr(self, nic_uuid):
        if self.nic_rule_dict.has_key(nic_uuid):
            return self.nic_rule_dict[nic_uuid][ICMP_EGRESS].keys()
        else:
            return []

    def get_nic_icmp_egress_rule_by_addr(self, nic_uuid, allowedCidr):
        if self.nic_rule_dict.has_key(nic_uuid) and self.nic_rule_dict[nic_uuid][ICMP_EGRESS].has_key(allowedCidr):
            return self.nic_rule_dict[nic_uuid][ICMP_EGRESS][allowedCidr]
        else:
            return []

    def get_nic_icmp_egress_rules(self, nic_uuid):
        icmp_egress_rules = []
        if self.nic_rule_dict.has_key(nic_uuid):
            for rules in self.nic_rule_dict[nic_uuid][ICMP_EGRESS].values():
                icmp_egress_rules.extend(rules)
        return icmp_egress_rules

    def _consolidate_nic_rules(self):
        for nic, sg_list in self.nic_sg_dict.items():
            self.nic_rule_dict[nic] = {TCP_INGRESS:{}, TCP_EGRESS:{}, UDP_INGRESS:{}, UDP_EGRESS:{}, ICMP_INGRESS:{}, ICMP_EGRESS:{}}
            for sg in sg_list:
                for allowedCidr in sg.get_tcp_ingress_all_addr():
                    if not self.nic_rule_dict[nic][TCP_INGRESS].has_key(allowedCidr):
                        self.nic_rule_dict[nic][TCP_INGRESS][allowedCidr] = list(sg.get_tcp_ingress_rule_by_addr(allowedCidr))
                    else:
                        self.nic_rule_dict[nic][TCP_INGRESS][allowedCidr].extend(sg.get_tcp_ingress_rule_by_addr(allowedCidr))
                for allowedCidr in sg.get_tcp_egress_all_addr():
                    if not self.nic_rule_dict[nic][TCP_EGRESS].has_key(allowedCidr):
                        self.nic_rule_dict[nic][TCP_EGRESS][allowedCidr] = list(sg.get_tcp_egress_rule_by_addr(allowedCidr))
                    else:
                        self.nic_rule_dict[nic][TCP_EGRESS][allowedCidr].extend(sg.get_tcp_egress_rule_by_addr(allowedCidr))

                for allowedCidr in sg.get_udp_ingress_all_addr():
                    if not self.nic_rule_dict[nic][UDP_INGRESS].has_key(allowedCidr):
                        self.nic_rule_dict[nic][UDP_INGRESS][allowedCidr] = list(sg.get_udp_ingress_rule_by_addr(allowedCidr))
                    else:
                        self.nic_rule_dict[nic][UDP_INGRESS][allowedCidr].extend(sg.get_udp_ingress_rule_by_addr(allowedCidr))
                for allowedCidr in sg.get_udp_egress_all_addr():
                    if not self.nic_rule_dict[nic][UDP_EGRESS].has_key(allowedCidr):
                        self.nic_rule_dict[nic][UDP_EGRESS][allowedCidr] = list(sg.get_udp_egress_rule_by_addr(allowedCidr))
                    else:
                        self.nic_rule_dict[nic][UDP_EGRESS][allowedCidr].extend(sg.get_udp_egress_rule_by_addr(allowedCidr))

                for allowedCidr in sg.get_icmp_ingress_all_addr():
                    if not self.nic_rule_dict[nic][ICMP_INGRESS].has_key(allowedCidr):
                        self.nic_rule_dict[nic][ICMP_INGRESS][allowedCidr] = list(sg.get_icmp_ingress_rule_by_addr(allowedCidr))
                    else:
                        self.nic_rule_dict[nic][ICMP_INGRESS][allowedCidr].extend(sg.get_icmp_ingress_rule_by_addr(allowedCidr))
                for allowedCidr in sg.get_icmp_egress_all_addr():
                    if not self.nic_rule_dict[nic][ICMP_EGRESS].has_key(allowedCidr):
                        self.nic_rule_dict[nic][ICMP_EGRESS][allowedCidr] = list(sg.get_icmp_egress_rule_by_addr(allowedCidr))
                    else:
                        self.nic_rule_dict[nic][ICMP_EGRESS][allowedCidr].extend(sg.get_icmp_egress_rule_by_addr(allowedCidr))

    def update(self):
        self._check_vm_destroyed()
        self._check_sg_destroyed()
        self._consolidate_nic_rules()

    def check(self):
        import zstackwoodpecker.zstack_test.checker_factory as checker_factory
        self.update()
        checker = checker_factory.CheckerFactory().create_checker(self)
        checker.check()
        super(ZstackTestSgVm , self).check()
