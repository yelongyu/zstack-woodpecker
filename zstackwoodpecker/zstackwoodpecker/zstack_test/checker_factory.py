'''
Zstack Checker Factory.


@author: YYK
'''
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_util as test_util

import zstackwoodpecker.header.checker as checker
import zstackwoodpecker.header.vm as vm_header
import zstackwoodpecker.header.volume as volume_header
import zstackwoodpecker.header.eip as eip_header
import zstackwoodpecker.header.image as image_header
import zstackwoodpecker.header.host as host_header
import zstackwoodpecker.header.vip as vip_header
import zstackwoodpecker.header.security_group as sg_header
import zstackwoodpecker.header.port_forwarding as test_pf_header
import zstackwoodpecker.header.snapshot as sp_header
import zstackwoodpecker.header.load_balancer as lb_header
import zstackwoodpecker.header.vid as vid_header
import zstackwoodpecker.zstack_test.kvm_checker.kvm_checker_factory as kvm_checker
import zstackwoodpecker.zstack_test.sim_checker.sim_checker_factory as sim_checker
import zstackwoodpecker.zstack_test.vcenter_checker.vcenter_checker_factory as vcenter_checker
import zstackwoodpecker.zstack_test.zstack_checker.zstack_checker_factory as zstack_checker
import zstackwoodpecker.zstack_test.vid_checker.vid_checker_factory as vid_checker
import zstackwoodpecker.zstack_test.zstack_test_node as zstack_test_node

class CheckerFactory(checker.CheckerFactory):
    def create_checker(self, test_obj):
        import zstackwoodpecker.zstack_test.zstack_test_snapshot as \
                zstack_sp_header

        if isinstance(test_obj, vm_header.TestVm):
            checker_chain = VmCheckerFactory().create_checker(test_obj)
            obj_uuid = test_obj.get_vm().uuid

        elif isinstance(test_obj, volume_header.TestVolume):
            checker_chain = VolumeCheckerFactory().create_checker(test_obj)
            obj_uuid = test_obj.get_volume().uuid
            
        elif isinstance(test_obj, image_header.TestImage):
            checker_chain = ImageCheckerFactory().create_checker(test_obj)
        #elif isinstance(test_obj, sg_header.TestSecurityGroup):
        #    checker_chain = SecurityGroupCheckerFactory().create_checker(test_obj)
            obj_uuid = test_obj.get_image().uuid
            
        elif isinstance(test_obj, sg_header.TestSecurityGroupVm):
            checker_chain = SecurityGroupCheckerFactory().create_checker(test_obj)
            obj_uuid = 'security group vm'
            
        elif isinstance(test_obj, test_pf_header.TestPortForwarding):
            checker_chain = PortForwardingCheckerFactory().create_checker(test_obj)
            obj_uuid = test_obj.get_port_forwarding().uuid
            
        elif isinstance(test_obj, zstack_test_node.ZstackTestNode):
            checker_chain = NodeCheckerFactory().create_checker(test_obj)
            obj_uuid = test_obj.get_test_node().uuid

        elif isinstance(test_obj, host_header.TestHost):
            checker_chain = HostCheckerFactory().create_checker(test_obj)
            obj_uuid = test_obj.get_host().uuid

        elif isinstance(test_obj, eip_header.TestEIP):
            checker_chain = EipCheckerFactory().create_checker(test_obj)
            obj_uuid = test_obj.get_eip().uuid

        elif isinstance(test_obj, vip_header.TestVip):
            checker_chain = VipCheckerFactory().create_checker(test_obj)
            obj_uuid = test_obj.get_vip().uuid

        elif isinstance(test_obj, sp_header.TestSnapshot):
            checker_chain = SnapshotCheckerFactory().create_checker(test_obj)
            obj_uuid = test_obj.get_snapshot().uuid

        elif isinstance(test_obj, zstack_sp_header.ZstackVolumeSnapshot):
            checker_chain = SnapshotCheckerFactory().create_checker(test_obj)
            volume_obj = test_obj.get_target_volume().get_volume()
            if not volume_obj:
                #volume is deleted, but volume snapshot has been backuped.
                obj_uuid = None
            else:
                obj_uuid = volume_obj.uuid

        elif isinstance(test_obj, lb_header.TestLoadBalancer):
            checker_chain = LoadBalancerCheckerFactory().create_checker(test_obj)
            obj_uuid = test_obj.get_load_balancer().uuid

        elif isinstance(test_obj, vid_header.TestVid):
            checker_chain = VidCheckerFactory().create_checker(test_obj)
            virtual_id_obj = test_obj.get_vid()
            obj_uuid = virtual_id_obj.uuid

        test_util.test_logger('Add checker for [%s:] %s. Checkers are: %s' % \
                (test_obj.__class__.__name__, obj_uuid, checker_chain))
        return checker_chain

class VmCheckerFactory(checker.CheckerFactory):
    def create_checker(self, test_obj):
        if not test_obj.vm:
            test_util.test_fail('test_obj.vm is None, can not create checker')

        if test_lib.lib_is_vm_kvm(test_obj.vm):
            return kvm_checker.KvmVmCheckerFactory().create_checker(test_obj)

        if test_lib.lib_is_vm_sim(test_obj.vm):
            return sim_checker.SimVmCheckerFactory().create_checker(test_obj)

        if test_lib.lib_is_vm_vcenter(test_obj.vm):
            return vcenter_checker.VCenterVmCheckerFactory().create_checker(test_obj)

        test_util.test_logger('Did not find checker for Hypervisor type: %s' % test_lib.lib_get_hv_type_of_vm(test_obj.vm))

class VolumeCheckerFactory(checker.CheckerFactory):
    def create_checker(self, test_obj):
        if not test_obj.volume:
            test_util.test_fail('test_obj.volume is None, can not create checker')

        if not test_obj.target_vm:
            #only check db. 
            return sim_checker.SimVolumeCheckerFactory().create_checker(test_obj)
        else:
            if test_lib.lib_is_sharable_volume(test_obj.volume):
                return kvm_checker.KvmSharableVolumeCheckerFactory().create_checker(test_obj)
            if test_lib.lib_is_vm_kvm(test_obj.target_vm.vm):
                return kvm_checker.KvmVolumeCheckerFactory().create_checker(test_obj)
            if test_lib.lib_is_vm_sim(test_obj.target_vm.vm):
                return sim_checker.SimVolumeCheckerFactory().create_checker(test_obj)
            if test_lib.lib_is_vm_vcenter(test_obj.target_vm.vm):
                return vcenter_checker.VCenterVolumeCheckerFactory().create_checker(test_obj)

            test_util.test_logger('Did not find checker for Hypervisor type: %s' % test_lib.lib_get_hv_type_of_vm(test_obj.target_vm.vm))

class ImageCheckerFactory(checker.CheckerFactory):
    def create_checker(self, test_obj):
        if not test_obj.image:
            test_util.test_fail('test_obj.image is None, can not create checker')
        if test_lib.lib_is_image_kvm(test_obj.image):
            return kvm_checker.KvmImageCheckerFactory().create_checker(test_obj)
        if test_lib.lib_is_image_sim(test_obj.image):
            return sim_checker.SimImageCheckerFactory().create_checker(test_obj)
        if test_lib.lib_is_image_vcenter(test_obj.image):
            return vcenter_checker.VCenterImageCheckerFactory().create_checker(test_obj)

        test_util.test_fail('Did not find checker for Hypervisor type: %s' % test_lib.lib_get_hv_type_of_image(test_obj.image))

class SecurityGroupCheckerFactory(checker.CheckerFactory):
    def create_checker(self, test_obj):
        return kvm_checker.KvmSecurityGroupCheckerFactory().create_checker(test_obj)

class PortForwardingCheckerFactory(checker.CheckerFactory):
    def create_checker(self, test_obj):
        return kvm_checker.KvmPortForwardingCheckerFactory().create_checker(test_obj)

class NodeCheckerFactory(checker.CheckerFactory):
    def create_checker(self, test_obj):
        return zstack_checker.NodeCheckerFactory().create_checker(test_obj)

class HostCheckerFactory(checker.CheckerFactory):
    def create_checker(self, test_obj):
        return kvm_checker.HostCheckerFactory().create_checker(test_obj)

class EipCheckerFactory(checker.CheckerFactory):
    def create_checker(self, test_obj):
        return kvm_checker.EipCheckerFactory().create_checker(test_obj)

class VipCheckerFactory(checker.CheckerFactory):
    def create_checker(self, test_obj):
        if not test_obj.isVcenter:
	    return kvm_checker.VipCheckerFactory().create_checker(test_obj)
        return vcenter_checker.VipCheckerFactory().create_checker(test_obj)

class SnapshotCheckerFactory(checker.CheckerFactory):
    def create_checker(self, test_obj):
        return kvm_checker.SnapshotCheckerFactory().create_checker(test_obj)

class LoadBalancerCheckerFactory(checker.CheckerFactory):
    def create_checker(self, test_obj):
        if not test_obj.isVcenter:
	    return kvm_checker.LoadBalancerCheckerFactory().create_checker(test_obj)
        return vcenter_checker.LoadBalancerCheckerFactory().create_checker(test_obj)

class VidCheckerFactory(checker.CheckerFactory):
    def create_checker(self, test_obj):
        return vid_checker.VidAttrCheckerFactory().create_checker(test_obj)

