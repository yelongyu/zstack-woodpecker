import os
import sys
import traceback
import re
import time

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
            return self.judge(True)
        
        test_lib.lib_install_testagent_to_vr(vm)
        host = test_lib.lib_get_vm_host(vm)
        test_lib.lib_install_testagent_to_host(host)
        test_lib.lib_set_vm_host_l2_ip(vm)
        default_l3_uuid = vm.defaultL3NetworkUuid
        vr = test_lib.lib_find_vr_by_pri_l3(default_l3_uuid)
        nic = test_lib.lib_get_vm_nic_by_vr(vm, vr)

        command = 'cat /root/result'
        cmd_result = test_lib.lib_ssh_vm_cmd_by_agent_with_retry(host.managementIp, nic.ip, test_lib.lib_get_vm_username(vm), test_lib.lib_get_vm_password(vm), command, self.exp_result)
        test_util.test_logger("czhou: %s" % cmd_result)
        
        #If it's a virtio-scsi volume, check the wwn in the output
        conditions = res_ops.gen_query_conditions('tag', '=', 'capability::virtio-scsi')
        conditions = res_ops.gen_query_conditions('resourceUuid', '=', volume.uuid, conditions)
        systemtag = res_ops.query_resource(res_ops.SYSTEM_TAG, conditions)
        size = str(int(volume.size)/1024/1024)+'M' if int(volume.size)/1024/1024 < 1024 else str(int(volume.size)/1024/1024/1024)+'G'
        if isinstance(cmd_result, str) and systemtag:
            condition = res_ops.gen_query_conditions("resourceUuid", '=', volume.uuid)
            for i in res_ops.query_resource(res_ops.SYSTEM_TAG, condition):
                if re.split("::",i.tag)[0] == "kvm":
                    wwn = re.split("::",i.tag)[2]

            for output in cmd_result.splitlines():
                if "old disks:/dev/disk/by-id/wwn-"+wwn+"-part1:"+size in output:
                    disk_md5 = re.split(":",output)[3]
                    vol_md5 = self.test_obj.get_md5sum()
                    if disk_md5 == vol_md5:
                        test_util.test_logger("Checker result: Success to check md5sum of attached virtioscsi volume [%s] in vm " % wwn)
                        continue
                    else:
                        test_util.test_logger("Checker result: Fail to check md5sum of attached virtioscsi volume [%s] in vm " % wwn)
                        return self.judge(False)
                    
                if "new disks:/dev/disk/by-id/wwn-"+wwn+"-part1:"+size in output:
                    disk_md5 = re.split(":",output)[3]
                    self.test_obj.set_md5sum(disk_md5)
                    return self.judge(True)

            test_util.test_logger("Checker result: Fail to check wwn of attached virtioscsi volume [%s] in vm" % wwn)
            return self.judge(False)

        #If it's a virtio-blk volume, we can only check the volume size and 'add' label in the output
        if not systemtag:
            #Skip virtio-blk check until we have a proper solution
            test_util.test_logger("Checker result: Skip to check wwn of attached virtioblk volume [%s] in vm " % cmd_result)
            return self.judge(False)

            if re.split(":",cmd_result)[0] == "add" and re.split(":",cmd_result)[2] == size:
                test_util.test_logger("Checker result: Success to check virtioblk attached volume [%s] in vm" % cmd_result)
                return self.judge(True)
            if "present disks" in cmd_result and size in cmd_result:
                test_util.test_logger("Checker result: Success to attach virtioblk volume [%s] in vm" % cmd_result)
                return self.judge(True)
            if "present disks" in cmd_result and size not in cmd_result:
                test_util.test_logger("Checker result: Success to attach virtioblk volume [%s] in vm" % cmd_result)
                return self.judge(False)


            test_util.test_logger("Checker result: Fail to check virtioblk attached volume [%s] in vm" % cmd_result)
            return self.judge(False)
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
            return self.judge(True)

        test_lib.lib_install_testagent_to_vr(vm)
        host = test_lib.lib_get_vm_host(vm)
        test_lib.lib_install_testagent_to_host(host)
        test_lib.lib_set_vm_host_l2_ip(vm)
        default_l3_uuid = vm.defaultL3NetworkUuid
        vr = test_lib.lib_find_vr_by_pri_l3(default_l3_uuid)
        nic = test_lib.lib_get_vm_nic_by_vr(vm, vr)

        command = 'cat /root/result'
        cmd_result = test_lib.lib_ssh_vm_cmd_by_agent_with_retry(host.managementIp, nic.ip, test_lib.lib_get_vm_username(vm), test_lib.lib_get_vm_password(vm), command, self.exp_result)
        test_util.test_logger("czhou: %s" % cmd_result)

        conditions = res_ops.gen_query_conditions('tag', '=', 'capability::virtio-scsi')
        conditions = res_ops.gen_query_conditions('resourceUuid', '=', volume.uuid, conditions)
        systemtag = res_ops.query_resource(res_ops.SYSTEM_TAG, conditions)
        size = str(int(volume.size)/1024/1024)+'M' if int(volume.size)/1024/1024 < 1024 else str(int(volume.size)/1024/1024/1024)+'G'

        #If it's a virtio-scsi volume, check the wwn in the output
        if isinstance(cmd_result, str) and systemtag:
            condition = res_ops.gen_query_conditions("resourceUuid", '=', volume.uuid)
            for i in res_ops.query_resource(res_ops.SYSTEM_TAG, condition):
                if re.split("::",i.tag)[0] == "kvm":
                    wwn = re.split("::",i.tag)[2]

            if "old disks:/dev/disk/by-id/wwn-"+wwn+"-part1:"+size not in cmd_result and "new disks:/dev/disk/by-id/wwn-"+wwn+"-part1:"+size not in cmd_result:
                test_util.test_logger("Checker result: Success to check wwn of detached virtioscsi volume [%s] in vm " % wwn)
                return self.judge(True)

            test_util.test_logger("Checker result: Fail to check wwn of detached virtioscsi volume [%s] in vm" % wwn)

            return self.judge(False)

        #If it's a virtio-blk volume, we can only check the volume size and 'remove' label in the output
        if isinstance(cmd_result, str) and not systemtag:
            #Skip virtio-blk check until we have a proper solution
            test_util.test_logger("Checker result: Skip to check wwn of detached virtioblk volume [%s] in vm " % cmd_result)
            return self.judge(False)

            if re.split(":",cmd_result)[0] == "remove" and re.split(":",cmd_result)[2] == size:
                test_util.test_logger("Checker result: Success to check virtioblk detached volume [%s] in vm" % cmd_result)
                return self.judge(True)
            if "present disks" in cmd_result and size not in cmd_result:
                test_util.test_logger("Checker result: Success to detach virtioblk volume [%s] in vm" % cmd_result)
                return self.judge(True)
            if "present disks" in cmd_result and size in cmd_result: 
                test_util.test_logger("Checker result: Failed to detach virtioblk volume [%s] in vm" % cmd_result)
                return self.judge(False)

            test_util.test_logger("Checker result: Fail to check virtioblk detached volume [%s] in vm" % cmd_result)
            return self.judge(False)
  
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
            return self.judge(True)
     
        time.sleep(30)

        test_lib.lib_install_testagent_to_vr(vm)
        host = test_lib.lib_get_vm_host(vm)
        test_lib.lib_install_testagent_to_host(host)
        test_lib.lib_set_vm_host_l2_ip(vm)
        default_l3_uuid = vm.defaultL3NetworkUuid
        vr = test_lib.lib_find_vr_by_pri_l3(default_l3_uuid)
        nic = test_lib.lib_get_vm_nic_by_vr(vm, vr)
        
        #print partition information
        cmd = 'ls -l /dev/disk/by-id/'
        cmd_res = test_lib.lib_ssh_vm_cmd_by_agent_with_retry(host.managementIp, nic.ip, test_lib.lib_get_vm_username(vm), test_lib.lib_get_vm_password(vm), cmd, self.exp_result)
        test_util.test_logger("partition information: %s" % cmd_res)
        #exec vdbench
        command = 'python /root/vdbench_test.py | tee result'
        cmd_result = test_lib.lib_ssh_vm_cmd_by_agent_with_retry(host.managementIp, nic.ip, test_lib.lib_get_vm_username(vm), test_lib.lib_get_vm_password(vm), command, self.exp_result)
        test_util.test_logger("czhou: %s" % cmd_result)

        if isinstance(cmd_result, str) and "generate successfully" in cmd_result:
            test_util.test_logger("Checker result: Success to validate data integrity, output: %s" % cmd_result)
            return self.judge(True)
      
        if isinstance(cmd_result, str) and "no disk attached, skip generating" in cmd_result:
            test_util.test_logger("Checker result: No validationg and no generating, output: %s" % cmd_result)
            return self.judge(True)

        #if isinstance(cmd_result, str) and "All old disks have been removed,skip validation" in cmd_result:
        #    if "generate successfully" in cmd_result or "skip generating" in cmd_result:
        #        test_util.test_logger("Checker result: Skip validation checker since all disks have been removed")
        #        return self.judge(True)
        #    else:
        #        test_util.test_logger("Checker result: Skip validation checker since all disks have been removed, but generating data failed on volume output: %s" % cmd_result)
        #        return self.judge(False)

        #if isinstance(cmd_result, str) and "validate successfully" in cmd_result:
        #    if "generate successfully" in cmd_result or "skip generating" in cmd_result:
        #        test_util.test_logger("Checker result: Success to validate data integrity, output: %s" % cmd_result)
        #        return self.judge(True)
        #    else:
        #        test_util.test_logger("Checker result: Success to validate data integrity, but generating data failed on volume output: %s" % cmd_result)
        #        return self.judge(False)
 
        #if isinstance(cmd_result, str) and "validate failed on" in cmd_result:
        #    test_util.test_logger("Checker result: Fail to validate data integrity, output: %s" % cmd_result)
        #    return self.judge(False)


        return self.judge(False)
