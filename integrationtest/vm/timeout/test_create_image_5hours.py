'''
New Integration Test for creating image timeout at 5 hours.
We set VM network limitation, which will lead create image
cost 4.5 hours.

@author: SyZhao
'''

import os
import time
import commands
#import sys

import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.backupstorage_operations as bs_ops
import zstackwoodpecker.operations.image_operations as img_ops

_config_ = {
        'timeout' : 18000,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

#6*1024*1024*1024=t*125Bps*bw; if 125Bps*bw=50MBps, bw=419430, t=123s; if t=4.5*3600, bw=3182
vm_outbound_bandwidth = 3182
timeout_value = 16200 #(=4.5*3600)s
image_uuid = None


def set_global_timeout_value():
    """
    """
    retVal, properties_file = commands.getstatusoutput('zstack-ctl status|grep properties|cut -d: -f2')
    if retVal != 0:
        test_util.test_fail("get properties file failure")

    cmd = "sed '/ApiTimeout.org.zstack.header.image.APIAddImageMsg = timeout::/'d -i " + properties_file
    retVal = os.system(cmd)
    if retVal != 0:
        test_util.test_fail("remove add image timeout line")

    cmd = "echo 'ApiTimeout.org.zstack.header.image.APIAddImageMsg = timeout::" + str(timeout_value) + "s' >>" + properties_file
    retVal = os.system(cmd)
    if retVal != 0:
        test_util.test_fail("modify add image timeout value failure")

    retVal = os.system("zstack-ctl stop && zstack-ctl start")
    if retVal != 0:
        test_util.test_fail("zstack-ctl restart")



def test():
    """
    """
    global image_uuid
    

    test_util.test_dsc('create image check timeout test')


    #modify default timeout value
    set_global_timeout_value()


    #create sftp server vm
    sftp_vm_offering = test_lib.lib_create_instance_offering(cpuNum = 1, \
            cpuSpeed = 16, memorySize = 536870912, name = 'sftp_vm_instance_name', \
            volume_iops = None, volume_bandwidth = None, \
            net_outbound_bandwidth = vm_outbound_bandwidth, net_inbound_bandwidth = None)
    test_obj_dict.add_instance_offering(sftp_vm_offering)

    sftp_server_vm = test_stub.create_vm(vm_name = 'sftp-vm', image_name = 'img5h', \
            instance_offering_uuid = sftp_vm_offering.uuid)
    test_obj_dict.add_vm(sftp_server_vm)

    sftp_server_vm.check()


    #create backup storage on previous vm
    sftp_backup_storage_option = test_util.SftpBackupStorageOption()
    sftp_backup_storage_option.name = "bs_from_sftp_server"
    sftp_backup_storage_option.username = "root"
    sftp_backup_storage_option.hostname = sftp_server_vm.get_vm().vmNics[0].ip
    sftp_backup_storage_option.password = "password"
    sftp_backup_storage_option.sshPort = 22
    sftp_backup_storage_option.url = "/zstack_bs"

    backup_storage_inventory = bs_ops.create_backup_storage(sftp_backup_storage_option)


    #create a new vm for creating image step
    vm_offering = test_lib.lib_create_instance_offering(cpuNum = 1, \
            cpuSpeed = 16, memorySize = 536870912, name = 'image_create_test_vm', \
            volume_iops = None, volume_bandwidth = None, \
            net_outbound_bandwidth = None, net_inbound_bandwidth = None)
    test_obj_dict.add_instance_offering(vm_offering)

    vm = test_stub.create_vm(vm_name = 'timeout-test-vm', image_name = 'img5h', \
            instance_offering_uuid = vm_offering.uuid)
    test_obj_dict.add_vm(vm)

    vm.check()


    #populate vm with big files, the max http execute time is 30 mins.
    #the max disk throughput is 50MB/s, use dd to generate 10GB big file will cost ~2400s.
    #the total disk size after dd is 1.0+5=6GB
    import tempfile
    script_file = tempfile.NamedTemporaryFile(delete=False)
    script_file.write("dd if=/dev/zero of=test1 bs=1M count=5120")
    script_file.close()
    if not test_lib.lib_execute_shell_script_in_vm(vm.get_vm(), script_file.name, timeout=3600):    
        test_util.test_fail("generate 5GB big file failed")
    

    #attach backup storage to zone
    cond = res_ops.gen_query_conditions('state', '=', 'Enabled')
    zone = res_ops.query_resource_with_num(res_ops.ZONE, cond, limit = 1)

    bs_ops.attach_backup_storage(backup_storage_inventory.uuid, zone[0].uuid)


    #invoke API with timeout
    vm_root_volume_inv = test_lib.lib_get_root_volume(vm.get_vm())
    root_volume_uuid = vm_root_volume_inv.uuid

    image_option1 = test_util.ImageOption()
    image_option1.set_root_volume_uuid(root_volume_uuid)
    image_option1.set_name('big_image_for_upload')
    image_option1.set_format('qcow2')
    image_option1.set_backup_storage_uuid_list([backup_storage_inventory.uuid])
    #image_option1.set_platform('Linux')
    #bs_type = backup_storage_list[0].type


    #this API can only be invoke when vm is stopped
    vm.stop()
    vm.check()


    time1 = time.time()
    image = img_ops.create_root_volume_template(image_option1)
    time2 = time.time()

    image_uuid = image.uuid

    cost_time = time2 - time1
    test_util.test_logger("start time: %s"  % (time1))
    test_util.test_logger("end time: %s"  % (time2))
    test_util.test_logger("total time: %s"  % (cost_time))


    if cost_time > int(timeout_value):
        test_util.test_fail("The test create image cost time is greater than %s hours: \
%s, which does not meet the test criterial." % (str(timeout_value), cost_time))



#Will be called only if exception happens in test().
def error_cleanup():
    global image_uuid
    img_ops.delete_image(image_uuid)
    img_ops.expunge_image(image_uuid)
    test_lib.lib_error_cleanup(test_obj_dict)
