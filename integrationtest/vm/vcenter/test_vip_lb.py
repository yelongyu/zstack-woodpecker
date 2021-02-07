'''

Test load balance with snat ip 

Test step:
    1. Create 2 VM with load balance l3 network service.
    2. Create 2 LB with 22 and 80 port
    3. Check the 2 LB status
    4. Destroy VMs

@author: moyu
'''


import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_load_balancer as zstack_lb_header
import zstackwoodpecker.zstack_test.zstack_test_vip as zstack_vip_header
import apibinding.inventory as inventory

import time
import os
import threading

test_lib.TestHarness = test_lib.TestHarnessVR

PfRule = test_state.PfRule
Port = test_state.Port
test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()


vm1 = None
vm2 = None
vip = None

def test():
  global vm1, vm2, vip

  l3_vr_network = os.environ['l3vCenterNoVlanNetworkName']
  image_name = os.environ['image_dhcp_name']

  test_util.test_dsc('Create test vm with lb.')
  vm1 = test_stub.create_vm_in_vcenter(vm_name='test_vip_lb_1', image_name = image_name, l3_name=l3_vr_network)
  test_obj_dict.add_vm(vm1)
  vm2 = test_stub.create_vm_in_vcenter(vm_name='test_vip_lb_2', image_name = image_name, l3_name=l3_vr_network)
  test_obj_dict.add_vm(vm2)
  time.sleep(50)


  vm_nic1 = vm1.get_vm().vmNics[0]
  vm_nic1_uuid = vm_nic1.uuid
  vm_nic1_ip = vm_nic1.ip
  vm_nic2 = vm2.get_vm().vmNics[0]
  vm_nic2_uuid = vm_nic2.uuid
  vm_nic2_ip = vm_nic2.ip

  
  test_stub.set_httpd_in_vm(vm1.get_vm(), vm_nic1_ip)
  test_stub.set_httpd_in_vm(vm2.get_vm(), vm_nic2_ip)

  pri_l3_uuid = vm_nic1.l3NetworkUuid

  vr = test_lib.lib_find_vr_by_l3_uuid(pri_l3_uuid)[0]
  vr_pub_ip = test_lib.lib_find_vr_pub_ip(vr)
  vip = zstack_vip_header.ZstackTestVip()
  vip.get_snat_ip_as_vip(vr_pub_ip)
  vip.isVcenter = True
  test_obj_dict.add_vip(vip)

  lb = zstack_lb_header.ZstackTestLoadBalancer()
  lb2 = zstack_lb_header.ZstackTestLoadBalancer()
  lb.create('create lb test', vip.get_vip().uuid)
  lb2.create('create lb2 test', vip.get_vip().uuid)
  lb.isVcenter = True
  lb2.isVcenter = True
  test_obj_dict.add_load_balancer(lb)
  test_obj_dict.add_load_balancer(lb2)
  vip.attach_lb(lb)
  vip.attach_lb(lb2)

  lb_creation_option = test_lib.lib_create_lb_listener_option(lbl_port = 222, lbi_port = 22)
  lb2_creation_option = test_lib.lib_create_lb_listener_option(lbl_port = 2222, lbi_port = 80)

  lbl = lb.create_listener(lb_creation_option)
  lbl2 = lb2.create_listener(lb2_creation_option)

  lbl.add_nics([vm_nic1_uuid, vm_nic2_uuid])
  lbl2.add_nics([vm_nic1_uuid, vm_nic2_uuid])

  vm1.check()
  vm2.check()

  lb.check()
  lb2.check()
  vip.check()
  lb.delete()
  lb2.delete()
  test_obj_dict.rm_vip(vip)
  test_obj_dict.rm_load_balancer(lb)
  test_obj_dict.rm_load_balancer(lb2)
  lb.check()
  lb2.check()
  test_lib.lib_robot_cleanup(test_obj_dict)
  test_util.test_pass('Create Load Balancer Test Success')

def error_cleanup():
    global vm1,vm2,vip
    vm1.destroy()
    vm2.destroy()
    vm1.expunge()
    vm2.expunge()
