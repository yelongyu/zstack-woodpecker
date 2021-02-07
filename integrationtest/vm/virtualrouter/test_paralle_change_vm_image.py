'''

Integration Test for changing vm image.
This case covers bug ZSTAC-20856

@author: Lei Liu
'''

import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.account_operations as acc_ops
import zstackwoodpecker.operations.config_operations as con_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import time
import urllib3
import json

vm = None
test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def change_vm_image(vm_uuid,image_uuid,session_uuid=None):
    if session_uuid is None:
        tmp_session_uuid = account_operations.login_as_admin()
    else:
        tmp_session_uuid = session_uuid

    management_node_ip = res_ops.query_resource(res_ops.MANAGEMENT_NODE)[0].hostName
    request_url = "http://" + management_node_ip + ":8080/zstack/v1/vm-instances/"\
        + vm_uuid + "/actions"

    pool = urllib3.PoolManager(timeout=120.0, retries=urllib3.util.retry.Retry(15))
    request_data = {
        "changeVmImage": {
            "imageUuid": image_uuid
            }
        }
    headers = {
        "Content-Type": "application/json",
        "Authorization": "OAuth " + tmp_session_uuid
    }
    rd = json.dumps(request_data)
    response = pool.urlopen('PUT', request_url, headers=headers,  body=rd)

    if session_uuid is None:
        # Need logout for this acction
        delete_session_uuid_url = "http://" + management_node_ip\
           + "zstack/v1/accounts/sessions/" + tmp_session_uuid
    pool.clear()

    return response

def test():
   test_util.test_dsc('Test Change VM Image Function')
   #set overProvisioning.primaryStorage's value as 10
   primary_storage_list = res_ops.query_resource(res_ops.PRIMARY_STORAGE)
   for ps in primary_storage_list:
       if ps.type == "SharedBlock" or ps.type == "AliyunEBS":
           test_util.test_skip('SharedBlock/AliyunEBS primary storage does not support overProvision')
   con_ops.change_global_config('mevoco','overProvisioning.primaryStorage',10)
   global vm
   test_lib.lib_create_disk_offering(diskSize=107374182400,name="100G")
   l3_uuid = test_lib.lib_get_l3_by_name("l3VlanNetwork3").uuid
   image1 = test_lib.lib_get_image_by_name("ttylinux")
   image1_uuid = image1.uuid
   #choose the ps which availableCapacity >= 105G
   cond = res_ops.gen_query_conditions('availableCapacity', '>=', '112742891520')
   ps_uuid = res_ops.query_resource(res_ops.PRIMARY_STORAGE, cond)[0].uuid
   system_tag = "primaryStorageUuidForDataVolume::%s" % ps_uuid
   vma = test_stub.create_vm(l3_uuid_list = [l3_uuid],image_uuid = image1_uuid,vm_name="test-change_image-a", system_tags=[system_tag])
   vmb = test_stub.create_vm(l3_uuid_list = [l3_uuid],image_uuid = image1_uuid,vm_name="test-change_image-b", system_tags=[system_tag])
   test_obj_dict.add_vm(vma)
   test_obj_dict.add_vm(vmb)
   vma.check()
   vmb.check()

   vma_uuid = vma.get_vm().uuid
   vmb_uuid = vmb.get_vm().uuid

   vm_ops.stop_vm(vma_uuid)
   vm_ops.stop_vm(vmb_uuid)

   image2 = test_lib.lib_get_image_by_name("windows")
   image2_uuid = image2.uuid
   for i in range(0, 5):
       vm_verify = test_lib.lib_get_vm_by_uuid(vma_uuid)
       if vm_verify.state == "Stopped":
           break
       time.sleep(5)
       if i == 4:
           test_util.test_fail('Fail to stop vm a within 25s')
           test_lib

   for i in range(0, 5):
       vm_verify = test_lib.lib_get_vm_by_uuid(vmb_uuid)
       if vm_verify.state == "Stopped":
           break
       time.sleep(5)
       if i == 4:
           test_util.test_fail('Fail to stop vm b within 25s')
           test_lib

   session_uuid = acc_ops.login_as_admin()
   joba_url = change_vm_image(vma_uuid, image2_uuid, session_uuid)
   jobb_url = change_vm_image(vmb_uuid, image2_uuid, session_uuid)

   # Just sleep 2s to wait change vm image response
   time.sleep(2)
   vm_ops.start_vm(vmb_uuid)

   vm_verify = test_lib.lib_get_vm_by_uuid(vmb_uuid)
   if len(vm_verify.hostUuid) != 32:
       test_util.test_fail('The host uuid of vm b is not right. Host uuid is: ' + vm_verify.hostUuid)
   if vm_verify.imageUuid != image2_uuid:
       test_util.test_fail('Fail to change vm b image. Vm b image uuid is ' + vm_verify.imageUuid)

   test_util.test_pass('Paralle Change Vm Image Test Success')

def error_cleanup():
   global vma
   global vmb
   if vma:
      vma.destroy()
   if vmb:
      vmb.destroy()
