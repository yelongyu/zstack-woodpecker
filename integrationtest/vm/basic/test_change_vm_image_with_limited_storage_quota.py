'''

New Integration Test for changing vm image.

@author: Xiaoshuang
'''
import hashlib
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.zstack_test.zstack_test_account as test_account
import zstackwoodpecker.zstack_test.zstack_test_image as zstack_image_header
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.image_operations as img_ops
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
   import uuid
   account_name = uuid.uuid1().get_hex()
   account_pass = uuid.uuid1().get_hex()
   account_pass = hashlib.sha512(account_name).hexdigest()
   test_account = acc_ops.create_normal_account(account_name,account_pass)
   global vm
   bs_cond = res_ops.gen_query_conditions("status", '=', "Connected")
   bss = res_ops.query_resource_fields(res_ops.BACKUP_STORAGE, bs_cond, None, fields=['uuid'])
   if not bss:
      test_util.test_skip("not find available backup storage. Skip test")

   test_util.test_dsc('Test change vm image with quota limited')
   test_account_uuid = test_account.uuid
   #set normal account's storage capacity as 4G
   acc_ops.update_quota(test_account.uuid,"volume.capacity","4294967296")
   test_account_session = acc_ops.login_by_account(account_name,account_pass)
   test_stub.share_admin_resource([test_account_uuid])

   vm = test_stub.create_vm(session_uuid = test_account_session)
   vm.check()
   image_option = test_util.ImageOption()
   image_option.set_name('8G')
   image_option.set_format('qcow2')
   image_option.set_url(os.environ.get('imageServer')+"/diskimages/CentOS-7-x86_64-Cloudinit-8G-official.qcow2")
   image_option.set_backup_storage_uuid_list([bss[0].uuid])
   new_image = zstack_image_header.ZstackTestImage()
   new_image.set_creation_option(image_option)
   new_image.add_root_volume_template()

   test_stub.share_admin_resource([test_account_uuid])
   vm.stop(session_uuid = test_account_session)
   image_uuid = test_lib.lib_get_image_by_name("8G").uuid
   try:
      vm_ops.change_vm_image(vm.get_vm().uuid,image_uuid,session_uuid = test_account_session)
   except:
      acc_ops.delete_account(test_account_uuid)
      img_ops.delete_image(test_lib.lib_get_image_by_name('8G').uuid)
      test_util.test_pass('Change Vm Image With Limited Storage Quota Test Success ')
   test_util.test_fail('Overstep the limit of storage capacity')


def error_cleanup():
   global vm
   global test_account_uuid
   if vm:
      vm.destroy()
   if test_account_uuid:
      acc_ops.delete_account(test_account_uuid)





