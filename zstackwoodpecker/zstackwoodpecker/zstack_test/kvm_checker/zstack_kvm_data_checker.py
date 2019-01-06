import os
import sys
import traceback
import re

import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.header.checker as checker_header
import zstackwoodpecker.header.vm as vm_header
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstacklib.utils.http as http
import zstacklib.utils.jsonobject as jsonobject
import zstacklib.utils.linux as linux
import apibinding.inventory as inventory
import zstacktestagent.plugins.vm as vm_plugin
import zstacktestagent.plugins.host as host_plugin
import zstacktestagent.testagent as testagent
import zstackwoodpecker.header.vm as vm_header
import zstackwoodpecker.header.volume as volume_header
import zstackwoodpecker.header.snapshot as sp_header
import zstackwoodpecker.zstack_test.zstack_test_snapshot as zstack_sp_header

################################################################################
#                         vdbench_file.py output:
#The first time running vdbench in vm:
#disklist:/dev/disk/by-uuid/$disk_uuid:$disk_size
#
#Add and remove volume:
#add:/dev/disk/by-uuid/$disk_uuid:$disk_size
#remove:/dev/disk/by-uuid/$disk_uuid:$disk_size
#
#Resize volume:
#resize:/dev/disk/by-uuid/$disk_uuid:$disk_size
#
#No volume change:
#same disk
#
#Validate:
#validate successfully
#if validate failed:
#validate failed on $disk_path
#if all disk been removed:
#All old disks have been removed,skip validation
#
#run test:
#generate successfully
#if all disk been removed:
#no disk attached, skip generating
#################################################################################
class zstack_kvm_vm_attach_volume_checker(checker_header.TestChecker):
    '''
        Check if volume is really attached to vm inside vm
    '''
    def check(self):
        super(zstack_kvm_vm_attach_volume_checker, self).check()
        volume = self.test_obj.volume
        vm = self.test_obj.target_vm.vm
        
        if vm.state != "Running":
            test_util.test_logger('Check result: Skip attach_volume_checker since VM is not in Running state')
        
        test_lib.lib_install_testagent_to_vr(vm)
        host = test_lib.lib_get_vm_host(vm)
        test_lib.lib_install_testagent_to_host(host)
        test_lib.lib_set_vm_host_l2_ip(vm)
        default_l3_uuid = vm.defaultL3NetworkUuid
        vr = test_lib.lib_find_vr_by_pri_l3(default_l3_uuid)
        nic = test_lib.lib_get_vm_nic_by_vr(vm, vr)

        command = 'python /root/vdbench_file.py dryrun'
        cmd_result = test_lib.lib_ssh_vm_cmd_by_agent_with_retry(host.managementIp, nic.ip, test_lib.lib_get_vm_username(vm), test_lib.lib_get_vm_password(vm), command, self.exp_result)
        test_util.test_logger("czhou: %s" % cmd_result)
        
        if isinstance(cmd_result, str) and cmd_result == "" or "same disk" in cmd_result:
            test_util.test_logger("Checker result: Fail  since there's no volume attached to the vm")
            return self.judge(False)

        #If it's a virtio-scsi volume, check the wwn in the output
        if isinstance(cmd_result, str) and "capability::virtio-scsi" in self.test_obj.volume_creation_option.get_system_tags():
            condition = res_ops.gen_query_conditions("resourceUuid", '=', volume.uuid)
            for i in res_ops.query_resource(res_ops.SYSTEM_TAG, condition):
                if re.split("::",i.tag)[0] == "kvm":
                    wwn = re.split("::",i.tag)[2]

            #For the first time data check, vdbench_file.py will only output disklist:$disk_uuid:$disk_size
            if "disklist" in cmd_result and wwn in cmd_result:
                test_util.test_logger("Checker result: Success to find volume [%s] in vm" % cmd_result)
                return self.judge(True)
            if "disklist" in cmd_result and wwn not in cmd_result:
                test_util.test_logger("Checker result: Fail to find volume [%s] in vm" % cmd_result)
                return self.judge(False)

            if "add:/dev/disk/by-id/"+wwn+":"+str(int(volume.size)/1024/1024/1024)+'G' in cmd_result:
                test_util.test_logger("Checker result: Success to check wwn of attached virtioscsi volume [%s] in vm" % cmd_result)
                return self.judge(True)
            else:
                test_util.test_logger("Checker result: Fail to check wwn of attached virtioscsi volume [%s] in vm " % cmd_result)
                return self.judge(False)

        #If it's a virtio-blk volume, we can only check the volume size and 'add' label in the output
        if isinstance(cmd_result, str) and "capability::virtio-scsi" not in self.test_obj.volume_creation_option.get_system_tags():
            if "disklist" in cmd_result and str(int(volume.size)/1024/1024/1024)+'G' in cmd_result:
                test_util.test_logger("Checker result: Success to attach virtioblk volume [%s] in vm" % cmd_result)
                return self.judge(True)
            if "disklist" in cmd_result and str(int(volume.size)/1024/1024/1024)+'G' not in cmd_result:
                test_util.test_logger("Checker result: Success to attach virtioblk volume [%s] in vm" % cmd_result)
                return self.judge(False)

            if re.split(":",cmd_ressult)[0] == "add" and re.split(":",cmd_ressult)[2] == str(int(volume.size)/1024/1024/1024)+'G':
                test_util.test_logger("Checker result: Success to check virtioblk attached volume [%s] in vm" % cmd_result)
                return self.judge(True)
            else:
                test_util.test_logger("Checker result: Fail to check virtioblk attached volume [%s] in vm" % cmd_result)
                return self.judge(False)
        

class zstack_kvm_vm_detach_volume_checker(checker_header.TestChecker):
    '''
        Check if volume is really detached from vm inside vm
    '''
    def check(self):
        super(zstack_kvm_vm_detach_volume_checker, self).check()
        volume = self.test_obj.volume
        vm = self.test_obj.target_vm.vm

        if vm.state != "Running":
            test_util.test_logger('Check result: Skip attach_volume_checker since VM is not in Running state')

        test_lib.lib_install_testagent_to_vr(vm)
        host = test_lib.lib_get_vm_host(vm)
        test_lib.lib_install_testagent_to_host(host)
        test_lib.lib_set_vm_host_l2_ip(vm)
        default_l3_uuid = vm.defaultL3NetworkUuid
        vr = test_lib.lib_find_vr_by_pri_l3(default_l3_uuid)
        nic = test_lib.lib_get_vm_nic_by_vr(vm, vr)

        command = 'python /root/vdbench_file.py dryrun'
        cmd_result = test_lib.lib_ssh_vm_cmd_by_agent_with_retry(host.managementIp, nic.ip, test_lib.lib_get_vm_username(vm), test_lib.lib_get_vm_password(vm), command, self.exp_result)
        test_util.test_logger("czhou: %s" % cmd_result)

        if isinstance(cmd_result, str) and cmd_result == "" or "same disk" in cmd_result:
            test_util.test_logger("Checker result: Fail  since there's no volume attached to the vm")
            return self.judge(False)

        #If it's a virtio-scsi volume, check the wwn in the output
        if isinstance(cmd_result, str) and "capability::virtio-scsi" in self.test_obj.volume_creation_option.get_system_tags():
            condition = res_ops.gen_query_conditions("resourceUuid", '=', volume.uuid)
            for i in res_ops.query_resource(res_ops.SYSTEM_TAG, condition):
                if re.split("::",i.tag)[0] == "kvm":
                    wwn = re.split("::",i.tag)[2]
            
            #For the first time data check, vdbench_file.py will only output disklist:$disk_uuid:$disk_size 
            if "disklist" in cmd_result and wwn not in cmd_result:
                test_util.test_logger("Checker result: Success to detach virtioscsi volume [%s] in vm" % cmd_result)
                return self.judge(True)
            if "disklist" in cmd_result and wwn in cmd_result:
                test_util.test_logger("Checker result: Fail to detach virtioscsi volume [%s], still find in vm" % cmd_result)
                return self.judge(False)
                
            if "remove:/dev/disk/by-id/"+wwn+":"+str(int(volume.size)/1024/1024/1024)+'G' in cmd_result:
                test_util.test_logger("Checker result: Success to check wwn of detached virtioscsi volume [%s] in vm" % cmd_result)
                return self.judge(True)
            else:
                test_util.test_logger("Checker result: Fail to check wwn of detached virtioscsi volume [%s] in vm " % cmd_result)
                return self.judge(False)

        #If it's a virtio-blk volume, we can only check the volume size and 'remove' label in the output
        if isinstance(cmd_result, str) and "capability::virtio-scsi" not in self.test_obj.volume_creation_option.get_system_tags():
            if "disklist" in cmd_result and str(int(volume.size)/1024/1024/1024)+'G' not in cmd_result:
                test_util.test_logger("Checker result: Success to detach virtioblk volume [%s] in vm" % cmd_result)
                return self.judge(True)
            if "disklist" in cmd_result and str(int(volume.size)/1024/1024/1024)+'G' in cmd_result: 
                test_util.test_logger("Checker result: Success to detach virtioblk volume [%s] in vm" % cmd_result)
                return self.judge(False)

            if re.split(":",cmd_ressult)[0] == "remove" and re.split(":",cmd_ressult)[2] == str(int(volume.size)/1024/1024/1024)+'G':
                test_util.test_logger("Checker result: Success to check virtioblk detached volume [%s] in vm" % cmd_result)
                return self.judge(True)
            else:
                test_util.test_logger("Checker result: Fail to check virtioblk detached volume [%s] in vm" % cmd_result)
                return self.judge(False)



class zstack_kvm_vm_resize_volume_checker(checker_header.TestChecker):
    '''
        Check if volume is properly resized inside vm
    '''
    def check(self):
        super(zstack_kvm_vm_resize_volume_checker, self).check()
        volume = self.test_obj.volume
        vm = self.test_obj.target_vm.vm

        if vm.state != "Running":
            test_util.test_logger('Check result: Skip attach_volume_checker since VM is not in Running state')

        test_lib.lib_install_testagent_to_vr(vm)
        host = test_lib.lib_get_vm_host(vm)
        test_lib.lib_install_testagent_to_host(host)
        test_lib.lib_set_vm_host_l2_ip(vm)
        default_l3_uuid = vm.defaultL3NetworkUuid
        vr = test_lib.lib_find_vr_by_pri_l3(default_l3_uuid)
        nic = test_lib.lib_get_vm_nic_by_vr(vm, vr)

        command = 'python /root/vdbench_file.py dryrun'
        cmd_result = test_lib.lib_ssh_vm_cmd_by_agent_with_retry(host.managementIp, nic.ip, test_lib.lib_get_vm_username(vm), test_lib.lib_get_vm_password(vm), command, self.exp_result)
        test_util.test_logger("czhou: %s" % cmd_result)

        if isinstance(cmd_result, str) and cmd_result == "" or "same disk" in cmd_result:
            test_util.test_logger("Checker result: Fail  since there's no volume attached to the vm")
            return self.judge(False)

        #If it's a virtio-scsi volume, check the wwn in the output
        if isinstance(cmd_result, str) and "capability::virtio-scsi" in self.test_obj.volume_creation_option.get_system_tags():
            condition = res_ops.gen_query_conditions("resourceUuid", '=', volume.uuid)
            for i in res_ops.query_resource(res_ops.SYSTEM_TAG, condition):
                if re.split("::",i.tag)[0] == "kvm":
                    wwn = re.split("::",i.tag)[2]

            #For the first time data check, vdbench_file.py will only output disklist:$disk_uuid:$disk_size
            if "disklist" in cmd_result and wwn in cmd_result:
                test_util.test_logger("Checker result: Success to resize virtioscsi volume [%s] in vm" % cmd_result)
                return self.judge(True)
            if "disklist" in cmd_result and wwn not in cmd_result:
                test_util.test_logger("Checker result: Fail to resize virtioscsi volume [%s], still find in vm" % cmd_result)
                return self.judge(False)

            if "resize:/dev/disk/by-id/"+wwn+":"+str(int(volume.size)/1024/1024/1024)+'G' in cmd_result:
                test_util.test_logger("Checker result: Success to check wwn of resized virtioscsi volume [%s] in vm" % cmd_result)
                return self.judge(True)
            else:
                test_util.test_logger("Checker result: Fail to check wwn of resized virtioscsi volume [%s] in vm " % cmd_result)
                return self.judge(False)

        #If it's a virtio-blk volume, we can only check the volume size and 'remove' label in the output
        if isinstance(cmd_result, str) and "capability::virtio-scsi" not in self.test_obj.volume_creation_option.get_system_tags():
            if "disklist" in cmd_result and str(int(volume.size)/1024/1024/1024)+'G' not in cmd_result:
                test_util.test_logger("Checker result: Success to resize virtioblk volume [%s] in vm" % cmd_result)
                return self.judge(True)
            if "disklist" in cmd_result and str(int(volume.size)/1024/1024/1024)+'G' in cmd_result:
                test_util.test_logger("Checker result: Success to resize virtioblk volume [%s] in vm" % cmd_result)
                return self.judge(False)

            if re.split(":",cmd_ressult)[0] == "resize" and re.split(":",cmd_ressult)[2] == str(int(volume.size)/1024/1024/1024)+'G':
                test_util.test_logger("Checker result: Success to check virtioblk resized volume [%s] in vm" % cmd_result)
                return self.judge(True)
            else:
                test_util.test_logger("Checker result: Fail to check virtioblk resized volume [%s] in vm" % cmd_result)
                return self.judge(False)

class zstack_kvm_vm_data_integrity_checker(checker_header.TestChecker):
    '''
        Check data integrity inside vm using vdbench
    '''
    def check(self):
        super(zstack_kvm_vm_data_integrity_checker, self).check()

        if isinstance(self.test_obj, volume_header.TestVolume):
            volume = self.test_obj.volume
            vm = self.test_obj.target_vm.vm
        if isinstance(self.test_obj, vm_header.TestVm):
            vm = self.test_obj.vm
        if isinstance(self.test_obj, zstack_sp_header.ZstackVolumeSnapshot):
            volume_obj = self.test_obj.get_target_volume()
            vm = volume_obj.get_target_vm()

        if vm.state != "Running":
            test_util.test_logger('Check result: Skip attach_volume_checker since VM is not in Running state')

        test_lib.lib_install_testagent_to_vr(vm)
        host = test_lib.lib_get_vm_host(vm)
        test_lib.lib_install_testagent_to_host(host)
        test_lib.lib_set_vm_host_l2_ip(vm)
        default_l3_uuid = vm.defaultL3NetworkUuid
        vr = test_lib.lib_find_vr_by_pri_l3(default_l3_uuid)
        nic = test_lib.lib_get_vm_nic_by_vr(vm, vr)

        command = 'python /root/vdbench_file.py'
        cmd_result = test_lib.lib_ssh_vm_cmd_by_agent_with_retry(host.managementIp, nic.ip, test_lib.lib_get_vm_username(vm), test_lib.lib_get_vm_password(vm), command, self.exp_result)
        test_util.test_logger("czhou: %s" % cmd_result)

        if isinstance(cmd_result, str) and "All old disks have been removed,skip validation" in cmd_result:
            if "generate successfully" in cmd_result or "skip generating" in cmd_result:
                test_util.test_logger("Checker result: Skip validation checker since all disks have been removed")
                return self.judge(True)
            else:
                test_util.test_logger("Checker result: Skip validation checker since all disks have been removed, but generating data failed on volume output: %s" % cmd_result)
                return self.judge(False)

        if isinstance(cmd_result, str) and "validate successfully" in cmd_result:
            if "generate successfully" in cmd_result or "skip generating" in cmd_result:
                test_util.test_logger("Checker result: Success to validate data integrity, output: %s" % cmd_result)
                return self.judge(True)
            else:
                test_util.test_logger("Checker result: Success to validate data integrity, but generating data failed on volume output: %s" % cmd_result)
                return self.judge(False)
 
        if isinstance(cmd_result, str) and "validate failed on" in cmd_result:
            test_util.test_logger("Checker result: Fail to validate data integrity, output: %s" % cmd_result)
            return self.judge(False)

        if isinstance(cmd_result, str) and "generate successfully" in cmd_result:
            test_util.test_logger("Checker result: Success to validate data integrity, output: %s" % cmd_result)
            return self.judge(True)

        return self.judge(False)
