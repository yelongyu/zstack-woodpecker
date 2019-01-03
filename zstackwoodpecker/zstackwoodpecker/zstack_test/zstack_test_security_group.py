'''
zstack security group test class

@author: Youyk
'''
import zstackwoodpecker.header.security_group as sg_header
import zstackwoodpecker.header.vm as vm_header
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import apibinding.inventory as inventory

class ZstackTestSecurityGroup(sg_header.TestSecurityGroup):

    def __init__(self):
        self.sg_creation_option = None
        #save SG rules based on target address: {allowedCidr:[rule1, rule2]}
        self.icmp_ingress_rule = {} 
        self.icmp_egress_rule = {}
        self.tcp_ingress_rule = {}
        self.tcp_egress_rule = {}
        self.udp_ingress_rule = {}
        self.udp_egress_rule = {}
        #nic_dict will save attached nic per l3_uuid based: l3_uuid:[nic_uuid1, nic_uuid2]
        self.nic_dict = {}
        super(ZstackTestSecurityGroup, self).__init__()

    def __hash__(self):
        return hash(self.security_group.uuid)

    def __eq__(self, other):
        return self.security_group.uuid == other.security_group.uuid

    def create(self):
        self.security_group = net_ops.create_security_group(self.sg_creation_option)
        super(ZstackTestSecurityGroup, self).create()

    #target_nics are nic_uuid list. The attach() API should not be directly called by test case. Test case should call zstack_test_sg_vm.ZstackTestSgVm.attach() API. 
    def attach(self, target_nic_uuids, ipv6 = None):
        added_l3_uuid = []
        for nic in target_nic_uuids:
            l3_uuid = test_lib.lib_get_l3_uuid_by_nic(nic)
            self._add_nic(l3_uuid, nic)
            #In zstack, need attach Nic's L3 to SG, before add Nic to SG
            # If SG has been attached to L3, it should not be attached again.
            if l3_uuid in added_l3_uuid:
                continue
            conditions = res_ops.gen_query_conditions('uuid', '=', self.security_group.uuid)
            sg = res_ops.query_resource(res_ops.SECURITY_GROUP, conditions)[0]
            if l3_uuid in sg.attachedL3NetworkUuids:
                added_l3_uuid.append(l3_uuid)
                continue
            added_l3_uuid.append(l3_uuid)
            
            if not ipv6:
                net_ops.attach_security_group_to_l3(self.security_group.uuid, l3_uuid)

        net_ops.add_nic_to_security_group(self.security_group.uuid, target_nic_uuids)
        super(ZstackTestSecurityGroup, self).attach(target_nic_uuids)

    #The dettach() API should not be directly called by test case. Test case should call zstack_test_sg_vm.ZstackTestSgVm.detach() API. 
    def detach(self, target_nic_uuid):
        net_ops.remove_nic_from_security_group(self.security_group.uuid, [target_nic_uuid])
        self._rm_nic(target_nic_uuid)

        if not self.nic_dict:
            super(ZstackTestSecurityGroup, self).detach(target_nic_uuid)

    def detach_l3(self, l3_uuid):
        #FIXME: this operation has global impaction, if the other parallel case are doing security group testing on the same l3. E.g. the 1st case is testing sg connection, while the 2nd case might call detach_l3. 
        self._rm_l3(l3_uuid)
        net_ops.detach_security_group_from_l3(self.security_group.uuid, l3_uuid)

    #The delete() API should not be directly called by test case. Test case should call zstack_test_sg_vm.ZstackTestSgVm.delete_sg() API. 
    def delete(self):
        net_ops.delete_security_group(self.security_group.uuid)
        super(ZstackTestSecurityGroup, self).delete()
        self.nic_dict = {}

    #The check() API should not be directly called by test case. Test case should call zstack_test_sg_vm.ZstackTestSgVm.check() API.
    def check(self):
        import zstackwoodpecker.zstack_test.checker_factory as checker_factory
        #self.update()
        #checker = checker_factory.CheckerFactory().create_checker(self)
        #checker.check()
        super(ZstackTestSecurityGroup, self).check()

    #check attached VM's status. If VM is destroyed, it should be removed from nic_dict
    #This function doesn't work, if destroyed VM structure is not exist in DB. The next function should be called instead.
    #When test vm is destroyed, the update action is similar with detach()
    #def update(self):
    #    for test_vm in self.test_vm_list:
    #        if test_vm.state == vm_header.DESTROYED or test_vm.state == vm_header.EXPUNGED:
    #            self.delete_vm(test_vm)

    def delete_vm(self, test_vm):
        all_nics = self.get_all_attached_nics()
        for nic in test_vm.vm.vmNics:
            if nic.uuid in all_nics:
                test_util.test_logger('Test [vm:] %s is destroyed, need to remove its [nic:] %s from attached list. ' % (test_vm.vm.uuid, nic.uuid))
                self._rm_nic(nic.uuid)
                target_nic = nic.uuid

        if not self.nic_dict:
            super(ZstackTestSecurityGroup, self).detach(target_nic)

    def set_creation_option(self, sg_creation_option):
        self.sg_creation_option = sg_creation_option

    def get_creation_option(self):
        return self.sg_creation_option

    def add_rule(self, target_rule_objs, remote_security_group_uuid=None):
        rules = net_ops.add_rules_to_security_group(self.security_group.uuid, target_rule_objs, remote_security_group_uuid).rules
        for rule in rules:
            if rule.protocol == inventory.TCP:
                if rule.type == inventory.INGRESS:
                    self._add_rule(rule, self.tcp_ingress_rule)
                else:
                    self._add_rule(rule, self.tcp_egress_rule)
            elif rule.protocol == inventory.UDP:
                if rule.type == inventory.INGRESS:
                    self._add_rule(rule, self.udp_ingress_rule)
                else:
                    self._add_rule(rule, self.udp_egress_rule)
            elif rule.protocol == inventory.ICMP:
                if rule.type == inventory.INGRESS:
                    self._add_rule(rule, self.icmp_ingress_rule)
                else:
                    self._add_rule(rule, self.icmp_egress_rule)

        return rules

    def _add_rule(self, target_rule, rule_dict):
        if rule_dict.has_key(target_rule.allowedCidr):
            current_rule_uuids = []
            for rule in rule_dict[target_rule.allowedCidr]:
                current_rule_uuids.append(rule.uuid)

            if not target_rule.uuid in current_rule_uuids:
                rule_dict[target_rule.allowedCidr].append(target_rule)

        else:
            rule_dict[target_rule.allowedCidr] = [target_rule]

    def delete_rule_by_uuids(self, target_rule_uuids):
        for rule_uuid in target_rule_uuids:
            rule = test_lib.lib_get_sg_rule_by_uuid(rule_uuid)

            if rule.protocol == inventory.TCP:
                if rule.type == inventory.INGRESS:
                    self._delete_rule(rule, self.tcp_ingress_rule)
                else:
                    self._delete_rule(rule, self.tcp_egress_rule)
            elif rule.protocol == inventory.UDP:
                if rule.type == inventory.INGRESS:
                    self._delete_rule(rule, self.udp_ingress_rule)
                else:
                    self._delete_rule(rule, self.udp_egress_rule)
            elif rule.protocol == inventory.ICMP:
                if rule.type == inventory.INGRESS:
                    self._delete_rule(rule, self.icmp_ingress_rule)
                else:
                    self._delete_rule(rule, self.icmp_egress_rule)
        net_ops.remove_rules_from_security_group(target_rule_uuids)

    def delete_rule(self, target_rule_objs):
        target_rule_uuids = test_lib.lib_get_sg_rule_uuid_by_rule_obj(self.security_group.uuid, target_rule_objs)
        self.delete_rule_by_uuids(target_rule_uuids)

    def _delete_rule(self, target_rule, rule_dict):
        if not rule_dict.has_key(target_rule.allowedCidr):
            return

        for rule in rule_dict[target_rule.allowedCidr]:
            if rule.uuid == target_rule.uuid:
                rule_dict[target_rule.allowedCidr].remove(rule)
                break
        if not rule_dict[target_rule.allowedCidr]:
            rule_dict.pop(target_rule.allowedCidr)

    def _add_nic(self, l3_uuid, nic_uuid):
        if self.nic_dict.has_key(l3_uuid):
            if not nic_uuid in self.nic_dict[l3_uuid]:
                self.nic_dict[l3_uuid].append(nic_uuid)
        else:
            self.nic_dict[l3_uuid] = [nic_uuid]

    def _rm_nic(self, nic_uuid):
        for key, value in self.nic_dict.iteritems():
            if nic_uuid in value:
                self.nic_dict[key].remove(nic_uuid)
                if not self.nic_dict[key]:
                    self.nic_dict.pop(key)
                return

    def _rm_l3(self, l3_uuid):
        if self.nic_dict.has_key(l3_uuid):
            self.nic_dict.pop(l3_uuid)

    def get_all_l3(self):
        return self.nic_dict.keys()

    def get_attached_nics_by_l3(self, l3_uuid):
        if self.nic_dict.has_key(l3_uuid):
            return self.nic_dict[l3_uuid]
        else:
            return None

    def get_all_attached_nics(self):
        nics = []
        for l3 in self.get_all_l3():
            nics.extend(self.get_attached_nics_by_l3(l3))
        return nics

    #get all tcp ingress rules' allowedCidr
    def get_tcp_ingress_all_addr(self):
        return self.tcp_ingress_rule.keys()

    def get_tcp_ingress_rule_by_addr(self, allowedCidr):
        return self.tcp_ingress_rule[allowedCidr]

    def get_tcp_ingress_all_rule(self):
        rules= []
        for addr in self.get_tcp_ingress_all_addr():
            rules.extend(self.get_tcp_ingress_rule_by_addr(addr))
        return rules

    #get all tcp egress rules' allowedCidr
    def get_tcp_egress_all_addr(self):
        return self.tcp_egress_rule.keys()

    def get_tcp_egress_rule_by_addr(self, allowedCidr):
        return self.tcp_egress_rule[allowedCidr]

    def get_tcp_egress_all_rule(self):
        rules= []
        for addr in self.get_tcp_egress_all_addr():
            rules.extend(self.get_tcp_egress_rule_by_addr(addr))
        return rules

    #get all udp ingress rules' allowedCidr
    def get_udp_ingress_all_addr(self):
        return self.udp_ingress_rule.keys()

    def get_udp_ingress_rule_by_addr(self, allowedCidr):
        return self.udp_ingress_rule[allowedCidr]

    def get_udp_ingress_all_rule(self):
        rules= []
        for addr in self.get_udp_ingress_all_addr():
            rules.extend(self.get_udp_ingress_rule_by_addr(addr))
        return rules

    #get all udp egress rules' allowedCidr
    def get_udp_egress_all_addr(self):
        return self.udp_egress_rule.keys()

    def get_udp_egress_rule_by_addr(self, allowedCidr):
        return self.udp_egress_rule[allowedCidr]

    def get_udp_egress_all_rule(self):
        rules= []
        for addr in self.get_udp_egress_all_addr():
            rules.extend(self.get_udp_egress_rule_by_addr(addr))
        return rules

    #get all icmp ingress rules' allowedCidr
    def get_icmp_ingress_all_addr(self):
        return self.icmp_ingress_rule.keys()

    def get_icmp_ingress_rule_by_addr(self, allowedCidr):
        return self.icmp_ingress_rule[allowedCidr]

    def get_icmp_ingress_all_rule(self):
        rules= []
        for addr in self.get_icmp_ingress_all_addr():
            rules.extend(self.get_icmp_ingress_rule_by_addr(addr))
        return rules

    #get all icmp egress rules' allowedCidr
    def get_icmp_egress_all_addr(self):
        return self.icmp_egress_rule.keys()

    def get_icmp_egress_rule_by_addr(self, allowedCidr):
        return self.icmp_egress_rule[allowedCidr]

    def get_icmp_egress_all_rule(self):
        rules= []
        for addr in self.get_icmp_egress_all_addr():
            rules.extend(self.get_icmp_egress_rule_by_addr(addr))
        return rules

    def get_all_rules(self):
        return self.get_tcp_egress_all_rule() + self.get_tcp_ingress_all_rule() + self.get_udp_ingress_all_rule() + self.get_udp_egress_all_rule() + self.get_icmp_ingress_all_rule() + self.get_icmp_egress_all_rule()
