'''
Zstack KVM Checker Factory.


@author: YYK
'''

import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.header.vm as vm_header
import zstackwoodpecker.header.volume as volume_header
import zstackwoodpecker.header.image as image_header
import zstackwoodpecker.header.security_group as sg_header
import zstackwoodpecker.header.port_forwarding as pf_header
import zstackwoodpecker.header.vip as vip_header
import zstackwoodpecker.header.load_balancer as lb_header
import zstackwoodpecker.header.checker as checker_header
import zstackwoodpecker.zstack_test.zstack_checker.zstack_db_checker as db_checker
import zstackwoodpecker.zstack_test.kvm_checker.zstack_kvm_vm_checker as vm_checker
import zstackwoodpecker.zstack_test.kvm_checker.zstack_kvm_volume_checker as volume_checker
import zstackwoodpecker.zstack_test.kvm_checker.zstack_kvm_share_volume_checker as share_volume_checker
import zstackwoodpecker.zstack_test.kvm_checker.zstack_kvm_image_checker as image_checker
import zstackwoodpecker.zstack_test.kvm_checker.zstack_kvm_security_group_checker as sg_checker
import zstackwoodpecker.zstack_test.kvm_checker.zstack_kvm_port_forwarding_checker as pf_checker
import zstackwoodpecker.zstack_test.kvm_checker.zstack_kvm_host_checker as host_checker
import zstackwoodpecker.zstack_test.kvm_checker.zstack_kvm_eip_checker as eip_checker
import zstackwoodpecker.zstack_test.kvm_checker.zstack_kvm_vip_checker as vip_checker
import zstackwoodpecker.zstack_test.kvm_checker.zstack_kvm_snapshot_checker as sp_checker
import zstackwoodpecker.zstack_test.kvm_checker.zstack_kvm_load_balancer_checker as lb_checker
import zstackwoodpecker.zstack_test.kvm_checker.zstack_kvm_data_checker as data_checker
import zstackwoodpecker.test_util as test_util
import apibinding.inventory as inventory
import collections

class KvmVmCheckerFactory(checker_header.CheckerFactory):
    def create_checker(self, test_obj):
        kvm_vm_checker_chain = checker_header.CheckerChain()
        checker_dict = {}
        checker_dict = collections.OrderedDict()

        if test_obj.state == vm_header.RUNNING:
            checker_dict[vm_checker.zstack_kvm_vm_set_host_vlan_ip] = True
            checker_dict[db_checker.zstack_vm_db_checker] = True
            checker_dict[vm_checker.zstack_kvm_vm_running_checker] = True
            #if behind of VR
            vrs = test_lib.lib_find_vr_by_vm(test_obj.vm)
            if vrs:
                svr_types = test_lib.lib_get_l3s_service_type(test_obj.vm)
                #The first DHCP checker will wait for VM start up.
                if 'DHCP' in svr_types and not test_lib.lib_get_flat_dhcp_by_vm(test_obj.vm):
                    checker_dict[vm_checker.zstack_kvm_vm_dhcp_checker] = True
                    checker_dict[vm_checker.zstack_kvm_vm_network_checker] = True
                    #if guest can't get IP address from DHCP, auto case can
                    # not test DNS feature.
                    if 'DNS' in svr_types:
                        checker_dict[vm_checker.zstack_kvm_vm_dns_checker] \
                                = True
                    else:
                        checker_dict[vm_checker.zstack_kvm_vm_dns_checker] \
                                = False
                elif 'DHCP' in svr_types and test_lib.lib_get_flat_dhcp_by_vm(test_obj.vm) and test_lib.lib_find_vr_by_vm(test_obj.vm):
                    checker_dict[vm_checker.zstack_kvm_vm_dhcp_checker] = False
                    checker_dict[vm_checker.zstack_kvm_vm_network_checker] = True
                else:
                    checker_dict[vm_checker.zstack_kvm_vm_network_checker] \
                            = False
                if 'SNAT' in svr_types and 'DHCP' in svr_types:
                    checker_dict[vm_checker.zstack_kvm_vm_snat_checker] = True
                else:
                    checker_dict[vm_checker.zstack_kvm_vm_snat_checker] = False
                #if 'PortForwarding' in svr_types:
                #    checker_dict[vm_checker.zstack_kvm_vm_dnat_checker] = True
                #else:
                #    checker_dict[vm_checker.zstack_kvm_vm_dnat_checker] = False
            else:
                svr_types = test_lib.lib_get_l3s_service_type(test_obj.vm)
                sp_types = test_lib.lib_get_vm_l3_service_provider_types(test_obj.vm)
                if 'Flat' in sp_types and 'DHCP' in svr_types:
                    checker_dict[vm_checker.zstack_kvm_vm_ssh_no_vr_checker] = True

            if test_obj.get_creation_option().get_default_l3_uuid():
                checker_dict[vm_checker.zstack_kvm_vm_default_l3_checker] = True

            if test_lib.ROBOT:
                checker_dict[data_checker.zstack_kvm_vm_data_integrity_checker] = True
  

        elif test_obj.state == vm_header.STOPPED:
            checker_dict[db_checker.zstack_vm_db_checker] = True
            #stopped_checker is deprecated, since the stopped vm will be removed
            #from host.
            #checker_dict[vm_checker.zstack_kvm_vm_stopped_checker] = True

        elif test_obj.state == vm_header.PAUSED:
            checker_dict[db_checker.zstack_vm_db_checker] = True
            checker_dict[vm_checker.zstack_kvm_vm_suspended_checker] = True

        elif test_obj.state == vm_header.DESTROYED:
            #VM destroy will cause vm structure be removed from DB, when VmExpungeInterval is set to 1, so doesn't need to check destroyed state sync in db in most case.
            checker_dict[db_checker.zstack_vm_db_checker] = True
            checker_dict[vm_checker.zstack_kvm_vm_destroyed_checker] = True
        elif test_obj.state == vm_header.EXPUNGED:
            checker_dict[db_checker.zstack_vm_db_checker] = True

        kvm_vm_checker_chain.add_checker_dict(checker_dict, test_obj)
        return kvm_vm_checker_chain

class KvmVolumeCheckerFactory(checker_header.CheckerFactory):
    def create_checker(self, test_obj):
        kvm_volume_checker_chain = checker_header.CheckerChain()
        checker_dict = {}
        checker_dict = collections.OrderedDict()

        if test_obj.state == volume_header.CREATED:
            checker_dict[db_checker.zstack_volume_db_checker] = True
            checker_dict[volume_checker.zstack_kvm_volume_file_checker] = False

        elif test_obj.state == volume_header.ATTACHED:
            checker_dict[db_checker.zstack_volume_db_checker] = True
            checker_dict[volume_checker.zstack_kvm_volume_file_checker] = True
            if not test_obj.target_vm.state == vm_header.DESTROYED:
                checker_dict[db_checker.zstack_volume_attach_db_checker] = True
                if test_obj.target_vm.state == vm_header.RUNNING:
                    checker_dict[volume_checker.zstack_kvm_volume_attach_checker] = True
                    if test_lib.ROBOT:
                        checker_dict[data_checker.zstack_kvm_vm_attach_volume_checker] = True
            else:
                checker_dict[db_checker.zstack_volume_attach_db_checker] = False

        elif test_obj.state == volume_header.DETACHED:
            checker_dict[db_checker.zstack_volume_db_checker] = True
            checker_dict[db_checker.zstack_volume_attach_db_checker] = False
            checker_dict[volume_checker.zstack_kvm_volume_attach_checker] = False
            checker_dict[volume_checker.zstack_kvm_volume_file_checker] = True
            if test_lib.ROBOT:
                checker_dict[data_checker.zstack_kvm_vm_detach_volume_checker] = True


        elif test_obj.state == volume_header.DELETED:
            checker_dict[db_checker.zstack_volume_db_checker] = True
            checker_dict[volume_checker.zstack_kvm_volume_file_checker] = True

        elif test_obj.state == volume_header.EXPUNGED:
            checker_dict[db_checker.zstack_volume_db_checker] = False
            checker_dict[volume_checker.zstack_kvm_volume_file_checker] = False

        kvm_volume_checker_chain.add_checker_dict(checker_dict, test_obj)
        return kvm_volume_checker_chain

class KvmSharableVolumeCheckerFactory(checker_header.CheckerFactory):
    def create_checker(self, test_obj):
        kvm_volume_checker_chain = checker_header.CheckerChain()
        checker_dict = {}
        checker_dict = collections.OrderedDict()

        if test_obj.state == volume_header.CREATED:
            checker_dict[db_checker.zstack_volume_db_checker] = True
            checker_dict[share_volume_checker.zstack_kvm_share_volume_file_checker] = False

        elif test_obj.state == volume_header.ATTACHED:
            checker_dict[db_checker.zstack_volume_db_checker] = True
            checker_dict[share_volume_checker.zstack_kvm_share_volume_file_checker] = True
            if not test_obj.target_vm.state == vm_header.DESTROYED:
                checker_dict[db_checker.zstack_share_volume_attach_db_checker] = True
                if test_obj.target_vm.state == vm_header.RUNNING:
                    checker_dict[share_volume_checker.zstack_kvm_share_volume_attach_checker] = True
                    checker_dict[share_volume_checker.zstack_kvm_virtioscsi_shareable_checker] = True
            else:
                checker_dict[db_checker.zstack_share_volume_attach_db_checker] = False

        elif test_obj.state == volume_header.DETACHED:
            checker_dict[db_checker.zstack_volume_db_checker] = True
            checker_dict[db_checker.zstack_share_volume_attach_db_checker] = False
            checker_dict[share_volume_checker.zstack_kvm_share_volume_attach_checker] = False
            checker_dict[share_volume_checker.zstack_kvm_share_volume_file_checker] = True

        elif test_obj.state == volume_header.DELETED:
            checker_dict[db_checker.zstack_volume_db_checker] = True
            checker_dict[share_volume_checker.zstack_kvm_share_volume_file_checker] = True

        elif test_obj.state == volume_header.EXPUNGED:
            checker_dict[db_checker.zstack_volume_db_checker] = False
            checker_dict[share_volume_checker.zstack_kvm_share_volume_file_checker] = False

        kvm_volume_checker_chain.add_checker_dict(checker_dict, test_obj)
        return kvm_volume_checker_chain

class KvmImageCheckerFactory(checker_header.CheckerFactory):
    def create_checker(self, test_obj):
        kvm_image_checker_chain = checker_header.CheckerChain()
        checker_dict = {}

        if test_obj.state == image_header.CREATED:
            checker_dict[db_checker.zstack_image_db_checker] = True
            checker_dict[image_checker.zstack_kvm_image_file_checker] = True

        if test_obj.state == image_header.DELETED:
            checker_dict[db_checker.zstack_image_db_checker] = True
            checker_dict[image_checker.zstack_kvm_image_file_checker] = True

        if test_obj.state == image_header.EXPUNGED:
            checker_dict[db_checker.zstack_image_db_checker] = False
            checker_dict[image_checker.zstack_kvm_image_file_checker] = False

        kvm_image_checker_chain.add_checker_dict(checker_dict, test_obj)
        return kvm_image_checker_chain

class KvmSecurityGroupCheckerFactory(checker_header.CheckerFactory):
    def create_checker(self, test_obj):
        kvm_sg_checker_chain = checker_header.CheckerChain()
        checker_dict = {}

        for nic_uuid in test_obj.get_all_nics():
            target_vm = test_obj.get_vm_by_nic(nic_uuid)
            if target_vm.state == vm_header.RUNNING:
                if test_lib.lib_is_vm_sim(target_vm.vm):
                    kvm_sg_checker_chain.add_checker(db_checker.zstack_sg_db_checker(True), test_obj)
                    continue
                if not test_lib.lib_is_vm_kvm(target_vm.vm):
                    continue

                if test_obj.get_nic_tcp_ingress_rules(nic_uuid):
                    checker = sg_checker.zstack_kvm_sg_tcp_ingress_exist_checker()
                    checker.set_nic_uuid(nic_uuid)
                    kvm_sg_checker_chain.add_checker(checker, True, test_obj)

                    checker = sg_checker.zstack_kvm_sg_tcp_ingress_checker()
                    checker.set_nic_uuid(nic_uuid)
                    kvm_sg_checker_chain.add_checker(checker, True, test_obj)

                    checker = sg_checker.zstack_kvm_sg_tcp_internal_vms_checker()
                    checker.set_nic_uuid(nic_uuid)
                    kvm_sg_checker_chain.add_checker(checker, True, test_obj)
                else:
                    checker = sg_checker.zstack_kvm_sg_tcp_ingress_exist_checker()
                    checker.set_nic_uuid(nic_uuid)
                    kvm_sg_checker_chain.add_checker(checker, False, test_obj)

                if test_obj.get_nic_tcp_egress_rules(nic_uuid):
                    checker = sg_checker.zstack_kvm_sg_tcp_egress_exist_checker()
                    checker.set_nic_uuid(nic_uuid)
                    kvm_sg_checker_chain.add_checker(checker, True, test_obj)

                    checker = sg_checker.zstack_kvm_sg_tcp_egress_checker()
                    checker.set_nic_uuid(nic_uuid)
                    kvm_sg_checker_chain.add_checker(checker, True, test_obj)

                    if not test_obj.get_nic_tcp_ingress_rules(nic_uuid):
                        checker = sg_checker.zstack_kvm_sg_tcp_internal_vms_checker()
                        checker.set_nic_uuid(nic_uuid)
                        kvm_sg_checker_chain.add_checker(checker, True, test_obj)
                else:
                    checker = sg_checker.zstack_kvm_sg_tcp_egress_exist_checker()
                    checker.set_nic_uuid(nic_uuid)
                    kvm_sg_checker_chain.add_checker(checker, False, test_obj)

                if test_obj.get_nic_udp_ingress_rules(nic_uuid):
                    checker = sg_checker.zstack_kvm_sg_udp_ingress_checker()
                    checker.set_nic_uuid(nic_uuid)
                    kvm_sg_checker_chain.add_checker(checker, True, test_obj)
                else:
                    checker = sg_checker.zstack_kvm_sg_udp_ingress_checker()
                    checker.set_nic_uuid(nic_uuid)
                    kvm_sg_checker_chain.add_checker(checker, False, test_obj)

                if test_obj.get_nic_udp_egress_rules(nic_uuid):
                    checker = sg_checker.zstack_kvm_sg_udp_egress_checker()
                    checker.set_nic_uuid(nic_uuid)
                    kvm_sg_checker_chain.add_checker(checker, True, test_obj)
                else:
                    checker = sg_checker.zstack_kvm_sg_udp_egress_checker()
                    checker.set_nic_uuid(nic_uuid)
                    kvm_sg_checker_chain.add_checker(checker, False, test_obj)

                if test_obj.get_nic_icmp_ingress_rules(nic_uuid):
                    checker = sg_checker.zstack_kvm_sg_icmp_ingress_exist_checker()
                    checker.set_nic_uuid(nic_uuid)
                    kvm_sg_checker_chain.add_checker(checker, True, test_obj)

                    checker = sg_checker.zstack_kvm_sg_icmp_ingress_checker()
                    checker.set_nic_uuid(nic_uuid)
                    kvm_sg_checker_chain.add_checker(checker, True, test_obj)

                    checker = sg_checker.zstack_kvm_sg_icmp_internal_vms_checker()
                    checker.set_nic_uuid(nic_uuid)
                    kvm_sg_checker_chain.add_checker(checker, True, test_obj)
                else:
                    checker = sg_checker.zstack_kvm_sg_icmp_ingress_exist_checker()
                    checker.set_nic_uuid(nic_uuid)
                    kvm_sg_checker_chain.add_checker(checker, False, test_obj)

                if test_obj.get_nic_icmp_egress_rules(nic_uuid):
                    checker = sg_checker.zstack_kvm_sg_icmp_egress_exist_checker()
                    checker.set_nic_uuid(nic_uuid)
                    kvm_sg_checker_chain.add_checker(checker, True, test_obj)

                    checker = sg_checker.zstack_kvm_sg_icmp_egress_checker()
                    checker.set_nic_uuid(nic_uuid)
                    kvm_sg_checker_chain.add_checker(checker, True, test_obj)

                    #if not test_obj.get_nic_icmp_ingress_rules(nic_uuid):
                    #    checker = sg_checker.zstack_kvm_sg_icmp_internal_vms_checker()
                    #    checker.set_nic_uuid(nic_uuid)
                    #    kvm_sg_checker_chain.add_checker(checker, True, test_obj)

                else:
                    checker = sg_checker.zstack_kvm_sg_icmp_egress_exist_checker()
                    checker.set_nic_uuid(nic_uuid)
                    kvm_sg_checker_chain.add_checker(checker, False, test_obj)

            else:
                #TODO: only do iptables rules check
                checker = sg_checker.zstack_kvm_sg_tcp_ingress_exist_checker()
                checker.set_nic_uuid(nic_uuid)
                kvm_sg_checker_chain.add_checker(checker, False, test_obj)

                checker = sg_checker.zstack_kvm_sg_tcp_egress_exist_checker()
                checker.set_nic_uuid(nic_uuid)
                kvm_sg_checker_chain.add_checker(checker, False, test_obj)

                checker = sg_checker.zstack_kvm_sg_icmp_egress_exist_checker()
                checker.set_nic_uuid(nic_uuid)
                kvm_sg_checker_chain.add_checker(checker, False, test_obj)

                checker = sg_checker.zstack_kvm_sg_icmp_ingress_exist_checker()
                checker.set_nic_uuid(nic_uuid)
                kvm_sg_checker_chain.add_checker(checker, False, test_obj)

                checker = sg_checker.zstack_kvm_sg_udp_ingress_checker()
                checker.set_nic_uuid(nic_uuid)
                kvm_sg_checker_chain.add_checker(checker, False, test_obj)

                checker = sg_checker.zstack_kvm_sg_udp_egress_checker()
                checker.set_nic_uuid(nic_uuid)
                kvm_sg_checker_chain.add_checker(checker, False, test_obj)

        for test_vm in test_obj.get_detached_vm():
            vm = test_vm.vm
            if not test_lib.lib_is_vm_kvm(vm):
                continue
            checker = sg_checker.zstack_kvm_sg_tcp_ingress_exist_checker()
            checker.set_vm(vm)
            kvm_sg_checker_chain.add_checker(checker, False, test_obj)

            checker = sg_checker.zstack_kvm_sg_tcp_egress_exist_checker()
            checker.set_vm(vm)
            kvm_sg_checker_chain.add_checker(checker, False, test_obj)

            checker = sg_checker.zstack_kvm_sg_icmp_egress_exist_checker()
            checker.set_vm(vm)
            kvm_sg_checker_chain.add_checker(checker, False, test_obj)

            checker = sg_checker.zstack_kvm_sg_icmp_ingress_exist_checker()
            checker.set_vm(vm)
            kvm_sg_checker_chain.add_checker(checker, False, test_obj)

            checker = sg_checker.zstack_kvm_sg_udp_ingress_checker()
            checker.set_vm(vm)
            kvm_sg_checker_chain.add_checker(checker, False, test_obj)

            checker = sg_checker.zstack_kvm_sg_udp_egress_checker()
            checker.set_vm(vm)
            kvm_sg_checker_chain.add_checker(checker, False, test_obj)

        return kvm_sg_checker_chain

class KvmPortForwardingCheckerFactory(checker_header.CheckerFactory):
    def create_checker(self, test_obj):
        kvm_pf_checker_chain = checker_header.CheckerChain()
        checker_dict = {}
        pf_rule = test_obj.get_port_forwarding()
        if test_obj.get_state() == pf_header.ATTACHED and \
                test_obj.get_target_vm().get_state() == vm_header.RUNNING:
            if pf_rule.protocolType == inventory.TCP:
                checker_dict[pf_checker.zstack_kvm_pf_tcp_checker] = True
            if pf_rule.protocolType == inventory.UDP:
                checker_dict[pf_checker.zstack_kvm_pf_rule_exist_checker] = True

        elif test_obj.get_state() == pf_header.ATTACHED and test_obj.get_target_vm().get_state() == vm_header.STOPPED:
            checker_dict[pf_checker.zstack_kvm_pf_vip_icmp_checker] = False
            if pf_rule.protocolType == inventory.TCP:
                checker_dict[pf_checker.zstack_kvm_pf_tcp_checker] = False

        elif test_obj.get_state() == pf_header.DETACHED:
            checker_dict[pf_checker.zstack_kvm_pf_vip_icmp_checker] = False

        kvm_pf_checker_chain.add_checker_dict(checker_dict, test_obj)
        return kvm_pf_checker_chain

class HostCheckerFactory(checker_header.CheckerFactory):
    def create_checker(self, test_obj):
        host_checker_chain = checker_header.CheckerChain()
        checker = host_checker.zstack_kvm_host_checker()
        host_checker_chain.add_checker(checker, True, test_obj)
        return host_checker_chain

class EipCheckerFactory(checker_header.CheckerFactory):
    def create_checker(self, test_obj):
        eip_checker_chain = checker_header.CheckerChain()
        checker = eip_checker.eip_checker()
        eip_checker_chain.add_checker(checker, True, test_obj)
        return eip_checker_chain

class VipCheckerFactory(checker_header.CheckerFactory):
    def create_checker(self, test_obj):
        vip_checker_chain = checker_header.CheckerChain()
        if test_obj.get_state() == vip_header.ATTACHED:
            if vip_header.PortForwarding in test_obj.get_use_for():
                checker = vip_checker.vip_used_for_checker()
                checker.set_target_use_for(vip_header.PortForwarding)
                vip_checker_chain.add_checker(checker, True, test_obj)
                vip_checker_chain.add_checker(vip_checker.pf_checker(), True, test_obj)
                for pf in test_obj.get_pf_list_for_running_vm():
                    vip_checker_chain.add_checker(pf_checker.zstack_kvm_pf_rule_exist_checker(), True, pf)
                for pf in test_obj.get_pf_list_for_stopped_vm():
                    #vip_checker_chain.add_checker(pf_checker.zstack_kvm_pf_rule_exist_checker(), True, pf)
                    pass

            elif vip_header.Eip in test_obj.get_use_for():
                checker = vip_checker.vip_used_for_checker()
                checker.set_target_use_for(vip_header.Eip)
                vip_checker_chain.add_checker(checker, True, test_obj)
                vip_checker_chain.add_checker(vip_checker.eip_checker(), True, test_obj)
          
            elif vip_header.LoadBalancer in test_obj.get_use_for():
                checker = vip_checker.vip_used_for_checker()
                checker.set_target_use_for(vip_header.LoadBalancer)
                vip_checker_chain.add_checker(checker, True, test_obj)

        elif test_obj.get_state() == vip_header.DETACHED:
            vip_checker_chain.add_checker(vip_checker.vip_icmp_checker(), False, test_obj)
        elif test_obj.get_state() == vip_header.CREATED:
            vip_checker_chain.add_checker(vip_checker.vip_icmp_checker(), False, test_obj)
        elif test_obj.get_state() == vip_header.DELETED:
            vip_checker_chain.add_checker(vip_checker.vip_icmp_checker(), False, test_obj)

        return vip_checker_chain

class SnapshotCheckerFactory(checker_header.CheckerFactory):
    def create_checker(self, test_obj):
        sp_checker_chain = checker_header.CheckerChain()
        if test_obj.get_target_volume().get_volume():
            #target volume is not deleted.
            sp_checker_chain.add_checker(\
                    sp_checker.zstack_kvm_snapshot_checker(), True, test_obj)
            ps_uuid = test_obj.get_target_volume().get_volume().primaryStorageUuid
            if test_lib.lib_is_ps_iscsi_backend(ps_uuid):
                sp_checker_chain.add_checker(\
                        sp_checker.zstack_kvm_snapshot_tree_checker(), True, \
                        test_obj)
        if test_obj.get_backuped_snapshots():
            sp_checker_chain.add_checker(\
                    sp_checker.zstack_kvm_backuped_snapshot_checker(), \
                    True, test_obj)
        return sp_checker_chain

class LoadBalancerCheckerFactory(checker_header.CheckerFactory):
    def create_checker(self, test_obj):
        lb_checker_chain = checker_header.CheckerChain()
        if test_obj.get_state() != lb_header.DELETED:
            lb_checker_chain.add_checker(db_checker.zstack_lb_db_checker(), \
                    True, test_obj)
            for lbl in test_obj.get_load_balancer_listeners().values():
                if lbl.get_state() != lb_header.DELETED:
                    checker = lb_checker.zstack_kvm_lbl_checker()
                    checker.set_lbl(lbl)
                    lb_checker_chain.add_checker(checker, True, test_obj)

            if test_obj.get_load_balancer_listeners():
                if test_obj.is_separated_vr():
                    lb_checker_chain.add_checker(\
                            db_checker.zstack_alone_lb_vr_db_checker(),\
                            True, test_obj)
                else:
                    lb_checker_chain.add_checker(\
                            db_checker.zstack_alone_lb_vr_db_checker(),\
                            False, test_obj)
        else:
            lb_checker_chain.add_checker(db_checker.zstack_lb_db_checker(), \
                    False, test_obj)

        return lb_checker_chain
