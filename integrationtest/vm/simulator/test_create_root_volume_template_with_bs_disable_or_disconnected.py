'''
Integration Test for VM create root volumn template from root volumn with ImageStore BackupStorage disable or disconnected.
@author: rhZhou
'''


import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.backupstorage_operations as bs_ops
import zstackwoodpecker.operations.image_operations as img_ops


ENABLE = 'enable'
DISABLE = 'disable'
infoType='hostname'
infoValue='222.222.222.222'

test_stub = test_lib.lib_get_test_stub()
bss = None
vm=None
host=None


def test():
	"""
	"""
	image_uuid = None
	flag1 = False
	flag2 = False
	global bss,vm,host
	test_util.test_dsc('test for creating root volume template with bss disconnected and disable')
	
	#create a new vm
	image_uuid = test_lib.lib_get_image_by_name("centos").uuid
	vm = test_stub.create_vm(image_uuid=image_uuid)

	# firstly,test for bss state disable
	# change backup storage state

	cond = res_ops.gen_query_conditions('state', '=', 'Enabled')
	bss = res_ops.query_resource_with_num(res_ops.BACKUP_STORAGE, cond, limit=1)
	bs_ops.change_backup_storage_state(bss[0].uuid,DISABLE)

	#prepare to create root volume template after buckup_storage change state to disable

	root_volume_uuid = test_lib.lib_get_root_volume_uuid(vm.get_vm())

	image_option1 = test_util.ImageOption()
	image_option1.set_root_volume_uuid(root_volume_uuid)
	image_option1.set_name('image_for_bss_disconnected_test')
	image_option1.set_format('qcow2')
	image_option1.set_backup_storage_uuid_list([bss[0].uuid])
	# image_option1.set_platform('Linux')
	# bs_type = bss[0].type

	vm.stop()

	# this API can only be invoke when vm is stopped
	try:
		img_ops.create_root_volume_template(image_option1)
	except:
		bs_ops.change_backup_storage_state(bss[0].uuid, ENABLE)
		flag1=True

	# secondly,test for bss disconnected
	# change bss.host(IP address) to let bss disconnected.
	
	host = bss[0].hostname
	bs_ops.update_image_store_backup_storage_info(bss[0].uuid, infoType, infoValue)
	try:
		bs_ops.reconnect_backup_storage(bss[0].uuid)
	except:
		#can't reconnect the bs,so the bs'status is disconnected
		pass
	
	#create root volume template after buckup_storage change state to disable
	try:
		img_ops.create_root_volume_template(image_option1)
	except:
		bs_ops.update_image_store_backup_storage_info(bss[0].uuid, infoType, host)
		bs_ops.reconnect_backup_storage(bss[0].uuid)
		flag2=True
	
	if flag1 and flag2:
		vm.clean()
		test_util.test_pass(
			"can't create root volume template,The test that create root volume template from root volume with ImageStoreBackupStorage server disconnected or disable is "
			"success! ")
	else:
		vm.clean()
		test_util.test_fail(
			"success create root image,The test that create root volume template from root volume with ImageStoreBackupStorage server disconnected or dieable is "
			"fail! ")


# Will be called only if exception happens in test().
def error_cleanup():
	global vm,bss,host,ENABLE,infoType
	if vm:
		vm.clean()
	bs_ops.change_backup_storage_state(bss[0].uuid, ENABLE)
	bs_ops.update_image_store_backup_storage_info(bss[0].uuid, infoType, host)
	bs_ops.reconnect_backup_storage(bss[0].uuid)