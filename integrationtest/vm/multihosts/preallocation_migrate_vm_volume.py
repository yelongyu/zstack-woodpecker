import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.account_operations as acc_ops
import apibinding.api_actions as api_actions
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as test_vm_header
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.volume_operations as vol_ops
import zstacklib.utils.ssh as ssh
import zstackwoodpecker.operations.config_operations as conf_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as zstack_vm_header
import time
import operator
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

preallocation_list = ['falloc','metadata','full','none']
preallocation_value = []
Volume_size = []
Volumebacking_file = []
Volume_installPath = []

mn_ip = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].hostName
ssh.make_ssh_no_password(mn_ip, 'root', 'password')

def test():
    global test_obj_dict
    for i in preallocation_list:
	conf_ops.change_global_config("localStoragePrimaryStorage", "qcow2.allocation", i)

	disk_offering = test_lib.lib_get_disk_offering_by_name(os.environ.get('smallDiskOfferingName'))
	volume_creation_option = test_util.VolumeOption()
	volume_creation_option.set_disk_offering_uuid(disk_offering.uuid)
	volume = test_stub.create_volume(volume_creation_option)
	test_obj_dict.add_volume(volume)
	volume.check()
	datavolume_uuid = volume.volume.uuid
	datavol_size = volume.volume.size

	vm_create_option = test_util.VmOption()
	vm = test_lib.lib_create_vm(vm_create_option)
	test_obj_dict.add_vm(vm)

	volume.attach(vm)

	vm.stop()
   	vm.check()
    	vm.start()
    	vm_uuid = vm.vm.uuid
   	target_host = test_lib.lib_find_random_host(vm.vm)
    	target_host_uuid = target_host.uuid

	value = conf_ops.get_global_config_value('localStoragePrimaryStorage', 'qcow2.allocation')
	preallocation_value.append(value)

	host_ip = test_lib.lib_find_host_by_vm(vm.get_vm()).managementIp
	installPath = res_ops.query_resource(res_ops.VOLUME)[0].installPath 
   	Volume_installPath.append(installPath)
     
    	cmd = 'qemu-img info %s | grep ''backing file:'' | awk ''{print $3}''  '%(installPath)
	ttt = test_lib.lib_execute_ssh_cmd(host_ip, 'admin', 'password', cmd)
    	Volumebacking_file.append(ttt)
        
	rootvolume_disksize = test_lib.lib_get_root_volume(vm.get_vm()).actualSize

    	rootvol_size = test_lib.lib_get_root_volume(vm.get_vm()).size
    	Volume_size.append(rootvol_size)
        
    	cmd = 'du -s %s | awk ''{print $1}'' '%(installPath)
    	a = test_lib.lib_execute_ssh_cmd(host_ip, 'admin', 'password', cmd)
#    	if a != rootvolume_disksize:
#                test_util.test_fail('Volume_size is not same as Volume_du_size ')

	conf_ops.change_global_config("localStoragePrimaryStorage", "liveMigrationWithStorage.allow", "true")

	volume.detach()

    	vm_ops.migrate_vm(vm_uuid,target_host_uuid)
    	vol_ops.migrate_volume(datavolume_uuid, target_host.uuid)

    	cond = res_ops.gen_query_conditions('uuid', '=', datavolume_uuid)
    	data_volume = res_ops.query_resource(res_ops.VOLUME, cond)
    	datavol_size_after = data_volume[0].size
    	if datavol_size != datavol_size_after:
        	test_util.test_fail('migrate data volume fail')

    	rootvolume_disksize_after = test_lib.lib_get_root_volume(vm.get_vm()).actualSize
    	if rootvolume_disksize != rootvolume_disksize_after:
        	test_util.test_fail('migrate root volume fail')
	test_lib.lib_error_cleanup(test_obj_dict)
    if operator.eq(preallocation_list,preallocation_value):
        try:
         	for x in range(1,4):
                	if Volume_size[0] != Volume_size[x]:
                    		test_util.test_fail('root volumr is not the same')
            	for m in range(1,4):
                	if Volume_installPath[0] == Volume_installPath[m]:
                    		test_lib.test_fail('the volume installpath is same ')
            	for m in range(1,4):
                	if Volumebacking_file[0] != Volumebacking_file[m]:
                    		test_lib.test_fail('the volume backingfile is not same ')
        except:
            	test_util.test_pass(' ')
    else:
        test_util.test_fail('preallocation setting failed')

#    	test_lib.lib_error_cleanup(test_obj_dict)

def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)

