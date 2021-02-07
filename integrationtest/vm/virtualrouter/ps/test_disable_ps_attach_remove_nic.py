'''
New Integration Test for attach and remove nic of vm under PS disable mode.

@author: SyZhao
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.primarystorage_operations as ps_ops
import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.header.vm as vm_header
import os

_config_ = {
        'timeout' : 1000,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()
ps_uuid = None
host_uuid = None
vr_uuid = None

def test():
    global test_obj_dict
    global ps_uuid
    global host_uuid
    global vr_uuid

    test_util.test_dsc('Create test vm and check')
    image_name = os.environ.get('imageName_net')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    l3_name = os.environ.get('l3VlanDNATNetworkName')
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    l3_net_list = [l3_net_uuid]
    l3_name2 = os.environ.get('l3VlanNetworkName1')
    l3_net_uuid2 = test_lib.lib_get_l3_by_name(l3_name2).uuid
    

    vm = test_stub.create_vm(l3_net_list, image_uuid, 'attach_nic_vm', \
            default_l3_uuid = l3_net_uuid)
    test_obj_dict.add_vm(vm)
    vm.check()
    l3_1 = test_lib.lib_get_l3_by_name(l3_name)
    vr = test_lib.lib_find_vr_by_l3_uuid(l3_1.uuid)[0]
    vr_uuid = vr.uuid
    
    host = test_lib.lib_get_vm_host(vm.get_vm())
    host_uuid = host.uuid
    test_obj_dict.add_vm(vm)
    vm.check()
    #ps = test_lib.lib_get_primary_storage_by_vm(vm.get_vm())
    #ps_uuid = ps.uuid


    vm.add_nic(l3_net_uuid2)
    attached_nic = test_lib.lib_get_vm_last_nic(vm.get_vm())
    if l3_net_uuid2 != attached_nic.l3NetworkUuid:
        test_util.test_fail("After attach a nic, VM:%s last nic is not belong l3: %s" % (vm.get_vm().uuid, l3_net_uuid2))

    test_lib.lib_restart_vm_network(vm.get_vm())
    vm.check()

    #ps_ops.change_primary_storage_state(ps_uuid, 'disable')
    test_stub.disable_all_pss()
    if not test_lib.lib_wait_target_up(vm.get_vm().vmNics[0].ip, '22', 90):
        test_util.test_fail('VM is expected to running when PS change to disable state')
    vm.set_state(vm_header.RUNNING)

    vm.remove_nic(attached_nic.uuid)
    attached_nic = test_lib.lib_get_vm_last_nic(vm.get_vm())
    if l3_net_uuid != attached_nic.l3NetworkUuid:
        test_util.test_fail("After detached NIC, VM:%s only nic is not belong l3: %s" % (vm.get_vm().uuid, l3_net_uuid2))

    vm.add_nic(l3_net_uuid2)
    attached_nic = test_lib.lib_get_vm_last_nic(vm.get_vm())
    if l3_net_uuid2 != attached_nic.l3NetworkUuid:
        test_util.test_fail("After attach a nic, VM:%s last nic is not belong l3: %s" % (vm.get_vm().uuid, l3_net_uuid2))

    test_lib.lib_restart_vm_network(vm.get_vm())
    vm.check()

    #ps_ops.change_primary_storage_state(ps_uuid, 'enable')
    test_stub.enable_all_pss()
    host_ops.reconnect_host(host_uuid)
    vm_ops.reconnect_vr(vr_uuid)
    vm.check()
    vm.destroy()
    vm.check()
    #vm.expunge()
    test_util.test_pass('PS disable mode Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global ps_uuid
    if ps_uuid != None:
        ps_ops.change_primary_storage_state(ps_uuid, 'enable')
    global host_uuid
    if host_uuid != None:
        host_ops.reconnect_host(host_uuid)
    global vr_uuid
    if vr_uuid != None:
        vm_ops.reconnect_vr(vr_uuid)
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
