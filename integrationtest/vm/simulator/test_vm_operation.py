'''

New Test For VM Operations

This case do almost all operations in vm life cycle.
Including:
    1.change instanceoffering
    2.set/del vm ha level
    3.add/del user tags
    4.set vm monitor number
    5.set vm usb redirect
    6.set vm RDP
    7.change owner
    8.add/del sshkey
    9.set/del console password
    10.change vm's password(qga)
    11.migrate(live/cold)
    12.clone vm
    13.change vm's status(stop/start/reboot/pause/resume/force stop/destroy/expunge)
    14.create/resume/delete snapshots
    15.create image;create vm based on the image
    16.create/attach/detach/delete volume;set/del volume qos
    17.attach/detach l3network;set/del nic qos
    18.update vm nic mac
    19.set/del static ip
    20.change vm image
    21.resize vm root volume
    22.add/del scheduler(stop vm;start vm;reboot vm;create volume snapshot)
Excluding:
    1.storage migrage
    2.change console mode

@author: Xiaoshuang
'''
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.volume_operations as vol_ops 
import zstackwoodpecker.operations.image_operations as img_ops
import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.operations.net_operations as net_ops
import zstackwoodpecker.operations.ha_operations as ha_ops
import zstackwoodpecker.operations.console_operations as console_ops
import zstackwoodpecker.operations.scheduler_operations as schd_ops
import zstackwoodpecker.operations.config_operations as config_ops
import zstackwoodpecker.operations.account_operations as account_operations
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.tag_operations as tag_ops
import zstackwoodpecker.zstack_test.zstack_test_image as zstack_image_header
import zstackwoodpecker.zstack_test.zstack_test_snapshot as zstack_snapshot_header
import zstackwoodpecker.zstack_test.zstack_test_vm as zstack_vm_header
import apibinding.api_actions as api_actions
import apibinding.inventory as inventory
import threading
import uuid
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def query_snapshot_number(volume_uuid):
    cond = res_ops.gen_query_conditions('volumeUuid', '=', volume_uuid)
    return res_ops.query_resource_count(res_ops.VOLUME_SNAPSHOT, cond)

def running_vm_operations(vm,bss):
      
   numa = config_ops.get_global_config_value('vm', 'numa')
   live_migration = config_ops.get_global_config_value('localStoragePrimaryStorage','liveMigrationWithStorage.allow')
   ps = test_lib.lib_get_primary_storage_by_vm(vm.get_vm())
   vm_uuid = vm.get_vm().uuid
   #change vm's instanceoffering
   if numa == 'false':
      try:
         vm_ops.update_vm(vm_uuic,2,2048*1024*1024)
         test_util.test_fail('Test Fail.Cannot change instanceoffering of running vm when NUMA is false')
      except:
         config_ops.change_global_config('vm','numa','true')
   
   vm_ops.reboot_vm(vm_uuid)
   vm_ops.update_vm(vm_uuid,2,2048*1024*1024)

   #Change vm's status;set ha level/stop/del ha level/reboot/pause/resume/force stop
   ha_ops.set_vm_instance_ha_level(vm_uuid,'NeverStop')
   vm_ops.stop_vm(vm_uuid)
   ha_ops.del_vm_instance_ha_level(vm_uuid)
   vm_ops.stop_vm(vm_uuid)
   vm_ops.start_vm(vm_uuid)
   vm_ops.reboot_vm(vm_uuid)
   vm_ops.suspend_vm(vm_uuid)
   vm_ops.resume_vm(vm_uuid)
   vm_ops.stop_vm(vm_uuid,'cold')
   vm_ops.start_vm(vm_uuid)

   #clone vms
   vm_ops.clone_vm(vm_uuid,['vm-1','vm-2','vm-3'],'InstantStart')

   #migrate
   candidate_hosts = vm_ops.get_vm_migration_candidate_hosts(vm_uuid)
   migrate_host_uuids = []
   if candidate_hosts == None:
      pass
   else:
      for host in candidate_hosts.inventories:
         migrate_host_uuids.append(host.uuid)
      if ps.type == 'LocalStorage':
         if live_migration == 'false':
       	   try:
       	      vm_ops.migrate_vm(vm_uuid,migrate_host_uuids[0])
       	      test_util.test_fail('Test Fail.Cannot migrate localstorage vm when liveMigrationWithStorage is false.' )
       	   except:
       	      config_ops.change_global_config('localStoragePrimaryStorage','liveMigrationWithStorage.allow','true')
       	 else:
       	    vm_ops.migrate_vm(vm_uuid,migrate_host_uuids[0])
       	    test_util.test_logger('migrate vm success')
      else:
         vm_ops.migrate_vm(vm_uuid,migrate_host_uuids[0])
         test_util.test_logger('migrate vm success')

   #change vm's password(qga)
   try:
      vm_ops.change_vm_password(vm_uuid,'root','testpassword')
      test_util.test_fail('Test Fail.Cannot change vm password when qga is disabled.')
   except:
      vm_ops.set_vm_qga_enable(vm_uuid)
     
   vm_ops.change_vm_password(vm_uuid,'root','testpassword')
   vm_ops.set_vm_qga_disable(vm_uuid)

   #snapshot operations
   sp_option = test_util.SnapshotOption()
   vm_root_volume_inv = test_lib.lib_get_root_volume(vm.get_vm())
   root_volume_uuid = vm_root_volume_inv.uuid
   test_util.test_logger('rootvolumerunning:%s' % root_volume_uuid)
   sp_option.set_volume_uuid(root_volume_uuid)
   sp = vol_ops.create_snapshot(sp_option)
   vm_ops.stop_vm(vm_uuid)
   vol_ops.use_snapshot(sp.uuid)
   vm_ops.start_vm(vm_uuid)
   vol_ops.delete_snapshot(sp.uuid)
   
   common_operations(vm,bss,'running')

   vm_ops.destroy_vm(vm_uuid)
   vm_ops.recover_vm(vm_uuid)
   vm_ops.start_vm(vm_uuid)
   vm.destroy()
   vm.expunge()
   
def stopped_vm_operations(vm,bss):
   
   vm_uuid = vm.get_vm().uuid
   ps = test_lib.lib_get_primary_storage_by_vm(vm.get_vm())
   vm_ops.stop_vm(vm_uuid)
   #Change vm's instanceoffering
   vm_ops.update_vm(vm_uuid,2,2048*1024*1024)
   
   #Change vm's status
   ha_ops.set_vm_instance_ha_level(vm_uuid,'neverstop')
   vm_ops.stop_vm(vm_uuid)
   ha_ops.del_vm_instance_ha_level(vm_uuid)
   vm_ops.stop_vm(vm_uuid)
   if ps.type != 'LocalStorage':
      target_host_uuid = test_lib.lib_find_random_host(vm.get_vm()).uuid
      if target_host_uuid != None:
         vm_ops.start_vm_with_target_host(vm_uuid,target_host_uuid)
   #vm_ops.stop_vm(vm_uuid)
   vm_ops.destroy_vm(vm_uuid)
   vm_ops.recover_vm(vm_uuid)
   vm_ops.reinit_vm(vm_uuid)

   #clone
   vm_ops.clone_vm(vm_uuid,['vm-1','vm-2','vm-3'],'InstantStart')

   #migrate
   vm_ops.start_vm(vm_uuid)
   candidate_hosts = vm_ops.get_vm_migration_candidate_hosts(vm_uuid)
   vm_ops.stop_vm(vm_uuid)
   migrate_host_uuids = []
   if candidate_hosts != None:
      for host in candidate_hosts.inventories:
         migrate_host_uuids.append(host.uuid)
      if ps.type == 'LocalStorage':
         vol_uuid = test_lib.lib_get_root_volume(vm.get_vm()).uuid
         #vm_ops.migrate_vm(vm_uuid,migrate_host_uuids[0])		
         vol_ops.migrate_volume(vol_uuid, migrate_host_uuids[0])
         test_util.test_logger('migrate vm success')
   
   #resize root volume
   vol_size = test_lib.lib_get_root_volume(vm.get_vm()).size
   vol_uuid = test_lib.lib_get_root_volume(vm.get_vm()).uuid
   set_size = 1024*1024*1024*5
   vol_ops.resize_volume(vol_uuid, set_size)
   vm.update()
   vol_size_after = test_lib.lib_get_root_volume(vm.get_vm()).size
   if set_size != vol_size_after:
      test_util.test_fail('Resize Root Volume failed, size = %s' % vol_size_after)
   test_util.test_logger('resize vm success')
   
   #storage migrate
         
   #change vm image
   image_list = vm_ops.get_image_candidates_for_vm_to_change(vm_uuid)
   image_uuids = []
   for image in image_list.inventories:
      image_uuids.append(image.uuid)
   vm_ops.change_vm_image(vm_uuid,image_uuids[0])
   vm.update()
   
   #update vm nic mac
   nic_uuid = vm.get_vm().vmNics[0].uuid
   mac = 'fa:4c:ee:9a:76:00'
   vm_ops.update_vm_nic_mac(nic_uuid,mac)

   #set/del static ip
   l3network_uuid = test_lib.lib_get_l3_uuid_by_nic(nic_uuid)
   vm_ops.change_vm_static_ip(vm_uuid, l3network_uuid, vm.get_vm().vmNics[0].ip)
   vm_ops.delete_vm_static_ip(vm_uuid, l3network_uuid)
  
   #snapshot operations
   sp_option = test_util.SnapshotOption()
   vm_root_volume_inv = test_lib.lib_get_root_volume(vm.get_vm())
   root_volume_uuid = vm_root_volume_inv.uuid
   sp_option.set_volume_uuid(root_volume_uuid)
   sp = vol_ops.create_snapshot(sp_option)
   vol_ops.use_snapshot(sp.uuid)
   vol_ops.delete_snapshot(sp.uuid)

   common_operations(vm,bss,'stopped')
   vm.destroy()
   vm.expunge()

def common_operations(vm,bss,status):

   vm_uuid = vm.get_vm().uuid 
   #image operations
   vm_root_volume_inv = test_lib.lib_get_root_volume(vm.get_vm())
   root_volume_uuid = vm_root_volume_inv.uuid
   image_option = test_util.ImageOption()
   image_option.set_root_volume_uuid(root_volume_uuid)
   image_option.set_name('image_base_on_%s_vm' % status)
   image_option.set_backup_storage_uuid_list([bss[0].uuid])
   image = img_ops.create_root_volume_template(image_option)
   test_util.test_logger('create image success')
   image_base_on_stopped_vm_uuid = test_lib.lib_get_image_by_name("image_base_on_%s_vm" % status).uuid
   base_on_image_vm = test_stub.create_vm(image_uuid=image_base_on_stopped_vm_uuid)
   vm_ops.destroy_vm(base_on_image_vm.get_vm().uuid)
   vm_ops.expunge_vm(base_on_image_vm.get_vm().uuid)

   #volume operations
   volume = test_stub.create_volume()
   vol_uuid = volume.get_volume().uuid
   test_lib.lib_attach_volume(vol_uuid, vm_uuid)
   test_util.test_logger('attach volume success')
   vm_ops.set_vm_disk_qos(vol_uuid,'20480')
   test_util.test_logger('set volume qos success')
   vm_ops.del_vm_disk_qos(vol_uuid)
   test_util.test_logger('delete volume qos success')
   test_lib.lib_detach_volume(vol_uuid)
   test_util.test_logger('detach volume success')
   test_lib.lib_delete_volume(vol_uuid)
   test_util.test_logger('delete volume success')

   #network operations
   nic_uuid = vm.get_vm().vmNics[0].uuid
   l3_uuid = test_lib.lib_get_random_l3(zone_uuid = vm.get_vm().zoneUuid).uuid
   test_util.test_logger("l3_uuid:%s"% l3_uuid)
   net_ops.detach_l3(nic_uuid)
   test_util.test_logger("l3_uuid:%s"% l3_uuid)
   net_ops.attach_l3(l3_uuid,vm_uuid)

   vm_uuid = vm.get_vm().uuid
   #set/del console password
   console_ops.set_vm_console_password(vm_uuid,'testpassword')
   console_ops.delete_vm_console_password(vm_uuid)

   #add/del sshkey
   sshkeyimage_uuid = test_lib.lib_get_image_by_name('sshkeyimage').uuid
   sshkey_vm = test_stub.create_vm(image_uuid = sshkeyimage_uuid)
   sshkey_vm_uuid = sshkey_vm.get_vm().uuid
   test_lib.lib_add_vm_sshkey(sshkey_vm_uuid,'testsshkey')
   vm_ops.delete_vm_ssh_key(sshkey_vm_uuid)
   vm_ops.destroy_vm(sshkey_vm_uuid)
   vm_ops.expunge_vm(sshkey_vm_uuid)

   #change owner
   account_name = uuid.uuid1().get_hex()
   account_pass = uuid.uuid1().get_hex()
   #account_pass = hashlib.sha512(account_name).hexdigest()
   test_account = account_operations.create_normal_account(account_name,account_pass)
   test_account_uuid = test_account.uuid
   admin_uuid = res_ops.get_resource_owner([vm_uuid])
   res_ops.change_recource_owner(test_account_uuid,vm_uuid)
   res_ops.change_recource_owner(admin_uuid,vm_uuid)
   account_operations.delete_account(test_account_uuid)

   #create/delete user tag
   tag = tag_ops.create_user_tag('VmInstanceVO',vm_uuid,'a simulator vm')
   tag_ops.delete_tag(tag.uuid)
      
   #set vm monitor number
   vm_ops.set_vm_monitor_number(vm_uuid,'2')

   #set vm usb redirect
   vm_ops.set_vm_usb_redirect(vm_uuid,'true')
   vm_ops.set_vm_usb_redirect(vm_uuid,'false')

   #set vm rdp
   vm_ops.set_vm_rdp(vm_uuid,'true')
   vm_ops.set_vm_rdp(vm_uuid,'false')
         
def scheduler_vm_operations(vm,bss):

   vm_ops.stop_vm(vm.get_vm().uuid)
   volume = vm.get_vm().allVolumes[0]

   start_date = int(time.time())
   schd_job1 = schd_ops.create_scheduler_job('simple_start_vm_scheduler', 'simple_start_vm_scheduler', vm.get_vm().uuid, 'startVm', None)
   schd_trigger1 = schd_ops.create_scheduler_trigger('simple_start_vm_scheduler', start_date+5, None, 15, 'simple')
   schd_ops.add_scheduler_job_to_trigger(schd_trigger1.uuid, schd_job1.uuid)

   schd_job2 = schd_ops.create_scheduler_job('simple_stop_vm_scheduler', 'simple_stop_vm_scheduler', vm.get_vm().uuid, 'stopVm', None)
   schd_trigger2 = schd_ops.create_scheduler_trigger('simple_stop_vm_scheduler', start_date+15, None, 15, 'simple')
   schd_ops.add_scheduler_job_to_trigger(schd_trigger2.uuid, schd_job2.uuid)

   schd_job3 = schd_ops.create_scheduler_job('simple_reboot_vm_scheduler', 'simple_reboot_vm_scheduler', vm.get_vm().uuid, 'rebootVm', None)
   schd_trigger3 = schd_ops.create_scheduler_trigger('simple_reboot_vm_scheduler', start_date+10, None, 15, 'simple')
   schd_ops.add_scheduler_job_to_trigger(schd_trigger3.uuid, schd_job3.uuid)

   schd_job4 = schd_ops.create_scheduler_job('simple_create_snapshot_scheduler', 'simple_create_snapshot_scheduler', volume.uuid, 'volumeSnapshot', None)
   schd_trigger4 = schd_ops.create_scheduler_trigger('simple_create_snapshot_scheduler', start_date+12, None, 15, 'simple')
   schd_ops.add_scheduler_job_to_trigger(schd_trigger4.uuid, schd_job4.uuid)

   snapshot_num = 0
   for i in range(0,3):
      test_util.test_logger('round %s' % (i))
      test_stub.sleep_util(start_date + 5 + 15*i + 1)  
      #test_util.test_logger('check volume snapshot number at %s, there should be %s' % (start_date + 5 +15*i, snapshot_num))
      test_util.test_logger('check VM status at %s, VM is expected to start' % (start_date + 15 + 15*i))
      vm.update()
      if vm.get_vm().state != 'Starting' and vm.get_vm().state != 'Running':
         test_util.test_fail('VM is expected to start')
      
      test_stub.sleep_util(start_date +10 +15*i + 1)
      test_util.test_logger('check VM status at %s, VM is expected to reboot' % (start_date + 10 + 15*i))
      vm.update()
      if not test_lib.lib_find_in_local_management_server_log(start_date+10, '[msg received]: {"org.zstack.header.vm.RebootVmInstanceMsg', vm.get_vm().uuid):
         test_util.test_fail('VM is expected to reboot start from %s' % (start_date+ 10 + 15*i))
     
      test_stub.sleep_util(start_date + 12 + 15*i + 1)
      snapshot_num +=1
      new_snapshot_num = query_snapshot_number(volume.uuid)
      if snapshot_num != new_snapshot_num:
         test_util.test_fail('there should be %s snapshots' % (snapshot_num))
      #snapshot_num +=1
      test_util.test_logger('check volume snapshot number at %s, there should be %s' % (start_date + 5 +15*i, snapshot_num))
      #test_util.test_logger('check VM status at %s, VM is expected to stop' % (start_date + 6 + 15*i +1))
 
     
      test_stub.sleep_util(start_date +15 +15*i + 1)
      test_util.test_logger('check VM status at %s, VM is expected to stop' % (start_date + 15 + 15*i))
      vm.update()
      if vm.get_vm().state != 'Stopping' and vm.get_vm().state != 'Stopped':
         test_util.test_fail('VM is expected to stop')
   
   schd_ops.del_scheduler_job(schd_job1.uuid)
   schd_ops.del_scheduler_trigger(schd_trigger1.uuid)
   schd_ops.del_scheduler_job(schd_job2.uuid)
   schd_ops.del_scheduler_trigger(schd_trigger2.uuid)
   schd_ops.del_scheduler_job(schd_job3.uuid)
   schd_ops.del_scheduler_trigger(schd_trigger3.uuid)
   schd_ops.del_scheduler_job(schd_job4.uuid)
   schd_ops.del_scheduler_trigger(schd_trigger4.uuid)
   
   vm.update()
   vm_state = vm.get_vm().state
   snapshot_num_after = query_snapshot_number(volume.uuid) 
   test_util.test_logger('snapshotnumber:%s' % snapshot_num_after)
   for i in range(3,5):
      test_util.test_logger('round %s' % (i))
      test_stub.sleep_util(start_date + 1 +15*i)
      vm.update()
      test_util.test_logger('check vm status at %s, vm is expected to stay in state %s' % (start_date + 5 + 15*i, vm_state))
      if vm.get_vm().state != vm_state:
         test_util.test_fail('vm is expected to stay in state %s' % (vm_state))
      if snapshot_num_after != snapshot_num:
         test_util.test_fail('the number of snapshots is expected to stay in %s' % (snapshot_num))

   vm.destroy()
   vm.expunge()
   
def test():
   global vm
   bs_cond = res_ops.gen_query_conditions('status','=','Connected')
   bss = res_ops.query_resource_fields(res_ops.BACKUP_STORAGE, bs_cond, None, fields=['uuid'])
   if not bss:
      test_util.test_skip("not find availbale backup storage.Skip test")
   
   #add iso
   image_option_iso = test_util.ImageOption()
   image_option_iso.set_name('vm-iso')
   image_option_iso.set_format('iso')
   image_option_iso.set_mediaType('RootVolumeTemplate')
   image_option_iso.set_url("http://iso/CentOS-x86_64-7.2-Minimal.iso")
   image_option_iso.set_backup_storage_uuid_list([bss[0].uuid])
   new_image = zstack_image_header.ZstackTestImage()
   new_image.set_creation_option(image_option_iso)
   new_image.add_root_volume_template()

   #add sshkeyimage 
   image_option_sshkey = test_util.ImageOption()
   image_option_sshkey.set_name('sshkeyimage')
   image_option_sshkey.set_format('qcow2')
   image_option_sshkey.set_mediaType('RootVolumeTemplate')
   image_option_sshkey.set_url("http://zstack-cloudinit.img")
   image_option_sshkey.set_backup_storage_uuid_list([bss[0].uuid])
   new_image = zstack_image_header.ZstackTestImage()
   new_image.set_creation_option(image_option_sshkey)
   new_image.add_root_volume_template()

   image_name = os.environ.get('imageName3')
   centosimage_uuid = test_lib.lib_get_image_by_name(image_name).uuid
   running_vm = test_stub.create_vm(image_uuid = centosimage_uuid)
   stopped_vm = test_stub.create_vm(image_uuid = centosimage_uuid)
   scheduler_vm = test_stub.create_vm(image_uuid = centosimage_uuid)

   running_vm_operations(running_vm,bss)
   stopped_vm_operations(stopped_vm,bss)  
   scheduler_vm_operations(scheduler_vm,bss)

def error_cleanup():
   global vm
   if vm:
      vm.destroy()
