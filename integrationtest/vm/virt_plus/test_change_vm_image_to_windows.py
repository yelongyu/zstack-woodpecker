'''
Integration Test for changing vm image from linux to windows in virt_plus.

@author: Xiaoshuang
'''

import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.zstack_test.zstack_test_image as zstack_image_header
import zstackwoodpecker.zstack_test.zstack_test_vm as zstack_vm_header
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.config_operations as con_ops
import time
import os

vm = None
test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
   test_util.test_dsc('Test Change VM Image Function')
   #set overProvisioning.primaryStorage's value as 10
   con_ops.change_global_config('mevoco','overProvisioning.primaryStorage',10)
   global vm
   bs_cond = res_ops.gen_query_conditions("status","=","Connected")
   bss = res_ops.query_resource_fields(res_ops.BACKUP_STORAGE, bs_cond, None, fields=['uuid'])
   if not bss:
      test_util.test_skip("not find available backup storage.Skip test")
   test_lib.lib_create_disk_offering(diskSize=1099511627776,name="1T")
   disk_offering_uuids = [test_lib.lib_get_disk_offering_by_name("smallDiskOffering").uuid,test_lib.lib_get_disk_offering_by_name("root-disk").uuid,test_lib.lib_get_disk_offering_by_name("1T").uuid]
   #create vm with 3 data volumes
   vm = test_stub.create_vm(image_name = "ttylinux",vm_name="test-vm",disk_offering_uuids = disk_offering_uuids)
   test_obj_dict.add_vm(vm)
   vm.check()

   vm_uuid = vm.get_vm().uuid
   last_data_volumes_uuids = []
   last_data_volumes = test_lib.lib_get_data_volumes(vm.get_vm())
   for data_volume in last_data_volumes:
        last_data_volumes_uuids.append(data_volume.uuid)
   last_l3network_uuid = test_lib.lib_get_l3s_uuid_by_vm(vm.get_vm())
   last_primarystorage_uuid = test_lib.lib_get_root_volume(vm.get_vm()).primaryStorageUuid
   vm_ops.stop_vm(vm_uuid)
   image_option = test_util.ImageOption()
   image_option.set_name('windows_for_test')
   image_option.set_format('qcow2')
   image_option.set_mediaType('RootVolumeTemplate')
   image_option.set_platform('windows')
   #image_option.set_url('http://172.20.1.16:7480/diskimages/windows-telnet.qcow2')
   image_option.set_url(os.environ.get('windowsImageUrl'))
   image_option.set_backup_storage_uuid_list([bss[0].uuid])
   image_option.set_timeout(1800*1000)
   new_image = zstack_image_header.ZstackTestImage()
   new_image.set_creation_option(image_option)
   new_image.add_root_volume_template()

   image_windows_uuid = test_lib.lib_get_image_by_name("windows_for_test").uuid
   vm_ops.change_vm_image(vm_uuid,image_windows_uuid)
   vm_ops.start_vm(vm_uuid)
   vm.update()
   vm_ip = vm.get_vm().vmNics[0].ip
   #check whether the windows vm is running successfully
   if not test_lib.lib_wait_target_up(vm_ip,'23',1200):
      test_util.test_fail('vm:%s is not startup in 1200 seconds.Fail to reboot it.' % vm_uuid)
   #check whether data volumes attached to the vm has changed
   data_volumes_after_uuids = []
   data_volumes_after = test_lib.lib_get_data_volumes(vm.get_vm())
   for data_volume in data_volumes_after:
      data_volumes_after_uuids.append(data_volume.uuid)
   if set(last_data_volumes_uuids) != set(data_volumes_after_uuids):
      test_util.test_fail('Change Vm Image Failed.Data volumes changed.')
   #check whether the network config has changed
   l3network_uuid_after = test_lib.lib_get_l3s_uuid_by_vm(vm.get_vm())
   if l3network_uuid_after != last_l3network_uuid:
      test_util.test_fail('Change VM Image Failed.The Network config has changed.')
   #check whether primarystorage has changed
   primarystorage_uuid_after = test_lib.lib_get_root_volume(vm.get_vm()).primaryStorageUuid
   if primarystorage_uuid_after != last_primarystorage_uuid:
      test_util.test_fail('Change VM Image Failed.Primarystorage has changed.')
   #check whether the linux vm is running successfully
   image_linux_uuid = test_lib.lib_get_image_by_name("image_for_sg_test").uuid
   vm_ops.stop_vm(vm_uuid)
   vm_ops.change_vm_image(vm_uuid,image_linux_uuid)
   vm_ops.start_vm(vm_uuid)
   if not test_lib.lib_wait_target_up(vm_ip,'22',180):
      test_util.test_fail('vm:%s is not startup in 180 seconds.Fail to reboot it.' % vm_uuid)
   #check whether data volumes attached to the vm has changed
   data_volumes_after_uuids_linux = []
   data_volumes_after_linux = test_lib.lib_get_data_volumes(vm.get_vm())
   for data_volume in data_volumes_after_linux:
      data_volumes_after_uuids_linux.append(data_volume.uuid)
   if set(data_volumes_after_uuids) != set(data_volumes_after_uuids_linux):
      test_util.test_fail('Change Vm Image Failed.Data volumes changed.')
   #check whether the network config has changed
   l3network_uuid_after_linux = test_lib.lib_get_l3s_uuid_by_vm(vm.get_vm())
   if l3network_uuid_after != l3network_uuid_after_linux:
      test_util.test_fail('Change VM Image Failed.The Network config has changed.')
   #check whether primarystorage has changed
   primarystorage_uuid_after_linux = test_lib.lib_get_root_volume(vm.get_vm()).primaryStorageUuid
   if primarystorage_uuid_after != primarystorage_uuid_after_linux:
      test_util.test_fail('Change VM Image Failed.Primarystorage has changed.')


   test_lib.lib_destroy_vm_and_data_volumes(vm.get_vm())
   vm.expunge()
   img_ops.delete_image(image_windows_uuid)
   img_ops.expunge_image(image_windows_uuid)
   test_util.test_pass('Change Vm Image Test Success')

def error_cleanup():
   global vm
   if vm:
      vm.destroy()
